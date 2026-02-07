"""Data models for Akinator 2.0."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class GameMode(Enum):
    WAITING_HINT = "waiting_hint"
    ASKING = "asking"
    GUESSING = "guessing"
    LEARNING = "learning"
    FINISHED = "finished"


class Answer(Enum):
    YES = "yes"
    NO = "no"
    PROBABLY_YES = "probably_yes"
    PROBABLY_NO = "probably_no"
    DONT_KNOW = "dont_know"


@dataclass
class Entity:
    id: int
    name: str
    description: str
    entity_type: str  # person, character, animal, object
    language: str  # ru, en
    attributes: dict[str, float] = field(default_factory=dict)
    aliases: list[str] = field(default_factory=list)
    play_count: int = 0
    guess_success_count: int = 0
    created_at: datetime | None = None


@dataclass
class Attribute:
    id: int
    key: str
    question_ru: str
    question_en: str
    category: str  # identity, media, geography, era, traits


@dataclass
class QAPair:
    attribute_id: int | None
    attribute_key: str
    question_text: str
    answer: Answer


@dataclass
class GameSession:
    session_id: str
    user_id: int
    language: str = "ru"
    mode: GameMode = GameMode.WAITING_HINT
    candidate_ids: list[int] = field(default_factory=list)
    weights: list[float] = field(default_factory=list)
    asked_attributes: list[int] = field(default_factory=list)
    history: list[QAPair] = field(default_factory=list)
    hint_text: str | None = None
    guess_count: int = 0
    question_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
