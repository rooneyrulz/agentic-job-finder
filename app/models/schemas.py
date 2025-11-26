from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class JobType(str, Enum):
    """Job type enumeration"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    ANY = "any"


class ExperienceLevel(str, Enum):
    """Experience level enumeration"""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"
    ANY = "any"


class WorkArrangment(str, Enum):
    """Work arrangment enumeration"""
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    ANY = "any"


class JobSearchRequest(BaseModel):
    """Request schema for job search"""
    keywords: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Job search keywords (e.g., 'Python Developer', 'Data Scientist')",
        examples=["Python Developer", "Machine Learning Engineer"]
    )
    location: Optional[str] = Field(
        default="New York, NY",
        max_length=100,
        description="Preferred job location (e.g: city, state, or remote)",
        examples=["San Francisco, CA", "Remote"]
    )
    country: Optional[str] = Field(
        default="US",
        max_length=100,
        description="Two letters country code (eg: US, UK, CA, FR)",
        examples=["US", "UK", "CA"]
    )
    job_type: JobType = Field(
        default=JobType.ANY,
        description="Type of employment (eg: full-time, part-time, contract)"
    )
    experience_level: ExperienceLevel = Field(
        default=ExperienceLevel.ANY,
        description="Required experience level"
    )
    remote: WorkArrangment = Field(
        default=WorkArrangment.ANY,
        description="Work arrangement preference (eg: remote, hybrid, onsite)"
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of jobs to return"
    )
    preferences: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional user preferences (skills, salary range, etc.)"
    )

    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v: str) -> str:
        """Validate and sanitize keywords"""
        if not v or v.strip() == "":
            raise ValueError("Keywords cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "keywords": "Senior Python Developer",
                "location": "San Francisco, CA",
                "job_type": "full_time",
                "experience_level": "senior",
                "remote": "remote",
                "limit": 10,
                "preferences": {
                    "min_salary": 120000,
                    "required_skills": ["Python", "FastAPI", "Docker"],
                    "exclude_companies": []
                }
            }
        }


class JobRecommendation(BaseModel):
    """Individual job recommendation schema"""
    job_id: str = Field(..., description="Unique job identifier")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    job_type: str = Field(..., description="Employment type")
    description: str = Field(..., description="Job description")
    requirements: List[str] = Field(
        default_factory=list,
        description="Job requirements and qualifications"
    )
    salary_range: Optional[str] = Field(
        None,
        description="Salary range if available"
    )
    posted_date: Optional[str] = Field(
        None,
        description="Job posting date"
    )
    apply_url: str = Field(..., description="Application URL")
    source: str = Field(..., description="Data source (LinkedIn/Glassdoor)")
    match_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="AI-calculated match score (0-100)"
    )
    match_reason: str = Field(
        ...,
        description="AI explanation of why this job is recommended"
    )
    key_highlights: List[str] = Field(
        default_factory=list,
        description="Key highlights of the job posting"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "linkedin_123456",
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "Remote",
                "job_type": "Full-time",
                "description": "We're looking for an experienced Python developer...",
                "requirements": ["5+ years Python", "FastAPI experience", "Cloud platforms"],
                "salary_range": "$120k - $180k",
                "posted_date": "2024-11-20",
                "apply_url": "https://linkedin.com/jobs/123456",
                "source": "LinkedIn",
                "match_score": 92.5,
                "match_reason": "Strong alignment with Python and FastAPI expertise, remote-first company",
                "key_highlights": ["Remote-first culture", "Competitive salary", "Modern tech stack"]
            }
        }


class JobSearchResponse(BaseModel):
    """Response schema for job search"""
    success: bool = Field(..., description="Whether the search was successful")
    query: str = Field(..., description="Original search query")
    total_found: int = Field(..., ge=0, description="Total jobs found")
    jobs: List[JobRecommendation] = Field(
        default_factory=list,
        description="List of recommended jobs"
    )
    search_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional search metadata"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "query": "Senior Python Developer",
                "total_found": 10,
                "jobs": [],
                "search_metadata": {
                    "sources": ["LinkedIn", "Glassdoor"],
                    "processing_time_ms": 3500,
                    "filters_applied": ["experience_level", "job_type"]
                },
                "timestamp": "2024-11-24T10:30:00Z"
            }
        }


# Health Check Schema
class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    version: str = Field(..., description="API version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "Job Finder API is running",
                "version": "1.0.0"
            }
        }


# LLM Structured Output Schemas

class LLMJobAnalysis(BaseModel):
    """Schema for LLM job analysis structured output"""
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Job relevance score based on search criteria"
    )
    match_explanation: str = Field(
        ...,
        min_length=20,
        max_length=500,
        description="Detailed explanation of why this job matches"
    )
    key_strengths: List[str] = Field(
        ...,
        min_items=1,
        max_items=5,
        description="Key strengths of this job posting"
    )
    potential_concerns: List[str] = Field(
        default_factory=list,
        max_items=3,
        description="Any potential concerns or mismatches"
    )
    recommendation: str = Field(
        ...,
        description="Recommend: 'highly_recommended', 'recommended', 'consider', or 'not_recommended'"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "relevance_score": 88.5,
                "match_explanation": "This position aligns well with senior Python development expertise...",
                "key_strengths": [
                    "Modern tech stack with FastAPI",
                    "Remote-first company culture",
                    "Competitive compensation"
                ],
                "potential_concerns": ["May require occasional travel"],
                "recommendation": "highly_recommended"
            }
        }


class LLMBatchAnalysis(BaseModel):
    """Schema for batch job analysis by LLM"""
    total_analyzed: int = Field(..., ge=0)
    analyses: List[LLMJobAnalysis] = Field(default_factory=list)
    top_recommendation_indices: List[int] = Field(
        default_factory=list,
        description="Indices of top recommended jobs in order"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_analyzed": 25,
                "analyses": [],
                "top_recommendation_indices": [0, 3, 5, 8, 10, 12, 15, 18, 20, 22]
            }
        }
