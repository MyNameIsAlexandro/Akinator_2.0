# Akinator 2.0 — Game Logic

## Overview

The game engine uses a **Bayesian probability update** approach combined with **information gain** for question selection. This document specifies the exact algorithms.

## 1. Session Initialization

### Without hint:
1. Load all entity IDs from database
2. Initialize uniform weights: `w_i = 1/N` for all candidates

### With hint:
1. Compute embedding of hint text
2. Query FAISS for top-K nearest neighbors (K = `MAX_CANDIDATES`)
3. Initialize weights proportional to cosine similarity scores
4. Normalize: `w_i = sim_i / sum(sim)`

## 2. Bayesian Weight Update

After each question-answer pair:

### Input:
- `attribute_key`: the attribute being asked about (e.g., `is_fictional`)
- `answer`: user's answer (Yes / No / Probably Yes / Probably No / Don't Know)
- `candidates[i].attributes[attribute_key]`: attribute value `p_i` for each candidate (0.0 to 1.0)

### Answer-to-likelihood mapping:

| Answer | Likelihood formula |
|--------|-------------------|
| Yes | `L_i = p_i` |
| No | `L_i = 1 - p_i` |
| Probably Yes | `L_i = 0.75 * p_i + 0.25 * (1 - p_i)` = `0.5 * p_i + 0.25` |
| Probably No | `L_i = 0.25 * p_i + 0.75 * (1 - p_i)` = `0.75 - 0.5 * p_i` |
| Don't Know | `L_i = 1.0` (no update) |

### Smoothing:

To avoid zero probabilities (which would permanently eliminate candidates):

```
L_i = max(L_i, EPSILON)    where EPSILON = 0.01
```

### Update rule:

```
w_i' = w_i * L_i
w_i'' = w_i' / sum(w')     # normalize
```

### Pruning:

After update, if a candidate's weight drops below `PRUNE_THRESHOLD = 1e-6`, it is removed from the active set to save computation.

## 3. Question Selection (Information Gain)

### Goal:
Select the attribute that maximally reduces uncertainty about the correct candidate.

### Algorithm:

For each candidate attribute `a` not yet asked:

1. Compute the **expected distribution of answers** given current weights:
   - `P(yes|a) = sum(w_i * p_i_a)` — weighted probability that answer is "Yes"
   - `P(no|a) = sum(w_i * (1 - p_i_a))` — weighted probability that answer is "No"

2. Compute **posterior entropy** for each possible answer:
   - For answer "Yes": compute updated weights `w_i' = w_i * p_i_a / Z`, then entropy `H_yes`
   - For answer "No": compute updated weights `w_i' = w_i * (1-p_i_a) / Z`, then entropy `H_no`

3. Compute **expected posterior entropy**:
   ```
   E[H|a] = P(yes|a) * H_yes + P(no|a) * H_no
   ```

4. Compute **information gain**:
   ```
   IG(a) = H_current - E[H|a]
   ```

5. Select attribute with maximum `IG(a)`.

### Entropy formula:

```
H = -sum(w_i * log2(w_i))   for w_i > 0
```

### Optimization:

For MVP, we only consider Yes/No answers in information gain calculation (not Probably Yes/No), as this is a good approximation and halves computation.

## 4. Guess Decision

After each weight update, check:

```python
def should_guess(session: GameSession) -> bool:
    max_w = max(session.weights)

    # Confident enough
    if max_w >= GUESS_THRESHOLD:    # 0.85
        return True

    # Running out of questions
    if session.question_count >= MAX_QUESTIONS:    # 20
        return True

    # Very few candidates left
    active = sum(1 for w in session.weights if w > 0.01)
    if active <= 2:
        return True

    return False
```

### Guess logic:

1. First guess: candidate with highest weight
2. If wrong and `max_w >= SECOND_GUESS_THRESHOLD` (0.70) for second candidate: guess second
3. If wrong again: enter learning mode

## 5. Learning Mode

When the bot fails to guess correctly:

1. Ask: "Who were you thinking of?" → user provides name
2. Ask: "Give a short description" → user provides description
3. Bot uses LLM to extract attributes from description
4. Bot asks 3-5 key attributes to confirm/correct
5. Entity is saved to database
6. Embedding is computed and added to FAISS index

## 6. Handling Missing Attributes

If a candidate has no value for a given attribute:

```python
def get_attribute_value(entity_id: int, attribute_key: str) -> float:
    value = db.get(entity_id, attribute_key)
    if value is None:
        return 0.5    # Maximum uncertainty = no information
    return value
```

## 7. Answer Parsing

User answers come via inline keyboard buttons, but we also support free-text:

| Button text (RU) | Button text (EN) | Answer enum |
|-------------------|-------------------|-------------|
| Да | Yes | `YES` |
| Нет | No | `NO` |
| Скорее да | Probably yes | `PROBABLY_YES` |
| Скорее нет | Probably no | `PROBABLY_NO` |
| Не знаю | Don't know | `DONT_KNOW` |

## 8. Complete Game Loop (Pseudocode)

```python
async def game_loop(session, user_answer=None):
    if session.mode == GameMode.WAITING_HINT:
        # Process hint or skip
        if hint_provided:
            candidates = candidate_engine.search(hint_text)
            session.init_with_candidates(candidates)
        else:
            session.init_all_candidates()
        session.mode = GameMode.ASKING

    if session.mode == GameMode.ASKING:
        if user_answer is not None:
            # Update weights with new answer
            scoring_engine.update(session, last_attribute, user_answer)
            session.question_count += 1

        if should_guess(session):
            session.mode = GameMode.GUESSING
            return make_guess(session)

        # Select next question
        best_attr = question_policy.select(session)
        question_text = llm.format_question(best_attr)
        session.asked_attributes.append(best_attr.id)
        return question_text

    if session.mode == GameMode.GUESSING:
        if user_answer == "correct":
            session.mode = GameMode.FINISHED
            return "I guessed it!"
        else:
            # Try second guess or enter learning
            second = get_second_candidate(session)
            if second and second.weight >= SECOND_GUESS_THRESHOLD:
                return make_guess(session, second)
            else:
                session.mode = GameMode.LEARNING
                return "Who were you thinking of?"

    if session.mode == GameMode.LEARNING:
        # Collect and save new entity
        save_new_entity(user_input)
        session.mode = GameMode.FINISHED
        return "Thanks! I'll remember that."
```
