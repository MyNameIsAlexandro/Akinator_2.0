"""Seed the database with sample entities and attributes for MVP testing."""

from __future__ import annotations

import asyncio
import os
import logging

from akinator.db.repository import Repository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("akinator.seed")

DB_PATH = os.environ.get("AKINATOR_DB_PATH", "data/akinator.db")

# ── Attribute definitions ──────────────────────────────────────

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
    # Geography
    ("from_usa", "Связан с США?", "Related to USA?", "geography"),
    ("from_europe", "Связан с Европой?", "Related to Europe?", "geography"),
    ("from_russia", "Связан с Россией?", "Related to Russia?", "geography"),
    ("from_asia", "Связан с Азией?", "Related to Asia?", "geography"),
    ("from_japan", "Связан с Японией?", "Related to Japan?", "geography"),
    # Era
    ("era_ancient", "Из древности (до 500 н.э.)?", "From ancient times (before 500 AD)?", "era"),
    ("era_medieval", "Из средневековья (500-1500)?", "From medieval era (500-1500)?", "era"),
    ("era_modern", "Из нового времени (1500-1900)?", "From modern era (1500-1900)?", "era"),
    ("era_20th_century", "Из 20-го века?", "From the 20th century?", "era"),
    ("era_21st_century", "Из 21-го века?", "From the 21st century?", "era"),
    # Traits
    ("has_superpower", "Обладает сверхспособностями?", "Has superpowers?", "traits"),
    ("wears_uniform", "Носит униформу/костюм?", "Wears a uniform/costume?", "traits"),
    ("has_famous_catchphrase", "Известен крылатой фразой?", "Known for a famous catchphrase?", "traits"),
    ("is_leader", "Является лидером/главой?", "Is a leader/head?", "traits"),
    ("is_wealthy", "Богатый/знатный?", "Wealthy/noble?", "traits"),
]

# ── Entity data: (name, description, type, lang, aliases, attributes) ──

