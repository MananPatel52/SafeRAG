import logging
import time

from typing import Optional

from langchain_core import documents

from app.retrieval.retriever import RetrieverService
from app.reasoning.conflict import ConflictDetector
from app.reasoning.temporal import TemporalResolver
from app.reasoning.generator import GeminiGenerator
from app.observability.logger import log_event

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)


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

        # Start total query timer.
        total_query_start = time.perf_counter()

    
        # 1. Retrieve relevant documents

        retrieval_start = time.perf_counter()

        documents = self.retriever.retrieve(
            query=question,
            department=department,
            document_type=document_type,
        )

        retrieval_latency_ms = (
            time.perf_counter() - retrieval_start
        ) * 1000

        log_event(
            "retrieval_completed",
            latency_ms=round(retrieval_latency_ms, 2),
            documents_retrieved=len(documents),
            department=department,
            document_type=document_type,
        )


        # Handle no retrieval results

        if not documents:

            total_query_latency_ms = (
                time.perf_counter() - total_query_start
            ) * 1000

            log_event(
                "query_completed",
                latency_ms=round(
                    total_query_latency_ms,
                    2,
                ),
                documents_retrieved=0,
                conflict_detected=False,
            )

            return {
                "answer": (
                    "I couldn't find sufficient "
                    "information in the provided documents."
                ),
                "sources": [],
                "conflict_detected": False,
            }

    
        # 2. Detect conflicts

        conflict_start = time.perf_counter()

        conflict_result = (
            self.conflict_detector.detect(
                documents
            )
        )

        conflict_latency_ms = (
            time.perf_counter() - conflict_start
        ) * 1000

        conflict_detected = (
            conflict_result["has_conflict"]
        )

        log_event(
            "conflict_detection_completed",
            latency_ms=round(
                conflict_latency_ms,
                2,
            ),
            conflict_detected=conflict_detected,
        )

    
        # 3. Resolve authoritative document

        authoritative_document = None

        if conflict_detected:

            temporal_start = time.perf_counter()

            authoritative_document = (
                self.temporal_resolver.resolve(
                    documents,
                    question=question,
                )
            )

            temporal_latency_ms = (
                time.perf_counter()
                - temporal_start
            ) * 1000

            log_event(
                "temporal_resolution_completed",
                latency_ms=round(
                    temporal_latency_ms,
                    2,
                ),
                resolved_document_id=(
                    authoritative_document.metadata.get(
                        "doc_id"
                    )
                    if authoritative_document
                    else None
                ),
            )


        # Select documents for grounded context

        if conflict_detected and authoritative_document:

            context_documents = [
                authoritative_document
            ]


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

        context = "\n".join(context_parts)

    
        # 5. Generate grounded answer

        answer = self.generator.generate(
            question=question,
            context=context,
        )

   
        # 6. Total query timing

        total_query_latency_ms = (
            time.perf_counter()
            - total_query_start
        ) * 1000

        log_event(
            "query_completed",
            latency_ms=round(
                total_query_latency_ms,
                2
            ),
            documents_retrieved=len(documents),
            context_documents=len(context_documents),
            conflict_detected=conflict_detected,
        )

        return {
            "answer": answer,
            "sources": sources,
            "conflict_detected": conflict_detected,
        }