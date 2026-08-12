from fastapi import FastAPI

from app.config.settings import settings


app = FastAPI(
    title=settings.app_name,
    description="Adversarial RAG Intelligence Platform",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """
    Basic health-check endpoint.

    Used to verify that the API service is running.
    """

    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.app_env,
    }