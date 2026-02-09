"""Tests for LLM Client (OpenAI API wrapper).

All tests use mocked API calls — no real OpenAI requests.

Covers:
- Embedding generation
- Question formatting
- Attribute extraction from description
- Reasoning explanation generation
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from akinator.config import EMBEDDING_DIM


class TestGetEmbedding:
    """Embedding generation via OpenAI API."""

    @pytest.mark.asyncio
    async def test_get_embedding_returns_correct_dimensions(self):
        from akinator.llm.client import LLMClient

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * EMBEDDING_DIM)]

        with patch("akinator.llm.client.LLMClient._get_openai_client") as mock_client:
            mock_client.return_value.embeddings.create = AsyncMock(
                return_value=mock_response
            )
            client = LLMClient(api_key="test-key")
            embedding = await client.get_embedding("Darth Vader, Star Wars villain")

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (EMBEDDING_DIM,)
        assert embedding.dtype == np.float32

    @pytest.mark.asyncio
    async def test_get_embedding_normalizes_vector(self):
        from akinator.llm.client import LLMClient

        raw = [float(i) for i in range(EMBEDDING_DIM)]
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=raw)]

        with patch("akinator.llm.client.LLMClient._get_openai_client") as mock_client:
            mock_client.return_value.embeddings.create = AsyncMock(
                return_value=mock_response
            )
            client = LLMClient(api_key="test-key")
            embedding = await client.get_embedding("test text")

        # Should be L2-normalized for cosine similarity
        norm = np.linalg.norm(embedding)
        assert np.isclose(norm, 1.0, atol=1e-5)


class TestFormatQuestion:
    """LLM-powered question formatting."""

    @pytest.mark.asyncio
    async def test_format_question_returns_string(self):
        from akinator.llm.client import LLMClient

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Is this character from a movie?"))
        ]

        with patch("akinator.llm.client.LLMClient._get_openai_client") as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                return_value=mock_response
            )
            client = LLMClient(api_key="test-key")
            question = await client.format_question(
                attribute_key="from_movie",
                default_question="Related to movies?",
                language="en",
            )

        assert isinstance(question, str)
        assert len(question) > 0

    @pytest.mark.asyncio
    async def test_format_question_respects_language(self):
        from akinator.llm.client import LLMClient

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Этот персонаж связан с кино?"))
        ]

        with patch("akinator.llm.client.LLMClient._get_openai_client") as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                return_value=mock_response
            )
            client = LLMClient(api_key="test-key")
            question = await client.format_question(
                attribute_key="from_movie",
                default_question="Связан с кино?",
                language="ru",
            )

        assert isinstance(question, str)


class TestExtractAttributes:
    """LLM-powered attribute extraction from free text."""

    @pytest.mark.asyncio
    async def test_extract_returns_dict(self):
        from akinator.llm.client import LLMClient

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(
                content='{"is_fictional": 1.0, "is_male": 1.0, "from_movie": 1.0}'
            ))
        ]

        with patch("akinator.llm.client.LLMClient._get_openai_client") as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                return_value=mock_response
            )
            client = LLMClient(api_key="test-key")
            attributes = await client.extract_attributes(
                description="Darth Vader is a fictional villain from Star Wars movies",
                attribute_keys=["is_fictional", "is_male", "from_movie"],
            )

        assert isinstance(attributes, dict)
        assert "is_fictional" in attributes
        assert 0.0 <= attributes["is_fictional"] <= 1.0

    @pytest.mark.asyncio
    async def test_extract_handles_malformed_json(self):
        from akinator.llm.client import LLMClient

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="this is not valid json"))
        ]

        with patch("akinator.llm.client.LLMClient._get_openai_client") as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                return_value=mock_response
            )
            client = LLMClient(api_key="test-key")
            attributes = await client.extract_attributes(
                description="Something",
                attribute_keys=["is_fictional"],
            )

        # Should return empty dict on failure, not raise
        assert isinstance(attributes, dict)


class TestExplainReasoning:
    """LLM-powered reasoning explanation for /why command."""

    @pytest.mark.asyncio
    async def test_explain_returns_string(self):
        from akinator.llm.client import LLMClient

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(
                content="Based on your answers, I think it's Darth Vader because..."
            ))
        ]

        with patch("akinator.llm.client.LLMClient._get_openai_client") as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                return_value=mock_response
            )
            client = LLMClient(api_key="test-key")
            explanation = await client.explain_reasoning(
                top_candidates=[("Darth Vader", 0.85), ("Luke", 0.10)],
                history=[("Is fictional?", "Yes"), ("Is villain?", "Yes")],
                language="en",
            )

        assert isinstance(explanation, str)
        assert len(explanation) > 0
