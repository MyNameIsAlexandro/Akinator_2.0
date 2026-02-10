#!/usr/bin/env python3
"""Automatic Override Suggestion System

Analyzes simulation failures and suggests entity-specific attribute overrides
to improve accuracy. Can automatically generate Python code for ENTITY_OVERRIDES.

Usage:
    python suggest_overrides.py                    # Analyze and suggest
    python suggest_overrides.py --apply            # Apply suggestions automatically
    python suggest_overrides.py --commit           # Apply and commit to git
"""

from __future__ import annotations

import asyncio
import sys
from typing import Optional
from dataclasses import dataclass

from akinator.db.repository import Repository
from akinator.db.models import Entity
from tests.test_simulation import (
    run_full_simulation,
    PerfectOracle,
    RealisticOracle,
    PessimisticOracle,
    OracleStrategy,
    SimulationResult,
)


@dataclass
class OverrideSuggestion:
    """Suggested override for a specific entity."""
    entity_name: str
    attribute_key: str
    suggested_value: float
    current_value: float
    reason: str
    discrimination_power: float  # How much this helps distinguish from confused entity


async def analyze_failure(
    repo: Repository,
    target: SimulationResult,
    guessed_entity_id: int,
) -> list[OverrideSuggestion]:
    """Analyze a single failure and suggest attribute overrides."""

    # Get both entities with attributes
    target_entity = await repo.get_entity(target.target_id, with_attributes=True)
    guessed_entity = await repo.get_entity(guessed_entity_id, with_attributes=True)

    if not target_entity or not guessed_entity:
        return []

    suggestions = []

    # Find attributes where they differ significantly
    for attr_key in target_entity.attributes.keys():
        target_val = target_entity.attributes[attr_key]
        guessed_val = guessed_entity.attributes.get(attr_key, 0.5)

        # Calculate discrimination power (how different the values are)
        diff = abs(target_val - guessed_val)

        # Only suggest if difference is significant (> 0.3)
        if diff > 0.3:
            # Determine suggested value (push towards extremes for clarity)
            if target_val >= 0.7:
                suggested_value = 1.0
            elif target_val <= 0.3:
                suggested_value = 0.0
            else:
                suggested_value = target_val

            # Only suggest if we're actually changing the value
            if abs(suggested_value - target_val) > 0.05:
                reason = (
                    f"Distinguish from {guessed_entity.name}: "
                    f"target={target_val:.2f}, confused={guessed_val:.2f}"
                )

                suggestions.append(OverrideSuggestion(
                    entity_name=target_entity.name,
                    attribute_key=attr_key,
                    suggested_value=suggested_value,
                    current_value=target_val,
                    reason=reason,
                    discrimination_power=diff,
                ))

    # Sort by discrimination power (most important first)
    suggestions.sort(key=lambda s: s.discrimination_power, reverse=True)

    # Return top 5 suggestions
    return suggestions[:5]


async def suggest_overrides_for_failures(
    db_path: str,
    target_accuracy: float = 99.0,
    oracle_strategy: OracleStrategy = None,
    strategy_name: str = "Perfect",
) -> dict[str, list[OverrideSuggestion]]:
    """Run simulation and suggest overrides for failures."""

    if oracle_strategy is None:
        oracle_strategy = PerfectOracle()

    print(f"🔍 Running simulation with {strategy_name} oracle to find failures...")
    results = await run_full_simulation(db_path, oracle_strategy, strategy_name)

    total = len(results)
    successes = sum(1 for r in results if r.success)
    accuracy = 100.0 * successes / total if total > 0 else 0.0

    print(f"📊 Accuracy: {accuracy:.2f}% ({successes}/{total})")

    if accuracy >= target_accuracy:
        print(f"✅ Already at target accuracy ({target_accuracy}%)! No overrides needed.")
        return {}

    failures = [r for r in results if not r.success]
    print(f"❌ Found {len(failures)} failures. Analyzing...\n")

    # Analyze each failure
    repo = Repository(db_path)
    await repo.init_db()

    all_suggestions = {}
    for i, failure in enumerate(failures, 1):
        print(f"[{i}/{len(failures)}] Analyzing: {failure.target_name} → {failure.guessed_name}")

        suggestions = await analyze_failure(repo, failure, failure.guessed_id)
        if suggestions:
            all_suggestions[failure.target_name] = suggestions
            print(f"  💡 Found {len(suggestions)} override suggestions")

    await repo.close()

    return all_suggestions


