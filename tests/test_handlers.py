"""Tests for Telegram Bot Handlers.

Covers:
- /start command
- /new command (start game)
- Answer callback handling
- Guess confirmation callbacks
- /top command
- /why command
- /giveup command
- /lang command
- Error handling (no active session, etc.)

Note: These tests use mocked aiogram objects and do NOT require a real Telegram connection.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from akinator.db.models import Answer, GameMode, GameSession


class TestStartCommand:
    """The /start command sends a welcome message."""

    @pytest.mark.asyncio
    async def test_start_sends_welcome(self):
        from akinator.bot.handlers import handle_start

        message = AsyncMock()
        message.from_user = MagicMock(id=42, language_code="ru")
        await handle_start(message)
        message.answer.assert_called_once()
        call_text = message.answer.call_args[0][0]
        # Should contain some welcome text
        assert len(call_text) > 0


class TestNewGameCommand:
    """The /new command creates a new game session."""

    @pytest.mark.asyncio
    async def test_new_creates_session(self):
        from akinator.bot.handlers import handle_new

        message = AsyncMock()
        message.from_user = MagicMock(id=42, language_code="en")

        session_store = {}
        with patch("akinator.bot.handlers.get_session_store", return_value=session_store):
            await handle_new(message)

        message.answer.assert_called()
        # A session should be stored
        assert 42 in session_store
        assert session_store[42].mode in (GameMode.WAITING_HINT, GameMode.ASKING)


class TestAnswerCallbacks:
    """Inline button answer callbacks."""

    @pytest.mark.asyncio
    async def test_yes_answer_callback(self):
        from akinator.bot.handlers import handle_answer_callback

        callback = AsyncMock()
        callback.from_user = MagicMock(id=42)
        callback.data = "answer:yes"

        session = GameSession(
            session_id="test", user_id=42,
            candidate_ids=[1, 2, 3], weights=[0.4, 0.3, 0.3],
            mode=GameMode.ASKING, question_count=1,
        )
        session_store = {42: session}

        with patch("akinator.bot.handlers.get_session_store", return_value=session_store), \
             patch("akinator.bot.handlers.get_entities") as mock_entities, \
             patch("akinator.bot.handlers.get_attributes") as mock_attrs:
            mock_entities.return_value = []
            mock_attrs.return_value = []
            await handle_answer_callback(callback)

        callback.answer.assert_called()

    @pytest.mark.asyncio
    async def test_answer_without_session_shows_error(self):
        from akinator.bot.handlers import handle_answer_callback

        callback = AsyncMock()
        callback.from_user = MagicMock(id=42)
        callback.data = "answer:yes"

        session_store = {}  # No session for user 42

        with patch("akinator.bot.handlers.get_session_store", return_value=session_store):
            await handle_answer_callback(callback)

        # Should notify user about missing session
        callback.answer.assert_called()


class TestGuessCallbacks:
    """Guess confirmation button callbacks."""

    @pytest.mark.asyncio
    async def test_correct_guess_finishes_game(self):
        from akinator.bot.handlers import handle_guess_callback

        callback = AsyncMock()
        callback.from_user = MagicMock(id=42)
        callback.data = "guess:correct"
        callback.message = AsyncMock()

        session = GameSession(
            session_id="test", user_id=42,
            candidate_ids=[1], weights=[1.0],
            mode=GameMode.GUESSING,
        )
        session_store = {42: session}

        with patch("akinator.bot.handlers.get_session_store", return_value=session_store):
            await handle_guess_callback(callback)

        assert session.mode == GameMode.FINISHED

    @pytest.mark.asyncio
    async def test_wrong_guess_transitions_state(self):
        from akinator.bot.handlers import handle_guess_callback

        callback = AsyncMock()
        callback.from_user = MagicMock(id=42)
        callback.data = "guess:wrong"
        callback.message = AsyncMock()

        session = GameSession(
            session_id="test", user_id=42,
            candidate_ids=[1, 2, 3], weights=[0.5, 0.3, 0.2],
            mode=GameMode.GUESSING, guess_count=2,
        )
        session_store = {42: session}

        with patch("akinator.bot.handlers.get_session_store", return_value=session_store):
            await handle_guess_callback(callback)

        # After max guesses, should go to learning
        assert session.mode == GameMode.LEARNING


class TestTopCommand:
    """/top shows top candidates."""

    @pytest.mark.asyncio
    async def test_top_with_active_session(self):
        from akinator.bot.handlers import handle_top

        message = AsyncMock()
        message.from_user = MagicMock(id=42)

        session = GameSession(
            session_id="test", user_id=42,
            candidate_ids=[1, 2, 3], weights=[0.5, 0.3, 0.2],
            mode=GameMode.ASKING,
        )
        session_store = {42: session}

        with patch("akinator.bot.handlers.get_session_store", return_value=session_store), \
             patch("akinator.bot.handlers.get_entity_names", return_value={
                 1: "Vader", 2: "Mario", 3: "Elon",
             }):
            await handle_top(message)

        message.answer.assert_called_once()
        text = message.answer.call_args[0][0]
        assert "Vader" in text

    @pytest.mark.asyncio
    async def test_top_without_session_shows_error(self):
        from akinator.bot.handlers import handle_top

        message = AsyncMock()
        message.from_user = MagicMock(id=42)

        with patch("akinator.bot.handlers.get_session_store", return_value={}):
            await handle_top(message)

        message.answer.assert_called_once()


class TestGiveUpCommand:
    """/giveup transitions to learning mode."""

    @pytest.mark.asyncio
    async def test_giveup_enters_learning(self):
        from akinator.bot.handlers import handle_giveup

        message = AsyncMock()
        message.from_user = MagicMock(id=42)

        session = GameSession(
            session_id="test", user_id=42,
            candidate_ids=[1, 2], weights=[0.5, 0.5],
            mode=GameMode.ASKING,
        )
        session_store = {42: session}

        with patch("akinator.bot.handlers.get_session_store", return_value=session_store):
            await handle_giveup(message)

        assert session.mode == GameMode.LEARNING


class TestLangCommand:
    """/lang switches language."""

    @pytest.mark.asyncio
    async def test_lang_switches_to_en(self):
        from akinator.bot.handlers import handle_lang

        message = AsyncMock()
        message.from_user = MagicMock(id=42)
        message.text = "/lang en"

        session = GameSession(
            session_id="test", user_id=42,
            language="ru",
            candidate_ids=[], weights=[],
            mode=GameMode.WAITING_HINT,
        )
        session_store = {42: session}

        with patch("akinator.bot.handlers.get_session_store", return_value=session_store):
            await handle_lang(message)

        assert session.language == "en"
