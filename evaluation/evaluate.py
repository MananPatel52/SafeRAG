import json
import statistics
import time
from pathlib import Path

from app.reasoning.rag_pipeline import SafeRAGPipeline
from app.retrieval.retriever import RetrieverService


EVAL_FILE = Path(__file__).with_name("eval_dataset.json")


def load_dataset():
    """Load the evaluation cases."""
    with open(EVAL_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize(text):
    """Normalize text for deterministic comparisons."""
    return " ".join(text.lower().split())


def calculate_faithfulness(answer, expected_phrases):
    """
    Lightweight faithfulness proxy.

    An answer is considered faithful when all expected
    evidence phrases are present in the generated answer.
    """
    if not expected_phrases:
        return 1.0

    normalized_answer = normalize(answer)

    matched = sum(
        normalize(phrase) in normalized_answer
        for phrase in expected_phrases
    )

    return matched / len(expected_phrases)


def calculate_context_precision(
    retrieved_documents,
    expected_source_ids,
):
    """
    Context precision:

        relevant retrieved documents
        ----------------------------
        total retrieved documents

    A retrieved document is relevant when its doc_id
    appears in the expected source IDs.
    """
    if not retrieved_documents:
        return 0.0

    expected = set(expected_source_ids)

    relevant = sum(
        1
        for document in retrieved_documents
        if document.metadata.get("doc_id") in expected
    )

    return relevant / len(retrieved_documents)


def calculate_citation_accuracy(
    sources,
    expected_source_ids,
):
    """
    Measure whether returned citations point to
    expected evidence documents.
    """
    expected = set(expected_source_ids)

    if not expected:
        return 1.0 if not sources else 0.0

    if not sources:
        return 0.0

    cited_ids = {
        source.get("document_id")
        for source in sources
        if source.get("document_id")
    }

    correct = cited_ids.intersection(expected)

    return len(correct) / len(expected)


def calculate_refusal_correctness(
    answer,
    sources,
    should_refuse,
    expected_phrases,
):
    """
    Check whether the system correctly refuses
    unsupported questions.
    """
    if not should_refuse:
        return None

    normalized_answer = normalize(answer)

    phrase_match = all(
        normalize(phrase) in normalized_answer
        for phrase in expected_phrases
    )

    no_sources = len(sources) == 0

    return 1.0 if phrase_match and no_sources else 0.0


def evaluate_case(pipeline, retriever, case):
    """
    Evaluate one query and return metric results
    together with end-to-end latency.
    """

    question = case["question"]
    department = case.get("department")
    document_type = case.get("document_type")

    # Retrieve separately so context precision can be measured.
    retrieved_documents = retriever.retrieve(
        query=question,
        department=department,
        document_type=document_type,
    )

    # Measure complete pipeline latency.
    start = time.perf_counter()

    result = pipeline.ask(
        question=question,
        department=department,
        document_type=document_type,
    )

    elapsed_ms = (time.perf_counter() - start) * 1000

    answer = result.get("answer", "")
    sources = result.get("sources", [])

    faithfulness = calculate_faithfulness(
        answer,
        case["expected_answer_contains"],
    )

    context_precision = calculate_context_precision(
        retrieved_documents,
        case["expected_source_ids"],
    )

    citation_accuracy = calculate_citation_accuracy(
        sources,
        case["expected_source_ids"],
    )

    refusal_correctness = calculate_refusal_correctness(
        answer,
        sources,
        case["should_refuse"],
        case["expected_answer_contains"],
    )

    return {
        "faithfulness": faithfulness,
        "context_precision": context_precision,
        "citation_accuracy": citation_accuracy,
        "refusal_correctness": refusal_correctness,
        "latency_ms": elapsed_ms,
    }


def percentile(values, percentile_value):
    """Calculate a percentile without external dependencies."""
    if not values:
        return 0.0

    values = sorted(values)

    if len(values) == 1:
        return values[0]

    position = (len(values) - 1) * percentile_value

    lower = int(position)
    upper = min(lower + 1, len(values) - 1)

    weight = position - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * weight
    )


def main():
    dataset = load_dataset()

    pipeline = SafeRAGPipeline()
    retriever = RetrieverService()

    faithfulness_scores = []
    context_precision_scores = []
    citation_accuracy_scores = []
    refusal_scores = []
    latency_values = []

    print("Running SafeRAG evaluation...")
    print(f"Evaluation cases: {len(dataset)}")
    print()

    for case in dataset:

        print(f"Evaluating: {case['id']}")

        metrics = evaluate_case(
            pipeline,
            retriever,
            case,
        )

        faithfulness_scores.append(
            metrics["faithfulness"]
        )

        context_precision_scores.append(
            metrics["context_precision"]
        )

        citation_accuracy_scores.append(
            metrics["citation_accuracy"]
        )

        latency_values.append(
            metrics["latency_ms"]
        )

        if metrics["refusal_correctness"] is not None:
            refusal_scores.append(
                metrics["refusal_correctness"]
            )

        print(
            f"  faithfulness: "
            f"{metrics['faithfulness']:.2f}"
        )

        print(
            f"  context_precision: "
            f"{metrics['context_precision']:.2f}"
        )

        print(
            f"  citation_accuracy: "
            f"{metrics['citation_accuracy']:.2f}"
        )

        if metrics["refusal_correctness"] is not None:
            print(
                f"  refusal_correctness: "
                f"{metrics['refusal_correctness']:.2f}"
            )

        print(
            f"  latency: "
            f"{metrics['latency_ms']:.2f} ms"
        )

        print()

    results = {
        "faithfulness": round(
            statistics.mean(faithfulness_scores),
            4,
        ),
        "context_precision": round(
            statistics.mean(context_precision_scores),
            4,
        ),
        "correct_refusal_rate": round(
            statistics.mean(refusal_scores)
            if refusal_scores
            else 0.0,
            4,
        ),
        "citation_accuracy": round(
            statistics.mean(citation_accuracy_scores),
            4,
        ),
        "p50_latency_ms": round(
            percentile(latency_values, 0.50),
            2,
        ),
        "p95_latency_ms": round(
            percentile(latency_values, 0.95),
            2,
        ),
    }

    print("=" * 60)
    print("FINAL EVALUATION")
    print("=" * 60)

    print(
        json.dumps(
            results,
            indent=2,
        )
    )

    output_file = Path(__file__).with_name(
        "evaluation_results.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
        )

    print()
    print(
        f"Results saved to: {output_file}"
    )


if __name__ == "__main__":
    main()