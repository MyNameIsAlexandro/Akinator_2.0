"""Simulation Test — measure accuracy of the Akinator system.

This test simulates a full game for every entity in the database:
- The "oracle" answers perfectly based on the target entity's attributes
- Tracks if the system guesses correctly within MAX_QUESTIONS
- Reports overall accuracy, average questions, and detailed statistics

Run with: pytest tests/test_simulation.py -v -s
"""

from __future__ import annotations

import asyncio
import os
import pytest

from akinator.config import MAX_QUESTIONS
from akinator.db.models import Answer, Entity, GameMode
from akinator.db.repository import Repository
from akinator.engine.session import GameSessionManager
from akinator.engine.scoring import ScoringEngine
from akinator.engine.question_policy import QuestionPolicy


class OracleStrategy:
    """Base class for oracle answer strategies."""

    def answer(self, attribute_key: str, entity: Entity) -> Answer:
        """Answer a question based on entity's attribute value."""
        raise NotImplementedError


class PerfectOracle(OracleStrategy):
    """Perfect oracle - always gives most informative answer."""

    def answer(self, attribute_key: str, entity: Entity) -> Answer:
        if attribute_key not in entity.attributes:
            return Answer.DONT_KNOW

        value = entity.attributes[attribute_key]

        # Convert continuous probability to discrete answer
        if value >= 0.85:
            return Answer.YES
        elif value >= 0.60:
            return Answer.PROBABLY_YES
        elif value <= 0.15:
            return Answer.NO
        elif value <= 0.40:
            return Answer.PROBABLY_NO
        else:
            return Answer.DONT_KNOW


class RealisticOracle(OracleStrategy):
    """Realistic oracle - simulates real user with some uncertainty."""

    def answer(self, attribute_key: str, entity: Entity) -> Answer:
        if attribute_key not in entity.attributes:
            return Answer.DONT_KNOW

        value = entity.attributes[attribute_key]

        # Realistic user is less certain, uses PROBABLY more often
        if value >= 0.90:
            return Answer.YES
        elif value >= 0.70:
            return Answer.PROBABLY_YES  # More uncertainty
        elif value >= 0.45:
            return Answer.DONT_KNOW  # Uncertain in middle range
        elif value >= 0.30:
            return Answer.PROBABLY_NO
        elif value >= 0.10:
            return Answer.PROBABLY_NO  # Still somewhat certain
        else:
            return Answer.NO


class PessimisticOracle(OracleStrategy):
    """Pessimistic oracle - uses DONT_KNOW very often (worst case)."""

    def answer(self, attribute_key: str, entity: Entity) -> Answer:
        if attribute_key not in entity.attributes:
            return Answer.DONT_KNOW

        value = entity.attributes[attribute_key]

        # Very conservative user, says DONT_KNOW for most things
        if value >= 0.95:
            return Answer.YES
        elif value >= 0.80:
            return Answer.PROBABLY_YES
        elif value >= 0.20:
            return Answer.DONT_KNOW  # Very uncertain!
        elif value >= 0.05:
            return Answer.PROBABLY_NO
        else:
            return Answer.NO


class SimulationOracle:
    """Oracle that uses a strategy to answer questions."""

    def __init__(self, target_entity: Entity, strategy: OracleStrategy = None):
        self.target = target_entity
        self.strategy = strategy or PerfectOracle()

    def answer_question(self, attribute_key: str) -> Answer:
        """Answer a question based on the target entity's attribute value."""
        return self.strategy.answer(attribute_key, self.target)


class SimulationResult:
    """Results from simulating one entity."""

    def __init__(
        self,
        target_id: int,
        target_name: str,
        success: bool,
        guessed_id: int | None,
        guessed_name: str | None,
        questions_asked: int,
        max_prob_at_end: float,
    ):
        self.target_id = target_id
        self.target_name = target_name
        self.success = success
        self.guessed_id = guessed_id
        self.guessed_name = guessed_name
        self.questions_asked = questions_asked
        self.max_prob_at_end = max_prob_at_end


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


