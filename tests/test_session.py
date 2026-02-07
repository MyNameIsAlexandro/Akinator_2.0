"""Tests for the Game Session Manager.

Covers:
- Session lifecycle (create, play, guess, learn, finish)
- Mode transitions
- Guess decision logic (threshold, max questions, few candidates)
- Integration of scoring + question policy
- Second guess logic
"""

from __future__ import annotations

import pytest

from akinator.config import GUESS_THRESHOLD, MAX_QUESTIONS, SECOND_GUESS_THRESHOLD
from akinator.db.models import Answer, Entity, GameMode, GameSession
from akinator.engine.session import GameSessionManager
from akinator.engine.scoring import ScoringEngine
from akinator.engine.question_policy import QuestionPolicy


class TestSessionCreation:
    """Creating and initializing game sessions."""

    def test_create_session(self):
        """New session should have correct initial state."""
        manager = GameSessionManager(
            scoring_engine=ScoringEngine(),
            question_policy=QuestionPolicy(),
        )
        session = manager.create_session(user_id=42, language="ru")
        assert session.user_id == 42
        assert session.language == "ru"
        assert session.mode == GameMode.WAITING_HINT
        assert session.question_count == 0
        assert session.guess_count == 0
        assert session.history == []

    def test_init_with_candidates(self):
        """Initializing with candidates should set uniform weights."""
        manager = GameSessionManager(
            scoring_engine=ScoringEngine(),
            question_policy=QuestionPolicy(),
        )
        session = manager.create_session(user_id=42)
        candidate_ids = [1, 2, 3, 4, 5]
        manager.init_candidates(session, candidate_ids)
        assert session.candidate_ids == candidate_ids
        assert len(session.weights) == 5
        assert all(w == pytest.approx(0.2) for w in session.weights)
        assert session.mode == GameMode.ASKING

    def test_init_with_similarity_scores(self):
        """Initializing with similarity scores should set proportional weights."""
        manager = GameSessionManager(
            scoring_engine=ScoringEngine(),
            question_policy=QuestionPolicy(),
        )
        session = manager.create_session(user_id=42)
        candidate_ids = [1, 2, 3]
        scores = [0.9, 0.6, 0.3]
        manager.init_candidates(session, candidate_ids, scores)
        # Weights should be proportional to scores
        assert session.weights[0] > session.weights[1] > session.weights[2]
        assert sum(session.weights) == pytest.approx(1.0)


class TestGuessDecision:
    """When should the bot make a guess."""

    def setup_method(self):
        self.manager = GameSessionManager(
            scoring_engine=ScoringEngine(),
            question_policy=QuestionPolicy(),
        )

    def test_should_guess_when_confident(self):
        """Guess when max probability exceeds threshold."""
        session = GameSession(
            session_id="test", user_id=1,
            candidate_ids=[1, 2, 3],
            weights=[GUESS_THRESHOLD + 0.01, 0.07, 0.07],
            mode=GameMode.ASKING,
        )
        assert self.manager.should_guess(session) is True

    def test_should_not_guess_when_uncertain(self):
        """Don't guess when max probability is below threshold."""
        session = GameSession(
            session_id="test", user_id=1,
            candidate_ids=[1, 2, 3],
            weights=[0.4, 0.3, 0.3],
            mode=GameMode.ASKING,
        )
        assert self.manager.should_guess(session) is False

    def test_should_guess_at_max_questions(self):
        """Force guess when max questions reached."""
        session = GameSession(
            session_id="test", user_id=1,
            candidate_ids=[1, 2, 3],
            weights=[0.4, 0.3, 0.3],
            mode=GameMode.ASKING,
            question_count=MAX_QUESTIONS,
        )
        assert self.manager.should_guess(session) is True

    def test_should_guess_when_two_candidates_left(self):
        """Guess when only 2 candidates with significant weight remain."""
        session = GameSession(
            session_id="test", user_id=1,
            candidate_ids=[1, 2],
            weights=[0.6, 0.4],
            mode=GameMode.ASKING,
        )
        assert self.manager.should_guess(session) is True


