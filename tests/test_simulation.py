"""Simulation test: 1000 random games, measure guess accuracy.

Run:
    python -m pytest tests/test_simulation.py -v -s
    python tests/test_simulation.py          # standalone with detailed output
"""

from __future__ import annotations

import asyncio
import os
import random
import sys
import time

# Allow running standalone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from akinator.db.models import Answer, Attribute, Entity
from akinator.db.repository import Repository
from akinator.engine.scoring import ScoringEngine
from akinator.engine.session import GameSessionManager
from akinator.engine.question_policy import QuestionPolicy

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "akinator.db")
NUM_GAMES = 100
SEED = 42


def answer_from_value(value: float) -> Answer:
    """Simulate a human answer based on the entity's actual attribute value.

    In a real game the user KNOWS the answer even when our database has 0.5
    (unknown).  For most specific attributes (from_anime, from_game, etc.)
    the answer is NO because the attribute simply doesn't apply.  We default
    unknown values to NO to simulate a realistic, knowledgeable user.
    """
    if value >= 0.8:
        return Answer.YES
    if value >= 0.6:
        return Answer.PROBABLY_YES
    if value <= 0.2:
        return Answer.NO
    if value <= 0.4:
        return Answer.PROBABLY_NO
    # value ~0.5 (unknown in DB) — user would still know; default to NO
    # because most specific attributes don't apply to most entities.
    return Answer.NO


def _coverage_scores(entities: list[Entity]) -> list[float]:
    """Return per-entity scores proportional to attribute coverage.

    Entities with more non-0.5 attributes are better known and should
    start with higher prior probability.
    """
    scores = []
    for e in entities:
        n = sum(1 for v in e.attributes.values() if abs(v - 0.5) > 0.1)
        scores.append(max(1.0, float(n)))
    return scores


def simulate_game(
    target: Entity,
    all_entities: list[Entity],
    attributes: list[Attribute],
) -> dict:
    """Simulate one full game. Returns result dict."""
    scoring = ScoringEngine()
    policy = QuestionPolicy()
    manager = GameSessionManager(scoring, policy)

    session = manager.create_session(user_id=0)
    # Use coverage-based priors instead of uniform weights
    scores = _coverage_scores(all_entities)
    manager.init_candidates(session, [e.id for e in all_entities], scores=scores)

    attr_by_key = {a.key: a for a in attributes}
    questions_asked = []

    for _ in range(20):
        best_key = policy.select(session, all_entities, attributes)
        if best_key is None:
            break

        attr = attr_by_key[best_key]
        value = target.attributes.get(best_key, 0.5)
        answer = answer_from_value(value)

        manager.process_answer(session, all_entities, attr, answer)
        questions_asked.append((best_key, answer.value, value))

        if manager.should_guess(session):
            break

    # Check guess
    guess_id = manager.get_guess_candidate(session)
    correct = guess_id == target.id

    # Check second guess
    if not correct:
        second = manager.handle_guess_response(session, correct=False)
        if second is not None:
            correct = second == target.id

    return {
        "target_id": target.id,
        "target_name": target.name,
        "correct": correct,
        "questions": len(questions_asked),
        "question_keys": [q[0] for q in questions_asked],
        "remaining_candidates": len(session.candidate_ids),
        "max_weight": max(session.weights) if session.weights else 0.0,
    }


