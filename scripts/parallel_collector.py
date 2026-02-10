#!/usr/bin/env python3
"""Parallel data collector - runs multiple collectors for different categories.

This script runs multiple collection workers in parallel, each focusing on
different entity categories for faster data collection.

Usage:
    python scripts/parallel_collector.py --workers 4 --db data/collected.db
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

sys.path.insert(0, str(Path(__file__).parent.parent))

from akinator.db.repository import Repository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger("parallel")

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "AkinatorParallelCollector/1.0"

shutdown_requested = False


def signal_handler(signum, frame):
    global shutdown_requested
    logger.info("Shutdown requested...")
    shutdown_requested = True


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# ═══════════════════════════════════════════════════════════════════════════════
# EXPANDED SEARCH SEEDS - Much larger lists for parallel collection
# ═══════════════════════════════════════════════════════════════════════════════

CATEGORY_SEEDS = {
    "actors": [
        # Hollywood A-list
        "Tom Hanks", "Leonardo DiCaprio", "Brad Pitt", "Johnny Depp", "Robert Downey Jr",
        "Will Smith", "Denzel Washington", "Morgan Freeman", "Samuel L Jackson", "Keanu Reeves",
        "Tom Cruise", "Harrison Ford", "Clint Eastwood", "Robert De Niro", "Al Pacino",
        "Jack Nicholson", "Anthony Hopkins", "Dustin Hoffman", "Gene Hackman", "Michael Caine",
        "Christian Bale", "Matt Damon", "Ben Affleck", "George Clooney", "Ryan Gosling",
        "Joaquin Phoenix", "Jake Gyllenhaal", "Edward Norton", "Mark Wahlberg", "Chris Hemsworth",
        "Chris Evans", "Chris Pratt", "Ryan Reynolds", "Dwayne Johnson", "Vin Diesel",
        "Jason Statham", "Liam Neeson", "Hugh Jackman", "Daniel Craig", "Benedict Cumberbatch",
        # Hollywood actresses
        "Scarlett Johansson", "Meryl Streep", "Julia Roberts", "Angelina Jolie", "Jennifer Lawrence",
        "Nicole Kidman", "Cate Blanchett", "Kate Winslet", "Natalie Portman", "Emma Stone",
        "Anne Hathaway", "Amy Adams", "Sandra Bullock", "Charlize Theron", "Margot Robbie",
        "Emma Watson", "Jennifer Aniston", "Reese Witherspoon", "Halle Berry", "Viola Davis",
        # International
        "Jackie Chan", "Bruce Lee", "Jet Li", "Tony Leung", "Gong Li", "Zhang Ziyi",
        "Shah Rukh Khan", "Amitabh Bachchan", "Aamir Khan", "Priyanka Chopra", "Deepika Padukone",
        "Antonio Banderas", "Penelope Cruz", "Javier Bardem", "Pedro Pascal", "Oscar Isaac",
        "Jean Reno", "Marion Cotillard", "Juliette Binoche", "Gerard Depardieu",
        "Mads Mikkelsen", "Christoph Waltz", "Daniel Bruhl", "Michael Fassbender",
        # Classic
        "Marilyn Monroe", "Audrey Hepburn", "James Dean", "Marlon Brando", "Humphrey Bogart",
        "Katharine Hepburn", "Elizabeth Taylor", "Clark Gable", "Cary Grant", "Gregory Peck",
        "Grace Kelly", "Ingrid Bergman", "Bette Davis", "Charlie Chaplin", "Buster Keaton",
    ],

    "musicians": [
        # Pop
        "Michael Jackson", "Madonna", "Beyonce", "Taylor Swift", "Lady Gaga",
        "Rihanna", "Justin Bieber", "Ariana Grande", "Selena Gomez", "Katy Perry",
        "Bruno Mars", "Ed Sheeran", "Adele", "Billie Eilish", "Dua Lipa",
        "Harry Styles", "The Weeknd", "Post Malone", "Shawn Mendes", "Doja Cat",
        "Justin Timberlake", "Christina Aguilera", "Shakira", "Jennifer Lopez", "Britney Spears",
        "Whitney Houston", "Mariah Carey", "Celine Dion", "Diana Ross", "Stevie Wonder",
        "Prince", "George Michael", "Elton John", "Phil Collins", "Lionel Richie",
        # Rock
        "Elvis Presley", "Freddie Mercury", "David Bowie", "John Lennon", "Paul McCartney",
        "Mick Jagger", "Keith Richards", "Ozzy Osbourne", "Robert Plant", "Jimmy Page",
        "Eric Clapton", "Jimi Hendrix", "Kurt Cobain", "Dave Grohl", "Eddie Vedder",
        "Chris Cornell", "Chester Bennington", "Bono", "Bruce Springsteen", "Axl Rose",
        "Jon Bon Jovi", "Steven Tyler", "James Hetfield", "Lars Ulrich", "Angus Young",
        # Hip Hop
        "Eminem", "Jay-Z", "Kanye West", "Drake", "Kendrick Lamar",
        "Snoop Dogg", "Dr Dre", "Ice Cube", "Tupac Shakur", "Notorious BIG",
        "Lil Wayne", "50 Cent", "Nas", "Nicki Minaj", "Cardi B",
        "Travis Scott", "J Cole", "Tyler the Creator", "A$AP Rocky", "Future",
        # Classical
        "Mozart", "Beethoven", "Bach", "Chopin", "Tchaikovsky",
        "Vivaldi", "Handel", "Brahms", "Schubert", "Liszt",
        "Wagner", "Verdi", "Debussy", "Rachmaninoff", "Stravinsky",
        # Jazz
        "Louis Armstrong", "Miles Davis", "John Coltrane", "Duke Ellington", "Charlie Parker",
        "Ella Fitzgerald", "Billie Holiday", "Nat King Cole", "Frank Sinatra", "Tony Bennett",
    ],

    "athletes": [
        # Football/Soccer
        "Lionel Messi", "Cristiano Ronaldo", "Neymar", "Kylian Mbappe", "Erling Haaland",
        "Diego Maradona", "Pele", "Zinedine Zidane", "Ronaldinho", "David Beckham",
        "Wayne Rooney", "Thierry Henry", "Robert Lewandowski", "Karim Benzema", "Luka Modric",
        "Sergio Ramos", "Gerard Pique", "Andres Iniesta", "Xavi", "Manuel Neuer",
        "Gianluigi Buffon", "Iker Casillas", "Kaka", "Zlatan Ibrahimovic", "Luis Suarez",
        # Basketball
        "Michael Jordan", "LeBron James", "Kobe Bryant", "Shaquille O'Neal", "Stephen Curry",
        "Kevin Durant", "Giannis Antetokounmpo", "Magic Johnson", "Larry Bird", "Kareem Abdul-Jabbar",
        "Tim Duncan", "Dirk Nowitzki", "Hakeem Olajuwon", "Charles Barkley", "Allen Iverson",
        # Tennis
        "Roger Federer", "Rafael Nadal", "Novak Djokovic", "Andy Murray", "Pete Sampras",
        "Andre Agassi", "Serena Williams", "Venus Williams", "Maria Sharapova", "Naomi Osaka",
        # Boxing/MMA
        "Muhammad Ali", "Mike Tyson", "Floyd Mayweather", "Manny Pacquiao", "Canelo Alvarez",
        "George Foreman", "Lennox Lewis", "Conor McGregor", "Khabib Nurmagomedov", "Jon Jones",
        # Olympics/Other
        "Usain Bolt", "Michael Phelps", "Simone Biles", "Carl Lewis", "Jesse Owens",
        "Tiger Woods", "Wayne Gretzky", "Tom Brady", "Babe Ruth", "Michael Schumacher",
        "Lewis Hamilton", "Ayrton Senna", "Valentino Rossi", "Tony Hawk", "Shaun White",
    ],

    "politicians": [
        # US
        "Barack Obama", "Donald Trump", "Joe Biden", "George Washington", "Abraham Lincoln",
        "Franklin Roosevelt", "John F Kennedy", "Ronald Reagan", "Bill Clinton", "George W Bush",
        "Thomas Jefferson", "Theodore Roosevelt", "Richard Nixon", "Jimmy Carter", "Lyndon Johnson",
        # World Leaders
        "Vladimir Putin", "Xi Jinping", "Angela Merkel", "Emmanuel Macron", "Boris Johnson",
        "Winston Churchill", "Margaret Thatcher", "Tony Blair", "Charles de Gaulle",
        "Nelson Mandela", "Mahatma Gandhi", "Jawaharlal Nehru", "Indira Gandhi", "Narendra Modi",
        "Fidel Castro", "Che Guevara", "Kim Jong Un", "Mao Zedong", "Deng Xiaoping",
        # Historical
        "Napoleon Bonaparte", "Julius Caesar", "Alexander the Great", "Cleopatra", "Augustus",
        "Genghis Khan", "Charlemagne", "Queen Victoria", "Elizabeth I", "Henry VIII",
        "Louis XIV", "Catherine the Great", "Peter the Great", "Stalin", "Hitler",
        "Mussolini", "Lenin", "Otto von Bismarck", "Queen Elizabeth II", "Princess Diana",
    ],

    "scientists": [
        "Albert Einstein", "Isaac Newton", "Stephen Hawking", "Marie Curie", "Nikola Tesla",
        "Charles Darwin", "Galileo Galilei", "Leonardo da Vinci", "Aristotle", "Plato",
        "Archimedes", "Copernicus", "Johannes Kepler", "Michael Faraday", "James Clerk Maxwell",
        "Richard Feynman", "Niels Bohr", "Werner Heisenberg", "Erwin Schrodinger", "Max Planck",
        "Thomas Edison", "Benjamin Franklin", "Alexander Graham Bell", "Alan Turing", "Tim Berners-Lee",
        "Carl Sagan", "Neil deGrasse Tyson", "Elon Musk", "Bill Gates", "Steve Jobs",
        "Mark Zuckerberg", "Jeff Bezos", "Larry Page", "Sergey Brin", "Jack Ma",
        "Socrates", "Confucius", "Buddha", "Nietzsche", "Kant", "Descartes", "Freud", "Jung",
    ],

    "writers": [
        "William Shakespeare", "Charles Dickens", "Mark Twain", "Ernest Hemingway", "F Scott Fitzgerald",
        "Jane Austen", "Oscar Wilde", "George Orwell", "Aldous Huxley", "Virginia Woolf",
        "Leo Tolstoy", "Fyodor Dostoevsky", "Anton Chekhov", "Victor Hugo", "Alexandre Dumas",
        "Stephen King", "JK Rowling", "George RR Martin", "Dan Brown", "Agatha Christie",
        "Arthur Conan Doyle", "Edgar Allan Poe", "HP Lovecraft", "Isaac Asimov", "Philip K Dick",
        "Haruki Murakami", "Paulo Coelho", "Gabriel Garcia Marquez", "Jorge Luis Borges", "Pablo Neruda",
        "Homer", "Dante", "Miguel de Cervantes", "Franz Kafka", "James Joyce",
    ],

    "fictional_superheroes": [
        # Marvel
        "Spider-Man", "Iron Man", "Captain America", "Thor", "Hulk",
        "Black Widow", "Hawkeye", "Black Panther", "Doctor Strange", "Scarlet Witch",
        "Ant-Man", "Captain Marvel", "Wolverine", "Deadpool", "Professor X",
        "Magneto", "Storm", "Cyclops", "Jean Grey", "Venom",
        "Thanos", "Loki", "Ultron", "Green Goblin", "Doctor Octopus",
        # DC
        "Batman", "Superman", "Wonder Woman", "Aquaman", "Flash",
        "Green Lantern", "Cyborg", "Shazam", "Martian Manhunter", "Robin",
        "Batgirl", "Nightwing", "Catwoman", "Harley Quinn", "Poison Ivy",
        "Joker", "Lex Luthor", "Darkseid", "Bane", "Riddler",
        "Two-Face", "Penguin", "Scarecrow", "Deathstroke", "Doomsday",
    ],

    "fictional_movies": [
        # Star Wars
        "Luke Skywalker", "Darth Vader", "Han Solo", "Princess Leia", "Yoda",
        "Obi-Wan Kenobi", "Emperor Palpatine", "Boba Fett", "Chewbacca", "R2-D2",
        "Kylo Ren", "Rey", "Baby Yoda", "Darth Maul", "Anakin Skywalker",
        # Harry Potter
        "Harry Potter", "Hermione Granger", "Ron Weasley", "Albus Dumbledore", "Severus Snape",
        "Lord Voldemort", "Draco Malfoy", "Hagrid", "Sirius Black", "Dobby",
        # LOTR
        "Frodo Baggins", "Gandalf", "Aragorn", "Legolas", "Gimli",
        "Gollum", "Sauron", "Saruman", "Bilbo Baggins", "Samwise Gamgee",
        # Other
        "James Bond", "Indiana Jones", "Forrest Gump", "The Terminator", "John Wick",
        "Jack Sparrow", "Neo", "Jason Bourne", "Ethan Hunt", "Rocky Balboa",
    ],

    "fictional_animation": [
        # Disney
        "Mickey Mouse", "Donald Duck", "Goofy", "Minnie Mouse", "Pluto",
        "Elsa", "Anna", "Simba", "Mufasa", "Nala",
        "Ariel", "Belle", "Jasmine", "Mulan", "Pocahontas",
        "Cinderella", "Snow White", "Rapunzel", "Moana", "Tiana",
        # Pixar
        "Woody", "Buzz Lightyear", "Nemo", "Dory", "Lightning McQueen",
        "Wall-E", "Sulley", "Mike Wazowski", "Remy", "Mr Incredible",
        # Other
        "Shrek", "Donkey", "SpongeBob", "Patrick Star", "Bugs Bunny",
        "Tom", "Jerry", "Scooby-Doo", "Homer Simpson", "Bart Simpson",
        "Peter Griffin", "Rick Sanchez", "Morty Smith", "Finn", "Jake",
    ],

    "fictional_anime": [
        "Goku", "Vegeta", "Naruto", "Sasuke", "Luffy",
        "Ichigo", "Light Yagami", "L", "Saitama", "Genos",
        "Eren Jaeger", "Mikasa Ackerman", "Levi Ackerman", "Tanjiro Kamado", "Nezuko",
        "Deku", "All Might", "Bakugo", "Todoroki", "Gojo Satoru",
        "Pikachu", "Ash Ketchum", "Sailor Moon", "Edward Elric", "Spike Spiegel",
        "Lelouch", "Kirito", "Rem", "Zero Two", "Itachi Uchiha",
    ],

    "fictional_games": [
        "Mario", "Luigi", "Princess Peach", "Bowser", "Yoshi",
        "Link", "Zelda", "Ganondorf", "Kirby", "Sonic",
        "Crash Bandicoot", "Spyro", "Lara Croft", "Nathan Drake", "Kratos",
        "Master Chief", "Solid Snake", "Geralt of Rivia", "Cloud Strife", "Sephiroth",
        "Pac-Man", "Mega Man", "Ryu", "Scorpion", "Sub-Zero",
        "Steve", "Creeper", "Pikachu", "Charizard", "Mewtwo",
    ],

    "youtubers": [
        "PewDiePie", "MrBeast", "Markiplier", "Jacksepticeye", "Ninja",
        "Pokimane", "xQc", "KSI", "Logan Paul", "Jake Paul",
        "Dude Perfect", "Smosh", "Ryan Higa", "Jenna Marbles", "Emma Chamberlain",
        "David Dobrik", "Liza Koshy", "Casey Neistat", "Philip DeFranco", "H3H3",
    ],
}

# Attributes (same as background_collector.py)
ATTRIBUTES = [
    ("is_fictional", "Вымышленный?", "Is fictional?", "identity"),
    ("is_male", "Мужчина?", "Is male?", "identity"),
    ("is_human", "Человек?", "Is human?", "identity"),
    ("is_alive", "Жив?", "Is alive?", "identity"),
    ("is_adult", "Взрослый?", "Is adult?", "identity"),
    ("from_movie", "Связан с кино?", "Related to movies?", "media"),
    ("from_tv_series", "Связан с ТВ?", "Related to TV?", "media"),
    ("from_anime", "Связан с аниме?", "Related to anime?", "media"),
    ("from_game", "Связан с играми?", "Related to games?", "media"),
    ("from_book", "Связан с книгами?", "Related to books?", "media"),
    ("from_comics", "Связан с комиксами?", "Related to comics?", "media"),
    ("from_music", "Связан с музыкой?", "Related to music?", "media"),
    ("from_sport", "Связан со спортом?", "Related to sports?", "media"),
    ("from_politics", "Связан с политикой?", "Related to politics?", "media"),
    ("from_science", "Связан с наукой?", "Related to science?", "media"),
    ("from_history", "Историческая личность?", "Historical?", "media"),
    ("from_literature", "Связан с литературой?", "Related to literature?", "media"),
    ("from_art", "Связан с искусством?", "Related to art?", "media"),
    ("from_business", "Связан с бизнесом?", "Related to business?", "media"),
    ("from_internet", "Интернет-знаменитость?", "Internet celebrity?", "media"),
    ("from_action_genre", "Жанр экшн?", "Action genre?", "genre"),
    ("from_comedy_genre", "Комедия?", "Comedy?", "genre"),
    ("from_drama_genre", "Драма?", "Drama?", "genre"),
    ("from_horror_genre", "Ужасы?", "Horror?", "genre"),
    ("from_scifi_genre", "Фантастика?", "Sci-fi?", "genre"),
    ("from_usa", "Из США?", "From USA?", "geography"),
    ("from_uk", "Из UK?", "From UK?", "geography"),
    ("from_europe", "Из Европы?", "From Europe?", "geography"),
    ("from_russia", "Из России?", "From Russia?", "geography"),
    ("from_asia", "Из Азии?", "From Asia?", "geography"),
    ("from_japan", "Из Японии?", "From Japan?", "geography"),
    ("from_china", "Из Китая?", "From China?", "geography"),
    ("from_india", "Из Индии?", "From India?", "geography"),
    ("from_korea", "Из Кореи?", "From Korea?", "geography"),
    ("from_south_america", "Из Ю.Америки?", "From S.America?", "geography"),
    ("from_africa", "Из Африки?", "From Africa?", "geography"),
    ("era_ancient", "Древность?", "Ancient?", "era"),
    ("era_medieval", "Средневековье?", "Medieval?", "era"),
    ("era_modern", "Новое время?", "Modern era?", "era"),
    ("era_20th_century", "20 век?", "20th century?", "era"),
    ("era_21st_century", "21 век?", "21st century?", "era"),
    ("born_before_1950", "До 1950?", "Before 1950?", "era"),
    ("born_1950_1970", "1950-1970?", "1950-1970?", "era"),
    ("born_1970_1990", "1970-1990?", "1970-1990?", "era"),
    ("born_after_1990", "После 1990?", "After 1990?", "era"),
    ("has_superpower", "Суперсилы?", "Superpowers?", "traits"),
    ("is_villain", "Злодей?", "Villain?", "traits"),
    ("is_leader", "Лидер?", "Leader?", "traits"),
    ("is_wealthy", "Богатый?", "Wealthy?", "traits"),
    ("is_comedic", "Комедийный?", "Comedic?", "traits"),
    ("is_dark_brooding", "Мрачный?", "Dark?", "traits"),
    ("is_action_hero", "Герой боевика?", "Action hero?", "traits"),
    ("wears_uniform", "Носит форму?", "Wears uniform?", "traits"),
    ("wears_mask", "Носит маску?", "Wears mask?", "traits"),
    ("has_armor", "Носит броню?", "Has armor?", "traits"),
    ("has_facial_hair", "Борода/усы?", "Facial hair?", "traits"),
    ("is_bald", "Лысый?", "Bald?", "appearance"),
    ("has_glasses", "Очки?", "Glasses?", "appearance"),
    ("has_tattoos", "Татуировки?", "Tattoos?", "appearance"),
    ("distinctive_hair", "Особые волосы?", "Distinctive hair?", "appearance"),
    ("has_distinctive_voice", "Особый голос?", "Distinctive voice?", "appearance"),
    ("known_for_physique", "Известен фигурой?", "Known for physique?", "appearance"),
    ("won_oscar", "Оскар?", "Oscar?", "achievement"),
    ("won_grammy", "Грэмми?", "Grammy?", "achievement"),
    ("won_nobel", "Нобель?", "Nobel?", "achievement"),
    ("olympic_medalist", "Олимпиада?", "Olympic medal?", "achievement"),
    ("world_champion", "Чемпион мира?", "World champion?", "achievement"),
    ("cultural_icon", "Культовая фигура?", "Cultural icon?", "fame"),
    ("controversial", "Скандальный?", "Controversial?", "fame"),
    ("billionaire", "Миллиардер?", "Billionaire?", "fame"),
    ("died_young", "Умер молодым?", "Died young?", "fame"),
    ("active_now", "Активен сейчас?", "Active now?", "fame"),
    ("is_child_friendly", "Детский?", "Child-friendly?", "traits"),
    ("has_famous_catchphrase", "Известная фраза?", "Famous catchphrase?", "traits"),
]

# Category templates
CATEGORY_TEMPLATES = {
    "actors": {
        "is_fictional": 0.0, "is_human": 1.0, "from_movie": 0.9, "from_tv_series": 0.5,
        "is_wealthy": 0.6, "cultural_icon": 0.3, "active_now": 0.7,
    },
    "musicians": {
        "is_fictional": 0.0, "is_human": 1.0, "from_music": 1.0, "from_movie": 0.2,
        "cultural_icon": 0.4, "has_famous_catchphrase": 0.3, "active_now": 0.6,
    },
    "athletes": {
        "is_fictional": 0.0, "is_human": 1.0, "from_sport": 1.0, "wears_uniform": 0.8,
        "known_for_physique": 0.6, "world_champion": 0.3, "active_now": 0.6,
    },
    "politicians": {
        "is_fictional": 0.0, "is_human": 1.0, "from_politics": 1.0, "is_leader": 0.7,
        "controversial": 0.4, "cultural_icon": 0.4,
    },
    "scientists": {
        "is_fictional": 0.0, "is_human": 1.0, "from_science": 1.0, "has_glasses": 0.4,
        "cultural_icon": 0.3, "won_nobel": 0.1,
    },
    "writers": {
        "is_fictional": 0.0, "is_human": 1.0, "from_book": 1.0, "from_literature": 1.0,
        "cultural_icon": 0.3, "has_glasses": 0.3,
    },
    "fictional_superheroes": {
        "is_fictional": 1.0, "is_human": 0.7, "from_comics": 1.0, "from_movie": 0.8,
        "has_superpower": 0.8, "wears_uniform": 0.9, "from_action_genre": 0.9,
        "cultural_icon": 0.5, "is_child_friendly": 0.6,
    },
    "fictional_movies": {
        "is_fictional": 1.0, "is_human": 0.8, "from_movie": 1.0, "from_action_genre": 0.6,
        "cultural_icon": 0.4, "is_child_friendly": 0.5,
    },
    "fictional_animation": {
        "is_fictional": 1.0, "is_human": 0.4, "from_movie": 0.8, "from_tv_series": 0.5,
        "is_child_friendly": 0.9, "is_comedic": 0.6, "cultural_icon": 0.4,
    },
    "fictional_anime": {
        "is_fictional": 1.0, "is_human": 0.7, "from_anime": 1.0, "from_japan": 1.0,
        "from_asia": 1.0, "from_action_genre": 0.7, "distinctive_hair": 0.6,
    },
    "fictional_games": {
        "is_fictional": 1.0, "is_human": 0.5, "from_game": 1.0, "from_action_genre": 0.6,
        "cultural_icon": 0.4, "is_child_friendly": 0.6,
    },
    "youtubers": {
        "is_fictional": 0.0, "is_human": 1.0, "from_internet": 1.0, "era_21st_century": 1.0,
        "born_after_1990": 0.7, "active_now": 1.0, "is_comedic": 0.5,
    },
}

COUNTRY_ATTRS = {
    "Q30": {"from_usa": 1.0},
    "Q145": {"from_uk": 1.0, "from_europe": 1.0},
    "Q142": {"from_europe": 1.0},
    "Q183": {"from_europe": 1.0},
    "Q159": {"from_russia": 1.0},
    "Q17": {"from_japan": 1.0, "from_asia": 1.0},
    "Q148": {"from_china": 1.0, "from_asia": 1.0},
    "Q668": {"from_india": 1.0, "from_asia": 1.0},
    "Q884": {"from_korea": 1.0, "from_asia": 1.0},
    "Q155": {"from_south_america": 1.0},
    "Q414": {"from_south_america": 1.0},
}


def api_request(params: dict, worker_id: int = 0) -> dict:
    """Make Wikidata API request."""
    params["format"] = "json"
    url = f"{WIKIDATA_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": f"{USER_AGENT}/W{worker_id}"})

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            if attempt < 2:
                time.sleep(1 + attempt)
    return {}


def search_entity(query: str, worker_id: int = 0) -> Optional[dict]:
    """Search for a single entity - return first exact/close match."""
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "limit": 3,
        "type": "item",
    }
    result = api_request(params, worker_id)

    query_lower = query.lower().strip()
    query_words = set(query_lower.split())

    for item in result.get("search", []):
        label = item.get("label", "").lower().strip()
        label_words = set(label.split())

        # Exact match
        if label == query_lower:
            return item

        # Same words
        if query_words == label_words:
            return item

    # Return first result if close enough
    if result.get("search"):
        first = result["search"][0]
        label = first.get("label", "").lower()
        if query_lower.split()[0] in label.split()[0]:
            return first

    return None


def get_entity_details(qid: str, worker_id: int = 0) -> dict:
    """Get entity details."""
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "props": "labels|claims|sitelinks",
        "languages": "en|ru",
    }
    result = api_request(params, worker_id)
    return result.get("entities", {}).get(qid, {})


def extract_and_build_attrs(entity: dict, category: str) -> dict:
    """Extract claims and build attributes."""
    claims = entity.get("claims", {})

    # Start with category template
    template = CATEGORY_TEMPLATES.get(category, {})
    attrs = {"is_human": 1.0, "is_adult": 1.0}
    attrs.update(template)

    # Fictional detection
    instance_of = []
    for claim in claims.get("P31", [])[:5]:
        try:
            instance_of.append(claim["mainsnak"]["datavalue"]["value"]["id"])
        except:
            pass

    fictional_types = {"Q95074", "Q15632617", "Q15773317", "Q4271324"}
    if set(instance_of) & fictional_types:
        attrs["is_fictional"] = 1.0

    # Gender
    if "P21" in claims:
        try:
            gender_id = claims["P21"][0]["mainsnak"]["datavalue"]["value"]["id"]
            attrs["is_male"] = 1.0 if gender_id == "Q6581097" else 0.0
        except:
            pass

    # Birth year
    birth_year = None
    if "P569" in claims:
        try:
            time_val = claims["P569"][0]["mainsnak"]["datavalue"]["value"]["time"]
            birth_year = int(time_val[1:5])
        except:
            pass

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

    # Death
    if "P570" in claims:
        attrs["is_alive"] = 0.0
        try:
            death_year = int(claims["P570"][0]["mainsnak"]["datavalue"]["value"]["time"][1:5])
            if birth_year and death_year - birth_year < 50:
                attrs["died_young"] = 0.8
        except:
            pass
    elif birth_year and birth_year < 1940:
        attrs["is_alive"] = 0.1
    else:
        attrs["is_alive"] = 0.9

    # Country
    if "P27" in claims:
        try:
            country = claims["P27"][0]["mainsnak"]["datavalue"]["value"]["id"]
            if country in COUNTRY_ATTRS:
                attrs.update(COUNTRY_ATTRS[country])
        except:
            pass

    # Sitelinks = popularity
    sitelinks = len(entity.get("sitelinks", {}))
    if sitelinks > 100:
        attrs["cultural_icon"] = max(attrs.get("cultural_icon", 0), 0.5)

    return attrs


async def worker(
    worker_id: int,
    category: str,
    seeds: list[str],
    repo: Repository,
    attr_ids: dict[str, int],
    existing_names: set[str],
    results: dict,
):
    """Worker that processes a category."""
    worker_logger = logging.getLogger(f"worker-{worker_id}")
    worker_logger.info(f"Starting on {category} ({len(seeds)} seeds)")

    count = 0
    for seed in seeds:
        if shutdown_requested:
            break

        # Search
        item = search_entity(seed, worker_id)
        if not item:
            continue

        qid = item.get("id", "")
        name = item.get("label", "")

        if not name or name.lower() in existing_names:
            continue

        # Get details
        entity = get_entity_details(qid, worker_id)
        if not entity:
            continue

        # Get Russian label
        labels = entity.get("labels", {})
        ru_label = labels.get("ru", {}).get("value", "")

        # Build attributes
        attrs = extract_and_build_attrs(entity, category)

        # Save
        try:
            eid = await repo.add_entity(name, f"wikidata:{qid}", category, "en")

            if ru_label and ru_label != name:
                await repo.add_alias(eid, ru_label, "ru")

            for attr_key, value in attrs.items():
                if attr_key in attr_ids:
                    await repo.set_entity_attribute(eid, attr_ids[attr_key], value)

            existing_names.add(name.lower())
            count += 1
            worker_logger.info(f"Added: {name}")
        except Exception as e:
            worker_logger.error(f"Error adding {name}: {e}")

        # Rate limiting per worker
        await asyncio.sleep(0.5)

    results[category] = count
    worker_logger.info(f"Finished {category}: {count} entities")


async def main(db_path: str, num_workers: int):
    """Main parallel collection."""
    global shutdown_requested

    logger.info(f"Starting parallel collector with {num_workers} workers")

    # Init DB
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    repo = Repository(db_path)
    await repo.init_db()

    # Ensure attributes
    existing_attrs = await repo.get_all_attributes()
    if not existing_attrs:
        logger.info(f"Creating {len(ATTRIBUTES)} attributes...")
        for key, q_ru, q_en, cat in ATTRIBUTES:
            await repo.add_attribute(key, q_ru, q_en, cat)

    attr_list = await repo.get_all_attributes()
    attr_ids = {a.key: a.id for a in attr_list}

    # Get existing
    existing = await repo.get_all_entities()
    existing_names = {e.name.lower() for e in existing}
    logger.info(f"Database has {len(existing_names)} entities")

    # Assign categories to workers
    categories = list(CATEGORY_SEEDS.keys())
    results = {}

    # Create worker tasks
    tasks = []
    for i, category in enumerate(categories):
        if i >= num_workers:
            break
        seeds = CATEGORY_SEEDS[category]
        task = asyncio.create_task(
            worker(i, category, seeds, repo, attr_ids, existing_names, results)
        )
        tasks.append(task)

    # Wait for all workers
    start_time = time.time()
    await asyncio.gather(*tasks)
    elapsed = time.time() - start_time

    # Summary
    total = sum(results.values())
    final_count = len(existing_names)

    logger.info("=" * 60)
    logger.info(f"DONE in {elapsed:.1f}s")
    logger.info(f"Total new entities: {total}")
    logger.info(f"Database now has: {final_count} entities")
    logger.info("By category:")
    for cat, cnt in results.items():
        logger.info(f"  {cat}: {cnt}")
    logger.info("=" * 60)

    await repo.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/collected.db")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    asyncio.run(main(args.db, args.workers))
