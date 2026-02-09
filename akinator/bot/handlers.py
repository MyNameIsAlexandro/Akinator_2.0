"""Telegram Bot Handlers — wired to aiogram Router."""

from __future__ import annotations

import logging
import os

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from akinator.bot.keyboards import (
    answer_keyboard, guess_keyboard, hint_keyboard,
    learn_confirm_keyboard, new_game_keyboard,
)
from akinator.config import (
    ATTRIBUTE_KEYS, GUESS_THRESHOLD, LLM_KNOWLEDGE_WEIGHT,
    LLM_QA_WEIGHT, TOP_K_DISPLAY,
)
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
_entity_names: dict[int, str] = {}
_scoring_engine = ScoringEngine()
_question_policy = QuestionPolicy()
_session_manager = GameSessionManager(_scoring_engine, _question_policy)
_repo: Repository | None = None
_llm_client = None  # LLMClient | None
_backup = None  # GitHubBackup | None

ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", "0"))


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


def set_repository(repo: Repository) -> None:
    """Called at startup to set the database repository for runtime learning."""
    global _repo
    _repo = repo


def set_llm_client(client) -> None:
    """Called at startup to set the LLM client for smart learning."""
    global _llm_client
    _llm_client = client


def set_backup(backup) -> None:
    """Called at startup to set the GitHub backup instance."""
    global _backup
    _backup = backup


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
    entity_count = len(_entities)
    store = get_session_store()
    user_id = message.from_user.id
    lang = store[user_id].language if user_id in store else "ru"

    if lang == "ru":
        text = (
            f"Добро пожаловать в Акинатор 2.0!\n\n"
            f"Я знаю **{entity_count:,}** персонажей.\n"
            f"Загадайте персонажа — реального или вымышленного — и я попробую угадать.\n"
            f"Используйте /new для начала игры."
        )
    else:
        text = (
            f"Welcome to Akinator 2.0!\n\n"
            f"I know **{entity_count:,}** characters.\n"
            f"Think of a character — real or fictional — and I'll try to guess who it is.\n"
            f"Use /new to start a new game."
        )
    await message.answer(text, parse_mode="Markdown")


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


@router.message(Command("stats"))
async def handle_stats(message: Message) -> None:
    entity_count = len(_entities)
    attr_count = len(_attributes)
    fictional = sum(1 for e in _entities if e.attributes.get("is_fictional", 0) > 0.5)
    real = entity_count - fictional
    active_games = len(_session_store)

    store = get_session_store()
    user_id = message.from_user.id
    lang = store[user_id].language if user_id in store else "ru"

    if lang == "ru":
        text = (
            f"**Статистика Акинатора 2.0**\n\n"
            f"Всего персонажей: **{entity_count:,}**\n"
            f"  Вымышленных: {fictional:,}\n"
            f"  Реальных: {real:,}\n"
            f"Атрибутов: {attr_count}\n"
            f"Активных игр: {active_games}"
        )
    else:
        text = (
            f"**Akinator 2.0 Stats**\n\n"
            f"Total characters: **{entity_count:,}**\n"
            f"  Fictional: {fictional:,}\n"
            f"  Real: {real:,}\n"
            f"Attributes: {attr_count}\n"
            f"Active games: {active_games}"
        )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("backup"))
