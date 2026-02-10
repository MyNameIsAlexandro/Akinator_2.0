#!/usr/bin/env python3
"""Fix remaining anime character differentiation issues.

Failures to fix:
- SASUKE -> Todoroki (both dark rivals)
- Ichigo Kurosaki -> Todoroki (both dark protagonists)
- L/l -> Rem (both quiet/mysterious)
- Eren Yeager -> Todoroki (both dark)
- Nezuko Kamado -> Rem (both female, pink)
- Deku -> Goku (both main protagonists)
- Zero Two -> Rem (both female, pink)
- Itachi Uchiha -> Todoroki (both dark)
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "collected.db"

# Anime character-specific attributes
ANIME_FIXES = {
    # === Naruto characters ===
    "SASUKE": {
        "is_dark_brooding": 1.0,
        "is_villain": 0.6,        # Was a villain for part of series
        "has_rival": 1.0,
        "has_distinctive_hair": 1.0,  # Black spiky
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 0.8,
        "has_tragic_past": 1.0,    # Clan massacre
        "is_stoic": 1.0,
        "uses_magic": 0.0,         # Uses chakra/ninjutsu
        "wears_mask": 0.0,
        "born_with_powers": 1.0,   # Sharingan
    },
    "Itachi Uchiha": {
        "is_dark_brooding": 1.0,
        "is_villain": 0.8,        # Portrayed as villain, revealed hero
        "has_rival": 0.3,
        "has_distinctive_hair": 1.0,  # Long black ponytail
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 0.4,  # Side character
        "has_tragic_past": 1.0,
        "is_stoic": 1.0,
        "wears_mask": 0.0,
        "born_with_powers": 1.0,
        "is_older_character": 1.0,  # Older than protagonist
        "is_mysterious": 1.0,
    },

    # === My Hero Academia ===
    "Todoroki": {
        "is_dark_brooding": 0.7,
        "is_villain": 0.0,
        "has_rival": 1.0,
        "has_distinctive_hair": 1.0,  # Half white half red
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 0.7,
        "has_tragic_past": 0.8,
        "is_stoic": 0.8,
        "born_with_powers": 1.0,
        "has_fire_powers": 1.0,    # Fire + ice
        "has_ice_powers": 1.0,
        "wears_costume": 1.0,
    },
    "Deku": {
        "is_dark_brooding": 0.0,
        "is_villain": 0.0,
        "has_rival": 1.0,
        "has_distinctive_hair": 1.0,  # Green curly
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 1.0,
        "has_tragic_past": 0.3,
        "is_stoic": 0.0,
        "is_comedic": 0.4,
        "born_with_powers": 0.0,   # Quirkless, got powers later
        "is_underdog": 1.0,
        "wears_costume": 1.0,
        "is_friendly": 1.0,
    },

    # === Bleach ===
    "Ichigo Kurosaki": {
        "is_dark_brooding": 0.6,
        "is_villain": 0.0,
        "has_rival": 0.7,
        "has_distinctive_hair": 1.0,  # Orange spiky
        "is_male": 1.0,
        "is_human": 0.8,          # Part hollow
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 1.0,
        "has_tragic_past": 0.7,
        "is_stoic": 0.3,
        "born_with_powers": 0.0,   # Got powers from Rukia
        "uses_sword": 1.0,
        "wears_costume": 0.8,
        "has_orange_hair": 1.0,
    },

    # === Attack on Titan ===
    "Eren Yeager": {
        "is_dark_brooding": 0.8,
        "is_villain": 0.7,        # Becomes antagonist
        "has_rival": 0.5,
        "has_distinctive_hair": 0.8,  # Brown, later long
        "is_male": 1.0,
        "is_human": 0.5,          # Titan shifter
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 1.0,
        "has_tragic_past": 1.0,
        "is_stoic": 0.4,
        "can_transform": 1.0,     # Titan form
        "born_with_powers": 0.0,
        "is_angry": 1.0,
        "has_revenge_motive": 1.0,
    },

    # === Death Note ===
    "L/l": {
        "is_dark_brooding": 0.5,
        "is_villain": 0.0,
        "has_rival": 1.0,         # Light Yagami
        "has_distinctive_hair": 1.0,  # Messy black
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 0.0,   # Just genius
        "from_action_genre": 0.3,
        "is_main_character": 0.9,
        "has_tragic_past": 0.5,
        "is_stoic": 0.7,
        "is_mysterious": 1.0,
        "is_genius": 1.0,
        "is_detective": 1.0,
        "is_eccentric": 1.0,
        "wears_costume": 0.0,
        "has_unusual_posture": 1.0,  # Sits weird
    },

    # === Demon Slayer ===
    "Nezuko Kamado": {
        "is_dark_brooding": 0.0,
        "is_villain": 0.0,
        "has_rival": 0.0,
        "has_distinctive_hair": 1.0,  # Long black with orange tips
        "is_male": 0.0,
        "is_human": 0.3,          # Demon
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 0.9,
        "has_tragic_past": 1.0,
        "is_stoic": 0.2,
        "can_transform": 1.0,
        "is_demon": 1.0,
        "wears_bamboo": 1.0,      # Bamboo muzzle
        "is_protective": 1.0,
        "is_cute": 1.0,
        "has_pink_eyes": 1.0,
    },

    # === Re:Zero ===
    "Rem": {
        "is_dark_brooding": 0.3,
        "is_villain": 0.0,
        "has_rival": 0.3,
        "has_distinctive_hair": 1.0,  # Short blue
        "is_male": 0.0,
        "is_human": 0.0,          # Demon maid
        "has_superpowers": 1.0,
        "from_action_genre": 0.7,
        "is_main_character": 0.7,
        "has_tragic_past": 0.8,
        "is_stoic": 0.0,
        "is_demon": 1.0,
        "is_maid": 1.0,
        "has_blue_hair": 1.0,
        "is_cute": 1.0,
        "has_twin": 1.0,          # Ram
        "is_loyal": 1.0,
    },

    # === Darling in the Franxx ===
    "Zero Two": {
        "is_dark_brooding": 0.4,
        "is_villain": 0.2,
        "has_rival": 0.3,
        "has_distinctive_hair": 1.0,  # Pink long with horns
        "is_male": 0.0,
        "is_human": 0.5,          # Klaxosaur hybrid
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 1.0,
        "has_tragic_past": 1.0,
        "is_stoic": 0.0,
        "has_horns": 1.0,
        "has_pink_hair": 1.0,
        "is_cute": 0.8,
        "is_flirty": 1.0,
        "pilots_mech": 1.0,
        "is_mysterious": 1.0,
    },

    # === Dragon Ball ===
    "Goku": {
        "is_dark_brooding": 0.0,
        "is_villain": 0.0,
        "has_rival": 1.0,         # Vegeta
        "has_distinctive_hair": 1.0,  # Black spiky, turns gold
        "is_male": 1.0,
        "is_human": 0.0,          # Saiyan
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 1.0,
        "has_tragic_past": 0.2,
        "is_stoic": 0.0,
        "is_comedic": 0.6,
        "is_alien": 1.0,
        "can_transform": 1.0,     # Super Saiyan
        "is_friendly": 1.0,
        "is_naive": 0.8,
        "loves_fighting": 1.0,
        "loves_food": 1.0,
        "from_classic_anime": 1.0,  # 80s/90s anime
        "has_martial_arts": 1.0,
    },

    # === Naruto ===
    "Naruto": {
        "is_dark_brooding": 0.0,
        "is_villain": 0.0,
        "has_rival": 1.0,         # Sasuke
        "has_distinctive_hair": 1.0,  # Blonde spiky
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 1.0,
        "has_tragic_past": 0.8,   # Orphan, outcast
        "is_stoic": 0.0,
        "is_comedic": 0.7,
        "is_friendly": 1.0,
        "is_underdog": 1.0,
        "has_orange_costume": 1.0,
        "is_ninja": 1.0,
        "has_demon_inside": 1.0,  # Nine-tails
        "born_with_powers": 0.0,
        "is_loud": 1.0,
    },

    # === One Piece ===
    "Luffy": {
        "is_dark_brooding": 0.0,
        "is_villain": 0.0,
        "has_rival": 0.5,
        "has_distinctive_hair": 1.0,  # Black messy
        "is_male": 1.0,
        "is_human": 0.8,
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 1.0,
        "has_tragic_past": 0.7,
        "is_stoic": 0.0,
        "is_comedic": 0.9,
        "is_friendly": 1.0,
        "wears_hat": 1.0,         # Straw hat
        "is_pirate": 1.0,
        "is_captain": 1.0,
        "is_naive": 0.7,
        "loves_food": 1.0,
        "is_stretchy": 1.0,       # Rubber powers
        "has_scar": 1.0,
    },

    # === One Punch Man ===
    "Saitama": {
        "is_dark_brooding": 0.0,
        "is_villain": 0.0,
        "has_rival": 0.3,
        "has_distinctive_hair": 0.0,  # Bald!
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "from_comedy_genre": 0.8,
        "is_main_character": 1.0,
        "has_tragic_past": 0.0,
        "is_stoic": 0.5,
        "is_comedic": 0.9,
        "is_bald": 1.0,
        "wears_costume": 1.0,
        "is_overpowered": 1.0,
        "is_parody": 1.0,
    },
    "Genos": {
        "is_dark_brooding": 0.5,
        "is_villain": 0.0,
        "has_rival": 0.2,
        "has_distinctive_hair": 1.0,  # Blonde
        "is_male": 1.0,
        "is_human": 0.3,          # Cyborg
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 0.8,
        "has_tragic_past": 1.0,
        "is_stoic": 0.7,
        "is_comedic": 0.2,
        "is_cyborg": 1.0,
        "has_revenge_motive": 1.0,
        "wears_costume": 0.0,
        "is_apprentice": 1.0,
    },

    # === Other anime characters ===
    "Light Yagami": {
        "is_dark_brooding": 0.8,
        "is_villain": 0.9,
        "has_rival": 1.0,         # L
        "has_distinctive_hair": 0.7,
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 0.5,   # Death Note power
        "from_action_genre": 0.5,
        "is_main_character": 1.0,
        "has_tragic_past": 0.0,
        "is_stoic": 0.6,
        "is_genius": 1.0,
        "is_student": 1.0,
        "is_serial_killer": 1.0,
        "has_god_complex": 1.0,
    },
    "Mikasa Ackerman": {
        "is_dark_brooding": 0.6,
        "is_villain": 0.0,
        "has_rival": 0.2,
        "has_distinctive_hair": 1.0,  # Black short
        "is_male": 0.0,
        "is_human": 1.0,
        "has_superpowers": 0.8,   # Ackerman strength
        "from_action_genre": 1.0,
        "is_main_character": 0.9,
        "has_tragic_past": 1.0,
        "is_stoic": 0.8,
        "is_protective": 1.0,
        "wears_scarf": 1.0,
        "is_soldier": 1.0,
    },
    "Levi Ackerman": {
        "is_dark_brooding": 0.8,
        "is_villain": 0.0,
        "has_rival": 0.3,
        "has_distinctive_hair": 1.0,  # Black undercut
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 0.8,
        "from_action_genre": 1.0,
        "is_main_character": 0.8,
        "has_tragic_past": 1.0,
        "is_stoic": 1.0,
        "is_soldier": 1.0,
        "is_short": 1.0,
        "is_captain": 1.0,
        "is_clean_freak": 1.0,
    },
    "All Might": {
        "is_dark_brooding": 0.0,
        "is_villain": 0.0,
        "has_rival": 0.3,
        "has_distinctive_hair": 1.0,  # Blonde, antenna-like
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 0.7,
        "has_tragic_past": 0.6,
        "is_stoic": 0.0,
        "is_comedic": 0.4,
        "is_mentor": 1.0,
        "wears_costume": 1.0,
        "is_muscular": 1.0,
        "is_symbol": 1.0,        # Symbol of Peace
        "can_transform": 1.0,
    },
    "Satoru Gojo": {
        "is_dark_brooding": 0.3,
        "is_villain": 0.0,
        "has_rival": 0.5,
        "has_distinctive_hair": 1.0,  # White spiky
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 0.8,
        "has_tragic_past": 0.5,
        "is_stoic": 0.0,
        "is_comedic": 0.6,
        "is_mentor": 1.0,
        "wears_blindfold": 1.0,
        "is_overpowered": 1.0,
        "is_arrogant": 0.7,
    },
    "Pikachu": {
        "is_dark_brooding": 0.0,
        "is_villain": 0.0,
        "has_rival": 0.0,
        "has_distinctive_hair": 0.0,
        "is_male": 0.5,
        "is_human": 0.0,
        "has_superpowers": 1.0,
        "from_action_genre": 0.7,
        "is_main_character": 1.0,
        "has_tragic_past": 0.0,
        "is_stoic": 0.0,
        "is_comedic": 0.6,
        "is_cute": 1.0,
        "is_animal": 1.0,
        "has_electric_powers": 1.0,
        "is_mascot": 1.0,
        "is_yellow": 1.0,
        "is_pet": 1.0,
    },
    "Ash Ketchum": {
        "is_dark_brooding": 0.0,
        "is_villain": 0.0,
        "has_rival": 1.0,
        "has_distinctive_hair": 1.0,
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 0.0,
        "from_action_genre": 0.7,
        "is_main_character": 1.0,
        "has_tragic_past": 0.0,
        "is_stoic": 0.0,
        "is_comedic": 0.5,
        "is_young": 1.0,
        "wears_hat": 1.0,
        "is_trainer": 1.0,
        "is_determined": 1.0,
    },
    "Sailor Moon": {
        "is_dark_brooding": 0.0,
        "is_villain": 0.0,
        "has_rival": 0.3,
        "has_distinctive_hair": 1.0,  # Blonde pigtails
        "is_male": 0.0,
        "is_human": 0.8,
        "has_superpowers": 1.0,
        "from_action_genre": 0.7,
        "is_main_character": 1.0,
        "has_tragic_past": 0.3,
        "is_stoic": 0.0,
        "is_comedic": 0.7,
        "wears_costume": 1.0,
        "is_magical_girl": 1.0,
        "has_team": 1.0,
        "is_princess": 1.0,
        "from_classic_anime": 1.0,
    },
    "Edward Elric": {
        "is_dark_brooding": 0.5,
        "is_villain": 0.0,
        "has_rival": 0.4,
        "has_distinctive_hair": 1.0,  # Blonde braid
        "is_male": 1.0,
        "is_human": 0.8,          # Automail
        "has_superpowers": 1.0,
        "from_action_genre": 1.0,
        "is_main_character": 1.0,
        "has_tragic_past": 1.0,
        "is_stoic": 0.3,
        "is_comedic": 0.5,
        "is_short": 1.0,
        "uses_alchemy": 1.0,
        "has_prosthetic": 1.0,
        "is_genius": 1.0,
        "has_sibling": 1.0,
    },
    "Spike Spiegel": {
        "is_dark_brooding": 0.7,
        "is_villain": 0.0,
        "has_rival": 0.5,
        "has_distinctive_hair": 1.0,  # Green afro
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 0.0,
        "from_action_genre": 1.0,
        "is_main_character": 1.0,
        "has_tragic_past": 0.9,
        "is_stoic": 0.6,
        "is_comedic": 0.4,
        "is_bounty_hunter": 1.0,
        "has_martial_arts": 1.0,
        "is_cool": 1.0,
        "from_classic_anime": 1.0,
        "is_adult": 1.0,
    },
    "Lelouch": {
        "is_dark_brooding": 0.9,
        "is_villain": 0.7,
        "has_rival": 0.8,
        "has_distinctive_hair": 1.0,
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 1.0,    # Geass
        "from_action_genre": 1.0,
        "is_main_character": 1.0,
        "has_tragic_past": 0.8,
        "is_stoic": 0.6,
        "is_genius": 1.0,
        "is_royalty": 1.0,
        "pilots_mech": 1.0,
        "wears_mask": 0.8,        # Zero mask
        "is_antihero": 1.0,
    },
    "Kirito": {
        "is_dark_brooding": 0.4,
        "is_villain": 0.0,
        "has_rival": 0.3,
        "has_distinctive_hair": 1.0,  # Black
        "is_male": 1.0,
        "is_human": 1.0,
        "has_superpowers": 0.5,
        "from_action_genre": 1.0,
        "is_main_character": 1.0,
        "has_tragic_past": 0.5,
        "is_stoic": 0.5,
        "is_gamer": 1.0,
        "uses_sword": 1.0,
        "is_overpowered": 0.8,
        "wears_black": 1.0,
        "is_trapped_in_game": 1.0,
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
    for name, attrs in ANIME_FIXES.items():
        if name not in entity_map:
            print(f"  Entity not found: {name}")
            continue

        eid = entity_map[name]

        for attr_key, value in attrs.items():
            if attr_key not in attr_map:
                # Skip attributes not in schema
                continue

            attr_id = attr_map[attr_key]
            conn.execute("""
                INSERT INTO entity_attributes (entity_id, attribute_id, value)
                VALUES (?, ?, ?)
                ON CONFLICT(entity_id, attribute_id) DO UPDATE SET value = ?
            """, (eid, attr_id, value, value))

        updated += 1
        print(f"  Fixed: {name}")

    conn.commit()
    conn.close()
    print(f"\nDone! Updated {updated} anime characters.")


if __name__ == "__main__":
    main()
