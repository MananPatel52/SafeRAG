from typing import List, Optional

from langchain_core.documents import Document

from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import VectorStoreService
from app.config.settings import settings


class RetrieverService:
    """
    Handles semantic and metadata-aware retrieval
    from the Chroma vector database.
    """

    def __init__(self):

        embedding_service = EmbeddingService()

        vector_store_service = VectorStoreService(
            embedding_service.get_model()
        )

        self.vector_store = (
            vector_store_service.get_store()
        )

    def retrieve(
        self,
        query: str,
        department: Optional[str] = None,
        document_type: Optional[str] = None,
    ) -> List[Document]:

        filters = {}

        if department:
            filters["department"] = department

        if document_type:
            filters["document_type"] = document_type

        search_kwargs = {
            "k": settings.top_k,
            "fetch_k": settings.fetch_k,
            "lambda_mult": settings.mmr_lambda,
        }

        if filters:
            search_kwargs["filter"] = filters

        return self.vector_store.max_marginal_relevance_search(
            query,
            **search_kwargs,
        )