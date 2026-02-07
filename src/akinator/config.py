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
