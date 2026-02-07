# Akinator 2.0 — Architecture

## Overview

Akinator 2.0 is a Telegram bot that guesses characters (real people and fictional characters) by asking yes/no questions. It combines deterministic Bayesian scoring with LLM-powered question generation and natural language understanding.

## System Components

```
+-------------------+       +-------------------+       +-------------------+
|   Telegram Bot    | <---> |   Game Session    | <---> |  Candidate Engine |
|   (aiogram)       |       |   Manager         |       |  (FAISS + SQLite) |
+-------------------+       +-------------------+       +-------------------+
                                    |                           |
                                    v                           v
                            +-------------------+       +-------------------+
                            |  Scoring Engine   |       |  Entity Database  |
                            |  (Bayesian)       |       |  (SQLite)         |
                            +-------------------+       +-------------------+
                                    |
                                    v
                            +-------------------+
                            | Question Policy   |
                            | (Info Gain +      |
                            |  LLM formatting)  |
                            +-------------------+
                                    |
                                    v
                            +-------------------+
                            |   LLM Client      |
                            |   (OpenAI API)    |
                            +-------------------+
```

## Module Breakdown

### 1. `bot/` — Telegram Bot Layer

**Responsibility:** Handle Telegram interactions, render UI (inline keyboards), route commands.

- `bot/handlers.py` — Command handlers (`/start`, `/new`, `/top`, `/why`, `/giveup`)
- `bot/keyboards.py` — Inline keyboard builders (answer buttons)
- `bot/middleware.py` — Session middleware, rate limiting

**Depends on:** Game Session Manager

### 2. `engine/candidate.py` — Candidate Engine

**Responsibility:** Find relevant candidates from the entity database using vector similarity search.

- Accepts an optional text hint from the user
- Computes embedding via OpenAI Embeddings API
- Queries FAISS index for top-K nearest neighbors
- Returns candidate IDs with initial similarity scores

**Depends on:** Entity Database, LLM Client (for embeddings)

### 3. `engine/scoring.py` — Scoring Engine

**Responsibility:** Maintain and update probability distribution over candidates using Bayesian updates.

- Holds `weights[]` array aligned with candidate list
- Updates weights after each user answer
- Normalizes weights after each update
- Provides `top_k()`, `max_prob()`, `entropy()` methods

**Key algorithm:** Bayesian likelihood update (see [GAME_LOGIC.md](GAME_LOGIC.md))

**Depends on:** Entity Database (for attribute values)

### 4. `engine/question_policy.py` — Question Policy

**Responsibility:** Select the next best attribute to ask about, maximizing information gain.

- Computes expected information gain for each unused attribute
- Selects attribute that best splits current candidate distribution
- Delegates to LLM Client for natural language question formatting

**Depends on:** Scoring Engine, Entity Database, LLM Client

### 5. `engine/session.py` — Game Session Manager

**Responsibility:** Orchestrate a single game session lifecycle.

- Manages session state (candidates, weights, history, mode)
- Coordinates Candidate Engine, Scoring Engine, and Question Policy
- Decides when to guess vs. ask another question
- Handles the "learning" flow when guess is wrong

**Depends on:** Candidate Engine, Scoring Engine, Question Policy

### 6. `db/` — Data Layer

**Responsibility:** Persist entities, attributes, and game statistics.

- `db/models.py` — SQLAlchemy / dataclass models
- `db/repository.py` — CRUD operations for entities
- `db/migrations.py` — Schema creation and migrations

**Storage:** SQLite (MVP), upgradable to PostgreSQL + pgvector

### 7. `llm/client.py` — LLM Client

**Responsibility:** Abstraction over OpenAI API calls.

- `get_embedding(text) -> list[float]` — Generate text embeddings
- `format_question(attribute, context) -> str` — Generate human-readable question
- `extract_attributes(description) -> dict` — Extract attributes from free text
- `explain_reasoning(candidates, history) -> str` — Generate explanation for `/why`

**Depends on:** OpenAI API

### 8. `config.py` — Configuration

- API keys (from environment variables)
- Thresholds (guess threshold, max questions, top-K size)
- Model names, embedding dimensions

## Data Flow: Single Game Round

```
1. User sends /new
2. Session created with empty state
3. (Optional) User provides hint text
4. Candidate Engine finds top-K candidates via FAISS
5. Scoring Engine initializes uniform weights
6. LOOP:
   a. Question Policy selects best attribute (max info gain)
   b. LLM formats question in natural language
   c. Bot sends question with answer buttons
   d. User answers (Yes/No/Maybe/...)
   e. Scoring Engine updates weights (Bayesian update)
   f. IF max_prob > GUESS_THRESHOLD or questions >= MAX_QUESTIONS:
      - Bot makes a guess
      - IF correct: game ends with success
      - IF wrong and retries left: continue loop
      - IF wrong and no retries: enter learning mode
   g. ELSE: continue loop
7. Learning mode: collect entity name + attributes from user
```

## Configuration Constants

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MAX_CANDIDATES` | 500 | Max candidates loaded per session |
| `MAX_QUESTIONS` | 20 | Max questions before forced guess |
| `GUESS_THRESHOLD` | 0.85 | Probability threshold to trigger guess |
| `SECOND_GUESS_THRESHOLD` | 0.70 | Threshold for second guess attempt |
| `TOP_K_DISPLAY` | 5 | Number of candidates shown in /top |
| `EMBEDDING_DIM` | 1536 | OpenAI embedding vector dimension |
| `ANSWER_WEIGHT_YES` | 1.0 | Likelihood multiplier for "Yes" |
| `ANSWER_WEIGHT_NO` | 0.0 | Likelihood multiplier for "No" |
| `ANSWER_WEIGHT_PROBABLY_YES` | 0.75 | Likelihood multiplier for "Probably Yes" |
| `ANSWER_WEIGHT_PROBABLY_NO` | 0.25 | Likelihood multiplier for "Probably No" |
| `ANSWER_WEIGHT_DONT_KNOW` | 0.5 | Likelihood multiplier for "Don't Know" |

## Directory Structure

```
Akinator_2.0/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_MODEL.md
│   ├── GAME_LOGIC.md
│   └── TELEGRAM_UX.md
├── src/
│   └── akinator/
│       ├── __init__.py
│       ├── config.py
│       ├── bot/
│       │   ├── __init__.py
│       │   ├── handlers.py
│       │   ├── keyboards.py
│       │   └── middleware.py
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── candidate.py
│       │   ├── scoring.py
│       │   ├── question_policy.py
│       │   └── session.py
│       ├── db/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   └── repository.py
│       └── llm/
│           ├── __init__.py
│           └── client.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_scoring.py
│   ├── test_question_policy.py
│   ├── test_candidate.py
│   ├── test_session.py
│   ├── test_repository.py
│   └── test_handlers.py
├── scripts/
│   └── seed_data.py
├── pyproject.toml
├── README.md
└── LICENSE
```
