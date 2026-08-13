from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import VectorStoreService


def main():

    embedding_service = EmbeddingService()

    vector_store_service = VectorStoreService(
        embedding_service.get_model()
    )

    vector_store = (
        vector_store_service.get_store()
    )

    collection = vector_store._collection

    count = collection.count()

    print(
        f"Documents/chunks stored in Chroma: {count}"
    )


if __name__ == "__main__":
    main()