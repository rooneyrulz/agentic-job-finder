import logging
from typing import List, Optional, Dict, Any, TypedDict, Annotated
from datetime import datetime
import operator

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from app.models.schemas import JobSearchResponse, JobRecommendation

logger = logging.getLogger(__name__)

# Define the agent state


class JobSearchState(TypedDict):
    """State for the job search agent workflow"""
    # Input
    keywords: str
    location: str
    country: str
    job_type: str
    experience_level: str
    remote: str
    limit: int
    user_preferences: Optional[Dict[str, Any]]

    # Intermediate state
    raw_jobs: Annotated[List[Dict[str, Any]], operator.add]
    analyzed_jobs: List[tuple[Dict[str, Any], Any]]

    # Output
    final_recommendations: List[JobRecommendation]
    search_metadata: Dict[str, Any]

    # Control flow
    error: Optional[str]
    processing_time: float


class JobFinderAgent:
    """LangGraph agent for orchestrating job search workflow"""

    def __init__(self):
        self.scraper = None  # Initialize BrightData scraper
        self.llm_service = None  # Initialize LLM service
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:

        # Create the state graph
        workflow = StateGraph(JobSearchState)

        # Add nodes to the workflow
        workflow.add_node("validate_input", self._validate_input_node)
        workflow.add_node("scrape_jobs", self._scrape_jobs_node)
        workflow.add_node("analyze_jobs", self._analyze_jobs_node)
        workflow.add_node("format_response", self._format_response_node)

        # Define the workflow edges
        workflow.set_entry_point("validate_input")

        workflow.add_edge("validate_input", "scrape_jobs")
        workflow.add_edge("scrape_jobs", "analyze_jobs")
        workflow.add_edge("analyze_jobs", "format_response")
        workflow.add_edge("format_response", END)

        return workflow.compile()

    async def _validate_input_node(self, state: JobSearchState) -> JobSearchState:
        """Node 1: Validate and normalize input parameters"""
        logger.info("Node 1: Validating input")

        try:
            # Normalize inputs
            state["keywords"] = state["keywords"].strip()
            state["location"] = state.get("location", "Remote").strip()
            state["limit"] = min(state.get("limit", 10), 50)

            # Initialize state
            state["raw_jobs"] = []
            state["analyzed_jobs"] = []
            state["final_recommendations"] = []
            state["search_metadata"] = {
                "start_time": datetime.utcnow().isoformat(),
                "sources": [],
                "filters_applied": []
            }
            state["error"] = None

            logger.info(
                f"Input validated: {state['keywords']} in {state['location']}")
            return state

        except Exception as e:
            logger.error(f"Input validation failed: {str(e)}")
            state["error"] = str(e)
            return state

    async def _scrape_jobs_node(self, state: JobSearchState) -> JobSearchState:
        """Node 2: Scrape jobs from BrightData sources"""
        logger.info("Node 2: Scraping jobs from sources")

        if state.get("error"):
            return state

        try:
            # Determine how many jobs to scrape per source
            limit_per_source = state["limit"] // 2

            # Scrape from all sources
            raw_jobs = await self.scraper.scrape_all_sources(
                keywords=state["keywords"],
                location=state["location"],
                limit_per_source=limit_per_source
            )

            state["raw_jobs"] = raw_jobs
            state["search_metadata"]["sources"] = ["LinkedIn", "Glassdoor"]
            state["search_metadata"]["total_scraped"] = len(raw_jobs)

            logger.info(f"Scraped {len(raw_jobs)} jobs")
            return state

        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            state["error"] = f"Scraping failed: {str(e)}"
            return state

    async def _analyze_jobs_node(self, state: JobSearchState) -> JobSearchState:
        """Node 3: Analyze jobs with LLM"""
        logger.info("Node 3: Analyzing jobs with LLM")

        if state.get("error") or not state.get("raw_jobs"):
            return state

        try:
            # Prepare search criteria for LLM
            search_criteria = {
                "keywords": state["keywords"],
                "location": state["location"],
                "country": state.get("country", "any"),
                "remote": state.get("remote", "any"),
                "job_type": state.get("job_type", "any"),
                "experience_level": state.get("experience_level", "any"),
                "preferences": state.get("user_preferences", {})
            }

            # Analyze jobs with LLM
            analyzed = await self.llm_service.analyze_jobs_batch(
                jobs=state["raw_jobs"],
                search_criteria=search_criteria,
                limit=state["limit"]
            )

            state["analyzed_jobs"] = analyzed
            state["search_metadata"]["analyzed_count"] = len(analyzed)

            logger.info(f"Analyzed {len(analyzed)} jobs")
            return state

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            state["error"] = f"Analysis failed: {str(e)}"
            return state

    async def _format_response_node(self, state: JobSearchState) -> JobSearchState:
        """Node 4: Format final response"""
        logger.info("Node 4: Formatting response")

        # Implementation of response formatting
        return state

    async def search_and_recommend() -> JobSearchResponse:
        """Execute the job search workflow and return recommendations"""

        # Implementation of workflow execution
        pass
