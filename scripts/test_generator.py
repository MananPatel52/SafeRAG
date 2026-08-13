from app.reasoning.generator import GeminiGenerator


def main():

    generator = GeminiGenerator()

    question = (
        "What is the hospital employee salary "
        "for a senior pharmacist?"
    )

    context = """
Document: 04_pharmacy_policy_march_update.pdf
Document ID: PHARM-2026-03
Document Date: 2026-03-15

The target dispensing time for standard medication
orders is reduced from 30 minutes to 20 minutes.

This document supersedes the previous 30-minute target
for standard medication orders.

This is the current pharmacy dispensing target as of
the effective date of this policy.
"""

    answer = generator.generate(
        question=question,
        context=context,
    )

    print("\nGEMINI RESPONSE")
    print("=" * 60)
    print(answer)


if __name__ == "__main__":
    main()