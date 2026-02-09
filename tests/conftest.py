"""Shared fixtures for Akinator 2.0 tests."""

from __future__ import annotations

import os
import tempfile
from typing import AsyncGenerator

import pytest

from akinator.db.models import Answer, Attribute, Entity, GameMode, GameSession


# ---------------------------------------------------------------------------
# Sample entities (small, deterministic dataset for tests)
# ---------------------------------------------------------------------------

SAMPLE_ATTRIBUTES: list[Attribute] = [
    Attribute(id=1, key="is_fictional", question_ru="Этот персонаж вымышленный?",
              question_en="Is this character fictional?", category="identity"),
    Attribute(id=2, key="is_male", question_ru="Это мужчина?",
              question_en="Is this a male?", category="identity"),
    Attribute(id=3, key="from_movie", question_ru="Связан с кино?",
              question_en="Related to movies?", category="media"),
    Attribute(id=4, key="from_game", question_ru="Связан с видеоиграми?",
              question_en="Related to video games?", category="media"),
    Attribute(id=5, key="is_villain", question_ru="Это злодей?",
              question_en="Is this a villain?", category="identity"),
    Attribute(id=6, key="from_russia", question_ru="Связан с Россией?",
              question_en="Related to Russia?", category="geography"),
]

SAMPLE_ENTITIES: list[Entity] = [
    Entity(
        id=1, name="Darth Vader", description="Iconic Star Wars villain",
        entity_type="character", language="en",
        attributes={"is_fictional": 1.0, "is_male": 1.0, "from_movie": 1.0,
                     "from_game": 0.3, "is_villain": 0.9, "from_russia": 0.0},
    ),
    Entity(
        id=2, name="Mario", description="Nintendo plumber hero",
        entity_type="character", language="en",
        attributes={"is_fictional": 1.0, "is_male": 1.0, "from_movie": 0.3,
                     "from_game": 1.0, "is_villain": 0.0, "from_russia": 0.0},
    ),
    Entity(
        id=3, name="Elon Musk", description="Tech entrepreneur and CEO",
        entity_type="person", language="en",
        attributes={"is_fictional": 0.0, "is_male": 1.0, "from_movie": 0.1,
                     "from_game": 0.0, "is_villain": 0.2, "from_russia": 0.0},
    ),
    Entity(
        id=4, name="Hermione Granger", description="Witch from Harry Potter",
        entity_type="character", language="en",
        attributes={"is_fictional": 1.0, "is_male": 0.0, "from_movie": 1.0,
                     "from_game": 0.2, "is_villain": 0.0, "from_russia": 0.0},
    ),
    Entity(
        id=5, name="Юрий Гагарин", description="Первый человек в космосе",
        entity_type="person", language="ru",
        attributes={"is_fictional": 0.0, "is_male": 1.0, "from_movie": 0.2,
                     "from_game": 0.0, "is_villain": 0.0, "from_russia": 1.0},
    ),
]


@pytest.fixture
def sample_entities() -> list[Entity]:
    return [Entity(**e.__dict__) for e in SAMPLE_ENTITIES]


@pytest.fixture
def sample_attributes() -> list[Attribute]:
    return list(SAMPLE_ATTRIBUTES)


@pytest.fixture
def uniform_session(sample_entities: list[Entity]) -> GameSession:
    """A game session with uniform weights over sample entities."""
    n = len(sample_entities)
    return GameSession(
        session_id="test-session-001",
        user_id=42,
        language="en",
        mode=GameMode.ASKING,
        candidate_ids=[e.id for e in sample_entities],
        weights=[1.0 / n] * n,
    )


@pytest.fixture
def skewed_session(sample_entities: list[Entity]) -> GameSession:
    """A session where Darth Vader has very high probability."""
    return GameSession(
        session_id="test-session-002",
        user_id=42,
        language="en",
        mode=GameMode.ASKING,
        candidate_ids=[e.id for e in sample_entities],
        weights=[0.90, 0.04, 0.03, 0.02, 0.01],
    )


@pytest.fixture
def tmp_db_path() -> str:
    """Temporary SQLite database file path."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)
