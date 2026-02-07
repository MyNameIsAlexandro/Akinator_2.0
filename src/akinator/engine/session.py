"""Game Session Manager — orchestrates game lifecycle. (Stub — TDD.)"""

from __future__ import annotations

from akinator.db.models import Answer, Attribute, Entity, GameMode, GameSession
from akinator.engine.scoring import ScoringEngine
from akinator.engine.question_policy import QuestionPolicy


class GameSessionManager:

    def __init__(self, scoring_engine: ScoringEngine, question_policy: QuestionPolicy):
        self.scoring_engine = scoring_engine
        self.question_policy = question_policy

    def create_session(self, user_id: int, language: str = "ru") -> GameSession:
        raise NotImplementedError

    def init_candidates(
        self,
        session: GameSession,
        candidate_ids: list[int],
        scores: list[float] | None = None,
    ) -> None:
        raise NotImplementedError

    def should_guess(self, session: GameSession) -> bool:
        raise NotImplementedError

    def get_guess_candidate(self, session: GameSession) -> int:
        raise NotImplementedError

    def handle_guess_response(self, session: GameSession, correct: bool) -> int | None:
        raise NotImplementedError

    def process_answer(
        self,
        session: GameSession,
        entities: list[Entity],
        attribute: Attribute,
        answer: Answer,
    ) -> None:
        raise NotImplementedError

    def finish_learning(self, session: GameSession) -> None:
        raise NotImplementedError
