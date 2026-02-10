"""Import entities from Wikidata to scale the database to 100K+.

Run locally (requires internet):
    python -m akinator.import_wikidata              # Import ALL (people + fictional)
    python -m akinator.import_wikidata --people      # Only real people (~60K)
    python -m akinator.import_wikidata --fictional   # Only fictional characters (~40K)
    python -m akinator.import_wikidata --limit 5000  # Limit per category
    python -m akinator.import_wikidata --db path.db  # Custom DB path

After import, copy the DB to repo as backup:
    cp data/akinator.db akinator/data/akinator.db
    git add akinator/data/akinator.db && git commit -m "Update bundled DB"
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

from akinator.db.repository import Repository

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("wikidata_import")

SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "AkinatorBot/2.0 (https://github.com/MyNameIsAlexandro/Akinator_2.0)"

BATCH_SIZE = 400  # Items per SPARQL query (reduced from 2000)
RETRY_DELAYS = [5, 15, 30]  # Exponential backoff delays in seconds (3 retries)

# ── Attributes (must match generate_db.py / seed.py) ──
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
    ("from_usa", "Связан с США?", "Related to USA?", "geography"),
    ("from_europe", "Связан с Европой?", "Related to Europe?", "geography"),
    ("from_russia", "Связан с Россией?", "Related to Russia?", "geography"),
    ("from_asia", "Связан с Азией?", "Related to Asia?", "geography"),
    ("from_japan", "Связан с Японией?", "Related to Japan?", "geography"),
    ("era_ancient", "Из древности (до 500 н.э.)?", "From ancient times (before 500 AD)?", "era"),
    ("era_medieval", "Из средневековья (500-1500)?", "From medieval era (500-1500)?", "era"),
    ("era_modern", "Из нового времени (1500-1900)?", "From modern era (1500-1900)?", "era"),
    ("era_20th_century", "Из 20-го века?", "From the 20th century?", "era"),
    ("era_21st_century", "Из 21-го века?", "From the 21st century?", "era"),
    ("has_superpower", "Обладает сверхспособностями?", "Has superpowers?", "traits"),
    ("wears_uniform", "Носит униформу/костюм?", "Wears a uniform/costume?", "traits"),
    ("has_famous_catchphrase", "Известен крылатой фразой?", "Known for a famous catchphrase?", "traits"),
    ("is_leader", "Является лидером/главой?", "Is a leader/head?", "traits"),
    ("is_wealthy", "Богатый/знатный?", "Wealthy/noble?", "traits"),
]

# ── SPARQL queries ──
# Lightweight: no GROUP_CONCAT, uses SERVICE wikibase:label

QUERY_PEOPLE_IDS = """
SELECT ?item ?itemLabel ?ruLabel WHERE {{
  ?item wdt:P31 wd:Q5 .
  ?item wikibase:sitelinks ?sitelinks .
  hint:Prior hint:rangeSafe true .
  FILTER(?sitelinks > {min_sitelinks})
  OPTIONAL {{ ?item rdfs:label ?ruLabel . FILTER(LANG(?ruLabel) = "ru") }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}
LIMIT {limit}
OFFSET {offset}
"""

QUERY_FICTIONAL_IDS = """
SELECT ?item ?itemLabel ?ruLabel WHERE {{
  {{ ?item wdt:P31/wdt:P279* wd:Q95074 . }}
  UNION
  {{ ?item wdt:P31/wdt:P279* wd:Q15632617 . }}
  ?item wikibase:sitelinks ?sitelinks .
  hint:Prior hint:rangeSafe true .
  FILTER(?sitelinks > {min_sitelinks})
  OPTIONAL {{ ?item rdfs:label ?ruLabel . FILTER(LANG(?ruLabel) = "ru") }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}
LIMIT {limit}
OFFSET {offset}
"""

# Separate lightweight property queries (batched via VALUES)

QUERY_GENDER = """
SELECT ?item ?genderLabel WHERE {{
  VALUES ?item {{ {values} }}
  ?item wdt:P21 ?gender .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}
"""

QUERY_BIRTH_DEATH = """
SELECT ?item ?birthYear ?deathYear WHERE {{
  VALUES ?item {{ {values} }}
  OPTIONAL {{ ?item wdt:P569 ?birth . BIND(YEAR(?birth) AS ?birthYear) }}
  OPTIONAL {{ ?item wdt:P570 ?death . BIND(YEAR(?death) AS ?deathYear) }}
}}
"""

QUERY_COUNTRY = """
SELECT ?item ?countryLabel WHERE {{
  VALUES ?item {{ {values} }}
  ?item wdt:P27 ?country .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}
"""

QUERY_OCCUPATIONS = """
SELECT ?item ?occupationLabel WHERE {{
  VALUES ?item {{ {values} }}
  ?item wdt:P106 ?occupation .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}
"""

QUERY_UNIVERSE = """
SELECT ?item ?universeLabel WHERE {{
  VALUES ?item {{ {values} }}
  ?item wdt:P1080 ?universe .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}
"""

QUERY_MEDIA = """
SELECT ?item ?mediaLabel WHERE {{
  VALUES ?item {{ {values} }}
  ?item wdt:P449 ?media .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}
"""

# ── Mapping tables ──

OCCUPATION_ATTRS: dict[str, dict[str, float]] = {
    "politician": {"from_politics": 1.0, "is_leader": 0.8},
    "head of state": {"from_politics": 1.0, "is_leader": 1.0},
    "head of government": {"from_politics": 1.0, "is_leader": 1.0},
    "monarch": {"from_politics": 1.0, "is_leader": 1.0, "is_wealthy": 1.0},
    "emperor": {"from_politics": 1.0, "is_leader": 1.0, "is_wealthy": 1.0},
    "pharaoh": {"from_politics": 1.0, "is_leader": 1.0, "is_wealthy": 1.0},
    "pope": {"from_politics": 0.5, "is_leader": 1.0},
    "physicist": {"from_science": 1.0},
    "mathematician": {"from_science": 1.0},
    "chemist": {"from_science": 1.0},
    "biologist": {"from_science": 1.0},
    "astronomer": {"from_science": 1.0},
    "inventor": {"from_science": 0.8},
    "engineer": {"from_science": 0.7},
    "computer scientist": {"from_science": 1.0},
    "singer": {"from_music": 1.0},
    "musician": {"from_music": 1.0},
    "composer": {"from_music": 1.0},
    "rapper": {"from_music": 1.0},
    "guitarist": {"from_music": 1.0},
    "pianist": {"from_music": 1.0},
    "singer-songwriter": {"from_music": 1.0},
    "conductor": {"from_music": 1.0},
    "disc jockey": {"from_music": 1.0},
    "actor": {"from_movie": 0.9},
    "film actor": {"from_movie": 1.0},
    "television actor": {"from_tv_series": 1.0, "from_movie": 0.5},
    "stage actor": {"from_movie": 0.4},
    "voice actor": {"from_movie": 0.5, "from_anime": 0.3},
    "film director": {"from_movie": 1.0},
    "television presenter": {"from_tv_series": 1.0},
    "screenwriter": {"from_movie": 0.8},
    "film producer": {"from_movie": 0.9, "is_wealthy": 0.7},
    "association football player": {"from_sport": 1.0, "wears_uniform": 1.0},
    "basketball player": {"from_sport": 1.0, "wears_uniform": 1.0},
    "tennis player": {"from_sport": 1.0},
    "boxer": {"from_sport": 1.0},
    "swimmer": {"from_sport": 1.0},
    "athlete": {"from_sport": 1.0},
    "ice hockey player": {"from_sport": 1.0, "wears_uniform": 1.0},
    "baseball player": {"from_sport": 1.0, "wears_uniform": 1.0},
    "cricket player": {"from_sport": 1.0, "wears_uniform": 1.0},
    "racing driver": {"from_sport": 1.0, "wears_uniform": 1.0},
    "mixed martial artist": {"from_sport": 1.0},
    "chess player": {"from_sport": 0.5},
    "writer": {"from_book": 1.0},
    "novelist": {"from_book": 1.0},
    "poet": {"from_book": 1.0},
    "playwright": {"from_book": 1.0},
    "journalist": {"from_book": 0.3},
    "painter": {},
    "sculptor": {},
    "architect": {},
    "photographer": {},
    "military officer": {"wears_uniform": 1.0, "is_leader": 0.6},
    "general": {"wears_uniform": 1.0, "is_leader": 1.0, "from_history": 0.7},
    "admiral": {"wears_uniform": 1.0, "is_leader": 1.0},
    "astronaut": {"from_science": 0.5, "wears_uniform": 1.0},
    "cosmonaut": {"from_science": 0.5, "wears_uniform": 1.0, "from_russia": 1.0},
    "businessperson": {"is_wealthy": 0.8},
    "entrepreneur": {"is_wealthy": 0.8},
    "YouTuber": {"era_21st_century": 1.0},
    "model": {},
    "fashion designer": {"is_wealthy": 0.7},
    "chef": {},
    "spy": {"wears_uniform": 0.3},
}

COUNTRY_ATTRS: dict[str, dict[str, float]] = {
    "United States of America": {"from_usa": 1.0},
    "United States": {"from_usa": 1.0},
    "United Kingdom": {"from_europe": 1.0},
    "England": {"from_europe": 1.0},
    "Scotland": {"from_europe": 1.0},
    "France": {"from_europe": 1.0},
    "Germany": {"from_europe": 1.0},
    "Italy": {"from_europe": 1.0},
    "Spain": {"from_europe": 1.0},
    "Portugal": {"from_europe": 1.0},
    "Netherlands": {"from_europe": 1.0},
    "Belgium": {"from_europe": 1.0},
    "Switzerland": {"from_europe": 1.0},
    "Austria": {"from_europe": 1.0},
    "Sweden": {"from_europe": 1.0},
    "Norway": {"from_europe": 1.0},
    "Denmark": {"from_europe": 1.0},
    "Finland": {"from_europe": 1.0},
    "Poland": {"from_europe": 1.0},
    "Czech Republic": {"from_europe": 1.0},
    "Hungary": {"from_europe": 1.0},
    "Romania": {"from_europe": 1.0},
    "Greece": {"from_europe": 1.0},
    "Ireland": {"from_europe": 1.0},
    "Russia": {"from_russia": 1.0},
    "Russian Empire": {"from_russia": 1.0},
    "Soviet Union": {"from_russia": 1.0},
    "USSR": {"from_russia": 1.0},
    "Japan": {"from_japan": 1.0, "from_asia": 1.0},
    "China": {"from_asia": 1.0},
    "People's Republic of China": {"from_asia": 1.0},
    "South Korea": {"from_asia": 1.0},
    "India": {"from_asia": 1.0},
    "Indonesia": {"from_asia": 1.0},
    "Thailand": {"from_asia": 1.0},
    "Turkey": {"from_asia": 0.5, "from_europe": 0.5},
    "Brazil": {},
    "Argentina": {},
    "Mexico": {},
    "Canada": {"from_usa": 0.5},
    "Australia": {},
}

UNIVERSE_ATTRS: dict[str, dict[str, float]] = {
    "marvel": {"from_comics": 1.0, "from_movie": 0.8, "from_usa": 1.0, "has_superpower": 0.8, "wears_uniform": 0.8, "era_21st_century": 0.7},
    "dc": {"from_comics": 1.0, "from_movie": 0.7, "from_usa": 1.0, "has_superpower": 0.8, "wears_uniform": 0.8, "era_21st_century": 0.7},
    "star wars": {"from_movie": 1.0, "from_usa": 1.0, "has_superpower": 0.5},
    "middle-earth": {"from_book": 1.0, "from_movie": 1.0, "from_europe": 0.7, "era_medieval": 0.5},
    "wizarding world": {"from_book": 1.0, "from_movie": 1.0, "from_europe": 1.0, "has_superpower": 0.9, "era_21st_century": 0.8},
    "harry potter": {"from_book": 1.0, "from_movie": 1.0, "from_europe": 1.0, "has_superpower": 0.9, "era_21st_century": 0.8},
    "dragon ball": {"from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0, "has_superpower": 1.0, "era_21st_century": 0.6},
    "naruto": {"from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0, "has_superpower": 0.8, "era_21st_century": 0.7},
    "one piece": {"from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0, "has_superpower": 0.7, "era_21st_century": 0.7},
    "pokémon": {"from_anime": 1.0, "from_game": 1.0, "from_japan": 1.0, "from_asia": 1.0, "is_human": 0.3, "era_21st_century": 0.7},
    "disney": {"from_movie": 1.0, "from_usa": 1.0, "era_21st_century": 0.6},
    "simpsons": {"from_tv_series": 1.0, "from_usa": 1.0, "era_21st_century": 0.8},
    "game of thrones": {"from_tv_series": 1.0, "from_book": 1.0, "era_medieval": 0.8, "from_europe": 0.7},
    "sonic": {"from_game": 1.0, "from_japan": 1.0, "has_superpower": 0.7, "is_human": 0.0},
    "super mario": {"from_game": 1.0, "from_japan": 1.0, "is_human": 0.8},
    "zelda": {"from_game": 1.0, "from_japan": 1.0},
    "final fantasy": {"from_game": 1.0, "from_japan": 1.0},
    "street fighter": {"from_game": 1.0, "from_japan": 1.0},
    "transformers": {"from_movie": 1.0, "from_usa": 1.0, "is_human": 0.0, "has_superpower": 0.7},
    "shrek": {"from_movie": 1.0, "from_usa": 1.0, "is_human": 0.3},
    "spongebob": {"from_tv_series": 1.0, "from_usa": 1.0, "is_human": 0.0},
    "south park": {"from_tv_series": 1.0, "from_usa": 1.0, "era_21st_century": 0.9},
    "family guy": {"from_tv_series": 1.0, "from_usa": 1.0, "era_21st_century": 0.8},
    "rick and morty": {"from_tv_series": 1.0, "from_usa": 1.0, "era_21st_century": 1.0},
    "sherlock holmes": {"from_book": 1.0, "from_europe": 1.0, "era_modern": 0.8, "is_human": 1.0},
    "breaking bad": {"from_tv_series": 1.0, "from_usa": 1.0, "era_21st_century": 1.0, "is_human": 1.0},
    "stranger things": {"from_tv_series": 1.0, "from_usa": 1.0, "era_20th_century": 0.8, "has_superpower": 0.5},
    "demon slayer": {"from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0, "has_superpower": 0.8},
    "attack on titan": {"from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0, "has_superpower": 0.6, "from_europe": 0.5},
    "jojo": {"from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0, "has_superpower": 1.0},
    "death note": {"from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0, "has_superpower": 0.8},
    "hunter": {"from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0, "has_superpower": 0.7},
    "bleach": {"from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0, "has_superpower": 0.9},
    "my hero academia": {"from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0, "has_superpower": 1.0},
    "mortal kombat": {"from_game": 1.0, "from_usa": 1.0, "has_superpower": 0.7},
    "resident evil": {"from_game": 1.0, "from_japan": 1.0},
    "witcher": {"from_game": 1.0, "from_book": 1.0, "from_europe": 1.0, "era_medieval": 0.7, "has_superpower": 0.6},
    "minecraft": {"from_game": 1.0},
    "overwatch": {"from_game": 1.0, "from_usa": 0.5, "has_superpower": 0.5, "wears_uniform": 0.8},
    "genshin": {"from_game": 1.0, "from_asia": 1.0, "has_superpower": 0.8},
}

# Fictional character occupation → attribute mappings
FICTIONAL_OCCUPATION_ATTRS: dict[str, dict[str, float]] = {
    "villain": {"is_villain": 1.0},
    "antagonist": {"is_villain": 0.9},
    "supervillain": {"is_villain": 1.0, "has_superpower": 0.9},
    "superhero": {"is_villain": 0.0, "has_superpower": 0.9, "wears_uniform": 0.8},
    "hero": {"is_villain": 0.0},
    "king": {"is_leader": 1.0, "is_wealthy": 0.9},
    "queen": {"is_leader": 1.0, "is_wealthy": 0.9, "is_male": 0.0},
    "prince": {"is_wealthy": 0.8, "is_leader": 0.5},
    "princess": {"is_wealthy": 0.8, "is_leader": 0.5, "is_male": 0.0},
    "pirate": {"is_villain": 0.5, "wears_uniform": 0.5},
    "knight": {"wears_uniform": 1.0, "is_leader": 0.4},
    "soldier": {"wears_uniform": 1.0},
    "warrior": {"wears_uniform": 0.6},
    "wizard": {"has_superpower": 0.9},
    "witch": {"has_superpower": 0.9, "is_male": 0.0},
    "detective": {"is_human": 1.0},
    "robot": {"is_human": 0.0},
    "android": {"is_human": 0.1},
    "cyborg": {"is_human": 0.5, "has_superpower": 0.6},
    "alien": {"is_human": 0.0},
    "god": {"has_superpower": 1.0, "is_leader": 0.7, "is_human": 0.3},
    "deity": {"has_superpower": 1.0, "is_leader": 0.7, "is_human": 0.3},
    "demon": {"has_superpower": 0.8, "is_villain": 0.7, "is_human": 0.0},
    "vampire": {"has_superpower": 0.7, "is_human": 0.3},
    "monster": {"is_human": 0.0, "is_villain": 0.5},
    "ninja": {"has_superpower": 0.4, "wears_uniform": 0.7, "from_asia": 0.7},
    "spy": {"is_human": 1.0},
    "thief": {"is_villain": 0.5},
    "assassin": {"is_villain": 0.6},
    "scientist": {"from_science": 0.7, "is_human": 1.0},
    "doctor": {"is_human": 1.0},
}


# ── Helpers ──

def _qid(uri: str) -> str:
    """Extract QID from Wikidata URI, e.g. 'http://www.wikidata.org/entity/Q42' -> 'Q42'."""
    return uri.rsplit("/", 1)[-1]


def _values_clause(qids: list[str]) -> str:
    """Build SPARQL VALUES clause content: 'wd:Q42 wd:Q76 ...'."""
    return " ".join(f"wd:{qid}" for qid in qids)


def _sparql_query(query: str) -> list[dict]:
    """Execute a SPARQL query with retry and exponential backoff."""
    url = f"{SPARQL_URL}?format=json&query={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})

    max_attempts = len(RETRY_DELAYS) + 1
    for attempt in range(max_attempts):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
            return data.get("results", {}).get("bindings", [])
        except Exception as e:
            if attempt < len(RETRY_DELAYS):
                delay = RETRY_DELAYS[attempt]
                logger.warning("SPARQL attempt %d/%d failed: %s. Retrying in %ds...",
                               attempt + 1, max_attempts, e, delay)
                time.sleep(delay)
            else:
                logger.error("SPARQL query failed after %d attempts: %s", max_attempts, e)
                return []


def _val(row: dict, key: str) -> str | None:
    v = row.get(key)
    return v["value"] if v else None


def _int_val(row: dict, key: str) -> int | None:
    v = _val(row, key)
    if v is None:
        return None
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


def _fetch_property(query_template: str, qids: list[str], key: str) -> dict[str, list[str]]:
    """Fetch a multi-value property for a batch of QIDs. Returns {qid: [values]}."""
    if not qids:
        return {}
    values = _values_clause(qids)
    rows = _sparql_query(query_template.format(values=values))
    result: dict[str, list[str]] = {}
    for row in rows:
        item = _val(row, "item")
        val = _val(row, key)
        if item and val:
            qid = _qid(item)
            result.setdefault(qid, []).append(val)
    time.sleep(1)
    return result


def _fetch_single_property(query_template: str, qids: list[str], key: str) -> dict[str, str]:
    """Fetch a single-value property for a batch of QIDs. Returns {qid: first_value}."""
    if not qids:
        return {}
    values = _values_clause(qids)
    rows = _sparql_query(query_template.format(values=values))
    result: dict[str, str] = {}
    for row in rows:
        item = _val(row, "item")
        val = _val(row, key)
        if item and val:
            qid = _qid(item)
            if qid not in result:
                result[qid] = val
    time.sleep(1)
    return result


def _fetch_birth_death(qids: list[str]) -> dict[str, tuple[int | None, int | None]]:
    """Fetch birth and death years for a batch of QIDs."""
    if not qids:
        return {}
    values = _values_clause(qids)
    rows = _sparql_query(QUERY_BIRTH_DEATH.format(values=values))
    result: dict[str, tuple[int | None, int | None]] = {}
    for row in rows:
        item = _val(row, "item")
        if item:
            qid = _qid(item)
            if qid not in result:
                result[qid] = (_int_val(row, "birthYear"), _int_val(row, "deathYear"))
    time.sleep(1)
    return result


def _era_attrs(birth: int | None, death: int | None) -> dict[str, float]:
    a: dict[str, float] = {}
    if birth is None:
        return a
    if birth < 500:
        a["era_ancient"] = 1.0
        a["from_history"] = 1.0
    elif birth < 1500:
        a["era_medieval"] = 1.0
        a["from_history"] = 1.0
    elif birth < 1900:
        a["era_modern"] = 1.0
        a["from_history"] = 0.8
    elif birth < 2000:
        a["era_20th_century"] = 1.0
    else:
        a["era_21st_century"] = 1.0
    a["is_alive"] = 0.0 if death is not None else (0.0 if birth < 1930 else 1.0)
    return a


def _occupation_attrs(occupations_str: str | None) -> dict[str, float]:
    if not occupations_str:
        return {}
    a: dict[str, float] = {}
    for occ in occupations_str.split("|"):
        occ_lower = occ.strip().lower()
        for key, vals in OCCUPATION_ATTRS.items():
            if key in occ_lower:
                a.update(vals)
    return a


def _country_attrs(country: str | None) -> dict[str, float]:
    if not country:
        return {}
    for key, vals in COUNTRY_ATTRS.items():
        if key.lower() in country.lower() or country.lower() in key.lower():
            return dict(vals)
    # European countries catch-all
    european = ["Ukraine", "Serbia", "Croatia", "Bulgaria", "Slovakia", "Slovenia",
                "Latvia", "Lithuania", "Estonia", "Iceland", "Albania", "Macedonia"]
    for eu in european:
        if eu.lower() in country.lower():
            return {"from_europe": 1.0}
    return {}


def _universe_attrs(universes: str | None, medias: str | None) -> dict[str, float]:
    a: dict[str, float] = {}
    for text in [universes or "", medias or ""]:
        text_lower = text.lower()
        for key, vals in UNIVERSE_ATTRS.items():
            if key in text_lower:
                a.update(vals)
    return a


def _is_cyrillic(s: str) -> bool:
    return any("\u0400" <= c <= "\u04ff" for c in s)


# ── Import functions ──

async def import_people(repo: Repository, attr_ids: dict[str, int],
                        existing_names: set[str], limit: int = 60000) -> int:
    """Import famous real people from Wikidata."""
    logger.info("=" * 60)
    logger.info("IMPORTING REAL PEOPLE (limit=%d)", limit)
    logger.info("=" * 60)

    count = 0
    batch = BATCH_SIZE
    thresholds = [(100, min(limit, 15000)), (50, min(limit, 30000)),
                  (30, min(limit, 50000)), (15, min(limit, 70000)),
                  (8, limit)]

    for min_sl, phase_limit in thresholds:
        if count >= limit:
            break
        logger.info("--- Phase: sitelinks > %d (target: %d) ---", min_sl, phase_limit)

        for offset in range(0, phase_limit, batch):
            if count >= limit:
                break

            # Step 1: Fetch IDs and labels (lightweight, no properties)
            query = QUERY_PEOPLE_IDS.format(min_sitelinks=min_sl, limit=batch, offset=offset)
            rows = _sparql_query(query)
            if not rows:
                logger.info("  No more results at offset %d", offset)
                break

            # Parse entities, deduplicate by QID
            entities: dict[str, dict] = {}
            for row in rows:
                item = _val(row, "item")
                if not item:
                    continue
                qid = _qid(item)
                if qid in entities:
                    continue
                en_name = _val(row, "itemLabel")
                ru_name = _val(row, "ruLabel")
                name = en_name or ru_name
                if not name or name.startswith("Q"):
                    continue
                if name.lower() in existing_names:
                    continue
                entities[qid] = {"en_name": en_name, "ru_name": ru_name, "name": name}

            if not entities:
                logger.info("  No new entities at offset %d", offset)
                time.sleep(1)
                continue

            qids = list(entities.keys())

            # Step 2: Fetch properties in separate lightweight queries
            time.sleep(1)
            genders = _fetch_single_property(QUERY_GENDER, qids, "genderLabel")
            birth_deaths = _fetch_birth_death(qids)
            countries = _fetch_single_property(QUERY_COUNTRY, qids, "countryLabel")
            occupations = _fetch_property(QUERY_OCCUPATIONS, qids, "occupationLabel")

            # Step 3: Process and insert into DB
            new_in_batch = 0
            for qid, info in entities.items():
                if count >= limit:
                    break

                name = info["name"]
                en_name = info["en_name"]
                ru_name = info["ru_name"]

                attrs: dict[str, float] = {
                    "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
                }

                # Gender
                gender = genders.get(qid)
                if gender:
                    attrs["is_male"] = 1.0 if "male" in gender.lower() and "female" not in gender.lower() else 0.0

                # Country
                attrs.update(_country_attrs(countries.get(qid)))

                # Era
                bd = birth_deaths.get(qid, (None, None))
                attrs.update(_era_attrs(bd[0], bd[1]))

                # Occupations
                occ_list = occupations.get(qid, [])
                attrs.update(_occupation_attrs("|".join(occ_list)))

                lang = "ru" if (_is_cyrillic(name)) else "en"
                eid = await repo.add_entity(name, "wikidata", "person", lang)

                # Add alias in the other language if both names exist and differ
                if en_name and ru_name and en_name != ru_name:
                    if name == en_name:
                        await repo.add_alias(eid, ru_name, "ru")
                    else:
                        await repo.add_alias(eid, en_name, "en")

                for attr_key, value in attrs.items():
                    if attr_key in attr_ids:
                        await repo.set_entity_attribute(eid, attr_ids[attr_key], value)

                existing_names.add(name.lower())
                count += 1
                new_in_batch += 1

            logger.info("  offset=%d: +%d new (total: %d)", offset, new_in_batch, count)

    logger.info("Imported %d real people", count)
    return count


async def import_fictional(repo: Repository, attr_ids: dict[str, int],
                           existing_names: set[str], limit: int = 40000) -> int:
    """Import fictional characters from Wikidata."""
    logger.info("=" * 60)
    logger.info("IMPORTING FICTIONAL CHARACTERS (limit=%d)", limit)
    logger.info("=" * 60)

    count = 0
    batch = BATCH_SIZE
    thresholds = [(30, min(limit, 10000)), (15, min(limit, 25000)),
                  (5, min(limit, 40000)), (3, limit)]

    for min_sl, phase_limit in thresholds:
        if count >= limit:
            break
        logger.info("--- Phase: sitelinks > %d (target: %d) ---", min_sl, phase_limit)

        for offset in range(0, phase_limit, batch):
            if count >= limit:
                break

            # Step 1: Fetch IDs and labels (lightweight)
            query = QUERY_FICTIONAL_IDS.format(min_sitelinks=min_sl, limit=batch, offset=offset)
            rows = _sparql_query(query)
            if not rows:
                logger.info("  No more results at offset %d", offset)
                break

            # Parse entities, deduplicate by QID
            entities: dict[str, dict] = {}
            for row in rows:
                item = _val(row, "item")
                if not item:
                    continue
                qid = _qid(item)
                if qid in entities:
                    continue
                en_name = _val(row, "itemLabel")
                ru_name = _val(row, "ruLabel")
                name = en_name or ru_name
                if not name or name.startswith("Q"):
                    continue
                if name.lower() in existing_names:
                    continue
                entities[qid] = {"en_name": en_name, "ru_name": ru_name, "name": name}

            if not entities:
                logger.info("  No new entities at offset %d", offset)
                time.sleep(1)
                continue

            qids = list(entities.keys())

            # Step 2: Fetch properties in separate lightweight queries
            time.sleep(1)
            genders = _fetch_single_property(QUERY_GENDER, qids, "genderLabel")
            universes = _fetch_property(QUERY_UNIVERSE, qids, "universeLabel")
            medias = _fetch_property(QUERY_MEDIA, qids, "mediaLabel")
            occupations = _fetch_property(QUERY_OCCUPATIONS, qids, "occupationLabel")

            # Step 3: Process and insert into DB
            new_in_batch = 0
            for qid, info in entities.items():
                if count >= limit:
                    break

                name = info["name"]
                en_name = info["en_name"]
                ru_name = info["ru_name"]

                attrs: dict[str, float] = {
                    "is_fictional": 1.0, "is_adult": 1.0, "is_human": 0.8,
                }

                # Gender
                gender = genders.get(qid)
                if gender:
                    attrs["is_male"] = 1.0 if "male" in gender.lower() and "female" not in gender.lower() else 0.0

                # Universe / Media
                uni_list = universes.get(qid, [])
                med_list = medias.get(qid, [])
                attrs.update(_universe_attrs("|".join(uni_list), "|".join(med_list)))

                # Occupations (villain, hero, robot, etc.)
                occ_list = occupations.get(qid, [])
                for occ in occ_list:
                    occ_lower = occ.strip().lower()
                    for key, vals in FICTIONAL_OCCUPATION_ATTRS.items():
                        if key in occ_lower:
                            attrs.update(vals)

                lang = "ru" if _is_cyrillic(name) else "en"
                eid = await repo.add_entity(name, "wikidata", "character", lang)

                if en_name and ru_name and en_name != ru_name:
                    if name == en_name:
                        await repo.add_alias(eid, ru_name, "ru")
                    else:
                        await repo.add_alias(eid, en_name, "en")

                for attr_key, value in attrs.items():
                    if attr_key in attr_ids:
                        await repo.set_entity_attribute(eid, attr_ids[attr_key], value)

                existing_names.add(name.lower())
                count += 1
                new_in_batch += 1

            logger.info("  offset=%d: +%d new (total: %d)", offset, new_in_batch, count)

    logger.info("Imported %d fictional characters", count)
    return count


async def main() -> None:
    db_path = "data/akinator.db"
    do_people = True
    do_fictional = True
    limit = 50000

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--people":
            do_fictional = False
        elif args[i] == "--fictional":
            do_people = False
        elif args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 1
        elif args[i] == "--db" and i + 1 < len(args):
            db_path = args[i + 1]
            i += 1
        i += 1

    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    repo = Repository(db_path)
    await repo.init_db()

    # Ensure attributes exist
    existing_attrs = await repo.get_all_attributes()
    if not existing_attrs:
        logger.info("Creating attributes...")
        for key, q_ru, q_en, cat in ATTRIBUTES:
            await repo.add_attribute(key, q_ru, q_en, cat)

    attr_list = await repo.get_all_attributes()
    attr_ids = {a.key: a.id for a in attr_list}

    existing = await repo.get_all_entities()
    existing_names = {e.name.lower() for e in existing}
    logger.info("Database already has %d entities", len(existing_names))

    total = 0
    if do_people:
        total += await import_people(repo, attr_ids, existing_names, limit)
    if do_fictional:
        total += await import_fictional(repo, attr_ids, existing_names, limit)

    await repo.close()

    size_mb = os.path.getsize(db_path) / (1024 * 1024)
    final_count = len(existing_names)
    logger.info("=" * 60)
    logger.info("DONE! Added %d entities (total in DB: %d)", total, final_count)
    logger.info("Database: %s (%.1f MB)", db_path, size_mb)
    logger.info("")
    logger.info("To use as bundled backup:")
    logger.info("  cp %s akinator/data/akinator.db", db_path)
    logger.info("  git add akinator/data/akinator.db")
    logger.info("  git commit -m 'Update bundled database'")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
