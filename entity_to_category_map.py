"""Manual mapping of existing 203 entities to categories.

This maps entity names to their appropriate category from categories.py
"""

from typing import Optional

ENTITY_CATEGORY_MAP = {
    # Star Wars
    "Darth Vader": "star_wars_dark",
    "Yoda": "star_wars_light",
    "Luke Skywalker": "star_wars_light",
    "Princess Leia": "star_wars_light",

    # Harry Potter
    "Harry Potter": "hp_good",
    "Hermione Granger": "hp_good",
    "Voldemort": "hp_dark",
    "Gandalf": "lotr_good",  # Actually LOTR

    # Nintendo/Games
    "Mario": "game_nintendo",
    "Link": "game_nintendo",
    "Pikachu": "game_nintendo",
    "Sonic the Hedgehog": "game_nintendo",
    "Princess Zelda": "game_nintendo",
    "Minecraft Steve": "game_hero",
    "Among Us Crewmate": "game_hero",
    "GTA Trevor": "game_villain",
    "Pac-Man": "game_nintendo",
    "Kratos": "game_hero",
    "Master Chief": "game_hero",
    "Lara Croft": "game_hero",
    "Lara Croft (reboot)": "game_hero",
    "Cloud Strife": "game_hero",
    "Ryu": "game_fighting",
    "Nemo": "pixar_character",

    # Marvel
    "Spider-Man": "marvel_hero",
    "Iron Man": "marvel_hero",
    "Captain America": "marvel_hero",
    "Thor": "marvel_hero",
    "Hulk": "marvel_hero",
    "Black Widow": "marvel_hero",
    "Wolverine": "marvel_hero",
    "Deadpool": "marvel_hero",
    "Doctor Strange": "marvel_hero",
    "Black Panther": "marvel_hero",
    "Thanos": "marvel_villain",
    "Loki": "marvel_villain",
    "Venom": "marvel_villain",

    # DC
    "Batman": "dc_hero",
    "Superman": "dc_hero",
    "Wonder Woman": "dc_hero",
    "Green Lantern": "dc_hero",
    "Flash": "dc_hero",
    "Aquaman": "dc_hero",
    "Joker": "dc_villain",

    # Anime
    "Naruto": "anime_shonen_hero",
    "Sasuke Uchiha": "anime_shonen_villain",
    "Sakura Haruno": "anime_female",
    "Goku": "anime_shonen_hero",
    "Vegeta": "anime_shonen_villain",
    "Luffy": "anime_shonen_hero",
    "Light Yagami": "anime_shonen_villain",
    "Eren Yeager": "anime_shonen_hero",
    "Mikasa Ackerman": "anime_female",
    "Saitama": "anime_shonen_hero",
    "Sailor Moon": "anime_female",
    "Lelouch Lamperouge": "anime_shonen_hero",
    "Edward Elric": "anime_shonen_hero",
    "Тоторо": "anime_female",

    # LOTR
    "Frodo Baggins": "lotr_good",
    "Aragorn": "lotr_good",

    # Movies/TV
    "Sherlock Holmes": "literature_classic",
    "James Bond": "tv_drama",
    "Indiana Jones": "tv_drama",
    "Jack Sparrow": "disney_hero",
    "Terminator": "tv_drama",
    "Neo": "tv_drama",
    "Walter White": "tv_drama",
    "Geralt of Rivia": "tv_fantasy",
    "Homer Simpson": "tv_animated",
    "SpongeBob SquarePants": "tv_animated",
    "Sheldon Cooper": "tv_comedy",
    "Daenerys Targaryen": "tv_fantasy",
    "Jon Snow": "tv_fantasy",
    "Rick Sanchez": "tv_animated",
    "Dexter Morgan": "tv_drama",
    "Eleven": "tv_drama",
    "Tommy Shelby": "tv_drama",
    "John Wick": "tv_drama",
    "Rocky Balboa": "tv_drama",
    "Forrest Gump": "tv_drama",
    "Hannibal Lecter": "horror_character",
    "Штирлиц": "russian_film_character",
    "Остап Бендер": "russian_film_character",

    # Disney/Pixar
    "Shrek": "disney_hero",
    "Elsa": "disney_princess",
    "Mickey Mouse": "disney_sidekick",
    "Simba": "disney_hero",
    "Buzz Lightyear": "pixar_character",
    "Woody": "pixar_character",
    "Rapunzel": "disney_princess",
    "Maui": "disney_hero",
    "Maleficent": "disney_villain",
    "Aladdin": "disney_hero",
    "Genie": "disney_sidekick",
    "Shrek's Donkey": "disney_sidekick",
    "Mulan": "disney_princess",
    "Pinocchio": "disney_hero",

    # Cartoons
    "Tom": "tv_animated",
    "Jerry": "tv_animated",
    "Bugs Bunny": "tv_animated",
    "Winnie the Pooh": "tv_animated",
    "Чебурашка": "soviet_cartoon",
    "Кот Матроскин": "soviet_cartoon",
    "Незнайка": "soviet_cartoon",
    "Маша": "soviet_cartoon",
    "Леопольд": "soviet_cartoon",
    "Волк из Ну погоди": "soviet_cartoon",

    # Mythology/Fairy Tales
    "Dracula": "horror_character",
    "Frankenstein's Monster": "horror_character",
    "Robin Hood": "fairy_tale_western",
    "Romeo": "literature_classic",
    "D'Artagnan": "literature_classic",
    "Zorro": "tv_drama",
    "Merlin": "myth_greek",
    "Геракл": "myth_greek",
    "Одиссей": "myth_greek",
    "Баба-Яга": "fairy_tale_russian",
    "Кощей Бессмертный": "fairy_tale_russian",
    "Иван-дурак": "fairy_tale_russian",
    "Снегурочка": "fairy_tale_russian",
    "Илья Муромец": "fairy_tale_russian",
    "Дед Мороз": "fairy_tale_russian",
    "Santa Claus": "fairy_tale_western",
    "Чужой": "horror_character",
    "Predator": "horror_character",
    "ET": "tv_drama",

    # Politicians
    "Elon Musk": "tech_leader",
    "Владимир Путин": "politician_modern",
    "Дональд Трамп": "politician_modern",
    "Барак Обама": "politician_modern",
    "Queen Elizabeth II": "politician_historical",
    "Napoleon": "politician_historical",
    "Пётр I": "ruler_medieval",
    "Юлий Цезарь": "ruler_ancient",
    "Чингисхан": "ruler_medieval",
    "Александр Великий": "ruler_ancient",
    "Спартак": "ruler_ancient",
    "Маргарет Тэтчер": "politician_modern",
    "Winston Churchill": "politician_historical",
    "Martin Luther King": "politician_modern",
    "Махатма Ганди": "politician_historical",
    "Cleopatra": "ruler_ancient",

    # Scientists
    "Albert Einstein": "scientist_modern",
    "Юрий Гагарин": "scientist_modern",
    "Leonardo da Vinci": "visual_artist",
    "Marie Curie": "scientist_modern",
    "Дмитрий Менделеев": "scientist",
    "Никола Тесла": "scientist",
    "Isaac Newton": "scientist",
    "Stephen Hawking": "scientist_modern",
    "Steve Jobs": "tech_leader",
    "Марк Цукерберг": "tech_leader",
    "Bill Gates": "tech_leader",
    "Jeff Bezos": "tech_leader",

    # Musicians
    "Michael Jackson": "musician_pop",
    "Taylor Swift": "musician_pop",
    "Elvis Presley": "musician_rock",
    "Фредди Меркьюри": "musician_rock",
    "Eminem": "musician_hiphop",
    "Mozart": "musician_classical",
    "Beethoven": "musician_classical",
    "John Lennon": "musician_rock",
    "Bob Marley": "musician_rock",
    "BTS Jungkook": "musician_pop",
    "Drake": "musician_hiphop",
    "Billie Eilish": "musician_pop",
    "Владимир Высоцкий": "musician_russian",
    "Алла Пугачёва": "musician_russian",
    "Виктор Цой": "musician_russian",

    # Athletes
    "Lionel Messi": "athlete_football",
    "Cristiano Ronaldo": "athlete_football",
    "Muhammad Ali": "athlete_boxing_mma",
    "Mike Tyson": "athlete_boxing_mma",
    "LeBron James": "athlete_basketball",
    "Усэйн Болт": "athlete_other",
    "Хабиб Нурмагомедов": "athlete_boxing_mma",
    "Neymar": "athlete_football",
    "Serena Williams": "athlete_tennis",
    "Conor McGregor": "athlete_boxing_mma",
    "Майкл Джордан": "athlete_basketball",
    "Коби Брайант": "athlete_basketball",
    "Диего Марадона": "athlete_football",
    "Зинедин Зидан": "athlete_football",

    # Actors
    "Arnold Schwarzenegger": "actor_hollywood",
    "Bruce Lee": "actor_hollywood",
    "Jackie Chan": "actor_hollywood",
    "Чарли Чаплин": "director",
    "Marilyn Monroe": "actor_hollywood",
    "Audrey Hepburn": "actor_hollywood",
    "Keanu Reeves": "actor_hollywood",
    "Morgan Freeman": "actor_hollywood",
    "Johnny Depp": "actor_hollywood",
    "Angelina Jolie": "actor_hollywood",
    "Дмитрий Нагиев": "actor_russian",

    # Writers
    "Александр Пушкин": "writer_russian",
    "Николай Гоголь": "writer_russian",
    "Лев Толстой": "writer_russian",
    "Фёдор Достоевский": "writer_russian",
    "Михаил Булгаков": "writer_russian",

    # Artists
    "Пикассо": "visual_artist",

    # Internet
    "PewDiePie": "youtuber",
    "MrBeast": "youtuber",
    "Опра Уинфри": "model_influencer",
}


