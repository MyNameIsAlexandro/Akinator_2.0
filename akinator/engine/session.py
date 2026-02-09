"""Game Session Manager — orchestrates game lifecycle."""

from __future__ import annotations

import uuid
from datetime import datetime

from akinator.config import GUESS_THRESHOLD, MAX_QUESTIONS, PRUNE_THRESHOLD, SECOND_GUESS_THRESHOLD
from akinator.db.models import Answer, Attribute, Entity, GameMode, GameSession, QAPair
from akinator.engine.scoring import ScoringEngine
from akinator.engine.question_policy import QuestionPolicy


class GameSessionManager:

    def __init__(self, scoring_engine: ScoringEngine, question_policy: QuestionPolicy):
        self.scoring_engine = scoring_engine
        self.question_policy = question_policy

    def create_session(self, user_id: int, language: str = "ru") -> GameSession:
        return GameSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            language=language,
            mode=GameMode.WAITING_HINT,
            created_at=datetime.now(),
        )

    def init_candidates(
        self,
        session: GameSession,
        candidate_ids: list[int],
        scores: list[float] | None = None,
    ) -> None:
        session.candidate_ids = list(candidate_ids)
        if scores is not None:
            total = sum(scores)
            session.weights = [s / total for s in scores] if total > 0 else [1.0 / len(scores)] * len(scores)
        else:
            n = len(candidate_ids)
            session.weights = [1.0 / n] * n
        session.mode = GameMode.ASKING

    def should_guess(self, session: GameSession) -> bool:
        if not session.weights:
            return False
        max_w = max(session.weights)
        if max_w >= GUESS_THRESHOLD:
            return True
        if session.question_count >= MAX_QUESTIONS:
            return True
        # Only consider early stop after enough questions have been asked
        if session.question_count >= 5:
            active = sum(1 for w in session.weights if w > PRUNE_THRESHOLD)
            if active <= 2:
                return True
        return False

    def get_guess_candidate(self, session: GameSession) -> int:
        pairs = list(zip(session.candidate_ids, session.weights))
        pairs.sort(key=lambda x: x[1], reverse=True)
        idx = min(session.guess_count, len(pairs) - 1)
        return pairs[idx][0]

    def handle_guess_response(self, session: GameSession, correct: bool) -> int | None:
        if correct:
            session.mode = GameMode.FINISHED
            return None

        session.guess_count += 1

        # Check if there's a viable second candidate
        pairs = sorted(
            zip(session.candidate_ids, session.weights),
            key=lambda x: x[1], reverse=True,
        )
        if session.guess_count < 2 and len(pairs) >= 2:
            second_w = pairs[1][1]
            if second_w >= SECOND_GUESS_THRESHOLD:
                # Keep in GUESSING for second attempt
                return pairs[1][0]

        # No more guesses — enter learning mode
        session.mode = GameMode.LEARNING
        return None

    def process_answer(
        self,
        session: GameSession,
        entities: list[Entity],
        attribute: Attribute,
        answer: Answer,
    ) -> None:
        self.scoring_engine.update(session, entities, attribute.key, answer)
        session.question_count += 1
        session.asked_attributes.append(attribute.id)
        session.history.append(QAPair(
            attribute_id=attribute.id,
            attribute_key=attribute.key,
            question_text=attribute.question_en if session.language == "en" else attribute.question_ru,
            answer=answer,
        ))

    def finish_learning(self, session: GameSession) -> None:
        session.mode = GameMode.FINISHED
