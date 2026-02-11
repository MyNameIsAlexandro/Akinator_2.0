#!/usr/bin/env python3
"""Fix all 28 remaining failures using only available attributes."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "collected.db")

def fix(entity_name: str, attrs: dict):
    """Set specific attribute values for an entity."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id FROM entities WHERE name = ?", (entity_name,))
    row = cur.fetchone()
    if not row:
        print(f"  ⚠️  Entity not found: {entity_name}")
        conn.close()
        return False

    entity_id = row[0]
    fixed = 0

    for attr_key, value in attrs.items():
        cur.execute("SELECT id FROM attributes WHERE key = ?", (attr_key,))
        attr_row = cur.fetchone()
        if not attr_row:
            continue  # Skip silently for brevity
        attr_id = attr_row[0]

        cur.execute("""
            INSERT INTO entity_attributes (entity_id, attribute_id, value)
            VALUES (?, ?, ?)
            ON CONFLICT(entity_id, attribute_id) DO UPDATE SET value = ?
        """, (entity_id, attr_id, value, value))
        fixed += 1

    conn.commit()
    conn.close()
    print(f"  ✓ {entity_name}: {fixed} attrs")
    return True

def main():
    print("Fixing 28 failures with available attributes...\n")

    # =========================================
    # ATHLETES - Use sport-specific attributes
    # =========================================
    print("=== ATHLETES ===")

    # Sergio Ramos vs Robert Lewandowski - both soccer, defender vs striker
    fix("Sergio Ramos", {
        "is_soccer_player": 1.0,
        "is_defender": 1.0,
        "is_striker": 0.0,
        "is_spanish": 1.0,
        "is_polish": 0.0,
        "is_german": 0.0,
        "has_tattoos": 1.0,
        "is_goalkeeper": 0.0,
    })

    fix("Robert Lewandowski", {
        "is_soccer_player": 1.0,
        "is_defender": 0.0,
        "is_striker": 1.0,
        "is_spanish": 0.0,
        "is_polish": 1.0,
        "is_german": 0.0,
        "has_tattoos": 0.0,
        "is_goalkeeper": 0.0,
    })

    # Iker Casillas vs Manuel Neuer - both goalkeepers, Spanish vs German
    fix("Iker Casillas", {
        "is_soccer_player": 1.0,
        "is_goalkeeper": 1.0,
        "is_spanish": 1.0,
        "is_german": 0.0,
        "born_1950_1970": 0.0,
        "born_1970_1990": 1.0,
    })

    fix("Manuel Neuer", {
        "is_soccer_player": 1.0,
        "is_goalkeeper": 1.0,
        "is_spanish": 0.0,
        "is_german": 1.0,
        "born_1950_1970": 0.0,
        "born_1970_1990": 1.0,
    })

    # Dirk Nowitzki vs Rafael Nadal - basketball vs tennis!
    fix("Dirk Nowitzki", {
        "plays_basketball": 1.0,
        "plays_tennis": 0.0,
        "is_german": 1.0,
        "is_spanish": 0.0,
        "is_tall": 1.0,  # 7 feet!
        "born_1970_1990": 1.0,
    })

    fix("Rafael Nadal", {
        "plays_basketball": 0.0,
        "plays_tennis": 1.0,
        "is_german": 0.0,
        "is_spanish": 1.0,
        "is_tall": 0.0,
        "is_muscular": 1.0,
        "born_1970_1990": 1.0,
    })

    # Novak Djokovic vs Rafael Nadal - both tennis, Serbian vs Spanish
    fix("Novak Djokovic", {
        "plays_tennis": 1.0,
        "plays_basketball": 0.0,
        "is_spanish": 0.0,
        "from_europe": 1.0,
        "is_muscular": 0.6,
        "born_1970_1990": 1.0,
    })

    # Jon Jones vs Tim Duncan - MMA vs basketball!
    fix("Jon Jones", {
        "is_mma_fighter": 1.0,
        "plays_basketball": 0.0,
        "from_usa": 1.0,
        "has_tattoos": 1.0,
        "controversial": 1.0,
        "born_1970_1990": 1.0,
    })

    fix("Tim Duncan", {
        "is_mma_fighter": 0.0,
        "plays_basketball": 1.0,
        "from_usa": 1.0,
        "has_tattoos": 0.0,
        "controversial": 0.0,
        "born_1970_1990": 1.0,
        "is_tall": 1.0,
    })

    # Michael Phelps vs Kevin Durant - swimming vs basketball!
    fix("Michael Phelps", {
        "is_swimmer": 1.0,
        "plays_basketball": 0.0,
        "from_usa": 1.0,
        "olympic_medalist": 1.0,
        "world_champion": 1.0,
        "has_tattoos": 1.0,
        "born_1970_1990": 1.0,
    })

    fix("Kevin Durant", {
        "is_swimmer": 0.0,
        "plays_basketball": 1.0,
        "from_usa": 1.0,
        "olympic_medalist": 1.0,
        "is_tall": 1.0,
        "has_tattoos": 1.0,
        "born_1970_1990": 1.0,
    })

    # Valentino Rossi vs Rafael Nadal - racing vs tennis!
    fix("Valentino Rossi", {
        "is_racer": 1.0,
        "plays_tennis": 0.0,
        "is_italian": 1.0,
        "is_spanish": 0.0,
        "wears_helmet": 1.0,
        "born_1970_1990": 1.0,
        "world_champion": 1.0,
    })

    # =========================================
    # ACTORS
    # =========================================
    print("\n=== ACTORS ===")

    # Emma Stone vs Reese Witherspoon
    fix("Emma Stone", {
        "is_blonde": 0.0,
        "is_redhead": 1.0,
        "is_comedic": 0.7,
        "from_usa": 1.0,
        "won_oscar": 1.0,
        "born_1970_1990": 1.0,
    })

    fix("Reese Witherspoon", {
        "is_blonde": 1.0,
        "is_redhead": 0.0,
        "is_comedic": 0.8,
        "from_usa": 1.0,
        "won_oscar": 1.0,
        "born_1970_1990": 1.0,
    })

    # Aamir Khan vs Shah Rukh Khan - both Bollywood
    fix("Aamir Khan", {
        "from_bollywood": 1.0,
        "from_india": 1.0,
        "is_muscular": 0.8,
        "born_1950_1970": 1.0,
        "born_1970_1990": 0.0,
    })

    fix("Shah Rukh Khan", {
        "from_bollywood": 1.0,
        "from_india": 1.0,
        "is_romantic_lead": 1.0,
        "is_muscular": 0.5,
        "born_1950_1970": 1.0,
        "born_1970_1990": 0.0,
    })

    # Gregory Peck vs Jack Nicholson
    fix("Gregory Peck", {
        "from_usa": 1.0,
        "is_tall": 1.0,
        "born_before_1950": 1.0,
        "is_alive": 0.0,
        "is_action_hero": 0.5,
        "is_villain": 0.0,
    })

    fix("Jack Nicholson", {
        "from_usa": 1.0,
        "is_tall": 0.0,
        "is_bald": 1.0,
        "born_before_1950": 1.0,
        "is_alive": 1.0,
        "is_villain": 0.7,
        "won_oscar": 1.0,
    })

    # =========================================
    # MUSICIANS - Classical composers
    # =========================================
    print("\n=== MUSICIANS ===")

    # Chopin vs Vivaldi
    fix("Chopin", {
        "is_classical": 1.0,
        "is_composer": 1.0,
        "is_polish": 1.0,
        "is_italian": 0.0,
        "plays_piano": 1.0,
        "born_before_1950": 1.0,
        "era_modern": 0.0,
    })

    fix("Vivaldi", {
        "is_classical": 1.0,
        "is_composer": 1.0,
        "is_polish": 0.0,
        "is_italian": 1.0,
        "plays_piano": 0.0,
        "born_before_1950": 1.0,
        "era_medieval": 0.0,
        "era_ancient": 0.0,
    })

    # Liszt vs Vivaldi
    fix("Liszt", {
        "is_classical": 1.0,
        "is_composer": 1.0,
        "is_italian": 0.0,
        "plays_piano": 1.0,
        "from_europe": 1.0,
        "born_before_1950": 1.0,
        "distinctive_hair": 1.0,
    })

    # John Coltrane vs Charlie Parker - both jazz
    fix("John Coltrane", {
        "is_jazz": 1.0,
        "plays_saxophone": 1.0,
        "from_usa": 1.0,
        "is_alive": 0.0,
        "born_before_1950": 1.0,
    })

    fix("Charlie Parker", {
        "is_jazz": 1.0,
        "plays_saxophone": 1.0,
        "from_usa": 1.0,
        "is_alive": 0.0,
        "born_before_1950": 1.0,
        "died_young": 1.0,
    })

    # =========================================
    # FICTIONAL - Anime
    # =========================================
    print("\n=== FICTIONAL ANIME ===")

    # SASUKE vs Itachi - Naruto characters
    fix("SASUKE", {
        "from_anime": 1.0,
        "from_japan": 1.0,
        "is_villain": 0.3,
        "is_human": 1.0,
        "has_dark_hair": 1.0,
        "is_sidekick": 0.0,
        "is_adult": 0.5,
    })

    fix("Itachi Uchiha", {
        "from_anime": 1.0,
        "from_japan": 1.0,
        "is_villain": 0.7,
        "is_human": 1.0,
        "has_dark_hair": 1.0,
        "is_adult": 1.0,
        "is_alive": 0.0,
    })

    # Ichigo Kurosaki vs Todoroki - different series
    fix("Ichigo Kurosaki", {
        "from_anime": 1.0,
        "from_japan": 1.0,
        "is_human": 0.5,
        "has_superpower": 1.0,
        "has_dark_hair": 0.0,  # Orange hair
        "is_redhead": 0.7,
    })

    fix("Todoroki", {
        "from_anime": 1.0,
        "from_japan": 1.0,
        "is_human": 1.0,
        "has_superpower": 1.0,
        "has_dark_hair": 0.5,  # Two-toned
        "is_redhead": 0.5,
    })

    # Zero Two vs Rem - different series
    fix("Zero Two", {
        "from_anime": 1.0,
        "from_japan": 1.0,
        "is_human": 0.5,
        "is_redhead": 1.0,  # Pink hair
        "is_robot": 0.0,
        "is_cyborg": 0.0,
    })

    fix("Rem", {
        "from_anime": 1.0,
        "from_japan": 1.0,
        "is_human": 0.0,  # Demon
        "is_redhead": 0.0,
        "has_dark_hair": 0.0,  # Blue hair
        "is_sidekick": 1.0,
    })

    # =========================================
    # FICTIONAL - Games
    # =========================================
    print("\n=== FICTIONAL GAMES ===")

    # Zelda vs Kirby
    fix("Zelda", {
        "from_game": 1.0,
        "from_nintendo": 1.0,
        "is_princess": 1.0,
        "is_human": 1.0,
        "is_animal": 0.0,
        "is_blonde": 1.0,
        "has_superpower": 1.0,
    })

    fix("Kirby", {
        "from_game": 1.0,
        "from_nintendo": 1.0,
        "is_princess": 0.0,
        "is_human": 0.0,
        "is_animal": 0.0,  # Not really animal either
        "is_blonde": 0.0,
        "is_child_friendly": 1.0,
    })

    # Mewtwo vs Kirby
    fix("Mewtwo", {
        "from_game": 1.0,
        "from_nintendo": 1.0,
        "from_pokemon": 1.0,
        "is_human": 0.0,
        "is_animal": 0.0,
        "has_superpower": 1.0,
        "is_villain": 0.5,
        "is_dark_brooding": 1.0,
    })

    # =========================================
    # FICTIONAL - Animation
    # =========================================
    print("\n=== FICTIONAL ANIMATION ===")

    # Simba vs Pluto - lion vs dog!
    fix("Simba", {
        "from_disney": 1.0,
        "is_lion": 1.0,
        "is_dog": 0.0,
        "is_animal": 1.0,
        "is_royalty": 1.0,
        "from_africa": 1.0,
        "is_human": 0.0,
        "is_sidekick": 0.0,
    })

    fix("Pluto", {
        "from_disney": 1.0,
        "is_lion": 0.0,
        "is_dog": 1.0,
        "is_animal": 1.0,
        "is_royalty": 0.0,
        "from_africa": 0.0,
        "is_human": 0.0,
        "is_sidekick": 1.0,
    })

    # Bugs Bunny vs Goofy - rabbit vs dog, WB vs Disney
    fix("Bugs Bunny", {
        "is_rabbit": 1.0,
        "is_dog": 0.0,
        "from_disney": 0.0,
        "is_animal": 1.0,
        "is_comedic": 1.0,
        "is_human": 0.0,
        "is_sidekick": 0.0,
    })

    fix("Goofy", {
        "is_rabbit": 0.0,
        "is_dog": 1.0,
        "from_disney": 1.0,
        "is_animal": 1.0,
        "is_comedic": 1.0,
        "is_human": 0.0,
        "is_sidekick": 1.0,
    })

    # =========================================
    # FICTIONAL - Superheroes
    # =========================================
    print("\n=== FICTIONAL SUPERHEROES ===")

    # Venom vs Loki
    fix("Venom", {
        "from_marvel": 1.0,
        "is_symbiote": 1.0,
        "is_god": 0.0,
        "is_human": 0.5,
        "is_villain": 0.7,
        "has_dark_hair": 0.0,  # Black symbiote
        "is_muscular": 1.0,
    })

    fix("Loki", {
        "from_marvel": 1.0,
        "is_symbiote": 0.0,
        "is_god": 1.0,
        "is_human": 0.0,
        "is_villain": 0.7,
        "has_dark_hair": 1.0,
        "has_armor": 1.0,
    })

    # cyborg vs Loki - DC vs Marvel!
    fix("cyborg", {
        "from_dc": 1.0,
        "from_marvel": 0.0,
        "is_cyborg": 1.0,
        "is_robot": 0.5,
        "is_god": 0.0,
        "is_human": 0.5,
        "has_armor": 1.0,
    })

    # Catwoman vs Wonder Woman
    fix("Catwoman", {
        "from_dc": 1.0,
        "is_villain": 0.7,
        "is_human": 1.0,
        "is_god": 0.0,
        "has_dark_hair": 1.0,
        "wears_mask": 1.0,
        "is_princess": 0.0,
    })

    fix("Wonder Woman", {
        "from_dc": 1.0,
        "is_villain": 0.0,
        "is_human": 0.0,
        "is_god": 0.5,
        "has_dark_hair": 1.0,
        "wears_mask": 0.0,
        "is_princess": 1.0,
        "is_muscular": 1.0,
    })

    # =========================================
    # FICTIONAL - Movies (LOTR)
    # =========================================
    print("\n=== FICTIONAL MOVIES ===")

    # Frodo vs Samwise
    fix("Frodo Baggins", {
        "from_lotr": 1.0,
        "is_hobbit": 1.0,
        "is_human": 0.0,
        "is_tall": 0.0,
        "has_dark_hair": 1.0,
        "is_sidekick": 0.0,
    })

    fix("Samwise Gamgee", {
        "from_lotr": 1.0,
        "is_hobbit": 1.0,
        "is_human": 0.0,
        "is_tall": 0.0,
        "has_dark_hair": 0.0,  # Blonde-ish
        "is_sidekick": 1.0,
    })

    # Bilbo vs Samwise
    fix("Bilbo Baggins", {
        "from_lotr": 1.0,
        "is_hobbit": 1.0,
        "is_human": 0.0,
        "is_tall": 0.0,
        "has_dark_hair": 0.5,
        "is_sidekick": 0.0,
        "is_adult": 1.0,  # Older
    })

    # =========================================
    # WRITERS
    # =========================================
    print("\n=== WRITERS ===")

    # Arthur Conan Doyle vs Charles Dickens
    fix("Arthur Conan Doyle", {
        "from_uk": 1.0,
        "is_british": 1.0,
        "from_literature": 1.0,
        "is_detective": 0.0,  # Created detective, wasn't one
        "born_before_1950": 1.0,
        "is_alive": 0.0,
        "has_facial_hair": 1.0,
    })

    fix("Charles Dickens", {
        "from_uk": 1.0,
        "is_british": 1.0,
        "from_literature": 1.0,
        "born_before_1950": 1.0,
        "is_alive": 0.0,
        "has_facial_hair": 1.0,
    })

    # Miguel de Cervantes vs Victor Hugo
    fix("Miguel de Cervantes", {
        "is_spanish": 1.0,
        "is_french": 0.0,
        "from_literature": 1.0,
        "from_europe": 1.0,
        "born_before_1950": 1.0,
        "era_medieval": 0.0,
        "era_modern": 0.0,
    })

    fix("Victor Hugo", {
        "is_spanish": 0.0,
        "is_french": 1.0,
        "from_literature": 1.0,
        "from_europe": 1.0,
        "from_france": 1.0,
        "born_before_1950": 1.0,
    })

    # =========================================
    # SCIENTISTS/PHILOSOPHERS
    # =========================================
    print("\n=== SCIENTISTS ===")

    # Descartes vs Kant
    fix("Descartes", {
        "is_philosopher": 1.0,
        "is_french": 1.0,
        "is_german": 0.0,
        "from_france": 1.0,
        "from_europe": 1.0,
        "born_before_1950": 1.0,
    })

    fix("Kant", {
        "is_philosopher": 1.0,
        "is_french": 0.0,
        "is_german": 1.0,
        "from_germany": 1.0,
        "from_europe": 1.0,
        "born_before_1950": 1.0,
    })

    print("\n✅ All fixes applied!")

if __name__ == "__main__":
    main()
