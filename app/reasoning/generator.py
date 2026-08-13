from google import genai

from app.config.settings import settings


class GeminiGenerator:
    """
    Generates grounded answers using only the
    supplied retrieved and resolved context.
    """

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    def generate(
        self,
        question: str,
        context: str,
    ) -> str:

        prompt = f"""
You are a grounded document question-answering assistant.

Your job is to answer the user's question using ONLY
the information provided in the CONTEXT.

IMPORTANT RULES:

1. Do not use outside knowledge.
2. Do not invent facts, numbers, dates, policies, or sources.
3. If the context does not contain enough information,
   say exactly:
   "I couldn't find sufficient information in the provided documents."
4. If the context contains conflicting information,
   use the already-resolved authoritative information.
5. Prefer the latest explicitly effective policy when provided.
6. Keep the answer concise and factual.
7. Do not mention information that is not supported by
   the provided context.

USER QUESTION:
{question}

CONTEXT:
{context}

ANSWER:
"""

        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )

        return response.text.strip()