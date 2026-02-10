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

# ── Attributes (must match generate_db.py - expanded to 62) ──
ATTRIBUTES = [
    # Identity
    ("is_fictional", "Этот персонаж вымышленный?", "Is this character fictional?", "identity"),
    ("is_male", "Это мужчина/мужской персонаж?", "Is this a male character?", "identity"),
    ("is_human", "Это человек (или человекоподобный)?", "Is this a human (or humanoid)?", "identity"),
    ("is_alive", "Этот персонаж/человек жив?", "Is this character/person alive?", "identity"),
    ("is_adult", "Это взрослый персонаж?", "Is this an adult character?", "identity"),
    ("is_villain", "Это злодей/антигерой?", "Is this a villain/antagonist?", "identity"),

    # Media
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

    # Geography
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

    # Era
    ("era_ancient", "Из древности (до 500 н.э.)?", "From ancient times (before 500 AD)?", "era"),
    ("era_medieval", "Из средневековья (500-1500)?", "From medieval era (500-1500)?", "era"),
    ("era_modern", "Из нового времени (1500-1900)?", "From modern era (1500-1900)?", "era"),
    ("era_20th_century", "Из 20-го века?", "From the 20th century?", "era"),
    ("era_21st_century", "Из 21-го века?", "From the 21st century?", "era"),

    # Birth Decades (for real people)
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

    # Traits
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

# ── SPARQL queries ──
# Each query fetches entity + label in EN and RU + key properties

QUERY_PEOPLE = """
SELECT DISTINCT ?item ?enLabel ?ruLabel ?genderLabel
       ?countryLabel ?birthYear ?deathYear
       (GROUP_CONCAT(DISTINCT ?occupationLabel; SEPARATOR="|") AS ?occupations)
WHERE {{
  ?item wdt:P31 wd:Q5 .
  ?item wikibase:sitelinks ?sitelinks .
  FILTER(?sitelinks > {min_sitelinks})
  OPTIONAL {{ ?item rdfs:label ?enLabel . FILTER(LANG(?enLabel) = "en") }}
  OPTIONAL {{ ?item rdfs:label ?ruLabel . FILTER(LANG(?ruLabel) = "ru") }}
  OPTIONAL {{ ?item wdt:P21 ?gender . ?gender rdfs:label ?genderLabel . FILTER(LANG(?genderLabel) = "en") }}
  OPTIONAL {{ ?item wdt:P27 ?country . ?country rdfs:label ?countryLabel . FILTER(LANG(?countryLabel) = "en") }}
  OPTIONAL {{ ?item wdt:P569 ?birth . BIND(YEAR(?birth) AS ?birthYear) }}
  OPTIONAL {{ ?item wdt:P570 ?death . BIND(YEAR(?death) AS ?deathYear) }}
  OPTIONAL {{ ?item wdt:P106 ?occupation . ?occupation rdfs:label ?occupationLabel . FILTER(LANG(?occupationLabel) = "en") }}
}}
GROUP BY ?item ?enLabel ?ruLabel ?genderLabel ?countryLabel ?birthYear ?deathYear
LIMIT {limit}
OFFSET {offset}
"""

QUERY_FICTIONAL = """
SELECT DISTINCT ?item ?enLabel ?ruLabel ?genderLabel
       (GROUP_CONCAT(DISTINCT ?universeLabel; SEPARATOR="|") AS ?universes)
       (GROUP_CONCAT(DISTINCT ?mediaLabel; SEPARATOR="|") AS ?medias)
WHERE {{
  {{ ?item wdt:P31/wdt:P279* wd:Q95074 . }}
  UNION
  {{ ?item wdt:P31/wdt:P279* wd:Q15632617 . }}
  ?item wikibase:sitelinks ?sitelinks .
  FILTER(?sitelinks > {min_sitelinks})
  OPTIONAL {{ ?item rdfs:label ?enLabel . FILTER(LANG(?enLabel) = "en") }}
  OPTIONAL {{ ?item rdfs:label ?ruLabel . FILTER(LANG(?ruLabel) = "ru") }}
  OPTIONAL {{ ?item wdt:P21 ?gender . ?gender rdfs:label ?genderLabel . FILTER(LANG(?genderLabel) = "en") }}
  OPTIONAL {{ ?item wdt:P1080 ?universe . ?universe rdfs:label ?universeLabel . FILTER(LANG(?universeLabel) = "en") }}
  OPTIONAL {{ ?item wdt:P449 ?media . ?media rdfs:label ?mediaLabel . FILTER(LANG(?mediaLabel) = "en") }}
}}
GROUP BY ?item ?enLabel ?ruLabel ?genderLabel
LIMIT {limit}
OFFSET {offset}
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
    "marvel": {"from_comics": 1.0, "from_movie": 0.8, "from_usa": 1.0, "has_superpower": 0.8, "wears_uniform": 0.8},
    "dc": {"from_comics": 1.0, "from_movie": 0.7, "from_usa": 1.0, "has_superpower": 0.8, "wears_uniform": 0.8},
    "star wars": {"from_movie": 1.0, "from_usa": 1.0},
    "middle-earth": {"from_book": 1.0, "from_movie": 1.0, "from_europe": 0.7, "era_medieval": 0.5},
    "wizarding world": {"from_book": 1.0, "from_movie": 1.0, "from_europe": 1.0, "has_superpower": 0.9},
    "harry potter": {"from_book": 1.0, "from_movie": 1.0, "from_europe": 1.0, "has_superpower": 0.9},
    "dragon ball": {"from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0, "has_superpower": 1.0},
    "naruto": {"from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0, "has_superpower": 0.8},
    "one piece": {"from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0, "has_superpower": 0.7},
    "pokémon": {"from_anime": 1.0, "from_game": 1.0, "from_japan": 1.0, "from_asia": 1.0},
    "disney": {"from_movie": 1.0, "from_usa": 1.0},
    "simpsons": {"from_tv_series": 1.0, "from_usa": 1.0},
    "game of thrones": {"from_tv_series": 1.0, "from_book": 1.0, "era_medieval": 0.8},
    "sonic": {"from_game": 1.0, "from_japan": 1.0, "has_superpower": 0.7},
    "super mario": {"from_game": 1.0, "from_japan": 1.0},
    "zelda": {"from_game": 1.0, "from_japan": 1.0},
    "final fantasy": {"from_game": 1.0, "from_japan": 1.0},
    "street fighter": {"from_game": 1.0, "from_japan": 1.0},
}


def _sparql_query(query: str, max_retries: int = 3) -> list[dict]:
    """Execute a SPARQL query against Wikidata with retry logic."""
    url = f"{SPARQL_URL}?format=json&query={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:  # Reduced timeout from 120 to 60
                data = json.loads(resp.read().decode())
            return data.get("results", {}).get("bindings", [])
        except urllib.error.HTTPError as e:
            if e.code == 504:  # Gateway Timeout
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning("Timeout (504) on attempt %d/%d, retrying in %ds...",
                             attempt + 1, max_retries, wait_time)
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
            logger.error("SPARQL request failed: HTTP %d - %s", e.code, e.reason)
            return []
        except Exception as e:
            logger.error("SPARQL request failed on attempt %d: %s", attempt + 1, e)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return []

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
    batch = 100  # Reduced from 2000 to avoid timeouts
    # Start with very famous (100+ sitelinks), then widen to less famous
    thresholds = [(100, min(limit, 15000)), (50, min(limit, 30000)),
                  (30, min(limit, 50000)), (15, limit)]

    for min_sl, phase_limit in thresholds:
        if count >= limit:
            break
        logger.info("--- Phase: sitelinks > %d (target: %d) ---", min_sl, phase_limit)

        for offset in range(0, phase_limit, batch):
            if count >= limit:
                break

            query = QUERY_PEOPLE.format(min_sitelinks=min_sl, limit=batch, offset=offset)
            rows = _sparql_query(query)
            if not rows:
                logger.info("  No more results at offset %d", offset)
                break

            new_in_batch = 0
            for row in rows:
                en_name = _val(row, "enLabel")
                ru_name = _val(row, "ruLabel")
                name = en_name or ru_name
                if not name or name.startswith("Q"):
                    continue
                if name.lower() in existing_names:
                    continue

                attrs: dict[str, float] = {
                    "is_fictional": 0.0, "is_human": 1.0, "is_adult": 1.0,
                }

                # Gender
                gender = _val(row, "genderLabel")
                if gender:
                    attrs["is_male"] = 1.0 if "male" in gender.lower() and "female" not in gender.lower() else 0.0

                # Country
                attrs.update(_country_attrs(_val(row, "countryLabel")))
                # Era
                attrs.update(_era_attrs(_int_val(row, "birthYear"), _int_val(row, "deathYear")))
                # Occupations
                attrs.update(_occupation_attrs(_val(row, "occupations")))

                lang = "ru" if (_is_cyrillic(name)) else "en"
                eid = await repo.add_entity(name, "wikidata", "person", lang)

                # Add Russian alias if both names exist and differ
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

            # Be polite to Wikidata servers
            time.sleep(1)

    logger.info("Imported %d real people", count)
    return count


async def import_fictional(repo: Repository, attr_ids: dict[str, int],
                           existing_names: set[str], limit: int = 40000) -> int:
    """Import fictional characters from Wikidata."""
    logger.info("=" * 60)
    logger.info("IMPORTING FICTIONAL CHARACTERS (limit=%d)", limit)
    logger.info("=" * 60)

    count = 0
    batch = 100  # Reduced from 2000 to avoid timeouts
    thresholds = [(30, min(limit, 10000)), (15, min(limit, 25000)),
                  (5, limit)]

    for min_sl, phase_limit in thresholds:
        if count >= limit:
            break
        logger.info("--- Phase: sitelinks > %d (target: %d) ---", min_sl, phase_limit)

        for offset in range(0, phase_limit, batch):
            if count >= limit:
                break

            query = QUERY_FICTIONAL.format(min_sitelinks=min_sl, limit=batch, offset=offset)
            rows = _sparql_query(query)
            if not rows:
                logger.info("  No more results at offset %d", offset)
                break

            new_in_batch = 0
            for row in rows:
                en_name = _val(row, "enLabel")
                ru_name = _val(row, "ruLabel")
                name = en_name or ru_name
                if not name or name.startswith("Q"):
                    continue
                if name.lower() in existing_names:
                    continue

                attrs: dict[str, float] = {
                    "is_fictional": 1.0, "is_adult": 1.0,
                }

                gender = _val(row, "genderLabel")
                if gender:
                    attrs["is_male"] = 1.0 if "male" in gender.lower() and "female" not in gender.lower() else 0.0

                attrs.update(_universe_attrs(_val(row, "universes"), _val(row, "medias")))

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
            time.sleep(1)

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
