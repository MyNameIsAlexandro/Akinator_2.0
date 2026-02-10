#!/usr/bin/env python3
"""Migration script to expand attributes from 62 to 80+ for better differentiation.

This adds:
- Genre-specific attributes (action, comedy, drama, horror, scifi)
- Achievement attributes (won_oscar, won_grammy, won_nobel, olympic_medalist)
- Appearance attributes (is_bald, has_glasses, has_tattoos, distinctive_hair)
- Fame attributes (cultural_icon, controversial, billionaire, died_young)
- Era refinements (born_before_1950, born_1950_1970, born_1970_1990, born_after_1990)

Run: python migrate_to_80_attrs.py
"""

import asyncio
import os
import shutil
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from akinator.db.repository import Repository

# New attributes to add (key, question_ru, question_en, category)
NEW_ATTRIBUTES = [
    # Genre-specific (5)
    ("from_action_genre", "Связан с жанром экшн/боевик?", "Related to action genre?", "genre"),
    ("from_comedy_genre", "Связан с комедией?", "Related to comedy genre?", "genre"),
    ("from_drama_genre", "Связан с драмой?", "Related to drama genre?", "genre"),
    ("from_horror_genre", "Связан с ужасами?", "Related to horror genre?", "genre"),
    ("from_scifi_genre", "Связан с фантастикой?", "Related to sci-fi genre?", "genre"),

    # Achievements (6)
    ("won_oscar", "Получил Оскар?", "Won Oscar?", "achievement"),
    ("won_grammy", "Получил Грэмми?", "Won Grammy?", "achievement"),
    ("won_nobel", "Получил Нобелевскую премию?", "Won Nobel Prize?", "achievement"),
    ("olympic_medalist", "Олимпийский медалист?", "Olympic medalist?", "achievement"),
    ("world_champion", "Чемпион мира?", "World champion?", "achievement"),
    ("hall_of_fame", "В Зале славы?", "In Hall of Fame?", "achievement"),

    # Appearance (6)
    ("is_bald", "Лысый?", "Is bald?", "appearance"),
    ("has_glasses", "Носит очки?", "Wears glasses?", "appearance"),
    ("has_tattoos", "Есть татуировки?", "Has tattoos?", "appearance"),
    ("distinctive_hair", "Особенная прическа/цвет волос?", "Distinctive hair?", "appearance"),
    ("has_distinctive_voice", "Особый узнаваемый голос?", "Distinctive voice?", "appearance"),
    ("known_for_physique", "Известен телосложением?", "Known for physique?", "appearance"),

    # Fame/Notoriety (5)
    ("cultural_icon", "Культурная икона?", "Cultural icon?", "fame"),
    ("controversial", "Скандальная личность?", "Controversial?", "fame"),
    ("billionaire", "Миллиардер?", "Billionaire?", "fame"),
    ("died_young", "Умер молодым (до 50)?", "Died young?", "fame"),
    ("active_now", "Активен в наши дни?", "Active now?", "fame"),
]

