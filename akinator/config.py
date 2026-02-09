"""Configuration constants for Akinator 2.0."""

MAX_CANDIDATES = 500
MAX_QUESTIONS = 20
GUESS_THRESHOLD = 0.85
SECOND_GUESS_THRESHOLD = 0.70
TOP_K_DISPLAY = 5
EMBEDDING_DIM = 1536
PRUNE_THRESHOLD = 1e-6
EPSILON = 0.01

ANSWER_WEIGHTS = {
    "yes": 1.0,
    "no": 0.0,
    "probably_yes": 0.75,
    "probably_no": 0.25,
    "dont_know": 0.5,
}

# All 31 attribute keys used for entity classification
ATTRIBUTE_KEYS = [
    "is_fictional", "is_male", "is_human", "is_alive", "is_adult", "is_villain",
    "from_movie", "from_tv_series", "from_anime", "from_game", "from_book",
    "from_comics", "from_music", "from_sport", "from_politics", "from_science",
    "from_history", "from_usa", "from_europe", "from_russia", "from_asia",
    "from_japan", "era_ancient", "era_medieval", "era_modern", "era_20th_century",
    "era_21st_century", "has_superpower", "wears_uniform", "has_famous_catchphrase",
    "is_leader", "is_wealthy",
]

# LLM attribute merge weights
LLM_QA_WEIGHT = 0.3
LLM_KNOWLEDGE_WEIGHT = 0.7

# GitHub auto-backup settings
BACKUP_INTERVAL_HOURS = 6.0
BACKUP_MIN_NEW_ENTITIES = 5
GITHUB_REPO = "MyNameIsAlexandro/Akinator_2.0"