class TestModeTransitions:
    """Game mode state machine transitions."""

    def setup_method(self):
        self.manager = GameSessionManager(
            scoring_engine=ScoringEngine(),
            question_policy=QuestionPolicy(),
        )

    def test_waiting_hint_to_asking(self):
        """Skipping hint should transition to ASKING."""
        session = self.manager.create_session(user_id=42)
        self.manager.init_candidates(session, [1, 2, 3])
        assert session.mode == GameMode.ASKING

    def test_asking_to_guessing(self):
        """When should_guess is true, mode transitions to GUESSING."""
        session = GameSession(
            session_id="test", user_id=1,
            candidate_ids=[1, 2, 3],
            weights=[0.90, 0.05, 0.05],
            mode=GameMode.ASKING,
        )
        assert self.manager.should_guess(session) is True

    def test_correct_guess_to_finished(self):
        """Correct guess should end the game."""
        session = GameSession(
            session_id="test", user_id=1,
            candidate_ids=[1, 2, 3],
            weights=[0.90, 0.05, 0.05],
            mode=GameMode.GUESSING,
        )
        self.manager.handle_guess_response(session, correct=True)
        assert session.mode == GameMode.FINISHED

    def test_wrong_guess_to_learning(self):
        """Wrong guess with no second candidate → learning mode."""
        session = GameSession(
            session_id="test", user_id=1,
            candidate_ids=[1, 2, 3],
            weights=[0.90, 0.05, 0.05],
            mode=GameMode.GUESSING,
            guess_count=2,
        )
        self.manager.handle_guess_response(session, correct=False)
        assert session.mode == GameMode.LEARNING

    def test_wrong_first_guess_allows_second(self):
        """Wrong first guess should allow a second if 2nd candidate is strong."""
        session = GameSession(
            session_id="test", user_id=1,
            candidate_ids=[1, 2, 3],
            weights=[0.28, SECOND_GUESS_THRESHOLD + 0.01, SECOND_GUESS_THRESHOLD + 0.01],
            mode=GameMode.GUESSING,
            guess_count=0,
        )
        result = self.manager.handle_guess_response(session, correct=False)
        # Should still be in GUESSING for second attempt
        assert session.mode == GameMode.GUESSING
        assert session.guess_count == 1

    def test_learning_to_finished(self):
        """After learning, session should finish."""
        session = GameSession(
            session_id="test", user_id=1,
            mode=GameMode.LEARNING,
            candidate_ids=[], weights=[],
        )
        self.manager.finish_learning(session)
        assert session.mode == GameMode.FINISHED


class TestGetGuessCandidate:
    """Getting the candidate to guess."""

    def setup_method(self):
        self.manager = GameSessionManager(
            scoring_engine=ScoringEngine(),
            question_policy=QuestionPolicy(),
        )

    def test_first_guess_is_top_candidate(self):
        """First guess should be the highest-weight candidate."""
        session = GameSession(
            session_id="test", user_id=1,
            candidate_ids=[10, 20, 30],
            weights=[0.1, 0.8, 0.1],
            mode=GameMode.GUESSING,
            guess_count=0,
        )
        candidate_id = self.manager.get_guess_candidate(session)
        assert candidate_id == 20

    def test_second_guess_is_second_candidate(self):
        """Second guess should be the second-highest candidate."""
        session = GameSession(
            session_id="test", user_id=1,
            candidate_ids=[10, 20, 30],
            weights=[0.1, 0.8, 0.1],
            mode=GameMode.GUESSING,
            guess_count=1,
        )
        candidate_id = self.manager.get_guess_candidate(session)
        # Second highest is 10 or 30 (both 0.1), implementation picks first
        assert candidate_id in [10, 30]


class TestProcessAnswer:
    """Processing a user answer updates session state correctly."""

    def test_process_answer_increments_question_count(
        self, uniform_session: GameSession, sample_entities: list[Entity],
        sample_attributes,
    ):
        manager = GameSessionManager(
            scoring_engine=ScoringEngine(),
            question_policy=QuestionPolicy(),
        )
        attr = sample_attributes[0]
        manager.process_answer(
            uniform_session, sample_entities, attr, Answer.YES
        )
        assert uniform_session.question_count == 1

    def test_process_answer_records_history(
        self, uniform_session: GameSession, sample_entities: list[Entity],
        sample_attributes,
    ):
        manager = GameSessionManager(
            scoring_engine=ScoringEngine(),
            question_policy=QuestionPolicy(),
        )
        attr = sample_attributes[0]
        manager.process_answer(
            uniform_session, sample_entities, attr, Answer.YES
        )
        assert len(uniform_session.history) == 1
        assert uniform_session.history[0].answer == Answer.YES
        assert uniform_session.history[0].attribute_key == attr.key

    def test_process_answer_adds_to_asked(
        self, uniform_session: GameSession, sample_entities: list[Entity],
        sample_attributes,
    ):
        manager = GameSessionManager(
            scoring_engine=ScoringEngine(),
            question_policy=QuestionPolicy(),
        )
        attr = sample_attributes[0]
        manager.process_answer(
            uniform_session, sample_entities, attr, Answer.YES
        )
        assert attr.id in uniform_session.asked_attributes
