#!/usr/bin/env python3
"""Fix remaining 49 failures to push accuracy toward 95%+.

Groups:
- Athletes (12): goalkeepers, tennis players, etc.
- Fictional (16): superheroes, games, animation
- Musicians (4): classical, jazz, pop
- Others: actors, scientists, writers
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "collected.db"

FIXES = {
    # === ATHLETES ===

    # Soccer goalkeepers - need is_goalkeeper attribute
    "Manuel Neuer": {
        "is_goalkeeper": 1.0,
        "from_europe": 1.0,
        "is_german": 1.0,
        "world_champion": 1.0,
        "is_tall": 1.0,
        "is_captain": 0.8,
    },
    "Gianluigi Buffon": {
        "is_goalkeeper": 1.0,
        "from_europe": 1.0,
        "is_italian": 1.0,
        "world_champion": 1.0,
        "is_tall": 1.0,
        "is_legend": 1.0,
    },
    "Iker Casillas": {
        "is_goalkeeper": 1.0,
        "from_europe": 1.0,
        "is_spanish": 1.0,
        "world_champion": 1.0,
        "is_captain": 1.0,
    },

    # Soccer defenders
    "Sergio Ramos": {
        "is_defender": 1.0,
        "from_europe": 1.0,
        "is_spanish": 1.0,
        "is_captain": 1.0,
        "is_aggressive": 1.0,
        "known_for_headers": 1.0,
    },

    # Soccer strikers/forwards
    "Thierry Henry": {
        "is_striker": 1.0,
        "from_europe": 1.0,
        "is_french": 1.0,
        "world_champion": 1.0,
        "is_fast": 1.0,
        "played_in_england": 1.0,
    },
    "Kylian Mbappé": {
        "is_striker": 1.0,
        "from_europe": 1.0,
        "is_french": 1.0,
        "world_champion": 1.0,
        "is_fast": 1.0,
        "born_after_1990": 1.0,
        "is_young": 1.0,
    },

    # Tennis players
    "Rafael Nadal": {
        "plays_tennis": 1.0,
        "from_europe": 1.0,
        "is_spanish": 1.0,
        "is_left_handed": 1.0,
        "known_for_clay": 1.0,
        "grand_slam_winner": 1.0,
    },
    "Novak Djokovic": {
        "plays_tennis": 1.0,
        "from_europe": 1.0,
        "is_serbian": 1.0,
        "grand_slam_winner": 1.0,
        "is_flexible": 1.0,
    },
    "Andy Murray": {
        "plays_tennis": 1.0,
        "from_uk": 1.0,
        "is_british": 1.0,
        "grand_slam_winner": 1.0,
        "olympic_gold": 1.0,
    },
    "Pete Sampras": {
        "plays_tennis": 1.0,
        "from_usa": 1.0,
        "grand_slam_winner": 1.0,
        "born_before_1980": 1.0,
        "is_retired": 1.0,
    },

    # Basketball
    "Dirk Nowitzki": {
        "plays_basketball": 1.0,
        "from_europe": 1.0,
        "is_german": 1.0,
        "is_tall": 1.0,
        "nba_champion": 1.0,
        "is_shooter": 1.0,
    },

    # Other athletes
    "Jon Jones": {
        "from_mma": 1.0,
        "from_usa": 1.0,
        "is_controversial": 1.0,
        "is_champion": 1.0,
    },
    "Michael Phelps": {
        "is_swimmer": 1.0,
        "from_usa": 1.0,
        "olympic_gold": 1.0,
        "most_decorated": 1.0,
        "is_tall": 1.0,
    },
    "Valentino Rossi": {
        "is_motorcycle_racer": 1.0,
        "from_europe": 1.0,
        "is_italian": 1.0,
        "world_champion": 1.0,
        "wears_yellow": 1.0,
    },

    # === ACTORS ===

    "Jackie Chan": {
        "does_own_stunts": 1.0,
        "from_asia": 1.0,
        "from_hong_kong": 1.0,
        "martial_artist": 1.0,
        "is_comedic": 0.7,
        "from_action_genre": 1.0,
    },
    "Chris Pratt": {
        "from_usa": 1.0,
        "is_comedic": 0.8,
        "from_action_genre": 0.7,
        "from_scifi_genre": 0.8,
        "was_overweight": 1.0,  # Parks and Rec era
        "is_voice_actor": 0.8,  # Mario, Garfield
    },
    "Chris Evans": {
        "from_usa": 1.0,
        "is_comedic": 0.3,
        "from_action_genre": 1.0,
        "plays_superhero": 1.0,  # Captain America
        "is_muscular": 1.0,
    },
    "Emma Stone": {
        "from_usa": 1.0,
        "is_redhead": 1.0,
        "won_oscar": 1.0,
        "from_comedy_genre": 0.7,
        "from_musical": 0.8,  # La La Land
    },
    "Reese Witherspoon": {
        "from_usa": 1.0,
        "is_blonde": 1.0,
        "won_oscar": 1.0,
        "is_producer": 1.0,
        "from_comedy_genre": 0.6,
    },
    "Aamir Khan": {
        "from_india": 1.0,
        "from_bollywood": 1.0,
        "is_producer": 1.0,
        "known_for_method_acting": 1.0,
    },
    "Shah Rukh Khan": {
        "from_india": 1.0,
        "from_bollywood": 1.0,
        "is_romantic_lead": 1.0,
        "known_for_dancing": 1.0,
    },

    # === MUSICIANS ===

    "Chopin": {
        "is_composer": 1.0,
        "from_europe": 1.0,
        "is_polish": 1.0,
        "plays_piano": 1.0,
        "from_romantic_era": 1.0,
        "died_young": 1.0,
    },
    "Liszt": {
        "is_composer": 1.0,
        "from_europe": 1.0,
        "is_hungarian": 1.0,
        "plays_piano": 1.0,
        "from_romantic_era": 1.0,
        "is_virtuoso": 1.0,
        "had_long_hair": 1.0,
    },
    "Vivaldi": {
        "is_composer": 1.0,
        "from_europe": 1.0,
        "is_italian": 1.0,
        "plays_violin": 1.0,
        "from_baroque_era": 1.0,
        "was_priest": 1.0,
        "has_red_hair": 1.0,
    },
    "John Coltrane": {
        "is_jazz": 1.0,
        "from_usa": 1.0,
        "plays_saxophone": 1.0,
        "is_innovative": 1.0,
        "died_young": 0.8,
    },
    "Charlie Parker": {
        "is_jazz": 1.0,
        "from_usa": 1.0,
        "plays_saxophone": 1.0,
        "is_bebop": 1.0,
        "died_young": 1.0,
        "had_addiction": 1.0,
    },
    "Justin Bieber": {
        "from_canada": 1.0,
        "is_pop": 1.0,
        "started_young": 1.0,
        "from_youtube": 1.0,
        "is_controversial": 0.6,
    },
    "The Weeknd": {
        "from_canada": 1.0,
        "is_pop": 1.0,
        "is_rnb": 1.0,
        "has_distinctive_hair": 1.0,
        "is_dark_brooding": 0.7,
    },
    "Kendrick Lamar": {
        "is_rapper": 1.0,
        "from_usa": 1.0,
        "from_compton": 1.0,
        "is_lyrical": 1.0,
        "won_pulitzer": 1.0,
    },
    "Lil Wayne": {
        "is_rapper": 1.0,
        "from_usa": 1.0,
        "from_new_orleans": 1.0,
        "has_tattoos": 1.0,
        "has_dreadlocks": 1.0,
    },

    # === POLITICIANS ===

    "Theodore Roosevelt": {
        "from_usa": 1.0,
        "is_president": 1.0,
        "is_republican": 1.0,
        "is_military": 1.0,
        "known_for_conservation": 1.0,
        "wore_glasses": 1.0,
        "had_mustache": 1.0,
    },
    "Thomas Jefferson": {
        "from_usa": 1.0,
        "is_president": 1.0,
        "is_founding_father": 1.0,
        "is_writer": 1.0,  # Declaration
        "born_before_1800": 1.0,
    },

    # === SCIENTISTS/PHILOSOPHERS ===

    "Kant": {
        "is_philosopher": 1.0,
        "from_europe": 1.0,
        "is_german": 1.0,
        "from_18th_century": 1.0,
        "known_for_ethics": 1.0,
    },
    "Descartes": {
        "is_philosopher": 1.0,
        "from_europe": 1.0,
        "is_french": 1.0,
        "is_mathematician": 1.0,
        "from_17th_century": 1.0,
        "known_for_cogito": 1.0,  # "I think therefore I am"
    },
    "Archimedes": {
        "is_scientist": 1.0,
        "from_ancient_greece": 1.0,
        "is_mathematician": 1.0,
        "is_inventor": 1.0,
        "born_before_0": 1.0,
    },

    # === WRITERS ===

    "Victor Hugo": {
        "is_writer": 1.0,
        "from_europe": 1.0,
        "is_french": 1.0,
        "from_19th_century": 1.0,
        "wrote_les_miserables": 1.0,
        "is_romantic": 1.0,
    },
    "Arthur Conan Doyle": {
        "is_writer": 1.0,
        "from_uk": 1.0,
        "is_british": 1.0,
        "created_sherlock": 1.0,
        "is_mystery_writer": 1.0,
        "was_doctor": 1.0,
    },
    "Charles Dickens": {
        "is_writer": 1.0,
        "from_uk": 1.0,
        "is_british": 1.0,
        "from_victorian_era": 1.0,
        "wrote_christmas_carol": 1.0,
    },

    # === YOUTUBERS ===

    "Casey Neistat": {
        "is_youtuber": 1.0,
        "from_usa": 1.0,
        "is_filmmaker": 1.0,
        "is_vlogger": 1.0,
        "wears_sunglasses": 1.0,
        "has_distinctive_style": 1.0,
    },
    "Markiplier": {
        "is_youtuber": 1.0,
        "from_usa": 1.0,
        "is_gamer": 1.0,
        "plays_horror_games": 1.0,
        "has_colored_hair": 1.0,
    },

    # === FICTIONAL - SUPERHEROES ===

    "Thor": {
        "is_god": 1.0,
        "from_marvel": 1.0,
        "has_hammer": 1.0,
        "is_blonde": 1.0,
        "from_asgard": 1.0,
        "controls_lightning": 1.0,
        "is_royalty": 1.0,
    },
    "Loki": {
        "is_god": 1.0,
        "from_marvel": 1.0,
        "is_villain": 0.7,
        "has_dark_hair": 1.0,
        "from_asgard": 1.0,
        "is_trickster": 1.0,
        "is_adopted": 1.0,
    },
    "Cyclops": {
        "from_marvel": 1.0,
        "is_xmen": 1.0,
        "has_laser_eyes": 1.0,
        "wears_visor": 1.0,
        "is_leader": 1.0,
    },
    "Flash": {
        "from_dc": 1.0,
        "has_super_speed": 1.0,
        "wears_red": 1.0,
        "is_scientist": 0.7,
    },
    "Venom": {
        "from_marvel": 1.0,
        "is_villain": 0.6,
        "is_symbiote": 1.0,
        "is_antihero": 0.8,
        "has_teeth": 1.0,
        "is_black": 1.0,
    },
    "Green Lantern": {
        "from_dc": 1.0,
        "has_ring": 1.0,
        "wears_green": 1.0,
        "is_space_cop": 1.0,
        "creates_constructs": 1.0,
    },
    "Captain Marvel": {
        "from_marvel": 1.0,
        "is_female": 1.0,
        "is_military": 1.0,
        "has_cosmic_powers": 1.0,
        "is_blonde": 1.0,
    },
    "cyborg": {
        "from_dc": 1.0,
        "is_robot": 0.5,
        "is_black": 1.0,
        "is_teen_titan": 1.0,
        "has_tech_powers": 1.0,
    },
    "Catwoman": {
        "from_dc": 1.0,
        "is_female": 1.0,
        "is_villain": 0.5,
        "is_thief": 1.0,
        "wears_black": 1.0,
        "has_whip": 1.0,
    },
    "Wonder Woman": {
        "from_dc": 1.0,
        "is_female": 1.0,
        "is_amazon": 1.0,
        "has_lasso": 1.0,
        "is_princess": 1.0,
        "is_warrior": 1.0,
    },
    "Bane": {
        "from_dc": 1.0,
        "is_villain": 1.0,
        "is_muscular": 1.0,
        "wears_mask": 1.0,
        "uses_venom_drug": 1.0,
        "broke_batman": 1.0,
    },
    "Batgirl": {
        "from_dc": 1.0,
        "is_female": 1.0,
        "is_bat_family": 1.0,
        "is_redhead": 1.0,
        "is_hacker": 1.0,
    },

    # === FICTIONAL - GAMES ===

    "Zelda": {
        "from_nintendo": 1.0,
        "is_princess": 1.0,
        "is_female": 1.0,
        "has_magic": 1.0,
        "from_hyrule": 1.0,
        "is_wise": 1.0,
    },
    "Kirby": {
        "from_nintendo": 1.0,
        "is_pink": 1.0,
        "is_round": 1.0,
        "can_absorb": 1.0,
        "is_cute": 1.0,
    },
    "Kratos": {
        "from_playstation": 1.0,
        "is_god_slayer": 1.0,
        "is_greek": 0.5,
        "is_norse": 0.5,
        "is_angry": 1.0,
        "is_bald": 1.0,
        "has_beard": 1.0,
        "is_father": 1.0,
    },
    "Charizard": {
        "from_pokemon": 1.0,
        "is_dragon": 0.5,  # Fire/Flying actually
        "has_fire": 1.0,
        "is_orange": 1.0,
        "can_fly": 1.0,
        "is_starter": 1.0,
    },
    "Mewtwo": {
        "from_pokemon": 1.0,
        "is_legendary": 1.0,
        "is_psychic": 1.0,
        "is_clone": 1.0,
        "is_purple": 1.0,
        "is_powerful": 1.0,
    },

    # === FICTIONAL - ANIMATION ===

    "Simba": {
        "from_disney": 1.0,
        "is_lion": 1.0,
        "is_prince": 1.0,
        "from_africa": 1.0,
        "has_mane": 1.0,
        "is_main_character": 1.0,
    },
    "Pluto": {
        "from_disney": 1.0,
        "is_dog": 1.0,
        "is_pet": 1.0,
        "is_yellow": 1.0,
        "cannot_speak": 1.0,
        "is_mickeys_pet": 1.0,
    },
    "donkey": {
        "from_dreamworks": 1.0,
        "is_donkey": 1.0,
        "is_comedic": 1.0,
        "is_sidekick": 1.0,
        "is_talkative": 1.0,
        "from_shrek": 1.0,
    },
    "Shrek": {
        "from_dreamworks": 1.0,
        "is_ogre": 1.0,
        "is_green": 1.0,
        "is_main_character": 1.0,
        "lives_in_swamp": 1.0,
    },
    "Bugs Bunny": {
        "from_warner_bros": 1.0,
        "is_rabbit": 1.0,
        "is_grey": 1.0,
        "is_comedic": 1.0,
        "eats_carrots": 1.0,
        "is_trickster": 1.0,
        "is_main_character": 1.0,
    },
    "Goofy": {
        "from_disney": 1.0,
        "is_dog": 1.0,
        "is_tall": 1.0,
        "is_clumsy": 1.0,
        "is_comedic": 1.0,
        "is_sidekick": 0.7,
    },

    # === FICTIONAL - MOVIES ===

    "Kylo Ren": {
        "from_star_wars": 1.0,
        "is_villain": 0.7,
        "has_dark_side": 1.0,
        "has_mask": 0.8,
        "is_solo_son": 1.0,
        "has_red_lightsaber": 1.0,
        "is_conflicted": 1.0,
    },
    "Darth Vader": {
        "from_star_wars": 1.0,
        "is_villain": 0.8,
        "has_dark_side": 1.0,
        "has_mask": 1.0,
        "is_father": 1.0,
        "has_red_lightsaber": 1.0,
        "is_iconic": 1.0,
        "has_breathing_sound": 1.0,
    },
    "Frodo Baggins": {
        "from_lotr": 1.0,
        "is_hobbit": 1.0,
        "is_ring_bearer": 1.0,
        "is_main_character": 1.0,
        "has_dark_hair": 1.0,
    },
    "Samwise Gamgee": {
        "from_lotr": 1.0,
        "is_hobbit": 1.0,
        "is_sidekick": 1.0,
        "is_loyal": 1.0,
        "is_gardener": 1.0,
        "has_blonde_hair": 1.0,
    },
    "Bilbo Baggins": {
        "from_lotr": 1.0,
        "is_hobbit": 1.0,
        "is_older": 1.0,
        "found_the_ring": 1.0,
        "is_writer": 1.0,  # "There and Back Again"
    },
}


def main():
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Get attribute IDs
    attr_map = {}
    for row in conn.execute("SELECT id, key FROM attributes"):
        attr_map[row["key"]] = row["id"]

    # Get entity IDs
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
        fixed = False

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
            fixed = True

        if fixed:
            updated += 1
            print(f"  Fixed: {name}")

    conn.commit()
    conn.close()

    if missing_attrs:
        print(f"\nMissing attributes (need to add to schema): {sorted(missing_attrs)}")

    print(f"\nDone! Updated {updated} entities.")


if __name__ == "__main__":
    main()