async def handle_backup(message: Message) -> None:
    user_id = message.from_user.id
    if ADMIN_USER_ID == 0 or user_id != ADMIN_USER_ID:
        await message.answer("This command is only available to the admin.")
        return

    if _backup is None:
        await message.answer("Backup is not configured (GITHUB_TOKEN not set).")
        return

    await message.answer("Starting backup...")
    success = await _backup.backup_now()
    entity_count = len(_entities)
    if success:
        await message.answer(f"Backup completed: {entity_count:,} entities pushed to GitHub.")
    else:
        await message.answer("Backup failed. Check logs for details.")


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(
        "/new — Start a new game\n"
        "/top — Show top 5 candidates\n"
        "/why — Explain reasoning\n"
        "/giveup — Give up\n"
        "/stats — Show statistics\n"
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

    # Answer display labels
    _answer_labels = {
        "ru": {"yes": "Да", "no": "Нет", "probably_yes": "Скорее да",
                "probably_no": "Скорее нет", "dont_know": "Не знаю"},
        "en": {"yes": "Yes", "no": "No", "probably_yes": "Probably yes",
                "probably_no": "Probably no", "dont_know": "Don't know"},
    }

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

    # Edit previous message to show selected answer (remove buttons)
    answer_label = _answer_labels.get(lang, _answer_labels["en"]).get(answer_key, answer_key)
    q_num = session.question_count
    if attr:
        q_text = _attr_question(attr, lang)
        await callback.message.edit_text(f"**Q{q_num}:** {q_text} — **{answer_label}**", parse_mode="Markdown")
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
        await callback.message.answer(text, reply_markup=guess_keyboard(lang), parse_mode="Markdown")
    else:
        await _ask_next_question(callback.message, session)


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


@router.callback_query(F.data.startswith("learn_confirm:"))
async def handle_learn_confirm_callback(callback: CallbackQuery) -> None:
    """Handle user confirmation of LLM-corrected entity name."""
    if await _handle_stale_session(callback):
        return
    store = get_session_store()
    user_id = callback.from_user.id
    session = store.get(user_id)

    if session is None or session.mode != GameMode.LEARNING_CONFIRM:
        await callback.answer()
        return

    action = callback.data.split(":")[1]
    lang = _get_lang(session)
    data = session.pending_entity

    if data is None:
        await callback.answer()
        return

    if action == "no":
        # User rejected correction — use original name but keep LLM attributes
        data["corrected_name"] = data.get("_original_name", data["corrected_name"])

    saved = await _save_enriched_entity(data, session, lang)
    _session_manager.finish_learning(session)
    session.pending_entity = None

    final_name = data.get("corrected_name", "")
    if saved:
        if lang == "ru":
            text = f"Спасибо! Я запомнил **{final_name}** и буду угадывать в следующий раз."
        else:
            text = f"Thanks! I learned **{final_name}** and will guess it next time."
    else:
        if lang == "ru":
            text = f"Спасибо! Я запомню **{final_name}** на будущее."
        else:
            text = f"Thanks! I'll remember **{final_name}** for next time."

    await callback.message.edit_text(text, reply_markup=new_game_keyboard(lang))
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
        entity_name = message.text.strip()

        # Try smart learning with LLM if available
        if _llm_client is not None:
            handled = await _smart_learn_entity(entity_name, session, lang, message)
            if handled:
                return

        # Fallback: save as-is with QA-only attributes
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
# Helpers
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


async def _smart_learn_entity(
    raw_name: str, session: GameSession, lang: str, message: Message,
) -> bool:
    """Use LLM to correct name and enrich attributes. Returns True if handled."""
    try:
        # Show thinking indicator
        if lang == "ru":
            thinking_msg = await message.answer("Ищу информацию...")
        else:
            thinking_msg = await message.answer("Looking up information...")

        # Build QA context
        qa_context = [(qa.question_text, qa.answer.value) for qa in session.history]

        result = await _llm_client.correct_and_enrich(
            raw_name=raw_name,
            qa_history=qa_context,
        )

        if result is None:
            # LLM failed — delete thinking message, let fallback handle it
            try:
                await thinking_msg.delete()
            except Exception:
                pass
            return False

        corrected = result.get("corrected_name", raw_name)

        # Check if name was corrected
        if corrected.lower().strip() != raw_name.lower().strip():
            # Store original name and ask for confirmation
            result["_original_name"] = raw_name
            session.pending_entity = result
            session.mode = GameMode.LEARNING_CONFIRM

            name_en = result.get("name_en", "")
            name_ru = result.get("name_ru", "")
            desc = result.get("description", "")

            if lang == "ru":
                text = f"Вы имели в виду **{name_ru}** ({name_en})?"
                if desc:
                    text += f"\n_{desc}_"
            else:
                text = f"Did you mean **{name_en}** ({name_ru})?"
                if desc:
                    text += f"\n_{desc}_"

            try:
                await thinking_msg.edit_text(text, reply_markup=learn_confirm_keyboard(lang), parse_mode="Markdown")
            except Exception:
                await message.answer(text, reply_markup=learn_confirm_keyboard(lang), parse_mode="Markdown")
            return True
        else:
            # No correction needed — save directly with LLM attributes
            saved = await _save_enriched_entity(result, session, lang)
            _session_manager.finish_learning(session)

            if saved:
                if lang == "ru":
                    text = f"Спасибо! Я запомнил **{corrected}** и буду угадывать в следующий раз."
                else:
                    text = f"Thanks! I learned **{corrected}** and will guess it next time."
            else:
                if lang == "ru":
                    text = f"Спасибо! Я запомню **{corrected}** на будущее."
                else:
                    text = f"Thanks! I'll remember **{corrected}** for next time."

            try:
                await thinking_msg.edit_text(text, reply_markup=new_game_keyboard(lang), parse_mode="Markdown")
            except Exception:
                await message.answer(text, reply_markup=new_game_keyboard(lang), parse_mode="Markdown")
            return True

    except Exception:
        logger.exception("Smart learning failed for: %s, falling back", raw_name)
        return False


def _merge_attributes(
    qa_attrs: dict[str, float],
    llm_attrs: dict[str, float],
) -> dict[str, float]:
    """Merge QA-derived and LLM-derived attribute values."""
    merged = dict(llm_attrs)
    for key, qa_val in qa_attrs.items():
        if key in merged:
            merged[key] = LLM_QA_WEIGHT * qa_val + LLM_KNOWLEDGE_WEIGHT * merged[key]
        else:
            merged[key] = qa_val
    return merged


async def _save_enriched_entity(
    data: dict, session: GameSession, lang: str,
) -> bool:
    """Save an LLM-enriched entity to DB and in-memory lists."""
    if _repo is None:
        return False

    try:
        corrected = data.get("corrected_name", "")
        name_en = data.get("name_en", corrected)
        name_ru = data.get("name_ru", corrected)
        entity_type = data.get("entity_type", "character")
        description = data.get("description", f"Learned from user {session.user_id}")
        llm_attrs = data.get("attributes", {})

        # Build QA attributes
        qa_attrs: dict[str, float] = {}
        answer_to_value = {
            Answer.YES: 1.0, Answer.NO: 0.0,
            Answer.PROBABLY_YES: 0.75, Answer.PROBABLY_NO: 0.25,
            Answer.DONT_KNOW: 0.5,
        }
        for qa in session.history:
            qa_attrs[qa.attribute_key] = answer_to_value[qa.answer]

        # Merge: LLM knowledge + QA answers
        attrs = _merge_attributes(qa_attrs, llm_attrs)

        attr_key_to_id = {a.key: a.id for a in _attributes}

        # Determine primary name for the entity
        primary_name = name_en if not _is_cyrillic(corrected) else name_ru
        if not primary_name:
            primary_name = corrected

        # Check for duplicates (by name and aliases)
        existing = await _repo.find_entity_by_name_or_alias(primary_name)
        if existing is None and name_en != primary_name:
            existing = await _repo.find_entity_by_name_or_alias(name_en)
        if existing is None and name_ru != primary_name:
            existing = await _repo.find_entity_by_name_or_alias(name_ru)

        if existing is not None:
            # Update existing entity
            for key, value in attrs.items():
                if key in attr_key_to_id:
                    await _repo.set_entity_attribute(existing.id, attr_key_to_id[key], value)
            for e in _entities:
                if e.id == existing.id:
                    e.attributes.update(attrs)
                    break
            # Add original spelling as alias if different
            original_name = data.get("_original_name")
            if original_name and original_name.lower() != existing.name.lower():
                await _repo.add_alias(existing.id, original_name, lang)
            logger.info("Updated existing entity: %s (id=%d) with %d LLM attrs", existing.name, existing.id, len(attrs))
            if _backup:
                _backup.notify_new_entity()
            return True

        # Save new entity
        eid = await _repo.add_entity(
            name=primary_name,
            description=description,
            entity_type=entity_type,
            language="ru" if _is_cyrillic(primary_name) else "en",
        )

        # Save attributes
        for key, value in attrs.items():
            if key in attr_key_to_id:
                await _repo.set_entity_attribute(eid, attr_key_to_id[key], value)

        # Save aliases
        if name_en and name_en != primary_name:
            await _repo.add_alias(eid, name_en, "en")
        if name_ru and name_ru != primary_name:
            await _repo.add_alias(eid, name_ru, "ru")
        original_name = data.get("_original_name")
        if original_name and original_name.lower() != primary_name.lower():
            if original_name.lower() != (name_en or "").lower() and original_name.lower() != (name_ru or "").lower():
                await _repo.add_alias(eid, original_name, lang)

        # Add to in-memory lists
        new_entity = Entity(
            id=eid, name=primary_name,
            description=description,
            entity_type=entity_type,
            language="ru" if _is_cyrillic(primary_name) else "en",
            attributes=attrs,
        )
        _entities.append(new_entity)
        _entity_names[eid] = primary_name

        logger.info("Learned new entity via LLM: %s (id=%d) with %d attrs", primary_name, eid, len(attrs))
        if _backup:
            _backup.notify_new_entity()
        return True

    except Exception:
        logger.exception("Failed to save enriched entity")
        return False


def _is_cyrillic(s: str) -> bool:
    return any("\u0400" <= c <= "\u04ff" for c in s)


async def _learn_new_entity(
    name: str, session: GameSession, lang: str,
) -> bool:
    """Save a new entity to DB and add to in-memory lists (fallback without LLM).

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
            if _backup:
                _backup.notify_new_entity()
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

        logger.info("Learned new entity: %s (id=%d) with %d attributes", name, eid, len(attrs))
        if _backup:
            _backup.notify_new_entity()
        return True

    except Exception:
        logger.exception("Failed to save new entity: %s", name)
        return False
