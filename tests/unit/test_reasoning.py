from langchain_core.documents import Document

from app.reasoning.temporal import TemporalResolver
from app.reasoning.conflict import ConflictDetector


def make_document(
    doc_id,
    date,
    text="Sample policy content.",
):
    return Document(
        page_content=text,
        metadata={
            "doc_id": doc_id,
            "document_date": date,
            "document_name": f"{doc_id}.pdf",
            "department": "pharmacy",
            "document_type": "policy",
            "page": 1,
        },
    )



# Temporal Resolution Tests


def test_temporal_resolver_selects_historical_document():
    """
    A historical question should select the document
    matching the requested month and year.
    """

    documents = [
        make_document("PHARM-2026-01", "2026-01-15"),
        make_document("PHARM-2026-03", "2026-03-15"),
    ]

    resolver = TemporalResolver()

    result = resolver.resolve(
        documents,
        "What was the pharmacy dispensing target in January 2026?",
    )

    assert result is not None
    assert result.metadata["doc_id"] == "PHARM-2026-01"


def test_temporal_resolver_selects_latest_for_current_query():
    """
    Without a historical date, the latest dated document
    should be selected.
    """

    documents = [
        make_document("PHARM-2026-01", "2026-01-15"),
        make_document("PHARM-2026-03", "2026-03-15"),
    ]

    resolver = TemporalResolver()

    result = resolver.resolve(
        documents,
        "What is the current pharmacy dispensing target?",
    )

    assert result is not None
    assert result.metadata["doc_id"] == "PHARM-2026-03"


def test_temporal_resolver_supports_numeric_date():
    """
    The resolver should understand YYYY-MM dates.
    """

    documents = [
        make_document("PHARM-2026-01", "2026-01-15"),
        make_document("PHARM-2026-03", "2026-03-15"),
    ]

    resolver = TemporalResolver()

    result = resolver.resolve(
        documents,
        "What was the policy in 2026-01?",
    )

    assert result is not None
    assert result.metadata["doc_id"] == "PHARM-2026-01"


def test_temporal_resolver_returns_none_for_empty_documents():
    """
    No retrieved documents should produce no temporal result.
    """

    resolver = TemporalResolver()

    result = resolver.resolve([])

    assert result is None


def test_temporal_resolver_deduplicates_document_ids():
    """
    Multiple chunks from the same document should be treated
    as one document during temporal resolution.
    """

    documents = [
        make_document("PHARM-2026-01", "2026-01-15", "Chunk 1"),
        make_document("PHARM-2026-01", "2026-01-15", "Chunk 2"),
        make_document("PHARM-2026-03", "2026-03-15", "Chunk 3"),
    ]

    resolver = TemporalResolver()

    result = resolver.resolve(
        documents,
        "What is the current pharmacy dispensing target?",
    )

    assert result is not None
    assert result.metadata["doc_id"] == "PHARM-2026-03"



# Conflict Detection Tests


def test_conflict_detector_detects_multiple_policy_versions():
    """
    Multiple documents belonging to the same policy should
    be identified as a conflict.
    """

    documents = [
        make_document(
            "PHARM-2026-01",
            "2026-01-15",
            "Dispensing target is 30 minutes.",
        ),
        make_document(
            "PHARM-2026-03",
            "2026-03-15",
            "Dispensing target is 20 minutes.",
        ),
    ]

    detector = ConflictDetector()

    result = detector.detect(documents)

    assert result["has_conflict"] is True


def test_conflict_detector_returns_false_for_single_document():
    """
    A single policy version should not be considered a conflict.
    """

    documents = [
        make_document(
            "PHARM-2026-03",
            "2026-03-15",
        )
    ]

    detector = ConflictDetector()

    result = detector.detect(documents)

    assert result["has_conflict"] is False


def test_conflict_detector_returns_false_for_empty_documents():
    """
    Empty retrieval results should not produce a conflict.
    """

    detector = ConflictDetector()

    result = detector.detect([])

    assert result["has_conflict"] is False