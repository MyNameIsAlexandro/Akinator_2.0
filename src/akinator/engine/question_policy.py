"""Question Policy — information gain based question selection. (Stub — TDD.)"""

from __future__ import annotations

from akinator.db.models import Attribute, Entity, GameSession


class QuestionPolicy:

    def compute_info_gain(
        self,
        session: GameSession,
        entities: list[Entity],
        attribute_key: str,
    ) -> float:
        raise NotImplementedError

    def select(
        self,
        session: GameSession,
        entities: list[Entity],
        attributes: list[Attribute],
    ) -> str | None:
        raise NotImplementedError
