"""Telegram Bot Handlers. (Stub — TDD.)"""

from __future__ import annotations


def get_session_store() -> dict:
    raise NotImplementedError


def get_entities() -> list:
    raise NotImplementedError


def get_attributes() -> list:
    raise NotImplementedError


def get_entity_names(ids: list[int]) -> dict[int, str]:
    raise NotImplementedError


async def handle_start(message) -> None:
    raise NotImplementedError


async def handle_new(message) -> None:
    raise NotImplementedError


async def handle_answer_callback(callback) -> None:
    raise NotImplementedError


async def handle_guess_callback(callback) -> None:
    raise NotImplementedError


async def handle_top(message) -> None:
    raise NotImplementedError


async def handle_giveup(message) -> None:
    raise NotImplementedError


async def handle_lang(message) -> None:
    raise NotImplementedError


async def handle_why(message) -> None:
    raise NotImplementedError
