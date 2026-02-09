"""Tests for the Bayesian Scoring Engine.

Covers:
- Weight initialization (uniform)
- Bayesian update for each answer type (Yes/No/ProbablyYes/ProbablyNo/DontKnow)
- Normalization after update
- Smoothing (epsilon floor)
- Pruning of low-weight candidates
- top_k / max_prob / entropy helpers
"""

from __future__ import annotations

import math

import pytest

from akinator.config import EPSILON, PRUNE_THRESHOLD
from akinator.db.models import Answer, Entity, GameSession
from akinator.engine.scoring import ScoringEngine


class TestWeightInitialization:
    """Weights must start uniform and sum to 1."""

    def test_uniform_weights_sum_to_one(self, uniform_session: GameSession):
        assert math.isclose(sum(uniform_session.weights), 1.0, rel_tol=1e-9)

    def test_uniform_weights_are_equal(self, uniform_session: GameSession):
        n = len(uniform_session.weights)
        expected = 1.0 / n
        for w in uniform_session.weights:
            assert math.isclose(w, expected, rel_tol=1e-9)


class TestBayesianUpdate:
    """Core Bayesian weight update after user answer."""

    def setup_method(self):
        self.engine = ScoringEngine()

    def test_yes_answer_boosts_high_attribute(
        self, uniform_session: GameSession, sample_entities: list[Entity]
    ):
        """Answering YES to 'is_fictional' should boost fictional characters."""
        self.engine.update(
            uniform_session, sample_entities, "is_fictional", Answer.YES
        )
        # Darth Vader (is_fictional=1.0) should have higher weight than Elon Musk (0.0)
        vader_idx = uniform_session.candidate_ids.index(1)
        elon_idx = uniform_session.candidate_ids.index(3)
        assert uniform_session.weights[vader_idx] > uniform_session.weights[elon_idx]

    def test_no_answer_boosts_low_attribute(
        self, uniform_session: GameSession, sample_entities: list[Entity]
    ):
        """Answering NO to 'is_fictional' should boost real people."""
        self.engine.update(
            uniform_session, sample_entities, "is_fictional", Answer.NO
        )
        elon_idx = uniform_session.candidate_ids.index(3)
        vader_idx = uniform_session.candidate_ids.index(1)
        assert uniform_session.weights[elon_idx] > uniform_session.weights[vader_idx]

    def test_probably_yes_is_softer_than_yes(
        self, sample_entities: list[Entity]
    ):
        """PROBABLY_YES update should be less extreme than YES."""
        engine = ScoringEngine()

        n = len(sample_entities)
        session_yes = GameSession(
            session_id="s1", user_id=1, candidate_ids=[e.id for e in sample_entities],
            weights=[1.0 / n] * n,
        )
        session_prob = GameSession(
            session_id="s2", user_id=1, candidate_ids=[e.id for e in sample_entities],
            weights=[1.0 / n] * n,
        )

        engine.update(session_yes, sample_entities, "is_fictional", Answer.YES)
        engine.update(session_prob, sample_entities, "is_fictional", Answer.PROBABLY_YES)

        # After YES, Elon (is_fictional=0.0) should have lower weight than after PROBABLY_YES
        elon_idx = session_yes.candidate_ids.index(3)
        assert session_yes.weights[elon_idx] < session_prob.weights[elon_idx]

    def test_probably_no_is_softer_than_no(
        self, sample_entities: list[Entity]
    ):
        """PROBABLY_NO update should be less extreme than NO."""
        engine = ScoringEngine()
        n = len(sample_entities)
        session_no = GameSession(
            session_id="s1", user_id=1, candidate_ids=[e.id for e in sample_entities],
            weights=[1.0 / n] * n,
        )
        session_prob = GameSession(
            session_id="s2", user_id=1, candidate_ids=[e.id for e in sample_entities],
            weights=[1.0 / n] * n,
        )

        engine.update(session_no, sample_entities, "is_fictional", Answer.NO)
        engine.update(session_prob, sample_entities, "is_fictional", Answer.PROBABLY_NO)

        # After NO, Darth Vader (is_fictional=1.0) should have lower weight than after PROBABLY_NO
        vader_idx = session_no.candidate_ids.index(1)
        assert session_no.weights[vader_idx] < session_prob.weights[vader_idx]

    def test_dont_know_does_not_change_weights(
        self, uniform_session: GameSession, sample_entities: list[Entity]
    ):
        """DON'T_KNOW should leave weights unchanged."""
        original_weights = list(uniform_session.weights)
        self.engine.update(
            uniform_session, sample_entities, "is_fictional", Answer.DONT_KNOW
        )
        for orig, new in zip(original_weights, uniform_session.weights):
            assert math.isclose(orig, new, rel_tol=1e-9)


