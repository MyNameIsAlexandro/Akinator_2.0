"""Telegram Bot Handlers — wired to aiogram Router."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from akinator.bot.keyboards import answer_keyboard, guess_keyboard, hint_keyboard, new_game_keyboard
from akinator.config import GUESS_THRESHOLD, TOP_K_DISPLAY
from akinator.db.models import Answer, Attribute, Entity, GameMode, GameSession
from akinator.engine.scoring import ScoringEngine
from akinator.engine.session import GameSessionManager
from akinator.engine.question_policy import QuestionPolicy

logger = logging.getLogger(__name__)

router = Router()

# --- Global state (in-memory for MVP single instance) ---
_session_store: dict[int, GameSession] = {}
_entities: list[Entity] = []
_attributes: list[Attribute] = []
_entity_names: dict[int, str] = {}
_scoring_engine = ScoringEngine()
_question_policy = QuestionPolicy()
_session_manager = GameSessionManager(_scoring_engine, _question_policy)


def get_session_store() -> dict[int, GameSession]:
    return _session_store


def get_entities() -> list[Entity]:
    return _entities


def get_attributes() -> list[Attribute]:
    return _attributes


def get_entity_names(ids: list[int] | None = None) -> dict[int, str]:
    if ids is None:
        return _entity_names
    return {eid: _entity_names[eid] for eid in ids if eid in _entity_names}


def set_game_data(entities: list[Entity], attributes: list[Attribute]) -> None:
    """Called at startup to load game data into memory."""
    _entities.clear()
    _entities.extend(entities)
    _attributes.clear()
    _attributes.extend(attributes)
    _entity_names.clear()
    for e in entities:
        _entity_names[e.id] = e.name


def _get_lang(session: GameSession | None, message_or_callback=None) -> str:
    if session:
        return session.language
    return "ru"


def _attr_question(attr: Attribute, lang: str) -> str:
    return attr.question_ru if lang == "ru" else attr.question_en


def _find_attr_by_key(key: str) -> Attribute | None:
    for a in _attributes:
        if a.key == key:
            return a
    return None


# ──────────────────────────────────────────────
# Command handlers
# ──────────────────────────────────────────────

@router.message(Command("start"))
async def handle_start(message: Message) -> None:
    text = (
        "Welcome to Akinator 2.0!\n\n"
        "Think of a character — real or fictional — and I'll try to guess who it is.\n"
        "Use /new to start a new game."
    )
    await message.answer(text)


@router.message(Command("new"))
async def handle_new(message: Message) -> None:
    store = get_session_store()
    user_id = message.from_user.id
    lang = store[user_id].language if user_id in store else "ru"
    session = _session_manager.create_session(user_id=user_id, language=lang)
    store[user_id] = session

    if lang == "ru":
        text = (
            "Загадайте персонажа — реального или вымышленного.\n"
            "Можете дать подсказку (описание в 1 фразе, без имени) или пропустить."
        )
    else:
        text = (
            "Think of a character — real or fictional.\n"
            "You can give me a hint (describe in 1 phrase, no name) or skip."
        )
    await message.answer(text, reply_markup=hint_keyboard(lang))


@router.message(Command("top"))
async def handle_top(message: Message) -> None:
    store = get_session_store()
    user_id = message.from_user.id
    session = store.get(user_id)
    if session is None:
        await message.answer("No game in progress. Use /new to start!")
        return

    names = get_entity_names([cid for cid in session.candidate_ids])
    top = _scoring_engine.top_k(session, k=TOP_K_DISPLAY)
    lines = ["Top candidates:"]
    for i, (cid, w) in enumerate(top, 1):
        name = names.get(cid, f"#{cid}")
        lines.append(f"{i}. **{name}** — {w:.1%}")
    await message.answer("\n".join(lines))


@router.message(Command("why"))
async def handle_why(message: Message) -> None:
    store = get_session_store()
    user_id = message.from_user.id
    session = store.get(user_id)
    if session is None:
        await message.answer("No game in progress. Use /new to start!")
        return

    lines = ["My reasoning:"]
    for qa in session.history:
        ans_label = qa.answer.value.replace("_", " ")
        lines.append(f"- {qa.question_text} → {ans_label}")

    names = get_entity_names()
    top = _scoring_engine.top_k(session, k=3)
    if top:
        cid, w = top[0]
        name = names.get(cid, f"#{cid}")
        lines.append(f"\nTop candidate: **{name}** ({w:.1%})")

    await message.answer("\n".join(lines))


@router.message(Command("giveup"))
async def handle_giveup(message: Message) -> None:
    store = get_session_store()
    user_id = message.from_user.id
    session = store.get(user_id)
    if session is None:
        await message.answer("No game in progress. Use /new to start!")
        return
    session.mode = GameMode.LEARNING
    lang = _get_lang(session)
    if lang == "ru":
        await message.answer("Сдаюсь! Кого вы загадали?")
    else:
        await message.answer("I give up! Who were you thinking of?")


@router.message(Command("lang"))
async def handle_lang(message: Message) -> None:
    store = get_session_store()
    user_id = message.from_user.id
    session = store.get(user_id)

    parts = message.text.split()
    lang = parts[1] if len(parts) > 1 else "ru"
    if lang not in ("ru", "en"):
        lang = "ru"

    if session is not None:
        session.language = lang

    await message.answer(f"Language set to: {lang}")


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(
        "/new — Start a new game\n"
        "/top — Show top 5 candidates\n"
        "/why — Explain reasoning\n"
        "/giveup — Give up\n"
        "/lang ru|en — Switch language\n"
        "/help — This help"
    )


# ──────────────────────────────────────────────
# Callback handlers
# ──────────────────────────────────────────────

@router.callback_query(F.data.startswith("hint:"))
async def handle_hint_callback(callback: CallbackQuery) -> None:
    store = get_session_store()
    user_id = callback.from_user.id
    session = store.get(user_id)
    if not session:
        await callback.answer("No game. Use /new")
        return

    action = callback.data.split(":")[1]
    lang = _get_lang(session)

    if action == "skip":
        # Init all candidates with uniform weights
        all_ids = [e.id for e in _entities]
        _session_manager.init_candidates(session, all_ids)
        await callback.answer()
        await _ask_next_question(callback.message, session)
    else:
        # Ask for hint text
        session.mode = GameMode.WAITING_HINT
        if lang == "ru":
            await callback.message.edit_text("Опишите персонажа одной фразой (без имени):")
        else:
            await callback.message.edit_text("Describe the character in one phrase (no name):")
        await callback.answer()


@router.callback_query(F.data.startswith("answer:"))
async def handle_answer_callback(callback: CallbackQuery) -> None:
    store = get_session_store()
    user_id = callback.from_user.id
    session = store.get(user_id)
    if session is None:
        await callback.answer("No game in progress. Use /new to start!")
        return

    answer_key = callback.data.split(":")[1]
    answer = Answer(answer_key)
    lang = _get_lang(session)

    # Find the last asked attribute
    if session.asked_attributes:
        last_attr_id = session.asked_attributes[-1]
        attr = None
        for a in _attributes:
            if a.id == last_attr_id:
                attr = a
                break
    else:
        attr = None

    # If we have the attribute, process the answer
    if attr:
        # Remove from asked (process_answer will re-add)
        session.asked_attributes.pop()
        _session_manager.process_answer(session, _entities, attr, answer)

    await callback.answer()

    # Check if we should guess
    if _session_manager.should_guess(session):
        session.mode = GameMode.GUESSING
        candidate_id = _session_manager.get_guess_candidate(session)
        name = _entity_names.get(candidate_id, f"#{candidate_id}")
        _, max_w = _scoring_engine.max_prob(session)

        if lang == "ru":
            text = f"Я думаю, это **{name}**! ({max_w:.0%} уверенность)"
        else:
            text = f"I think it's **{name}**! ({max_w:.0%} confident)"
        await callback.message.edit_text(text, reply_markup=guess_keyboard(lang))
    else:
        await _ask_next_question(callback.message, session)


@router.callback_query(F.data.startswith("guess:"))
async def handle_guess_callback(callback: CallbackQuery) -> None:
    store = get_session_store()
    user_id = callback.from_user.id
    session = store.get(user_id)
    if session is None:
        await callback.answer("No game in progress.")
        return

    action = callback.data.split(":")[1]
    lang = _get_lang(session)

    if action == "correct":
        _session_manager.handle_guess_response(session, correct=True)
        q_count = session.question_count
        if lang == "ru":
            text = f"Угадал за {q_count} вопросов!"
        else:
            text = f"I guessed it in {q_count} questions!"
        await callback.message.edit_text(text, reply_markup=new_game_keyboard(lang))
    else:
        second = _session_manager.handle_guess_response(session, correct=False)
        if session.mode == GameMode.GUESSING and second is not None:
            name = _entity_names.get(second, f"#{second}")
            if lang == "ru":
                text = f"Тогда может это **{name}**?"
            else:
                text = f"Then maybe it's **{name}**?"
            await callback.message.edit_text(text, reply_markup=guess_keyboard(lang))
        elif session.mode == GameMode.LEARNING:
            if lang == "ru":
                await callback.message.edit_text("Сдаюсь! Кого вы загадали? Напишите имя:")
            else:
                await callback.message.edit_text("I give up! Who were you thinking of? Type the name:")
        else:
            session.mode = GameMode.LEARNING
            if lang == "ru":
                await callback.message.edit_text("Сдаюсь! Кого вы загадали? Напишите имя:")
            else:
                await callback.message.edit_text("I give up! Who were you thinking of? Type the name:")
    await callback.answer()


@router.callback_query(F.data == "action:new_game")
async def handle_new_game_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    # Simulate /new command
    await handle_new(callback.message)


# ──────────────────────────────────────────────
# Free-text messages (hint, learning)
# ──────────────────────────────────────────────

@router.message()
async def handle_text(message: Message) -> None:
    store = get_session_store()
    user_id = message.from_user.id
    session = store.get(user_id)

    if session is None:
        await message.answer("Use /new to start a game!")
        return

    lang = _get_lang(session)

    if session.mode == GameMode.WAITING_HINT:
        # Process hint — for MVP just init all candidates (embedding search requires LLM)
        session.hint_text = message.text
        all_ids = [e.id for e in _entities]
        _session_manager.init_candidates(session, all_ids)

        if lang == "ru":
            await message.answer("Принял! Начинаем.")
        else:
            await message.answer("Got it! Let's begin.")
        await _ask_next_question(message, session)

    elif session.mode == GameMode.LEARNING:
        # User tells who it was — just acknowledge for MVP
        _session_manager.finish_learning(session)
        if lang == "ru":
            text = f"Спасибо! Я запомню **{message.text}** на будущее."
        else:
            text = f"Thanks! I'll remember **{message.text}** for next time."
        await message.answer(text, reply_markup=new_game_keyboard(lang))

    else:
        if lang == "ru":
            await message.answer("Пожалуйста, используйте кнопки для ответа.")
        else:
            await message.answer("Please use the buttons to answer.")


# ──────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────

async def _ask_next_question(message: Message, session: GameSession) -> None:
    """Select next attribute and send question."""
    lang = _get_lang(session)
    best_key = _question_policy.select(session, _entities, _attributes)

    if best_key is None:
        # No more attributes to ask — force guess
        session.mode = GameMode.GUESSING
        candidate_id = _session_manager.get_guess_candidate(session)
        name = _entity_names.get(candidate_id, f"#{candidate_id}")
        if lang == "ru":
            text = f"У меня закончились вопросы. Это **{name}**?"
        else:
            text = f"I'm out of questions. Is it **{name}**?"
        await message.answer(text, reply_markup=guess_keyboard(lang))
        return

    attr = _find_attr_by_key(best_key)
    if attr is None:
        return

    # Track that we've "asked" this attribute (will be finalized in process_answer)
    session.asked_attributes.append(attr.id)

    q_num = session.question_count + 1
    q_text = _attr_question(attr, lang)

    if lang == "ru":
        header = f"Вопрос {q_num}/20:"
    else:
        header = f"Question {q_num}/20:"

    await message.answer(f"{header}\n{q_text}", reply_markup=answer_keyboard(lang))
