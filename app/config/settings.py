from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.

    Values are loaded from environment variables or the .env file.
    """

    # Application
    app_name: str = "SafeRAG"
    app_env: str = "development"
    log_level: str = "INFO"

    # LLM
    gemini_api_key: str
    gemini_model: str = "gemini-3.5-flash"

    # Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_version: str = "v1"

    # Vector database
    chroma_persist_dir: str = "./chroma_data"
    chroma_collection: str = "saferag_documents"

    # Retrieval
    top_k: int = 5
    fetch_k: int = 20
    mmr_lambda: float = 0.7

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()