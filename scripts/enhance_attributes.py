#!/usr/bin/env python3
"""Enhance entity attributes by extracting more Wikidata properties.

This script improves accuracy by adding entity-specific attributes
instead of relying on generic category templates.
"""

import json
import sqlite3
import time
import urllib.parse
import urllib.request
from pathlib import Path

WIKIDATA_API = "https://www.wikidata.org/w/api.php"

# Award QIDs to attribute mapping
AWARDS = {
    "Q19020": "won_oscar",      # Academy Award
    "Q41254": "won_grammy",     # Grammy
    "Q7191": "won_nobel",       # Nobel Prize
    "Q35637": "olympic_medalist",  # Olympic medal
    "Q215380": "cultural_icon",  # Grammy Lifetime Achievement
    "Q1364556": "cultural_icon",  # Rock and Roll Hall of Fame
}

# Occupation QIDs to attributes
OCCUPATIONS = {
    # Actors by type
    "Q33999": {"from_movie": 0.95, "from_action_genre": 0.4},  # actor
    "Q10800557": {"from_movie": 0.95},  # film actor
    "Q2405480": {"from_comedy_genre": 0.8, "is_comedic": 0.7},  # comedian
    "Q245068": {"from_comedy_genre": 0.9},  # stand-up comedian

    # Musicians by type
    "Q177220": {"from_music": 1.0, "is_action_hero": 0.0},  # singer
    "Q639669": {"from_music": 1.0},  # singer-songwriter
    "Q36834": {"from_music": 1.0},  # composer
    "Q855091": {"from_music": 1.0},  # guitarist
    "Q386854": {"from_music": 1.0},  # drummer
    "Q66763670": {"from_music": 1.0},  # hip hop musician
    "Q2643890": {"from_music": 1.0},  # rapper
    "Q753110": {"from_music": 1.0},  # rock musician

    # Athletes by sport
    "Q937857": {"from_sport": 1.0, "world_champion": 0.3},  # football player
    "Q3665646": {"from_sport": 1.0},  # basketball player
    "Q10833314": {"from_sport": 1.0},  # tennis player
    "Q11338576": {"from_sport": 1.0},  # boxer
    "Q2309784": {"from_sport": 1.0},  # MMA fighter
    "Q10873124": {"from_sport": 1.0, "olympic_medalist": 0.4},  # swimmer
    "Q11513337": {"from_sport": 1.0, "olympic_medalist": 0.5},  # athletics competitor

    # Scientists
    "Q901": {"from_science": 1.0, "has_glasses": 0.4},  # scientist
    "Q169470": {"from_science": 1.0},  # physicist
    "Q593644": {"from_science": 1.0},  # chemist
    "Q864503": {"from_science": 1.0},  # biologist
    "Q170790": {"from_science": 1.0},  # mathematician

    # Business
    "Q131524": {"from_business": 1.0, "is_wealthy": 0.7},  # entrepreneur
    "Q43845": {"from_business": 1.0, "is_wealthy": 0.9, "billionaire": 0.5},  # businessperson

    # Writers
    "Q36180": {"from_book": 1.0, "from_literature": 1.0},  # writer
    "Q6625963": {"from_book": 1.0, "from_literature": 1.0},  # novelist
    "Q49757": {"from_book": 1.0, "from_literature": 1.0},  # poet
    "Q4853732": {"from_horror_genre": 0.7},  # horror writer

    # Directors
    "Q2526255": {"from_movie": 0.9},  # film director

    # Politics
    "Q82955": {"from_politics": 1.0, "is_leader": 0.6},  # politician
    "Q30461": {"from_politics": 1.0, "is_leader": 0.9},  # president
    "Q372436": {"from_politics": 1.0, "is_leader": 0.7},  # statesman
}

