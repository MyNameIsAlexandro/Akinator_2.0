"""Akinator 2.0 — Telegram Bot entry point."""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import sys

from aiogram import Bot, Dispatcher

from akinator.bot.handlers import router, set_game_data, set_repository
from akinator.db.repository import Repository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("akinator")

DB_PATH = os.environ.get("AKINATOR_DB_PATH", "data/akinator.db")
# Pre-built database shipped with the repo (backup)
BUNDLED_DB = os.path.join(os.path.dirname(__file__), "data", "akinator.db")


async def load_game_data(repo: Repository) -> None:
    """Load entities with attributes into memory for the game engine."""
    entities = await repo.get_all_entities()
    attributes = await repo.get_all_attributes()

    # Batch-load all entity attributes in one query
    all_attrs = await repo.get_all_entity_attributes()
    for entity in entities:
        if entity.id in all_attrs:
            entity.attributes = all_attrs[entity.id]

    await set_game_data(entities, attributes, repo)
    logger.info("Loaded %d entities, %d attributes", len(entities), len(attributes))


def _ensure_database() -> None:
    """Always copy bundled DB from repo to ensure latest data."""
    logger.info("DB_PATH: %s", DB_PATH)
    logger.info("BUNDLED_DB: %s", BUNDLED_DB)
    logger.info("BUNDLED_DB exists: %s", os.path.exists(BUNDLED_DB))

    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    if os.path.exists(BUNDLED_DB):
        # Get bundled DB info before copy
        import sqlite3
        with sqlite3.connect(BUNDLED_DB) as conn:
            attr_count = conn.execute("SELECT COUNT(*) FROM attributes").fetchone()[0]
            entity_count = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        logger.info("Bundled DB: %d entities, %d attributes", entity_count, attr_count)

        shutil.copy2(BUNDLED_DB, DB_PATH)
        logger.info("Copied bundled database to %s", DB_PATH)
    else:
        logger.error("BUNDLED_DB not found at %s!", BUNDLED_DB)


async def main() -> None:
    token = os.environ.get("BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN environment variable is required")
        sys.exit(1)

    # Copy bundled DB if runtime path is empty
    _ensure_database()

    repo = Repository(DB_PATH)
    await repo.init_db()

    entity_count = len(await repo.get_all_entities())
    if entity_count == 0:
        logger.warning(
            "Database is empty! Run: python -m akinator.generate_db to populate."
        )
    else:
        await load_game_data(repo)

    # Keep repo open for runtime learning
    set_repository(repo)

    # Start bot
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Starting Akinator 2.0 bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