async def load_data() -> tuple[list[Entity], list[Attribute]]:
    """Load entities and attributes from the database."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    repo = Repository(DB_PATH)
    await repo.init_db()

    entities = await repo.get_all_entities()
    attributes = await repo.get_all_attributes()
    all_attrs = await repo.get_all_entity_attributes()

    for entity in entities:
        if entity.id in all_attrs:
            entity.attributes = all_attrs[entity.id]

    await repo.close()
    return entities, attributes


def run_simulation(
    entities: list[Entity],
    attributes: list[Attribute],
    num_games: int = NUM_GAMES,
    seed: int = SEED,
    verbose: bool = False,
) -> dict:
    """Run N simulated games and return statistics."""
    rng = random.Random(seed)

    # Filter entities that have at least 3 non-0.5 attributes
    viable = [e for e in entities if sum(1 for v in e.attributes.values() if abs(v - 0.5) > 0.1) >= 3]

    if len(viable) < num_games:
        targets = rng.choices(viable, k=num_games)
    else:
        targets = rng.sample(viable, k=num_games)

    correct = 0
    total_questions = 0
    failures = []
    t0 = time.time()

    for i, target in enumerate(targets):
        result = simulate_game(target, entities, attributes)
        if result["correct"]:
            correct += 1
        else:
            failures.append(result)
        total_questions += result["questions"]

        if verbose and (i + 1) % 10 == 0:
            pct = correct / (i + 1) * 100
            elapsed = time.time() - t0
            per_game = elapsed / (i + 1)
            print(f"  [{i+1}/{num_games}] accuracy={pct:.1f}% avg_q={total_questions/(i+1):.1f} ({per_game:.1f}s/game)")

    accuracy = correct / num_games * 100
    avg_questions = total_questions / num_games

    return {
        "num_games": num_games,
        "correct": correct,
        "accuracy": accuracy,
        "avg_questions": avg_questions,
        "failures": failures[:20],  # first 20 failures for inspection
        "total_entities": len(entities),
        "viable_entities": len(viable),
    }


# -- Pytest entry point --

def test_simulation_accuracy():
    """Simulation: 100 games should achieve >=99% accuracy."""
    entities, attributes = asyncio.run(load_data())
    assert len(entities) > 100, f"Too few entities: {len(entities)}"

    stats = run_simulation(entities, attributes, verbose=True)

    print(f"\n{'='*60}")
    print(f"SIMULATION RESULTS")
    print(f"{'='*60}")
    print(f"Total entities in DB: {stats['total_entities']}")
    print(f"Viable entities (>=3 attrs): {stats['viable_entities']}")
    print(f"Games played: {stats['num_games']}")
    print(f"Correct guesses: {stats['correct']}")
    print(f"Accuracy: {stats['accuracy']:.1f}%")
    print(f"Avg questions per game: {stats['avg_questions']:.1f}")

    if stats["failures"]:
        print(f"\nFirst 10 failures:")
        for f in stats["failures"][:10]:
            print(f"  {f['target_name']} -- {f['questions']}q, remaining={f['remaining_candidates']}, max_w={f['max_weight']:.4f}, asked: {f['question_keys'][:5]}...")

    assert stats["accuracy"] >= 99.0, (
        f"Accuracy {stats['accuracy']:.1f}% < 99%. "
        f"{len(stats['failures'])} failures out of {stats['num_games']} games."
    )


# -- Standalone runner --

if __name__ == "__main__":
    entities, attributes = asyncio.run(load_data())
    print(f"Loaded {len(entities)} entities, {len(attributes)} attributes")

    stats = run_simulation(entities, attributes, verbose=True)

    print(f"\n{'='*60}")
    print(f"SIMULATION RESULTS")
    print(f"{'='*60}")
    print(f"Total entities in DB: {stats['total_entities']}")
    print(f"Viable entities (>=3 attrs): {stats['viable_entities']}")
    print(f"Games played: {stats['num_games']}")
    print(f"Correct guesses: {stats['correct']}")
    print(f"Accuracy: {stats['accuracy']:.1f}%")
    print(f"Avg questions per game: {stats['avg_questions']:.1f}")

    if stats["failures"]:
        print(f"\nFirst 20 failures:")
        for f in stats["failures"]:
            print(f"  {f['target_name']} -- {f['questions']}q, remaining={f['remaining_candidates']}, max_w={f['max_weight']:.4f}, asked: {f['question_keys'][:8]}")
