"""Database Repository — SQLite CRUD operations."""

from __future__ import annotations

import numpy as np
import aiosqlite

from akinator.db.models import Attribute, Entity


_SCHEMA = """
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    language TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    play_count INTEGER DEFAULT 0,
    guess_success_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS entity_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL REFERENCES entities(id),
    alias TEXT NOT NULL,
    language TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS attributes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    question_ru TEXT NOT NULL,
    question_en TEXT NOT NULL,
    category TEXT
);

CREATE TABLE IF NOT EXISTS entity_attributes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL REFERENCES entities(id),
    attribute_id INTEGER NOT NULL REFERENCES attributes(id),
    value REAL NOT NULL,
    UNIQUE(entity_id, attribute_id)
);

CREATE TABLE IF NOT EXISTS entity_embeddings (
    entity_id INTEGER PRIMARY KEY REFERENCES entities(id),
    embedding BLOB NOT NULL
);

CREATE TABLE IF NOT EXISTS user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL REFERENCES entities(id),
    attribute_id INTEGER NOT NULL REFERENCES attributes(id),
    user_answer TEXT NOT NULL,
    expected_value REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_language TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_entity ON user_feedback(entity_id);
CREATE INDEX IF NOT EXISTS idx_feedback_attribute ON user_feedback(attribute_id);
"""


