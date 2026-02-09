"""Generate the Akinator SQLite database from categorized entity data.

Usage:
    python -m akinator.generate_db            # Generate data/akinator.db
    python -m akinator.generate_db --output path/to/db
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

from akinator.data.categories import TEMPLATES
from akinator.db.repository import Repository

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_db")

# ── Attributes (same 32 as original seed.py) ──
ATTRIBUTES = [
    ("is_fictional", "Этот персонаж вымышленный?", "Is this character fictional?", "identity"),
    ("is_male", "Это мужчина/мужской персонаж?", "Is this a male character?", "identity"),
    ("is_human", "Это человек (или человекоподобный)?", "Is this a human (or humanoid)?", "identity"),
    ("is_alive", "Этот персонаж/человек жив?", "Is this character/person alive?", "identity"),
    ("is_adult", "Это взрослый персонаж?", "Is this an adult character?", "identity"),
    ("is_villain", "Это злодей/антигерой?", "Is this a villain/antagonist?", "identity"),
    ("from_movie", "Связан с кино?", "Related to movies?", "media"),
    ("from_tv_series", "Связан с сериалами?", "Related to TV series?", "media"),
    ("from_anime", "Связан с аниме/мангой?", "Related to anime/manga?", "media"),
    ("from_game", "Связан с видеоиграми?", "Related to video games?", "media"),
    ("from_book", "Связан с книгами/литературой?", "Related to books/literature?", "media"),
    ("from_comics", "Связан с комиксами?", "Related to comics?", "media"),
    ("from_music", "Связан с музыкой?", "Related to music?", "media"),
    ("from_sport", "Связан со спортом?", "Related to sports?", "media"),
    ("from_politics", "Связан с политикой?", "Related to politics?", "media"),
    ("from_science", "Связан с наукой?", "Related to science?", "media"),
    ("from_history", "Историческая личность/персонаж?", "Historical figure/character?", "media"),
    ("from_usa", "Связан с США?", "Related to USA?", "geography"),
    ("from_europe", "Связан с Европой?", "Related to Europe?", "geography"),
    ("from_russia", "Связан с Россией?", "Related to Russia?", "geography"),
    ("from_asia", "Связан с Азией?", "Related to Asia?", "geography"),
    ("from_japan", "Связан с Японией?", "Related to Japan?", "geography"),
    ("era_ancient", "Из древности (до 500 н.э.)?", "From ancient times (before 500 AD)?", "era"),
    ("era_medieval", "Из средневековья (500-1500)?", "From medieval era (500-1500)?", "era"),
    ("era_modern", "Из нового времени (1500-1900)?", "From modern era (1500-1900)?", "era"),
    ("era_20th_century", "Из 20-го века?", "From the 20th century?", "era"),
    ("era_21st_century", "Из 21-го века?", "From the 21st century?", "era"),
    ("has_superpower", "Обладает сверхспособностями?", "Has superpowers?", "traits"),
    ("wears_uniform", "Носит униформу/костюм?", "Wears a uniform/costume?", "traits"),
    ("has_famous_catchphrase", "Известен крылатой фразой?", "Known for a famous catchphrase?", "traits"),
    ("is_leader", "Является лидером/главой?", "Is a leader/head?", "traits"),
    ("is_wealthy", "Богатый/знатный?", "Wealthy/noble?", "traits"),
]


def _load_all_entities() -> list[tuple]:
    """Load entity data from all data modules."""
    all_entities = []

    try:
        from akinator.data.fictional import FICTIONAL
        all_entities.extend(FICTIONAL)
        logger.info("Loaded %d fictional characters", len(FICTIONAL))
    except ImportError:
        logger.warning("akinator.data.fictional not found, skipping")

    try:
        from akinator.data.real_people import REAL_PEOPLE
        all_entities.extend(REAL_PEOPLE)
        logger.info("Loaded %d real people", len(REAL_PEOPLE))
    except ImportError:
        logger.warning("akinator.data.real_people not found, skipping")

    return all_entities


def _resolve_attrs(category: str, overrides: dict[str, float] | None) -> dict[str, float]:
    """Merge category template with entity-specific overrides."""
    template = TEMPLATES.get(category, {})
    attrs = dict(template)
    if overrides:
        attrs.update(overrides)
    return attrs


def _detect_language(name: str) -> str:
    """Detect if name is Russian (Cyrillic) or English."""
    for c in name:
        if "\u0400" <= c <= "\u04ff":
            return "ru"
    return "en"


def _detect_entity_type(category: str) -> str:
    """Infer entity type from category."""
    real_categories = {
        "politician_modern", "politician_historical", "ruler_ancient", "ruler_medieval",
        "scientist", "scientist_modern", "tech_leader",
        "musician_rock", "musician_pop", "musician_hiphop", "musician_classical", "musician_russian",
        "athlete_football", "athlete_basketball", "athlete_tennis", "athlete_boxing_mma", "athlete_other",
        "actor_hollywood", "actor_russian", "director",
        "writer_western", "writer_russian",
        "visual_artist", "youtuber", "model_influencer",
    }
    return "person" if category in real_categories else "character"


async def generate(db_path: str) -> int:
    """Generate the database. Returns number of entities created."""
    # Remove old DB if exists
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info("Removed existing database: %s", db_path)

    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    repo = Repository(db_path)
    await repo.init_db()

    # Insert attributes
    attr_ids: dict[str, int] = {}
    for key, q_ru, q_en, cat in ATTRIBUTES:
        aid = await repo.add_attribute(key, q_ru, q_en, cat)
        attr_ids[key] = aid

    logger.info("Created %d attributes", len(attr_ids))

    # Load and insert entities
    raw_entities = _load_all_entities()
    logger.info("Total raw entities to process: %d", len(raw_entities))

    seen_names: set[str] = set()
    count = 0

    for entry in raw_entities:
        # Parse entry: (name, category, aliases) or (name, category, aliases, overrides)
        if len(entry) == 3:
            name, category, aliases = entry
            overrides = None
        elif len(entry) == 4:
            name, category, aliases, overrides = entry
        else:
            logger.warning("Skipping malformed entry: %s", entry[:2] if len(entry) >= 2 else entry)
            continue

        # Skip duplicates
        name_lower = name.lower()
        if name_lower in seen_names:
            continue
        seen_names.add(name_lower)

        # Validate category
        if category not in TEMPLATES:
            logger.warning("Unknown category '%s' for entity '%s', skipping", category, name)
            continue

        lang = _detect_language(name)
        etype = _detect_entity_type(category)
        attrs = _resolve_attrs(category, overrides)

        eid = await repo.add_entity(name, f"{category}", etype, lang)

        # Add aliases
        for alias in aliases:
            alias_lang = _detect_language(alias)
            await repo.add_alias(eid, alias, alias_lang)

        # Add attributes
        for attr_key, value in attrs.items():
            if attr_key in attr_ids:
                await repo.set_entity_attribute(eid, attr_ids[attr_key], value)

        count += 1
        if count % 500 == 0:
            logger.info("  ... processed %d entities", count)

    logger.info("Generated database with %d entities at %s", count, db_path)
    await repo.close()
    return count


async def main() -> None:
    db_path = "data/akinator.db"
    if len(sys.argv) > 2 and sys.argv[1] == "--output":
        db_path = sys.argv[2]

    count = await generate(db_path)
    size_mb = os.path.getsize(db_path) / (1024 * 1024)
    logger.info("Done! %d entities, database size: %.2f MB", count, size_mb)


if __name__ == "__main__":
    asyncio.run(main())
