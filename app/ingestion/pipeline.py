from pathlib import Path
from typing import List

import fitz

from app.models.schemas import DocumentChunk


class PDFLoader:
    """
    Loads text from PDF documents while preserving page-level provenance.
    """

    def load(self, pdf_path: str) -> List[DocumentChunk]:
        """
        Extract text from every page of a PDF.

        Each page becomes an initial DocumentChunk.
        """

        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        documents = []

        pdf = fitz.open(pdf_path)

        try:
            for page_number, page in enumerate(pdf):

                text = page.get_text()

                if not text.strip():
                    continue

                documents.append(
                    DocumentChunk(
                        text=text.strip(),
                        metadata={
                            "source": str(path),
                            "page": page_number + 1,
                        },
                    )
                )

        finally:
            pdf.close()

        return documents