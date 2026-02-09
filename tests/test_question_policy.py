"""Tests for Question Policy (information gain based question selection).

Covers:
- Information gain computation
- Best attribute selection
- Skipping already-asked attributes
- Edge cases (single candidate, all same attribute values)
"""

from __future__ import annotations

import math

import pytest

from akinator.db.models import Attribute, Entity, GameMode, GameSession
from akinator.engine.question_policy import QuestionPolicy
from tests.conftest import SAMPLE_ATTRIBUTES, SAMPLE_ENTITIES


class TestInformationGain:
    """Information gain calculation for individual attributes."""

    def setup_method(self):
        self.policy = QuestionPolicy()

    def test_info_gain_is_non_negative(
        self, uniform_session: GameSession, sample_entities: list[Entity],
        sample_attributes: list[Attribute],
    ):
        """Information gain should always be >= 0."""
        for attr in sample_attributes:
            ig = self.policy.compute_info_gain(
                uniform_session, sample_entities, attr.key
            )
            assert ig >= -1e-9, f"Negative info gain for {attr.key}: {ig}"

    def test_discriminating_attribute_has_higher_gain(
        self, uniform_session: GameSession, sample_entities: list[Entity],
    ):
        """An attribute that splits candidates well should have higher IG
        than one that doesn't."""
        # is_fictional: 3 fictional (1.0) vs 2 real (0.0) → good split
        # is_male: 4 male (1.0) vs 1 female (0.0) → less balanced split
        ig_fictional = self.policy.compute_info_gain(
            uniform_session, sample_entities, "is_fictional"
        )
        ig_male = self.policy.compute_info_gain(
            uniform_session, sample_entities, "is_male"
        )
        assert ig_fictional > ig_male

    def test_uniform_attribute_has_zero_gain(self):
        """If all candidates have the same attribute value, IG should be ~0."""
        entities = [
            Entity(id=i, name=f"E{i}", description="", entity_type="character",
                   language="en", attributes={"same_attr": 1.0})
            for i in range(5)
        ]
        session = GameSession(
            session_id="uniform-attr", user_id=1,
            candidate_ids=[e.id for e in entities],
            weights=[0.2] * 5,
        )
        policy = QuestionPolicy()
        ig = policy.compute_info_gain(session, entities, "same_attr")
        assert math.isclose(ig, 0.0, abs_tol=1e-9)


class TestSelectBestAttribute:
    """Selecting the attribute with maximum information gain."""

    def setup_method(self):
        self.policy = QuestionPolicy()

    def test_select_returns_best_attribute(
        self, uniform_session: GameSession, sample_entities: list[Entity],
        sample_attributes: list[Attribute],
    ):
        """Selected attribute should have the highest information gain."""
        best_key = self.policy.select(
            uniform_session, sample_entities, sample_attributes
        )
        assert best_key is not None

        # Verify it's actually the best by computing all IGs
        best_ig = self.policy.compute_info_gain(
            uniform_session, sample_entities, best_key
        )
        for attr in sample_attributes:
            ig = self.policy.compute_info_gain(
                uniform_session, sample_entities, attr.key
            )
            assert best_ig >= ig - 1e-9

    def test_select_skips_already_asked(
        self, uniform_session: GameSession, sample_entities: list[Entity],
        sample_attributes: list[Attribute],
    ):
        """Attributes already asked should not be selected."""
        # Mark first attribute as asked
        uniform_session.asked_attributes.append(sample_attributes[0].id)
        best_key = self.policy.select(
            uniform_session, sample_entities, sample_attributes
        )
        assert best_key != sample_attributes[0].key

    def test_select_returns_none_when_all_asked(
        self, uniform_session: GameSession, sample_entities: list[Entity],
        sample_attributes: list[Attribute],
    ):
        """When all attributes are asked, select should return None."""
        uniform_session.asked_attributes = [a.id for a in sample_attributes]
        best_key = self.policy.select(
            uniform_session, sample_entities, sample_attributes
        )
        assert best_key is None


class TestEdgeCases:
    """Edge cases in question selection."""

    def test_single_candidate(self, sample_attributes: list[Attribute]):
        """With one candidate, all IGs should be 0."""
        entities = [SAMPLE_ENTITIES[0]]
        session = GameSession(
            session_id="single", user_id=1,
            candidate_ids=[entities[0].id], weights=[1.0],
        )
        policy = QuestionPolicy()
        for attr in sample_attributes:
            ig = policy.compute_info_gain(session, entities, attr.key)
            assert math.isclose(ig, 0.0, abs_tol=1e-9)

    def test_two_identical_candidates(self, sample_attributes: list[Attribute]):
        """Two candidates with identical attributes → IG ~0 for all."""
        attrs = {"is_fictional": 1.0, "is_male": 1.0, "from_movie": 1.0,
                 "from_game": 0.0, "is_villain": 0.0, "from_russia": 0.0}
        entities = [
            Entity(id=1, name="A", description="", entity_type="character",
                   language="en", attributes=dict(attrs)),
            Entity(id=2, name="B", description="", entity_type="character",
                   language="en", attributes=dict(attrs)),
        ]
        session = GameSession(
            session_id="identical", user_id=1,
            candidate_ids=[1, 2], weights=[0.5, 0.5],
        )
        policy = QuestionPolicy()
        for attr in sample_attributes:
            ig = policy.compute_info_gain(session, entities, attr.key)
            assert math.isclose(ig, 0.0, abs_tol=1e-9)

    def test_perfect_split_has_maximum_gain(self):
        """An attribute that perfectly splits two equal candidates
        should have maximum IG (1 bit)."""
        entities = [
            Entity(id=1, name="A", description="", entity_type="character",
                   language="en", attributes={"split_attr": 1.0}),
            Entity(id=2, name="B", description="", entity_type="character",
                   language="en", attributes={"split_attr": 0.0}),
        ]
        session = GameSession(
            session_id="perfect-split", user_id=1,
            candidate_ids=[1, 2], weights=[0.5, 0.5],
        )
        policy = QuestionPolicy()
        ig = policy.compute_info_gain(session, entities, "split_attr")
        # For 2 equal-weight candidates, perfect split → IG = 1 bit
        assert math.isclose(ig, 1.0, abs_tol=1e-6)
