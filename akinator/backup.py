"""Database backup to GitHub repository via Contents API."""

from __future__ import annotations

import asyncio
import base64
import logging
import os
from datetime import datetime, timezone

import aiohttp

logger = logging.getLogger("akinator.backup")

GITHUB_API = "https://api.github.com"


class GitHubBackup:

    def __init__(
        self,
        token: str,
        repo: str,
        db_path: str,
        file_path: str = "akinator/data/akinator.db",
        interval_hours: float = 6.0,
        min_new_entities: int = 5,
    ):
        self.token = token
        self.repo = repo
        self.db_path = db_path
        self.file_path = file_path
        self.interval_hours = interval_hours
        self.min_new_entities = min_new_entities
        self._new_entity_count = 0
        self._task: asyncio.Task | None = None

    def notify_new_entity(self) -> None:
        """Called when a new entity is learned."""
        self._new_entity_count += 1

    async def _get_file_sha(self, session: aiohttp.ClientSession) -> str | None:
        """Get the current SHA of the file in the repo (needed for update)."""
        url = f"{GITHUB_API}/repos/{self.repo}/contents/{self.file_path}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("sha")
            return None

    async def backup_now(self) -> bool:
        """Push current DB to GitHub. Returns True on success."""
        if not os.path.exists(self.db_path):
            logger.warning("DB file not found: %s", self.db_path)
            return False

        try:
            with open(self.db_path, "rb") as f:
                content = base64.b64encode(f.read()).decode("ascii")

            async with aiohttp.ClientSession() as session:
                sha = await self._get_file_sha(session)

                url = f"{GITHUB_API}/repos/{self.repo}/contents/{self.file_path}"
                headers = {
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json",
                }
                now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                body = {
                    "message": f"Auto-backup DB ({now})",
                    "content": content,
                    "branch": "main",
                }
                if sha:
                    body["sha"] = sha

                async with session.put(url, headers=headers, json=body) as resp:
                    if resp.status in (200, 201):
                        logger.info("Backup pushed to GitHub successfully")
                        self._new_entity_count = 0
                        return True
                    else:
                        text = await resp.text()
                        logger.error("GitHub backup failed: %d %s", resp.status, text[:200])
                        return False

        except Exception:
            logger.exception("Backup to GitHub failed")
            return False

    async def _periodic_loop(self) -> None:
        """Background loop: check every interval, backup if conditions met."""
        while True:
            await asyncio.sleep(self.interval_hours * 3600)
            if self._new_entity_count >= self.min_new_entities:
                logger.info(
                    "Auto-backup triggered: %d new entities since last backup",
                    self._new_entity_count,
                )
                await self.backup_now()

    def start(self) -> None:
        """Start the periodic backup task."""
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._periodic_loop())
            logger.info(
                "Backup scheduler started: every %.1fh, min %d new entities",
                self.interval_hours, self.min_new_entities,
            )

    def stop(self) -> None:
        """Stop the periodic backup task."""
        if self._task and not self._task.done():
            self._task.cancel()
