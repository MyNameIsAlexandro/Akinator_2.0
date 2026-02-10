#!/usr/bin/env python3
"""Fix attributes for historical figures and real people with collisions."""

import sqlite3
from pathlib import Path

# Person-specific overrides
PERSON_RULES = {
    # Classical composers - differentiate by era, nationality, style
    "Mozart": {"era_modern": 1.0, "born_before_1950": 1.0, "from_europe": 1.0, "died_young": 1.0, "is_child_friendly": 0.7},
    "Beethoven": {"era_modern": 1.0, "born_before_1950": 1.0, "from_europe": 1.0, "is_dark_brooding": 0.7, "has_glasses": 0.0},
    "Bach": {"era_modern": 1.0, "born_before_1950": 1.0, "from_europe": 1.0, "has_facial_hair": 0.0, "cultural_icon": 0.8},
    "Chopin": {"era_modern": 1.0, "from_europe": 1.0, "is_dark_brooding": 0.5, "died_young": 0.8},
    "Tchaikovsky": {"from_russia": 1.0, "era_20th_century": 0.3, "is_dark_brooding": 0.6, "has_facial_hair": 1.0},
    "Vivaldi": {"era_modern": 1.0, "from_europe": 1.0, "distinctive_hair": 1.0, "from_italy": 1.0},
    "Handel": {"era_modern": 1.0, "from_europe": 1.0, "from_uk": 0.8, "known_for_physique": 0.4},
    "Brahms": {"from_europe": 1.0, "era_20th_century": 0.2, "has_facial_hair": 1.0, "is_dark_brooding": 0.5},
    "Schubert": {"era_modern": 1.0, "from_europe": 1.0, "has_glasses": 1.0, "died_young": 1.0},
    "Liszt": {"era_modern": 1.0, "from_europe": 1.0, "distinctive_hair": 1.0, "controversial": 0.4},
    "Wagner": {"era_20th_century": 0.1, "from_europe": 1.0, "is_dark_brooding": 0.8, "controversial": 0.9},
    "Verdi": {"from_europe": 1.0, "has_facial_hair": 0.8, "cultural_icon": 0.8},
    "Debussy": {"era_20th_century": 0.7, "from_europe": 1.0, "has_facial_hair": 0.8, "is_dark_brooding": 0.3},
    "Rachmaninoff": {"era_20th_century": 1.0, "from_russia": 1.0, "known_for_physique": 0.6, "is_dark_brooding": 0.6},
    "Stravinsky": {"era_20th_century": 1.0, "from_russia": 1.0, "controversial": 0.7, "has_glasses": 1.0},

    # Jazz musicians
    "Louis Armstrong": {"from_usa": 1.0, "era_20th_century": 1.0, "born_before_1950": 1.0, "is_comedic": 0.5, "has_distinctive_voice": 1.0},
    "Miles Davis": {"from_usa": 1.0, "era_20th_century": 1.0, "is_dark_brooding": 0.7, "cultural_icon": 0.9},
    "John Coltrane": {"from_usa": 1.0, "era_20th_century": 1.0, "is_dark_brooding": 0.5, "died_young": 0.7},
    "Duke Ellington": {"from_usa": 1.0, "era_20th_century": 1.0, "is_leader": 0.8, "cultural_icon": 0.8},
    "Charlie Parker": {"from_usa": 1.0, "era_20th_century": 1.0, "died_young": 1.0, "controversial": 0.5},
    "Ella Fitzgerald": {"is_male": 0.0, "from_usa": 1.0, "era_20th_century": 1.0, "cultural_icon": 0.8},
    "Billie Holiday": {"is_male": 0.0, "from_usa": 1.0, "died_young": 0.8, "is_dark_brooding": 0.7},
    "Nat King Cole": {"from_usa": 1.0, "era_20th_century": 1.0, "has_distinctive_voice": 0.9},
    "Frank Sinatra": {"from_usa": 1.0, "era_20th_century": 1.0, "cultural_icon": 1.0, "is_wealthy": 0.8, "controversial": 0.4},
    "Tony Bennett": {"from_usa": 1.0, "active_now": 0.3, "cultural_icon": 0.7},

    # Ancient rulers and conquerors
    "Napoleon Bonaparte": {"from_europe": 1.0, "era_modern": 1.0, "is_leader": 1.0, "world_champion": 0.7, "known_for_physique": 0.3},
    "Julius Caesar": {"era_ancient": 1.0, "from_europe": 1.0, "is_leader": 1.0, "is_bald": 0.7, "controversial": 0.6},
    "Alexander the Great": {"era_ancient": 1.0, "from_europe": 1.0, "world_champion": 1.0, "died_young": 1.0},
    "Cleopatra": {"is_male": 0.0, "era_ancient": 1.0, "from_africa": 1.0, "is_wealthy": 1.0, "cultural_icon": 0.9},
    "Augustus": {"era_ancient": 1.0, "from_europe": 1.0, "is_leader": 1.0, "cultural_icon": 0.6},
    "Genghis Khan": {"from_asia": 1.0, "era_medieval": 1.0, "world_champion": 1.0, "is_villain": 0.5, "is_leader": 1.0},
    "Charlemagne": {"from_europe": 1.0, "era_medieval": 1.0, "is_leader": 1.0, "has_facial_hair": 1.0},
    "Queen Victoria": {"is_male": 0.0, "from_uk": 1.0, "era_modern": 1.0, "is_leader": 1.0, "cultural_icon": 0.9},
    "Elizabeth I": {"is_male": 0.0, "from_uk": 1.0, "era_modern": 1.0, "is_leader": 1.0, "distinctive_hair": 0.8},
    "Henry VIII": {"from_uk": 1.0, "era_modern": 1.0, "is_leader": 1.0, "known_for_physique": 0.6, "controversial": 0.9},
    "Louis XIV": {"from_europe": 1.0, "era_modern": 1.0, "is_wealthy": 1.0, "distinctive_hair": 1.0, "is_leader": 1.0},
    "Catherine the Great": {"is_male": 0.0, "from_russia": 1.0, "era_modern": 1.0, "is_leader": 1.0, "controversial": 0.5},
    "Peter the Great": {"from_russia": 1.0, "era_modern": 1.0, "is_leader": 1.0, "known_for_physique": 0.8},

    # Ancient philosophers
    "Aristotle": {"era_ancient": 1.0, "from_europe": 1.0, "from_science": 1.0, "has_facial_hair": 1.0, "cultural_icon": 1.0},
    "Plato": {"era_ancient": 1.0, "from_europe": 1.0, "from_science": 0.7, "has_facial_hair": 1.0},
    "Socrates": {"era_ancient": 1.0, "from_europe": 1.0, "is_bald": 0.8, "has_facial_hair": 1.0, "controversial": 0.6},
    "Confucius": {"from_china": 1.0, "from_asia": 1.0, "era_ancient": 1.0, "has_facial_hair": 1.0, "is_leader": 0.5},
    "Buddha": {"from_india": 1.0, "from_asia": 1.0, "era_ancient": 1.0, "is_bald": 0.8, "cultural_icon": 1.0},
    "Archimedes": {"era_ancient": 1.0, "from_europe": 1.0, "from_science": 1.0, "died_young": 0.0},
    "Copernicus": {"era_modern": 1.0, "from_europe": 1.0, "from_science": 1.0, "controversial": 0.6},

    # Modern philosophers
    "Nietzsche": {"from_europe": 1.0, "era_20th_century": 0.3, "is_dark_brooding": 0.9, "controversial": 0.9, "has_facial_hair": 1.0},
    "Kant": {"from_europe": 1.0, "era_modern": 1.0, "from_science": 0.7, "is_dark_brooding": 0.3},
    "Descartes": {"from_europe": 1.0, "era_modern": 1.0, "from_science": 1.0, "has_facial_hair": 0.5},
    "Freud": {"from_europe": 1.0, "era_20th_century": 1.0, "controversial": 0.7, "has_facial_hair": 1.0, "has_glasses": 0.8},
    "Jung": {"from_europe": 1.0, "era_20th_century": 1.0, "has_glasses": 1.0, "is_dark_brooding": 0.4},

    # Famous scientists
    "Albert Einstein": {"from_europe": 1.0, "from_usa": 0.7, "era_20th_century": 1.0, "distinctive_hair": 1.0, "won_nobel": 1.0, "cultural_icon": 1.0},
    "Isaac Newton": {"from_uk": 1.0, "era_modern": 1.0, "distinctive_hair": 0.8, "is_dark_brooding": 0.5},
    "Stephen Hawking": {"from_uk": 1.0, "era_21st_century": 1.0, "has_glasses": 1.0, "has_distinctive_voice": 1.0, "cultural_icon": 0.9},
    "Marie Curie": {"is_male": 0.0, "from_europe": 1.0, "era_20th_century": 1.0, "won_nobel": 1.0, "died_young": 0.0},
    "Nikola Tesla": {"from_europe": 1.0, "from_usa": 0.6, "era_20th_century": 1.0, "controversial": 0.5, "is_dark_brooding": 0.4},
    "Charles Darwin": {"from_uk": 1.0, "era_modern": 1.0, "has_facial_hair": 1.0, "controversial": 0.6},
    "Galileo Galilei": {"from_europe": 1.0, "era_modern": 1.0, "controversial": 0.8, "has_facial_hair": 1.0},
    "Leonardo da Vinci": {"from_europe": 1.0, "era_modern": 1.0, "from_art": 1.0, "cultural_icon": 1.0, "has_facial_hair": 1.0},
    "Johannes Kepler": {"from_europe": 1.0, "era_modern": 1.0, "has_glasses": 0.5, "from_science": 1.0},
    "Michael Faraday": {"from_uk": 1.0, "era_modern": 1.0, "from_science": 1.0},
    "James Clerk Maxwell": {"from_uk": 1.0, "era_modern": 1.0, "has_facial_hair": 1.0, "from_science": 1.0},
    "Richard Feynman": {"from_usa": 1.0, "era_20th_century": 1.0, "is_comedic": 0.5, "won_nobel": 1.0},
    "Niels Bohr": {"from_europe": 1.0, "era_20th_century": 1.0, "won_nobel": 1.0},
    "Werner Heisenberg": {"from_europe": 1.0, "era_20th_century": 1.0, "controversial": 0.4, "won_nobel": 1.0},
    "Erwin Schrödinger": {"from_europe": 1.0, "era_20th_century": 1.0, "has_glasses": 1.0, "won_nobel": 1.0},
    "Max Planck": {"from_europe": 1.0, "era_20th_century": 1.0, "has_facial_hair": 0.7, "won_nobel": 1.0},
    "Thomas Edison": {"from_usa": 1.0, "era_20th_century": 0.5, "is_wealthy": 0.7, "controversial": 0.4},
    "Benjamin Franklin": {"from_usa": 1.0, "era_modern": 1.0, "is_bald": 0.7, "has_glasses": 1.0, "is_leader": 0.5},
    "Alexander Graham Bell": {"from_uk": 0.5, "from_usa": 0.7, "era_20th_century": 0.3, "has_facial_hair": 1.0},
    "Alan Turing": {"from_uk": 1.0, "era_20th_century": 1.0, "died_young": 0.8, "controversial": 0.4},
    "Tim Berners-Lee": {"from_uk": 1.0, "era_21st_century": 1.0, "from_internet": 0.9, "active_now": 1.0},
    "Carl Sagan": {"from_usa": 1.0, "era_20th_century": 1.0, "from_tv_series": 0.7, "has_distinctive_voice": 0.7},
    "Neil deGrasse Tyson": {"from_usa": 1.0, "era_21st_century": 1.0, "from_tv_series": 0.8, "active_now": 1.0, "has_facial_hair": 1.0},

    # Tech billionaires
    "Elon Musk": {"from_usa": 0.8, "from_africa": 0.3, "era_21st_century": 1.0, "billionaire": 1.0, "controversial": 0.8, "active_now": 1.0},
    "Bill Gates": {"from_usa": 1.0, "era_21st_century": 1.0, "billionaire": 1.0, "has_glasses": 1.0, "cultural_icon": 0.7},
    "Steve Jobs": {"from_usa": 1.0, "era_21st_century": 1.0, "billionaire": 1.0, "is_bald": 0.5, "cultural_icon": 1.0, "died_young": 0.0},
    "Mark Zuckerberg": {"from_usa": 1.0, "era_21st_century": 1.0, "billionaire": 1.0, "born_after_1990": 0.0, "born_1970_1990": 1.0, "controversial": 0.6},
    "Jeff Bezos": {"from_usa": 1.0, "era_21st_century": 1.0, "billionaire": 1.0, "is_bald": 1.0, "known_for_physique": 0.5},
    "Larry Page": {"from_usa": 1.0, "era_21st_century": 1.0, "billionaire": 1.0, "has_glasses": 0.0},
    "Sergey Brin": {"from_usa": 1.0, "from_russia": 0.5, "era_21st_century": 1.0, "billionaire": 1.0},
    "Jack Ma": {"from_china": 1.0, "from_asia": 1.0, "era_21st_century": 1.0, "billionaire": 1.0, "controversial": 0.4},

    # Writers
    "William Shakespeare": {"from_uk": 1.0, "era_modern": 1.0, "cultural_icon": 1.0, "has_facial_hair": 0.5, "is_bald": 0.6},
    "Charles Dickens": {"from_uk": 1.0, "era_modern": 1.0, "has_facial_hair": 1.0, "is_dark_brooding": 0.4},
    "Mark Twain": {"from_usa": 1.0, "era_20th_century": 0.2, "has_facial_hair": 1.0, "is_comedic": 0.6, "distinctive_hair": 1.0},
    "Ernest Hemingway": {"from_usa": 1.0, "era_20th_century": 1.0, "has_facial_hair": 1.0, "is_dark_brooding": 0.6, "won_nobel": 1.0},
    "F. Scott Fitzgerald": {"from_usa": 1.0, "era_20th_century": 1.0, "died_young": 0.7, "is_wealthy": 0.3},
    "Jane Austen": {"is_male": 0.0, "from_uk": 1.0, "era_modern": 1.0, "is_dark_brooding": 0.0},
    "Oscar Wilde": {"from_uk": 0.7, "from_europe": 1.0, "era_modern": 1.0, "is_comedic": 0.7, "controversial": 0.8},
    "George Orwell": {"from_uk": 1.0, "era_20th_century": 1.0, "is_dark_brooding": 0.7, "from_politics": 0.5},
    "Aldous Huxley": {"from_uk": 1.0, "era_20th_century": 1.0, "from_scifi_genre": 0.6},
    "Virginia Woolf": {"is_male": 0.0, "from_uk": 1.0, "era_20th_century": 1.0, "is_dark_brooding": 0.7, "died_young": 0.0},
    "Leo Tolstoy": {"from_russia": 1.0, "era_modern": 1.0, "has_facial_hair": 1.0, "cultural_icon": 0.9},
    "Fyodor Dostoevsky": {"from_russia": 1.0, "era_modern": 1.0, "is_dark_brooding": 1.0, "has_facial_hair": 1.0},
    "Anton Chekhov": {"from_russia": 1.0, "era_20th_century": 0.3, "has_glasses": 1.0, "is_comedic": 0.4},
    "Victor Hugo": {"from_europe": 1.0, "era_modern": 1.0, "has_facial_hair": 1.0, "is_dark_brooding": 0.5},
    "Alexandre Dumas": {"from_europe": 1.0, "era_modern": 1.0, "from_action_genre": 0.6},
    "Stephen King": {"from_usa": 1.0, "era_21st_century": 1.0, "from_horror_genre": 1.0, "has_glasses": 1.0, "active_now": 1.0},
    "JK Rowling": {"is_male": 0.0, "from_uk": 1.0, "era_21st_century": 1.0, "billionaire": 0.8, "controversial": 0.6},
    "George RR Martin": {"from_usa": 1.0, "era_21st_century": 1.0, "has_facial_hair": 1.0, "from_tv_series": 0.8},
    "Dan Brown": {"from_usa": 1.0, "era_21st_century": 1.0, "from_movie": 0.6},
    "Agatha Christie": {"is_male": 0.0, "from_uk": 1.0, "era_20th_century": 1.0, "cultural_icon": 0.8},
    "Arthur Conan Doyle": {"from_uk": 1.0, "era_20th_century": 0.5, "has_facial_hair": 1.0},
    "Edgar Allan Poe": {"from_usa": 1.0, "era_modern": 1.0, "is_dark_brooding": 1.0, "from_horror_genre": 0.7, "died_young": 0.8},
    "HP Lovecraft": {"from_usa": 1.0, "era_20th_century": 1.0, "from_horror_genre": 1.0, "is_dark_brooding": 1.0, "controversial": 0.5},
    "Isaac Asimov": {"from_usa": 1.0, "era_20th_century": 1.0, "from_scifi_genre": 1.0, "has_glasses": 0.6},
    "Philip K Dick": {"from_usa": 1.0, "era_20th_century": 1.0, "from_scifi_genre": 1.0, "is_dark_brooding": 0.6, "has_facial_hair": 1.0},
    "Haruki Murakami": {"from_japan": 1.0, "from_asia": 1.0, "era_21st_century": 1.0, "active_now": 1.0},
    "Paulo Coelho": {"from_south_america": 1.0, "era_21st_century": 1.0, "active_now": 1.0},
    "Gabriel García Márquez": {"from_south_america": 1.0, "era_20th_century": 1.0, "won_nobel": 1.0, "has_facial_hair": 1.0},
    "Jorge Luis Borges": {"from_south_america": 1.0, "era_20th_century": 1.0, "has_glasses": 1.0},
    "Pablo Neruda": {"from_south_america": 1.0, "era_20th_century": 1.0, "won_nobel": 1.0, "from_politics": 0.4},
    "Homer": {"era_ancient": 1.0, "from_europe": 1.0, "is_bald": 0.5, "has_facial_hair": 1.0, "cultural_icon": 1.0},
    "Dante": {"from_europe": 1.0, "era_medieval": 1.0, "is_dark_brooding": 0.7, "cultural_icon": 0.9},
    "Miguel de Cervantes": {"from_europe": 1.0, "era_modern": 1.0, "is_comedic": 0.5, "has_facial_hair": 0.8},
    "Franz Kafka": {"from_europe": 1.0, "era_20th_century": 1.0, "is_dark_brooding": 1.0, "died_young": 0.7},
    "James Joyce": {"from_europe": 1.0, "era_20th_century": 1.0, "has_glasses": 1.0, "controversial": 0.4},

    # Athletes - differentiate by sport, era, nationality
    "Thierry Henry": {"from_europe": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "is_bald": 0.7},
    "Karim Benzema": {"from_europe": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "has_facial_hair": 0.8},
    "Gianluigi Buffon": {"from_europe": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "distinctive_hair": 0.3},
    "Robert Lewandowski": {"from_europe": 1.0, "born_1970_1990": 1.0, "active_now": 1.0},
    "Luka Modrić": {"from_europe": 1.0, "born_1970_1990": 1.0, "distinctive_hair": 0.7, "active_now": 1.0},
    "Luis Suárez": {"from_south_america": 1.0, "born_1970_1990": 1.0, "controversial": 0.8},
    "Sergio Ramos": {"from_europe": 1.0, "born_1970_1990": 1.0, "has_tattoos": 1.0, "controversial": 0.5},
    "Manuel Neuer": {"from_europe": 1.0, "born_1970_1990": 1.0, "known_for_physique": 0.6},
    "Iker Casillas": {"from_europe": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0},
    "Pele": {"from_south_america": 1.0, "born_before_1950": 1.0, "cultural_icon": 1.0, "world_champion": 1.0},
    "Xavi": {"from_europe": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "is_bald": 0.6},
    "Kaka": {"from_south_america": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "distinctive_hair": 0.5},

    # Basketball
    "Larry Bird": {"from_usa": 1.0, "born_1950_1970": 1.0, "distinctive_hair": 0.7, "cultural_icon": 0.7},
    "Hakeem Olajuwon": {"from_africa": 1.0, "from_usa": 0.7, "born_1950_1970": 1.0, "world_champion": 1.0},
    "Charles Barkley": {"from_usa": 1.0, "born_1950_1970": 1.0, "is_comedic": 0.6, "controversial": 0.5},
    "Kevin Durant": {"from_usa": 1.0, "born_1970_1990": 1.0, "active_now": 1.0, "known_for_physique": 0.7},
    "Tim Duncan": {"from_usa": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "is_comedic": 0.0},
    "Allen Iverson": {"from_usa": 1.0, "born_1970_1990": 1.0, "has_tattoos": 1.0, "distinctive_hair": 0.8, "controversial": 0.5},
    "Dirk Nowitzki": {"from_europe": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "known_for_physique": 0.8},
    "Michael Phelps": {"from_usa": 1.0, "born_1970_1990": 1.0, "olympic_medalist": 1.0, "known_for_physique": 0.8},

    # Tennis and other sports
    "Roger Federer": {"from_europe": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "cultural_icon": 0.8, "is_wealthy": 0.9},
    "Rafael Nadal": {"from_europe": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "known_for_physique": 0.8, "distinctive_hair": 0.6},
    "Novak Djokovic": {"from_europe": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "controversial": 0.5, "active_now": 1.0},
    "Andy Murray": {"from_uk": 1.0, "born_1970_1990": 1.0, "world_champion": 0.8},
    "Pete Sampras": {"from_usa": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0},
    "Floyd Mayweather": {"from_usa": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "is_wealthy": 1.0, "controversial": 0.7},
    "Khabib Nurmagomedov": {"from_russia": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "has_facial_hair": 1.0},
    "Jon Jones": {"from_usa": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "controversial": 0.8},
    "Lewis Hamilton": {"from_uk": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "is_wealthy": 0.9, "has_tattoos": 0.7},
    "Valentino Rossi": {"from_europe": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "distinctive_hair": 0.6},
    "Tom Brady": {"from_usa": 1.0, "born_1970_1990": 1.0, "world_champion": 1.0, "is_wealthy": 0.9, "cultural_icon": 0.7},
    "Shaun White": {"from_usa": 1.0, "born_1970_1990": 1.0, "olympic_medalist": 1.0, "distinctive_hair": 1.0},

    # Modern politicians
    "Kim Jong Un": {"from_korea": 1.0, "from_asia": 1.0, "era_21st_century": 1.0, "is_leader": 1.0, "controversial": 0.9, "known_for_physique": 0.4},
    "Nelson Mandela": {"from_africa": 1.0, "era_21st_century": 1.0, "is_leader": 1.0, "cultural_icon": 1.0, "won_nobel": 1.0},
    "Fidel Castro": {"from_south_america": 0.7, "era_20th_century": 1.0, "is_leader": 1.0, "controversial": 0.9, "has_facial_hair": 1.0},
    "Deng Xiaoping": {"from_china": 1.0, "from_asia": 1.0, "era_20th_century": 1.0, "is_leader": 1.0},
    "Donald Trump": {"from_usa": 1.0, "era_21st_century": 1.0, "is_leader": 1.0, "billionaire": 1.0, "controversial": 1.0, "distinctive_hair": 1.0},
    "George W. Bush": {"from_usa": 1.0, "era_21st_century": 1.0, "is_leader": 1.0, "controversial": 0.6},
    "Joe Biden": {"from_usa": 1.0, "era_21st_century": 1.0, "is_leader": 1.0, "active_now": 1.0, "has_glasses": 0.5},
    "Bill Clinton": {"from_usa": 1.0, "era_21st_century": 1.0, "is_leader": 1.0, "controversial": 0.7, "has_distinctive_voice": 0.6},
    "George Washington": {"from_usa": 1.0, "era_modern": 1.0, "is_leader": 1.0, "cultural_icon": 1.0, "distinctive_hair": 0.8},
    "Mahatma Gandhi": {"from_india": 1.0, "from_asia": 1.0, "era_20th_century": 1.0, "is_bald": 1.0, "has_glasses": 1.0, "cultural_icon": 1.0},
    "Jawaharlal Nehru": {"from_india": 1.0, "from_asia": 1.0, "era_20th_century": 1.0, "is_leader": 1.0},
    "Mao Zedong": {"from_china": 1.0, "from_asia": 1.0, "era_20th_century": 1.0, "is_leader": 1.0, "controversial": 0.9},
    "Otto von Bismarck": {"from_europe": 1.0, "era_modern": 1.0, "is_leader": 1.0, "has_facial_hair": 1.0},

    # YouTubers
    "Dude Perfect": {"from_usa": 1.0, "from_sport": 0.7, "is_comedic": 0.6, "is_child_friendly": 0.9},
    "Smosh": {"from_usa": 1.0, "is_comedic": 1.0, "born_1970_1990": 1.0},
    "h3h3Productions": {"from_usa": 1.0, "is_comedic": 0.8, "controversial": 0.5, "has_facial_hair": 0.7},
    "Jacksepticeye": {"from_europe": 1.0, "from_game": 0.8, "is_comedic": 0.7, "has_distinctive_voice": 0.8},
    "xQc": {"from_usa": 0.3, "from_game": 1.0, "is_comedic": 0.5, "controversial": 0.6, "distinctive_hair": 0.6},

    # Actors with collisions
    "Ryan Gosling": {"from_usa": 0.7, "born_1970_1990": 1.0, "is_dark_brooding": 0.5, "from_drama_genre": 0.7},
    "Chris Hemsworth": {"from_usa": 0.3, "born_1970_1990": 1.0, "known_for_physique": 0.9, "from_action_genre": 0.9},
    "Oscar Isaac": {"from_usa": 0.7, "born_1970_1990": 1.0, "from_scifi_genre": 0.7, "has_facial_hair": 0.8},
    "Michael Fassbender": {"from_europe": 1.0, "born_1970_1990": 1.0, "from_action_genre": 0.6},
    "Samuel Lee Jackson": {"from_usa": 1.0, "born_1950_1970": 1.0, "is_bald": 1.0, "has_distinctive_voice": 0.9, "from_action_genre": 0.9},
    "Penelope Cruz": {"is_male": 0.0, "from_europe": 1.0, "born_1970_1990": 1.0, "won_oscar": 1.0},
    "Tom Cruise": {"from_usa": 1.0, "born_1950_1970": 1.0, "from_action_genre": 1.0, "is_wealthy": 1.0, "controversial": 0.6},
    "George Clooney": {"from_usa": 1.0, "born_1950_1970": 1.0, "from_drama_genre": 0.7, "is_wealthy": 0.9, "has_facial_hair": 0.6},
    "Christian Bale": {"from_uk": 1.0, "born_1970_1990": 1.0, "won_oscar": 1.0, "from_action_genre": 0.8, "is_dark_brooding": 0.6},
    "Benedict Cumberbatch": {"from_uk": 1.0, "born_1970_1990": 1.0, "from_scifi_genre": 0.6, "has_distinctive_voice": 0.8},
    "Edward Norton": {"from_usa": 1.0, "born_1970_1990": 1.0, "is_dark_brooding": 0.6, "controversial": 0.3},
    "Daniel Bruhl": {"from_europe": 1.0, "born_1970_1990": 1.0, "is_villain": 0.4},
    "Julia Roberts": {"is_male": 0.0, "from_usa": 1.0, "born_1950_1970": 1.0, "won_oscar": 1.0, "from_comedy_genre": 0.6},
    "Halle Berry": {"is_male": 0.0, "from_usa": 1.0, "born_1950_1970": 1.0, "won_oscar": 1.0, "from_action_genre": 0.5},
    "Sandra Bullock": {"is_male": 0.0, "from_usa": 1.0, "born_1950_1970": 1.0, "won_oscar": 1.0, "from_comedy_genre": 0.6},
    "Viola Davis": {"is_male": 0.0, "from_usa": 1.0, "born_1950_1970": 1.0, "won_oscar": 1.0, "from_drama_genre": 0.9},
    "Marlon Brando": {"from_usa": 1.0, "born_before_1950": 1.0, "won_oscar": 1.0, "cultural_icon": 1.0, "known_for_physique": 0.5},
    "Clark Gable": {"from_usa": 1.0, "born_before_1950": 1.0, "has_facial_hair": 1.0, "cultural_icon": 0.9},
    "Grace Kelly": {"is_male": 0.0, "from_usa": 1.0, "born_before_1950": 1.0, "is_wealthy": 1.0, "from_politics": 0.3},
    "Bette Davis": {"is_male": 0.0, "from_usa": 1.0, "born_before_1950": 1.0, "won_oscar": 1.0, "is_dark_brooding": 0.6},

    # Musicians with collisions
    "Ed Sheeran": {"from_uk": 1.0, "born_after_1990": 1.0, "has_glasses": 0.5, "distinctive_hair": 1.0, "active_now": 1.0},
    "Harry Styles": {"from_uk": 1.0, "born_after_1990": 1.0, "distinctive_hair": 0.8, "active_now": 1.0, "controversial": 0.3},
    "Keith Richards": {"from_uk": 1.0, "born_before_1950": 1.0, "has_tattoos": 0.6, "cultural_icon": 0.8},
    "Jimmy Page": {"from_uk": 1.0, "born_before_1950": 1.0, "distinctive_hair": 0.7, "cultural_icon": 0.7},
    "Eddie Vedder": {"from_usa": 1.0, "born_1950_1970": 1.0, "is_dark_brooding": 0.6, "distinctive_hair": 0.6},
    "James Hetfield": {"from_usa": 1.0, "born_1950_1970": 1.0, "has_facial_hair": 1.0, "is_dark_brooding": 0.7},
    "A$AP Rocky": {"from_usa": 1.0, "born_1970_1990": 1.0, "distinctive_hair": 0.8, "controversial": 0.5},
    "Future": {"from_usa": 1.0, "born_1970_1990": 1.0, "has_tattoos": 0.6, "controversial": 0.4},
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

        if name not in PERSON_RULES:
            continue

        rules = PERSON_RULES[name]

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

    print(f"Updated {updated} historical/real persons with specific attributes.")


if __name__ == "__main__":
    main()
