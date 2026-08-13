from app.reasoning.rag_pipeline import SafeRAGPipeline


def main():

    pipeline = SafeRAGPipeline()

    question = (
        "What is the current pharmacy "
        "dispensing target?"
    )

    result = pipeline.ask(
        question=question,
        department="pharmacy",
    )

    print("\nSAFE RAG RESPONSE")
    print("=" * 60)

    print("\nAnswer:")
    print(result["answer"])

    print(
        "\nConflict detected:",
        result["conflict_detected"],
    )

    print("\nSources:")

    for source in result["sources"]:

        print(
            f"- {source['document_name']} "
            f"(ID: {source['document_id']}, "
            f"Date: {source['document_date']}, "
            f"Page: {source['page']})"
        )


if __name__ == "__main__":
    main()