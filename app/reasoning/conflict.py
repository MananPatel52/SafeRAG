from collections import defaultdict
from datetime import datetime
from typing import List

from langchain_core.documents import Document


class ConflictDetector:
    """
    Detects whether retrieved documents contain
    multiple versions of the same policy/document type.
    """

    def detect(
        self,
        documents: List[Document],
    ) -> dict:

        grouped_documents = defaultdict(list)

        for document in documents:

            metadata = document.metadata

            department = metadata.get(
                "department"
            )

            document_type = metadata.get(
                "document_type"
            )

            if not department:
                continue

            # Normalize policy updates into the
            # same policy category.
            if document_type in {
                "policy",
                "policy_update",
            }:
                document_type = "policy"

            key = (
                department,
                document_type,
            )

            grouped_documents[key].append(
                document
            )

        conflicts = []

        for key, docs in grouped_documents.items():

            document_ids = {
                doc.metadata.get("doc_id")
                for doc in docs
                if doc.metadata.get("doc_id")
            }

            dates = []

            for doc in docs:

                date_value = doc.metadata.get(
                    "document_date"
                )

                if date_value:

                    try:
                        parsed_date = datetime.fromisoformat(
                            date_value
                        )

                        dates.append(
                            parsed_date
                        )

                    except ValueError:
                        continue

            if len(document_ids) > 1:

                conflicts.append(
                    {
                        "group": key,
                        "document_ids": list(
                            document_ids
                        ),
                        "document_dates": [
                            date.isoformat()
                            for date in dates
                        ],
                    }
                )

        return {
            "has_conflict": len(conflicts) > 0,
            "conflicts": conflicts,
        }