def get_category(entity_name: str) -> Optional[str]:
    """Get category for entity name, or None if not found."""
    return ENTITY_CATEGORY_MAP.get(entity_name)


# Entity-specific attribute overrides
# These override the category template defaults for specific entities
ENTITY_OVERRIDES = {
    # Tech Leaders - distinguish by birth decade and internet focus
    "Elon Musk": {
        "born_1970s": 1.0,
        "born_1950s": 0.0,
        "born_1980s": 0.0,
        "from_internet": 0.3,
    },
    "Bill Gates": {
        "born_1950s": 1.0,
        "born_1970s": 0.0,
        "born_1980s": 0.0,
        "from_internet": 0.7,
    },
    "Марк Цукерберг": {
        "born_1980s": 1.0,
        "born_1950s": 0.0,
        "born_1970s": 0.0,
        "from_internet": 1.0,
    },

    # Athletes - distinguish by birth decade and region
    "Lionel Messi": {
        "born_1980s": 1.0,
        "born_1970s": 0.0,
        "from_south_america": 1.0,
        "from_europe": 0.2,
        "is_alive": 1.0,
    },
    "Зинедин Зидан": {
        "born_1970s": 1.0,
        "born_1980s": 0.0,
        "from_south_america": 0.0,
        "from_europe": 1.0,
        "from_africa": 0.3,  # Algerian heritage
        "is_alive": 0.5,  # Retired from playing
    },

    # Marvel Heroes - visual and personality traits
    "Wolverine": {
        "has_facial_hair": 1.0,
        "is_dark_brooding": 1.0,
        "is_child_friendly": 0.3,
        "has_armor": 0.0,
        "wears_mask": 0.2,
        "is_comedic": 0.0,
    },
    "Spider-Man": {
        "has_facial_hair": 0.0,
        "is_dark_brooding": 0.0,
        "is_child_friendly": 1.0,
        "wears_mask": 1.0,
        "is_comedic": 0.7,
        "has_armor": 0.0,
    },
    "Hulk": {
        "has_facial_hair": 0.0,
        "is_dark_brooding": 0.5,
        "is_child_friendly": 0.5,
        "wears_mask": 0.0,
        "is_comedic": 0.0,
        "has_armor": 0.0,
        "is_action_hero": 1.0,
        "wears_uniform": 0.2,  # Torn pants
    },

    # Classic Cartoons - distinguish by characteristics
    "Mickey Mouse": {
        "is_child_friendly": 1.0,
        "from_usa": 1.0,
        "has_famous_catchphrase": 1.0,
        "is_comedic": 0.3,
        "is_action_hero": 0.0,
        "from_movie": 1.0,
        "era_20th_century": 1.0,
    },
    "Tom": {
        "is_child_friendly": 1.0,
        "is_comedic": 1.0,
        "is_villain": 0.5,
        "has_famous_catchphrase": 0.2,
    },
    "Jerry": {
        "is_child_friendly": 1.0,
        "is_comedic": 1.0,
        "is_villain": 0.0,
        "has_famous_catchphrase": 0.2,
    },
    "Bugs Bunny": {
        "is_child_friendly": 0.9,
        "is_comedic": 1.0,
        "has_famous_catchphrase": 1.0,
        "is_action_hero": 0.3,
        "is_villain": 0.0,
        "from_tv_series": 1.0,
    },

    # Politicians - birth decade and business background
    "Барак Обама": {
        "born_1960s": 1.0,
        "born_1940s": 0.0,
        "from_business": 0.0,
        "from_internet": 0.3,
        "from_literature": 0.3,  # Author
    },
    "Дональд Трамп": {
        "born_1940s": 1.0,
        "born_1960s": 0.0,
        "from_business": 1.0,
        "from_internet": 0.5,
        "is_wealthy": 1.0,
    },

    # Classical Composers - subtle differences
    "Mozart": {
        "is_alive": 0.0,
        "era_modern": 1.0,
        "from_art": 0.2,
        "is_dark_brooding": 0.0,
        "is_child_friendly": 0.8,
        "from_europe": 1.0,
        "from_usa": 0.0,
    },
    "Beethoven": {
        "is_alive": 0.0,
        "era_modern": 1.0,
        "from_art": 0.5,
        "is_dark_brooding": 0.6,
        "is_child_friendly": 0.5,
        "from_europe": 1.0,
        "from_usa": 0.0,
    },

    # Russian Writers - philosophical depth vs satire
    "Фёдор Достоевский": {
        "from_philosophy": 0.7,
        "from_literature": 1.0,
        "is_dark_brooding": 0.8,
        "era_modern": 1.0,
        "is_comedic": 0.0,
    },
    "Николай Гоголь": {
        "from_philosophy": 0.3,
        "from_literature": 1.0,
        "is_comedic": 0.5,
        "is_dark_brooding": 0.4,
        "era_modern": 1.0,
    },

    # Hollywood Actors - distinguish by era and style
    "Keanu Reeves": {
        "born_1960s": 1.0,
        "born_1930s": 0.0,
        "from_movie": 1.0,
        "is_action_hero": 0.3,
        "has_facial_hair": 0.6,
        "is_dark_brooding": 0.4,
        "is_comedic": 0.1,
    },
    "Johnny Depp": {
        "born_1960s": 1.0,
        "born_1930s": 0.0,
        "from_movie": 1.0,
        "is_action_hero": 0.6,
        "has_facial_hair": 0.8,
        "is_dark_brooding": 0.5,
        "is_comedic": 0.4,
    },
    "Morgan Freeman": {
        "born_1930s": 1.0,
        "born_1960s": 0.0,
        "from_movie": 1.0,
        "has_facial_hair": 0.3,
        "is_dark_brooding": 0.2,
        "is_comedic": 0.1,
        "has_famous_catchphrase": 0.4,
    },

    # Musicians - different genres and origins
    "Bob Marley": {
        "born_1940s": 1.0,
        "born_1930s": 0.0,
        "from_music": 1.0,
        "from_africa": 0.5,
        "has_facial_hair": 1.0,
        "is_dark_brooding": 0.0,
        "is_child_friendly": 0.7,
    },
    "John Lennon": {
        "born_1940s": 1.0,
        "from_music": 1.0,
        "from_europe": 1.0,
        "from_africa": 0.0,
        "has_facial_hair": 0.4,
        "is_dark_brooding": 0.3,
        "is_child_friendly": 0.6,
        "from_art": 0.3,
    },

    # ──────────────────────────────────────────
    # New overrides to fix confusion pairs
    # ──────────────────────────────────────────

    # Deadpool vs Spider-Man - Deadpool is R-rated, very comedic, anti-hero
    "Deadpool": {
        "is_child_friendly": 0.0,
        "is_comedic": 1.0,
        "is_villain": 0.4,  # Anti-hero
        "is_dark_brooding": 0.0,
        "has_famous_catchphrase": 1.0,
        "wears_mask": 1.0,
        "has_facial_hair": 0.0,  # Scarred under mask
        "from_movie": 1.0,
    },

    # Batman vs Black Panther - Batman has no powers, uses tech/gadgets
    "Batman": {
        "has_superpower": 0.0,
        "is_wealthy": 1.0,
        "is_dark_brooding": 1.0,
        "from_usa": 1.0,
        "from_africa": 0.0,
        "wears_mask": 1.0,
        "has_armor": 0.3,
        "is_leader": 0.3,
    },
    "Black Panther": {
        "has_superpower": 0.7,
        "is_wealthy": 1.0,
        "is_dark_brooding": 0.3,
        "from_usa": 0.3,
        "from_africa": 1.0,
        "wears_mask": 1.0,
        "has_armor": 1.0,
        "is_leader": 1.0,
    },

    # Naruto vs Saitama vs Luffy - distinguish anime protagonists
    "Naruto": {
        "is_comedic": 0.4,
        "has_famous_catchphrase": 1.0,  # "Believe it!"
        "is_leader": 1.0,  # Becomes Hokage
        "has_superpower": 1.0,
        "wears_uniform": 0.8,  # Orange outfit
        "has_facial_hair": 0.0,
        "from_japan": 1.0,
        "is_action_hero": 1.0,
    },
    "Luffy": {
        "is_comedic": 0.7,  # More comedic than Naruto
        "has_famous_catchphrase": 1.0,  # "I'm gonna be King of the Pirates!"
        "is_leader": 1.0,  # Captain
        "has_superpower": 1.0,  # Rubber powers
        "wears_uniform": 0.3,  # Casual clothes, straw hat
        "has_facial_hair": 0.0,
        "from_japan": 1.0,
        "is_action_hero": 1.0,
        "is_wealthy": 0.0,  # Pirate, not rich
        "from_sport": 0.0,
        "is_dark_brooding": 0.0,  # Always cheerful
    },
    "Saitama": {
        "is_comedic": 1.0,  # One Punch Man is comedy
        "has_famous_catchphrase": 0.5,
        "is_leader": 0.0,
        "has_superpower": 1.0,
        "wears_uniform": 0.3,  # Plain hero suit
        "has_facial_hair": 0.0,
        "is_dark_brooding": 0.0,
    },

    # Thor vs Black Panther - Thor is Norse god with hammer
    "Thor": {
        "from_europe": 1.0,  # Norse mythology
        "from_africa": 0.0,
        "has_superpower": 1.0,
        "is_leader": 0.8,  # King of Asgard
        "has_armor": 1.0,
        "has_facial_hair": 0.6,
        "wears_mask": 0.0,
    },

    # Freddie Mercury vs Elvis - different decades and styles
    "Фредди Меркьюри": {
        "born_1940s": 1.0,
        "born_1930s": 0.0,
        "from_europe": 1.0,  # UK based
        "from_africa": 0.2,  # Born in Zanzibar
        "has_facial_hair": 1.0,  # Famous mustache
        "is_alive": 0.0,
        "era_20th_century": 1.0,
    },
    "Elvis Presley": {
        "born_1930s": 1.0,
        "born_1940s": 0.0,
        "from_usa": 1.0,
        "from_europe": 0.0,
        "has_facial_hair": 0.0,  # Clean shaven
        "is_alive": 0.0,
        "era_20th_century": 1.0,
    },

    # Maui vs Genie - Maui is Polynesian demigod, Genie is from Arabia
    "Maui": {
        "from_oceania": 1.0,
        "from_middle_east": 0.0,
        "has_superpower": 1.0,
        "is_human": 0.5,  # Demigod
        "is_comedic": 0.6,
        "has_famous_catchphrase": 1.0,  # "You're welcome!"
        "has_facial_hair": 0.0,
    },
    "Genie": {
        "from_oceania": 0.0,
        "from_middle_east": 1.0,
        "has_superpower": 1.0,
        "is_human": 0.0,  # Magical being
        "is_comedic": 1.0,
        "has_famous_catchphrase": 1.0,
        "has_facial_hair": 0.3,
    },

    # Спартак vs Александр Великий - Spartacus was slave, Alexander was king
    "Спартак": {
        "is_leader": 0.7,  # Led slave revolt
        "is_wealthy": 0.0,  # Was a slave
        "from_military": 1.0,
        "is_villain": 0.0,  # Freedom fighter
        "era_ancient": 1.0,
        "from_europe": 1.0,
    },
    "Александр Великий": {
        "is_leader": 1.0,  # Emperor/King
        "is_wealthy": 1.0,  # Royalty
        "from_military": 1.0,
        "is_villain": 0.3,  # Conqueror
        "era_ancient": 1.0,
        "from_europe": 0.7,
        "from_asia": 0.5,  # Conquered East
    },

    # Волк vs Леопольд - Wolf is troublemaker, Leopold is peaceful
    "Волк из Ну погоди": {
        "is_villain": 0.8,
        "is_comedic": 1.0,
        "has_famous_catchphrase": 1.0,  # "Ну погоди!"
        "is_child_friendly": 0.7,
        "is_adult": 1.0,
        "from_russia": 1.0,
    },
    "Леопольд": {
        "is_villain": 0.0,
        "is_comedic": 0.7,
        "has_famous_catchphrase": 1.0,  # "Ребята, давайте жить дружно!"
        "is_child_friendly": 1.0,
        "is_adult": 1.0,
        "from_russia": 1.0,
        "is_dark_brooding": 0.0,
    },
}


def get_overrides(entity_name: str) -> Optional[dict[str, float]]:
    """Get attribute overrides for specific entity, or None if no overrides."""
    return ENTITY_OVERRIDES.get(entity_name)