# Mapping of new attributes to existing categories
CATEGORY_ATTR_UPDATES = {
    # Marvel heroes
    "marvel_hero": {
        "from_action_genre": 0.9, "from_scifi_genre": 0.4, "cultural_icon": 0.6,
        "known_for_physique": 0.6, "active_now": 1.0,
    },
    "marvel_villain": {
        "from_action_genre": 0.8, "from_scifi_genre": 0.3, "controversial": 0.3,
        "active_now": 0.8,
    },
    # DC heroes
    "dc_hero": {
        "from_action_genre": 0.9, "from_scifi_genre": 0.3, "cultural_icon": 0.7,
        "known_for_physique": 0.5, "active_now": 1.0,
    },
    "dc_villain": {
        "from_action_genre": 0.7, "from_drama_genre": 0.3, "controversial": 0.4,
        "active_now": 0.8,
    },
    # Star Wars
    "star_wars_light": {
        "from_scifi_genre": 1.0, "from_action_genre": 0.7, "cultural_icon": 0.5,
    },
    "star_wars_dark": {
        "from_scifi_genre": 1.0, "from_action_genre": 0.8, "cultural_icon": 0.4,
    },
    # Harry Potter
    "harry_potter_good": {
        "from_scifi_genre": 0.7, "cultural_icon": 0.6, "active_now": 0.0,
    },
    "harry_potter_evil": {
        "from_scifi_genre": 0.7, "from_horror_genre": 0.3, "active_now": 0.0,
    },
    # Disney
    "disney_princess": {
        "from_drama_genre": 0.5, "cultural_icon": 0.5, "active_now": 0.0,
    },
    "disney_animal": {
        "from_comedy_genre": 0.6, "cultural_icon": 0.4, "active_now": 0.0,
    },
    "disney_classic": {
        "from_comedy_genre": 0.6, "cultural_icon": 0.7, "active_now": 0.0,
    },
    "pixar": {
        "from_comedy_genre": 0.7, "from_scifi_genre": 0.3, "cultural_icon": 0.4,
    },
    # Anime
    "anime_shonen": {
        "from_action_genre": 0.9, "known_for_physique": 0.5, "distinctive_hair": 0.7,
        "active_now": 0.7,
    },
    "anime_popular": {
        "from_action_genre": 0.6, "cultural_icon": 0.4, "distinctive_hair": 0.6,
    },
    # Games
    "game_nintendo": {
        "from_action_genre": 0.5, "cultural_icon": 0.6, "active_now": 0.9,
    },
    "game_action": {
        "from_action_genre": 0.9, "known_for_physique": 0.5, "active_now": 0.8,
    },
    "game_classic": {
        "from_action_genre": 0.6, "cultural_icon": 0.5, "active_now": 0.7,
    },
    # Classic literature
    "literature_classic": {
        "from_drama_genre": 0.6, "cultural_icon": 0.7, "active_now": 0.0,
    },
    "literature_detective": {
        "from_drama_genre": 0.5, "cultural_icon": 0.6, "has_distinctive_voice": 0.4,
    },
    # Cartoons
    "cartoon_classic": {
        "from_comedy_genre": 0.9, "cultural_icon": 0.6, "active_now": 0.3,
    },
    "cartoon_modern": {
        "from_comedy_genre": 0.7, "from_action_genre": 0.3, "active_now": 0.8,
    },
    # TV Shows
    "tv_drama": {
        "from_drama_genre": 0.9, "controversial": 0.3, "active_now": 0.6,
    },
    "tv_sitcom": {
        "from_comedy_genre": 0.9, "active_now": 0.5,
    },
    # Real people - Hollywood
    "hollywood_actor": {
        "from_drama_genre": 0.5, "from_action_genre": 0.4, "won_oscar": 0.2,
        "cultural_icon": 0.3, "active_now": 0.7, "billionaire": 0.1,
    },
    "hollywood_actress": {
        "from_drama_genre": 0.5, "from_comedy_genre": 0.3, "won_oscar": 0.2,
        "cultural_icon": 0.3, "active_now": 0.7,
    },
    "hollywood_director": {
        "from_drama_genre": 0.4, "from_action_genre": 0.3, "won_oscar": 0.3,
        "cultural_icon": 0.3, "has_glasses": 0.4,
    },
    # Musicians
    "musician_rock": {
        "won_grammy": 0.3, "cultural_icon": 0.5, "has_tattoos": 0.4,
        "distinctive_hair": 0.4, "controversial": 0.3, "active_now": 0.5,
    },
    "musician_pop": {
        "won_grammy": 0.4, "cultural_icon": 0.5, "distinctive_hair": 0.3,
        "active_now": 0.8,
    },
    "musician_hiphop": {
        "won_grammy": 0.3, "has_tattoos": 0.6, "controversial": 0.4,
        "billionaire": 0.2, "active_now": 0.8,
    },
    "musician_classic": {
        "won_grammy": 0.1, "cultural_icon": 0.8, "has_glasses": 0.3,
        "died_young": 0.3, "active_now": 0.0,
    },
    # Athletes
    "athlete_football": {
        "world_champion": 0.2, "known_for_physique": 0.7, "has_tattoos": 0.4,
        "cultural_icon": 0.3, "billionaire": 0.1, "active_now": 0.7,
    },
    "athlete_basketball": {
        "world_champion": 0.3, "olympic_medalist": 0.2, "known_for_physique": 0.8,
        "hall_of_fame": 0.3, "billionaire": 0.2, "active_now": 0.6,
    },
    "athlete_tennis": {
        "world_champion": 0.4, "olympic_medalist": 0.2, "known_for_physique": 0.5,
        "cultural_icon": 0.3, "active_now": 0.6,
    },
    "athlete_boxing": {
        "world_champion": 0.5, "olympic_medalist": 0.2, "known_for_physique": 0.9,
        "controversial": 0.4, "cultural_icon": 0.4, "active_now": 0.4,
    },
    "athlete_olympics": {
        "olympic_medalist": 0.9, "world_champion": 0.5, "known_for_physique": 0.7,
        "cultural_icon": 0.3, "active_now": 0.5,
    },
    "athlete_f1": {
        "world_champion": 0.4, "billionaire": 0.2, "active_now": 0.6,
    },
    # Politicians
    "politician_modern": {
        "controversial": 0.5, "cultural_icon": 0.4, "has_glasses": 0.3,
        "active_now": 0.6,
    },
    "politician_historical": {
        "cultural_icon": 0.7, "controversial": 0.4, "died_young": 0.2,
        "active_now": 0.0,
    },
    # Scientists/Thinkers
    "scientist": {
        "won_nobel": 0.2, "has_glasses": 0.5, "cultural_icon": 0.3,
        "active_now": 0.3,
    },
    "philosopher": {
        "cultural_icon": 0.5, "has_glasses": 0.4, "active_now": 0.0,
    },
    # Writers
    "writer_modern": {
        "cultural_icon": 0.4, "has_glasses": 0.4, "active_now": 0.5,
    },
    "writer_classic": {
        "cultural_icon": 0.6, "active_now": 0.0, "died_young": 0.2,
    },
    # Business
    "business_tech": {
        "billionaire": 0.7, "has_glasses": 0.4, "controversial": 0.3,
        "cultural_icon": 0.4, "active_now": 0.9,
    },
    # Internet
    "youtuber": {
        "active_now": 1.0, "controversial": 0.3, "cultural_icon": 0.2,
    },
}

