from dataclasses import dataclass
from typing import Dict, Any
from typing import Optional, List
from pydantic import BaseModel


@dataclass
class DocumentChunk:
    """
    Represents one chunk of text extracted from a source document.

    Each chunk contains both the text and provenance metadata.
    """

    text: str
    metadata: Dict[str, Any]

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """
    Request body for the SafeRAG query endpoint.
    """

    question: str = Field(
        ...,
        min_length=3,
        description="Question to ask against the document knowledge base."
    )

    department: Optional[str] = None

    document_type: Optional[str] = None


class Source(BaseModel):
    """
    Source document returned with the answer.
    """

    document_id: Optional[str] = None
    document_name: Optional[str] = None
    document_date: Optional[str] = None
    page: Optional[int] = None


class QueryResponse(BaseModel):
    """
    Response returned by the SafeRAG query endpoint.
    """

    answer: str
    sources: List[Source]
    conflict_detected: bool