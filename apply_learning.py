#!/usr/bin/env python3
"""Apply Learning from User Feedback

This script analyzes accumulated user feedback and updates entity attributes
to better match real user answers. Run periodically (e.g., daily) to improve
accuracy based on actual gameplay data.

Usage:
    python apply_learning.py                    # Apply learning to main DB
    python apply_learning.py --db path.db       # Custom DB path
    python apply_learning.py --min-feedback 5   # Require more samples
    python apply_learning.py --dry-run          # Preview changes without applying
"""

from __future__ import annotations

import asyncio
import logging
import sys

from akinator.db.repository import Repository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("apply_learning")


async def preview_learning(repo: Repository, min_feedback: int = 3) -> None:
    """Preview what would be learned without actually updating."""
    db = await repo._conn()

    # Get entity-attribute pairs with enough feedback
    cursor = await db.execute(
        """SELECT entity_id, attribute_id, COUNT(*) as feedback_count
           FROM user_feedback
           GROUP BY entity_id, attribute_id
           HAVING feedback_count >= ?
           ORDER BY feedback_count DESC
           LIMIT 20""",
        (min_feedback,),
    )
    rows = await cursor.fetchall()

    if not rows:
        logger.info("No entity-attribute pairs with >= %d feedback samples", min_feedback)
        return

    logger.info("Top 20 entity-attribute pairs by feedback count:")
    logger.info("=" * 80)

    for entity_id, attribute_id, count in rows:
        # Get entity name
        entity = await repo.get_entity(entity_id)
        if not entity:
            continue

        # Get attribute key
        cursor2 = await db.execute("SELECT key FROM attributes WHERE id = ?", (attribute_id,))
        attr_row = await cursor2.fetchone()
        if not attr_row:
            continue
        attr_key = attr_row[0]

        # Get current value
        current = await repo.get_entity_attribute(entity_id, attribute_id)

        # Calculate proposed new value
        new_value = await repo.calculate_learned_value(entity_id, attribute_id, current)

        # Get feedback stats
        stats = await repo.get_feedback_stats(entity_id, attribute_id)

        if new_value is not None and abs(new_value - current) > 0.05:
            change = new_value - current
            logger.info(
                f"  {entity.name:30s} | {attr_key:20s} | "
                f"{current:.2f} → {new_value:.2f} ({change:+.2f}) | "
                f"Samples: {count} | {stats}"
            )


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apply learning from user feedback")
    parser.add_argument("--db", default="data/akinator.db", help="Database path")
    parser.add_argument("--min-feedback", type=int, default=3,
                       help="Minimum feedback samples required to update (default: 3)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview changes without applying them")
    args = parser.parse_args()

    repo = Repository(args.db)
    await repo.init_db()

    # Count total feedback
    db = await repo._conn()
    cursor = await db.execute("SELECT COUNT(*) FROM user_feedback")
    total_feedback = (await cursor.fetchone())[0]

    logger.info("=" * 80)
    logger.info("User Feedback Learning System")
    logger.info("=" * 80)
    logger.info("Database: %s", args.db)
    logger.info("Total feedback entries: %d", total_feedback)
    logger.info("Minimum samples required: %d", args.min_feedback)
    logger.info("Mode: %s", "DRY RUN (preview only)" if args.dry_run else "LIVE UPDATE")
    logger.info("=" * 80)
    logger.info("")

    if total_feedback == 0:
        logger.info("✅ No feedback data yet. Play some games to accumulate data!")
        await repo.close()
        return 0

    if args.dry_run:
        await preview_learning(repo, args.min_feedback)
    else:
        updated = await repo.apply_learning(args.min_feedback)
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ Learning applied successfully!")
        logger.info("Updated %d entity-attribute pairs", updated)
        logger.info("=" * 80)

        if updated == 0:
            logger.info("")
            logger.info("💡 Tip: Need more gameplay data! Current feedback: %d entries", total_feedback)
            logger.info("   Try lowering --min-feedback or wait for more games to be played.")

    await repo.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