# Genre QIDs to attributes
GENRES = {
    # Film genres
    "Q188473": {"from_action_genre": 0.9},  # action film
    "Q157443": {"from_comedy_genre": 0.9},  # comedy film
    "Q130232": {"from_drama_genre": 0.9},  # drama film
    "Q200092": {"from_horror_genre": 0.9},  # horror film
    "Q471839": {"from_scifi_genre": 0.9},  # science fiction film

    # Music genres
    "Q11399": {"from_action_genre": 0.3},  # rock
    "Q37073": {"from_action_genre": 0.2},  # pop
    "Q11401": {"is_dark_brooding": 0.5},  # jazz
    "Q9759": {"is_dark_brooding": 0.3},  # classical
    "Q6010": {"from_action_genre": 0.4},  # hip hop
    "Q38848": {"is_dark_brooding": 0.7},  # metal
    "Q131272": {"is_dark_brooding": 0.4},  # blues
    "Q83440": {"is_dark_brooding": 0.2},  # country
}


def api_request(params: dict) -> dict:
    """Make Wikidata API request."""
    params["format"] = "json"
    url = f"{WIKIDATA_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "AkinatorEnhancer/1.0"})

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            if attempt < 2:
                time.sleep(1)
    return {}


def get_entity_claims(qid: str) -> dict:
    """Get entity claims from Wikidata."""
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "props": "claims",
    }
    result = api_request(params)
    return result.get("entities", {}).get(qid, {}).get("claims", {})


def extract_enhanced_attrs(claims: dict) -> dict:
    """Extract enhanced attributes from Wikidata claims."""
    attrs = {}

    # P166 - Awards received
    for claim in claims.get("P166", [])[:10]:
        try:
            award_qid = claim["mainsnak"]["datavalue"]["value"]["id"]
            if award_qid in AWARDS:
                attrs[AWARDS[award_qid]] = 1.0
        except:
            pass

    # P106 - Occupation (more specific)
    for claim in claims.get("P106", [])[:5]:
        try:
            occ_qid = claim["mainsnak"]["datavalue"]["value"]["id"]
            if occ_qid in OCCUPATIONS:
                for attr, val in OCCUPATIONS[occ_qid].items():
                    # Keep higher values
                    attrs[attr] = max(attrs.get(attr, 0), val)
        except:
            pass

    # P136 - Genre
    for claim in claims.get("P136", [])[:5]:
        try:
            genre_qid = claim["mainsnak"]["datavalue"]["value"]["id"]
            if genre_qid in GENRES:
                for attr, val in GENRES[genre_qid].items():
                    attrs[attr] = max(attrs.get(attr, 0), val)
        except:
            pass

    # P21 - Gender
    if "P21" in claims:
        try:
            gender_id = claims["P21"][0]["mainsnak"]["datavalue"]["value"]["id"]
            attrs["is_male"] = 1.0 if gender_id == "Q6581097" else 0.0
        except:
            pass

    # P569 - Birth date -> era attributes
    if "P569" in claims:
        try:
            time_val = claims["P569"][0]["mainsnak"]["datavalue"]["value"]["time"]
            birth_year = int(time_val[1:5])

            # Clear any existing era attributes first
            attrs["born_before_1950"] = 0.0
            attrs["born_1950_1970"] = 0.0
            attrs["born_1970_1990"] = 0.0
            attrs["born_after_1990"] = 0.0

            if birth_year < 1950:
                attrs["born_before_1950"] = 1.0
            elif birth_year < 1970:
                attrs["born_1950_1970"] = 1.0
            elif birth_year < 1990:
                attrs["born_1970_1990"] = 1.0
            else:
                attrs["born_after_1990"] = 1.0

            # Century
            if birth_year < 1900:
                attrs["era_modern"] = 1.0
            elif birth_year < 2000:
                attrs["era_20th_century"] = 1.0
            else:
                attrs["era_21st_century"] = 1.0

        except:
            pass

    # P570 - Death date
    if "P570" in claims:
        attrs["is_alive"] = 0.0
        try:
            death_time = claims["P570"][0]["mainsnak"]["datavalue"]["value"]["time"]
            death_year = int(death_time[1:5])

            if "P569" in claims:
                birth_time = claims["P569"][0]["mainsnak"]["datavalue"]["value"]["time"]
                birth_year = int(birth_time[1:5])
                if death_year - birth_year < 45:
                    attrs["died_young"] = 1.0
        except:
            pass

    # P27 - Country of citizenship
    country_attrs = {
        "Q30": {"from_usa": 1.0},
        "Q145": {"from_uk": 1.0, "from_europe": 1.0},
        "Q142": {"from_europe": 1.0},
        "Q183": {"from_europe": 1.0},
        "Q159": {"from_russia": 1.0, "from_europe": 0.5},
        "Q17": {"from_japan": 1.0, "from_asia": 1.0},
        "Q148": {"from_china": 1.0, "from_asia": 1.0},
        "Q668": {"from_india": 1.0, "from_asia": 1.0},
        "Q155": {"from_south_america": 1.0},
        "Q414": {"from_south_america": 1.0},
        "Q96": {"from_south_america": 1.0},  # Mexico
        "Q29": {"from_europe": 1.0},  # Spain
        "Q38": {"from_europe": 1.0},  # Italy
    }

    if "P27" in claims:
        try:
            country_qid = claims["P27"][0]["mainsnak"]["datavalue"]["value"]["id"]
            if country_qid in country_attrs:
                attrs.update(country_attrs[country_qid])
        except:
            pass

    # P1411 - Nominated for (indicates prominence)
    if len(claims.get("P1411", [])) > 3:
        attrs["cultural_icon"] = max(attrs.get("cultural_icon", 0), 0.5)

    # P2048 - Height (for athletes)
    if "P2048" in claims:
        try:
            height = claims["P2048"][0]["mainsnak"]["datavalue"]["value"]["amount"]
            height_cm = float(height.lstrip("+"))
            if height_cm > 190:
                attrs["known_for_physique"] = max(attrs.get("known_for_physique", 0), 0.6)
        except:
            pass

    return attrs


