# Final Results Report

## Summary

| Metric | Value |
|--------|-------|
| **Entities** | 203 (manual) |
| **Attributes** | 62 |
| **Accuracy (Perfect)** | 100.00% |
| **Accuracy (Realistic)** | 99.51% |
| **Accuracy (Pessimistic)** | 100.00% |
| **Avg Questions** | 12-14 |

## Test Strategies

### 1. Perfect Oracle (YES/NO only)
- User answers with exact YES/NO based on ground truth
- Best case scenario
- Result: **100.00%** (203/203)

### 2. Realistic Oracle
- User sometimes answers PROBABLY_YES/PROBABLY_NO
- 10% chance of DONT_KNOW on uncertain attributes
- Result: **99.51%** (202/203)

### 3. Pessimistic Oracle
- User frequently answers DONT_KNOW
- 30% chance of uncertain answers
- Simulates users who don't know details
- Result: **100.00%** (203/203)

## Key Achievements

### 1. Attribute Expansion (32 → 62)
Added 30 new attributes:
- Birth decades (born_1900s - born_1990s)
- Visual traits (has_facial_hair, wears_mask, has_armor)
- Personality (is_comedic, is_dark_brooding)
- Extended geography and media categories

### 2. Entity Override System
Created `entity_to_category_map.py` with:
- 61 category templates
- 36 entity-specific overrides
- Handles confusing pairs like Musk/Gates, Wolverine/Spider-Man

### 3. Smart Question Policy
- Information gain based selection
- Skips related questions (book → literature)
- Adaptive to user uncertainty

### 4. Answer Highlighting
- Shows "✓ Ваш ответ: **Да**" after each answer
- Better UX feedback

### 5. CI/CD Integration
- GitHub Actions runs accuracy test on every push
- Fails if accuracy < 99%
- Railway auto-deploys on success

## Architecture

```
akinator/
├── data/
│   ├── akinator.db      # Bundled database
│   └── categories.py    # Category templates
├── db/
│   ├── models.py        # Entity, Attribute, Session
│   └── repository.py    # SQLite operations
├── engine/
│   ├── scoring.py       # Bayesian inference
│   ├── question_policy.py # Information gain
│   └── session.py       # Game session management
├── bot/
│   ├── handlers.py      # Telegram handlers
│   └── keyboards.py     # Inline keyboards
└── __main__.py          # Entry point
```

## Files Reference

| File | Purpose |
|------|---------|
| `entity_to_category_map.py` | Category mapping + overrides |
| `migrate_db_62_attrs.py` | DB migration script |
| `tests/test_simulation.py` | Accuracy regression test |
| `.github/workflows/regression-test.yml` | CI/CD |

## Scaling Roadmap

| Entities | Attributes Needed | Status |
|----------|-------------------|--------|
| 203 | 62 | ✅ Done |
| 1,000 | ~70 | Ready (synthetic_1k.db) |
| 10,000 | ~80 | Wikidata import available |
| 100,000 | ~100 | Future |

## Commands

```bash
# Run accuracy test
pytest tests/test_simulation.py -v -s

# Regenerate DB with overrides
python migrate_db_62_attrs.py

# Import from Wikidata
python -m akinator.import_wikidata --limit 10000

# Start bot locally
BOT_TOKEN=xxx python -m akinator
```
