#!/usr/bin/env python3
"""Final fixes for remaining 41 failures."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "collected.db"

FIXES = {
    # === ATHLETES - need sport-specific differentiation ===

    # Tennis players
    "Rafael Nadal": {
        "plays_tennis": 1.0,
        "is_spanish": 1.0,
        "from_europe": 1.0,
        "from_sport": 1.0,
    },
    "Novak Djokovic": {
        "plays_tennis": 1.0,
        "from_europe": 1.0,
        "from_sport": 1.0,
    },
    "Andy Murray": {
        "plays_tennis": 1.0,
        "is_british": 1.0,
        "from_europe": 1.0,
        "from_sport": 1.0,
    },
    "Pete Sampras": {
        "plays_tennis": 1.0,
        "from_usa": 1.0,
        "from_sport": 1.0,
        "born_before_1950": 0.0,
        "born_1950_1970": 1.0,
    },

    # Soccer goalkeepers
    "Manuel Neuer": {
        "is_goalkeeper": 1.0,
        "is_german": 1.0,
        "from_europe": 1.0,
        "is_tall": 1.0,
        "plays_tennis": 0.0,
        "plays_basketball": 0.0,
    },
    "Gianluigi Buffon": {
        "is_goalkeeper": 1.0,
        "is_italian": 1.0,
        "from_europe": 1.0,
        "is_tall": 1.0,
        "plays_tennis": 0.0,
    },
    "Iker Casillas": {
        "is_goalkeeper": 1.0,
        "is_spanish": 1.0,
        "from_europe": 1.0,
        "plays_tennis": 0.0,
    },

    # Soccer defenders
    "Sergio Ramos": {
        "is_defender": 1.0,
        "is_spanish": 1.0,
        "from_europe": 1.0,
        "plays_tennis": 0.0,
        "plays_basketball": 0.0,
        "has_tattoos": 1.0,
    },

    # Soccer strikers
    "Thierry Henry": {
        "is_striker": 1.0,
        "is_french": 1.0,
        "from_europe": 1.0,
        "plays_tennis": 0.0,
        "plays_basketball": 0.0,
    },
    "Robert Lewandowski": {
        "is_striker": 1.0,
        "is_polish": 1.0,
        "from_europe": 1.0,
        "plays_tennis": 0.0,
    },
    "Karim Benzema": {
        "is_striker": 1.0,
        "is_french": 1.0,
        "from_europe": 1.0,
        "plays_tennis": 0.0,
    },

    # Basketball
    "Dirk Nowitzki": {
        "plays_basketball": 1.0,
        "is_german": 1.0,
        "from_europe": 1.0,
        "is_tall": 1.0,
        "plays_tennis": 0.0,
        "is_goalkeeper": 0.0,
    },
    "Tim Duncan": {
        "plays_basketball": 1.0,
        "from_usa": 1.0,
        "is_tall": 1.0,
        "plays_tennis": 0.0,
    },
    "Kevin Durant": {
        "plays_basketball": 1.0,
        "from_usa": 1.0,
        "is_tall": 1.0,
        "plays_tennis": 0.0,
    },

    # Other athletes
    "Jon Jones": {
        "is_mma_fighter": 1.0,
        "from_usa": 1.0,
        "plays_tennis": 0.0,
        "plays_basketball": 0.0,
        "controversial": 1.0,
    },
    "Michael Phelps": {
        "is_swimmer": 1.0,
        "from_usa": 1.0,
        "olympic_medalist": 1.0,
        "plays_tennis": 0.0,
        "plays_basketball": 0.0,
    },
    "Valentino Rossi": {
        "is_racer": 1.0,
        "is_italian": 1.0,
        "from_europe": 1.0,
        "plays_tennis": 0.0,
    },

    # === MUSICIANS ===

    # Classical composers - differentiate by era and instrument
    "Chopin": {
        "is_composer": 1.0,
        "is_classical": 1.0,
        "is_polish": 1.0,
        "plays_piano": 1.0,
        "is_jazz": 0.0,
        "from_europe": 1.0,
        "born_before_1950": 1.0,
        "era_modern": 1.0,
    },
    "Liszt": {
        "is_composer": 1.0,
        "is_classical": 1.0,
        "plays_piano": 1.0,
        "is_jazz": 0.0,
        "from_europe": 1.0,
        "born_before_1950": 1.0,
        "era_modern": 1.0,
        "known_for_physique": 0.8,  # Was known as very handsome
    },
    "Vivaldi": {
        "is_composer": 1.0,
        "is_classical": 1.0,
        "is_italian": 1.0,
        "plays_piano": 0.0,
        "plays_guitar": 0.0,  # Violin actually, but differentiate
        "is_jazz": 0.0,
        "from_europe": 1.0,
        "born_before_1950": 1.0,
        "era_medieval": 0.5,  # Baroque era
    },

    # Jazz musicians
    "John Coltrane": {
        "is_jazz": 1.0,
        "plays_saxophone": 1.0,
        "from_usa": 1.0,
        "is_classical": 0.0,
        "plays_piano": 0.0,
        "born_1950_1970": 0.0,
        "born_before_1950": 1.0,
    },
    "Charlie Parker": {
        "is_jazz": 1.0,
        "plays_saxophone": 1.0,
        "from_usa": 1.0,
        "is_classical": 0.0,
        "died_young": 1.0,
        "born_before_1950": 1.0,
    },

    # Rappers
    "Kendrick Lamar": {
        "is_rapper": 1.0,
        "from_usa": 1.0,
        "has_glasses": 0.0,
        "has_tattoos": 0.3,
        "won_grammy": 1.0,
    },
    "Lil Wayne": {
        "is_rapper": 1.0,
        "from_usa": 1.0,
        "has_tattoos": 1.0,
        "distinctive_hair": 1.0,
    },

    # === ACTORS ===

    "Emma Stone": {
        "is_redhead": 1.0,
        "won_oscar": 1.0,
        "from_usa": 1.0,
        "is_comedic": 0.6,
        "is_blonde": 0.0,
    },
    "Reese Witherspoon": {
        "is_blonde": 1.0,
        "won_oscar": 1.0,
        "from_usa": 1.0,
        "is_redhead": 0.0,
    },
    "Aamir Khan": {
        "from_bollywood": 1.0,
        "from_india": 1.0,
        "from_asia": 1.0,
        "is_muscular": 0.8,  # Known for body transformations
    },
    "Shah Rukh Khan": {
        "from_bollywood": 1.0,
        "from_india": 1.0,
        "from_asia": 1.0,
        "is_romantic_lead": 1.0,
    },

    # === POLITICIANS ===

    "Theodore Roosevelt": {
        "is_president": 1.0,
        "from_usa": 1.0,
        "has_glasses": 1.0,
        "has_facial_hair": 1.0,
        "is_muscular": 0.8,
        "born_before_1950": 1.0,
    },
    "Thomas Jefferson": {
        "is_president": 1.0,
        "from_usa": 1.0,
        "has_glasses": 0.0,
        "has_facial_hair": 0.0,
        "era_modern": 1.0,
        "born_before_1950": 1.0,
    },

    # === SCIENTISTS/PHILOSOPHERS ===

    "Kant": {
        "is_philosopher": 1.0,
        "is_german": 1.0,
        "from_europe": 1.0,
        "from_science": 0.5,
        "born_before_1950": 1.0,
        "era_modern": 1.0,
    },
    "Descartes": {
        "is_philosopher": 1.0,
        "is_french": 1.0,
        "from_europe": 1.0,
        "from_science": 0.7,  # Also mathematician
        "born_before_1950": 1.0,
        "era_modern": 1.0,
    },
    "Archimedes": {
        "is_philosopher": 0.3,
        "from_science": 1.0,
        "from_europe": 1.0,
        "era_ancient": 1.0,
        "born_before_1950": 1.0,
    },

    # === WRITERS ===

    "Victor Hugo": {
        "from_literature": 1.0,
        "is_french": 1.0,
        "from_europe": 1.0,
        "from_politics": 0.3,
        "born_before_1950": 1.0,
    },
    "Arthur Conan Doyle": {
        "from_literature": 1.0,
        "is_british": 1.0,
        "from_europe": 1.0,
        "is_detective": 0.0,  # Wrote detective fiction
        "born_before_1950": 1.0,
    },
    "Charles Dickens": {
        "from_literature": 1.0,
        "is_british": 1.0,
        "from_europe": 1.0,
        "born_before_1950": 1.0,
        "has_facial_hair": 1.0,
    },
    "Otto von Bismarck": {
        "from_politics": 1.0,
        "is_german": 1.0,
        "from_europe": 1.0,
        "from_literature": 0.0,
        "is_leader": 1.0,
        "has_facial_hair": 1.0,
    },

    # === YOUTUBERS ===

    "Casey Neistat": {
        "is_youtuber": 1.0,
        "is_vlogger": 1.0,
        "from_usa": 1.0,
        "is_gamer": 0.0,
        "has_glasses": 1.0,
    },
    "Markiplier": {
        "is_youtuber": 1.0,
        "is_gamer": 1.0,
        "from_usa": 1.0,
        "is_vlogger": 0.3,
        "distinctive_hair": 1.0,
    },

    # === FICTIONAL - LOTR ===

    "Frodo Baggins": {
        "is_hobbit": 1.0,
        "from_lotr": 1.0,
        "has_dark_hair": 1.0,
        "is_sidekick": 0.0,
        "is_fictional": 1.0,
    },
    "Samwise Gamgee": {
        "is_hobbit": 1.0,
        "from_lotr": 1.0,
        "is_blonde": 1.0,
        "has_dark_hair": 0.0,
        "is_sidekick": 1.0,
        "is_fictional": 1.0,
    },
    "Bilbo Baggins": {
        "is_hobbit": 1.0,
        "from_lotr": 1.0,
        "has_dark_hair": 0.5,
        "is_sidekick": 0.0,
        "is_fictional": 1.0,
        "is_adult": 1.0,  # Older
    },

    # === FICTIONAL - ANIMATION ===

    "Simba": {
        "is_lion": 1.0,
        "is_animal": 1.0,
        "from_disney": 1.0,
        "is_royalty": 1.0,
        "is_dog": 0.0,
        "is_fictional": 1.0,
    },
    "Pluto": {
        "is_dog": 1.0,
        "is_animal": 1.0,
        "from_disney": 1.0,
        "is_lion": 0.0,
        "is_sidekick": 1.0,
        "is_fictional": 1.0,
    },
    "donkey": {
        "is_donkey": 1.0,
        "is_animal": 1.0,
        "from_dreamworks": 1.0,
        "is_sidekick": 1.0,
        "is_comedic": 1.0,
        "is_dog": 0.0,
        "is_ogre": 0.0,
        "is_fictional": 1.0,
    },
    "Shrek": {
        "is_ogre": 1.0,
        "from_dreamworks": 1.0,
        "is_sidekick": 0.0,
        "is_animal": 0.0,
        "is_donkey": 0.0,
        "is_fictional": 1.0,
    },
    "Bugs Bunny": {
        "is_rabbit": 1.0,
        "is_animal": 1.0,
        "is_comedic": 1.0,
        "from_disney": 0.0,
        "is_dog": 0.0,
        "is_fictional": 1.0,
    },
    "Goofy": {
        "is_dog": 1.0,
        "is_animal": 1.0,
        "from_disney": 1.0,
        "is_rabbit": 0.0,
        "is_comedic": 1.0,
        "is_sidekick": 1.0,
        "is_fictional": 1.0,
    },

    # === FICTIONAL - GAMES ===

    "Zelda": {
        "from_nintendo": 1.0,
        "is_princess": 1.0,
        "is_royalty": 1.0,
        "from_game": 1.0,
        "from_pokemon": 0.0,
        "is_fictional": 1.0,
    },
    "Kirby": {
        "from_nintendo": 1.0,
        "is_princess": 0.0,
        "from_game": 1.0,
        "from_pokemon": 0.0,
        "is_fictional": 1.0,
        "is_child_friendly": 1.0,
    },
    "Kratos": {
        "from_nintendo": 0.0,
        "from_game": 1.0,
        "is_bald": 1.0,
        "has_facial_hair": 1.0,
        "is_action_hero": 1.0,
        "is_dark_brooding": 1.0,
        "is_fictional": 1.0,
    },
    "Charizard": {
        "from_pokemon": 1.0,
        "from_nintendo": 1.0,
        "from_game": 1.0,
        "is_animal": 1.0,
        "is_princess": 0.0,
        "is_fictional": 1.0,
    },
    "Mewtwo": {
        "from_pokemon": 1.0,
        "from_nintendo": 1.0,
        "from_game": 1.0,
        "is_villain": 0.5,
        "is_princess": 0.0,
        "is_dark_brooding": 0.7,
        "is_fictional": 1.0,
    },

    # === FICTIONAL - SUPERHEROES ===

    "Venom": {
        "is_symbiote": 1.0,
        "from_marvel": 1.0,
        "is_villain": 0.6,
        "is_dark_brooding": 1.0,
        "is_god": 0.0,
        "is_fictional": 1.0,
    },
    "Loki": {
        "is_god": 1.0,
        "from_marvel": 1.0,
        "is_villain": 0.7,
        "is_symbiote": 0.0,
        "is_fictional": 1.0,
    },
    "cyborg": {
        "is_cyborg": 1.0,
        "from_dc": 1.0,
        "is_robot": 0.5,
        "is_god": 0.0,
        "is_symbiote": 0.0,
        "is_fictional": 1.0,
    },
    "Catwoman": {
        "from_dc": 1.0,
        "is_villain": 0.5,
        "is_male": 0.0,
        "is_god": 0.0,
        "is_fictional": 1.0,
    },
    "Wonder Woman": {
        "from_dc": 1.0,
        "is_villain": 0.0,
        "is_male": 0.0,
        "is_god": 0.5,
        "is_royalty": 1.0,
        "is_fictional": 1.0,
    },
    "Bane": {
        "from_dc": 1.0,
        "is_villain": 1.0,
        "is_male": 1.0,
        "is_muscular": 1.0,
        "wears_mask": 1.0,
        "is_fictional": 1.0,
    },
    "Batgirl": {
        "from_dc": 1.0,
        "is_villain": 0.0,
        "is_male": 0.0,
        "is_redhead": 1.0,
        "is_muscular": 0.0,
        "is_fictional": 1.0,
    },

    # === FICTIONAL - ANIME ===

    "SASUKE": {
        "from_anime": 1.0,
        "is_dark_brooding": 1.0,
        "is_villain": 0.6,
        "has_dark_hair": 1.0,
        "is_sidekick": 0.0,
        "is_fictional": 1.0,
    },
    "Itachi Uchiha": {
        "from_anime": 1.0,
        "is_dark_brooding": 1.0,
        "is_villain": 0.8,
        "has_dark_hair": 1.0,
        "is_sidekick": 0.0,
        "is_adult": 1.0,
        "is_fictional": 1.0,
    },
    "Ichigo Kurosaki": {
        "from_anime": 1.0,
        "is_dark_brooding": 0.6,
        "distinctive_hair": 1.0,  # Orange hair
        "has_dark_hair": 0.0,
        "is_fictional": 1.0,
    },
    "Todoroki": {
        "from_anime": 1.0,
        "is_dark_brooding": 0.7,
        "distinctive_hair": 1.0,  # Half-and-half hair
        "has_dark_hair": 0.5,
        "is_fictional": 1.0,
    },
    "Genos": {
        "from_anime": 1.0,
        "is_cyborg": 1.0,
        "is_robot": 0.5,
        "is_blonde": 1.0,
        "has_dark_hair": 0.0,
        "is_fictional": 1.0,
    },
    "Goku": {
        "from_anime": 1.0,
        "is_cyborg": 0.0,
        "is_blonde": 0.0,  # Normally black hair
        "has_dark_hair": 1.0,
        "is_comedic": 0.6,
        "is_fictional": 1.0,
    },
    "Zero Two": {
        "from_anime": 1.0,
        "is_male": 0.0,
        "distinctive_hair": 1.0,  # Pink with horns
        "is_fictional": 1.0,
    },
    "Rem": {
        "from_anime": 1.0,
        "is_male": 0.0,
        "is_sidekick": 0.8,
        "is_fictional": 1.0,
    },
}


def main():
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    attr_map = {}
    for row in conn.execute("SELECT id, key FROM attributes"):
        attr_map[row["key"]] = row["id"]

    entity_map = {}
    for row in conn.execute("SELECT id, name FROM entities"):
        entity_map[row["name"]] = row["id"]

    updated = 0
    missing_attrs = set()

    for name, attrs in FIXES.items():
        if name not in entity_map:
            print(f"  Entity not found: {name}")
            continue

        eid = entity_map[name]

        for attr_key, value in attrs.items():
            if attr_key not in attr_map:
                missing_attrs.add(attr_key)
                continue

            attr_id = attr_map[attr_key]
            conn.execute("""
                INSERT INTO entity_attributes (entity_id, attribute_id, value)
                VALUES (?, ?, ?)
                ON CONFLICT(entity_id, attribute_id) DO UPDATE SET value = ?
            """, (eid, attr_id, value, value))

        updated += 1

    conn.commit()
    conn.close()

    if missing_attrs:
        print(f"Missing attributes: {sorted(missing_attrs)}")

    print(f"Done! Updated {updated} entities.")


if __name__ == "__main__":
    main()
