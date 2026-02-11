"""Inline keyboard builders for Akinator 2.0."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def answer_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """5-button answer keyboard."""
    if language == "ru":
        labels = [
            ("Да", "answer:yes"),
            ("Нет", "answer:no"),
            ("Скорее да", "answer:probably_yes"),
            ("Скорее нет", "answer:probably_no"),
            ("Не знаю", "answer:dont_know"),
        ]
    else:
        labels = [
            ("Yes", "answer:yes"),
            ("No", "answer:no"),
            ("Probably yes", "answer:probably_yes"),
            ("Probably no", "answer:probably_no"),
            ("Don't know", "answer:dont_know"),
        ]
    builder = InlineKeyboardBuilder()
    for text, data in labels:
        builder.button(text=text, callback_data=data)
    builder.adjust(2, 3)
    return builder.as_markup()


def guess_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """Guess confirmation keyboard."""
    if language == "ru":
        yes_text, no_text = "Да, верно!", "Нет, не угадал"
    else:
        yes_text, no_text = "Yes, correct!", "No, wrong"
    builder = InlineKeyboardBuilder()
    builder.button(text=yes_text, callback_data="guess:correct")
    builder.button(text=no_text, callback_data="guess:wrong")
    builder.adjust(2)
    return builder.as_markup()


def hint_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """Hint choice keyboard."""
    if language == "ru":
        skip, give = "Пропустить", "Дать подсказку"
    else:
        skip, give = "Skip hint", "Give hint"
    builder = InlineKeyboardBuilder()
    builder.button(text=skip, callback_data="hint:skip")
    builder.button(text=give, callback_data="hint:give")
    builder.adjust(2)
    return builder.as_markup()


def learn_confirm_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """Confirmation keyboard for LLM-corrected entity name."""
    if language == "ru":
        yes_text, no_text = "Да, верно", "Нет, оставить как ввёл"
    else:
        yes_text, no_text = "Yes, correct", "No, keep my input"
    builder = InlineKeyboardBuilder()
    builder.button(text=yes_text, callback_data="learn_confirm:yes")
    builder.button(text=no_text, callback_data="learn_confirm:no")
    builder.adjust(2)
    return builder.as_markup()


def new_game_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """Post-game new game button."""
    text = "Новая игра" if language == "ru" else "New game"
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data="action:new_game")
    return builder.as_markup()
