from unittest.mock import MagicMock, patch

from app.retrieval.retriever import RetrieverService


def create_retriever_with_mock_store():
    """
    Create RetrieverService without initializing the real
    embedding model or Chroma vector store.
    """

    mock_store = MagicMock()

    with patch(
        "app.retrieval.retriever.EmbeddingService"
    ) as mock_embedding_service, patch(
        "app.retrieval.retriever.VectorStoreService"
    ) as mock_vector_store_service:

        mock_embedding_service.return_value.get_model.return_value = (
            MagicMock()
        )

        mock_vector_store_service.return_value.get_store.return_value = (
            mock_store
        )

        retriever = RetrieverService()

    return retriever, mock_store


def test_retriever_calls_vector_store():
    """
    Retriever should pass the query to the vector store.
    """

    retriever, mock_store = create_retriever_with_mock_store()

    mock_store.max_marginal_relevance_search.return_value = [
        MagicMock()
    ]

    result = retriever.retrieve(
        "What is the pharmacy dispensing target?"
    )

    mock_store.max_marginal_relevance_search.assert_called_once()

    assert result == mock_store.max_marginal_relevance_search.return_value


def test_retriever_applies_department_filter():
    """
    Department should be converted into a Chroma metadata filter.
    """

    retriever, mock_store = create_retriever_with_mock_store()

    mock_store.max_marginal_relevance_search.return_value = []

    retriever.retrieve(
        "What is the pharmacy dispensing target?",
        department="pharmacy",
    )

    _, kwargs = (
        mock_store.max_marginal_relevance_search.call_args
    )

    assert kwargs["filter"] == {
        "department": "pharmacy"
    }


def test_retriever_applies_document_type_filter():
    """
    Document type should be converted into a metadata filter.
    """

    retriever, mock_store = create_retriever_with_mock_store()

    mock_store.max_marginal_relevance_search.return_value = []

    retriever.retrieve(
        "What is the pharmacy dispensing target?",
        document_type="policy",
    )

    _, kwargs = (
        mock_store.max_marginal_relevance_search.call_args
    )

    assert kwargs["filter"] == {
        "document_type": "policy"
    }


def test_retriever_applies_multiple_metadata_filters():
    """
    Department and document type filters should be combined.
    """

    retriever, mock_store = create_retriever_with_mock_store()

    mock_store.max_marginal_relevance_search.return_value = []

    retriever.retrieve(
        "What is the pharmacy dispensing target?",
        department="pharmacy",
        document_type="policy",
    )

    _, kwargs = (
        mock_store.max_marginal_relevance_search.call_args
    )

    assert kwargs["filter"] == {
        "department": "pharmacy",
        "document_type": "policy",
    }


def test_retriever_uses_mmr_configuration():
    """
    Retriever should use the configured top_k, fetch_k,
    and MMR lambda values.
    """

    retriever, mock_store = create_retriever_with_mock_store()

    mock_store.max_marginal_relevance_search.return_value = []

    retriever.retrieve(
        "What is the pharmacy dispensing target?"
    )

    _, kwargs = (
        mock_store.max_marginal_relevance_search.call_args
    )

    assert kwargs["k"] == 5
    assert kwargs["fetch_k"] == 20
    assert kwargs["lambda_mult"] == 0.7