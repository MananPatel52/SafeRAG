from app.retrieval.retriever import RetrieverService


def main():

    retriever = RetrieverService()

    question = (
        "What is the current pharmacy "
        "dispensing target?"
    )

    results = retriever.retrieve(
        query=question,
        department="pharmacy",
    )

    print("\nRETRIEVAL RESULTS")
    print("=" * 60)

    for index, document in enumerate(
        results,
        start=1,
    ):

        print(f"\nResult {index}")

        print(
            "Metadata:",
            document.metadata,
        )

        print(
            "Content:",
            document.page_content[:500],
        )


if __name__ == "__main__":
    main()