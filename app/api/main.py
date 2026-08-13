from fastapi import FastAPI, HTTPException

from app.config.settings import settings
from app.models.schemas import QueryRequest, QueryResponse
from app.reasoning.rag_pipeline import SafeRAGPipeline


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="SafeRAG - Grounded document question answering system",
)


# Create the pipeline once when the application starts.
pipeline = SafeRAGPipeline()


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


@app.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest):
    """
    Ask a question against the hospital document
    knowledge base.
    """

    try:

        result = pipeline.ask(
            question=request.question,
            department=request.department,
            document_type=request.document_type,
        )

        return result

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail="Required document could not be found.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to process the query.",
        )