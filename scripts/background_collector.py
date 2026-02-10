#!/usr/bin/env python3
"""Background data collector for Akinator.

This script runs continuously in the background, collecting entity data
from various sources and enriching the database.

Usage:
    # Start collector
    nohup python scripts/background_collector.py > logs/collector.log 2>&1 &

    # Or with specific settings
    python scripts/background_collector.py --db data/collected.db --interval 60

    # Check status
    tail -f logs/collector.log
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import random
import signal
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from akinator.db.repository import Repository

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("collector")

# Wikidata API
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "AkinatorCollector/1.0 (educational project)"

# Graceful shutdown flag
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    logger.info("Shutdown requested, finishing current batch...")
    shutdown_requested = True


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# ═══════════════════════════════════════════════════════════════════════════════
# EXPANDED ATTRIBUTE SYSTEM (100+ potential differentiating attributes)
# ═══════════════════════════════════════════════════════════════════════════════

ATTRIBUTES = [
    # Identity (5)
    ("is_fictional", "Вымышленный персонаж?", "Is fictional?", "identity"),
    ("is_male", "Мужчина?", "Is male?", "identity"),
    ("is_human", "Человек?", "Is human?", "identity"),
    ("is_alive", "Жив?", "Is alive?", "identity"),
    ("is_adult", "Взрослый?", "Is adult?", "identity"),

    # Media/Domain (20)
    ("from_movie", "Связан с кино?", "Related to movies?", "media"),
    ("from_tv_series", "Связан с сериалами?", "Related to TV?", "media"),
    ("from_anime", "Связан с аниме?", "Related to anime?", "media"),
    ("from_game", "Связан с играми?", "Related to games?", "media"),
    ("from_book", "Связан с книгами?", "Related to books?", "media"),
    ("from_comics", "Связан с комиксами?", "Related to comics?", "media"),
    ("from_music", "Связан с музыкой?", "Related to music?", "media"),
    ("from_sport", "Связан со спортом?", "Related to sports?", "media"),
    ("from_politics", "Связан с политикой?", "Related to politics?", "media"),
    ("from_science", "Связан с наукой?", "Related to science?", "media"),
    ("from_history", "Историческая личность?", "Historical figure?", "media"),
    ("from_literature", "Связан с литературой?", "Related to literature?", "media"),
    ("from_art", "Связан с искусством?", "Related to art?", "media"),
    ("from_business", "Связан с бизнесом?", "Related to business?", "media"),
    ("from_internet", "Интернет-знаменитость?", "Internet celebrity?", "media"),
    ("from_action_genre", "Жанр экшн?", "Action genre?", "media"),
    ("from_comedy_genre", "Жанр комедия?", "Comedy genre?", "media"),
    ("from_drama_genre", "Жанр драма?", "Drama genre?", "media"),
    ("from_horror_genre", "Жанр ужасы?", "Horror genre?", "media"),
    ("from_scifi_genre", "Жанр фантастика?", "Sci-fi genre?", "media"),

    # Geography (15)
    ("from_usa", "Из США?", "From USA?", "geography"),
    ("from_uk", "Из Великобритании?", "From UK?", "geography"),
    ("from_europe", "Из Европы?", "From Europe?", "geography"),
    ("from_russia", "Из России?", "From Russia?", "geography"),
    ("from_asia", "Из Азии?", "From Asia?", "geography"),
    ("from_japan", "Из Японии?", "From Japan?", "geography"),
    ("from_china", "Из Китая?", "From China?", "geography"),
    ("from_india", "Из Индии?", "From India?", "geography"),
    ("from_korea", "Из Кореи?", "From Korea?", "geography"),
    ("from_france", "Из Франции?", "From France?", "geography"),
    ("from_germany", "Из Германии?", "From Germany?", "geography"),
    ("from_south_america", "Из Южной Америки?", "From South America?", "geography"),
    ("from_africa", "Из Африки?", "From Africa?", "geography"),
    ("from_middle_east", "С Ближнего Востока?", "From Middle East?", "geography"),
    ("from_oceania", "Из Океании?", "From Oceania?", "geography"),

    # Era (10)
    ("era_ancient", "Древность?", "Ancient era?", "era"),
    ("era_medieval", "Средневековье?", "Medieval era?", "era"),
    ("era_modern", "Новое время?", "Modern era?", "era"),
    ("era_20th_century", "20 век?", "20th century?", "era"),
    ("era_21st_century", "21 век?", "21st century?", "era"),
    ("born_before_1950", "Родился до 1950?", "Born before 1950?", "era"),
    ("born_1950_1970", "Родился 1950-1970?", "Born 1950-1970?", "era"),
    ("born_1970_1990", "Родился 1970-1990?", "Born 1970-1990?", "era"),
    ("born_after_1990", "Родился после 1990?", "Born after 1990?", "era"),
    ("active_now", "Активен сейчас?", "Active now?", "era"),

    # Traits/Appearance (20)
    ("has_superpower", "Есть суперсилы?", "Has superpowers?", "traits"),
    ("is_villain", "Злодей?", "Is villain?", "traits"),
    ("is_leader", "Лидер/глава?", "Is leader?", "traits"),
    ("is_wealthy", "Богатый?", "Is wealthy?", "traits"),
    ("is_comedic", "Комедийный?", "Is comedic?", "traits"),
    ("is_dark_brooding", "Мрачный?", "Is dark/brooding?", "traits"),
    ("is_action_hero", "Герой боевика?", "Action hero?", "traits"),
    ("is_romantic_lead", "Романтический герой?", "Romantic lead?", "traits"),
    ("is_child_friendly", "Детский персонаж?", "Child-friendly?", "traits"),
    ("has_famous_catchphrase", "Известная фраза?", "Famous catchphrase?", "traits"),
    ("wears_uniform", "Носит форму?", "Wears uniform?", "traits"),
    ("wears_mask", "Носит маску?", "Wears mask?", "traits"),
    ("has_armor", "Носит броню?", "Wears armor?", "traits"),
    ("has_facial_hair", "Борода/усы?", "Has facial hair?", "traits"),
    ("has_glasses", "Носит очки?", "Wears glasses?", "traits"),
    ("is_bald", "Лысый?", "Is bald?", "traits"),
    ("has_distinctive_voice", "Особый голос?", "Distinctive voice?", "traits"),
    ("known_for_physique", "Известен телосложением?", "Known for physique?", "traits"),
    ("has_tattoos", "Есть татуировки?", "Has tattoos?", "traits"),
    ("distinctive_hair", "Особая причёска?", "Distinctive hair?", "traits"),

    # Achievement/Fame (10)
    ("won_oscar", "Выиграл Оскар?", "Won Oscar?", "achievement"),
    ("won_grammy", "Выиграл Грэмми?", "Won Grammy?", "achievement"),
    ("won_nobel", "Выиграл Нобель?", "Won Nobel?", "achievement"),
    ("olympic_medalist", "Олимпийский медалист?", "Olympic medalist?", "achievement"),
    ("world_champion", "Чемпион мира?", "World champion?", "achievement"),
    ("billionaire", "Миллиардер?", "Billionaire?", "achievement"),
    ("controversial", "Скандальный?", "Controversial?", "achievement"),
    ("died_young", "Умер молодым?", "Died young?", "achievement"),
    ("cultural_icon", "Культурная икона?", "Cultural icon?", "achievement"),
    ("hall_of_fame", "В зале славы?", "Hall of fame?", "achievement"),
]

# Profession QID to detailed category
PROFESSION_CATEGORIES = {
    # Actors - subdivided
    "Q33999": "actor_generic",
    "Q10800557": "actor_film",
    "Q10798782": "actor_tv",
    "Q2405480": "actor_voice",
    "Q2259451": "actor_stage",

    # Musicians - subdivided by genre
    "Q177220": "musician_singer",
    "Q639669": "musician_generic",
    "Q753110": "musician_rapper",
    "Q36834": "musician_composer",
    "Q486748": "musician_pianist",
    "Q855091": "musician_guitarist",
    "Q386854": "musician_drummer",
    "Q158852": "musician_dj",

    # Athletes - by sport
    "Q937857": "athlete_football",
    "Q3665646": "athlete_basketball",
    "Q13590141": "athlete_tennis",
    "Q11338576": "athlete_boxing",
    "Q10843263": "athlete_racing",
    "Q18581305": "athlete_hockey",
    "Q10871364": "athlete_baseball",
    "Q11513337": "athlete_track",
    "Q13141064": "athlete_golf",
    "Q10833314": "athlete_swimming",

    # Politicians
    "Q82955": "politician_generic",
    "Q30461": "politician_president",
    "Q14915627": "politician_chancellor",
    "Q193391": "politician_monarch",

    # Writers
    "Q36180": "writer_generic",
    "Q49757": "writer_poet",
    "Q4853732": "writer_novelist",
    "Q28389": "writer_screenwriter",

    # Scientists
    "Q901": "scientist_generic",
    "Q169470": "scientist_physicist",
    "Q593644": "scientist_chemist",
    "Q864503": "scientist_biologist",

    # Directors/Producers
    "Q2526255": "director_film",
    "Q3282637": "producer_film",
    "Q578109": "director_tv",

    # Other
    "Q15981151": "internet_youtuber",
    "Q2259532": "internet_influencer",
    "Q1028181": "artist_painter",
    "Q1281618": "artist_sculptor",
    "Q3387717": "model",
    "Q18844224": "comedian",
}

# Category to attribute templates (detailed)
CATEGORY_TEMPLATES = {
    "actor_film": {
        "is_fictional": 0.0, "is_human": 1.0, "from_movie": 1.0, "from_tv_series": 0.4,
        "is_wealthy": 0.6, "from_drama_genre": 0.5, "from_action_genre": 0.4,
    },
    "actor_tv": {
        "is_fictional": 0.0, "is_human": 1.0, "from_movie": 0.3, "from_tv_series": 1.0,
        "is_wealthy": 0.4,
    },
    "actor_voice": {
        "is_fictional": 0.0, "is_human": 1.0, "from_movie": 0.6, "from_anime": 0.4,
        "has_distinctive_voice": 0.9,
    },
    "musician_singer": {
        "is_fictional": 0.0, "is_human": 1.0, "from_music": 1.0, "from_movie": 0.2,
        "has_famous_catchphrase": 0.4, "cultural_icon": 0.3,
    },
    "musician_rapper": {
        "is_fictional": 0.0, "is_human": 1.0, "from_music": 1.0, "from_usa": 0.7,
        "has_tattoos": 0.6, "controversial": 0.4, "is_wealthy": 0.5,
    },
    "musician_composer": {
        "is_fictional": 0.0, "is_human": 1.0, "from_music": 1.0, "from_europe": 0.7,
        "from_history": 0.6, "cultural_icon": 0.5,
    },
    "athlete_football": {
        "is_fictional": 0.0, "is_human": 1.0, "from_sport": 1.0, "wears_uniform": 1.0,
        "from_europe": 0.5, "from_south_america": 0.3, "known_for_physique": 0.6,
    },
    "athlete_basketball": {
        "is_fictional": 0.0, "is_human": 1.0, "from_sport": 1.0, "wears_uniform": 1.0,
        "from_usa": 0.8, "known_for_physique": 0.7, "is_wealthy": 0.6,
    },
    "athlete_boxing": {
        "is_fictional": 0.0, "is_human": 1.0, "from_sport": 1.0,
        "known_for_physique": 0.9, "is_action_hero": 0.3, "controversial": 0.4,
    },
    "politician_president": {
        "is_fictional": 0.0, "is_human": 1.0, "from_politics": 1.0, "is_leader": 1.0,
        "has_famous_catchphrase": 0.5, "controversial": 0.4, "is_wealthy": 0.5,
    },
    "politician_monarch": {
        "is_fictional": 0.0, "is_human": 1.0, "from_politics": 0.8, "is_leader": 1.0,
        "is_wealthy": 0.9, "from_history": 0.6, "cultural_icon": 0.5,
    },
    "writer_novelist": {
        "is_fictional": 0.0, "is_human": 1.0, "from_book": 1.0, "from_literature": 1.0,
        "has_glasses": 0.4, "cultural_icon": 0.3,
    },
    "scientist_physicist": {
        "is_fictional": 0.0, "is_human": 1.0, "from_science": 1.0,
        "has_glasses": 0.5, "won_nobel": 0.2, "cultural_icon": 0.2,
    },
    "internet_youtuber": {
        "is_fictional": 0.0, "is_human": 1.0, "from_internet": 1.0,
        "era_21st_century": 1.0, "born_after_1990": 0.7, "is_comedic": 0.5,
    },
    "director_film": {
        "is_fictional": 0.0, "is_human": 1.0, "from_movie": 1.0,
        "is_wealthy": 0.5, "won_oscar": 0.2, "has_glasses": 0.4,
    },
    "default": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
    },
}

# Country QID to attributes
COUNTRY_ATTRS = {
    "Q30": {"from_usa": 1.0},
    "Q145": {"from_uk": 1.0, "from_europe": 1.0},
    "Q142": {"from_france": 1.0, "from_europe": 1.0},
    "Q183": {"from_germany": 1.0, "from_europe": 1.0},
    "Q159": {"from_russia": 1.0},
    "Q17": {"from_japan": 1.0, "from_asia": 1.0},
    "Q148": {"from_china": 1.0, "from_asia": 1.0},
    "Q668": {"from_india": 1.0, "from_asia": 1.0},
    "Q884": {"from_korea": 1.0, "from_asia": 1.0},
    "Q155": {"from_south_america": 1.0},
    "Q414": {"from_south_america": 1.0},
    "Q408": {"from_oceania": 1.0},
}


# ═══════════════════════════════════════════════════════════════════════════════
# DATA COLLECTION
# ═══════════════════════════════════════════════════════════════════════════════

def api_request(params: dict, max_retries: int = 3) -> dict:
    """Make Wikidata API request with retries."""
    params["format"] = "json"
    url = f"{WIKIDATA_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            logger.warning("API request failed (attempt %d): %s", attempt + 1, e)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return {}


def search_entities(query: str, limit: int = 10) -> list[dict]:
    """Search for entities by name."""
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "limit": limit,
        "type": "item",
    }
    result = api_request(params)
    return result.get("search", [])


def get_entity_details(qids: list[str]) -> dict:
    """Get detailed entity information."""
    if not qids:
        return {}

    batch_size = 50
    all_entities = {}

    for i in range(0, len(qids), batch_size):
        batch = qids[i:i + batch_size]
        params = {
            "action": "wbgetentities",
            "ids": "|".join(batch),
            "props": "labels|descriptions|claims|sitelinks",
            "languages": "en|ru",
        }
        result = api_request(params)
        all_entities.update(result.get("entities", {}))
        time.sleep(0.3)

    return all_entities


def extract_claims(entity: dict) -> dict:
    """Extract relevant claims from entity."""
    claims = entity.get("claims", {})
    result = {}

    # Birth year (P569)
    if "P569" in claims:
        try:
            time_val = claims["P569"][0]["mainsnak"]["datavalue"]["value"]["time"]
            result["birth_year"] = int(time_val[1:5])
        except:
            pass

    # Death year (P570)
    if "P570" in claims:
        try:
            time_val = claims["P570"][0]["mainsnak"]["datavalue"]["value"]["time"]
            result["death_year"] = int(time_val[1:5])
        except:
            pass

    # Gender (P21)
    if "P21" in claims:
        try:
            gender_id = claims["P21"][0]["mainsnak"]["datavalue"]["value"]["id"]
            result["is_male"] = 1.0 if gender_id == "Q6581097" else 0.0
        except:
            pass

    # Country (P27)
    if "P27" in claims:
        try:
            result["country_qid"] = claims["P27"][0]["mainsnak"]["datavalue"]["value"]["id"]
        except:
            pass

    # Occupations (P106)
    result["occupations"] = []
    if "P106" in claims:
        for claim in claims["P106"][:5]:
            try:
                occ_id = claim["mainsnak"]["datavalue"]["value"]["id"]
                result["occupations"].append(occ_id)
            except:
                pass

    # Instance of (P31) - for fictional detection
    result["instance_of"] = []
    if "P31" in claims:
        for claim in claims["P31"][:5]:
            try:
                type_id = claim["mainsnak"]["datavalue"]["value"]["id"]
                result["instance_of"].append(type_id)
            except:
                pass

    # Awards (P166) - for achievement attrs
    result["has_awards"] = "P166" in claims

    # Sitelinks count (popularity indicator)
    result["sitelinks"] = len(entity.get("sitelinks", {}))

    return result


def build_attributes(claims: dict) -> dict[str, float]:
    """Build attribute dictionary from claims."""
    attrs = {"is_human": 1.0, "is_adult": 1.0}

    # Fictional detection
    fictional_types = {"Q95074", "Q15632617", "Q15773317", "Q4271324"}
    is_fictional = bool(set(claims.get("instance_of", [])) & fictional_types)
    attrs["is_fictional"] = 1.0 if is_fictional else 0.0

    # Only Q5 (human) is a real person
    if "Q5" not in claims.get("instance_of", []) and not is_fictional:
        return {}  # Not a valid entity

    # Gender
    if "is_male" in claims:
        attrs["is_male"] = claims["is_male"]

    # Category from occupations
    category = "default"
    for occ_qid in claims.get("occupations", []):
        if occ_qid in PROFESSION_CATEGORIES:
            category = PROFESSION_CATEGORIES[occ_qid]
            break

    # Apply category template
    template = CATEGORY_TEMPLATES.get(category, CATEGORY_TEMPLATES["default"])
    for key, value in template.items():
        attrs[key] = value

    # Country
    country_qid = claims.get("country_qid")
    if country_qid and country_qid in COUNTRY_ATTRS:
        for key, value in COUNTRY_ATTRS[country_qid].items():
            if value > attrs.get(key, 0):
                attrs[key] = value

    # Birth era
    birth_year = claims.get("birth_year")
    if birth_year:
        if birth_year < 1950:
            attrs["born_before_1950"] = 1.0
        elif birth_year < 1970:
            attrs["born_1950_1970"] = 1.0
        elif birth_year < 1990:
            attrs["born_1970_1990"] = 1.0
        else:
            attrs["born_after_1990"] = 1.0

        if birth_year < 500:
            attrs["era_ancient"] = 1.0
            attrs["from_history"] = 1.0
        elif birth_year < 1500:
            attrs["era_medieval"] = 1.0
            attrs["from_history"] = 1.0
        elif birth_year < 1900:
            attrs["era_modern"] = 1.0
        elif birth_year < 2000:
            attrs["era_20th_century"] = 1.0
        else:
            attrs["era_21st_century"] = 1.0

    # Alive status
    if claims.get("death_year"):
        attrs["is_alive"] = 0.0
        if claims.get("death_year") - claims.get("birth_year", 0) < 50:
            attrs["died_young"] = 0.8
    elif birth_year and birth_year < 1940:
        attrs["is_alive"] = 0.1
    else:
        attrs["is_alive"] = 0.9
        attrs["active_now"] = 0.7

    # Awards/achievements
    if claims.get("has_awards"):
        attrs["cultural_icon"] = max(attrs.get("cultural_icon", 0), 0.3)

    # Popularity indicator from sitelinks
    sitelinks = claims.get("sitelinks", 0)
    if sitelinks > 100:
        attrs["cultural_icon"] = max(attrs.get("cultural_icon", 0), 0.5)

    return attrs


# ═══════════════════════════════════════════════════════════════════════════════
# SEARCH SEEDS (diverse categories)
# ═══════════════════════════════════════════════════════════════════════════════

SEARCH_SEEDS = {
    "actors_hollywood": [
        "Tom Hanks", "Leonardo DiCaprio", "Brad Pitt", "Meryl Streep",
        "Denzel Washington", "Morgan Freeman", "Scarlett Johansson",
    ],
    "actors_international": [
        "Jackie Chan", "Shah Rukh Khan", "Gong Li", "Antonio Banderas",
        "Jean Reno", "Mads Mikkelsen", "Penelope Cruz",
    ],
    "musicians_pop": [
        "Michael Jackson", "Madonna", "Beyonce", "Taylor Swift",
        "Lady Gaga", "Rihanna", "Justin Bieber",
    ],
    "musicians_rock": [
        "Freddie Mercury", "John Lennon", "Mick Jagger", "Kurt Cobain",
        "David Bowie", "Ozzy Osbourne", "Robert Plant",
    ],
    "musicians_hiphop": [
        "Eminem", "Jay-Z", "Kanye West", "Drake", "Snoop Dogg",
        "Tupac Shakur", "Kendrick Lamar",
    ],
    "athletes_football": [
        "Lionel Messi", "Cristiano Ronaldo", "Pele", "Diego Maradona",
        "Zinedine Zidane", "Neymar", "Kylian Mbappe",
    ],
    "athletes_basketball": [
        "Michael Jordan", "LeBron James", "Kobe Bryant", "Shaquille O'Neal",
        "Stephen Curry", "Magic Johnson", "Kareem Abdul-Jabbar",
    ],
    "athletes_other": [
        "Muhammad Ali", "Mike Tyson", "Usain Bolt", "Roger Federer",
        "Tiger Woods", "Michael Phelps", "Serena Williams",
    ],
    "politicians": [
        "Barack Obama", "Donald Trump", "Vladimir Putin", "Angela Merkel",
        "Winston Churchill", "Abraham Lincoln", "Napoleon Bonaparte",
    ],
    "scientists": [
        "Albert Einstein", "Stephen Hawking", "Marie Curie", "Nikola Tesla",
        "Isaac Newton", "Charles Darwin", "Galileo Galilei",
    ],
    "writers": [
        "William Shakespeare", "Stephen King", "JK Rowling", "Leo Tolstoy",
        "Ernest Hemingway", "Agatha Christie", "George Orwell",
    ],
    "fictional_marvel": [
        "Spider-Man", "Iron Man", "Captain America", "Thor", "Hulk",
        "Wolverine", "Deadpool", "Black Panther",
    ],
    "fictional_dc": [
        "Batman", "Superman", "Wonder Woman", "Joker", "Flash",
        "Aquaman", "Harley Quinn",
    ],
    "fictional_anime": [
        "Goku", "Naruto", "Luffy", "Pikachu", "Saitama",
        "Light Yagami", "Eren Jaeger",
    ],
    "fictional_disney": [
        "Mickey Mouse", "Elsa", "Simba", "Woody", "Buzz Lightyear",
        "Ariel", "Mulan",
    ],
    "fictional_games": [
        "Mario", "Link", "Sonic", "Kratos", "Master Chief",
        "Lara Croft", "Geralt of Rivia",
    ],
    "youtubers": [
        "PewDiePie", "MrBeast", "Markiplier", "Ninja", "KSI",
        "Logan Paul", "Emma Chamberlain",
    ],
}


async def collect_batch(
    repo: Repository,
    attr_ids: dict[str, int],
    existing_names: set[str],
    category: str,
    seeds: list[str],
) -> int:
    """Collect a batch of entities from one category."""
    count = 0

    for seed in seeds:
        if shutdown_requested:
            break

        logger.debug("Searching: %s", seed)
        results = search_entities(seed, limit=5)

        # Filter - only accept EXACT or very close matches
        qids = []
        seed_lower = seed.lower().strip()
        seed_words = set(seed_lower.split())

        for item in results[:3]:  # Only check first 3 results
            qid = item.get("id", "")
            label = item.get("label", "").lower().strip()
            label_words = set(label.split())

            if not qid:
                continue

            # Exact match
            if label == seed_lower:
                qids.append(qid)
                break  # Found exact match, stop

            # Same words (handles "Messi Lionel" vs "Lionel Messi")
            if seed_words == label_words:
                qids.append(qid)
                break

            # First result is close enough if it starts the same
            if len(qids) == 0 and label.startswith(seed_lower.split()[0]):
                # Check it's not a completely different person (no extra words)
                if len(label_words - seed_words) <= 1:
                    qids.append(qid)

        if not qids:
            continue

        entities = get_entity_details(qids)

        for qid, entity in entities.items():
            labels = entity.get("labels", {})
            en_label = labels.get("en", {}).get("value", "")
            ru_label = labels.get("ru", {}).get("value", "")

            name = en_label or ru_label
            if not name or name.lower() in existing_names:
                continue

            claims = extract_claims(entity)
            attrs = build_attributes(claims)

            if not attrs:  # Invalid entity
                continue

            # Save entity
            lang = "ru" if ru_label and not en_label else "en"
            eid = await repo.add_entity(name, f"wikidata:{qid}", category, lang)

            # Add alias
            if en_label and ru_label and en_label != ru_label:
                alias = ru_label if name == en_label else en_label
                await repo.add_alias(eid, alias, "ru" if name == en_label else "en")

            # Save attributes
            for attr_key, value in attrs.items():
                if attr_key in attr_ids:
                    await repo.set_entity_attribute(eid, attr_ids[attr_key], value)

            existing_names.add(name.lower())
            count += 1
            logger.info("Added: %s (%s)", name, category)

        time.sleep(1)  # Rate limiting

    return count


async def run_collector(
    db_path: str,
    interval: int = 300,
    batch_size: int = 50,
):
    """Main collector loop."""
    global shutdown_requested

    logger.info("Starting collector (db=%s, interval=%ds)", db_path, interval)

    # Initialize database
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    repo = Repository(db_path)
    await repo.init_db()

    # Ensure attributes exist
    existing_attrs = await repo.get_all_attributes()
    if not existing_attrs:
        logger.info("Creating %d attributes...", len(ATTRIBUTES))
        for key, q_ru, q_en, cat in ATTRIBUTES:
            await repo.add_attribute(key, q_ru, q_en, cat)

    attr_list = await repo.get_all_attributes()
    attr_ids = {a.key: a.id for a in attr_list}

    # Get existing entities
    existing = await repo.get_all_entities()
    existing_names = {e.name.lower() for e in existing}
    logger.info("Database has %d entities", len(existing_names))

    # Main loop
    categories = list(SEARCH_SEEDS.keys())
    category_idx = 0
    total_collected = 0

    while not shutdown_requested:
        # Select category
        category = categories[category_idx % len(categories)]
        seeds = SEARCH_SEEDS[category]

        # Shuffle seeds for variety
        random.shuffle(seeds)
        batch = seeds[:batch_size]

        logger.info("Collecting from %s (%d seeds)", category, len(batch))

        count = await collect_batch(repo, attr_ids, existing_names, category, batch)
        total_collected += count

        logger.info("Collected %d new entities (total: %d)", count, total_collected)

        category_idx += 1

        # Save checkpoint
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "total_entities": len(existing_names),
            "last_category": category,
        }
        checkpoint_path = db_path.replace(".db", "_checkpoint.json")
        with open(checkpoint_path, "w") as f:
            json.dump(checkpoint, f)

        # Wait before next batch
        if not shutdown_requested:
            logger.info("Sleeping for %d seconds...", interval)
            for _ in range(interval):
                if shutdown_requested:
                    break
                time.sleep(1)

    await repo.close()
    logger.info("Collector stopped. Total collected: %d", total_collected)


def main():
    parser = argparse.ArgumentParser(description="Background data collector")
    parser.add_argument("--db", default="data/collected.db", help="Database path")
    parser.add_argument("--interval", type=int, default=300, help="Seconds between batches")
    parser.add_argument("--batch-size", type=int, default=50, help="Seeds per batch")
    args = parser.parse_args()

    asyncio.run(run_collector(args.db, args.interval, args.batch_size))


if __name__ == "__main__":
    main()
