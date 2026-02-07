"""Telegram Bot Handlers."""

from __future__ import annotations

from akinator.db.models import GameMode, GameSession
from akinator.engine.scoring import ScoringEngine
from akinator.engine.session import GameSessionManager
from akinator.engine.question_policy import QuestionPolicy

_session_store: dict[int, GameSession] = {}
_session_manager = GameSessionManager(ScoringEngine(), QuestionPolicy())


def get_session_store() -> dict[int, GameSession]:
    return _session_store


def get_entities() -> list:
    return []


def get_attributes() -> list:
    return []


def get_entity_names(ids: list[int]) -> dict[int, str]:
    return {}


async def handle_start(message) -> None:
    text = (
        "Welcome to Akinator 2.0!\n\n"
        "Think of a character — real or fictional — and I'll try to guess who it is.\n"
        "Use /new to start a new game."
    )
    await message.answer(text)


async def handle_new(message) -> None:
    store = get_session_store()
    user_id = message.from_user.id
    session = _session_manager.create_session(user_id=user_id, language="ru")
    store[user_id] = session
    await message.answer(
        "Think of a character — real or fictional.\n"
        "Ready? You can give me a hint or we can start right away.",
    )


async def handle_answer_callback(callback) -> None:
    store = get_session_store()
    user_id = callback.from_user.id
    session = store.get(user_id)
    if session is None:
        await callback.answer("No game in progress. Use /new to start!")
        return
    await callback.answer("Got it!")


async def handle_guess_callback(callback) -> None:
    store = get_session_store()
    user_id = callback.from_user.id
    session = store.get(user_id)
    if session is None:
        await callback.answer("No game in progress.")
        return

    action = callback.data.split(":")[1]
    if action == "correct":
        _session_manager.handle_guess_response(session, correct=True)
        await callback.message.answer("I guessed it!")
    else:
        _session_manager.handle_guess_response(session, correct=False)
        if session.mode == GameMode.LEARNING:
            await callback.message.answer("I give up! Who were you thinking of?")
        else:
            await callback.message.answer("Let me try again...")
    await callback.answer()


async def handle_top(message) -> None:
    store = get_session_store()
    user_id = message.from_user.id
    session = store.get(user_id)
    if session is None:
        await message.answer("No game in progress. Use /new to start!")
        return

    names = get_entity_names([cid for cid in session.candidate_ids])
    scoring = ScoringEngine()
    top = scoring.top_k(session, k=5)
    lines = ["Top candidates:"]
    for i, (cid, w) in enumerate(top, 1):
        name = names.get(cid, f"#{cid}")
        lines.append(f"{i}. **{name}** — {w:.1%}")
    await message.answer("\n".join(lines))


async def handle_giveup(message) -> None:
    store = get_session_store()
    user_id = message.from_user.id
    session = store.get(user_id)
    if session is None:
        await message.answer("No game in progress. Use /new to start!")
        return
    session.mode = GameMode.LEARNING
    await message.answer("I give up! Who were you thinking of?")


async def handle_lang(message) -> None:
    store = get_session_store()
    user_id = message.from_user.id
    session = store.get(user_id)

    parts = message.text.split()
    lang = parts[1] if len(parts) > 1 else "ru"

    if session is not None:
        session.language = lang
    await message.answer(f"Language set to: {lang}")


async def handle_why(message) -> None:
    store = get_session_store()
    user_id = message.from_user.id
    session = store.get(user_id)
    if session is None:
        await message.answer("No game in progress. Use /new to start!")
        return
    await message.answer("Reasoning explanation will be here.")
