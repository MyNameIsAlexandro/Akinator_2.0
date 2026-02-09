"""LLM Client — OpenAI API wrapper."""

from __future__ import annotations

import json
import logging

import numpy as np

from akinator.config import ATTRIBUTE_KEYS, EMBEDDING_DIM

logger = logging.getLogger(__name__)


class LLMClient:

    def __init__(self, api_key: str):
        self.api_key = api_key

    @staticmethod
    def _get_openai_client():
        from openai import AsyncOpenAI
        return AsyncOpenAI()

    async def get_embedding(self, text: str) -> np.ndarray:
        client = self._get_openai_client()
        response = await client.embeddings.create(
            input=text, model="text-embedding-3-small",
        )
        raw = response.data[0].embedding
        vec = np.array(raw, dtype=np.float32)
        # L2 normalize for cosine similarity
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    async def format_question(
        self, attribute_key: str, default_question: str, language: str = "en",
    ) -> str:
        client = self._get_openai_client()
        lang_name = "Russian" if language == "ru" else "English"
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    f"You are a question formatter for a guessing game. "
                    f"Rephrase the following yes/no question to sound natural in {lang_name}. "
                    f"Keep it short (one sentence). Return only the question text."
                )},
                {"role": "user", "content": f"Attribute: {attribute_key}\nDefault question: {default_question}"},
            ],
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()

    async def extract_attributes(
        self, description: str, attribute_keys: list[str],
    ) -> dict[str, float]:
        client = self._get_openai_client()
        keys_str = ", ".join(attribute_keys)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "You extract attribute probabilities from character descriptions. "
                    "Return a JSON object mapping attribute keys to float values (0.0-1.0). "
                    "Only return valid JSON, nothing else."
                )},
                {"role": "user", "content": (
                    f"Description: {description}\n"
                    f"Attributes to extract: {keys_str}"
                )},
            ],
            max_tokens=300,
        )
        text = response.choices[0].message.content.strip()
        try:
            result = json.loads(text)
            return {k: float(v) for k, v in result.items() if k in attribute_keys}
        except (json.JSONDecodeError, ValueError, TypeError):
            return {}

    async def correct_and_enrich(
        self,
        raw_name: str,
        qa_history: list[tuple[str, str]] | None = None,
    ) -> dict | None:
        """Correct spelling, provide bilingual names, and extract all attributes.

        Returns dict with keys: corrected_name, name_en, name_ru, description,
        entity_type, attributes (dict[str, float]), confidence.
        Returns None on failure.
        """
        client = self._get_openai_client()
        keys_str = ", ".join(ATTRIBUTE_KEYS)

        qa_context = ""
        if qa_history:
            lines = [f"- {q} → {a}" for q, a in qa_history[:15]]
            qa_context = "Context from the game (questions the user answered):\n" + "\n".join(lines)

        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": (
                        "You help identify characters and real people for a guessing game. "
                        "Given a name (possibly misspelled, in any language) and optional QA context, "
                        "you must:\n"
                        "1. Correct the spelling if needed and find the real character/person\n"
                        "2. Provide the canonical English name and Russian name\n"
                        "3. Provide a short description (1-2 sentences)\n"
                        "4. Classify as 'character' (fictional) or 'person' (real)\n"
                        "5. Rate ALL of these attributes from 0.0 to 1.0:\n"
                        f"   {keys_str}\n\n"
                        "Handle misspellings and transliterations. Examples:\n"
                        '- "Фонтомас" or "Фантамас" → corrected to "Фантомас" / "Fantomas"\n'
                        '- "Энштейн" → "Альберт Эйнштейн" / "Albert Einstein"\n'
                        '- "Iron Man" → "Железный человек" / "Iron Man"\n\n'
                        "Return ONLY valid JSON with this exact structure:\n"
                        '{"corrected_name": "...", "name_en": "...", "name_ru": "...", '
                        '"description": "...", "entity_type": "character"|"person", '
                        '"attributes": {"is_fictional": 0.0, ...}, "confidence": 0.95}'
                    )},
                    {"role": "user", "content": f"Entity name: {raw_name}\n\n{qa_context}".strip()},
                ],
                max_tokens=600,
                temperature=0.3,
            )
            text = response.choices[0].message.content.strip()
            # Strip markdown code block if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
            result = json.loads(text)

            # Validate required fields
            if not result.get("corrected_name"):
                result["corrected_name"] = raw_name
            if not result.get("name_en"):
                result["name_en"] = result["corrected_name"]
            if not result.get("name_ru"):
                result["name_ru"] = result["corrected_name"]
            result.setdefault("entity_type", "character")
            result.setdefault("description", "")
            result.setdefault("confidence", 0.5)

            # Normalize attributes
            attrs = result.get("attributes", {})
            result["attributes"] = {
                k: max(0.0, min(1.0, float(v)))
                for k, v in attrs.items()
                if k in ATTRIBUTE_KEYS
            }

            return result

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.warning("LLM returned invalid JSON for '%s': %s", raw_name, e)
            return None
        except Exception as e:
            logger.warning("LLM call failed for '%s': %s", raw_name, e)
            return None

    async def explain_reasoning(
        self,
        top_candidates: list[tuple[str, float]],
        history: list[tuple[str, str]],
        language: str = "en",
    ) -> str:
        client = self._get_openai_client()
        lang_name = "Russian" if language == "ru" else "English"
        candidates_str = "\n".join(
            f"- {name}: {prob:.1%}" for name, prob in top_candidates
        )
        history_str = "\n".join(
            f"- Q: {q} → A: {a}" for q, a in history
        )
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    f"Explain your reasoning in the guessing game in {lang_name}. "
                    f"Be concise (2-3 sentences)."
                )},
                {"role": "user", "content": (
                    f"Top candidates:\n{candidates_str}\n\n"
                    f"Question history:\n{history_str}"
                )},
            ],
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
