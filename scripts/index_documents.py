from pathlib import Path

from app.ingestion.pipeline import PDFLoader
from app.ingestion.metadata import MetadataBuilder
from app.ingestion.chunker import DocumentChunker

from app.retrieval.indexer import IndexingService


DATA_DIR = Path("data/raw")


def main():

    loader = PDFLoader()
    metadata_builder = MetadataBuilder()
    chunker = DocumentChunker()

    all_documents = []

    pdf_files = sorted(
        DATA_DIR.glob("*.pdf")
    )

    print(
        f"Found {len(pdf_files)} PDF documents."
    )

    for pdf_file in pdf_files:

        print(
            f"Loading: {pdf_file.name}"
        )

        documents = loader.load(
            str(pdf_file)
        )

        enriched_documents = []

        for document in documents:

            document.metadata = (
                metadata_builder.enrich(
                    document.metadata
                )
            )

            enriched_documents.append(
                document
            )

        chunks = chunker.chunk_documents(
            enriched_documents
        )

        all_documents.extend(chunks)

        print(
            f"  Created {len(chunks)} chunks"
        )

    print(
        f"\nTotal chunks: {len(all_documents)}"
    )

    indexer = IndexingService()

    count = indexer.index_documents(
        all_documents
    )

    print(
        f"Indexed {count} chunks into Chroma."
    )


if __name__ == "__main__":
    main()