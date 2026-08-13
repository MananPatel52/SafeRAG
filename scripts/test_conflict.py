from app.reasoning.conflict import ConflictDetector
from app.retrieval.retriever import RetrieverService


def main():

    retriever = RetrieverService()

    question = (
        "What is the current pharmacy "
        "dispensing target?"
    )

    documents = retriever.retrieve(
        query=question,
        department="pharmacy",
    )

    detector = ConflictDetector()

    result = detector.detect(
        documents
    )

    print("\nCONFLICT DETECTION")
    print("=" * 60)

    print(
        "Conflict detected:",
        result["has_conflict"],
    )

    for conflict in result["conflicts"]:

        print(
            "\nConflict group:",
            conflict["group"],
        )

        print(
            "Document IDs:",
            conflict["document_ids"],
        )

        print(
            "Document dates:",
            conflict["document_dates"],
        )


if __name__ == "__main__":
    main()