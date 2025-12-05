import logging
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.config import get_settings
from app.models.schemas import LLMJobAnalysis

logger = logging.getLogger(__name__)
settings = get_settings()


class JobAnalysisLLM:
    """LLM service for analyzing and scoring job postings"""

    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL,
            temperature=settings.GROQ_TEMPERATURE,
            max_tokens=settings.GROQ_MAX_TOKENS,
        )  # .with_structured_output(LLMJobAnalysis)

        self.parser = JsonOutputParser(pydantic_object=LLMJobAnalysis)

    def _create_analysis_prompt(self) -> ChatPromptTemplate:
        """Create prompt template for job analysis"""
        template = """You are an expert career advisor and job matching specialist. 
Analyze the following job posting against the candidate's search criteria and preferences.

SEARCH CRITERIA:
Keywords: {keywords}
Location: {location}
Job Type: {job_type}
Country: {country}
Remote: {remote}
Experience Level: {experience_level}
User Preferences: {preferences}

JOB POSTING:
Title: {job_title}
Company: {company}
Location: {job_location}
Employment Type: {job_employment_type}
Industries: {job_industries}
Function: {job_function}
Seniority Level: {job_seniority_level}
Base Pay Range: {job_base_pay_range}
Summary: {job_summary}
Employee Benefit Reviews: {employee_benefit_reviews}

TASK:
Analyze this job posting and provide a detailed assessment. Consider:
1. How well does this match the search keywords and criteria?
2. Is the experience level appropriate?
3. Does it align with user preferences?
4. What are the key strengths of this opportunity?
5. Are there any red flags or concerns?

{format_instructions}

Provide your analysis in valid JSON format with no additional text or markdown.
"""

        return ChatPromptTemplate.from_template(template)

    async def analyze_job(
        self, job: Dict[str, Any], search_criteria: Dict[str, Any]
    ) -> LLMJobAnalysis:
        """
        Analyze a single job posting using LLM

        Args:
            job: Job posting data
            search_criteria: User's search criteria

        Returns:
            LLMJobAnalysis with scoring and recommendation
        """
        try:
            prompt = self._create_analysis_prompt()

            chain = (
                {
                    "keywords": lambda x: x["keywords"],
                    "location": lambda x: x["location"],
                    "job_type": lambda x: x["job_type"],
                    "country": lambda x: x["country"],
                    "remote": lambda x: x["remote"],
                    "experience_level": lambda x: x["experience_level"],
                    "preferences": lambda x: str(x.get("preferences", {})),
                    "job_title": lambda x: x["job"]["title"],
                    "company": lambda x: x["job"]["company"],
                    "job_location": lambda x: x["job"]["location"],
                    "job_employment_type": lambda x: x["job"]["job_type"],
                    "job_industries": lambda x: x["job"]["job_industries"],
                    "job_function": lambda x: x["job"]["job_function"],
                    "job_seniority_level": lambda x: x["job"]["job_seniority_level"],
                    "job_base_pay_range": lambda x: x["job"]["job_base_pay_range"],
                    # Truncate
                    "job_summary": lambda x: x["job"]["job_summary"][:1000],
                    "employee_benefit_reviews": lambda x: x["job"][
                        "employee_benefit_reviews"
                    ],
                    "format_instructions": lambda x: self.parser.get_format_instructions(),
                }
                | prompt
                | self.llm
                | self.parser
            )

            input_data = {**search_criteria, "job": job}
            result = await chain.ainvoke(input_data)

            return LLMJobAnalysis(**result)

        except Exception as e:
            logger.error(f"LLM analysis failed for job {job.get('job_id')}: {str(e)}")
            # Return default analysis if LLM fails
            return LLMJobAnalysis(
                relevance_score=50.0,
                match_explanation="Unable to perform detailed analysis",
                key_strengths=["Job posting available"],
                potential_concerns=["Analysis unavailable"],
                recommendation="consider",
            )

    async def analyze_jobs_batch(
        self,
        jobs: List[Dict[str, Any]],
        search_criteria: Dict[str, Any],
        limit: int = 10,
    ) -> List[tuple[Dict[str, Any], LLMJobAnalysis]]:
        """
        Analyze multiple jobs and return top recommendations

        Args:
            jobs: List of job postings
            search_criteria: User's search criteria
            limit: Number of top jobs to return

        Returns:
            List of (job, analysis) tuples sorted by relevance
        """
        logger.info(f"Analyzing {len(jobs)} jobs with LLM")

        analyzed_jobs = []

        # Analyze jobs (could be parallelized further with asyncio.gather)
        for job in jobs:
            try:
                analysis = await self.analyze_job(job, search_criteria)
                analyzed_jobs.append((job, analysis))
            except Exception as e:
                logger.error(f"Failed to analyze job: {str(e)}")
                continue

        # Sort by relevance score
        analyzed_jobs.sort(key=lambda x: x[1].relevance_score, reverse=True)

        # Filter by minimum score and limit
        filtered_jobs = [
            (job, analysis)
            for job, analysis in analyzed_jobs
            if analysis.relevance_score >= settings.MIN_MATCH_SCORE
        ]

        logger.info(
            f"Filtered to {len(filtered_jobs[:limit])} top jobs "
            f"(min score: {settings.MIN_MATCH_SCORE})"
        )

        return filtered_jobs[:limit]
