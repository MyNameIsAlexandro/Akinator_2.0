#!/usr/bin/env python3
"""Fix attributes for fictional characters using rule-based overrides.

Since fictional characters don't have detailed Wikidata properties,
we use name-based rules to differentiate them.
"""

import sqlite3
from pathlib import Path

# Character-specific overrides
CHARACTER_RULES = {
    # Disney Princesses - differentiate by movie/era/traits
    "Elsa": {"has_superpower": 1.0, "distinctive_hair": 1.0, "born_after_1990": 1.0},
    "Anna": {"has_superpower": 0.0, "distinctive_hair": 1.0, "born_after_1990": 1.0},
    "Ariel": {"is_human": 0.3, "distinctive_hair": 1.0, "from_music": 0.7, "born_1970_1990": 1.0},
    "Belle": {"from_book": 0.8, "has_glasses": 0.0, "born_1970_1990": 1.0},
    "Jasmine": {"from_asia": 0.8, "is_wealthy": 0.9, "born_1970_1990": 1.0},
    "Mulan": {"from_china": 1.0, "from_asia": 1.0, "wears_uniform": 0.8, "is_action_hero": 0.7},
    "Pocahontas": {"from_usa": 1.0, "era_modern": 0.8, "from_history": 0.5},
    "Cinderella": {"born_before_1950": 1.0, "is_wealthy": 0.3},
    "Snow White": {"born_before_1950": 1.0, "is_dark_brooding": 0.0},
    "Rapunzel": {"distinctive_hair": 1.0, "born_after_1990": 1.0, "has_superpower": 0.5},
    "Moana": {"from_asia": 0.3, "born_after_1990": 1.0, "has_superpower": 0.3},
    "Tiana": {"from_usa": 1.0, "is_wealthy": 0.2, "born_after_1990": 1.0},

    # Pixar characters
    "Woody": {"is_human": 0.0, "from_usa": 1.0, "wears_uniform": 0.8, "is_leader": 0.7},
    "Buzz Lightyear": {"is_human": 0.0, "from_scifi_genre": 0.8, "has_armor": 0.9, "is_action_hero": 0.8},
    "Nemo": {"is_human": 0.0, "is_child_friendly": 1.0, "from_scifi_genre": 0.0},
    "Dory": {"is_human": 0.0, "is_comedic": 0.9, "is_child_friendly": 1.0},
    "Lightning McQueen": {"is_human": 0.0, "from_sport": 0.7, "from_usa": 1.0},
    "Wall-E": {"is_human": 0.0, "from_scifi_genre": 1.0, "is_comedic": 0.5},
    "Sulley": {"is_human": 0.0, "from_horror_genre": 0.3, "known_for_physique": 0.8},
    "Mike Wazowski": {"is_human": 0.0, "is_comedic": 0.9, "has_glasses": 0.0},
    "Remy": {"is_human": 0.0, "from_europe": 1.0, "is_action_hero": 0.0},
    "Mr Incredible": {"is_human": 0.7, "has_superpower": 1.0, "known_for_physique": 0.9, "has_armor": 0.3},

    # Other animation
    "Shrek": {"is_human": 0.0, "from_comedy_genre": 0.9, "is_villain": 0.1, "distinctive_hair": 0.0},
    "donkey": {"is_human": 0.0, "is_comedic": 1.0, "from_comedy_genre": 0.9},
    "SpongeBob SquarePants": {"is_human": 0.0, "is_comedic": 1.0, "is_child_friendly": 1.0, "born_after_1990": 1.0},
    "Patrick Star": {"is_human": 0.0, "is_comedic": 1.0, "is_child_friendly": 1.0},
    "Bugs Bunny": {"is_human": 0.0, "is_comedic": 1.0, "born_before_1950": 1.0},
    "Tom": {"is_human": 0.0, "is_comedic": 0.8, "is_villain": 0.5, "born_before_1950": 1.0},
    "Mickey Mouse": {"is_human": 0.0, "is_leader": 0.7, "is_comedic": 0.6, "born_before_1950": 1.0},
    "Donald Duck": {"is_human": 0.0, "is_comedic": 0.9, "wears_uniform": 0.8, "born_before_1950": 1.0},
    "Goofy": {"is_human": 0.0, "is_comedic": 1.0, "born_before_1950": 1.0},
    "Homer Simpson": {"is_human": 1.0, "is_comedic": 1.0, "is_bald": 1.0, "from_usa": 1.0, "is_adult": 1.0},
    "Bart Simpson": {"is_human": 1.0, "is_comedic": 0.9, "is_adult": 0.0, "distinctive_hair": 1.0},
    "Peter Griffin": {"is_human": 1.0, "is_comedic": 1.0, "known_for_physique": 0.5, "from_usa": 1.0},
    "Rick Sanchez": {"is_human": 1.0, "from_scifi_genre": 1.0, "has_distinctive_voice": 0.9, "is_dark_brooding": 0.4},
    "Morty Smith": {"is_human": 1.0, "from_scifi_genre": 1.0, "is_adult": 0.0, "is_comedic": 0.6},

    # Marvel superheroes - differentiate
    "Spider-Man": {"wears_mask": 1.0, "is_adult": 0.5, "from_usa": 1.0, "has_superpower": 1.0},
    "Iron Man": {"has_armor": 1.0, "is_wealthy": 1.0, "billionaire": 1.0, "wears_mask": 0.7},
    "Captain America": {"wears_uniform": 1.0, "has_superpower": 0.7, "is_leader": 0.9, "born_before_1950": 1.0},
    "Thor": {"has_superpower": 1.0, "is_human": 0.0, "from_europe": 0.5, "distinctive_hair": 0.8},
    "Hulk": {"has_superpower": 1.0, "known_for_physique": 1.0, "distinctive_hair": 0.0, "is_dark_brooding": 0.5},
    "Black Widow": {"is_male": 0.0, "from_russia": 1.0, "is_action_hero": 1.0, "has_superpower": 0.1},
    "Hawkeye": {"has_superpower": 0.0, "is_action_hero": 0.9, "wears_uniform": 0.6},
    "Black Panther": {"from_africa": 1.0, "is_wealthy": 1.0, "is_leader": 1.0, "wears_uniform": 1.0},
    "Doctor Strange": {"has_superpower": 1.0, "has_facial_hair": 1.0, "from_science": 0.5},
    "Scarlet Witch": {"is_male": 0.0, "has_superpower": 1.0, "from_europe": 0.7, "is_dark_brooding": 0.6},
    "Ant-Man": {"has_superpower": 0.8, "is_comedic": 0.6, "has_armor": 0.7},
    "Captain Marvel": {"is_male": 0.0, "has_superpower": 1.0, "from_scifi_genre": 0.7},
    "Wolverine": {"has_superpower": 1.0, "has_facial_hair": 1.0, "is_dark_brooding": 0.8, "is_action_hero": 1.0},
    "Deadpool": {"has_superpower": 0.8, "is_comedic": 1.0, "wears_mask": 1.0, "controversial": 0.7},
    "Professor X": {"has_superpower": 1.0, "is_bald": 1.0, "is_leader": 1.0, "has_glasses": 0.0},
    "Magneto": {"has_superpower": 1.0, "is_villain": 0.6, "from_europe": 0.8, "from_history": 0.5},
    "Storm": {"is_male": 0.0, "has_superpower": 1.0, "from_africa": 1.0, "distinctive_hair": 1.0},
    "Cyclops": {"has_superpower": 1.0, "has_glasses": 1.0, "is_leader": 0.6},
    "Jean Grey": {"is_male": 0.0, "has_superpower": 1.0, "distinctive_hair": 0.8, "is_dark_brooding": 0.4},
    "Venom": {"is_villain": 0.7, "is_human": 0.3, "is_dark_brooding": 1.0, "has_superpower": 1.0},
    "Thanos": {"is_villain": 1.0, "is_human": 0.0, "has_superpower": 1.0, "is_leader": 0.9},
    "Loki": {"is_villain": 0.6, "is_human": 0.0, "has_superpower": 1.0, "is_comedic": 0.4},

    # DC superheroes
    "Batman": {"has_superpower": 0.0, "is_wealthy": 1.0, "billionaire": 1.0, "is_dark_brooding": 1.0, "wears_mask": 1.0},
    "Superman": {"has_superpower": 1.0, "from_scifi_genre": 0.6, "is_action_hero": 1.0, "distinctive_hair": 0.3},
    "Wonder Woman": {"is_male": 0.0, "has_superpower": 1.0, "is_action_hero": 1.0, "era_ancient": 0.5},
    "Aquaman": {"has_superpower": 1.0, "is_leader": 0.8, "distinctive_hair": 0.7},
    "Flash": {"has_superpower": 1.0, "is_comedic": 0.4, "wears_uniform": 1.0},
    "Green Lantern": {"has_superpower": 1.0, "from_scifi_genre": 0.7, "wears_uniform": 1.0},
    "cyborg": {"has_superpower": 0.8, "is_human": 0.5, "from_scifi_genre": 0.8},
    "Shazam": {"has_superpower": 1.0, "is_adult": 0.5, "is_comedic": 0.5},
    "Martian Manhunter": {"has_superpower": 1.0, "is_human": 0.0, "from_scifi_genre": 1.0},
    "Robin": {"has_superpower": 0.0, "is_adult": 0.4, "wears_uniform": 1.0},
    "Batgirl": {"is_male": 0.0, "has_superpower": 0.0, "wears_mask": 1.0},
    "Nightwing": {"has_superpower": 0.0, "is_action_hero": 0.9, "wears_uniform": 1.0},
    "Catwoman": {"is_male": 0.0, "is_villain": 0.4, "wears_uniform": 1.0, "is_action_hero": 0.7},
    "Harley Quinn": {"is_male": 0.0, "is_villain": 0.7, "is_comedic": 0.6, "distinctive_hair": 1.0},
    "Poison Ivy": {"is_male": 0.0, "is_villain": 0.8, "has_superpower": 1.0, "distinctive_hair": 1.0},
    "Joker": {"is_villain": 1.0, "is_comedic": 0.7, "is_dark_brooding": 0.6, "has_distinctive_voice": 0.8},
    "Lex Luthor": {"is_villain": 1.0, "is_wealthy": 1.0, "billionaire": 1.0, "is_bald": 1.0, "has_superpower": 0.0},
    "Darkseid": {"is_villain": 1.0, "is_human": 0.0, "has_superpower": 1.0, "from_scifi_genre": 0.8},
    "Bane": {"is_villain": 1.0, "wears_mask": 1.0, "known_for_physique": 1.0, "has_superpower": 0.5},
    "Riddler": {"is_villain": 1.0, "has_glasses": 0.6, "is_comedic": 0.4, "has_superpower": 0.0},
    "Two-Face": {"is_villain": 1.0, "has_superpower": 0.0, "is_dark_brooding": 0.8},
    "Penguin": {"is_villain": 1.0, "is_wealthy": 0.7, "known_for_physique": 0.5, "has_superpower": 0.0},
    "Scarecrow": {"is_villain": 1.0, "from_horror_genre": 0.8, "has_superpower": 0.3},
    "Deathstroke": {"is_villain": 0.8, "wears_mask": 1.0, "is_action_hero": 0.9, "has_superpower": 0.3},
    "doomsday": {"is_villain": 1.0, "is_human": 0.0, "has_superpower": 1.0, "known_for_physique": 1.0},

    # Star Wars
    "Luke Skywalker": {"has_superpower": 0.7, "is_action_hero": 0.9, "is_leader": 0.6},
    "Darth Vader": {"is_villain": 0.7, "wears_mask": 1.0, "has_armor": 1.0, "is_dark_brooding": 1.0},
    "Han Solo": {"has_superpower": 0.0, "is_action_hero": 1.0, "is_comedic": 0.4},
    "Princess Leia": {"is_male": 0.0, "is_leader": 0.8, "is_wealthy": 0.8},
    "Yoda": {"is_human": 0.0, "era_ancient": 0.9, "is_leader": 0.9, "has_superpower": 0.9},
    "Obi-Wan Kenobi": {"has_facial_hair": 1.0, "has_superpower": 0.7, "is_leader": 0.5},
    "Emperor Palpatine": {"is_villain": 1.0, "is_leader": 1.0, "has_superpower": 0.9, "is_dark_brooding": 1.0},
    "Boba Fett": {"wears_mask": 1.0, "has_armor": 1.0, "is_villain": 0.5, "is_action_hero": 0.8},
    "Chewbacca": {"is_human": 0.0, "distinctive_hair": 1.0, "has_superpower": 0.0},
    "R2-D2": {"is_human": 0.0, "from_scifi_genre": 1.0, "is_comedic": 0.5},
    "Kylo Ren": {"is_villain": 0.6, "wears_mask": 0.7, "is_dark_brooding": 0.9, "has_superpower": 0.7},
    "Rey": {"is_male": 0.0, "has_superpower": 0.8, "is_action_hero": 0.9},

    # Harry Potter
    "Harry Potter": {"has_superpower": 0.8, "wears_mask": 0.0, "has_glasses": 1.0, "distinctive_hair": 0.6},
    "Hermione Granger": {"is_male": 0.0, "has_superpower": 0.8, "from_book": 0.9},
    "Ron Weasley": {"has_superpower": 0.7, "distinctive_hair": 1.0, "is_comedic": 0.5},
    "Albus Dumbledore": {"has_superpower": 1.0, "is_leader": 1.0, "has_facial_hair": 1.0, "has_glasses": 0.8},
    "Severus Snape": {"has_superpower": 0.8, "is_dark_brooding": 1.0, "distinctive_hair": 0.8},
    "Lord Voldemort": {"is_villain": 1.0, "has_superpower": 1.0, "is_bald": 1.0, "is_dark_brooding": 1.0},
    "Draco Malfoy": {"is_villain": 0.5, "distinctive_hair": 0.8, "is_wealthy": 0.8},
    "Hagrid": {"known_for_physique": 1.0, "has_facial_hair": 1.0, "is_comedic": 0.4},
    "Sirius Black": {"has_superpower": 0.7, "is_dark_brooding": 0.6, "distinctive_hair": 0.7},
    "Dobby": {"is_human": 0.0, "has_superpower": 0.5, "is_comedic": 0.5},

    # LOTR
    "Frodo Baggins": {"is_human": 0.5, "is_action_hero": 0.3, "is_leader": 0.4},
    "Gandalf": {"has_superpower": 1.0, "has_facial_hair": 1.0, "is_leader": 0.7, "era_medieval": 0.8},
    "Aragorn": {"is_action_hero": 1.0, "is_leader": 1.0, "has_facial_hair": 0.8},
    "Legolas": {"is_human": 0.0, "is_action_hero": 0.9, "distinctive_hair": 1.0},
    "Gimli": {"is_human": 0.0, "has_facial_hair": 1.0, "is_comedic": 0.5, "known_for_physique": 0.3},
    "Gollum": {"is_human": 0.3, "is_villain": 0.6, "is_dark_brooding": 0.8, "is_bald": 1.0},
    "Sauron": {"is_villain": 1.0, "is_human": 0.0, "is_leader": 1.0, "is_dark_brooding": 1.0},
    "Saruman": {"is_villain": 1.0, "has_superpower": 0.9, "has_facial_hair": 1.0, "is_leader": 0.7},
    "Bilbo Baggins": {"is_human": 0.5, "is_comedic": 0.4, "is_wealthy": 0.5},
    "Samwise Gamgee": {"is_human": 0.5, "is_comedic": 0.3, "is_action_hero": 0.2},

    # Other movies
    "James Bond": {"is_action_hero": 1.0, "is_wealthy": 0.6, "from_uk": 1.0, "wears_uniform": 0.3},
    "Indiana Jones": {"is_action_hero": 1.0, "from_usa": 1.0, "from_history": 0.5},
    "Forrest Gump": {"is_comedic": 0.5, "from_usa": 1.0, "from_sport": 0.4, "is_action_hero": 0.0},
    "The Terminator": {"is_human": 0.0, "from_scifi_genre": 1.0, "is_action_hero": 1.0, "is_villain": 0.5},
    "John Wick": {"is_action_hero": 1.0, "is_dark_brooding": 0.8, "has_facial_hair": 0.6},
    "Jack Sparrow": {"is_comedic": 0.8, "has_facial_hair": 1.0, "from_action_genre": 0.7, "distinctive_hair": 1.0},
    "Neo": {"has_superpower": 0.8, "from_scifi_genre": 1.0, "wears_uniform": 0.7, "is_dark_brooding": 0.5},
    "Jason Bourne": {"is_action_hero": 1.0, "is_dark_brooding": 0.6, "has_superpower": 0.0},
    "Ethan Hunt": {"is_action_hero": 1.0, "from_scifi_genre": 0.4, "wears_mask": 0.5},
    "Rocky Balboa": {"from_sport": 1.0, "is_action_hero": 0.8, "from_usa": 1.0, "known_for_physique": 0.9},

    # Anime
    "Goku": {"has_superpower": 1.0, "distinctive_hair": 1.0, "is_action_hero": 1.0, "is_comedic": 0.3},
    "Vegeta": {"has_superpower": 1.0, "distinctive_hair": 1.0, "is_villain": 0.3, "is_dark_brooding": 0.6},
    "Naruto": {"has_superpower": 1.0, "distinctive_hair": 0.9, "wears_uniform": 0.8, "is_comedic": 0.4},
    "Sasuke": {"has_superpower": 1.0, "is_dark_brooding": 0.9, "is_villain": 0.4},
    "Luffy": {"has_superpower": 1.0, "is_leader": 0.7, "is_comedic": 0.6, "distinctive_hair": 0.7},
    "Ichigo Kurosaki": {"has_superpower": 1.0, "distinctive_hair": 1.0, "is_dark_brooding": 0.4},
    "Light Yagami": {"has_superpower": 0.6, "is_villain": 0.7, "is_dark_brooding": 0.8},
    "L": {"has_superpower": 0.0, "is_dark_brooding": 0.6, "is_comedic": 0.3, "distinctive_hair": 0.8},
    "Saitama": {"is_bald": 1.0, "has_superpower": 1.0, "is_comedic": 0.7, "wears_uniform": 0.8},
    "Genos": {"is_human": 0.3, "has_superpower": 0.9, "distinctive_hair": 0.8, "is_action_hero": 0.9},
    "Eren Yeager": {"has_superpower": 0.9, "is_dark_brooding": 0.7, "is_villain": 0.4},
    "Mikasa Ackerman": {"is_male": 0.0, "is_action_hero": 1.0, "is_dark_brooding": 0.5},
    "Levi Ackerman": {"is_action_hero": 1.0, "is_dark_brooding": 0.6, "is_leader": 0.6},
    "Tanjiro Kamado": {"has_superpower": 0.7, "distinctive_hair": 0.6, "from_action_genre": 1.0},
    "Nezuko Kamado": {"is_male": 0.0, "has_superpower": 0.7, "is_human": 0.4},
    "Deku": {"has_superpower": 1.0, "is_comedic": 0.3, "distinctive_hair": 0.7},
    "All Might": {"has_superpower": 1.0, "known_for_physique": 1.0, "is_leader": 0.8, "distinctive_hair": 0.9},
    "Bakugo": {"has_superpower": 1.0, "is_dark_brooding": 0.6, "distinctive_hair": 0.9},
    "Todoroki": {"has_superpower": 1.0, "distinctive_hair": 1.0, "is_dark_brooding": 0.5},
    "Gojo Satoru": {"has_superpower": 1.0, "distinctive_hair": 0.8, "is_comedic": 0.4, "wears_mask": 0.5},
    "Pikachu": {"is_human": 0.0, "has_superpower": 0.8, "is_child_friendly": 1.0, "is_comedic": 0.5},
    "Ash Ketchum": {"is_human": 1.0, "is_adult": 0.3, "is_leader": 0.5},
    "Sailor Moon": {"is_male": 0.0, "has_superpower": 1.0, "wears_uniform": 1.0, "distinctive_hair": 1.0},
    "Edward Elric": {"has_superpower": 0.8, "is_adult": 0.4, "distinctive_hair": 0.8, "has_armor": 0.3},
    "Spike Spiegel": {"is_action_hero": 0.9, "is_dark_brooding": 0.6, "has_facial_hair": 0.0, "from_scifi_genre": 0.8},
    "Lelouch": {"has_superpower": 0.7, "is_leader": 0.9, "is_dark_brooding": 0.7, "is_villain": 0.4},
    "Kirito": {"is_action_hero": 0.9, "from_game": 0.8, "is_dark_brooding": 0.4},
    "Rem": {"is_male": 0.0, "is_human": 0.3, "distinctive_hair": 1.0},
    "Zero Two": {"is_male": 0.0, "is_human": 0.5, "distinctive_hair": 1.0, "from_scifi_genre": 0.8},
    "Itachi Uchiha": {"is_villain": 0.6, "has_superpower": 1.0, "is_dark_brooding": 0.9},

    # Games
    "Mario": {"is_human": 1.0, "has_facial_hair": 1.0, "is_comedic": 0.5, "wears_uniform": 0.7},
    "Luigi": {"is_human": 1.0, "has_facial_hair": 1.0, "is_comedic": 0.6, "is_dark_brooding": 0.2},
    "Princess Peach": {"is_male": 0.0, "is_wealthy": 1.0, "is_leader": 0.7, "distinctive_hair": 0.7},
    "Bowser": {"is_human": 0.0, "is_villain": 1.0, "has_superpower": 0.6, "known_for_physique": 0.8},
    "Yoshi": {"is_human": 0.0, "is_comedic": 0.6, "is_child_friendly": 1.0},
    "Link": {"is_human": 1.0, "is_action_hero": 1.0, "wears_uniform": 0.8, "distinctive_hair": 0.7},
    "Zelda": {"is_male": 0.0, "has_superpower": 0.6, "is_wealthy": 1.0, "is_leader": 0.8},
    "Ganondorf": {"is_villain": 1.0, "has_superpower": 0.9, "is_dark_brooding": 0.9},
    "Kirby": {"is_human": 0.0, "has_superpower": 0.9, "is_child_friendly": 1.0, "is_comedic": 0.5},
    "Sonic": {"is_human": 0.0, "has_superpower": 0.8, "is_comedic": 0.5, "distinctive_hair": 0.9},
    "Crash Bandicoot": {"is_human": 0.0, "is_comedic": 0.7, "is_action_hero": 0.6},
    "Spyro": {"is_human": 0.0, "has_superpower": 0.7, "is_child_friendly": 0.8},
    "Lara Croft": {"is_male": 0.0, "is_action_hero": 1.0, "is_wealthy": 0.7, "from_uk": 1.0},
    "Nathan Drake": {"is_action_hero": 1.0, "is_comedic": 0.4, "from_usa": 1.0},
    "Kratos": {"has_superpower": 0.9, "is_action_hero": 1.0, "is_bald": 1.0, "is_dark_brooding": 0.9},
    "Master Chief": {"wears_mask": 1.0, "has_armor": 1.0, "from_scifi_genre": 1.0, "is_action_hero": 1.0},
    "Solid Snake": {"is_action_hero": 1.0, "has_facial_hair": 0.8, "wears_uniform": 0.6, "is_dark_brooding": 0.6},
    "Geralt of Rivia": {"is_action_hero": 1.0, "distinctive_hair": 1.0, "has_facial_hair": 0.7, "has_superpower": 0.5},
    "Cloud Strife": {"is_action_hero": 1.0, "distinctive_hair": 1.0, "is_dark_brooding": 0.5, "has_superpower": 0.3},
    "Sephiroth": {"is_villain": 1.0, "distinctive_hair": 1.0, "has_superpower": 0.8, "is_dark_brooding": 1.0},
    "Pac-Man": {"is_human": 0.0, "born_before_1950": 0.0, "born_1970_1990": 1.0, "is_child_friendly": 1.0},
    "Mega Man": {"is_human": 0.3, "has_armor": 0.8, "is_action_hero": 0.9, "is_child_friendly": 0.8},
    "Ryu": {"is_human": 1.0, "from_sport": 0.8, "is_action_hero": 1.0, "from_japan": 1.0},
    "Scorpion": {"is_human": 0.5, "wears_mask": 1.0, "is_action_hero": 1.0, "has_superpower": 0.7},
    "Sub-Zero": {"is_human": 0.5, "wears_mask": 1.0, "is_action_hero": 1.0, "has_superpower": 0.8},
    "Steve": {"is_human": 1.0, "is_comedic": 0.3, "is_child_friendly": 1.0, "born_after_1990": 1.0},
    "Creeper": {"is_human": 0.0, "is_villain": 0.7, "is_child_friendly": 0.6, "born_after_1990": 1.0},
    "Charizard": {"is_human": 0.0, "has_superpower": 0.9, "is_action_hero": 0.5},
    "Mewtwo": {"is_human": 0.0, "has_superpower": 1.0, "is_villain": 0.4, "is_dark_brooding": 0.6},
}


def main():
    db_path = Path(__file__).parent.parent / "data" / "collected.db"

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Get attribute IDs
    attr_map = {}
    for row in conn.execute("SELECT id, key FROM attributes"):
        attr_map[row["key"]] = row["id"]

    # Get all entities
    entities = conn.execute("SELECT id, name FROM entities").fetchall()

    updated = 0
    for entity in entities:
        name = entity["name"]
        eid = entity["id"]

        if name not in CHARACTER_RULES:
            continue

        rules = CHARACTER_RULES[name]

        for attr_key, value in rules.items():
            if attr_key not in attr_map:
                continue

            attr_id = attr_map[attr_key]
            conn.execute("""
                INSERT INTO entity_attributes (entity_id, attribute_id, value)
                VALUES (?, ?, ?)
                ON CONFLICT(entity_id, attribute_id) DO UPDATE SET value = ?
            """, (eid, attr_id, value, value))

        updated += 1

    conn.commit()
    conn.close()

    print(f"Updated {updated} fictional characters with specific attributes.")


if __name__ == "__main__":
    main()
