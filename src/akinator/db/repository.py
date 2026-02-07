"""Database Repository — SQLite CRUD operations. (Stub — TDD.)"""

from __future__ import annotations

import numpy as np

from akinator.db.models import Attribute, Entity


class Repository:

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self) -> None:
        raise NotImplementedError

    async def close(self) -> None:
        raise NotImplementedError

    async def list_tables(self) -> list[str]:
        raise NotImplementedError

    async def add_entity(
        self, name: str, description: str, entity_type: str, language: str,
    ) -> int:
        raise NotImplementedError

    async def get_entity(self, entity_id: int, with_attributes: bool = False) -> Entity | None:
        raise NotImplementedError

    async def get_all_entities(self) -> list[Entity]:
        raise NotImplementedError

    async def increment_play_count(self, entity_id: int) -> None:
        raise NotImplementedError

    async def add_attribute(
        self, key: str, question_ru: str, question_en: str, category: str,
    ) -> int:
        raise NotImplementedError

    async def get_all_attributes(self) -> list[Attribute]:
        raise NotImplementedError

    async def set_entity_attribute(
        self, entity_id: int, attribute_id: int, value: float,
    ) -> None:
        raise NotImplementedError

    async def get_entity_attribute(
        self, entity_id: int, attribute_id: int,
    ) -> float | None:
        raise NotImplementedError

    async def add_alias(self, entity_id: int, alias: str, language: str) -> None:
        raise NotImplementedError

    async def get_aliases(self, entity_id: int) -> list[tuple[str, str]]:
        raise NotImplementedError

    async def set_embedding(self, entity_id: int, embedding: np.ndarray) -> None:
        raise NotImplementedError

    async def get_embedding(self, entity_id: int) -> np.ndarray | None:
        raise NotImplementedError

    async def get_all_embeddings(self) -> dict[int, np.ndarray]:
        raise NotImplementedError
