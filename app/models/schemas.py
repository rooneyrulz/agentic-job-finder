from pydantic import BaseModel, Field

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