def main():
    db_path = Path(__file__).parent.parent / "data" / "collected.db"

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Get all entities with wikidata descriptions
    entities = conn.execute("""
        SELECT id, name, description FROM entities
        WHERE description LIKE 'wikidata:%'
    """).fetchall()

    print(f"Enhancing {len(entities)} entities...")

    # Get attribute IDs
    attr_map = {}
    for row in conn.execute("SELECT id, key FROM attributes"):
        attr_map[row["key"]] = row["id"]

    enhanced = 0
    for i, entity in enumerate(entities):
        eid = entity["id"]
        name = entity["name"]
        qid = entity["description"].replace("wikidata:", "")

        if not qid.startswith("Q"):
            continue

        # Get Wikidata claims
        claims = get_entity_claims(qid)
        if not claims:
            continue

        # Extract enhanced attributes
        new_attrs = extract_enhanced_attrs(claims)

        if not new_attrs:
            continue

        # Update attributes in DB
        for attr_key, value in new_attrs.items():
            if attr_key not in attr_map:
                continue

            attr_id = attr_map[attr_key]

            # Update or insert
            conn.execute("""
                INSERT INTO entity_attributes (entity_id, attribute_id, value)
                VALUES (?, ?, ?)
                ON CONFLICT(entity_id, attribute_id) DO UPDATE SET value = ?
            """, (eid, attr_id, value, value))

        conn.commit()
        enhanced += 1

        if (i + 1) % 50 == 0:
            print(f"Progress: {i+1}/{len(entities)} (enhanced {enhanced})")

        # Rate limiting
        time.sleep(0.3)

    conn.close()
    print(f"\nDone! Enhanced {enhanced} entities.")


if __name__ == "__main__":
    main()
