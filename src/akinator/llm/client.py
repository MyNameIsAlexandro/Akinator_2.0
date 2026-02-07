"""LLM Client — OpenAI API wrapper."""

from __future__ import annotations

import json

import numpy as np

from akinator.config import EMBEDDING_DIM


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
