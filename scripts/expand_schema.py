#!/usr/bin/env python3
"""Expand attribute schema to improve differentiation.

Adds 40 new attributes for better accuracy on remaining failures.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "collected.db"

# New attributes to add (key, question_ru, question_en, category)
NEW_ATTRIBUTES = [
    # Sports positions/types
    ("is_goalkeeper", "Персонаж - вратарь?", "Is the character a goalkeeper?", "sports"),
    ("is_defender", "Персонаж - защитник?", "Is the character a defender?", "sports"),
    ("is_striker", "Персонаж - нападающий?", "Is the character a striker/forward?", "sports"),
    ("plays_tennis", "Персонаж играет в теннис?", "Does the character play tennis?", "sports"),
    ("plays_basketball", "Персонаж играет в баскетбол?", "Does the character play basketball?", "sports"),
    ("is_swimmer", "Персонаж - пловец?", "Is the character a swimmer?", "sports"),
    ("is_racer", "Персонаж - гонщик?", "Is the character a racer?", "sports"),

    # Franchises
    ("from_marvel", "Персонаж из Marvel?", "Is the character from Marvel?", "franchise"),
    ("from_dc", "Персонаж из DC?", "Is the character from DC?", "franchise"),
    ("from_disney", "Персонаж из Disney?", "Is the character from Disney?", "franchise"),
    ("from_dreamworks", "Персонаж из DreamWorks?", "Is the character from DreamWorks?", "franchise"),
    ("from_nintendo", "Персонаж из Nintendo?", "Is the character from Nintendo?", "franchise"),
    ("from_pokemon", "Персонаж из Pokemon?", "Is the character from Pokemon?", "franchise"),
    ("from_star_wars", "Персонаж из Звёздных Войн?", "Is the character from Star Wars?", "franchise"),
    ("from_lotr", "Персонаж из Властелина Колец?", "Is the character from Lord of the Rings?", "franchise"),

    # Physical traits
    ("is_blonde", "У персонажа светлые волосы?", "Does the character have blonde hair?", "appearance"),
    ("is_redhead", "У персонажа рыжие волосы?", "Does the character have red hair?", "appearance"),
    ("has_dark_hair", "У персонажа тёмные волосы?", "Does the character have dark hair?", "appearance"),
    ("is_tall", "Персонаж высокого роста?", "Is the character tall?", "appearance"),
    ("is_muscular", "Персонаж мускулистый?", "Is the character muscular?", "appearance"),

    # Roles/traits
    ("is_sidekick", "Персонаж - помощник главного героя?", "Is the character a sidekick?", "role"),
    ("is_god", "Персонаж - бог?", "Is the character a god?", "role"),
    ("is_royalty", "Персонаж - королевской крови?", "Is the character royalty?", "role"),
    ("is_animal", "Персонаж - животное?", "Is the character an animal?", "type"),
    ("is_robot", "Персонаж - робот?", "Is the character a robot?", "type"),

    # Professions
    ("is_composer", "Персонаж - композитор?", "Is the character a composer?", "profession"),
    ("is_philosopher", "Персонаж - философ?", "Is the character a philosopher?", "profession"),
    ("is_president", "Персонаж был президентом?", "Was the character a president?", "profession"),
    ("is_detective", "Персонаж - детектив?", "Is the character a detective?", "profession"),

    # Music specific
    ("is_classical", "Персонаж связан с классической музыкой?", "Is the character associated with classical music?", "music"),
    ("is_jazz", "Персонаж связан с джазом?", "Is the character associated with jazz?", "music"),
    ("is_rapper", "Персонаж - рэпер?", "Is the character a rapper?", "music"),
    ("plays_piano", "Персонаж играет на пианино?", "Does the character play piano?", "music"),
    ("plays_guitar", "Персонаж играет на гитаре?", "Does the character play guitar?", "music"),

    # Nationalities (more specific)
    ("is_french", "Персонаж - француз?", "Is the character French?", "nationality"),
    ("is_italian", "Персонаж - итальянец?", "Is the character Italian?", "nationality"),
    ("is_spanish", "Персонаж - испанец?", "Is the character Spanish?", "nationality"),
    ("is_german", "Персонаж - немец?", "Is the character German?", "nationality"),
    ("is_british", "Персонаж - британец?", "Is the character British?", "nationality"),
    ("is_polish", "Персонаж - поляк?", "Is the character Polish?", "nationality"),
]


def main():
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)

    # Get existing attributes
    existing = set()
    for row in conn.execute("SELECT key FROM attributes"):
        existing.add(row[0])

    added = 0
    for key, q_ru, q_en, category in NEW_ATTRIBUTES:
        if key in existing:
            print(f"  Skipped (exists): {key}")
            continue

        conn.execute("""
            INSERT INTO attributes (key, question_ru, question_en, category)
            VALUES (?, ?, ?, ?)
        """, (key, q_ru, q_en, category))
        added += 1
        print(f"  Added: {key}")

    conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM attributes").fetchone()[0]
    conn.close()

    print(f"\nDone! Added {added} attributes. Total now: {total}")


if __name__ == "__main__":
    main()
