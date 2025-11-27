from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

from app.core.config import get_settings
from app.models.schemas import HealthResponse, JobSearchRequest, JobSearchResponse
from app.services.job_agent import JobFinderAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    logger.info("Starting Job Finder API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    logger.info("Shutting down Job Finder API...")

app = FastAPI(
    title="Job Finder API",
    description="AI-powered job search and recommendation API using BrightData and LangGraph",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return HealthResponse(
        status="healthy",
        message="Job Finder API is running",
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="All systems operational",
        version="1.0.0"
    )


@app.post(
    "/api/v1/jobs/search",
    response_model=JobSearchResponse,
    status_code=status.HTTP_200_OK,
    tags=["Jobs"],
    summary="Search and get AI-recommended jobs",
    description="Submit a job search query and receive AI-curated job recommendations from LinkedIn and Glassdoor"
)
async def search_jobs(request: JobSearchRequest) -> JobSearchResponse | None:
    """
    Search for jobs and get AI-powered recommendations

    Args:
        request: Job search parameters including keywords, location, and preferences

    Returns:
        JobSearchResponse with top recommended jobs

    Raises:
        HTTPException: If search fails or invalid parameters
    """
    try:
        logger.info(f"Received job search request: {request.keywords}")

        # Initialize agent
        agent = JobFinderAgent()

        # Execute agentic workflow
        results = await agent.search_and_recommend(
            keywords=request.keywords,
            location=request.location,
            country=request.country,
            remote=request.remote,
            job_type=request.job_type,
            experience_level=request.experience_level,
            limit=request.limit,
            user_preferences=request.preferences
        )

        logger.info(f"Successfully found {len(results.jobs)} jobs")

        return results

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error processing job search: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing job search"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
