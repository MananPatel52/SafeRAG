from typing import List

from langchain_core.documents import Document

from app.ingestion.pipeline import DocumentChunk
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import VectorStoreService


class IndexingService:
    """
    Converts our internal DocumentChunk objects into
    LangChain Documents and stores them in Chroma.
    """

    def __init__(self):

        embedding_service = EmbeddingService()

        self.vector_store_service = VectorStoreService(
            embedding_service.get_model()
        )

        self.vector_store = (
            self.vector_store_service.get_store()
        )

    def _to_langchain_document(
        self,
        chunk: DocumentChunk,
    ) -> Document:

        return Document(
            page_content=chunk.text,
            metadata=chunk.metadata,
        )

    def index_documents(
        self,
        documents: List[DocumentChunk],
    ):

        if not documents:
            return 0

        langchain_documents = [
            self._to_langchain_document(chunk)
            for chunk in documents
        ]

        self.vector_store.add_documents(
            langchain_documents
        )

        return len(langchain_documents)