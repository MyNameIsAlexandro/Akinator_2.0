"""Question Policy — information gain based question selection."""

from __future__ import annotations

import math

from akinator.config import EXCLUSIVE_GROUPS
from akinator.db.models import Answer, Attribute, Entity, GameSession


def _entropy(weights: list[float]) -> float:
    h = 0.0
    for w in weights:
        if w > 0:
            h -= w * math.log2(w)
    return h


class QuestionPolicy:

    def compute_info_gain(
        self,
        session: GameSession,
        entities: list[Entity],
        attribute_key: str,
    ) -> float:
        entity_map = {e.id: e for e in entities}
        n = len(session.candidate_ids)
        if n <= 1:
            return 0.0

        h_current = _entropy(session.weights)

        # For each candidate, get attribute value (default 0.5)
        p_values = []
        for cid in session.candidate_ids:
            entity = entity_map.get(cid)
            if entity and attribute_key in entity.attributes:
                p_values.append(entity.attributes[attribute_key])
            else:
                p_values.append(0.5)

        # P(yes) = sum(w_i * p_i)
        p_yes = sum(w * p for w, p in zip(session.weights, p_values))
        p_no = 1.0 - p_yes

        if p_yes < 1e-12 or p_no < 1e-12:
            return 0.0

        # Posterior weights for "yes" answer
        weights_yes = [w * p for w, p in zip(session.weights, p_values)]
        z_yes = sum(weights_yes)
        if z_yes > 0:
            weights_yes = [w / z_yes for w in weights_yes]
        h_yes = _entropy(weights_yes)

        # Posterior weights for "no" answer
        weights_no = [w * (1.0 - p) for w, p in zip(session.weights, p_values)]
        z_no = sum(weights_no)
        if z_no > 0:
            weights_no = [w / z_no for w in weights_no]
        h_no = _entropy(weights_no)

        expected_h = p_yes * h_yes + p_no * h_no
        ig = h_current - expected_h
        return max(ig, 0.0)

    @staticmethod
    def _get_excluded_keys(session: GameSession, attributes: list[Attribute]) -> set[str]:
        """Find attribute keys to skip based on exclusive groups.

        When a user answered yes/probably_yes for an attribute in an
        exclusive group, all OTHER attributes in that group are skipped.
        """
        if not session.history:
            return set()

        # Build attr_id → key lookup
        id_to_key = {a.id: a.key for a in attributes}

        # Collect confirmed keys (yes / probably_yes answers)
        confirmed_keys: set[str] = set()
        for qa in session.history:
            if qa.answer in (Answer.YES, Answer.PROBABLY_YES):
                confirmed_keys.add(qa.attribute_key)

        excluded: set[str] = set()
        for group in EXCLUSIVE_GROUPS:
            for key in group:
                if key in confirmed_keys:
                    # Exclude all OTHER keys in this group
                    excluded.update(k for k in group if k != key)
                    break
        return excluded

    def select(
        self,
        session: GameSession,
        entities: list[Entity],
        attributes: list[Attribute],
    ) -> str | None:
        asked_set = set(session.asked_attributes)
        excluded_keys = self._get_excluded_keys(session, attributes)
        best_key = None
        best_ig = -1.0

        for attr in attributes:
            if attr.id in asked_set:
                continue
            if attr.key in excluded_keys:
                continue
            ig = self.compute_info_gain(session, entities, attr.key)
            if ig > best_ig:
                best_ig = ig
                best_key = attr.key

        return best_key
