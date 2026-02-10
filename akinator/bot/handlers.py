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

from akinator.db.repository import Repository

logger = logging.getLogger(__name__)

router = Router()

# --- Global state (in-memory for MVP single instance) ---
_session_store: dict[int, GameSession] = {}
_entities: list[Entity] = []
_attributes: list[Attribute] = []
_entity_names: dict[int, str] = {}  # Default names (fallback)
_entity_names_ru: dict[int, str] = {}  # Russian localized names
_entity_names_en: dict[int, str] = {}  # English localized names
_scoring_engine = ScoringEngine()
_question_policy = QuestionPolicy()
_session_manager = GameSessionManager(_scoring_engine, _question_policy)
_repo: Repository | None = None


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


def get_localized_entity_name(entity_id: int, lang: str = "en") -> str:
    """Get entity name in the specified language."""
    if lang == "ru" and entity_id in _entity_names_ru:
        return _entity_names_ru[entity_id]
    elif lang == "en" and entity_id in _entity_names_en:
        return _entity_names_en[entity_id]
    # Fallback to default name
    return _entity_names.get(entity_id, f"#{entity_id}")


def set_repository(repo: Repository) -> None:
    """Called at startup to set the database repository for runtime learning."""
    global _repo
    _repo = repo


async def set_game_data(entities: list[Entity], attributes: list[Attribute], repo: Repository | None = None) -> None:
    """Called at startup to load game data into memory."""
    _entities.clear()
    _entities.extend(entities)
    _attributes.clear()
    _attributes.extend(attributes)
    _entity_names.clear()
    _entity_names_ru.clear()
    _entity_names_en.clear()

    for e in entities:
        _entity_names[e.id] = e.name
        # Default: use entity name for both languages
        _entity_names_en[e.id] = e.name
        _entity_names_ru[e.id] = e.name

    # Load localized names from aliases if repository is available
    if repo:
        for e in entities:
            aliases = await repo.get_aliases(e.id)
            for alias, lang in aliases:
                if lang == "ru":
                    _entity_names_ru[e.id] = alias
                elif lang == "en":
                    _entity_names_en[e.id] = alias


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


async def _handle_stale_session(callback: CallbackQuery) -> bool:
    """Detect stale session (e.g. after bot restart) and auto-restart game.

    Returns True if session was stale and handled (caller should return).
    """
    store = get_session_store()
    user_id = callback.from_user.id
    session = store.get(user_id)
    if session is not None:
        return False

    # Session lost — auto-restart
    lang = "ru"
    new_session = _session_manager.create_session(user_id=user_id, language=lang)
    store[user_id] = new_session

    if lang == "ru":
        text = (
            "Бот был обновлён, сессия сброшена.\n"
            "Начинаем новую игру!\n\n"
            "Загадайте персонажа — реального или вымышленного.\n"
            "Можете дать подсказку (описание в 1 фразе, без имени) или пропустить."
        )
    else:
        text = (
            "Bot was updated, session reset.\n"
            "Starting a new game!\n\n"
            "Think of a character — real or fictional.\n"
            "You can give me a hint (describe in 1 phrase, no name) or skip."
        )
    await callback.message.edit_text(text, reply_markup=hint_keyboard(lang))
    await callback.answer()
    return True


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

    lang = _get_lang(session)
    top = _scoring_engine.top_k(session, k=TOP_K_DISPLAY)
    if lang == "ru":
        lines = ["Топ кандидатов:"]
    else:
        lines = ["Top candidates:"]
    for i, (cid, w) in enumerate(top, 1):
        name = get_localized_entity_name(cid, lang)
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

    lang = _get_lang(session)
    if lang == "ru":
        lines = ["Моё рассуждение:"]
    else:
        lines = ["My reasoning:"]

    for qa in session.history:
        ans_label = qa.answer.value.replace("_", " ")
        lines.append(f"- {qa.question_text} → {ans_label}")

    top = _scoring_engine.top_k(session, k=3)
    if top:
        cid, w = top[0]
        name = get_localized_entity_name(cid, lang)
        if lang == "ru":
            lines.append(f"\nТоп кандидат: **{name}** ({w:.1%})")
        else:
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
    if await _handle_stale_session(callback):
        return
    store = get_session_store()
    user_id = callback.from_user.id
    session = store.get(user_id)

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
    if await _handle_stale_session(callback):
        return
    store = get_session_store()
    user_id = callback.from_user.id
    session = store.get(user_id)

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
        name = get_localized_entity_name(candidate_id, lang)
        _, max_w = _scoring_engine.max_prob(session)

        if lang == "ru":
            text = f"Я думаю, это **{name}**! ({max_w:.0%} уверенность)"
        else:
            text = f"I think it's **{name}**! ({max_w:.0%} confident)"
        await callback.message.edit_text(text, reply_markup=guess_keyboard(lang))
    else:
        await _ask_next_question(callback.message, session)


