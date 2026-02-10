# Failure Analysis & Debugging Guide

## Journey: 78.82% → 100%

### Phase 1: Baseline (32 attributes) - 78.82%
**Problem**: Only 32 attributes provided ~7.7 bits of information, barely enough for 203 entities.

**Common failures**:
- Tech leaders confused (Musk vs Gates vs Zuckerberg)
- Marvel heroes confused (Spider-Man vs Wolverine vs Hulk)
- Anime protagonists confused (Naruto vs Goku vs Luffy)

### Phase 2: Expanded Attributes (62) - 93.10%
**Solution**: Added 30 new attributes including:
- Birth decades (born_1900s through born_1990s)
- Visual traits (has_facial_hair, wears_mask, has_armor)
- Personality (is_comedic, is_dark_brooding, is_action_hero)

**Remaining failures**: 14 entities still confused

### Phase 3: Entity Overrides - 97.04%
**Solution**: Added specific attribute overrides for confusing pairs:
- Elon Musk: born_1970s=1.0, born_1950s=0.0
- Bill Gates: born_1950s=1.0, born_1970s=0.0
- Wolverine: has_facial_hair=1.0, is_dark_brooding=1.0

**Remaining failures**: 6 entities

### Phase 4: More Overrides - 100%
**Solution**: Added overrides for remaining pairs:
- Mickey Mouse vs cartoon characters
- Tom vs Jerry (villain vs hero role)
- Obama vs Trump (birth decade, profession)
- Mozart vs Beethoven (style, era)

## Debugging Checklist

When accuracy drops, check in order:

### 1. Database Integrity
```bash
sqlite3 akinator/data/akinator.db "SELECT COUNT(*) FROM entities;"
sqlite3 akinator/data/akinator.db "SELECT COUNT(*) FROM attributes;"
```
Expected: 203+ entities, 62 attributes

### 2. Entity Attributes
```bash
sqlite3 akinator/data/akinator.db "
SELECT a.key, ea.value
FROM entity_attributes ea
JOIN attributes a ON ea.attribute_id = a.id
JOIN entities e ON ea.entity_id = e.id
WHERE e.name = 'EntityName'
ORDER BY a.id;"
```

### 3. Test Output
Look at "Sample failures" in test output:
```
Target: Wolverine | Guessed: Spider-Man | Questions: 20 | Prob: 0.45
```

This means:
- Wolverine was target
- Algorithm guessed Spider-Man
- Asked max 20 questions
- Final confidence was only 45%

### 4. Add Override
If two entities are confused, find distinguishing attributes:

```python
# In entity_to_category_map.py ENTITY_OVERRIDES
"Wolverine": {
    "has_facial_hair": 1.0,  # Has distinctive sideburns
    "is_dark_brooding": 1.0, # Brooding personality
    "wears_mask": 0.2,       # Rarely wears mask
},
"Spider-Man": {
    "has_facial_hair": 0.0,  # Clean shaven
    "is_dark_brooding": 0.0, # Friendly neighborhood hero
    "wears_mask": 1.0,       # Always masked
},
```

### 5. Regenerate DB
```bash
python migrate_db_62_attrs.py
```

### 6. Run Test
```bash
pytest tests/test_simulation.py::test_full_simulation -v -s
```

## Common Confusion Pairs & Solutions

| Pair | Distinguishing Attributes |
|------|--------------------------|
| Musk vs Gates | born_1970s vs born_1950s |
| Messi vs Zidane | from_south_america vs from_europe, born_1980s vs born_1970s |
| Wolverine vs Spider-Man | has_facial_hair, is_dark_brooding, wears_mask |
| Batman vs Black Panther | has_superpower, from_africa |
| Naruto vs Luffy | wears_uniform, is_wealthy |
| Freddie Mercury vs Elvis | born_1940s vs born_1930s, has_facial_hair |

## Information Gain Debugging

If an entity is being confused, check which attributes have low information gain:

```python
from akinator.engine.question_policy import QuestionPolicy
policy = QuestionPolicy()
ig = policy.compute_info_gain(session, entities, "attribute_key")
print(f"Information gain for {attr}: {ig}")
```

Low IG means the attribute doesn't help distinguish between remaining candidates.
