"""Akinator 2.0 — Telegram Bot entry point."""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import sys

from aiogram import Bot, Dispatcher

from akinator.backup import GitHubBackup
from akinator.bot.handlers import router, set_backup, set_game_data, set_llm_client, set_repository
from akinator.config import BACKUP_INTERVAL_HOURS, BACKUP_MIN_NEW_ENTITIES, GITHUB_REPO
from akinator.db.repository import Repository
from akinator.llm.client import LLMClient

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

    set_game_data(entities, attributes)
    logger.info("Loaded %d entities, %d attributes", len(entities), len(attributes))


def _ensure_database() -> None:
    """Copy bundled DB from repo if runtime DB doesn't exist."""
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    if os.path.exists(DB_PATH):
        size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
        logger.info("Using existing database: %s (%.1f MB)", DB_PATH, size_mb)
    elif os.path.exists(BUNDLED_DB):
        shutil.copy2(BUNDLED_DB, DB_PATH)
        size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
        logger.info("Copied bundled database to %s (%.1f MB)", DB_PATH, size_mb)


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

    # Initialize LLM client (optional — works without it)
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        llm = LLMClient(api_key=openai_key)
        set_llm_client(llm)
        logger.info("LLM client initialized (smart learning enabled)")
    else:
        logger.warning("OPENAI_API_KEY not set — smart learning disabled")

    # Initialize GitHub backup (optional)
    github_token = os.environ.get("GITHUB_TOKEN")
    backup = None
    if github_token:
        backup = GitHubBackup(
            token=github_token,
            repo=GITHUB_REPO,
            db_path=DB_PATH,
            interval_hours=BACKUP_INTERVAL_HOURS,
            min_new_entities=BACKUP_MIN_NEW_ENTITIES,
        )
        set_backup(backup)
        backup.start()
        logger.info("GitHub auto-backup enabled (repo: %s)", GITHUB_REPO)
    else:
        logger.warning("GITHUB_TOKEN not set — auto-backup disabled")

    # Start bot
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Starting Akinator 2.0 bot...")
    try:
        await dp.start_polling(bot)
    finally:
        if backup:
            backup.stop()


if __name__ == "__main__":
    asyncio.run(main())
