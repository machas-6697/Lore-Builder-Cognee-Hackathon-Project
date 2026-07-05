"""
llm_client.py – OpenRouter LLM Client
=======================================
Wraps the OpenRouter API (OpenAI-compatible) to produce answers
strictly grounded in Cognee memory context.

The system prompt is engineered to:
  1. Refuse to hallucinate information not present in the context.
  2. Answer only from the retrieved world lore knowledge.
  3. Stay in character as a world-lore narrator.

Uses the standard `openai` SDK pointed at the OpenRouter base URL.
"""

import logging
import time
from typing import Optional

from openai import OpenAI

from Backend.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# OpenAI-compatible client pointed at OpenRouter
# ------------------------------------------------------------------
_client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
)

# ------------------------------------------------------------------
# Retry helper for 429 / rate-limit errors
# ------------------------------------------------------------------
def _call_with_retry(fn, max_retries: int = 3, base_wait: float = 10.0):
    """
    Calls fn() and retries up to max_retries times if a 429 rate-limit
    error is returned. Uses exponential backoff: 10s, 20s, 40s...
    Raises the last exception if all retries are exhausted.
    """
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as exc:
            err_str = str(exc)
            # Detect 429 rate-limit error
            if "429" in err_str and attempt < max_retries - 1:
                wait_time = base_wait * (2 ** attempt)  # 10s, 20s, 40s
                logger.warning(
                    "Rate limit (429) on attempt %d/%d. Retrying in %.0fs...",
                    attempt + 1, max_retries, wait_time
                )
                time.sleep(wait_time)
            else:
                raise

_ASK_SYSTEM_PROMPT = """You are a precise World Lore Narrator for the LoreBuilder application.

Your ONLY source of truth is the WORLD CONTEXT provided to you below the user's question.
You must STRICTLY follow these rules:
1. Answer ONLY using information explicitly present in the WORLD CONTEXT.
2. If the answer is not in the WORLD CONTEXT, respond with:
   "I don't have enough lore knowledge to answer that question for this world."
3. Do NOT invent, speculate, or add any information beyond what is in the WORLD CONTEXT.
4. Be immersive and narrative — write as a knowledgeable chronicler of this fictional world.
5. Keep your answer concise and relevant.
"""

_UPDATE_SYSTEM_PROMPT = """You are a World Lore Expansion Writer for the LoreBuilder application.

Your task is to CREATE NEW LORE content for a fictional world, based on:
  - The WORLD CONTEXT: existing established lore for this world.
  - The USER REQUEST: what new story element or lore the user wants to add.

Rules:
1. Your new content MUST be consistent with the WORLD CONTEXT. Do not contradict established lore.
2. Write in a rich, descriptive narrative style appropriate for world-building.
3. The output will be DIRECTLY SAVED as new memory — make it factual lore, not a conversation.
4. Keep the response focused and under 300 words.
5. Do NOT reference the user's request in your output — write as if this is an official lore entry.
"""


# ------------------------------------------------------------------
# Public function: Ask Question
# ------------------------------------------------------------------
def ask_question(world_context: str, user_query: str) -> str:
    """
    Answers the user's question strictly based on the world context
    retrieved from Cognee memory.

    Args:
        world_context: Text retrieved via cognee.recall()
        user_query:    The user's question about the world

    Returns:
        LLM-generated answer grounded strictly in world_context.
    """
    if not world_context.strip():
        return (
            "No world knowledge was retrieved from memory. "
            "Please ensure the world has been initialized first."
        )

    user_message = (
        f"WORLD CONTEXT:\n{world_context}\n\n"
        f"QUESTION: {user_query}"
    )

    logger.info("ask_question: sending request to OpenRouter (%s)", OPENROUTER_MODEL)
    try:
        def _call():
            return _client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": _ASK_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
                max_tokens=1024,
            )
        response = _call_with_retry(_call)
        answer = response.choices[0].message.content
        logger.info("ask_question: received response (%d chars)", len(answer))
        return answer
    except Exception as exc:
        logger.error("ask_question failed: %s", exc)
        raise


# ------------------------------------------------------------------
# Public function: Update World (Generate New Lore)
# ------------------------------------------------------------------
def generate_world_update(world_context: str, user_request: str) -> str:
    """
    Generates new lore content consistent with the existing world context,
    based on the user's expansion request.

    The returned text is what will be stored into Cognee memory.

    Args:
        world_context:  Text retrieved via cognee.recall()
        user_request:   The user's prompt describing new lore to add

    Returns:
        New lore text generated by the LLM (to be remembered by Cognee).
    """
    user_message = (
        f"WORLD CONTEXT:\n{world_context}\n\n"
        f"USER REQUEST: {user_request}"
    )

    logger.info("generate_world_update: sending request to OpenRouter (%s)", OPENROUTER_MODEL)
    try:
        def _call():
            return _client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": _UPDATE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.7,
                max_tokens=512,
            )
        response = _call_with_retry(_call)
        new_lore = response.choices[0].message.content
        logger.info("generate_world_update: generated %d chars of new lore", len(new_lore))
        return new_lore
    except Exception as exc:
        logger.error("generate_world_update failed: %s", exc)
        raise
