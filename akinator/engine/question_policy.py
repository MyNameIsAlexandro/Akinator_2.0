"""Question Policy — information gain based question selection."""

from __future__ import annotations

import math
from typing import Optional

from akinator.db.models import Answer, Attribute, Entity, GameSession

# Related attribute groups - if user answers one, related ones are skipped or implied
RELATED_ATTRIBUTES = {
    # Books & Literature
    "from_book": ["from_literature"],
    "from_literature": ["from_book"],
    # Geography regions
    "from_japan": ["from_asia"],
    "from_china": ["from_asia"],
    "from_russia": ["from_europe", "from_asia"],
    # Era overlaps
    "era_20th_century": ["era_21st_century", "era_modern"],
    "era_21st_century": ["era_20th_century"],
    "era_modern": ["era_medieval", "era_ancient"],
    # Birth decades (if answered one, skip nearby)
    "born_1970s": ["born_1960s", "born_1980s"],
    "born_1980s": ["born_1970s", "born_1990s"],
    "born_1960s": ["born_1950s", "born_1970s"],
    "born_1950s": ["born_1940s", "born_1960s"],
    "born_1940s": ["born_1930s", "born_1950s"],
}


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

    def get_implied_skip_keys(self, session: GameSession, attributes: list[Attribute]) -> set[str]:
        """Get attribute keys that should be skipped based on previous answers.

        Skip related attributes regardless of answer type - if user answered
        one attribute in a group, don't ask about closely related ones.
        """
        skip_keys: set[str] = set()

        for qa in session.history:
            asked_key = qa.attribute_key
            # Skip related attributes regardless of answer type
            # (if user doesn't know about "books", they probably don't know about "literature" either)
            if asked_key in RELATED_ATTRIBUTES:
                skip_keys.update(RELATED_ATTRIBUTES[asked_key])

        return skip_keys

    def select(
        self,
        session: GameSession,
        entities: list[Entity],
        attributes: list[Attribute],
    ) -> Optional[str]:
        asked_set = set(session.asked_attributes)
        attr_id_to_key = {a.id: a.key for a in attributes}

        # Get keys to skip based on related answers
        skip_keys = self.get_implied_skip_keys(session, attributes)

        best_key = None
        best_ig = -1.0

        for attr in attributes:
            if attr.id in asked_set:
                continue
            # Skip related attributes
            if attr.key in skip_keys:
                continue
            ig = self.compute_info_gain(session, entities, attr.key)
            if ig > best_ig:
                best_ig = ig
                best_key = attr.key

        return best_key
