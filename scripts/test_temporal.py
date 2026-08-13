from app.reasoning.temporal import TemporalResolver
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

    resolver = TemporalResolver()

    latest = resolver.resolve(
        documents
    )

    print("\nTEMPORAL RESOLUTION")
    print("=" * 60)

    if latest is None:

        print(
            "No authoritative document found."
        )

        return

    print(
        "Selected document:",
        latest.metadata.get(
            "doc_id"
        ),
    )

    print(
        "Document date:",
        latest.metadata.get(
            "document_date"
        ),
    )

    print(
        "Source:",
        latest.metadata.get(
            "source"
        ),
    )

    print(
        "\nContent:"
    )

    print(
        latest.page_content
    )


if __name__ == "__main__":
    main()