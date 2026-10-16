"""Modular LLM provider layer supporting Google Gemini with local extractive fallback."""
import os
import re
import logging
from typing import Optional, List
from .prompts import SYSTEM_PROMPT, format_qa_prompt

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _local_fallback_answer(question: str, context: str) -> str:
    """
    Fallback contextual extractor when GEMINI_API_KEY is not yet configured.
    Respects the strict requirement:
    If context lacks sufficient facts, responds:
    'I could not find enough information in the uploaded documents to answer this question.'
    """
    if not context or context.strip() == "No relevant context found.":
        return "I could not find enough information in the uploaded documents to answer this question."

    # Extract non-stopword tokens from question
    stop_words = {
        "what", "is", "the", "of", "and", "a", "an", "in", "to", "for", "how",
        "does", "are", "this", "that", "it", "with", "as", "by", "on", "at",
        "from", "which", "or", "be", "was", "were", "can", "could", "would",
        "should", "tell", "me", "about", "describe", "explain"
    }

    q_words = re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", question.lower())
    informative_tokens = [w for w in q_words if w not in stop_words]

    # If completely unrelated terms like 'japan', 'population', 'weather', 'recipe'
    # don't exist anywhere in the context
    context_lower = context.lower()
    matches = [t for t in informative_tokens if t in context_lower]

    # If none or very few keywords match, strictly declare information not found
    if not matches:
        return "I could not find enough information in the uploaded documents to answer this question."

    # Split context into sentences
    # Clean source headers out of sentence splitting
    clean_ctx = re.sub(r"\[Source \d+ \|.*?\]", "", context)
    clean_ctx = re.sub(r"-{10,}", "", clean_ctx)

    sentences = re.split(r"(?<=[.!?])\s+", clean_ctx)
    scored_sentences = []

    for s in sentences:
        s_clean = s.strip()
        if len(s_clean) < 20:
            continue
        s_lower = s_clean.lower()
        score = sum(1 for t in informative_tokens if t in s_lower)
        if score > 0:
            scored_sentences.append((score, s_clean))

    if not scored_sentences:
        return "I could not find enough information in the uploaded documents to answer this question."

    # Sort by relevance to question tokens
    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    top_sentences = [s[1] for s in scored_sentences[:3]]
    synthesized = " ".join(top_sentences)

    note = (
        "\n\n*(Note: Generated using local contextual extractor. "
        "To enable live Google Gemini AI answers, enter your GEMINI_API_KEY in Settings or in .env)*"
    )

    return synthesized + note


def generate_answer(
    question: str,
    context: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> str:
    """
    Generates an answer using Google Gemini based strictly on the retrieved context.
    Handles missing keys, invalid keys, and network issues gracefully without raising
    raw stack traces.
    """
    effective_api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
    effective_model = model_name or os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip()

    # If context is blank or indicates no chunks found
    if not context or context.strip() == "No relevant context found.":
        return "I could not find enough information in the uploaded documents to answer this question."

    # If API key is not yet set or is the placeholder string
    has_valid_key = bool(
        effective_api_key
        and effective_api_key != "your_api_key_here"
        and effective_api_key != "your_gemini_api_key_here"
    )

    if not has_valid_key:
        logger.info("No Gemini API key provided. Using local extractive fallback.")
        return _local_fallback_answer(question, context)

    # Call Gemini API
    user_prompt = format_qa_prompt(question, context)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=effective_api_key)

        response = client.models.generate_content(
            model=effective_model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,  # Low temperature for strict factual accuracy
                max_output_tokens=1024,
            )
        )

        if response and response.text:
            return response.text.strip()
        else:
            return "I could not find enough information in the uploaded documents to answer this question."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Gemini generation error: {error_msg}")

        # Check for specific common error scenarios
        if "API_KEY_INVALID" in error_msg or "invalid api key" in error_msg.lower() or "400" in error_msg or "403" in error_msg:
            return (
                "⚠️ **Gemini API Authentication Error**\n\n"
                "The provided Gemini API key appears to be invalid or expired. "
                "Please verify your key in Google AI Studio (https://aistudio.google.com/) "
                "and update it in the **Settings** panel."
            )
        elif "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
            return (
                "⚠️ **Gemini API Rate Limit Exceeded**\n\n"
                "The Gemini API rate limit or quota has been reached. Please wait a few moments before submitting another question."
            )
        elif "model not found" in error_msg.lower() or "not supported" in error_msg.lower():
            return (
                f"⚠️ **Model Unavailable**\n\n"
                f"The model `{effective_model}` could not be found or is not supported. "
                "Try switching to `gemini-2.5-flash` or `gemini-1.5-flash` in Settings."
            )
        else:
            logger.warning("Falling back to local contextual extraction due to LLM error.")
            return _local_fallback_answer(question, context)