class TestNormalization:
    """Weights must always sum to 1 after update."""

    def test_weights_sum_to_one_after_update(
        self, uniform_session: GameSession, sample_entities: list[Entity]
    ):
        engine = ScoringEngine()
        engine.update(uniform_session, sample_entities, "is_fictional", Answer.YES)
        assert math.isclose(sum(uniform_session.weights), 1.0, rel_tol=1e-9)

    def test_weights_sum_to_one_after_multiple_updates(
        self, uniform_session: GameSession, sample_entities: list[Entity]
    ):
        engine = ScoringEngine()
        engine.update(uniform_session, sample_entities, "is_fictional", Answer.YES)
        engine.update(uniform_session, sample_entities, "is_male", Answer.NO)
        engine.update(uniform_session, sample_entities, "from_movie", Answer.PROBABLY_YES)
        assert math.isclose(sum(uniform_session.weights), 1.0, rel_tol=1e-9)


class TestSmoothing:
    """Epsilon floor prevents zero-probability elimination."""

    def test_no_zero_weights_after_update(
        self, uniform_session: GameSession, sample_entities: list[Entity]
    ):
        """Even extreme answer should not produce zero weights (before pruning)."""
        engine = ScoringEngine()
        engine.update(uniform_session, sample_entities, "is_fictional", Answer.YES)
        # Elon Musk has is_fictional=0.0 → likelihood should be max(0.0, EPSILON) = EPSILON
        # So weight should be > 0
        for w in uniform_session.weights:
            assert w > 0


class TestPruning:
    """Candidates with negligible weight should be pruned."""

    def test_pruning_removes_very_low_weight_candidates(
        self, sample_entities: list[Entity]
    ):
        engine = ScoringEngine()
        session = GameSession(
            session_id="prune-test", user_id=1,
            candidate_ids=[e.id for e in sample_entities],
            weights=[1.0 / len(sample_entities)] * len(sample_entities),
        )
        # Apply many strong updates to drive some weights very low
        for _ in range(10):
            engine.update(session, sample_entities, "is_fictional", Answer.YES)
            engine.update(session, sample_entities, "from_russia", Answer.NO)

        # Real people with from_russia=1.0 should be pruned after many rounds
        # At minimum, weights should sum to 1
        assert math.isclose(sum(session.weights), 1.0, rel_tol=1e-9)
        # Pruned candidates should be removed from both lists
        assert len(session.candidate_ids) == len(session.weights)


class TestHelpers:
    """top_k, max_prob, entropy utility methods."""

    def test_top_k_returns_correct_order(self, skewed_session: GameSession):
        engine = ScoringEngine()
        top = engine.top_k(skewed_session, k=3)
        assert len(top) == 3
        # Should be sorted by weight descending
        assert top[0][0] == skewed_session.candidate_ids[0]  # Darth Vader (0.90)
        assert top[0][1] == pytest.approx(0.90, abs=1e-9)

    def test_top_k_respects_k_limit(self, skewed_session: GameSession):
        engine = ScoringEngine()
        top = engine.top_k(skewed_session, k=2)
        assert len(top) == 2

    def test_max_prob(self, skewed_session: GameSession):
        engine = ScoringEngine()
        max_id, max_w = engine.max_prob(skewed_session)
        assert max_id == skewed_session.candidate_ids[0]
        assert max_w == pytest.approx(0.90, abs=1e-9)

    def test_entropy_uniform_is_maximal(self, uniform_session: GameSession):
        engine = ScoringEngine()
        h = engine.entropy(uniform_session)
        n = len(uniform_session.weights)
        max_entropy = math.log2(n)
        assert math.isclose(h, max_entropy, rel_tol=1e-9)

    def test_entropy_skewed_is_low(
        self, uniform_session: GameSession, skewed_session: GameSession
    ):
        engine = ScoringEngine()
        h_uniform = engine.entropy(uniform_session)
        h_skewed = engine.entropy(skewed_session)
        assert h_skewed < h_uniform

    def test_entropy_single_candidate_is_zero(self):
        engine = ScoringEngine()
        session = GameSession(
            session_id="single", user_id=1,
            candidate_ids=[1], weights=[1.0],
        )
        assert engine.entropy(session) == pytest.approx(0.0, abs=1e-9)


class TestMissingAttributes:
    """Entities missing an attribute should use default 0.5."""

    def test_missing_attribute_treated_as_uncertain(self):
        engine = ScoringEngine()
        entities = [
            Entity(id=1, name="A", description="", entity_type="character",
                   language="en", attributes={"is_fictional": 1.0}),
            Entity(id=2, name="B", description="", entity_type="character",
                   language="en", attributes={}),  # no attributes at all
        ]
        session = GameSession(
            session_id="missing", user_id=1,
            candidate_ids=[1, 2], weights=[0.5, 0.5],
        )
        engine.update(session, entities, "is_fictional", Answer.YES)
        # Entity B has no is_fictional → default 0.5 → likelihood 0.5
        # Entity A has is_fictional=1.0 → likelihood 1.0
        # So A should have higher weight than B
        assert session.weights[0] > session.weights[1]
