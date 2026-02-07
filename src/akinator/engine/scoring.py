"""Scoring Engine — Bayesian weight updates. (Stub — TDD: implement to pass tests.)"""

from __future__ import annotations

from akinator.db.models import Answer, Entity, GameSession


class ScoringEngine:

    def update(
        self,
        session: GameSession,
        entities: list[Entity],
        attribute_key: str,
        answer: Answer,
    ) -> None:
        raise NotImplementedError

    def top_k(self, session: GameSession, k: int = 5) -> list[tuple[int, float]]:
        raise NotImplementedError

    def max_prob(self, session: GameSession) -> tuple[int, float]:
        raise NotImplementedError

    def entropy(self, session: GameSession) -> float:
        raise NotImplementedError
