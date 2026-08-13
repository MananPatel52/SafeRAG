from langchain_huggingface import HuggingFaceEmbeddings

from app.config.settings import settings


class EmbeddingService:
    """
    Creates and manages the embedding model used by SafeRAG.
    """

    def __init__(self):
        self.model = HuggingFaceEmbeddings(
            model_name=settings.embedding_model
        )

    def get_model(self):
        """
        Return the configured embedding model.
        """

        return self.model