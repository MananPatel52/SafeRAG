from typing import Optional

from app.retrieval.retriever import RetrieverService
from app.reasoning.conflict import ConflictDetector
from app.reasoning.temporal import TemporalResolver
from app.reasoning.generator import GeminiGenerator


class SafeRAGPipeline:
    """
    End-to-end SafeRAG pipeline.

    Flow:
        Query
        -> Retrieval
        -> Conflict Detection
        -> Temporal Resolution
        -> Grounded Generation
    """

    def __init__(self):

        self.retriever = RetrieverService()

        self.conflict_detector = (
            ConflictDetector()
        )

        self.temporal_resolver = (
            TemporalResolver()
        )

        self.generator = (
            GeminiGenerator()
        )

    def ask(
        self,
        question: str,
        department: Optional[str] = None,
        document_type: Optional[str] = None,
    ) -> dict:

        
        # 1. Retrieve relevant documents

        documents = self.retriever.retrieve(
            query=question,
            department=department,
            document_type=document_type,
        )

        if not documents:

            return {
                "answer": (
                    "I couldn't find sufficient "
                    "information in the provided documents."
                ),
                "sources": [],
                "conflict_detected": False,
            }

     
        # 2. Detect conflicts

        conflict_result = (
            self.conflict_detector.detect(
                documents
            )
        )

        conflict_detected = (
            conflict_result["has_conflict"]
        )

        
        # 3. Resolve authoritative document

        if conflict_detected:

            authoritative_document = (
                self.temporal_resolver.resolve(
                    documents,
                    question=question,
                )
            )

            if authoritative_document:

                context_documents = [
                    authoritative_document
                ]

            else:

                context_documents = documents

        else:

            context_documents = documents

        
        # 4. Build grounded context

        context_parts = []

        sources = []

        for document in context_documents:

            metadata = document.metadata

            context_parts.append(
                f"""
SOURCE:
{metadata.get("document_name", "Unknown")}

DOCUMENT ID:
{metadata.get("doc_id", "Unknown")}

DOCUMENT DATE:
{metadata.get("document_date", "Unknown")}

PAGE:
{metadata.get("page", "Unknown")}

CONTENT:
{document.page_content}
"""
            )

            sources.append(
                {
                    "document_id": metadata.get(
                        "doc_id"
                    ),
                    "document_name": metadata.get(
                        "document_name"
                    ),
                    "document_date": metadata.get(
                        "document_date"
                    ),
                    "page": metadata.get(
                        "page"
                    ),
                }
            )

        context = "\n".join(
            context_parts
        )


        # 5. Generate grounded answer

        answer = self.generator.generate(
            question=question,
            context=context,
        )

        return {
            "answer": answer,
            "sources": sources,
            "conflict_detected": conflict_detected,
        }