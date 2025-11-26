from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Settings
    APP_NAME: str = "Job Finder API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # BrightData Configuration
    BRIGHTDATA_API_KEY: str
    BRIGHTDATA_LINKEDIN_ENDPOINT: str = "https://api.brightdata.com/datasets/v3/trigger"
    BRIGHTDATA_GLASSDOOR_ENDPOINT: str = "https://api.brightdata.com/datasets/v3/trigger"
    BRIGHTDATA_DATASET_ID_LINKEDIN: Optional[str] = None
    BRIGHTDATA_DATASET_ID_GLASSDOOR: Optional[str] = None
    
    # Groq LLM Configuration
    GROQ_API_KEY: str
    GROQ_MODEL: str = "mixtral-8x7b-32768"  # Fast and capable model
    GROQ_MAX_TOKENS: int = 2048
    GROQ_TEMPERATURE: float = 0.3
    
    # LangChain/LangGraph Settings
    LANGCHAIN_TRACING: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "job-finder-api"
    
    # Rate Limiting & Performance
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 60
    CACHE_TTL: int = 3600  # 1 hour cache
    
    # Job Search Configuration
    DEFAULT_JOB_LIMIT: int = 10
    MAX_JOB_LIMIT: int = 50
    MIN_MATCH_SCORE: float = 60.0
    
    # Scraping Configuration
    SCRAPING_RETRY_ATTEMPTS: int = 3
    SCRAPING_RETRY_DELAY: int = 2
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()