from pathlib import Path

from app.ingestion.pipeline import PDFLoader
from app.ingestion.metadata import MetadataBuilder


DATA_DIR = Path("data/raw")


def test_all_dataset_documents_can_be_loaded():

    loader = PDFLoader()
    metadata_builder = MetadataBuilder()

    pdf_files = sorted(DATA_DIR.glob("*.pdf"))

    assert len(pdf_files) == 8

    for pdf_file in pdf_files:

        documents = loader.load(str(pdf_file))

        assert len(documents) > 0

        for document in documents:

            enriched = metadata_builder.enrich(
                document.metadata
            )

            assert enriched["doc_id"]

            assert enriched["document_name"]

            assert enriched["document_type"]

            assert enriched["department"]

            assert enriched["document_date"]

            assert enriched["page"] >= 1