async def _track_session_feedback(
    session: GameSession, entity_id: int, lang: str
) -> None:
    """Track user feedback for all questions asked in this session."""
    if _repo is None:
        return

    # Get the entity with attributes
    entities_with_attrs = [e for e in _entities if e.id == entity_id]
    if not entities_with_attrs:
        return

    entity = entities_with_attrs[0]
    attr_key_to_id = {a.key: a.id for a in _attributes}

    # Track each question/answer pair
    for qa in session.history:
        if qa.attribute_key not in attr_key_to_id:
            continue

        attribute_id = attr_key_to_id[qa.attribute_key]
        expected_value = entity.attributes.get(qa.attribute_key, 0.5)
        user_answer = qa.answer.value

        try:
            await _repo.track_feedback(
                entity_id=entity_id,
                attribute_id=attribute_id,
                user_answer=user_answer,
                expected_value=expected_value,
                language=lang,
            )
        except Exception as e:
            logger.warning("Failed to track feedback: %s", e)


@router.callback_query(F.data.startswith("guess:"))
async def handle_guess_callback(callback: CallbackQuery) -> None:
    if await _handle_stale_session(callback):
        return
    store = get_session_store()
    user_id = callback.from_user.id
    session = store.get(user_id)

    action = callback.data.split(":")[1]
    lang = _get_lang(session)

    if action == "correct":
        # Track feedback for correct guess before finishing
        guessed_id = _session_manager.get_guess_candidate(session)
        await _track_session_feedback(session, guessed_id, lang)

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
            name = get_localized_entity_name(second, lang)
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
    # Create a new game directly (works even after redeploy)
    store = get_session_store()
    user_id = callback.from_user.id
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
    await callback.message.edit_text(text, reply_markup=hint_keyboard(lang))


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
        # Save new entity to database from user answers
        entity_name = message.text.strip()
        saved = await _learn_new_entity(entity_name, session, lang)
        _session_manager.finish_learning(session)
        if saved:
            if lang == "ru":
                text = f"Спасибо! Я запомнил **{entity_name}** и буду угадывать в следующий раз."
            else:
                text = f"Thanks! I learned **{entity_name}** and will guess it next time."
        else:
            if lang == "ru":
                text = f"Спасибо! Я запомню **{entity_name}** на будущее."
            else:
                text = f"Thanks! I'll remember **{entity_name}** for next time."
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
        name = get_localized_entity_name(candidate_id, lang)
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


async def _learn_new_entity(
    name: str, session: GameSession, lang: str,
) -> bool:
    """Save a new entity to DB and add to in-memory lists.

    Infer attribute values from the session's QA history.
    If an entity with the same name already exists, update its attributes.
    Returns True if saved successfully.
    """
    if _repo is None:
        return False

    try:
        # Build attributes from QA history
        attrs: dict[str, float] = {}
        answer_to_value = {
            Answer.YES: 1.0,
            Answer.NO: 0.0,
            Answer.PROBABLY_YES: 0.75,
            Answer.PROBABLY_NO: 0.25,
            Answer.DONT_KNOW: 0.5,
        }
        for qa in session.history:
            attrs[qa.attribute_key] = answer_to_value[qa.answer]

        attr_key_to_id = {a.key: a.id for a in _attributes}

        # Check if entity already exists (duplicate detection)
        existing = await _repo.find_entity_by_name(name)
        if existing is not None:
            # Update existing entity's attributes with new answers
            for key, value in attrs.items():
                if key in attr_key_to_id:
                    await _repo.set_entity_attribute(existing.id, attr_key_to_id[key], value)
            # Update in-memory entity
            for e in _entities:
                if e.id == existing.id:
                    e.attributes.update(attrs)
                    break
            logger.info("Updated existing entity: %s (id=%d) with %d attributes", name, existing.id, len(attrs))
            return True

        # Save new entity to DB
        eid = await _repo.add_entity(
            name=name,
            description=f"Learned from user {session.user_id}",
            entity_type="character",
            language=lang,
        )

        # Save attributes
        for key, value in attrs.items():
            if key in attr_key_to_id:
                await _repo.set_entity_attribute(eid, attr_key_to_id[key], value)

        # Add to in-memory lists so it's available immediately for all users
        new_entity = Entity(
            id=eid, name=name,
            description=f"Learned from user {session.user_id}",
            entity_type="character", language=lang,
            attributes=attrs,
        )
        _entities.append(new_entity)
        _entity_names[eid] = name
        # Add to localized name dictionaries
        if lang == "ru":
            _entity_names_ru[eid] = name
            _entity_names_en[eid] = name  # Use same name as fallback for EN
        else:
            _entity_names_en[eid] = name
            _entity_names_ru[eid] = name  # Use same name as fallback for RU

        logger.info("Learned new entity: %s (id=%d) with %d attributes", name, eid, len(attrs))
        return True

    except Exception:
        logger.exception("Failed to save new entity: %s", name)
        return False
