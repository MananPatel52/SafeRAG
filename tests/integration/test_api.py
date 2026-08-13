import pytest

from fastapi.testclient import TestClient

from app.api.main import app, pipeline


client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_gemini(monkeypatch):
    """
    Prevent integration tests from calling the real Gemini API.

    The rest of the SafeRAG pipeline remains real:
        Retrieval -> Conflict Detection -> Temporal Resolution

    Only the final LLM generation step is mocked.
    """

    def fake_generate(question, context):
        """
        Deterministic replacement for Gemini during tests.

        Returns the expected answer based on the retrieved context.
        """

        if "January 2026" in question:
            return (
                "The pharmacy dispensing target was 30 minutes "
                "in January 2026."
            )

        return (
            "The current pharmacy dispensing target is 20 minutes."
        )

    monkeypatch.setattr(
        pipeline.generator,
        "generate",
        fake_generate,
    )


def test_health_endpoint():
    """
    Verify that the API health endpoint is working.
    """

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_query_validation_rejects_short_question():
    """
    Verify that very short questions are rejected
    by Pydantic validation.
    """

    response = client.post(
        "/query",
        json={
            "question": "?"
        },
    )

    assert response.status_code == 422


def test_query_endpoint():
    """
    Verify that the query endpoint returns
    the expected response structure.

    This test uses the actual SafeRAG pipeline.
    """

    response = client.post(
        "/query",
        json={
            "question": (
                "What is the current pharmacy "
                "dispensing target?"
            ),
            "department": "pharmacy",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert "sources" in data
    assert "conflict_detected" in data

    assert len(data["sources"]) > 0


def test_query_returns_pharmacy_answer():
    """
    Verify that the RAG pipeline returns the
    correct current pharmacy dispensing target.
    """

    response = client.post(
        "/query",
        json={
            "question": (
                "What is the current pharmacy "
                "dispensing target?"
            ),
            "department": "pharmacy",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "20 minutes" in data["answer"]

    assert data["conflict_detected"] is True

    assert any(
        source["document_id"] == "PHARM-2026-03"
        for source in data["sources"]
    )


def test_query_handles_internal_error(monkeypatch):
    """
    Verify that an unexpected pipeline failure
    is converted into a controlled HTTP 500 response.
    """

    def failing_pipeline(*args, **kwargs):
        raise RuntimeError("Simulated internal failure")

    monkeypatch.setattr(
        pipeline,
        "ask",
        failing_pipeline,
    )

    response = client.post(
        "/query",
        json={
            "question": "What is the pharmacy policy?"
        },
    )

    assert response.status_code == 500

    data = response.json()

    assert data["detail"] == "Unable to process the query."

def test_historical_policy_query():
    response = client.post(
        "/query",
        json={
            "question": (
                "What was the pharmacy dispensing "
                "target in January 2026?"
            ),
            "department": "pharmacy",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "30 minutes" in data["answer"]

    assert data["conflict_detected"] is True

    assert len(data["sources"]) > 0

    assert (
        data["sources"][0]["document_id"]
        == "PHARM-2026-01"
    )



def test_current_policy_query():
    response = client.post(
        "/query",
        json={
            "question": (
                "What is the current pharmacy "
                "dispensing target?"
            ),
            "department": "pharmacy",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "20 minutes" in data["answer"]

    assert data["conflict_detected"] is True

    assert len(data["sources"]) > 0

    assert (
        data["sources"][0]["document_id"]
        == "PHARM-2026-03"
    )


def test_unsupported_question_abstains():
    response = client.post(
        "/query",
        json={
            "question": (
                "What is the hospital's policy "
                "for employee vacation leave?"
            ),
            "department": "hr",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["answer"]
        == "I couldn't find sufficient information "
        "in the provided documents."
    )

    assert data["sources"] == []

    assert data["conflict_detected"] is False