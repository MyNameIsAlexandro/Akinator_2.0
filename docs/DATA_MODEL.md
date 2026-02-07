# Akinator 2.0 — Data Model

## Entity Schema

### Table: `entities`

Stores all guessable characters/people.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-increment ID |
| `name` | TEXT NOT NULL | Primary display name |
| `description` | TEXT NOT NULL | 1-2 sentence description (used for embeddings) |
| `entity_type` | TEXT NOT NULL | Category: `person`, `character`, `animal`, `object` |
| `language` | TEXT NOT NULL | Primary language: `ru`, `en` |
| `created_at` | TIMESTAMP | When entity was added |
| `play_count` | INTEGER DEFAULT 0 | How many times this entity was the answer |
| `guess_success_count` | INTEGER DEFAULT 0 | How many times bot guessed correctly |

### Table: `entity_aliases`

Multiple names/spellings for the same entity.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-increment ID |
| `entity_id` | INTEGER FK → entities.id | Parent entity |
| `alias` | TEXT NOT NULL | Alternative name |
| `language` | TEXT NOT NULL | Language of alias: `ru`, `en` |

### Table: `entity_attributes`

Probabilistic attribute values for each entity.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-increment ID |
| `entity_id` | INTEGER FK → entities.id | Parent entity |
| `attribute_id` | INTEGER FK → attributes.id | Attribute definition |
| `value` | REAL NOT NULL | Probability 0.0 — 1.0 |

### Table: `attributes`

Attribute definitions (the "questions" we can ask).

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-increment ID |
| `key` | TEXT UNIQUE NOT NULL | Machine key: `is_fictional`, `is_male`, etc. |
| `question_ru` | TEXT NOT NULL | Question text in Russian |
| `question_en` | TEXT NOT NULL | Question text in English |
| `category` | TEXT | Grouping: `identity`, `media`, `geography`, `era`, `profession` |

### Table: `entity_embeddings`

Stored embeddings for FAISS index reconstruction.

| Column | Type | Description |
|--------|------|-------------|
| `entity_id` | INTEGER PK FK → entities.id | Parent entity |
| `embedding` | BLOB NOT NULL | Serialized float32 vector (1536 dims) |

## Core Attributes (MVP Set)

### Identity
| Key | Question (RU) | Question (EN) |
|-----|---------------|---------------|
| `is_fictional` | Этот персонаж вымышленный? | Is this character fictional? |
| `is_male` | Это мужчина/мужской персонаж? | Is this a male character? |
| `is_human` | Это человек (или человекоподобный)? | Is this a human (or humanoid)? |
| `is_alive` | Этот персонаж/человек жив? | Is this character/person alive? |
| `is_adult` | Это взрослый персонаж? | Is this an adult character? |
| `is_villain` | Это злодей/антигерой? | Is this a villain/antagonist? |

### Media / Origin
| Key | Question (RU) | Question (EN) |
|-----|---------------|---------------|
| `from_movie` | Связан с кино? | Related to movies? |
| `from_tv_series` | Связан с сериалами? | Related to TV series? |
| `from_anime` | Связан с аниме/мангой? | Related to anime/manga? |
| `from_game` | Связан с видеоиграми? | Related to video games? |
| `from_book` | Связан с книгами/литературой? | Related to books/literature? |
| `from_comics` | Связан с комиксами? | Related to comics? |
| `from_music` | Связан с музыкой? | Related to music? |
| `from_sport` | Связан со спортом? | Related to sports? |
| `from_politics` | Связан с политикой? | Related to politics? |
| `from_science` | Связан с наукой? | Related to science? |
| `from_history` | Историческая личность/персонаж? | Historical figure/character? |

### Geography
| Key | Question (RU) | Question (EN) |
|-----|---------------|---------------|
| `from_usa` | Связан с США? | Related to USA? |
| `from_europe` | Связан с Европой? | Related to Europe? |
| `from_russia` | Связан с Россией? | Related to Russia? |
| `from_asia` | Связан с Азией? | Related to Asia? |
| `from_japan` | Связан с Японией? | Related to Japan? |

### Era
| Key | Question (RU) | Question (EN) |
|-----|---------------|---------------|
| `era_ancient` | Из древности (до 500 н.э.)? | From ancient times (before 500 AD)? |
| `era_medieval` | Из средневековья (500-1500)? | From medieval era (500-1500)? |
| `era_modern` | Из нового времени (1500-1900)? | From modern era (1500-1900)? |
| `era_20th_century` | Из 20-го века? | From the 20th century? |
| `era_21st_century` | Из 21-го века? | From the 21st century? |

### Appearance / Traits
| Key | Question (RU) | Question (EN) |
|-----|---------------|---------------|
| `has_superpower` | Обладает сверхспособностями? | Has superpowers? |
| `wears_uniform` | Носит униформу/костюм? | Wears a uniform/costume? |
| `has_famous_catchphrase` | Известен крылатой фразой? | Known for a famous catchphrase? |
| `is_leader` | Является лидером/главой? | Is a leader/head? |
| `is_wealthy` | Богатый/знатный? | Wealthy/noble? |

**Total MVP attributes: 31**

## In-Memory Session State

```python
@dataclass
class GameSession:
    session_id: str               # UUID
    user_id: int                  # Telegram user ID
    language: str                 # 'ru' or 'en'
    mode: GameMode                # ASKING, GUESSING, LEARNING, FINISHED
    candidate_ids: list[int]      # Entity IDs in play
    weights: list[float]          # Probability weights (same order as candidate_ids)
    asked_attributes: list[int]   # Attribute IDs already asked
    history: list[QAPair]         # Question-answer history
    hint_text: str | None         # Optional initial hint from user
    guess_count: int              # Number of guesses made
    question_count: int           # Number of questions asked
    created_at: datetime
```

```python
class GameMode(Enum):
    WAITING_HINT = "waiting_hint"   # Waiting for optional hint
    ASKING = "asking"               # Asking questions
    GUESSING = "guessing"           # Making a guess
    LEARNING = "learning"           # Collecting new entity data
    FINISHED = "finished"           # Game over

@dataclass
class QAPair:
    attribute_id: int | None    # None if free-form LLM question
    attribute_key: str
    question_text: str
    answer: Answer

class Answer(Enum):
    YES = "yes"
    NO = "no"
    PROBABLY_YES = "probably_yes"
    PROBABLY_NO = "probably_no"
    DONT_KNOW = "dont_know"
```

## FAISS Index

- **Type:** `IndexFlatIP` (inner product, cosine similarity on normalized vectors)
- **Dimensions:** 1536 (OpenAI `text-embedding-3-small`)
- **ID mapping:** `IndexIDMap` wrapping `IndexFlatIP`, maps FAISS indices to entity IDs
- **Storage:** Serialized to disk as `data/faiss_index.bin`
- **Rebuild:** On startup or when new entities are added

## Database File Layout

```
data/
├── akinator.db          # SQLite database
├── faiss_index.bin      # FAISS index file
└── faiss_id_map.json    # Entity ID to FAISS index mapping
```