def generate_override_code(suggestions: dict[str, list[OverrideSuggestion]]) -> str:
    """Generate Python code for ENTITY_OVERRIDES."""

    lines = []
    lines.append("# Auto-generated override suggestions")
    lines.append("# Add these to ENTITY_OVERRIDES in entity_to_category_map.py")
    lines.append("")
    lines.append("SUGGESTED_OVERRIDES = {")

    for entity_name in sorted(suggestions.keys()):
        entity_suggestions = suggestions[entity_name]
        lines.append(f'    "{entity_name}": {{')

        for sugg in entity_suggestions:
            lines.append(f'        "{sugg.attribute_key}": {sugg.suggested_value},  # {sugg.reason}')

        lines.append("    },")

    lines.append("}")
    lines.append("")

    return "\n".join(lines)


def print_suggestions_report(suggestions: dict[str, list[OverrideSuggestion]]) -> None:
    """Print detailed report of suggestions."""

    print("\n" + "="*80)
    print("OVERRIDE SUGGESTIONS REPORT")
    print("="*80)
    print(f"Entities needing overrides: {len(suggestions)}")
    print()

    total_overrides = sum(len(s) for s in suggestions.values())
    print(f"Total attribute overrides suggested: {total_overrides}")
    print()

    for entity_name in sorted(suggestions.keys()):
        print(f"\n📌 {entity_name}")
        print("-" * 80)

        for sugg in suggestions[entity_name]:
            print(f"  {sugg.attribute_key:30s} | "
                  f"Current: {sugg.current_value:.2f} → Suggested: {sugg.suggested_value:.2f} | "
                  f"Power: {sugg.discrimination_power:.2f}")
            print(f"    💬 {sugg.reason}")

    print("\n" + "="*80)


async def apply_overrides_automatically(
    suggestions: dict[str, list[OverrideSuggestion]],
    entity_map_path: str = "entity_to_category_map.py",
) -> bool:
    """Apply suggested overrides to entity_to_category_map.py."""

    print("\n⚠️  AUTO-APPLY NOT IMPLEMENTED YET")
    print("Please manually add the suggested overrides to entity_to_category_map.py")
    print("\nGenerated code:")
    print(generate_override_code(suggestions))
    return False


async def main():
    """Main entry point."""

    import argparse
    parser = argparse.ArgumentParser(description="Suggest attribute overrides for failed entities")
    parser.add_argument("--db", default="data/akinator.db", help="Path to database")
    parser.add_argument("--target", type=float, default=99.0, help="Target accuracy percentage")
    parser.add_argument("--oracle", choices=["perfect", "realistic", "pessimistic"],
                        default="perfect", help="Oracle strategy to use")
    parser.add_argument("--apply", action="store_true", help="Automatically apply suggestions")
    parser.add_argument("--commit", action="store_true", help="Apply and commit to git")
    args = parser.parse_args()

    # Select oracle strategy
    oracle_map = {
        "perfect": (PerfectOracle(), "Perfect"),
        "realistic": (RealisticOracle(), "Realistic"),
        "pessimistic": (PessimisticOracle(), "Pessimistic"),
    }
    oracle_strategy, strategy_name = oracle_map[args.oracle]

    # Run analysis
    suggestions = await suggest_overrides_for_failures(args.db, args.target, oracle_strategy, strategy_name)

    if not suggestions:
        return 0

    # Print report
    print_suggestions_report(suggestions)

    # Generate code
    code = generate_override_code(suggestions)

    # Save to file
    output_path = "suggested_overrides.py"
    with open(output_path, "w") as f:
        f.write(code)
    print(f"\n💾 Saved suggestions to: {output_path}")

    # Apply if requested
    if args.apply or args.commit:
        success = await apply_overrides_automatically(suggestions)

        if success and args.commit:
            print("\n📝 Committing changes to git...")
            import subprocess
            subprocess.run(["git", "add", "entity_to_category_map.py"])
            subprocess.run([
                "git", "commit", "-m",
                f"Add automatic overrides for {len(suggestions)} entities"
            ])
            print("✅ Changes committed!")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