# Entity-specific overrides for new attributes
ENTITY_OVERRIDES = {
    # Actors with Oscars
    "Leonardo DiCaprio": {"won_oscar": 1.0, "cultural_icon": 0.8},
    "Tom Hanks": {"won_oscar": 1.0, "cultural_icon": 0.9},
    "Meryl Streep": {"won_oscar": 1.0, "cultural_icon": 0.8},
    "Denzel Washington": {"won_oscar": 1.0},
    "Morgan Freeman": {"won_oscar": 1.0, "has_distinctive_voice": 0.9},

    # Bald actors
    "Dwayne Johnson": {"is_bald": 1.0, "known_for_physique": 1.0, "from_action_genre": 0.9},
    "Vin Diesel": {"is_bald": 1.0, "known_for_physique": 0.8, "from_action_genre": 0.9},
    "Jason Statham": {"is_bald": 0.8, "known_for_physique": 0.9, "from_action_genre": 1.0},
    "Bruce Willis": {"is_bald": 1.0, "from_action_genre": 0.9},
    "Samuel L. Jackson": {"is_bald": 0.9, "has_distinctive_voice": 0.8},

    # Distinctive voices
    "James Earl Jones": {"has_distinctive_voice": 1.0},
    "Arnold Schwarzenegger": {"has_distinctive_voice": 0.8, "known_for_physique": 1.0, "from_action_genre": 1.0},

    # Musicians with Grammys
    "Beyoncé": {"won_grammy": 1.0, "cultural_icon": 0.9},
    "Taylor Swift": {"won_grammy": 1.0, "cultural_icon": 0.8},
    "Eminem": {"won_grammy": 1.0, "controversial": 0.6},

    # Died young
    "Kurt Cobain": {"died_young": 1.0, "cultural_icon": 0.8},
    "Freddie Mercury": {"died_young": 0.9, "cultural_icon": 1.0, "has_distinctive_voice": 1.0},
    "Elvis Presley": {"died_young": 0.7, "cultural_icon": 1.0},
    "Marilyn Monroe": {"died_young": 1.0, "cultural_icon": 1.0},
    "James Dean": {"died_young": 1.0, "cultural_icon": 0.8},
    "Heath Ledger": {"died_young": 1.0, "won_oscar": 1.0},

    # Nobel Prize
    "Albert Einstein": {"won_nobel": 1.0, "cultural_icon": 1.0, "distinctive_hair": 0.9},
    "Marie Curie": {"won_nobel": 1.0, "cultural_icon": 0.7},

    # Olympic medalists
    "Michael Phelps": {"olympic_medalist": 1.0, "world_champion": 1.0, "known_for_physique": 0.8},
    "Usain Bolt": {"olympic_medalist": 1.0, "world_champion": 1.0, "cultural_icon": 0.7},
    "Simone Biles": {"olympic_medalist": 1.0, "world_champion": 1.0},

    # World Champions (Football)
    "Lionel Messi": {"world_champion": 1.0, "cultural_icon": 0.9},
    "Diego Maradona": {"world_champion": 1.0, "cultural_icon": 0.9, "controversial": 0.7, "died_young": 0.0},
    "Pelé": {"world_champion": 1.0, "cultural_icon": 1.0},

    # Billionaires
    "Elon Musk": {"billionaire": 1.0, "controversial": 0.7, "cultural_icon": 0.6},
    "Bill Gates": {"billionaire": 1.0, "has_glasses": 0.9, "cultural_icon": 0.6},
    "Jeff Bezos": {"billionaire": 1.0, "is_bald": 0.9},
    "Mark Zuckerberg": {"billionaire": 1.0},

    # Controversial
    "Kanye West": {"controversial": 0.9, "won_grammy": 1.0, "billionaire": 0.8},
    "Donald Trump": {"controversial": 0.9, "billionaire": 0.8, "distinctive_hair": 0.9},

    # Distinctive hair
    "Bob Marley": {"distinctive_hair": 1.0, "cultural_icon": 0.9},
    "David Bowie": {"distinctive_hair": 0.8, "cultural_icon": 0.9},

    # Tattoos
    "Post Malone": {"has_tattoos": 1.0, "distinctive_hair": 0.7},
    "Lil Wayne": {"has_tattoos": 1.0},

    # Fictional - distinctive features
    "Darth Vader": {"has_distinctive_voice": 1.0, "cultural_icon": 0.9},
    "Joker": {"distinctive_hair": 0.8, "cultural_icon": 0.8, "from_drama_genre": 0.6},
    "Hulk": {"known_for_physique": 1.0, "distinctive_hair": 0.0},
    "Wolverine": {"known_for_physique": 0.8, "distinctive_hair": 0.8},
    "Goku": {"distinctive_hair": 1.0, "known_for_physique": 0.8},
    "Naruto": {"distinctive_hair": 0.9},
    "Pikachu": {"distinctive_hair": 0.0, "cultural_icon": 0.9},
}


