"""Scoring Engine — Bayesian weight updates."""

from __future__ import annotations

import math

from akinator.config import EPSILON, PRUNE_THRESHOLD
from akinator.db.models import Answer, Entity, GameSession


# Likelihood given attribute value p and answer
def _likelihood(p: float, answer: Answer) -> float:
    if answer == Answer.YES:
        L = p
    elif answer == Answer.NO:
        L = 1.0 - p
    elif answer == Answer.PROBABLY_YES:
        L = 0.5 * p + 0.25
    elif answer == Answer.PROBABLY_NO:
        L = 0.75 - 0.5 * p
    else:  # DONT_KNOW
        return 1.0
    return max(L, EPSILON)


class ScoringEngine:

    def update(
        self,
        session: GameSession,
        entities: list[Entity],
        attribute_key: str,
        answer: Answer,
    ) -> None:
        if answer == Answer.DONT_KNOW:
            return

        entity_map = {e.id: e for e in entities}

        for i, cid in enumerate(session.candidate_ids):
            entity = entity_map.get(cid)
            p = 0.5  # default for missing attribute
            if entity and attribute_key in entity.attributes:
                p = entity.attributes[attribute_key]
            session.weights[i] *= _likelihood(p, answer)

        # Normalize
        total = sum(session.weights)
        if total > 0:
            session.weights = [w / total for w in session.weights]

        # Prune
        surviving_ids = []
        surviving_weights = []
        for cid, w in zip(session.candidate_ids, session.weights):
            if w >= PRUNE_THRESHOLD:
                surviving_ids.append(cid)
                surviving_weights.append(w)

        if surviving_ids:
            session.candidate_ids = surviving_ids
            session.weights = surviving_weights
            # Re-normalize after pruning
            total = sum(session.weights)
            session.weights = [w / total for w in session.weights]

    def top_k(self, session: GameSession, k: int = 5) -> list[tuple[int, float]]:
        pairs = list(zip(session.candidate_ids, session.weights))
        pairs.sort(key=lambda x: x[1], reverse=True)
        return pairs[:k]

    def max_prob(self, session: GameSession) -> tuple[int, float]:
        best_idx = 0
        for i, w in enumerate(session.weights):
            if w > session.weights[best_idx]:
                best_idx = i
        return session.candidate_ids[best_idx], session.weights[best_idx]

    def entropy(self, session: GameSession) -> float:
        h = 0.0
        for w in session.weights:
            if w > 0:
                h -= w * math.log2(w)
        return h
