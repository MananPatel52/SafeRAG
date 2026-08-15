from unittest.mock import MagicMock, patch

from app.reasoning.generator import GeminiGenerator


def create_generator_with_mock_client():
    """
    Create GeminiGenerator with the real Gemini API replaced
    by a mock client.
    """

    mock_client = MagicMock()

    with patch(
        "app.reasoning.generator.genai.Client",
        return_value=mock_client,
    ):
        generator = GeminiGenerator()

    return generator, mock_client


def test_generator_returns_gemini_response():
    """
    Generator should return the text produced by Gemini.
    """

    generator, mock_client = create_generator_with_mock_client()

    mock_response = MagicMock()
    mock_response.text = "The pharmacy dispensing target is 20 minutes."

    mock_client.models.generate_content.return_value = mock_response

    result = generator.generate(
        question="What is the current pharmacy dispensing target?",
        context="The current pharmacy dispensing target is 20 minutes.",
    )

    assert result == "The pharmacy dispensing target is 20 minutes."


def test_generator_sends_question_and_context_to_gemini():
    """
    The user question and retrieved context should both be
    included in the prompt sent to Gemini.
    """

    generator, mock_client = create_generator_with_mock_client()

    mock_response = MagicMock()
    mock_response.text = "20 minutes."
    mock_client.models.generate_content.return_value = mock_response

    question = "What is the current pharmacy dispensing target?"
    context = "The current pharmacy dispensing target is 20 minutes."

    generator.generate(
        question=question,
        context=context,
    )

    call_kwargs = (
        mock_client.models.generate_content.call_args.kwargs
    )

    prompt = call_kwargs["contents"]

    assert question in prompt
    assert context in prompt


def test_generator_uses_configured_gemini_model():
    """
    Generator should use the model configured in application settings.
    """

    generator, mock_client = create_generator_with_mock_client()

    mock_response = MagicMock()
    mock_response.text = "20 minutes."
    mock_client.models.generate_content.return_value = mock_response

    generator.generate(
        question="What is the current pharmacy dispensing target?",
        context="The current pharmacy dispensing target is 20 minutes.",
    )

    call_kwargs = (
        mock_client.models.generate_content.call_args.kwargs
    )

    assert call_kwargs["model"] == "gemini-3.5-flash"


def test_generator_prompt_contains_grounding_rules():
    """
    The prompt should explicitly instruct Gemini to use only
    the supplied context and avoid unsupported information.
    """

    generator, mock_client = create_generator_with_mock_client()

    mock_response = MagicMock()
    mock_response.text = "20 minutes."
    mock_client.models.generate_content.return_value = mock_response

    generator.generate(
        question="What is the current pharmacy dispensing target?",
        context="The current pharmacy dispensing target is 20 minutes.",
    )

    call_kwargs = (
        mock_client.models.generate_content.call_args.kwargs
    )

    prompt = call_kwargs["contents"]

    assert "ONLY" in prompt
    assert "provided in the CONTEXT" in prompt
    assert "Do not use outside knowledge" in prompt
    assert "Do not invent facts" in prompt