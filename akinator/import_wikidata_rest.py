"""Import entities from Wikidata using REST API (more reliable than SPARQL).

This script fetches popular entities from Wikidata using the REST API,
which is more stable than SPARQL queries that often timeout.

Usage:
    python -m akinator.import_wikidata_rest --limit 100000
    python -m akinator.import_wikidata_rest --resume  # Continue from checkpoint
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from akinator.db.repository import Repository

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("wikidata_rest")

# Wikidata REST API
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "AkinatorBot/2.0 (https://github.com/MyNameIsAlexandro/Akinator_2.0)"

# Checkpoint file for resuming
CHECKPOINT_FILE = "data/import_checkpoint.json"

# Categories to fetch (Wikidata item IDs)
CATEGORIES = {
    # Real people by profession
    "Q33999": "actor",
    "Q177220": "singer",
    "Q36180": "writer",
    "Q82955": "politician",
    "Q937857": "association football player",
    "Q3665646": "basketball player",
    "Q901": "scientist",
    "Q11774202": "film director",
    "Q639669": "musician",
    "Q2066131": "athlete",
    "Q214917": "playwright",
    "Q1930187": "journalist",
    "Q183945": "record producer",
    "Q488205": "singer-songwriter",
    "Q10800557": "film actor",
    "Q10798782": "television actor",
    "Q15981151": "YouTuber",
    "Q3282637": "film producer",
    "Q49757": "poet",
    "Q1028181": "painter",
    "Q1622272": "university teacher",
    "Q11513337": "athletics competitor",
    "Q11338576": "boxer",
    "Q18581305": "ice hockey player",
    "Q10871364": "baseball player",
    "Q13590141": "tennis player",
    # Fictional characters
    "Q95074": "fictional character",
    "Q15632617": "fictional human",
    "Q15773317": "fictional animal",
    "Q4271324": "mythical character",
}

# 62 attributes (same as main import script)
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
    ("from_literature", "Связан с литературой?", "Related to literature?", "media"),
    ("from_philosophy", "Связан с философией?", "Related to philosophy?", "media"),
    ("from_military", "Связан с военным делом?", "Related to military?", "media"),
    ("from_business", "Связан с бизнесом?", "Related to business?", "media"),
    ("from_fashion", "Связан с модой?", "Related to fashion?", "media"),
    ("from_art", "Связан с изобразительным искусством?", "Related to visual arts?", "media"),
    ("from_religion", "Связан с религией?", "Related to religion?", "media"),
    ("from_internet", "Интернет-знаменитость?", "Internet celebrity?", "media"),
    ("from_usa", "Связан с США?", "Related to USA?", "geography"),
    ("from_europe", "Связан с Европой?", "Related to Europe?", "geography"),
    ("from_russia", "Связан с Россией?", "Related to Russia?", "geography"),
    ("from_asia", "Связан с Азией?", "Related to Asia?", "geography"),
    ("from_japan", "Связан с Японией?", "Related to Japan?", "geography"),
    ("from_africa", "Связан с Африкой?", "Related to Africa?", "geography"),
    ("from_south_america", "Связан с Южной Америкой?", "Related to South America?", "geography"),
    ("from_middle_east", "Связан с Ближним Востоком?", "Related to Middle East?", "geography"),
    ("from_oceania", "Связан с Океанией?", "Related to Oceania?", "geography"),
    ("from_china", "Связан с Китаем?", "Related to China?", "geography"),
    ("era_ancient", "Из древности (до 500 н.э.)?", "From ancient times (before 500 AD)?", "era"),
    ("era_medieval", "Из средневековья (500-1500)?", "From medieval era (500-1500)?", "era"),
    ("era_modern", "Из нового времени (1500-1900)?", "From modern era (1500-1900)?", "era"),
    ("era_20th_century", "Из 20-го века?", "From the 20th century?", "era"),
    ("era_21st_century", "Из 21-го века?", "From the 21st century?", "era"),
    ("born_1900s", "Родился в 1900-х?", "Born in 1900s?", "birth_decade"),
    ("born_1910s", "Родился в 1910-х?", "Born in 1910s?", "birth_decade"),
    ("born_1920s", "Родился в 1920-х?", "Born in 1920s?", "birth_decade"),
    ("born_1930s", "Родился в 1930-х?", "Born in 1930s?", "birth_decade"),
    ("born_1940s", "Родился в 1940-х?", "Born in 1940s?", "birth_decade"),
    ("born_1950s", "Родился в 1950-х?", "Born in 1950s?", "birth_decade"),
    ("born_1960s", "Родился в 1960-х?", "Born in 1960s?", "birth_decade"),
    ("born_1970s", "Родился в 1970-х?", "Born in 1970s?", "birth_decade"),
    ("born_1980s", "Родился в 1980-х?", "Born in 1980s?", "birth_decade"),
    ("born_1990s", "Родился в 1990-х или позже?", "Born in 1990s or later?", "birth_decade"),
    ("has_superpower", "Обладает сверхспособностями?", "Has superpowers?", "traits"),
    ("wears_uniform", "Носит униформу/костюм?", "Wears a uniform/costume?", "traits"),
    ("has_famous_catchphrase", "Известен крылатой фразой?", "Known for a famous catchphrase?", "traits"),
    ("is_leader", "Является лидером/главой?", "Is a leader/head?", "traits"),
    ("is_wealthy", "Богатый/знатный?", "Wealthy/noble?", "traits"),
    ("is_action_hero", "Герой боевика/экшена?", "Action hero?", "traits"),
    ("is_comedic", "Комедийный персонаж?", "Comedic character?", "traits"),
    ("is_dark_brooding", "Мрачный/серьёзный персонаж?", "Dark/brooding character?", "traits"),
    ("is_child_friendly", "Детский персонаж?", "Child-friendly character?", "traits"),
    ("wears_mask", "Носит маску?", "Wears a mask?", "traits"),
    ("has_armor", "Носит броню/доспехи?", "Wears armor?", "traits"),
    ("has_facial_hair", "Имеет бороду/усы?", "Has facial hair?", "traits"),
]

# Profession to attributes mapping
PROFESSION_ATTRS = {
    "actor": {"from_movie": 0.9},
    "film actor": {"from_movie": 1.0},
    "television actor": {"from_tv_series": 1.0, "from_movie": 0.5},
    "singer": {"from_music": 1.0},
    "singer-songwriter": {"from_music": 1.0},
    "musician": {"from_music": 1.0},
    "record producer": {"from_music": 0.9},
    "writer": {"from_book": 0.9, "from_literature": 0.9},
    "playwright": {"from_book": 0.8, "from_literature": 0.9},
    "poet": {"from_book": 0.8, "from_literature": 1.0},
    "journalist": {"from_book": 0.5},
    "politician": {"from_politics": 1.0, "is_leader": 0.7},
    "association football player": {"from_sport": 1.0, "wears_uniform": 1.0},
    "basketball player": {"from_sport": 1.0, "wears_uniform": 1.0},
    "ice hockey player": {"from_sport": 1.0, "wears_uniform": 1.0},
    "baseball player": {"from_sport": 1.0, "wears_uniform": 1.0},
    "tennis player": {"from_sport": 1.0},
    "boxer": {"from_sport": 1.0},
    "athletics competitor": {"from_sport": 1.0},
    "athlete": {"from_sport": 1.0},
    "scientist": {"from_science": 1.0},
    "film director": {"from_movie": 1.0},
    "film producer": {"from_movie": 0.9, "is_wealthy": 0.6},
    "painter": {"from_art": 1.0},
    "university teacher": {"from_science": 0.6},
    "YouTuber": {"from_internet": 1.0, "era_21st_century": 1.0},
}

# Country to attributes mapping (QID -> attrs)
COUNTRY_ATTRS_BY_QID = {
    "Q30": {"from_usa": 1.0},                           # USA
    "Q145": {"from_europe": 1.0},                       # UK
    "Q142": {"from_europe": 1.0},                       # France
    "Q183": {"from_europe": 1.0},                       # Germany
    "Q38": {"from_europe": 1.0},                        # Italy
    "Q29": {"from_europe": 1.0},                        # Spain
    "Q159": {"from_russia": 1.0, "from_europe": 0.5},   # Russia
    "Q17": {"from_japan": 1.0, "from_asia": 1.0},       # Japan
    "Q148": {"from_china": 1.0, "from_asia": 1.0},      # China
    "Q668": {"from_asia": 1.0},                         # India
    "Q155": {"from_south_america": 1.0},                # Brazil
    "Q414": {"from_south_america": 1.0},                # Argentina
    "Q408": {"from_oceania": 1.0},                      # Australia
    "Q16": {"from_usa": 0.3},                           # Canada
    "Q96": {"from_south_america": 0.5},                 # Mexico
    "Q884": {"from_asia": 1.0},                         # South Korea
    "Q28": {"from_europe": 1.0},                        # Hungary
    "Q36": {"from_europe": 1.0},                        # Poland
    "Q39": {"from_europe": 1.0},                        # Switzerland
    "Q55": {"from_europe": 1.0},                        # Netherlands
    "Q31": {"from_europe": 1.0},                        # Belgium
    "Q40": {"from_europe": 1.0},                        # Austria
    "Q34": {"from_europe": 1.0},                        # Sweden
    "Q35": {"from_europe": 1.0},                        # Denmark
    "Q20": {"from_europe": 1.0},                        # Norway
    "Q33": {"from_europe": 1.0},                        # Finland
    "Q45": {"from_europe": 1.0},                        # Portugal
    "Q41": {"from_europe": 1.0},                        # Greece
    "Q43": {"from_middle_east": 1.0},                   # Turkey
    "Q801": {"from_middle_east": 1.0},                  # Israel
    "Q79": {"from_middle_east": 1.0},                   # Egypt
    "Q794": {"from_middle_east": 1.0},                  # Iran
    "Q258": {"from_africa": 1.0},                       # South Africa
    "Q1033": {"from_africa": 1.0},                      # Nigeria
    "Q114": {"from_africa": 1.0},                       # Kenya
}

# Profession QID -> Category mapping (for template application)
PROFESSION_TO_CATEGORY = {
    # Actors/Entertainment
    "Q33999": "hollywood_actor",        # actor
    "Q10800557": "hollywood_actor",     # film actor
    "Q10798782": "tv_actor",            # television actor
    "Q2526255": "hollywood_actor",      # film director
    "Q3282637": "hollywood_actor",      # film producer
    "Q2405480": "voice_actor",          # voice actor
    "Q214917": "writer_modern",         # playwright

    # Musicians
    "Q177220": "rock_musician",         # singer
    "Q639669": "rock_musician",         # musician
    "Q488205": "rock_musician",         # singer-songwriter
    "Q183945": "rock_musician",         # record producer
    "Q36834": "classical_composer",     # composer
    "Q486748": "classical_musician",    # pianist
    "Q855091": "classical_musician",    # guitarist

    # Athletes - Football
    "Q937857": "footballer",            # association football player
    "Q6665249": "footballer",           # football manager

    # Athletes - Basketball
    "Q3665646": "basketball_player",    # basketball player

    # Athletes - Tennis
    "Q13590141": "tennis_player",       # tennis player

    # Athletes - Other
    "Q11338576": "athlete_fighter",     # boxer
    "Q11513337": "athlete_runner",      # athletics competitor
    "Q2066131": "athlete_generic",      # athlete
    "Q18581305": "hockey_player",       # ice hockey player
    "Q10871364": "baseball_player",     # baseball player
    "Q10843263": "f1_driver",           # racing driver

    # Politicians
    "Q82955": "politician_modern",      # politician
    "Q30461": "politician_leader",      # president
    "Q14915627": "politician_leader",   # chancellor

    # Scientists
    "Q901": "scientist",                # scientist
    "Q169470": "scientist",             # physicist
    "Q593644": "scientist",             # chemist
    "Q864503": "scientist",             # biologist
    "Q170790": "scientist",             # mathematician

    # Writers
    "Q36180": "writer_modern",          # writer
    "Q49757": "writer_classic",         # poet
    "Q4853732": "writer_classic",       # novelist

    # Artists
    "Q1028181": "visual_artist",        # painter
    "Q1281618": "visual_artist",        # sculptor
    "Q33231": "visual_artist",          # photographer

    # Internet/Modern
    "Q15981151": "youtuber",            # YouTuber
    "Q2259532": "internet_personality", # social media celebrity

    # Fictional characters (will be detected separately)
    "Q95074": "fictional_generic",      # fictional character
    "Q15632617": "fictional_generic",   # fictional human
}

# Category templates (simplified - full templates in categories.py)
CATEGORY_TEMPLATES = {
    "hollywood_actor": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_movie": 0.95, "from_tv_series": 0.6, "from_usa": 0.7,
        "is_wealthy": 0.7, "has_famous_catchphrase": 0.3, "is_leader": 0.0,
        "has_superpower": 0.0, "from_music": 0.1, "from_sport": 0.0,
        "from_comics": 0.0, "from_anime": 0.0, "from_game": 0.0,
        "from_book": 0.1, "from_politics": 0.0, "from_science": 0.0,
    },
    "tv_actor": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_movie": 0.4, "from_tv_series": 0.95, "from_usa": 0.6,
        "is_wealthy": 0.5, "has_superpower": 0.0,
    },
    "voice_actor": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_movie": 0.6, "from_tv_series": 0.4, "from_anime": 0.4,
        "is_wealthy": 0.4, "has_superpower": 0.0,
    },
    "rock_musician": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_music": 1.0, "from_movie": 0.2, "has_famous_catchphrase": 0.5,
        "is_wealthy": 0.6, "has_superpower": 0.0, "wears_uniform": 0.2,
        "from_sport": 0.0, "from_politics": 0.0,
    },
    "classical_composer": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_music": 1.0, "from_europe": 0.8, "is_wealthy": 0.3,
        "has_famous_catchphrase": 0.2, "from_history": 0.7,
        "era_modern": 0.6, "has_facial_hair": 0.5,
    },
    "classical_musician": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_music": 1.0, "from_europe": 0.5, "is_wealthy": 0.4,
    },
    "footballer": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_sport": 1.0, "wears_uniform": 1.0, "is_wealthy": 0.6,
        "from_europe": 0.6, "from_south_america": 0.3,
        "has_superpower": 0.0, "from_music": 0.0, "from_movie": 0.1,
    },
    "basketball_player": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_sport": 1.0, "wears_uniform": 1.0, "is_wealthy": 0.7,
        "from_usa": 0.8, "has_superpower": 0.0,
    },
    "tennis_player": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_sport": 1.0, "wears_uniform": 0.8, "is_wealthy": 0.6,
    },
    "athlete_fighter": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_sport": 1.0, "is_action_hero": 0.3, "is_wealthy": 0.5,
    },
    "athlete_runner": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_sport": 1.0, "wears_uniform": 0.7,
    },
    "athlete_generic": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_sport": 1.0, "wears_uniform": 0.7,
    },
    "hockey_player": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_sport": 1.0, "wears_uniform": 1.0, "has_armor": 0.8,
    },
    "baseball_player": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_sport": 1.0, "wears_uniform": 1.0, "from_usa": 0.7,
    },
    "f1_driver": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_sport": 1.0, "wears_uniform": 1.0, "is_wealthy": 0.8,
    },
    "politician_modern": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_politics": 1.0, "is_leader": 0.6, "is_wealthy": 0.5,
        "has_famous_catchphrase": 0.4,
    },
    "politician_leader": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_politics": 1.0, "is_leader": 1.0, "is_wealthy": 0.6,
        "has_famous_catchphrase": 0.5,
    },
    "scientist": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_science": 1.0, "is_wealthy": 0.3, "has_famous_catchphrase": 0.2,
        "has_facial_hair": 0.4,
    },
    "writer_modern": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_book": 0.9, "from_literature": 1.0, "is_wealthy": 0.4,
    },
    "writer_classic": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_book": 1.0, "from_literature": 1.0, "from_history": 0.5,
        "has_facial_hair": 0.5,
    },
    "visual_artist": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_art": 1.0, "is_wealthy": 0.3, "has_facial_hair": 0.4,
    },
    "youtuber": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 0.8,
        "from_internet": 1.0, "era_21st_century": 1.0, "is_wealthy": 0.5,
    },
    "internet_personality": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
        "from_internet": 1.0, "era_21st_century": 1.0,
    },
    "fictional_generic": {
        "is_fictional": 1.0, "is_human": 0.7, "is_adult": 0.8,
        "from_movie": 0.5, "from_book": 0.3, "from_comics": 0.3,
    },
    "default_person": {
        "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
    },
}


def api_request(params: dict, max_retries: int = 3) -> dict:
    """Make a request to Wikidata API with retry logic."""
    params["format"] = "json"
    url = f"{WIKIDATA_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            logger.warning("API request failed (attempt %d/%d): %s", attempt + 1, max_retries, e)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return {}


def get_category_members(category_qid: str, limit: int = 500) -> list[str]:
    """Get members of a Wikidata category using the API."""
    members = []
    params = {
        "action": "wbgetentities",
        "ids": category_qid,
        "props": "claims",
    }
    # This is simplified - in practice would need to use different API
    return members


def search_entities(query: str, limit: int = 50) -> list[dict]:
    """Search for entities using Wikidata API."""
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "limit": min(limit, 50),
        "type": "item",
    }
    result = api_request(params)
    return result.get("search", [])


# Valid P31 (instance of) values for entities we want to import
VALID_ENTITY_TYPES = {
    # Humans
    "Q5",           # human
    # Fictional
    "Q95074",       # fictional character
    "Q15632617",    # fictional human
    "Q15773317",    # fictional animal
    "Q4271324",     # mythical character
    "Q15773347",    # fictional deity
    "Q28803874",    # anime character
    "Q28833485",    # manga character
    "Q15711870",    # animated character
    "Q21070568",    # character that may be fictional
    "Q22988604",    # stock character
}

# Keywords that indicate non-entity items (to filter out)
EXCLUDE_KEYWORDS = {
    "filmography", "discography", "awards", "bibliography", "list of",
    "career", "category:", "template:", "module:", "album", "song",
    "episode", "season", "tour", "concert", "documentary"
}


def get_entity_details(qids: list[str]) -> dict:
    """Get detailed information for multiple entities."""
    if not qids:
        return {}

    # API limit is 50 entities per request
    batch_size = 50
    all_entities = {}

    for i in range(0, len(qids), batch_size):
        batch = qids[i:i + batch_size]
        params = {
            "action": "wbgetentities",
            "ids": "|".join(batch),
            "props": "labels|descriptions|claims",
            "languages": "en|ru",
        }
        result = api_request(params)
        entities = result.get("entities", {})
        all_entities.update(entities)
        time.sleep(0.5)  # Rate limiting

    return all_entities


def extract_birth_year(claims: dict) -> int | None:
    """Extract birth year from entity claims."""
    birth_claim = claims.get("P569", [])  # P569 = date of birth
    if birth_claim:
        try:
            time_value = birth_claim[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("time", "")
            if time_value:
                # Format: +YYYY-MM-DDT00:00:00Z
                year_str = time_value[1:5]
                return int(year_str)
        except (IndexError, KeyError, ValueError):
            pass
    return None


def extract_death_year(claims: dict) -> int | None:
    """Extract death year from entity claims."""
    death_claim = claims.get("P570", [])  # P570 = date of death
    if death_claim:
        try:
            time_value = death_claim[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("time", "")
            if time_value:
                year_str = time_value[1:5]
                return int(year_str)
        except (IndexError, KeyError, ValueError):
            pass
    return None


def extract_gender(claims: dict) -> str | None:
    """Extract gender from entity claims."""
    gender_claim = claims.get("P21", [])  # P21 = sex or gender
    if gender_claim:
        try:
            gender_id = gender_claim[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
            if gender_id == "Q6581097":
                return "male"
            elif gender_id == "Q6581072":
                return "female"
        except (IndexError, KeyError):
            pass
    return None


def extract_country(claims: dict) -> str | None:
    """Extract country of citizenship from entity claims."""
    country_claim = claims.get("P27", [])  # P27 = country of citizenship
    if country_claim:
        try:
            return country_claim[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
        except (IndexError, KeyError):
            pass
    return None


def is_valid_entity(name: str, claims: dict) -> tuple[bool, bool]:
    """Check if entity is a valid person/character.

    Returns:
        (is_valid, is_fictional) - whether entity is valid and whether it's fictional
    """
    # Filter out items with excluded keywords in name
    name_lower = name.lower()
    for keyword in EXCLUDE_KEYWORDS:
        if keyword in name_lower:
            return False, False

    # Check P31 (instance of)
    instance_of = claims.get("P31", [])
    if not instance_of:
        return False, False

    is_fictional = False
    is_human = False

    for claim in instance_of:
        try:
            type_id = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
            if type_id in VALID_ENTITY_TYPES:
                if type_id == "Q5":
                    is_human = True
                else:
                    is_fictional = True
        except (KeyError, TypeError):
            pass

    if is_human or is_fictional:
        return True, is_fictional

    return False, False


def get_occupations(claims: dict) -> list[str]:
    """Extract occupations from entity claims."""
    occupations = []
    occ_claim = claims.get("P106", [])  # P106 = occupation
    for claim in occ_claim:
        try:
            occ_id = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
            if occ_id in CATEGORIES:
                occupations.append(CATEGORIES[occ_id])
        except (KeyError, TypeError):
            pass
    return occupations


def get_occupation_qids(claims: dict) -> list[str]:
    """Extract occupation QIDs from entity claims."""
    qids = []
    occ_claim = claims.get("P106", [])  # P106 = occupation
    for claim in occ_claim:
        try:
            occ_id = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
            if occ_id:
                qids.append(occ_id)
        except (KeyError, TypeError):
            pass
    return qids


def detect_category(occ_qids: list[str], is_fictional: bool) -> str:
    """Detect best category based on occupation QIDs."""
    if is_fictional:
        return "fictional_generic"

    # Try to find a matching category
    for qid in occ_qids:
        if qid in PROFESSION_TO_CATEGORY:
            return PROFESSION_TO_CATEGORY[qid]

    return "default_person"


def get_country_qid(claims: dict) -> str | None:
    """Extract country of citizenship QID from entity claims."""
    country_claim = claims.get("P27", [])  # P27 = country of citizenship
    if not country_claim:
        # Try place of birth
        birth_claim = claims.get("P19", [])  # P19 = place of birth
        if birth_claim:
            try:
                return birth_claim[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
            except (IndexError, KeyError):
                pass
        return None
    try:
        return country_claim[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
    except (IndexError, KeyError):
        return None


def build_entity_attributes(
    claims: dict,
    is_fictional: bool,
    occ_qids: list[str],
    birth_year: int | None,
    death_year: int | None,
    gender: str | None,
) -> dict[str, float]:
    """Build full attribute dictionary for an entity."""

    # Detect category and start with template
    category = detect_category(occ_qids, is_fictional)
    template = CATEGORY_TEMPLATES.get(category, CATEGORY_TEMPLATES["default_person"])

    # Start with template
    attrs = dict(template)

    # Override with specific Wikidata facts
    attrs["is_fictional"] = 1.0 if is_fictional else 0.0

    if gender:
        attrs["is_male"] = 1.0 if gender == "male" else 0.0

    # Birth/death years
    attrs.update(birth_year_to_attrs(birth_year))

    if death_year:
        attrs["is_alive"] = 0.0
    elif birth_year and birth_year < 1930:
        attrs["is_alive"] = 0.1
    elif birth_year:
        attrs["is_alive"] = 0.95
    else:
        attrs["is_alive"] = 0.7  # Unknown, assume alive

    # Country attributes
    country_qid = get_country_qid(claims)
    if country_qid and country_qid in COUNTRY_ATTRS_BY_QID:
        country_attrs = COUNTRY_ATTRS_BY_QID[country_qid]
        for key, value in country_attrs.items():
            # Only override if it's a stronger signal
            if value > attrs.get(key, 0):
                attrs[key] = value

    # Apply profession-based attributes on top
    for qid in occ_qids:
        if qid in CATEGORIES and CATEGORIES[qid] in PROFESSION_ATTRS:
            prof_attrs = PROFESSION_ATTRS[CATEGORIES[qid]]
            for key, value in prof_attrs.items():
                if value > attrs.get(key, 0):
                    attrs[key] = value

    return attrs


def birth_year_to_attrs(year: int | None) -> dict[str, float]:
    """Convert birth year to attribute values."""
    if year is None:
        return {}

    attrs = {}
    decade = (year // 10) * 10

    decade_map = {
        1900: "born_1900s",
        1910: "born_1910s",
        1920: "born_1920s",
        1930: "born_1930s",
        1940: "born_1940s",
        1950: "born_1950s",
        1960: "born_1960s",
        1970: "born_1970s",
        1980: "born_1980s",
        1990: "born_1990s",
    }

    if decade in decade_map:
        attrs[decade_map[decade]] = 1.0
    elif decade >= 1990:
        attrs["born_1990s"] = 1.0

    # Era attributes
    if year < 500:
        attrs["era_ancient"] = 1.0
        attrs["from_history"] = 1.0
    elif year < 1500:
        attrs["era_medieval"] = 1.0
        attrs["from_history"] = 1.0
    elif year < 1900:
        attrs["era_modern"] = 1.0
    elif year < 2000:
        attrs["era_20th_century"] = 1.0
    else:
        attrs["era_21st_century"] = 1.0

    return attrs


def save_checkpoint(data: dict) -> None:
    """Save import progress checkpoint."""
    os.makedirs(os.path.dirname(CHECKPOINT_FILE), exist_ok=True)
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(data, f)


def load_checkpoint() -> dict:
    """Load import progress checkpoint."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"imported_qids": [], "last_category": None, "total_count": 0}


