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

    # ─── Additional Fictional Characters ──────────────────

    ("Merlin", "Legendary wizard from Arthurian legends", "character", "en",
     ["Мэрлин", "Мерлин"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.7, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_book": 1.0, "from_movie": 0.7, "from_tv_series": 0.5,
      "from_europe": 1.0, "era_medieval": 1.0, "from_history": 0.5, "has_superpower": 1.0,
      "wears_uniform": 0.6, "has_famous_catchphrase": 0.4, "is_leader": 0.6}),

    ("Iron Man", "Marvel superhero, genius billionaire Tony Stark", "character", "en",
     ["Железный человек", "Tony Stark", "Тони Старк"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.5, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_comics": 1.0, "from_game": 0.4,
      "from_usa": 1.0, "era_21st_century": 1.0, "has_superpower": 0.7,
      "wears_uniform": 1.0, "has_famous_catchphrase": 1.0, "is_leader": 0.8, "is_wealthy": 1.0}),

    ("Superman", "DC superhero from planet Krypton, Clark Kent", "character", "en",
     ["Супермен", "Clark Kent", "Кларк Кент"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_comics": 1.0, "from_tv_series": 0.6,
      "from_usa": 1.0, "era_20th_century": 0.9, "has_superpower": 1.0,
      "wears_uniform": 1.0, "has_famous_catchphrase": 0.7, "is_leader": 0.5}),

    ("Wonder Woman", "DC superheroine, Amazonian warrior princess Diana", "character", "en",
     ["Чудо-женщина", "Diana Prince", "Диана Принс"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 0.6, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_comics": 1.0, "from_usa": 1.0,
      "era_20th_century": 0.8, "has_superpower": 1.0, "wears_uniform": 1.0,
      "is_leader": 0.7, "is_wealthy": 0.6}),

    ("Thanos", "Marvel supervillain, the Mad Titan", "character", "en",
     ["Танос"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.2, "is_alive": 0.5, "is_adult": 1.0,
      "is_villain": 1.0, "from_movie": 1.0, "from_comics": 1.0, "from_usa": 0.8,
      "era_21st_century": 0.9, "has_superpower": 1.0, "wears_uniform": 0.7,
      "is_leader": 1.0, "is_wealthy": 0.7, "has_famous_catchphrase": 0.8}),

    ("Wolverine", "Marvel mutant superhero with adamantium claws", "character", "en",
     ["Росомаха", "Logan", "Логан"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.7, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.1, "from_movie": 1.0, "from_comics": 1.0, "from_game": 0.4,
      "from_usa": 0.9, "era_20th_century": 0.8, "has_superpower": 1.0,
      "wears_uniform": 0.8, "has_famous_catchphrase": 0.6}),

    ("Deadpool", "Marvel antihero, the Merc with a Mouth", "character", "en",
     ["Дэдпул"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.8, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.3, "from_movie": 1.0, "from_comics": 1.0, "from_game": 0.3,
      "from_usa": 1.0, "era_21st_century": 1.0, "has_superpower": 0.9,
      "wears_uniform": 1.0, "has_famous_catchphrase": 0.9}),

    ("Captain America", "Marvel superhero, patriotic super-soldier Steve Rogers", "character", "en",
     ["Капитан Америка", "Steve Rogers", "Стив Роджерс"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_comics": 1.0, "from_game": 0.3,
      "from_usa": 1.0, "era_20th_century": 0.8, "has_superpower": 0.8,
      "wears_uniform": 1.0, "has_famous_catchphrase": 0.7, "is_leader": 1.0}),

    ("Thor", "Marvel superhero, Norse god of thunder", "character", "en",
     ["Тор"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.3, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_comics": 1.0, "from_europe": 0.7,
      "from_usa": 0.6, "era_21st_century": 0.8, "has_superpower": 1.0,
      "wears_uniform": 0.8, "is_leader": 0.7, "is_wealthy": 0.8}),

    ("Hulk", "Marvel superhero, giant green rage monster Bruce Banner", "character", "en",
     ["Халк", "Bruce Banner", "Брюс Бэннер"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.6, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.2, "from_movie": 1.0, "from_comics": 1.0, "from_game": 0.4,
      "from_usa": 1.0, "era_20th_century": 0.8, "has_superpower": 1.0,
      "from_science": 0.5, "has_famous_catchphrase": 0.9}),

    ("Black Widow", "Marvel superheroine, spy and assassin Natasha Romanoff", "character", "en",
     ["Чёрная вдова", "Natasha Romanoff", "Наташа Романофф"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 0.5, "is_adult": 1.0,
      "is_villain": 0.1, "from_movie": 1.0, "from_comics": 1.0, "from_usa": 0.7,
      "from_russia": 0.6, "era_21st_century": 0.9, "wears_uniform": 1.0}),

    ("Loki", "Marvel character, Norse god of mischief", "character", "en",
     ["Локи"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.3, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.7, "from_movie": 1.0, "from_comics": 1.0, "from_tv_series": 0.8,
      "from_usa": 0.6, "from_europe": 0.6, "era_21st_century": 0.9, "has_superpower": 1.0,
      "wears_uniform": 0.7, "has_famous_catchphrase": 0.6, "is_leader": 0.5, "is_wealthy": 0.7}),

    ("Sasuke Uchiha", "Rival and friend of Naruto, avenger of the Uchiha clan", "character", "en",
     ["Саске Учиха", "Саске"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.6,
      "is_villain": 0.5, "from_anime": 1.0, "from_game": 0.3, "from_japan": 1.0,
      "from_asia": 1.0, "era_21st_century": 0.9, "has_superpower": 0.9,
      "wears_uniform": 0.5}),

    ("Luffy", "Rubber-powered pirate captain from One Piece", "character", "en",
     ["Луффи", "Monkey D. Luffy", "Монки Д. Луффи"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.6,
      "is_villain": 0.0, "from_anime": 1.0, "from_game": 0.3, "from_japan": 1.0,
      "from_asia": 1.0, "era_21st_century": 0.9, "has_superpower": 0.9,
      "is_leader": 0.8, "has_famous_catchphrase": 0.8}),

    ("Light Yagami", "Genius student who finds the Death Note", "character", "en",
     ["Лайт Ягами", "Кира"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 0.6,
      "is_villain": 0.8, "from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0,
      "era_21st_century": 0.9, "has_superpower": 0.7, "has_famous_catchphrase": 0.6}),

    ("Eren Yeager", "Protagonist of Attack on Titan who becomes a titan shifter", "character", "en",
     ["Эрен Йегер", "Эрен"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.7, "is_alive": 0.0, "is_adult": 0.6,
      "is_villain": 0.6, "from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0,
      "era_21st_century": 1.0, "has_superpower": 0.9, "wears_uniform": 0.8,
      "is_leader": 0.7, "has_famous_catchphrase": 0.5}),

    ("Saitama", "Superhero who defeats any enemy with one punch", "character", "en",
     ["Сайтама"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0,
      "era_21st_century": 1.0, "has_superpower": 1.0, "wears_uniform": 0.8,
      "has_famous_catchphrase": 0.7}),

    ("Frodo Baggins", "Hobbit ring-bearer from Lord of the Rings", "character", "en",
     ["Фродо Бэггинс", "Фродо"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.6, "is_alive": 1.0, "is_adult": 0.7,
      "is_villain": 0.0, "from_book": 1.0, "from_movie": 1.0, "from_europe": 0.8,
      "era_20th_century": 0.8, "has_superpower": 0.3, "is_leader": 0.3}),

    ("Aragorn", "Ranger and rightful king of Gondor from Lord of the Rings", "character", "en",
     ["Арагорн"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_book": 1.0, "from_movie": 1.0, "from_europe": 0.8,
      "era_20th_century": 0.8, "wears_uniform": 0.6, "is_leader": 1.0,
      "is_wealthy": 0.7, "has_famous_catchphrase": 0.5}),

    ("Jack Sparrow", "Eccentric pirate captain from Pirates of the Caribbean", "character", "en",
     ["Джек Воробей", "Captain Jack Sparrow", "Капитан Джек Воробей"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.3, "from_movie": 1.0, "from_usa": 0.8, "from_europe": 0.4,
      "era_21st_century": 0.8, "wears_uniform": 0.7, "has_famous_catchphrase": 1.0,
      "is_leader": 0.5}),

    ("Indiana Jones", "Adventurer archaeologist and professor", "character", "en",
     ["Индиана Джонс"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_usa": 1.0, "era_20th_century": 1.0,
      "wears_uniform": 0.7, "has_famous_catchphrase": 0.6, "from_science": 0.3,
      "from_history": 0.4}),

    ("James Bond", "British secret agent 007", "character", "en",
     ["Джеймс Бонд", "007", "Агент 007"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_book": 0.8, "from_game": 0.4,
      "from_europe": 1.0, "era_20th_century": 0.9, "wears_uniform": 0.6,
      "has_famous_catchphrase": 1.0, "is_wealthy": 0.7}),

    ("Terminator", "Cybernetic assassin from the future, T-800", "character", "en",
     ["Терминатор", "T-800", "Т-800"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.3, "is_alive": 0.5, "is_adult": 1.0,
      "is_villain": 0.5, "from_movie": 1.0, "from_usa": 1.0, "era_20th_century": 0.9,
      "has_superpower": 0.8, "wears_uniform": 0.3, "has_famous_catchphrase": 1.0}),

    ("Neo", "The One, hacker who discovers the Matrix", "character", "en",
     ["Нео", "Thomas Anderson", "Томас Андерсон"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_usa": 1.0, "era_20th_century": 0.8,
      "has_superpower": 0.9, "wears_uniform": 0.7, "has_famous_catchphrase": 0.6,
      "is_leader": 0.7}),

    ("Yoda", "Ancient Jedi Grand Master from Star Wars", "character", "en",
     ["Йода"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.2, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_game": 0.3, "from_usa": 0.8,
      "era_20th_century": 0.9, "has_superpower": 1.0, "wears_uniform": 0.5,
      "has_famous_catchphrase": 1.0, "is_leader": 0.9}),

    ("Luke Skywalker", "Jedi hero from Star Wars, son of Anakin Skywalker", "character", "en",
     ["Люк Скайуокер"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.7,
      "is_villain": 0.0, "from_movie": 1.0, "from_game": 0.3, "from_usa": 0.8,
      "era_20th_century": 0.9, "has_superpower": 0.9, "wears_uniform": 0.6,
      "is_leader": 0.7, "has_famous_catchphrase": 0.5}),

    ("Princess Leia", "Rebel leader and princess from Star Wars", "character", "en",
     ["Принцесса Лея", "Leia Organa", "Лея Органа"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_usa": 0.8, "era_20th_century": 0.9,
      "wears_uniform": 0.5, "is_leader": 1.0, "is_wealthy": 0.8,
      "has_famous_catchphrase": 0.5}),

    ("Kratos", "Spartan warrior and god slayer from God of War", "character", "en",
     ["Кратос"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.4, "from_game": 1.0, "from_europe": 0.7, "era_21st_century": 0.8,
      "era_ancient": 0.6, "has_superpower": 1.0, "wears_uniform": 0.5,
      "has_famous_catchphrase": 0.6}),

    ("Master Chief", "Spartan supersoldier from the Halo franchise", "character", "en",
     ["Мастер Чиф"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.8, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_game": 1.0, "from_usa": 0.9, "era_21st_century": 0.9,
      "has_superpower": 0.6, "wears_uniform": 1.0, "is_leader": 0.7,
      "has_famous_catchphrase": 0.5}),

    ("Sonic the Hedgehog", "Super-fast blue hedgehog from Sega games", "character", "en",
     ["Соник", "Ёж Соник"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 0.5,
      "is_villain": 0.0, "from_game": 1.0, "from_movie": 0.6, "from_tv_series": 0.4,
      "from_japan": 0.8, "from_asia": 0.8, "era_20th_century": 0.9,
      "has_superpower": 0.9, "has_famous_catchphrase": 0.7}),

    ("SpongeBob SquarePants", "Cheerful sea sponge living in Bikini Bottom", "character", "en",
     ["Губка Боб", "Губка Боб Квадратные Штаны"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 0.6,
      "is_villain": 0.0, "from_tv_series": 1.0, "from_movie": 0.5, "from_usa": 1.0,
      "era_21st_century": 0.9, "wears_uniform": 0.6, "has_famous_catchphrase": 1.0}),

    ("Mickey Mouse", "Classic Disney cartoon character", "character", "en",
     ["Микки Маус"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 0.7,
      "is_villain": 0.0, "from_movie": 0.8, "from_tv_series": 0.8, "from_game": 0.4,
      "from_usa": 1.0, "era_20th_century": 1.0, "wears_uniform": 0.5,
      "has_famous_catchphrase": 0.7, "is_leader": 0.3}),

    ("Tom", "Cat who chases Jerry in Tom and Jerry cartoons", "character", "en",
     ["Том"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 0.7,
      "is_villain": 0.4, "from_movie": 0.5, "from_tv_series": 1.0, "from_usa": 1.0,
      "era_20th_century": 1.0}),

    ("Jerry", "Mouse who outsmarts Tom in Tom and Jerry cartoons", "character", "en",
     ["Джерри"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 0.5,
      "is_villain": 0.2, "from_movie": 0.5, "from_tv_series": 1.0, "from_usa": 1.0,
      "era_20th_century": 1.0}),

    ("Bugs Bunny", "Clever cartoon rabbit from Looney Tunes", "character", "en",
     ["Багз Банни"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 0.7,
      "is_villain": 0.0, "from_movie": 0.5, "from_tv_series": 1.0, "from_usa": 1.0,
      "era_20th_century": 1.0, "has_famous_catchphrase": 1.0}),

    ("Winnie the Pooh", "Honey-loving bear from A.A. Milne stories", "character", "en",
     ["Винни-Пух"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 0.5,
      "is_villain": 0.0, "from_book": 1.0, "from_movie": 0.7, "from_tv_series": 0.5,
      "from_europe": 0.8, "from_russia": 0.4, "era_20th_century": 0.9,
      "has_famous_catchphrase": 0.7}),

    ("Чебурашка", "Ушастый зверёк из советского мультфильма", "character", "ru",
     ["Cheburashka"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 0.3,
      "is_villain": 0.0, "from_movie": 0.8, "from_book": 0.7, "from_russia": 1.0,
      "era_20th_century": 1.0, "has_famous_catchphrase": 0.5}),

    ("Кот Матроскин", "Хозяйственный кот из мультфильма Простоквашино", "character", "ru",
     ["Matroskin", "Cat Matroskin"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 0.7,
      "is_villain": 0.0, "from_movie": 0.7, "from_book": 0.8, "from_tv_series": 0.5,
      "from_russia": 1.0, "era_20th_century": 1.0, "has_famous_catchphrase": 0.9}),

    ("Незнайка", "Коротышка из Цветочного города, герой Носова", "character", "ru",
     ["Neznaika", "Dunno"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.6, "is_alive": 1.0, "is_adult": 0.3,
      "is_villain": 0.0, "from_book": 1.0, "from_movie": 0.5, "from_russia": 1.0,
      "era_20th_century": 1.0, "has_famous_catchphrase": 0.5}),

    ("Баба-Яга", "Ведьма из русских народных сказок", "character", "ru",
     ["Baba Yaga", "Baba-Yaga"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 0.5, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.8, "from_book": 0.8, "from_movie": 0.5, "from_russia": 1.0,
      "from_history": 0.3, "era_medieval": 0.6, "has_superpower": 0.9,
      "has_famous_catchphrase": 0.7}),

    # ─── Additional Real People ───────────────────────────

    ("Владимир Путин", "Президент Российской Федерации", "person", "ru",
     ["Vladimir Putin"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.3, "from_russia": 1.0, "from_politics": 1.0, "era_21st_century": 1.0,
      "is_leader": 1.0, "is_wealthy": 0.9, "wears_uniform": 0.4,
      "has_famous_catchphrase": 0.6}),

    ("Дональд Трамп", "Президент США, бизнесмен", "person", "ru",
     ["Donald Trump", "Trump"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.3, "from_usa": 1.0, "from_politics": 1.0, "era_21st_century": 1.0,
      "is_leader": 1.0, "is_wealthy": 1.0, "has_famous_catchphrase": 1.0}),

    ("Барак Обама", "44-й президент США", "person", "ru",
     ["Barack Obama", "Obama"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_usa": 1.0, "from_politics": 1.0, "era_21st_century": 1.0,
      "is_leader": 1.0, "is_wealthy": 0.8, "has_famous_catchphrase": 0.7}),

    ("Илья Муромец", "Русский богатырь из былин", "character", "ru",
     ["Ilya Muromets"],
     {"is_fictional": 0.8, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_book": 0.7, "from_movie": 0.4, "from_russia": 1.0,
      "from_history": 0.8, "era_medieval": 0.9, "has_superpower": 0.8,
      "wears_uniform": 0.7, "is_leader": 0.6, "has_famous_catchphrase": 0.4}),

    ("Arnold Schwarzenegger", "Actor, bodybuilder, and former governor of California", "person", "en",
     ["Арнольд Шварценеггер", "Шварц"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_usa": 0.9, "from_europe": 0.5,
      "from_politics": 0.4, "from_sport": 0.5, "era_20th_century": 0.9,
      "has_famous_catchphrase": 1.0, "is_leader": 0.5, "is_wealthy": 0.8}),

    ("Bruce Lee", "Legendary martial artist and actor", "person", "en",
     ["Брюс Ли"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_sport": 0.7, "from_usa": 0.7,
      "from_asia": 0.9, "era_20th_century": 1.0, "wears_uniform": 0.6,
      "has_famous_catchphrase": 0.8}),

    ("Jackie Chan", "Martial arts actor and stuntman", "person", "en",
     ["Джеки Чан"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_sport": 0.4, "from_usa": 0.5,
      "from_asia": 1.0, "era_20th_century": 0.8, "era_21st_century": 0.7,
      "has_famous_catchphrase": 0.4, "is_wealthy": 0.8}),

    ("Дмитрий Менделеев", "Русский химик, создатель периодической таблицы", "person", "ru",
     ["Dmitri Mendeleev", "Mendeleev"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_russia": 1.0, "from_science": 1.0, "from_history": 0.8,
      "era_modern": 0.8, "era_20th_century": 0.3}),

    ("Никола Тесла", "Изобретатель и физик, пионер электротехники", "person", "ru",
     ["Nikola Tesla", "Tesla"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_europe": 0.8, "from_usa": 0.7, "from_science": 1.0,
      "from_history": 0.8, "era_modern": 0.6, "era_20th_century": 0.8}),

    ("Isaac Newton", "Physicist and mathematician, laws of motion and gravity", "person", "en",
     ["Исаак Ньютон"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_europe": 1.0, "from_science": 1.0, "from_history": 1.0,
      "era_modern": 1.0, "has_famous_catchphrase": 0.3}),

    ("Чарли Чаплин", "Легендарный комедийный актёр немого кино", "person", "ru",
     ["Charlie Chaplin", "Chaplin"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_europe": 0.7, "from_usa": 0.8,
      "from_history": 0.7, "era_20th_century": 1.0, "wears_uniform": 0.7,
      "has_famous_catchphrase": 0.6, "is_wealthy": 0.7}),

    ("Elvis Presley", "The King of Rock and Roll", "person", "en",
     ["Элвис Пресли", "Элвис"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_music": 1.0, "from_usa": 1.0, "era_20th_century": 1.0,
      "wears_uniform": 0.6, "has_famous_catchphrase": 0.7, "is_wealthy": 0.8}),

    ("Фредди Меркьюри", "Вокалист группы Queen", "person", "ru",
     ["Freddie Mercury", "Фредди Меркури"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_music": 1.0, "from_europe": 0.9, "from_asia": 0.3,
      "from_movie": 0.4, "era_20th_century": 1.0, "wears_uniform": 0.5,
      "has_famous_catchphrase": 0.7, "is_wealthy": 0.7}),

    ("Eminem", "American rapper, one of the best-selling artists", "person", "en",
     ["Эминем", "Slim Shady", "Marshall Mathers"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.1, "from_music": 1.0, "from_usa": 1.0, "era_21st_century": 0.9,
      "era_20th_century": 0.7, "has_famous_catchphrase": 0.8}),

    ("Muhammad Ali", "Legendary heavyweight boxing champion", "person", "en",
     ["Мохаммед Али", "Cassius Clay"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_sport": 1.0, "from_usa": 1.0, "era_20th_century": 1.0,
      "from_history": 0.6, "has_famous_catchphrase": 1.0, "is_leader": 0.4,
      "is_wealthy": 0.7}),

    ("Mike Tyson", "Heavyweight boxing champion, youngest ever", "person", "en",
     ["Майк Тайсон"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.2, "from_sport": 1.0, "from_usa": 1.0, "era_20th_century": 0.9,
      "era_21st_century": 0.5, "has_famous_catchphrase": 0.5, "is_wealthy": 0.6}),

    ("LeBron James", "Basketball superstar, one of the greatest NBA players", "person", "en",
     ["Леброн Джеймс"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_sport": 1.0, "from_usa": 1.0, "era_21st_century": 1.0,
      "wears_uniform": 1.0, "is_leader": 0.5, "is_wealthy": 1.0}),

    ("Усэйн Болт", "Самый быстрый человек в мире, спринтер", "person", "ru",
     ["Usain Bolt", "Bolt"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_sport": 1.0, "era_21st_century": 1.0,
      "wears_uniform": 0.8, "has_famous_catchphrase": 0.5, "is_wealthy": 0.7}),

    ("Пётр I", "Первый российский император, реформатор", "person", "ru",
     ["Peter the Great", "Пётр Великий", "Peter I"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.2, "from_russia": 1.0, "from_politics": 0.9, "from_history": 1.0,
      "era_modern": 1.0, "is_leader": 1.0, "is_wealthy": 1.0, "wears_uniform": 0.7,
      "has_famous_catchphrase": 0.4}),

    ("Юлий Цезарь", "Римский полководец и диктатор", "person", "ru",
     ["Julius Caesar", "Caesar"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.3, "from_europe": 1.0, "from_politics": 1.0, "from_history": 1.0,
      "era_ancient": 1.0, "is_leader": 1.0, "is_wealthy": 1.0, "wears_uniform": 0.8,
      "has_famous_catchphrase": 1.0}),

    ("Чингисхан", "Основатель Монгольской империи", "person", "ru",
     ["Genghis Khan", "Чингиз-хан"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.6, "from_asia": 1.0, "from_politics": 0.8, "from_history": 1.0,
      "era_medieval": 1.0, "is_leader": 1.0, "is_wealthy": 1.0, "wears_uniform": 0.7}),

    ("Mozart", "Austrian composer, musical genius of the Classical era", "person", "en",
     ["Моцарт", "Wolfgang Amadeus Mozart", "Вольфганг Амадей Моцарт"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_music": 1.0, "from_europe": 1.0, "from_history": 1.0,
      "era_modern": 1.0, "is_wealthy": 0.4, "wears_uniform": 0.4}),

    ("Beethoven", "German composer, one of the greatest in Western music", "person", "en",
     ["Бетховен", "Ludwig van Beethoven", "Людвиг ван Бетховен"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_music": 1.0, "from_europe": 1.0, "from_history": 1.0,
      "era_modern": 1.0}),

    ("Пикассо", "Испанский художник, основатель кубизма", "person", "ru",
     ["Pablo Picasso", "Picasso"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_europe": 1.0, "from_history": 0.7,
      "era_20th_century": 1.0, "is_wealthy": 0.7}),

    ("Stephen Hawking", "Theoretical physicist, author of A Brief History of Time", "person", "en",
     ["Стивен Хокинг"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_europe": 0.9, "from_science": 1.0, "from_book": 0.6,
      "from_history": 0.5, "era_20th_century": 0.8, "era_21st_century": 0.7,
      "has_famous_catchphrase": 0.4}),

    ("Николай Гоголь", "Русский писатель, автор Мёртвых душ и Ревизора", "person", "ru",
     ["Nikolai Gogol", "Gogol"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_russia": 1.0, "from_book": 1.0, "from_history": 0.8,
      "era_modern": 0.9}),

    ("Лев Толстой", "Великий русский писатель, автор Войны и мира", "person", "ru",
     ["Leo Tolstoy", "Tolstoy"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_russia": 1.0, "from_book": 1.0, "from_history": 0.9,
      "era_modern": 0.9, "is_wealthy": 0.6}),

    ("Фёдор Достоевский", "Русский писатель, автор Преступления и наказания", "person", "ru",
     ["Fyodor Dostoevsky", "Dostoevsky"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_russia": 1.0, "from_book": 1.0, "from_history": 0.8,
      "era_modern": 0.9}),

    ("Михаил Булгаков", "Русский писатель, автор Мастера и Маргариты", "person", "ru",
     ["Mikhail Bulgakov", "Bulgakov"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_russia": 1.0, "from_book": 1.0, "from_history": 0.6,
      "era_20th_century": 1.0}),

    ("Марк Цукерберг", "Основатель Facebook/Meta", "person", "ru",
     ["Mark Zuckerberg", "Zuckerberg"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.2, "from_usa": 1.0, "from_science": 0.5, "era_21st_century": 1.0,
      "is_leader": 0.9, "is_wealthy": 1.0}),

    # ──────────────── Disney / Pixar / Animation ────────────────

    ("Simba", "Lion prince from Disney's The Lion King", "character", "en",
     ["Симба", "Lion King"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 0.7,
      "is_villain": 0.0, "from_movie": 1.0, "from_book": 0.3, "from_usa": 1.0,
      "is_leader": 1.0, "era_20th_century": 1.0}),

    ("Buzz Lightyear", "Space ranger toy from Pixar's Toy Story", "character", "en",
     ["Базз Лайтер", "Buzz"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 0.5, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_usa": 1.0, "wears_uniform": 1.0,
      "has_famous_catchphrase": 1.0, "era_20th_century": 1.0}),

    ("Woody", "Cowboy toy sheriff from Pixar's Toy Story", "character", "en",
     ["Вуди", "Sheriff Woody"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 0.5, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_usa": 1.0, "wears_uniform": 0.7,
      "has_famous_catchphrase": 1.0, "is_leader": 0.8, "era_20th_century": 1.0}),

    ("Rapunzel", "Disney princess with magical long golden hair", "character", "en",
     ["Рапунцель"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.7,
      "is_villain": 0.0, "from_movie": 1.0, "from_book": 0.8, "from_europe": 1.0,
      "has_superpower": 0.8, "is_wealthy": 0.8}),

    ("Maui", "Demigod from Disney's Moana", "character", "en",
     ["Мауи"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "has_superpower": 1.0,
      "has_famous_catchphrase": 1.0, "from_asia": 0.3}),

    ("Maleficent", "Evil fairy from Disney's Sleeping Beauty", "character", "en",
     ["Малефисента"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 1.0, "from_movie": 1.0, "from_europe": 0.7,
      "has_superpower": 1.0, "era_medieval": 0.7}),

    ("Aladdin", "Street thief who finds a magic lamp, Disney character", "character", "en",
     ["Аладдин"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.8,
      "is_villain": 0.0, "from_movie": 1.0, "from_book": 1.0, "from_asia": 1.0,
      "is_wealthy": 0.5, "era_medieval": 0.8}),

    ("Genie", "Magical genie from Disney's Aladdin", "character", "en",
     ["Джинн"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "has_superpower": 1.0,
      "has_famous_catchphrase": 1.0, "from_asia": 1.0}),

    ("Nemo", "Clownfish from Pixar's Finding Nemo", "character", "en",
     ["Немо"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 0.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_usa": 1.0, "era_21st_century": 1.0}),

    ("Shrek's Donkey", "Talking donkey, Shrek's best friend", "character", "en",
     ["Ослик", "Donkey"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "has_famous_catchphrase": 0.7,
      "from_usa": 1.0}),

    # ──────────────── Classic literature / horror ────────────────

    ("Dracula", "Vampire count from Bram Stoker's novel", "character", "en",
     ["Дракула", "Count Dracula"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 0.5, "is_adult": 1.0,
      "is_villain": 1.0, "from_movie": 1.0, "from_book": 1.0, "from_europe": 1.0,
      "has_superpower": 1.0, "is_wealthy": 1.0, "era_modern": 1.0}),

    ("Frankenstein's Monster", "Creature created by Victor Frankenstein", "character", "en",
     ["Франкенштейн", "Frankenstein"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.3, "is_alive": 0.7, "is_adult": 1.0,
      "is_villain": 0.5, "from_movie": 1.0, "from_book": 1.0, "from_europe": 1.0,
      "has_superpower": 0.5, "era_modern": 1.0}),

    ("Robin Hood", "Legendary English outlaw who robs from the rich", "character", "en",
     ["Робин Гуд"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.3, "from_movie": 1.0, "from_book": 1.0, "from_europe": 1.0,
      "is_leader": 0.8, "era_medieval": 1.0, "from_history": 0.5}),

    ("Romeo", "Tragic young lover from Shakespeare's Romeo and Juliet", "character", "en",
     ["Ромео"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 0.7,
      "is_villain": 0.0, "from_book": 1.0, "from_movie": 0.8, "from_europe": 1.0,
      "era_modern": 1.0}),

    ("D'Artagnan", "Young Gascon swordsman from The Three Musketeers", "character", "en",
     ["Д'Артаньян", "ДАртаньян"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 0.8,
      "is_villain": 0.0, "from_book": 1.0, "from_movie": 1.0, "from_europe": 1.0,
      "wears_uniform": 0.8, "era_modern": 1.0}),

    ("Zorro", "Masked vigilante swordsman in colonial California", "character", "en",
     ["Зорро"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_book": 1.0, "from_usa": 0.5,
      "wears_uniform": 1.0, "is_wealthy": 1.0, "era_modern": 1.0}),

    # ──────────────── More anime ────────────────

    ("Vegeta", "Saiyan prince from Dragon Ball", "character", "en",
     ["Вегета"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.4, "from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0,
      "has_superpower": 1.0, "wears_uniform": 0.7, "is_leader": 0.7, "is_wealthy": 0.8}),

    ("Sakura Haruno", "Kunoichi and medic from Naruto", "character", "en",
     ["Сакура Харуно", "Sakura"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.7,
      "is_villain": 0.0, "from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0,
      "has_superpower": 0.8, "wears_uniform": 0.5}),

    ("Mikasa Ackerman", "Elite soldier from Attack on Titan", "character", "en",
     ["Микаса Аккерман", "Mikasa"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.8,
      "is_villain": 0.0, "from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0,
      "wears_uniform": 1.0, "has_superpower": 0.5}),

    ("Sailor Moon", "Magical schoolgirl warrior who fights evil", "character", "en",
     ["Сейлор Мун", "Усаги Цукино", "Usagi"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.4,
      "is_villain": 0.0, "from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0,
      "has_superpower": 1.0, "wears_uniform": 1.0, "is_leader": 0.8}),

    ("Lelouch Lamperouge", "Exiled prince with mind control power from Code Geass", "character", "en",
     ["Лелуш", "Lelouch vi Britannia"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.5, "is_adult": 0.7,
      "is_villain": 0.5, "from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0,
      "has_superpower": 1.0, "is_leader": 1.0, "is_wealthy": 0.8, "wears_uniform": 0.8}),

    ("Edward Elric", "Young alchemist from Fullmetal Alchemist", "character", "en",
     ["Эдвард Элрик", "Ed Elric"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.5,
      "is_villain": 0.0, "from_anime": 1.0, "from_japan": 1.0, "from_asia": 1.0,
      "has_superpower": 0.8, "from_science": 0.6}),

    ("Тоторо", "Добрый лесной дух из мультфильма Хаяо Миядзаки", "character", "ru",
     ["Totoro", "My Neighbor Totoro"],
     {"is_fictional": 1.0, "is_male": 0.5, "is_human": 0.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_anime": 1.0, "from_movie": 1.0, "from_japan": 1.0,
      "from_asia": 1.0, "has_superpower": 0.8}),

    # ──────────────── More video games ────────────────

    ("Cloud Strife", "Spiky-haired swordsman from Final Fantasy VII", "character", "en",
     ["Клауд Страйф", "Cloud"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_game": 1.0, "from_japan": 1.0,
      "wears_uniform": 0.5, "has_superpower": 0.5}),

    ("Pac-Man", "Yellow circle-shaped character who eats pellets in a maze", "character", "en",
     ["Пакман"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 0.5,
      "is_villain": 0.0, "from_game": 1.0, "from_japan": 1.0, "from_asia": 1.0,
      "era_20th_century": 1.0}),

    ("Princess Zelda", "Princess of Hyrule from The Legend of Zelda", "character", "en",
     ["Зельда", "Zelda"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.8,
      "is_villain": 0.0, "from_game": 1.0, "from_japan": 1.0,
      "has_superpower": 0.8, "is_wealthy": 1.0, "is_leader": 0.9}),

    ("Minecraft Steve", "Default player character from Minecraft", "character", "en",
     ["Стив", "Steve Minecraft"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_game": 1.0, "era_21st_century": 1.0}),

    ("Among Us Crewmate", "Spaceship crewmate from the game Among Us", "character", "en",
     ["Амонг Ас", "Crewmate", "Impostor"],
     {"is_fictional": 1.0, "is_male": 0.5, "is_human": 0.5, "is_alive": 1.0, "is_adult": 0.5,
      "is_villain": 0.5, "from_game": 1.0, "wears_uniform": 1.0, "era_21st_century": 1.0}),

    ("GTA Trevor", "Unhinged criminal from Grand Theft Auto V", "character", "en",
     ["Тревор Филлипс", "Trevor Philips"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.8, "from_game": 1.0, "from_usa": 1.0, "era_21st_century": 1.0}),

    # ──────────────── TV series ────────────────

    ("Sheldon Cooper", "Genius physicist from The Big Bang Theory", "character", "en",
     ["Шелдон Купер", "Sheldon"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_tv_series": 1.0, "from_usa": 1.0, "from_science": 0.9,
      "has_famous_catchphrase": 1.0, "era_21st_century": 1.0}),

    ("Daenerys Targaryen", "Dragon queen from Game of Thrones", "character", "en",
     ["Дейенерис Таргариен", "Daenerys", "Khaleesi"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 0.8,
      "is_villain": 0.5, "from_tv_series": 1.0, "from_book": 1.0, "from_europe": 0.5,
      "has_superpower": 0.7, "is_leader": 1.0, "is_wealthy": 1.0, "era_medieval": 0.8}),

    ("Jon Snow", "Bastard of Winterfell from Game of Thrones", "character", "en",
     ["Джон Сноу"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.8,
      "is_villain": 0.0, "from_tv_series": 1.0, "from_book": 1.0, "from_europe": 0.5,
      "wears_uniform": 0.7, "is_leader": 0.9, "era_medieval": 0.8}),

    ("Rick Sanchez", "Genius scientist from Rick and Morty", "character", "en",
     ["Рик Санчез", "Rick"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.4, "from_tv_series": 1.0, "from_usa": 1.0, "from_science": 1.0,
      "has_superpower": 0.7, "has_famous_catchphrase": 1.0}),

    ("Dexter Morgan", "Blood spatter analyst who is a serial killer", "character", "en",
     ["Декстер Морган", "Dexter"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.7, "from_tv_series": 1.0, "from_usa": 1.0, "from_science": 0.5,
      "era_21st_century": 1.0}),

    ("Eleven", "Girl with telekinetic powers from Stranger Things", "character", "en",
     ["Одиннадцать", "011"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.3,
      "is_villain": 0.0, "from_tv_series": 1.0, "from_usa": 1.0,
      "has_superpower": 1.0, "era_20th_century": 0.8}),

    ("Tommy Shelby", "Gangster leader from Peaky Blinders", "character", "en",
     ["Томми Шелби"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.6, "from_tv_series": 1.0, "from_europe": 1.0,
      "is_leader": 1.0, "is_wealthy": 1.0, "wears_uniform": 0.7, "era_20th_century": 1.0}),

    # ──────────────── More real people ────────────────

    ("Bill Gates", "Co-founder of Microsoft", "person", "en",
     ["Билл Гейтс"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.1, "from_usa": 1.0, "from_science": 0.7, "era_21st_century": 1.0,
      "is_leader": 0.9, "is_wealthy": 1.0}),

    ("Jeff Bezos", "Founder of Amazon, one of the richest people", "person", "en",
     ["Джефф Безос"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.2, "from_usa": 1.0, "era_21st_century": 1.0,
      "is_leader": 0.9, "is_wealthy": 1.0}),

    ("Marilyn Monroe", "Iconic American actress and model of the 1950s", "person", "en",
     ["Мэрилин Монро"],
     {"is_fictional": 0.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_usa": 1.0, "from_music": 0.3,
      "era_20th_century": 1.0, "is_wealthy": 0.8, "has_famous_catchphrase": 0.7}),

    ("Audrey Hepburn", "Elegant British-Belgian actress, Breakfast at Tiffany's", "person", "en",
     ["Одри Хепбёрн"],
     {"is_fictional": 0.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_europe": 1.0,
      "era_20th_century": 1.0, "is_wealthy": 0.7}),

    ("Keanu Reeves", "Canadian actor, known for The Matrix and John Wick", "person", "en",
     ["Киану Ривз"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_usa": 0.8,
      "era_21st_century": 1.0}),

    ("Morgan Freeman", "American actor known for his distinctive voice", "person", "en",
     ["Морган Фриман"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_usa": 1.0,
      "era_21st_century": 1.0}),

    ("Johnny Depp", "American actor, known for Captain Jack Sparrow", "person", "en",
     ["Джонни Депп"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_usa": 1.0,
      "era_21st_century": 1.0, "is_wealthy": 0.8}),

    ("Angelina Jolie", "American actress and filmmaker, humanitarian", "person", "en",
     ["Анджелина Джоли"],
     {"is_fictional": 0.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_usa": 1.0,
      "era_21st_century": 1.0, "is_wealthy": 0.8}),

    ("Дмитрий Нагиев", "Российский актёр и телеведущий", "person", "ru",
     ["Nagiev"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_tv_series": 0.8, "from_movie": 0.7, "from_russia": 1.0,
      "era_21st_century": 1.0}),

    ("Алла Пугачёва", "Российская эстрадная певица, примадонна", "person", "ru",
     ["Pugacheva", "Примадонна"],
     {"is_fictional": 0.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_music": 1.0, "from_russia": 1.0,
      "era_20th_century": 0.8, "era_21st_century": 0.7, "is_wealthy": 0.8}),

    ("Виктор Цой", "Советский рок-музыкант, лидер группы Кино", "person", "ru",
     ["Tsoi", "Цой"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_music": 1.0, "from_russia": 1.0, "from_asia": 0.3,
      "era_20th_century": 1.0, "has_famous_catchphrase": 0.7, "is_leader": 0.5}),

    ("Хабиб Нурмагомедов", "Российский боец ММА, непобеждённый чемпион UFC", "person", "ru",
     ["Khabib", "Khabib Nurmagomedov"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_sport": 1.0, "from_russia": 1.0,
      "era_21st_century": 1.0, "is_leader": 0.5}),

    ("Neymar", "Brazilian football star", "person", "en",
     ["Неймар"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.1, "from_sport": 1.0, "era_21st_century": 1.0,
      "is_wealthy": 1.0}),

    ("Serena Williams", "American tennis champion, one of the greatest ever", "person", "en",
     ["Серена Уильямс"],
     {"is_fictional": 0.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_sport": 1.0, "from_usa": 1.0,
      "era_21st_century": 1.0, "is_wealthy": 0.9}),

    ("Conor McGregor", "Irish MMA fighter, former UFC champion", "person", "en",
     ["Конор Макгрегор"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.3, "from_sport": 1.0, "from_europe": 1.0,
      "era_21st_century": 1.0, "is_wealthy": 0.9, "has_famous_catchphrase": 0.8}),

    ("Александр Великий", "Македонский царь-завоеватель", "person", "ru",
     ["Alexander the Great", "Александр Македонский"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.3, "from_history": 1.0, "from_europe": 1.0,
      "era_ancient": 1.0, "is_leader": 1.0, "is_wealthy": 1.0}),

    ("Спартак", "Фракийский гладиатор, предводитель восстания рабов", "person", "ru",
     ["Spartacus"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.3, "from_history": 1.0, "from_europe": 1.0, "from_movie": 0.7,
      "era_ancient": 1.0, "is_leader": 1.0, "wears_uniform": 0.7}),

    ("Маргарет Тэтчер", "Премьер-министр Великобритании, железная леди", "person", "ru",
     ["Margaret Thatcher", "Iron Lady"],
     {"is_fictional": 0.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.3, "from_politics": 1.0, "from_europe": 1.0,
      "era_20th_century": 1.0, "is_leader": 1.0, "has_famous_catchphrase": 0.7}),

    ("Winston Churchill", "British Prime Minister during World War II", "person", "en",
     ["Уинстон Черчилль", "Черчилль"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_politics": 1.0, "from_europe": 1.0, "from_history": 1.0,
      "era_20th_century": 1.0, "is_leader": 1.0, "has_famous_catchphrase": 1.0}),

    ("Martin Luther King", "American civil rights leader", "person", "en",
     ["Мартин Лютер Кинг", "MLK"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_politics": 1.0, "from_usa": 1.0, "from_history": 1.0,
      "era_20th_century": 1.0, "is_leader": 1.0, "has_famous_catchphrase": 1.0}),

    ("Махатма Ганди", "Индийский лидер, борец за независимость", "person", "ru",
     ["Mahatma Gandhi", "Gandhi"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_politics": 1.0, "from_asia": 1.0, "from_history": 1.0,
      "era_20th_century": 1.0, "is_leader": 1.0, "has_famous_catchphrase": 0.8}),

    ("John Lennon", "Beatles musician and peace activist", "person", "en",
     ["Джон Леннон"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_music": 1.0, "from_europe": 1.0,
      "era_20th_century": 1.0, "has_famous_catchphrase": 0.8}),

    ("Bob Marley", "Jamaican reggae legend", "person", "en",
     ["Боб Марли"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_music": 1.0,
      "era_20th_century": 1.0, "has_famous_catchphrase": 0.7}),

    ("BTS Jungkook", "South Korean K-pop singer, member of BTS", "person", "en",
     ["Чонгук", "Jungkook"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_music": 1.0, "from_asia": 1.0,
      "era_21st_century": 1.0, "is_wealthy": 0.8}),

    ("Drake", "Canadian rapper and singer", "person", "en",
     ["Дрейк"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_music": 1.0, "from_usa": 0.7,
      "era_21st_century": 1.0, "is_wealthy": 1.0}),

    ("Billie Eilish", "American singer-songwriter, Gen Z pop icon", "person", "en",
     ["Билли Айлиш"],
     {"is_fictional": 0.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.8,
      "is_villain": 0.0, "from_music": 1.0, "from_usa": 1.0,
      "era_21st_century": 1.0, "is_wealthy": 0.8}),

    # ──────────────── More comics / superheroes ────────────────

    ("Doctor Strange", "Marvel sorcerer, former neurosurgeon", "character", "en",
     ["Доктор Стрэндж"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_comics": 1.0, "from_usa": 1.0,
      "has_superpower": 1.0, "from_science": 0.5, "wears_uniform": 0.8, "is_wealthy": 0.7}),

    ("Black Panther", "Marvel superhero, king of Wakanda", "character", "en",
     ["Чёрная Пантера", "T'Challa"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_comics": 1.0,
      "has_superpower": 0.8, "wears_uniform": 1.0, "is_leader": 1.0, "is_wealthy": 1.0}),

    ("Green Lantern", "DC superhero powered by a green power ring", "character", "en",
     ["Зелёный Фонарь"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 0.7, "from_comics": 1.0, "from_usa": 1.0,
      "has_superpower": 1.0, "wears_uniform": 1.0}),

    ("Flash", "DC superhero with super speed", "character", "en",
     ["Флэш", "Barry Allen"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 0.8, "from_comics": 1.0, "from_tv_series": 1.0,
      "from_usa": 1.0, "has_superpower": 1.0, "wears_uniform": 1.0}),

    ("Aquaman", "DC superhero, king of Atlantis", "character", "en",
     ["Аквамен"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_comics": 1.0,
      "has_superpower": 1.0, "wears_uniform": 0.7, "is_leader": 1.0, "is_wealthy": 1.0}),

    ("Venom", "Marvel anti-hero, alien symbiote", "character", "en",
     ["Веном"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.6, "from_movie": 1.0, "from_comics": 1.0, "from_usa": 1.0,
      "has_superpower": 1.0}),

    # ──────────────── Mythological / fairy tale ────────────────

    ("Геракл", "Древнегреческий герой, сын Зевса", "character", "ru",
     ["Hercules", "Геркулес"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 0.7, "from_book": 1.0, "from_europe": 1.0,
      "has_superpower": 1.0, "from_history": 0.5, "era_ancient": 1.0}),

    ("Одиссей", "Хитроумный царь Итаки из греческих мифов", "character", "ru",
     ["Odysseus", "Ulysses"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_book": 1.0, "from_europe": 1.0,
      "is_leader": 1.0, "era_ancient": 1.0, "from_history": 0.5}),

    ("Кощей Бессмертный", "Злодей из русских сказок, хранит смерть в игле", "character", "ru",
     ["Koschei"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 1.0, "from_book": 1.0, "from_russia": 1.0,
      "has_superpower": 1.0, "is_wealthy": 0.8, "era_medieval": 0.8}),

    ("Иван-дурак", "Младший сын из русских сказок, всегда побеждает", "character", "ru",
     ["Ivan the Fool"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.7,
      "is_villain": 0.0, "from_book": 1.0, "from_russia": 1.0,
      "is_wealthy": 0.0, "era_medieval": 0.8}),

    ("Снегурочка", "Внучка Деда Мороза, персонаж русских сказок", "character", "ru",
     ["Snow Maiden"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 0.5, "is_alive": 1.0, "is_adult": 0.5,
      "is_villain": 0.0, "from_book": 0.7, "from_russia": 1.0,
      "has_superpower": 0.5, "era_medieval": 0.5}),

    # ──────────────── Internet / meme culture ────────────────

    ("PewDiePie", "Swedish YouTuber, one of the most subscribed creators", "person", "en",
     ["Пьюдипай", "Felix Kjellberg"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_europe": 1.0, "from_game": 0.5,
      "era_21st_century": 1.0, "is_wealthy": 0.8}),

    ("MrBeast", "American YouTuber known for expensive stunts and charity", "person", "en",
     ["МрБист", "Jimmy Donaldson"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_usa": 1.0,
      "era_21st_century": 1.0, "is_wealthy": 1.0}),

    # ──────────────── More Russian culture ────────────────

    ("Штирлиц", "Советский разведчик из фильма 17 мгновений весны", "character", "ru",
     ["Stirlitz", "Исаев"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_tv_series": 1.0, "from_russia": 1.0,
      "from_europe": 0.8, "wears_uniform": 1.0, "has_famous_catchphrase": 1.0,
      "era_20th_century": 1.0}),

    ("Остап Бендер", "Великий комбинатор из романов Ильфа и Петрова", "character", "ru",
     ["Ostap Bender"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.5, "from_book": 1.0, "from_movie": 1.0, "from_russia": 1.0,
      "has_famous_catchphrase": 1.0, "era_20th_century": 1.0}),

    ("Маша", "Непоседливая девочка из мультфильма Маша и Медведь", "character", "ru",
     ["Masha"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.0,
      "is_villain": 0.0, "from_tv_series": 1.0, "from_russia": 1.0,
      "era_21st_century": 1.0}),

    ("Леопольд", "Добрый кот из советского мультфильма", "character", "ru",
     ["Кот Леопольд", "Leopold"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_tv_series": 1.0, "from_russia": 1.0,
      "has_famous_catchphrase": 1.0, "era_20th_century": 1.0}),

    ("Волк из Ну погоди", "Хулиганистый волк, преследует зайца", "character", "ru",
     ["Wolf", "Ну погоди волк"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.7, "from_tv_series": 1.0, "from_russia": 1.0,
      "has_famous_catchphrase": 1.0, "era_20th_century": 1.0}),

    # ──────────────── Final batch to 200+ ────────────────

    ("John Wick", "Legendary hitman seeking revenge, played by Keanu Reeves", "character", "en",
     ["Джон Уик"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.3, "from_movie": 1.0, "from_usa": 1.0,
      "era_21st_century": 1.0}),

    ("Rocky Balboa", "Underdog boxer from the Rocky film series", "character", "en",
     ["Рокки Бальбоа", "Rocky"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_sport": 1.0, "from_usa": 1.0,
      "has_famous_catchphrase": 0.8, "era_20th_century": 1.0}),

    ("Forrest Gump", "Kind simple-minded man who witnesses history", "character", "en",
     ["Форрест Гамп"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_book": 1.0, "from_usa": 1.0,
      "has_famous_catchphrase": 1.0, "from_sport": 0.4, "era_20th_century": 1.0}),

    ("Hannibal Lecter", "Brilliant psychiatrist and cannibalistic serial killer", "character", "en",
     ["Ганнибал Лектер", "Hannibal"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 1.0, "from_movie": 1.0, "from_book": 1.0, "from_tv_series": 0.8,
      "from_usa": 0.5, "from_europe": 0.5, "from_science": 0.5,
      "is_wealthy": 0.8, "era_20th_century": 1.0}),

    ("Mulan", "Chinese warrior who disguises as a man to save her father", "character", "en",
     ["Мулан"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 0.8,
      "is_villain": 0.0, "from_movie": 1.0, "from_book": 0.7, "from_asia": 1.0,
      "wears_uniform": 1.0, "era_medieval": 0.8}),

    ("Ryu", "Japanese martial artist from Street Fighter", "character", "en",
     ["Рю"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_game": 1.0, "from_japan": 1.0, "from_asia": 1.0,
      "wears_uniform": 0.7, "has_famous_catchphrase": 1.0, "has_superpower": 0.7}),

    ("Lara Croft (reboot)", "Young archaeologist and survivor from Tomb Raider reboot", "character", "en",
     ["Лара Крофт 2013"],
     {"is_fictional": 1.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_game": 1.0, "from_movie": 0.5, "from_europe": 1.0,
      "era_21st_century": 1.0}),

    ("Pinocchio", "Wooden puppet who wants to become a real boy", "character", "en",
     ["Пиноккио", "Буратино"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 1.0, "is_adult": 0.0,
      "is_villain": 0.0, "from_movie": 1.0, "from_book": 1.0, "from_europe": 1.0,
      "has_famous_catchphrase": 0.5, "era_modern": 0.8}),

    ("Дед Мороз", "Русский новогодний волшебник", "character", "ru",
     ["Ded Moroz", "Father Frost"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_russia": 1.0, "has_superpower": 1.0,
      "wears_uniform": 1.0, "is_wealthy": 0.5}),

    ("Santa Claus", "Christmas gift-giver who lives at the North Pole", "character", "en",
     ["Санта Клаус", "Santa"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_usa": 0.5, "from_europe": 0.5,
      "has_superpower": 1.0, "wears_uniform": 1.0, "is_wealthy": 0.5,
      "has_famous_catchphrase": 1.0}),

    ("Чужой", "Инопланетный хищник из фильма Alien", "character", "ru",
     ["Alien", "Xenomorph"],
     {"is_fictional": 1.0, "is_male": 0.5, "is_human": 0.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 1.0, "from_movie": 1.0, "from_usa": 1.0,
      "has_superpower": 0.5, "era_20th_century": 1.0}),

    ("Predator", "Alien hunter who collects trophies from worthy prey", "character", "en",
     ["Хищник"],
     {"is_fictional": 1.0, "is_male": 1.0, "is_human": 0.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.7, "from_movie": 1.0, "from_usa": 1.0,
      "has_superpower": 0.5, "wears_uniform": 0.7, "era_20th_century": 1.0}),

    ("ET", "Friendly alien stranded on Earth from Spielberg's film", "character", "en",
     ["Инопланетянин", "E.T."],
     {"is_fictional": 1.0, "is_male": 0.5, "is_human": 0.0, "is_alive": 1.0, "is_adult": 0.5,
      "is_villain": 0.0, "from_movie": 1.0, "from_usa": 1.0,
      "has_superpower": 0.7, "has_famous_catchphrase": 1.0, "era_20th_century": 1.0}),

    ("Опра Уинфри", "Американская телеведущая и медиамагнат", "person", "ru",
     ["Oprah Winfrey", "Oprah"],
     {"is_fictional": 0.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_tv_series": 0.8, "from_usa": 1.0,
      "era_21st_century": 1.0, "is_leader": 0.8, "is_wealthy": 1.0}),

    ("Майкл Джордан", "Величайший баскетболист всех времён", "person", "ru",
     ["Michael Jordan", "MJ"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_sport": 1.0, "from_usa": 1.0,
      "era_20th_century": 0.8, "era_21st_century": 0.5, "is_wealthy": 1.0,
      "has_famous_catchphrase": 0.5}),

    ("Коби Брайант", "Легендарный баскетболист Лейкерс", "person", "ru",
     ["Kobe Bryant", "Kobe"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_sport": 1.0, "from_usa": 1.0,
      "era_21st_century": 1.0, "is_wealthy": 1.0}),

    ("Диего Марадона", "Аргентинский футболист, автор Руки Бога", "person", "ru",
     ["Diego Maradona", "Maradona"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0, "is_adult": 1.0,
      "is_villain": 0.2, "from_sport": 1.0,
      "era_20th_century": 1.0, "is_wealthy": 0.8, "has_famous_catchphrase": 0.7}),

    ("Зинедин Зидан", "Французский футболист и тренер", "person", "ru",
     ["Zinedine Zidane", "Zidane"],
     {"is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0, "is_adult": 1.0,
      "is_villain": 0.0, "from_sport": 1.0, "from_europe": 1.0,
      "era_21st_century": 1.0, "is_leader": 0.7, "is_wealthy": 0.9}),
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