class Repository:

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def _conn(self) -> aiosqlite.Connection:
        if self._db is None:
            self._db = await aiosqlite.connect(self.db_path)
            self._db.row_factory = aiosqlite.Row
        return self._db

    async def init_db(self) -> None:
        db = await self._conn()
        await db.executescript(_SCHEMA)
        await db.commit()

    async def close(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    async def list_tables(self) -> list[str]:
        db = await self._conn()
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        rows = await cursor.fetchall()
        return [r[0] for r in rows]

    # ---- Entities ----

    async def add_entity(
        self, name: str, description: str, entity_type: str, language: str,
    ) -> int:
        db = await self._conn()
        cursor = await db.execute(
            "INSERT INTO entities (name, description, entity_type, language) VALUES (?, ?, ?, ?)",
            (name, description, entity_type, language),
        )
        await db.commit()
        return cursor.lastrowid

    async def get_entity(self, entity_id: int, with_attributes: bool = False) -> Entity | None:
        db = await self._conn()
        cursor = await db.execute("SELECT * FROM entities WHERE id = ?", (entity_id,))
        row = await cursor.fetchone()
        if row is None:
            return None
        entity = Entity(
            id=row["id"], name=row["name"], description=row["description"],
            entity_type=row["entity_type"], language=row["language"],
            play_count=row["play_count"],
            guess_success_count=row["guess_success_count"],
        )
        if with_attributes:
            cursor2 = await db.execute(
                """SELECT a.key, ea.value
                   FROM entity_attributes ea
                   JOIN attributes a ON a.id = ea.attribute_id
                   WHERE ea.entity_id = ?""",
                (entity_id,),
            )
            for arow in await cursor2.fetchall():
                entity.attributes[arow[0]] = arow[1]
        return entity

    async def get_all_entities(self) -> list[Entity]:
        db = await self._conn()
        cursor = await db.execute("SELECT * FROM entities")
        rows = await cursor.fetchall()
        return [
            Entity(
                id=r["id"], name=r["name"], description=r["description"],
                entity_type=r["entity_type"], language=r["language"],
                play_count=r["play_count"],
                guess_success_count=r["guess_success_count"],
            )
            for r in rows
        ]

    async def find_entity_by_name(self, name: str) -> Entity | None:
        db = await self._conn()
        cursor = await db.execute(
            "SELECT * FROM entities WHERE LOWER(name) = LOWER(?)", (name,),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return Entity(
            id=row["id"], name=row["name"], description=row["description"],
            entity_type=row["entity_type"], language=row["language"],
            play_count=row["play_count"],
            guess_success_count=row["guess_success_count"],
        )

    async def get_all_entity_attributes(self) -> dict[int, dict[str, float]]:
        """Batch-load all entity attributes in one query."""
        db = await self._conn()
        cursor = await db.execute(
            """SELECT ea.entity_id, a.key, ea.value
               FROM entity_attributes ea
               JOIN attributes a ON a.id = ea.attribute_id"""
        )
        rows = await cursor.fetchall()
        result: dict[int, dict[str, float]] = {}
        for r in rows:
            eid = r[0]
            if eid not in result:
                result[eid] = {}
            result[eid][r[1]] = r[2]
        return result

    async def increment_play_count(self, entity_id: int) -> None:
        db = await self._conn()
        await db.execute(
            "UPDATE entities SET play_count = play_count + 1 WHERE id = ?",
            (entity_id,),
        )
        await db.commit()

    # ---- Attributes ----

    async def add_attribute(
        self, key: str, question_ru: str, question_en: str, category: str,
    ) -> int:
        db = await self._conn()
        cursor = await db.execute(
            "INSERT INTO attributes (key, question_ru, question_en, category) VALUES (?, ?, ?, ?)",
            (key, question_ru, question_en, category),
        )
        await db.commit()
        return cursor.lastrowid

    async def get_all_attributes(self) -> list[Attribute]:
        db = await self._conn()
        cursor = await db.execute("SELECT * FROM attributes")
        rows = await cursor.fetchall()
        return [
            Attribute(id=r["id"], key=r["key"], question_ru=r["question_ru"],
                      question_en=r["question_en"], category=r["category"])
            for r in rows
        ]

    async def set_entity_attribute(
        self, entity_id: int, attribute_id: int, value: float,
    ) -> None:
        db = await self._conn()
        await db.execute(
            """INSERT INTO entity_attributes (entity_id, attribute_id, value)
               VALUES (?, ?, ?)
               ON CONFLICT(entity_id, attribute_id) DO UPDATE SET value = excluded.value""",
            (entity_id, attribute_id, value),
        )
        await db.commit()

    async def get_entity_attribute(
        self, entity_id: int, attribute_id: int,
    ) -> float | None:
        db = await self._conn()
        cursor = await db.execute(
            "SELECT value FROM entity_attributes WHERE entity_id = ? AND attribute_id = ?",
            (entity_id, attribute_id),
        )
        row = await cursor.fetchone()
        return row[0] if row else None

    # ---- Aliases ----

    async def add_alias(self, entity_id: int, alias: str, language: str) -> None:
        db = await self._conn()
        await db.execute(
            "INSERT INTO entity_aliases (entity_id, alias, language) VALUES (?, ?, ?)",
            (entity_id, alias, language),
        )
        await db.commit()

    async def get_aliases(self, entity_id: int) -> list[tuple[str, str]]:
        db = await self._conn()
        cursor = await db.execute(
            "SELECT alias, language FROM entity_aliases WHERE entity_id = ?",
            (entity_id,),
        )
        rows = await cursor.fetchall()
        return [(r[0], r[1]) for r in rows]

    async def get_localized_name(self, entity_id: int, language: str = "en") -> str:
        """Get entity name in the specified language.

        Tries to find an alias in the requested language first.
        Falls back to the default entity name if no alias is found.
        """
        # Get entity default name
        entity = await self.get_entity(entity_id)
        if not entity:
            return ""

        # Try to find alias in requested language
        aliases = await self.get_aliases(entity_id)
        for alias, lang in aliases:
            if lang == language:
                return alias

        # Fallback to default name
        return entity.name

    async def find_entity_by_name_or_alias(self, name: str) -> Entity | None:
        """Search by entity name OR any alias (case-insensitive)."""
        entity = await self.find_entity_by_name(name)
        if entity:
            return entity
        db = await self._conn()
        cursor = await db.execute(
            """SELECT e.* FROM entities e
               JOIN entity_aliases ea ON ea.entity_id = e.id
               WHERE LOWER(ea.alias) = LOWER(?)""",
            (name,),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return Entity(
            id=row["id"], name=row["name"], description=row["description"],
            entity_type=row["entity_type"], language=row["language"],
            play_count=row["play_count"],
            guess_success_count=row["guess_success_count"],
        )

    async def get_entity_count(self) -> int:
        """Return total number of entities."""
        db = await self._conn()
        cursor = await db.execute("SELECT COUNT(*) FROM entities")
        row = await cursor.fetchone()
        return row[0]

    # ---- Embeddings ----

    async def set_embedding(self, entity_id: int, embedding: np.ndarray) -> None:
        db = await self._conn()
        blob = embedding.astype(np.float32).tobytes()
        await db.execute(
            """INSERT INTO entity_embeddings (entity_id, embedding)
               VALUES (?, ?)
               ON CONFLICT(entity_id) DO UPDATE SET embedding = excluded.embedding""",
            (entity_id, blob),
        )
        await db.commit()

    async def get_embedding(self, entity_id: int) -> np.ndarray | None:
        db = await self._conn()
        cursor = await db.execute(
            "SELECT embedding FROM entity_embeddings WHERE entity_id = ?",
            (entity_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return np.frombuffer(row[0], dtype=np.float32).copy()

    async def get_all_embeddings(self) -> dict[int, np.ndarray]:
        db = await self._conn()
        cursor = await db.execute("SELECT entity_id, embedding FROM entity_embeddings")
        rows = await cursor.fetchall()
        return {
            r[0]: np.frombuffer(r[1], dtype=np.float32).copy()
            for r in rows
        }

    # ---- User Feedback (Learning) ----

    async def track_feedback(
        self,
        entity_id: int,
        attribute_id: int,
        user_answer: str,
        expected_value: float,
        language: str = "en",
    ) -> None:
        """Track user answer for learning purposes."""
        db = await self._conn()
        await db.execute(
            """INSERT INTO user_feedback
               (entity_id, attribute_id, user_answer, expected_value, session_language)
               VALUES (?, ?, ?, ?, ?)""",
            (entity_id, attribute_id, user_answer, expected_value, language),
        )
        await db.commit()

    async def get_feedback_stats(
        self, entity_id: int, attribute_id: int
    ) -> dict[str, int]:
        """Get feedback statistics for an entity-attribute pair.

        Returns count of each answer type (YES, NO, PROBABLY_YES, etc.)
        """
        db = await self._conn()
        cursor = await db.execute(
            """SELECT user_answer, COUNT(*) as count
               FROM user_feedback
               WHERE entity_id = ? AND attribute_id = ?
               GROUP BY user_answer""",
            (entity_id, attribute_id),
        )
        rows = await cursor.fetchall()
        return {r[0]: r[1] for r in rows}

    async def get_entity_feedback_count(self, entity_id: int) -> int:
        """Get total number of feedback entries for an entity."""
        db = await self._conn()
        cursor = await db.execute(
            "SELECT COUNT(*) FROM user_feedback WHERE entity_id = ?",
            (entity_id,),
        )
        row = await cursor.fetchone()
        return row[0] if row else 0

    async def calculate_learned_value(
        self, entity_id: int, attribute_id: int, current_value: float
    ) -> float | None:
        """Calculate new attribute value based on user feedback.

        Returns None if not enough feedback, otherwise returns weighted average.
        Requires at least 3 feedback samples to update.
        """
        stats = await self.get_feedback_stats(entity_id, attribute_id)
        if not stats:
            return None

        total = sum(stats.values())
        if total < 3:  # Need at least 3 samples
            return None

        # Convert answers to values
        answer_values = {
            "YES": 1.0,
            "PROBABLY_YES": 0.75,
            "DONT_KNOW": 0.5,
            "PROBABLY_NO": 0.25,
            "NO": 0.0,
        }

        # Calculate weighted average from feedback
        feedback_sum = 0.0
        for answer, count in stats.items():
            feedback_sum += answer_values.get(answer, 0.5) * count

        feedback_avg = feedback_sum / total

        # Blend current value with feedback (70% feedback, 30% current)
        # This prevents sudden jumps and maintains some stability
        new_value = 0.7 * feedback_avg + 0.3 * current_value

        return round(new_value, 2)

    async def apply_learning(self, min_feedback_count: int = 3) -> int:
        """Apply learning from user feedback to entity attributes.

        Updates entity attributes based on accumulated user feedback.
        Returns number of attributes updated.
        """
        db = await self._conn()

        # Get all entity-attribute pairs with enough feedback
        cursor = await db.execute(
            """SELECT entity_id, attribute_id, COUNT(*) as feedback_count
               FROM user_feedback
               GROUP BY entity_id, attribute_id
               HAVING feedback_count >= ?""",
            (min_feedback_count,),
        )
        rows = await cursor.fetchall()

        updated_count = 0
        for entity_id, attribute_id, _ in rows:
            # Get current value
            current_value = await self.get_entity_attribute(entity_id, attribute_id)
            if current_value is None:
                continue

            # Calculate new value from feedback
            new_value = await self.calculate_learned_value(
                entity_id, attribute_id, current_value
            )

            if new_value is not None and abs(new_value - current_value) > 0.05:
                # Update if difference is significant (>5%)
                await self.set_entity_attribute(entity_id, attribute_id, new_value)
                updated_count += 1

        return updated_count
