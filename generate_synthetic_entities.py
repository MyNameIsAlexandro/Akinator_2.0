#!/usr/bin/env python3
"""Generate synthetic entities for testing scalability.

Usage:
    python generate_synthetic_entities.py --count 1000 --db data/test_1k.db
    python generate_synthetic_entities.py --count 10000 --db data/test_10k.db
"""

from __future__ import annotations

import asyncio
import random
import sys

from akinator.db.repository import Repository
from akinator.generate_db import ATTRIBUTES

# Entity name templates
FIRST_NAMES = [
    "Alex", "Taylor", "Jordan", "Morgan", "Casey", "Riley", "Skylar", "Quinn",
    "Avery", "Parker", "Kendall", "Finley", "River", "Sage", "Phoenix", "Rowan",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
]

FICTIONAL_PREFIXES = ["Super", "Dark", "Mighty", "Swift", "Iron", "Shadow", "Golden", "Silver"]
FICTIONAL_SUFFIXES = ["Man", "Woman", "Hero", "Knight", "Warrior", "Mage", "Hunter", "Master"]

# Regions for distribution
REGIONS = ["USA", "Europe", "Russia", "Asia", "Japan", "Africa", "South America", "Middle East", "Oceania", "China"]

# Birth decades (for real people)
BIRTH_DECADES = ["1900s", "1910s", "1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s"]

# Professions
PROFESSIONS = [
    "actor", "musician", "athlete", "politician", "scientist", "writer",
    "artist", "business", "military", "fashion", "religion", "internet"
]


def generate_person_name(index: int) -> str:
    """Generate a unique person name."""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {last} #{index}"


def generate_fictional_name(index: int) -> str:
    """Generate a unique fictional character name."""
    prefix = random.choice(FICTIONAL_PREFIXES)
    suffix = random.choice(FICTIONAL_SUFFIXES)
    return f"{prefix}{suffix} #{index}"


def generate_person_attributes() -> dict[str, float]:
    """Generate realistic attributes for a person."""
    attrs = {}

    # Identity
    attrs["is_fictional"] = 0.0
    attrs["is_male"] = random.choice([0.0, 1.0])
    attrs["is_human"] = 1.0
    attrs["is_alive"] = random.choice([0.0, 1.0])
    attrs["is_adult"] = 1.0
    attrs["is_villain"] = 0.0

    # Profession (pick 1-2)
    prof = random.choice(PROFESSIONS)
    if prof == "actor":
        attrs["from_movie"] = 0.9
        attrs["from_tv_series"] = 0.5
    elif prof == "musician":
        attrs["from_music"] = 1.0
    elif prof == "athlete":
        attrs["from_sport"] = 1.0
        attrs["wears_uniform"] = 0.8
    elif prof == "politician":
        attrs["from_politics"] = 1.0
        attrs["is_leader"] = 0.7
    elif prof == "scientist":
        attrs["from_science"] = 1.0
    elif prof == "writer":
        attrs["from_literature"] = 1.0
        attrs["from_book"] = 0.8
    elif prof == "business":
        attrs["from_business"] = 1.0
        attrs["is_wealthy"] = 0.8

    # Geography (pick 1 region)
    region = random.choice(REGIONS)
    if region == "USA":
        attrs["from_usa"] = 1.0
    elif region == "Europe":
        attrs["from_europe"] = 1.0
    elif region == "Russia":
        attrs["from_russia"] = 1.0
    elif region == "Asia":
        attrs["from_asia"] = 1.0
    elif region == "Japan":
        attrs["from_japan"] = 1.0
    elif region == "Africa":
        attrs["from_africa"] = 1.0
    elif region == "South America":
        attrs["from_south_america"] = 1.0
    elif region == "Middle East":
        attrs["from_middle_east"] = 1.0
    elif region == "Oceania":
        attrs["from_oceania"] = 1.0
    elif region == "China":
        attrs["from_china"] = 1.0

    # Birth decade
    decade = random.choice(BIRTH_DECADES)
    attrs[f"born_{decade}"] = 1.0

    # Era
    if decade in ["1900s", "1910s"]:
        attrs["era_20th_century"] = 1.0
    elif decade in ["1920s", "1930s", "1940s"]:
        attrs["era_20th_century"] = 1.0
    else:
        attrs["era_20th_century"] = 1.0
        attrs["era_21st_century"] = 0.3

    # Random traits
    if random.random() < 0.3:
        attrs["is_wealthy"] = 1.0
    if random.random() < 0.2:
        attrs["has_famous_catchphrase"] = 1.0
    if random.random() < 0.3:
        attrs["has_facial_hair"] = 1.0

    return attrs