# Popular search terms to seed entity discovery (expanded for 100K target)
SEARCH_SEEDS = [
    # A-list Actors (Hollywood)
    "Tom Hanks", "Leonardo DiCaprio", "Brad Pitt", "Johnny Depp", "Robert Downey Jr",
    "Will Smith", "Denzel Washington", "Morgan Freeman", "Samuel L Jackson", "Keanu Reeves",
    "Scarlett Johansson", "Meryl Streep", "Julia Roberts", "Angelina Jolie", "Jennifer Lawrence",
    "Tom Cruise", "Harrison Ford", "Clint Eastwood", "Robert De Niro", "Al Pacino",
    "Jack Nicholson", "Anthony Hopkins", "Dustin Hoffman", "Gene Hackman", "Michael Caine",
    "Christian Bale", "Matt Damon", "Ben Affleck", "George Clooney", "Ryan Gosling",
    "Joaquin Phoenix", "Jared Leto", "Jake Gyllenhaal", "Edward Norton", "Heath Ledger",
    "Nicole Kidman", "Cate Blanchett", "Kate Winslet", "Natalie Portman", "Emma Stone",
    "Anne Hathaway", "Amy Adams", "Sandra Bullock", "Charlize Theron", "Margot Robbie",
    "Dwayne Johnson", "Vin Diesel", "Jason Statham", "Chris Hemsworth", "Chris Evans",
    "Chris Pratt", "Ryan Reynolds", "Zac Efron", "Timothee Chalamet", "Adam Driver",
    # Classic Hollywood
    "Marilyn Monroe", "Audrey Hepburn", "James Dean", "Marlon Brando", "Humphrey Bogart",
    "Katharine Hepburn", "Elizabeth Taylor", "Clark Gable", "Cary Grant", "Gregory Peck",
    "Grace Kelly", "Ingrid Bergman", "Bette Davis", "Joan Crawford", "Rita Hayworth",
    # International actors
    "Jackie Chan", "Bruce Lee", "Jet Li", "Tony Leung", "Gong Li",
    "Shah Rukh Khan", "Amitabh Bachchan", "Aamir Khan", "Priyanka Chopra", "Deepika Padukone",
    "Antonio Banderas", "Penelope Cruz", "Javier Bardem", "Pedro Pascal", "Oscar Isaac",
    "Jean Reno", "Marion Cotillard", "Juliette Binoche", "Gerard Depardieu", "Jean Dujardin",
    # Musicians - Pop
    "Michael Jackson", "Elvis Presley", "Madonna", "Beyonce", "Taylor Swift",
    "Lady Gaga", "Britney Spears", "Justin Bieber", "Ariana Grande", "Selena Gomez",
    "Katy Perry", "Bruno Mars", "Ed Sheeran", "Adele", "Billie Eilish",
    "Dua Lipa", "Harry Styles", "The Weeknd", "Post Malone", "Shawn Mendes",
    "Justin Timberlake", "Christina Aguilera", "Shakira", "Ricky Martin", "Enrique Iglesias",
    "Celine Dion", "Whitney Houston", "Mariah Carey", "Diana Ross", "Stevie Wonder",
    "Prince", "David Bowie", "Freddie Mercury", "George Michael", "Elton John",
    # Musicians - Rock
    "Beatles", "Rolling Stones", "Led Zeppelin", "Pink Floyd", "Queen",
    "The Who", "Deep Purple", "Black Sabbath", "AC/DC", "Aerosmith",
    "Bon Jovi", "Guns N Roses", "Metallica", "Nirvana", "Red Hot Chili Peppers",
    "Foo Fighters", "Green Day", "Linkin Park", "Coldplay", "U2",
    "Radiohead", "Oasis", "Arctic Monkeys", "Muse", "Imagine Dragons",
    "John Lennon", "Paul McCartney", "Mick Jagger", "Keith Richards", "Ozzy Osbourne",
    "Robert Plant", "Jimmy Page", "Eric Clapton", "Jimi Hendrix", "Eddie Van Halen",
    "Kurt Cobain", "Dave Grohl", "Chris Cornell", "Chester Bennington", "Eddie Vedder",
    # Musicians - Hip Hop/Rap
    "Eminem", "Drake", "Kanye West", "Jay-Z", "Rihanna",
    "Kendrick Lamar", "Travis Scott", "J Cole", "Nicki Minaj", "Cardi B",
    "Snoop Dogg", "Dr Dre", "Ice Cube", "Tupac Shakur", "Notorious BIG",
    "Lil Wayne", "50 Cent", "Nas", "Wiz Khalifa", "Future",
    "Megan Thee Stallion", "Doja Cat", "Lil Nas X", "Tyler the Creator", "A$AP Rocky",
    # Musicians - Country
    "Johnny Cash", "Dolly Parton", "Willie Nelson", "Garth Brooks", "Tim McGraw",
    "Kenny Rogers", "Blake Shelton", "Carrie Underwood", "Miranda Lambert", "Luke Bryan",
    # Musicians - R&B/Soul
    "Aretha Franklin", "Ray Charles", "James Brown", "Otis Redding", "Marvin Gaye",
    "Usher", "Chris Brown", "Ne-Yo", "John Legend", "Alicia Keys",
    # Musicians - Classical
    "Mozart", "Beethoven", "Bach", "Chopin", "Tchaikovsky",
    "Vivaldi", "Handel", "Brahms", "Schubert", "Liszt",
    "Paganini", "Verdi", "Wagner", "Debussy", "Rachmaninoff",
    # Musicians - Jazz
    "Louis Armstrong", "Miles Davis", "John Coltrane", "Duke Ellington", "Charlie Parker",
    "Ella Fitzgerald", "Billie Holiday", "Nat King Cole", "Frank Sinatra", "Tony Bennett",
    # Athletes - Football/Soccer
    "Lionel Messi", "Cristiano Ronaldo", "Neymar", "Kylian Mbappe", "Erling Haaland",
    "Diego Maradona", "Pele", "Zinedine Zidane", "Ronaldinho", "Ronaldo Nazario",
    "David Beckham", "Wayne Rooney", "Steven Gerrard", "Frank Lampard", "Thierry Henry",
    "Robert Lewandowski", "Karim Benzema", "Luka Modric", "Toni Kroos", "Sergio Ramos",
    "Gerard Pique", "Andres Iniesta", "Xavi", "Sergio Busquets", "Carles Puyol",
    "Gianluigi Buffon", "Manuel Neuer", "Iker Casillas", "Edwin van der Sar", "Oliver Kahn",
    # Athletes - Basketball
    "LeBron James", "Michael Jordan", "Kobe Bryant", "Shaquille O'Neal", "Stephen Curry",
    "Kevin Durant", "Giannis Antetokounmpo", "Kawhi Leonard", "James Harden", "Anthony Davis",
    "Magic Johnson", "Larry Bird", "Kareem Abdul-Jabbar", "Tim Duncan", "Dirk Nowitzki",
    "Hakeem Olajuwon", "Charles Barkley", "Karl Malone", "John Stockton", "Allen Iverson",
    # Athletes - Tennis
    "Roger Federer", "Rafael Nadal", "Novak Djokovic", "Andy Murray", "Pete Sampras",
    "Andre Agassi", "Boris Becker", "John McEnroe", "Bjorn Borg", "Jimmy Connors",
    "Serena Williams", "Venus Williams", "Maria Sharapova", "Steffi Graf", "Martina Navratilova",
    "Naomi Osaka", "Simona Halep", "Ashleigh Barty", "Billie Jean King", "Chris Evert",
    # Athletes - Boxing/MMA
    "Muhammad Ali", "Mike Tyson", "Floyd Mayweather", "Manny Pacquiao", "Canelo Alvarez",
    "Sugar Ray Leonard", "George Foreman", "Joe Frazier", "Evander Holyfield", "Lennox Lewis",
    "Conor McGregor", "Khabib Nurmagomedov", "Jon Jones", "Anderson Silva", "Georges St-Pierre",
    # Athletes - American Football
    "Tom Brady", "Joe Montana", "Peyton Manning", "Aaron Rodgers", "Patrick Mahomes",
    "Brett Favre", "Dan Marino", "John Elway", "Drew Brees", "Russell Wilson",
    "Jerry Rice", "Walter Payton", "Barry Sanders", "Jim Brown", "Emmitt Smith",
    "Lawrence Taylor", "Ray Lewis", "Reggie White", "Deion Sanders", "Randy Moss",
    # Athletes - Baseball
    "Babe Ruth", "Willie Mays", "Hank Aaron", "Mickey Mantle", "Ted Williams",
    "Derek Jeter", "Mike Trout", "Shohei Ohtani", "Albert Pujols", "Alex Rodriguez",
    # Athletes - Golf
    "Tiger Woods", "Jack Nicklaus", "Arnold Palmer", "Phil Mickelson", "Rory McIlroy",
    "Dustin Johnson", "Jordan Spieth", "Brooks Koepka", "Bryson DeChambeau", "Justin Thomas",
    # Athletes - Olympics
    "Usain Bolt", "Carl Lewis", "Jesse Owens", "Michael Phelps", "Simone Biles",
    "Nadia Comaneci", "Mary Lou Retton", "Gabby Douglas", "Katie Ledecky", "Allyson Felix",
    # Athletes - F1/Racing
    "Lewis Hamilton", "Michael Schumacher", "Ayrton Senna", "Sebastian Vettel", "Max Verstappen",
    "Fernando Alonso", "Niki Lauda", "Alain Prost", "Nigel Mansell", "Mika Hakkinen",
    # Athletes - Other
    "Wayne Gretzky", "Sidney Crosby", "Alex Ovechkin", "Connor McDavid", "Mario Lemieux",
    "Sachin Tendulkar", "Virat Kohli", "MS Dhoni", "Brian Lara", "Ricky Ponting",
    # Politicians - US Presidents
    "Barack Obama", "Donald Trump", "Joe Biden", "George Washington", "Abraham Lincoln",
    "Franklin Roosevelt", "John F Kennedy", "Ronald Reagan", "Bill Clinton", "George Bush",
    "Thomas Jefferson", "Theodore Roosevelt", "Woodrow Wilson", "Harry Truman", "Dwight Eisenhower",
    "Richard Nixon", "Jimmy Carter", "George H W Bush", "Gerald Ford", "Lyndon Johnson",
    # Politicians - World Leaders
    "Vladimir Putin", "Xi Jinping", "Angela Merkel", "Emmanuel Macron", "Boris Johnson",
    "Winston Churchill", "Margaret Thatcher", "Tony Blair", "Charles de Gaulle", "Francois Mitterrand",
    "Nelson Mandela", "Mahatma Gandhi", "Jawaharlal Nehru", "Indira Gandhi", "Narendra Modi",
    "Kim Jong Un", "Mao Zedong", "Deng Xiaoping", "Hirohito", "Shinzo Abe",
    "Justin Trudeau", "Fidel Castro", "Che Guevara", "Hugo Chavez", "Eva Peron",
    "Benjamin Netanyahu", "Yasser Arafat", "Recep Erdogan", "Ataturk", "Benazir Bhutto",
    # Politicians - Historical
    "Napoleon Bonaparte", "Julius Caesar", "Alexander the Great", "Cleopatra", "Augustus",
    "Genghis Khan", "Charlemagne", "Queen Victoria", "Elizabeth I", "Henry VIII",
    "Louis XIV", "Catherine the Great", "Peter the Great", "Ivan the Terrible", "Stalin",
    "Hitler", "Mussolini", "Lenin", "Trotsky", "Marx",
    # Scientists
    "Albert Einstein", "Isaac Newton", "Stephen Hawking", "Marie Curie", "Nikola Tesla",
    "Charles Darwin", "Galileo Galilei", "Aristotle", "Plato", "Archimedes",
    "Leonardo da Vinci", "Copernicus", "Johannes Kepler", "Michael Faraday", "James Clerk Maxwell",
    "Richard Feynman", "Niels Bohr", "Werner Heisenberg", "Erwin Schrodinger", "Max Planck",
    "Thomas Edison", "Benjamin Franklin", "Alexander Graham Bell", "Wright Brothers", "Alan Turing",
    "Tim Berners-Lee", "Bill Gates", "Steve Jobs", "Elon Musk", "Mark Zuckerberg",
    "Jeff Bezos", "Larry Page", "Sergey Brin", "Jack Ma", "Satya Nadella",
    # Philosophers
    "Socrates", "Plato", "Aristotle", "Confucius", "Buddha",
    "Nietzsche", "Kant", "Descartes", "Hegel", "Rousseau",
    "John Locke", "David Hume", "Voltaire", "Sartre", "Simone de Beauvoir",
    # Writers - Classic
    "William Shakespeare", "Charles Dickens", "Mark Twain", "Ernest Hemingway", "F Scott Fitzgerald",
    "Jane Austen", "Charlotte Bronte", "Emily Bronte", "Oscar Wilde", "George Orwell",
    "Aldous Huxley", "Virginia Woolf", "James Joyce", "Franz Kafka", "Leo Tolstoy",
    "Fyodor Dostoevsky", "Anton Chekhov", "Victor Hugo", "Alexandre Dumas", "Honore de Balzac",
    "Miguel de Cervantes", "Gabriel Garcia Marquez", "Jorge Luis Borges", "Pablo Neruda", "Mario Vargas Llosa",
    # Writers - Modern
    "Stephen King", "JK Rowling", "George RR Martin", "Dan Brown", "John Grisham",
    "James Patterson", "Agatha Christie", "Arthur Conan Doyle", "Ian Fleming", "Tom Clancy",
    "Neil Gaiman", "Terry Pratchett", "Isaac Asimov", "Arthur C Clarke", "Philip K Dick",
    "Haruki Murakami", "Paulo Coelho", "Salman Rushdie", "Umberto Eco", "Margaret Atwood",
    # Artists
    "Pablo Picasso", "Vincent van Gogh", "Leonardo da Vinci", "Michelangelo", "Rembrandt",
    "Claude Monet", "Salvador Dali", "Andy Warhol", "Frida Kahlo", "Jackson Pollock",
    "Henri Matisse", "Auguste Renoir", "Edgar Degas", "Paul Cezanne", "Gustav Klimt",
    "Edvard Munch", "Wassily Kandinsky", "Banksy", "Jean-Michel Basquiat", "Keith Haring",
    # Directors
    "Steven Spielberg", "Martin Scorsese", "Christopher Nolan", "Quentin Tarantino", "James Cameron",
    "Stanley Kubrick", "Alfred Hitchcock", "Francis Ford Coppola", "Ridley Scott", "Denis Villeneuve",
    "David Fincher", "Wes Anderson", "Paul Thomas Anderson", "Coen Brothers", "Tim Burton",
    "Peter Jackson", "George Lucas", "Guillermo del Toro", "Spike Lee", "Michael Bay",
    "Akira Kurosawa", "Hayao Miyazaki", "Wong Kar-wai", "Park Chan-wook", "Bong Joon-ho",
    # Comedians
    "Charlie Chaplin", "Robin Williams", "Eddie Murphy", "Jim Carrey", "Adam Sandler",
    "Chris Rock", "Dave Chappelle", "Kevin Hart", "Jerry Seinfeld", "Bill Murray",
    "Steve Martin", "Richard Pryor", "George Carlin", "Ricky Gervais", "Louis CK",
    "Amy Schumer", "Tina Fey", "Amy Poehler", "Melissa McCarthy", "Kristen Wiig",
    # TV Personalities
    "Oprah Winfrey", "Ellen DeGeneres", "Jimmy Fallon", "Jimmy Kimmel", "Stephen Colbert",
    "Conan O'Brien", "David Letterman", "Jay Leno", "Trevor Noah", "John Oliver",
    "James Corden", "Graham Norton", "Jonathan Ross", "Graham Norton", "Simon Cowell",
    # YouTubers/Internet
    "PewDiePie", "MrBeast", "Logan Paul", "Jake Paul", "KSI",
    "Markiplier", "Jacksepticeye", "Ninja", "Pokimane", "xQc",
    "Dude Perfect", "Smosh", "Ryan Higa", "Jenna Marbles", "Emma Chamberlain",
    # Models
    "Gigi Hadid", "Bella Hadid", "Kendall Jenner", "Cara Delevingne", "Naomi Campbell",
    "Cindy Crawford", "Claudia Schiffer", "Kate Moss", "Heidi Klum", "Tyra Banks",
    "Adriana Lima", "Gisele Bundchen", "Miranda Kerr", "Karlie Kloss", "Rosie Huntington-Whiteley",
    # Reality TV/Socialites
    "Kim Kardashian", "Kylie Jenner", "Paris Hilton", "Nicole Richie", "Khloe Kardashian",
    "Kourtney Kardashian", "Caitlyn Jenner", "Kris Jenner", "Rob Kardashian", "Kanye West",
    # Fictional - Marvel
    "Spider-Man", "Iron Man", "Captain America", "Thor", "Hulk",
    "Black Widow", "Hawkeye", "Black Panther", "Doctor Strange", "Scarlet Witch",
    "Vision", "Ant-Man", "Wasp", "Captain Marvel", "Falcon",
    "Winter Soldier", "Loki", "Thanos", "Ultron", "Venom",
    "Wolverine", "Deadpool", "Professor X", "Magneto", "Storm",
    "Cyclops", "Jean Grey", "Beast", "Gambit", "Rogue",
    "Fantastic Four", "Silver Surfer", "Daredevil", "Punisher", "Ghost Rider",
    # Fictional - DC
    "Batman", "Superman", "Wonder Woman", "Aquaman", "Flash",
    "Green Lantern", "Cyborg", "Shazam", "Hawkman", "Martian Manhunter",
    "Robin", "Batgirl", "Nightwing", "Catwoman", "Harley Quinn",
    "Joker", "Lex Luthor", "Darkseid", "Bane", "Riddler",
    "Two-Face", "Penguin", "Scarecrow", "Poison Ivy", "Mr Freeze",
    # Fictional - Star Wars
    "Luke Skywalker", "Darth Vader", "Han Solo", "Princess Leia", "Chewbacca",
    "Yoda", "Obi-Wan Kenobi", "Emperor Palpatine", "Boba Fett", "R2-D2",
    "C-3PO", "Anakin Skywalker", "Padme Amidala", "Mace Windu", "Qui-Gon Jinn",
    "Kylo Ren", "Rey", "Finn", "Poe Dameron", "Baby Yoda",
    # Fictional - Harry Potter
    "Harry Potter", "Hermione Granger", "Ron Weasley", "Albus Dumbledore", "Severus Snape",
    "Lord Voldemort", "Draco Malfoy", "Hagrid", "Sirius Black", "Remus Lupin",
    "Neville Longbottom", "Luna Lovegood", "Ginny Weasley", "Bellatrix Lestrange", "Dobby",
    # Fictional - Lord of the Rings
    "Frodo Baggins", "Gandalf", "Aragorn", "Legolas", "Gimli",
    "Samwise Gamgee", "Gollum", "Sauron", "Saruman", "Bilbo Baggins",
    "Boromir", "Faramir", "Eowyn", "Arwen", "Elrond",
    # Fictional - Disney
    "Mickey Mouse", "Minnie Mouse", "Donald Duck", "Goofy", "Pluto",
    "Cinderella", "Snow White", "Sleeping Beauty", "Ariel", "Belle",
    "Jasmine", "Mulan", "Pocahontas", "Rapunzel", "Tiana",
    "Moana", "Elsa", "Anna", "Olaf", "Simba",
    "Mufasa", "Scar", "Timon", "Pumbaa", "Nala",
    "Woody", "Buzz Lightyear", "Jessie", "Rex", "Mr Potato Head",
    "Nemo", "Dory", "Marlin", "Crush", "Gill",
    "Lightning McQueen", "Mater", "Sally", "Doc Hudson", "Luigi",
    "Wall-E", "Eve", "Ratatouille", "Sulley", "Mike Wazowski",
    # Fictional - Anime
    "Goku", "Vegeta", "Naruto", "Sasuke", "Luffy",
    "Ichigo", "Light Yagami", "L", "Saitama", "Genos",
    "Pikachu", "Ash Ketchum", "Charizard", "Mewtwo", "Eevee",
    "Sailor Moon", "Tuxedo Mask", "Edward Elric", "Alphonse Elric", "Roy Mustang",
    "Eren Jaeger", "Mikasa Ackerman", "Levi", "Armin", "Erwin",
    "Spike Spiegel", "Faye Valentine", "Jet Black", "Ein", "Edward",
    "Gon Freecss", "Killua Zoldyck", "Kurapika", "Leorio", "Hisoka",
    "Tanjiro Kamado", "Nezuko", "Zenitsu", "Inosuke", "Muzan",
    "Deku", "All Might", "Bakugo", "Todoroki", "Uraraka",
    "Gojo Satoru", "Yuji Itadori", "Megumi Fushiguro", "Nobara Kugisaki", "Sukuna",
    # Fictional - Games
    "Mario", "Luigi", "Princess Peach", "Bowser", "Yoshi",
    "Link", "Zelda", "Ganondorf", "Kirby", "Sonic",
    "Crash Bandicoot", "Spyro", "Lara Croft", "Nathan Drake", "Kratos",
    "Master Chief", "Cortana", "Solid Snake", "Geralt of Rivia", "Aloy",
    "Cloud Strife", "Sephiroth", "Tifa", "Aerith", "Squall",
    "Pac-Man", "Mega Man", "Ryu", "Ken", "Chun-Li",
    "Scorpion", "Sub-Zero", "Liu Kang", "Johnny Cage", "Raiden",
    "Steve", "Alex", "Creeper", "Enderman", "Herobrine",
    # Fictional - Classic/Literature
    "Sherlock Holmes", "Dr Watson", "James Bond", "Jason Bourne", "Hercule Poirot",
    "Miss Marple", "Dracula", "Frankenstein", "Hamlet", "Macbeth",
    "Romeo", "Juliet", "Othello", "King Lear", "Prospero",
    "Don Quixote", "Sancho Panza", "Huckleberry Finn", "Tom Sawyer", "Oliver Twist",
    "Ebenezer Scrooge", "Tiny Tim", "David Copperfield", "Great Expectations", "Jane Eyre",
    "Elizabeth Bennet", "Mr Darcy", "Emma Woodhouse", "Heathcliff", "Catherine Earnshaw",
    # Fictional - TV Shows
    "Walter White", "Jesse Pinkman", "Tony Soprano", "Don Draper", "Dexter Morgan",
    "Jon Snow", "Daenerys Targaryen", "Tyrion Lannister", "Cersei Lannister", "Arya Stark",
    "Rick Grimes", "Daryl Dixon", "Negan", "Michonne", "Carol Peletier",
    "Eleven", "Dustin Henderson", "Mike Wheeler", "Hopper", "Steve Harrington",
    "Ted Lasso", "Roy Kent", "Jamie Tartt", "Keeley Jones", "Rebecca Welton",
    "Michael Scott", "Dwight Schrute", "Jim Halpert", "Pam Beesly", "Stanley Hudson",
    "Leslie Knope", "Ron Swanson", "Andy Dwyer", "April Ludgate", "Ben Wyatt",
    "Homer Simpson", "Bart Simpson", "Lisa Simpson", "Marge Simpson", "Maggie Simpson",
    "Peter Griffin", "Stewie Griffin", "Brian Griffin", "Lois Griffin", "Meg Griffin",
    "Rick Sanchez", "Morty Smith", "Summer Smith", "Beth Smith", "Jerry Smith",
    "SpongeBob", "Patrick Star", "Squidward", "Mr Krabs", "Sandy Cheeks",
    "Bugs Bunny", "Daffy Duck", "Tweety", "Sylvester", "Porky Pig",
    "Tom", "Jerry", "Scooby-Doo", "Shaggy", "Velma",
    # Fictional - Cartoons
    "Popeye", "Olive Oyl", "Fred Flintstone", "Barney Rubble", "George Jetson",
    "Dexter", "Johnny Bravo", "Powerpuff Girls", "Samurai Jack", "Ben 10",
    "Avatar Aang", "Korra", "Zuko", "Katara", "Sokka",
    "Finn", "Jake", "Ice King", "Princess Bubblegum", "Marceline",
    "Gumball", "Darwin", "Regular Show", "Mordecai", "Rigby",
    # Russian
    "Чебурашка", "Крокодил Гена", "Винни Пух", "Пятачок", "Кот Леопольд",
    "Волк", "Заяц", "Кот Матроскин", "Шарик", "Дядя Федор",
    "Карлсон", "Малыш", "Домовенок Кузя", "Незнайка", "Буратино",
    # Russian - Real
    "Пушкин", "Толстой", "Достоевский", "Чехов", "Гоголь",
    "Тургенев", "Булгаков", "Пастернак", "Солженицын", "Бродский",
    "Чайковский", "Рахманинов", "Шостакович", "Стравинский", "Прокофьев",
    "Гагарин", "Королев", "Менделеев", "Павлов", "Ломоносов",
]


