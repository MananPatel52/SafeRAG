from pathlib import Path

from langchain_chroma import Chroma

from app.config.settings import settings


class VectorStoreService:
    """
    Manages the Chroma vector database.
    """

    def __init__(self, embedding_model):

        self.persist_directory = Path(
            settings.chroma_persist_dir
        )

        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        self.vector_store = Chroma(
            collection_name=settings.chroma_collection,
            embedding_function=embedding_model,
            persist_directory=str(
                self.persist_directory
            ),
        )

    def get_store(self):
        """
        Return the Chroma vector store.
        """

        return self.vector_store