def generate_fictional_attributes() -> dict[str, float]:
    """Generate realistic attributes for a fictional character."""
    attrs = {}

    # Identity
    attrs["is_fictional"] = 1.0
    attrs["is_male"] = random.choice([0.0, 1.0])
    attrs["is_human"] = random.choice([1.0, 0.5, 0.0])
    attrs["is_alive"] = 1.0
    attrs["is_adult"] = random.choice([1.0, 0.0])
    attrs["is_villain"] = random.choice([0.0, 0.0, 0.0, 1.0])  # 25% villains

    # Media (pick 1-2)
    media_types = random.sample(
        ["movie", "tv", "anime", "game", "book", "comics"],
        k=random.randint(1, 2)
    )
    if "movie" in media_types:
        attrs["from_movie"] = 1.0
    if "tv" in media_types:
        attrs["from_tv_series"] = 1.0
    if "anime" in media_types:
        attrs["from_anime"] = 1.0
    if "game" in media_types:
        attrs["from_game"] = 1.0
    if "book" in media_types:
        attrs["from_book"] = 1.0
    if "comics" in media_types:
        attrs["from_comics"] = 1.0

    # Superpowers for some
    if random.random() < 0.4:
        attrs["has_superpower"] = 1.0

    # Traits
    if random.random() < 0.5:
        attrs["is_action_hero"] = 1.0
    if random.random() < 0.3:
        attrs["is_comedic"] = 1.0
    if random.random() < 0.2:
        attrs["is_dark_brooding"] = 1.0
    if random.random() < 0.4:
        attrs["is_child_friendly"] = 1.0

    # Visual traits
    if random.random() < 0.3:
        attrs["wears_uniform"] = 1.0
    if random.random() < 0.2:
        attrs["wears_mask"] = 1.0
    if random.random() < 0.2:
        attrs["has_armor"] = 1.0

    return attrs


async def generate_entities(db_path: str, count: int, people_ratio: float = 0.6):
    """Generate synthetic entities."""
    print(f"🔧 Generating {count} synthetic entities...")
    print(f"   {int(count * people_ratio)} people, {int(count * (1-people_ratio))} fictional")
    print()

    repo = Repository(db_path)
    await repo.init_db()

    # Create attributes if needed
    existing_attrs = await repo.get_all_attributes()
    if not existing_attrs:
        print("📝 Creating attributes...")
        for key, q_ru, q_en, cat in ATTRIBUTES:
            await repo.add_attribute(key, q_ru, q_en, cat)

    attr_list = await repo.get_all_attributes()
    attr_ids = {a.key: a.id for a in attr_list}

    # Generate entities
    people_count = int(count * people_ratio)
    fictional_count = count - people_count

    # Generate people
    print(f"👤 Generating {people_count} people...")
    for i in range(1, people_count + 1):
        name = generate_person_name(i)
        attrs = generate_person_attributes()

        eid = await repo.add_entity(name, "synthetic", "person", "en")
        for attr_key, value in attrs.items():
            if attr_key in attr_ids:
                await repo.set_entity_attribute(eid, attr_ids[attr_key], value)

        if i % 100 == 0 or i == people_count:
            print(f"  Progress: {i}/{people_count}")

    # Generate fictional characters
    print(f"🦸 Generating {fictional_count} fictional characters...")
    for i in range(1, fictional_count + 1):
        name = generate_fictional_name(i)
        attrs = generate_fictional_attributes()

        eid = await repo.add_entity(name, "synthetic", "fictional", "en")
        for attr_key, value in attrs.items():
            if attr_key in attr_ids:
                await repo.set_entity_attribute(eid, attr_ids[attr_key], value)

        if i % 100 == 0 or i == fictional_count:
            print(f"  Progress: {i}/{fictional_count}")

    await repo.close()

    import os
    size_mb = os.path.getsize(db_path) / (1024 * 1024)
    print()
    print("="*60)
    print(f"✅ Generated {count} entities")
    print(f"📊 Database: {db_path} ({size_mb:.1f} MB)")
    print("="*60)


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic entities for testing")
    parser.add_argument("--count", type=int, default=1000, help="Number of entities to generate")
    parser.add_argument("--db", default="data/synthetic_test.db", help="Database path")
    parser.add_argument("--people-ratio", type=float, default=0.6, help="Ratio of people vs fictional (0.0-1.0)")
    args = parser.parse_args()

    await generate_entities(args.db, args.count, args.people_ratio)


if __name__ == "__main__":
    asyncio.run(main())