ENTITIES = [
    # ─── Fictional Characters ────────────────────
    ("Darth Vader", "Sith Lord from Star Wars, formerly Anakin Skywalker", "character", "en",
     ["Дарт Вейдер", "Anakin Skywalker", "Энакин Скайуокер"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.9, "from_movie": 1.0, "from_tv_series": 0.3, "from_game": 0.4,
      "from_book": 0.3, "from_comics": 0.4, "from_usa": 0.8, "era_20th_century": 0.8,
      "has_superpower": 0.9, "wears_uniform": 1.0, "has_famous_catchphrase": 1.0,
      "is_leader": 0.8, "is_wealthy": 0.5}),

    ("Harry Potter", "Boy wizard from J.K. Rowling's series", "character", "en",
     ["Гарри Поттер"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.4,
      "is_villain": 0.0, "from_movie": 1.0, "from_book": 1.0, "from_game": 0.3,
      "from_europe": 0.9, "era_21st_century": 0.8, "has_superpower": 0.9,
      "wears_uniform": 0.7, "has_famous_catchphrase": 0.5, "is_leader": 0.5}),

    ("Hermione Granger", "Brilliant witch from Harry Potter", "character", "en",
     ["Гермиона Грейнджер"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.4,
      "is_villain": 0.0, "from_movie": 1.0, "from_book": 1.0, "from_europe": 0.9,
      "era_21st_century": 0.8, "has_superpower": 0.8, "wears_uniform": 0.7}),

    ("Mario", "Nintendo plumber and video game hero", "character", "en",
     ["Марио", "Super Mario"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_game": 1.0, "from_movie": 0.3, "from_japan": 0.8,
      "from_asia": 0.8, "era_20th_century": 0.9, "wears_uniform": 0.8,
      "has_famous_catchphrase": 0.8}),

    ("Link", "Hero of the Legend of Zelda series", "character", "en",
     ["Линк"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.8, "is_alive": 1.0, "is_adult": 0.7,
      "is_villain": 0.0, "from_game": 1.0, "from_japan": 0.8, "from_asia": 0.8,
      "era_20th_century": 0.8, "wears_uniform": 0.8, "has_superpower": 0.5, "is_leader": 0.3}),

    ("Spider-Man", "Marvel superhero, Peter Parker", "character", "en",
     ["Человек-паук", "Peter Parker", "Питер Паркер"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.6,
      "is_villain": 0.0, "from_movie": 1.0, "from_comics": 1.0, "from_game": 0.5,
      "from_tv_series": 0.5, "from_usa": 1.0, "era_20th_century": 0.9,
      "has_superpower": 1.0, "wears_uniform": 1.0, "has_famous_catchphrase": 1.0}),

    ("Batman", "DC superhero, Bruce Wayne, the Dark Knight", "character", "en",
     ["Бэтмен", "Bruce Wayne", "Брюс Уэйн"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.1, "from_movie": 1.0, "from_comics": 1.0, "from_game": 0.5,
      "from_tv_series": 0.6, "from_usa": 1.0, "era_20th_century": 0.9,
      "has_superpower": 0.2, "wears_uniform": 1.0, "is_leader": 0.5, "is_wealthy": 1.0}),

    ("Joker", "Batman's archenemy, clown prince of crime", "character", "en",
     ["Джокер"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 1.0, "from_movie": 1.0, "from_comics": 1.0, "from_tv_series": 0.5,
      "from_usa": 1.0, "era_20th_century": 0.9, "wears_uniform": 0.8,
      "has_famous_catchphrase": 0.9}),

    ("Naruto", "Ninja from the anime Naruto, dreams of becoming Hokage", "character", "en",
     ["Наруто", "Naruto Uzumaki", "Наруто Узумаки"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.5,
      "is_villain": 0.0, "from_anime": 1.0, "from_game": 0.4, "from_japan": 1.0,
      "from_asia": 1.0, "era_21st_century": 0.9, "has_superpower": 0.9,
      "wears_uniform": 0.7, "is_leader": 0.7, "has_famous_catchphrase": 0.8}),

    ("Goku", "Saiyan warrior from Dragon Ball", "character", "en",
     ["Гоку", "Son Goku", "Сон Гоку", "Kakarot"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 1.0, "is_adult": 0.7,
      "is_villain": 0.0, "from_anime": 1.0, "from_game": 0.5, "from_japan": 1.0,
      "from_asia": 1.0, "era_20th_century": 0.9, "has_superpower": 1.0,
      "wears_uniform": 0.7, "has_famous_catchphrase": 0.7}),

    ("Sherlock Holmes", "Famous detective created by Arthur Conan Doyle", "character", "en",
     ["Шерлок Холмс"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.5, "is_adult": 1.0,
      "is_villain": 0.0, "from_book": 1.0, "from_movie": 0.8, "from_tv_series": 0.8,
      "from_europe": 1.0, "era_modern": 0.9, "has_famous_catchphrase": 0.9}),

    ("Shrek", "Green ogre from animated DreamWorks films", "character", "en",
     ["Шрек"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.2, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.1, "from_movie": 1.0, "from_game": 0.2, "from_usa": 0.8,
      "era_21st_century": 0.9, "has_famous_catchphrase": 0.8}),

    ("Elsa", "Ice queen from Disney's Frozen", "character", "en",
     ["Эльза"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.8,
      "is_villain": 0.1, "from_movie": 1.0, "from_usa": 0.8, "from_europe": 0.5,
      "era_21st_century": 1.0, "has_superpower": 1.0, "is_leader": 0.9, "is_wealthy": 0.9,
      "has_famous_catchphrase": 1.0}),

    ("Pikachu", "Electric-type Pokemon, Ash's partner", "character", "en",
     ["Пикачу"],
     {"is_fictional": 1.0, "is_male": 0.5, "is_human": 0.0, "is_alive": 1.0, "is_adult": 0.5,
      "is_villain": 0.0, "from_anime": 1.0, "from_game": 1.0, "from_japan": 1.0,
      "from_asia": 1.0, "era_20th_century": 0.9, "has_superpower": 0.9,
      "has_famous_catchphrase": 0.9}),

    ("Voldemort", "Dark wizard, main antagonist of Harry Potter", "character", "en",
     ["Волдеморт", "Tom Riddle", "Том Реддл"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.8, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 1.0, "from_book": 1.0, "from_movie": 1.0, "from_europe": 0.9,
      "era_21st_century": 0.8, "has_superpower": 1.0, "is_leader": 0.9,
      "has_famous_catchphrase": 0.7}),

    ("Gandalf", "Wizard from Lord of the Rings", "character", "en",
     ["Гэндальф"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_book": 1.0, "from_movie": 1.0, "from_europe": 0.8,
      "era_20th_century": 0.8, "has_superpower": 0.9, "wears_uniform": 0.7,
      "is_leader": 0.6, "has_famous_catchphrase": 1.0}),

    ("Homer Simpson", "Father from The Simpsons animated series", "character", "en",
     ["Гомер Симпсон"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_tv_series": 1.0, "from_usa": 1.0, "era_20th_century": 0.9,
      "has_famous_catchphrase": 1.0}),

    ("Walter White", "Chemistry teacher turned drug lord from Breaking Bad", "character", "en",
     ["Уолтер Уайт", "Heisenberg", "Хайзенберг"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.7, "from_tv_series": 1.0, "from_usa": 1.0, "era_21st_century": 1.0,
      "has_famous_catchphrase": 0.9, "from_science": 0.5, "is_leader": 0.6}),

    ("Geralt of Rivia", "Monster hunter from The Witcher", "character", "en",
     ["Геральт из Ривии", "Ведьмак"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.7, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.1, "from_game": 1.0, "from_book": 1.0, "from_tv_series": 0.8,
      "from_europe": 0.9, "era_21st_century": 0.8, "has_superpower": 0.6,
      "wears_uniform": 0.5, "has_famous_catchphrase": 0.7}),

    ("Lara Croft", "Adventurer archaeologist from Tomb Raider", "character", "en",
     ["Лара Крофт"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_game": 1.0, "from_movie": 0.7, "from_europe": 0.7,
      "era_20th_century": 0.9, "is_wealthy": 0.8}),

    # ─── Real People ────────────────────────────

    ("Elon Musk", "Tech entrepreneur, CEO of Tesla and SpaceX", "person", "en",
     ["Илон Маск"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.2, "from_usa": 0.8, "from_science": 0.7, "era_21st_century": 1.0,
      "is_leader": 1.0, "is_wealthy": 1.0, "has_famous_catchphrase": 0.4}),

    ("Albert Einstein", "Theoretical physicist, theory of relativity", "person", "en",
     ["Альберт Эйнштейн"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_science": 1.0, "from_europe": 0.8, "from_usa": 0.5,
      "era_20th_century": 1.0, "from_history": 0.8, "has_famous_catchphrase": 0.6}),

    ("Юрий Гагарин", "Первый человек в космосе", "person", "ru",
     ["Yuri Gagarin"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_russia": 1.0, "from_science": 0.6, "from_history": 0.9,
      "era_20th_century": 1.0, "wears_uniform": 0.9, "is_leader": 0.3,
      "has_famous_catchphrase": 0.9}),

    ("Leonardo da Vinci", "Renaissance artist, inventor and polymath", "person", "en",
     ["Леонардо да Винчи"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_europe": 1.0, "from_science": 0.8, "from_history": 1.0,
      "era_medieval": 0.8, "is_wealthy": 0.4}),

    ("Queen Elizabeth II", "Queen of the United Kingdom 1952-2022", "person", "en",
     ["Елизавета II", "Королева Елизавета"],
     {"is_fictional": 0.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_europe": 1.0, "from_politics": 0.9, "from_history": 0.8,
      "era_20th_century": 0.9, "era_21st_century": 0.7, "is_leader": 1.0,
      "is_wealthy": 1.0, "wears_uniform": 0.5}),

    ("Michael Jackson", "King of Pop, legendary musician", "person", "en",
     ["Майкл Джексон"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_music": 1.0, "from_usa": 1.0, "era_20th_century": 1.0,
      "has_famous_catchphrase": 0.7, "is_wealthy": 0.9, "wears_uniform": 0.6}),

    ("Lionel Messi", "Argentine football player, considered the GOAT", "person", "en",
     ["Лионель Месси"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_sport": 1.0, "from_europe": 0.6, "era_21st_century": 1.0,
      "is_leader": 0.6, "is_wealthy": 0.9, "wears_uniform": 1.0}),

    ("Cleopatra", "Last pharaoh of ancient Egypt", "person", "en",
     ["Клеопатра"],
     {"is_fictional": 0.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.2, "from_history": 1.0, "from_africa": 0.5, "era_ancient": 1.0,
      "is_leader": 1.0, "is_wealthy": 1.0}),

    ("Napoleon", "French emperor and military leader", "person", "en",
     ["Наполеон", "Napoleon Bonaparte", "Наполеон Бонапарт"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.4, "from_europe": 1.0, "from_history": 1.0, "from_politics": 0.9,
      "era_modern": 1.0, "is_leader": 1.0, "is_wealthy": 0.8, "wears_uniform": 1.0,
      "has_famous_catchphrase": 0.5}),

    ("Steve Jobs", "Co-founder of Apple, tech visionary", "person", "en",
     ["Стив Джобс"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.1, "from_usa": 1.0, "from_science": 0.6, "era_20th_century": 0.8,
      "era_21st_century": 0.7, "is_leader": 1.0, "is_wealthy": 1.0,
      "has_famous_catchphrase": 0.7}),

    ("Владимир Высоцкий", "Советский поэт, бард и актёр", "person", "ru",
     ["Vladimir Vysotsky"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_russia": 1.0, "from_music": 0.9, "from_movie": 0.5,
      "era_20th_century": 1.0, "has_famous_catchphrase": 0.8}),

    ("Александр Пушкин", "Великий русский поэт", "person", "ru",
     ["Alexander Pushkin"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_russia": 1.0, "from_book": 1.0, "from_history": 0.9,
      "era_modern": 0.9, "has_famous_catchphrase": 0.6}),

    ("Taylor Swift", "American singer-songwriter, pop superstar", "person", "en",
     ["Тейлор Свифт"],
     {"is_fictional": 0.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_music": 1.0, "from_usa": 1.0, "era_21st_century": 1.0,
      "is_wealthy": 0.9, "has_famous_catchphrase": 0.4}),

    ("Cristiano Ronaldo", "Portuguese football player", "person", "en",
     ["Криштиану Роналду", "CR7"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_sport": 1.0, "from_europe": 0.9, "era_21st_century": 1.0,
      "is_wealthy": 0.9, "wears_uniform": 1.0, "has_famous_catchphrase": 0.6}),

    ("Marie Curie", "Physicist, first woman to win a Nobel Prize", "person", "en",
     ["Мария Кюри", "Maria Sklodowska"],
     {"is_fictional": 0.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_europe": 1.0, "from_science": 1.0, "from_history": 0.8,
      "era_modern": 0.5, "era_20th_century": 0.8}),
]


