from pathlib import Path
from typing import Dict


DOCUMENT_REGISTRY = {
    "01_hospital_operations_january.pdf": {
        "doc_id": "OPS-2026-01",
        "document_type": "operations_report",
        "department": "hospital_operations",
        "document_date": "2026-01-15",
    },

    "02_patient_safety_report.pdf": {
        "doc_id": "SAFE-2026-02",
        "document_type": "safety_report",
        "department": "patient_safety",
        "document_date": "2026-02-10",
    },

    "03_pharmacy_policy_january.pdf": {
        "doc_id": "PHARM-2026-01",
        "document_type": "policy",
        "department": "pharmacy",
        "document_date": "2026-01-05",
    },

    "04_pharmacy_policy_march_update.pdf": {
        "doc_id": "PHARM-2026-03",
        "document_type": "policy_update",
        "department": "pharmacy",
        "document_date": "2026-03-15",
    },

    "05_quality_committee_notes.pdf": {
        "doc_id": "QUALITY-2026-03",
        "document_type": "committee_notes",
        "department": "quality_improvement",
        "document_date": "2026-03-18",
    },

    "06_department_guidelines.pdf": {
        "doc_id": "GUIDE-2026-02",
        "document_type": "guidelines",
        "department": "hospital_operations",
        "document_date": "2026-02-20",
    },

    "07_security_policy.pdf": {
        "doc_id": "SEC-2026-01",
        "document_type": "security_policy",
        "department": "information_security",
        "document_date": "2026-01-20",
    },

    "08_adversarial_document.pdf": {
        "doc_id": "ADV-2026-01",
        "document_type": "adversarial_test",
        "department": "unknown",
        "document_date": "2026-03-20",
    },
}


class MetadataBuilder:
    """
    Adds structured metadata to documents based on the source file.
    """

    def enrich(self, metadata: dict) -> dict:
        source = metadata["source"]

        filename = Path(source).name

        document_info = DOCUMENT_REGISTRY.get(filename)

        if document_info is None:
            raise ValueError(
                f"No metadata registered for document: {filename}"
            )

        enriched_metadata = {
            **metadata,
            "doc_id": document_info["doc_id"],
            "document_name": filename,
            "document_type": document_info["document_type"],
            "department": document_info["department"],
            "document_date": document_info["document_date"],
        }

        return enriched_metadata