async def simulate_entity(
    repo: Repository,
    manager: GameSessionManager,
    policy: QuestionPolicy,
    all_entities: list[Entity],
    all_attrs: dict[int, dict[str, float]],
    target_entity: Entity,
    oracle_strategy: OracleStrategy = None,
) -> SimulationResult:
    """Simulate a full game for a single target entity."""

    # Load full attributes for target
    target_full = await repo.get_entity(target_entity.id, with_attributes=True)
    oracle = SimulationOracle(target_full, oracle_strategy)

    # Initialize session with all entities as candidates
    session = manager.create_session(user_id=1, language="en")
    candidate_ids = [e.id for e in all_entities]

    # Use coverage-based priors for better performance
    scores = _coverage_scores(all_entities)
    manager.init_candidates(session, candidate_ids, scores=scores)

    # Load all entities with attributes for scoring
    entities_with_attrs = []
    for eid in candidate_ids:
        e = Entity(
            id=eid,
            name=next(ent.name for ent in all_entities if ent.id == eid),
            description="",
            entity_type="",
            language="en",
            attributes=all_attrs.get(eid, {}),
        )
        entities_with_attrs.append(e)

    # Get all attributes
    all_attributes = await repo.get_all_attributes()

    # Play the game
    questions_asked = 0
    while session.mode == GameMode.ASKING and questions_asked < MAX_QUESTIONS:
        # Check if we should guess
        if manager.should_guess(session):
            break

        # Ask next question
        available_attrs = [a for a in all_attributes if a.id not in session.asked_attributes]
        if not available_attrs:
            break

        best_attr_key = policy.select(session, entities_with_attrs, available_attrs)
        if not best_attr_key:
            break

        # Find the attribute object
        best_attr = next(a for a in available_attrs if a.key == best_attr_key)

        # Oracle answers
        answer = oracle.answer_question(best_attr.key)

        # Update session
        manager.process_answer(session, entities_with_attrs, best_attr, answer)
        questions_asked += 1

    # Get the final guess
    guessed_id = manager.get_guess_candidate(session)
    guessed_entity = await repo.get_entity(guessed_id)

    # Check success
    success = (guessed_id == target_entity.id)

    # Get max probability
    max_prob = max(session.weights) if session.weights else 0.0

    return SimulationResult(
        target_id=target_entity.id,
        target_name=target_entity.name,
        success=success,
        guessed_id=guessed_id,
        guessed_name=guessed_entity.name if guessed_entity else None,
        questions_asked=questions_asked,
        max_prob_at_end=max_prob,
    )


async def run_full_simulation(
    db_path: str,
    oracle_strategy: OracleStrategy = None,
    strategy_name: str = "Perfect",
) -> list[SimulationResult]:
    """Run simulation for all entities in the database."""

    repo = Repository(db_path)
    await repo.init_db()

    # Load all entities and their attributes once
    all_entities = await repo.get_all_entities()
    all_attrs = await repo.get_all_entity_attributes()

    print(f"\n{'='*60}")
    print(f"Starting simulation with {len(all_entities)} entities")
    print(f"Oracle Strategy: {strategy_name}")
    print(f"{'='*60}\n")

    # Initialize game components
    scoring = ScoringEngine()
    policy = QuestionPolicy()
    manager = GameSessionManager(scoring, policy)

    # Run simulation for each entity
    results = []
    for i, target in enumerate(all_entities, 1):
        result = await simulate_entity(
            repo, manager, policy, all_entities, all_attrs, target, oracle_strategy
        )
        results.append(result)

        # Progress indicator
        if i % 10 == 0 or i == len(all_entities):
            successes = sum(1 for r in results if r.success)
            accuracy = 100.0 * successes / len(results)
            print(f"Progress: {i}/{len(all_entities)} | Accuracy: {accuracy:.1f}%")

    await repo.close()
    return results