async def migrate():
    """Run the migration."""
    db_path = "akinator/data/akinator.db"
    backup_path = f"data/akinator_62_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

    print(f"Backing up to {backup_path}...")
    os.makedirs("data", exist_ok=True)
    shutil.copy2(db_path, backup_path)

    print("Connecting to database...")
    repo = Repository(db_path)
    await repo.init_db()

    # Get existing attributes
    existing_attrs = await repo.get_all_attributes()
    existing_keys = {a.key for a in existing_attrs}
    print(f"Existing attributes: {len(existing_keys)}")

    # Add new attributes
    new_count = 0
    for key, q_ru, q_en, cat in NEW_ATTRIBUTES:
        if key not in existing_keys:
            await repo.add_attribute(key, q_ru, q_en, cat)
            new_count += 1
            print(f"  Added: {key}")

    print(f"Added {new_count} new attributes")

    # Get all attributes (including new ones)
    all_attrs = await repo.get_all_attributes()
    attr_map = {a.key: a.id for a in all_attrs}
    print(f"Total attributes: {len(attr_map)}")

    # Get all entities
    entities = await repo.get_all_entities()
    print(f"Updating {len(entities)} entities...")

    # Import category mapping
    from entity_to_category_map import ENTITY_CATEGORY_MAP

    updated = 0
    for entity in entities:
        # Get category
        category = ENTITY_CATEGORY_MAP.get(entity.name, "")
        if not category:
            continue

        # Get category updates
        cat_updates = CATEGORY_ATTR_UPDATES.get(category, {})

        # Get entity-specific overrides
        entity_updates = ENTITY_OVERRIDES.get(entity.name, {})

        # Merge updates (entity overrides take precedence)
        updates = {**cat_updates, **entity_updates}

        if updates:
            for key, value in updates.items():
                if key in attr_map:
                    await repo.set_entity_attribute(entity.id, attr_map[key], value)

            updated += 1
            if updated % 20 == 0:
                print(f"  Updated {updated} entities...")

    print(f"Updated {updated} entities with new attributes")

    await repo.close()
    print("\nMigration complete!")
    print(f"Run 'pytest tests/test_simulation.py -v -s' to verify accuracy")


if __name__ == "__main__":
    asyncio.run(migrate())
