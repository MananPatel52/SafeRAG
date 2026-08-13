from datetime import datetime
import re
from typing import List, Optional

from langchain_core.documents import Document


class TemporalResolver:
    """
    Resolves conflicting documents using the time period
    requested by the user.

    Behavior:
    - Historical question -> select document matching requested month/year.
    - No historical date -> select latest document.
    """

    def _extract_requested_date(
        self,
        question: str,
    ) -> Optional[datetime]:
        """
        Extract a month/year from the user's question.

        Example:
            "What was the policy in January 2026?"
            -> 2026-01-01
        """

        month_pattern = (
            r"(January|February|March|April|May|June|July|"
            r"August|September|October|November|December)"
            r"\s+(\d{4})"
        )

        match = re.search(
            month_pattern,
            question,
            re.IGNORECASE,
        )

        if match:

            month_name = match.group(1)
            year = int(match.group(2))

            try:

                return datetime.strptime(
                    f"{month_name} {year}",
                    "%B %Y",
                )

            except ValueError:
                return None

        # Also support YYYY-MM format.
        numeric_pattern = r"\b(\d{4})-(\d{2})\b"

        match = re.search(
            numeric_pattern,
            question,
        )

        if match:

            year = int(match.group(1))
            month = int(match.group(2))

            try:

                return datetime(
                    year=year,
                    month=month,
                    day=1,
                )

            except ValueError:
                return None

        return None

    def resolve(
        self,
        documents: List[Document],
        question: Optional[str] = None,
    ) -> Optional[Document]:
        """
        Select the most appropriate document.

        If the question contains a historical month/year,
        select the document matching that period.

        Otherwise, select the latest dated document.
        """

        if not documents:
            return None

        # Deduplicate documents by document ID.
        unique_documents = {}

        for document in documents:

            doc_id = document.metadata.get(
                "doc_id"
            )

            if doc_id:
                unique_documents[doc_id] = document

        candidates = list(
            unique_documents.values()
        )

        if not candidates:
            return None

        dated_documents = []

        for document in candidates:

            date_value = document.metadata.get(
                "document_date"
            )

            if not date_value:
                continue

            try:

                parsed_date = datetime.fromisoformat(
                    date_value
                )

                dated_documents.append(
                    (
                        parsed_date,
                        document,
                    )
                )

            except ValueError:
                continue

        if not dated_documents:
            return candidates[0]

        
        # Historical query handling

        requested_date = None

        if question:

            requested_date = (
                self._extract_requested_date(
                    question
                )
            )

        if requested_date:

            matching_documents = [
                (
                    document_date,
                    document,
                )
                for document_date, document
                in dated_documents
                if (
                    document_date.year
                    == requested_date.year
                    and document_date.month
                    == requested_date.month
                )
            ]

            if matching_documents:

                # If multiple documents exist in the
                # requested month, choose the latest one.
                matching_documents.sort(
                    key=lambda item: item[0],
                    reverse=True,
                )

                return matching_documents[0][1]

        
        # Default behavior: latest document

        dated_documents.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return dated_documents[0][1]