def get_related_entities(qids: list[str]) -> list[str]:
    """Get entities related to given entities (collaborators, relatives, etc.)."""
    if not qids:
        return []

    related_qids = set()

    # Fetch details of entities to get related people
    entities = get_entity_details(qids[:10])  # Limit to avoid too many requests

    for qid, entity in entities.items():
        claims = entity.get("claims", {})

        # P22 = father, P25 = mother, P26 = spouse, P40 = child
        # P161 = cast member, P57 = director, P175 = performer
        # P1327 = partner in business, P451 = partner
        relation_props = ["P22", "P25", "P26", "P40", "P161", "P57", "P175", "P1327", "P451"]

        for prop in relation_props:
            prop_claims = claims.get(prop, [])
            for claim in prop_claims[:5]:  # Limit per property
                try:
                    related_id = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
                    if related_id and related_id.startswith("Q"):
                        related_qids.add(related_id)
                except (KeyError, TypeError):
                    pass

    return list(related_qids)


async def import_from_searches(
    repo: Repository,
    attr_ids: dict[str, int],
    existing_names: set[str],
    limit: int,
) -> int:
    """Import entities by searching for popular names."""
    count = 0
    checkpoint = load_checkpoint()
    imported_qids = set(checkpoint.get("imported_qids", []))
    pending_qids: list[str] = []  # QIDs to fetch from related entities

    logger.info("Starting search-based import (checkpoint: %d already imported)", len(imported_qids))

    for seed in SEARCH_SEEDS:
        if count >= limit:
            break

        logger.info("Searching: %s", seed)
        results = search_entities(seed, limit=10)  # Reduced limit

        # Only take results that closely match the search query
        qids_to_fetch = []
        seed_lower = seed.lower()
        for item in results:
            qid = item.get("id", "")
            label = item.get("label", "").lower()
            # Only accept if label starts with search term or is very close
            if qid and qid not in imported_qids:
                # Check if this is a close match
                if (label == seed_lower or
                    label.startswith(seed_lower) or
                    seed_lower.startswith(label) or
                    label in seed_lower or
                    seed_lower in label):
                    qids_to_fetch.append(qid)
                    if len(qids_to_fetch) >= 3:  # Max 3 per search
                        break

        if not qids_to_fetch:
            continue

        entities = get_entity_details(qids_to_fetch)

        for qid, entity in entities.items():
            if count >= limit:
                break
            if qid in imported_qids:
                continue

            # Get labels
            labels = entity.get("labels", {})
            en_label = labels.get("en", {}).get("value", "")
            ru_label = labels.get("ru", {}).get("value", "")

            name = en_label or ru_label
            if not name or name.lower() in existing_names:
                continue

            claims = entity.get("claims", {})

            # Validate entity is a real person or fictional character
            is_valid, is_fictional = is_valid_entity(name, claims)
            if not is_valid:
                logger.debug("Skipping invalid entity: %s (%s)", name, qid)
                continue

            # Extract data for attribute building
            gender = extract_gender(claims)
            birth_year = extract_birth_year(claims)
            death_year = extract_death_year(claims)
            occ_qids = get_occupation_qids(claims)

            # Build full attributes using category templates
            attrs = build_entity_attributes(
                claims, is_fictional, occ_qids, birth_year, death_year, gender
            )

            # Save to database
            lang = "ru" if ru_label and not en_label else "en"
            eid = await repo.add_entity(name, f"wikidata:{qid}", "character", lang)

            # Add alias
            if en_label and ru_label and en_label != ru_label:
                if name == en_label:
                    await repo.add_alias(eid, ru_label, "ru")
                else:
                    await repo.add_alias(eid, en_label, "en")

            # Save attributes
            for attr_key, value in attrs.items():
                if attr_key in attr_ids:
                    await repo.set_entity_attribute(eid, attr_ids[attr_key], value)

            existing_names.add(name.lower())
            imported_qids.add(qid)
            pending_qids.append(qid)  # Add to pending for related entity discovery
            count += 1

            if count % 100 == 0:
                logger.info("Progress: %d entities imported", count)
                save_checkpoint({
                    "imported_qids": list(imported_qids),
                    "total_count": count,
                })

        time.sleep(1)  # Rate limiting between searches

    logger.info("Phase 1 complete: %d entities from search seeds", count)

    # Phase 2: Expand by fetching related entities
    logger.info("Phase 2: Expanding via related entities...")
    expansion_rounds = 0
    max_expansion_rounds = 50  # Limit expansion iterations

    while count < limit and pending_qids and expansion_rounds < max_expansion_rounds:
        expansion_rounds += 1
        batch_qids = pending_qids[:50]
        pending_qids = pending_qids[50:]

        logger.info("Expansion round %d: fetching related to %d entities", expansion_rounds, len(batch_qids))

        related = get_related_entities(batch_qids)
        new_qids = [q for q in related if q not in imported_qids]

        if not new_qids:
            continue

        entities = get_entity_details(new_qids)

        for qid, entity in entities.items():
            if count >= limit:
                break
            if qid in imported_qids:
                continue

            labels = entity.get("labels", {})
            en_label = labels.get("en", {}).get("value", "")
            ru_label = labels.get("ru", {}).get("value", "")

            name = en_label or ru_label
            if not name or name.lower() in existing_names:
                imported_qids.add(qid)  # Mark as processed
                continue

            claims = entity.get("claims", {})

            is_valid, is_fictional = is_valid_entity(name, claims)
            if not is_valid:
                imported_qids.add(qid)
                continue

            # Extract data for attribute building
            gender = extract_gender(claims)
            birth_year = extract_birth_year(claims)
            death_year = extract_death_year(claims)
            occ_qids = get_occupation_qids(claims)

            # Build full attributes using category templates
            attrs = build_entity_attributes(
                claims, is_fictional, occ_qids, birth_year, death_year, gender
            )

            lang = "ru" if ru_label and not en_label else "en"
            eid = await repo.add_entity(name, f"wikidata:{qid}", "character", lang)

            if en_label and ru_label and en_label != ru_label:
                if name == en_label:
                    await repo.add_alias(eid, ru_label, "ru")
                else:
                    await repo.add_alias(eid, en_label, "en")

            for attr_key, value in attrs.items():
                if attr_key in attr_ids:
                    await repo.set_entity_attribute(eid, attr_ids[attr_key], value)

            existing_names.add(name.lower())
            imported_qids.add(qid)
            pending_qids.append(qid)
            count += 1

            if count % 100 == 0:
                logger.info("Progress: %d entities imported", count)
                save_checkpoint({
                    "imported_qids": list(imported_qids),
                    "total_count": count,
                })

        time.sleep(0.5)

    save_checkpoint({
        "imported_qids": list(imported_qids),
        "total_count": count,
    })

    return count


async def main() -> None:
    db_path = "data/wikidata_100k.db"
    limit = 100000
    resume = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 1
        elif args[i] == "--db" and i + 1 < len(args):
            db_path = args[i + 1]
            i += 1
        elif args[i] == "--resume":
            resume = True
        i += 1

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

    existing = await repo.get_all_entities()
    existing_names = {e.name.lower() for e in existing}
    logger.info("Database already has %d entities", len(existing_names))

    # Import using search
    total = await import_from_searches(repo, attr_ids, existing_names, limit)

    await repo.close()

    size_mb = os.path.getsize(db_path) / (1024 * 1024)
    logger.info("=" * 60)
    logger.info("DONE! Imported %d new entities", total)
    logger.info("Database: %s (%.1f MB)", db_path, size_mb)
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