def print_simulation_report(results: list[SimulationResult]) -> None:
    """Print detailed simulation report."""

    total = len(results)
    successes = sum(1 for r in results if r.success)
    failures = total - successes
    accuracy = 100.0 * successes / total if total > 0 else 0.0

    avg_questions = sum(r.questions_asked for r in results) / total if total > 0 else 0.0
    avg_questions_success = (
        sum(r.questions_asked for r in results if r.success) / successes
        if successes > 0 else 0.0
    )

    avg_prob_success = (
        sum(r.max_prob_at_end for r in results if r.success) / successes
        if successes > 0 else 0.0
    )
    avg_prob_failure = (
        sum(r.max_prob_at_end for r in results if not r.success) / failures
        if failures > 0 else 0.0
    )

    print(f"\n{'='*60}")
    print(f"SIMULATION RESULTS")
    print(f"{'='*60}")
    print(f"Total entities tested: {total}")
    print(f"Successful guesses:    {successes}")
    print(f"Failed guesses:        {failures}")
    print(f"Accuracy:              {accuracy:.2f}%")
    print(f"")
    print(f"Average questions asked:         {avg_questions:.2f}")
    print(f"Average questions (success):     {avg_questions_success:.2f}")
    print(f"Average max probability (success): {avg_prob_success:.3f}")
    print(f"Average max probability (failure): {avg_prob_failure:.3f}")
    print(f"{'='*60}\n")

    # Show some failures for debugging
    if failures > 0:
        print("Sample failures (showing first 10):")
        failure_cases = [r for r in results if not r.success][:10]
        for r in failure_cases:
            print(f"  Target: {r.target_name:30s} | "
                  f"Guessed: {r.guessed_name:30s} | "
                  f"Questions: {r.questions_asked:2d} | "
                  f"Prob: {r.max_prob_at_end:.3f}")
        print()


@pytest.mark.asyncio
async def test_full_simulation(tmp_path):
    """Run full simulation test with PERFECT oracle (baseline - must be 99%+)."""

    # Use the actual database (not tmp_path for this test)
    db_path = "data/akinator.db"

    results = await run_full_simulation(db_path, PerfectOracle(), "Perfect")
    print_simulation_report(results)

    # Calculate accuracy
    total = len(results)
    successes = sum(1 for r in results if r.success)
    accuracy = 100.0 * successes / total if total > 0 else 0.0

    # Report and assert
    print(f"\n🎯 Final Accuracy: {accuracy:.2f}%")
    print(f"🎯 Target: 99.00%")

    # Assert minimum accuracy requirement
    assert total > 0, "Database should contain entities"
    assert accuracy >= 99.0, f"Accuracy regression! Expected >= 99%, got {accuracy:.2f}%. Check SIMULATION_RESULTS.md for details."

    # Save results to memory for tracking
    memory_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory")
    os.makedirs(memory_dir, exist_ok=True)

    with open(os.path.join(memory_dir, "SIMULATION_RESULTS.md"), "a") as f:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n## Run: {timestamp}\n")
        f.write(f"- **Entities**: {total}\n")
        f.write(f"- **Accuracy**: {accuracy:.2f}%\n")
        f.write(f"- **Successful**: {successes}/{total}\n")
        f.write(f"- **Avg Questions**: {sum(r.questions_asked for r in results) / total:.2f}\n")
        f.write("\n")


@pytest.mark.asyncio
async def test_realistic_user_simulation(tmp_path):
    """Run simulation with REALISTIC oracle (uses uncertainty - should be >= 95%)."""

    db_path = "data/akinator.db"

    results = await run_full_simulation(db_path, RealisticOracle(), "Realistic")
    print_simulation_report(results)

    # Calculate accuracy
    total = len(results)
    successes = sum(1 for r in results if r.success)
    accuracy = 100.0 * successes / total if total > 0 else 0.0

    print(f"\n🎯 Realistic User Accuracy: {accuracy:.2f}%")
    print(f"🎯 Target: >= 95.00% (allows some degradation)")

    assert total > 0, "Database should contain entities"
    assert accuracy >= 95.0, f"Realistic user accuracy too low! Expected >= 95%, got {accuracy:.2f}%"


if __name__ == "__main__":
    # Allow running directly for quick testing
    print("Running all oracle strategies...\n")

    print("=" * 60)
    print("PERFECT ORACLE (Baseline)")
    print("=" * 60)
    results = asyncio.run(run_full_simulation("data/akinator.db", PerfectOracle(), "Perfect"))
    print_simulation_report(results)

    print("\n" + "=" * 60)
    print("REALISTIC ORACLE (Real User Behavior)")
    print("=" * 60)
    results = asyncio.run(run_full_simulation("data/akinator.db", RealisticOracle(), "Realistic"))
    print_simulation_report(results)
