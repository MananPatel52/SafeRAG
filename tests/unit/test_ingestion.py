from pathlib import Path

from app.ingestion.pipeline import PDFLoader

from app.ingestion.metadata import MetadataBuilder

from app.ingestion.chunker import DocumentChunker
from app.models.schemas import DocumentChunk


def test_pdf_loader_requires_existing_file():

    loader = PDFLoader()

    missing_file = Path("data/raw/does_not_exist.pdf")

    try:
        loader.load(str(missing_file))
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        assert True

def test_pdf_loader_extracts_text():

    loader = PDFLoader()

    pdf_path = "data/raw/01_hospital_operations_january.pdf"

    documents = loader.load(pdf_path)

    assert len(documents) > 0

    first_document = documents[0]

    assert "Green Valley General Hospital" in first_document.text

    assert first_document.metadata["page"] == 1

    assert Path(first_document.metadata["source"]) == Path(pdf_path)


def test_metadata_builder_enriches_document_metadata():

    builder = MetadataBuilder()

    metadata = {
        "source": "data/raw/01_hospital_operations_january.pdf",
        "page": 1,
    }

    enriched = builder.enrich(metadata)

    assert enriched["doc_id"] == "OPS-2026-01"

    assert enriched["document_name"] == (
        "01_hospital_operations_january.pdf"
    )

    assert enriched["document_type"] == "operations_report"

    assert enriched["department"] == "hospital_operations"

    assert enriched["document_date"] == "2026-01-15"

    assert enriched["page"] == 1


def test_document_chunker_preserves_metadata():

    document = DocumentChunk(
        text=(
            "The emergency department average patient wait time "
            "was 42 minutes. "
            "The hospital target was 45 minutes. "
            "The hospital is working to improve patient flow. "
            "Additional operational improvements are planned "
            "for the following month. "
        ),
        metadata={
            "source": "data/raw/01_hospital_operations_january.pdf",
            "page": 1,
            "doc_id": "OPS-2026-01",
            "document_name": "01_hospital_operations_january.pdf",
            "document_type": "operations_report",
            "department": "hospital_operations",
            "document_date": "2026-01-15",
        },
    )

    chunker = DocumentChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.chunk_documents([document])

    assert len(chunks) > 1

    for chunk in chunks:

        assert chunk.text.strip()

        assert chunk.metadata["doc_id"] == "OPS-2026-01"

        assert chunk.metadata["page"] == 1

        assert chunk.metadata["document_date"] == "2026-01-15"

        assert "chunk_id" in chunk.metadata