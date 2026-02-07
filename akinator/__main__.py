"""Akinator 2.0 — Telegram Bot entry point."""

from __future__ import annotations

import asyncio
import logging
import os
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


async def load_game_data(repo: Repository) -> None:
    """Load entities with attributes into memory for the game engine."""
    entities = await repo.get_all_entities()
    attributes = await repo.get_all_attributes()

    # Batch-load all entity attributes in one query
    all_attrs = await repo.get_all_entity_attributes()
    for entity in entities:
        if entity.id in all_attrs:
            entity.attributes = all_attrs[entity.id]

    set_game_data(entities, attributes)
    logger.info("Loaded %d entities, %d attributes", len(entities), len(attributes))


async def main() -> None:
    token = os.environ.get("BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN environment variable is required")
        sys.exit(1)

    # Init database and load data
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    repo = Repository(DB_PATH)
    await repo.init_db()

    entity_count = len(await repo.get_all_entities())
    if entity_count == 0:
        logger.warning(
            "Database is empty! Run: python -m akinator.seed to populate with sample data"
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