async def seed() -> None:
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    repo = Repository(DB_PATH)
    await repo.init_db()

    # Check if already seeded
    existing = await repo.get_all_entities()
    if existing:
        logger.info("Database already has %d entities, skipping seed.", len(existing))
        await repo.close()
        return

    # Insert attributes
    attr_ids: dict[str, int] = {}
    for key, q_ru, q_en, category in ATTRIBUTES:
        aid = await repo.add_attribute(key, q_ru, q_en, category)
        attr_ids[key] = aid
        logger.info("  Attribute: %s (id=%d)", key, aid)

    # Insert entities
    for name, desc, etype, lang, aliases, attrs in ENTITIES:
        eid = await repo.add_entity(name, desc, etype, lang)
        logger.info("  Entity: %s (id=%d)", name, eid)

        # Add aliases
        for alias in aliases:
            alias_lang = "ru" if any(ord(c) > 127 for c in alias) else "en"
            await repo.add_alias(eid, alias, alias_lang)

        # Add attribute values
        for attr_key, value in attrs.items():
            if attr_key in attr_ids:
                await repo.set_entity_attribute(eid, attr_ids[attr_key], value)

    logger.info("Seeded %d attributes, %d entities.", len(ATTRIBUTES), len(ENTITIES))
    await repo.close()


if __name__ == "__main__":
    asyncio.run(seed())
