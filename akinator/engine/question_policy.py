"""Question Policy — information gain based question selection."""

from __future__ import annotations

import math

from akinator.config import CONDITIONAL_EXCLUSIONS, EXCLUSIVE_GROUPS
from akinator.db.models import Answer, Attribute, Entity, GameSession


def _entropy(weights: list[float]) -> float:
    h = 0.0
    for w in weights:
        if w > 0:
            h -= w * math.log2(w)
    return h


class QuestionPolicy:

    # ── Public API (backward-compatible) ──

    def compute_info_gain(
        self,
        session: GameSession,
        entities: list[Entity],
        attribute_key: str,
    ) -> float:
        """Compute information gain for *attribute_key*.

        Accepts a full entity list and resolves candidates internally.
        """
        entity_map = {e.id: e for e in entities}
        candidate_entities = [entity_map.get(cid) for cid in session.candidate_ids]
        return self._compute_ig(session, candidate_entities, attribute_key)

    # ── Internal optimised version ──

    def _compute_ig(
        self,
        session: GameSession,
        candidate_entities: list[Entity | None],
        attribute_key: str,
        h_current: float | None = None,
    ) -> float:
        """Information gain with pre-resolved candidates and optional cached entropy."""
        n = len(session.candidate_ids)
        if n <= 1:
            return 0.0

        weights = session.weights
        if h_current is None:
            h_current = _entropy(weights)

        # For each candidate, get attribute value (default 0.5)
        p_values: list[float] = []
        for entity in candidate_entities:
            if entity and attribute_key in entity.attributes:
                p_values.append(entity.attributes[attribute_key])
            else:
                p_values.append(0.5)

        # Weighted mean
        mean_p = 0.0
        for w, p in zip(weights, p_values):
            mean_p += w * p

        # Variance penalty: low variance → attribute cannot discriminate
        variance = 0.0
        for w, p in zip(weights, p_values):
            diff = p - mean_p
            variance += w * diff * diff

        if variance < 0.01:
            return 0.0

        # P(yes) = sum(w_i * p_i)
        p_yes = mean_p
        p_no = 1.0 - p_yes

        if p_yes < 1e-12 or p_no < 1e-12:
            return 0.0

        # Posterior weights for "yes" answer
        weights_yes = [w * p for w, p in zip(weights, p_values)]
        z_yes = sum(weights_yes)
        if z_yes > 0:
            weights_yes = [w / z_yes for w in weights_yes]
        h_yes = _entropy(weights_yes)

        # Posterior weights for "no" answer
        weights_no = [w * (1.0 - p) for w, p in zip(weights, p_values)]
        z_no = sum(weights_no)
        if z_no > 0:
            weights_no = [w / z_no for w in weights_no]
        h_no = _entropy(weights_no)

        expected_h = p_yes * h_yes + p_no * h_no
        ig = h_current - expected_h
        ig = max(ig, 0.0)

        # Scale down low-variance attributes
        ig *= min(1.0, variance / 0.05)

        return ig

    # ── Exclusion logic ──

    @staticmethod
    def _get_excluded_keys(session: GameSession, attributes: list[Attribute]) -> set[str]:
        """Find attribute keys to skip based on exclusive groups and conditional exclusions."""
        if not session.history:
            return set()

        # Collect confirmed and denied keys
        confirmed_keys: set[str] = set()
        denied_keys: set[str] = set()
        for qa in session.history:
            if qa.answer in (Answer.YES, Answer.PROBABLY_YES):
                confirmed_keys.add(qa.attribute_key)
            elif qa.answer in (Answer.NO, Answer.PROBABLY_NO):
                denied_keys.add(qa.attribute_key)

        excluded: set[str] = set()

        # Exclusive groups
        for group in EXCLUSIVE_GROUPS:
            for key in group:
                if key in confirmed_keys:
                    excluded.update(k for k in group if k != key)
                    break

        # Conditional exclusions
        for (key, answer_type), excluded_list in CONDITIONAL_EXCLUSIONS.items():
            if answer_type == "yes" and key in confirmed_keys:
                excluded.update(excluded_list)
            elif answer_type == "no" and key in denied_keys:
                excluded.update(excluded_list)

        return excluded

    # ── Question selection ──

    def select(
        self,
        session: GameSession,
        entities: list[Entity],
        attributes: list[Attribute],
    ) -> str | None:
        asked_set = set(session.asked_attributes)
        excluded_keys = self._get_excluded_keys(session, attributes)

        # Build entity map and resolve candidates ONCE per question round
        entity_map = {e.id: e for e in entities}
        candidate_entities = [entity_map.get(cid) for cid in session.candidate_ids]

        # Pre-compute current entropy (same for all attributes this round)
        h_current = _entropy(session.weights)

        best_key = None
        best_ig = -1.0

        for attr in attributes:
            if attr.id in asked_set:
                continue
            if attr.key in excluded_keys:
                continue
            ig = self._compute_ig(session, candidate_entities, attr.key, h_current)
            if ig > best_ig:
                best_ig = ig
                best_key = attr.key

        return best_key
