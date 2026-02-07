"""LLM Client — OpenAI API wrapper. (Stub — TDD.)"""

from __future__ import annotations

import numpy as np


class LLMClient:

    def __init__(self, api_key: str):
        self.api_key = api_key

    @staticmethod
    def _get_openai_client():
        raise NotImplementedError

    async def get_embedding(self, text: str) -> np.ndarray:
        raise NotImplementedError

    async def format_question(
        self, attribute_key: str, default_question: str, language: str = "en",
    ) -> str:
        raise NotImplementedError

    async def extract_attributes(
        self, description: str, attribute_keys: list[str],
    ) -> dict[str, float]:
        raise NotImplementedError

    async def explain_reasoning(
        self,
        top_candidates: list[tuple[str, float]],
        history: list[tuple[str, str]],
        language: str = "en",
    ) -> str:
        raise NotImplementedError
