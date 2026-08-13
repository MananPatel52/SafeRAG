from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.models.schemas import DocumentChunk


class DocumentChunker:
    """
    Splits document text into smaller chunks while preserving
    document-level and page-level metadata.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

    def chunk_documents(
        self,
        documents: List[DocumentChunk],
    ) -> List[DocumentChunk]:

        chunks = []

        for document in documents:

            split_texts = self.text_splitter.split_text(
                document.text
            )

            for chunk_index, text in enumerate(split_texts):

                chunk_metadata = {
                    **document.metadata,
                    "chunk_id": (
                        f"{document.metadata['doc_id']}"
                        f"-p{document.metadata['page']}"
                        f"-c{chunk_index + 1}"
                    ),
                }

                chunks.append(
                    DocumentChunk(
                        text=text,
                        metadata=chunk_metadata,
                    )
                )

        return chunks