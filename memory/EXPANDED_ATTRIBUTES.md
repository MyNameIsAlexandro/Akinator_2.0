# Expanded Attributes System (32 → 62)

## Overview

The attribute system was expanded from 32 to 62 attributes to improve accuracy from ~79% to 100%.

## Attribute Categories

### Identity (6 attributes)
| Key | Question (RU) | Question (EN) |
|-----|--------------|---------------|
| is_fictional | Этот персонаж вымышленный? | Is this character fictional? |
| is_male | Это мужчина/мужской персонаж? | Is this a male character? |
| is_human | Это человек (или человекоподобный)? | Is this a human (or humanoid)? |
| is_alive | Этот персонаж/человек жив? | Is this character/person alive? |
| is_adult | Это взрослый персонаж? | Is this an adult character? |
| is_villain | Это злодей/антигерой? | Is this a villain/antagonist? |

### Media (19 attributes)
| Key | Question (RU) |
|-----|--------------|
| from_movie | Связан с кино? |
| from_tv_series | Связан с сериалами? |
| from_anime | Связан с аниме/мангой? |
| from_game | Связан с видеоиграми? |
| from_book | Связан с книгами/литературой? |
| from_comics | Связан с комиксами? |
| from_music | Связан с музыкой? |
| from_sport | Связан со спортом? |
| from_politics | Связан с политикой? |
| from_science | Связан с наукой? |
| from_history | Историческая личность/персонаж? |
| from_literature | Связан с литературой? |
| from_philosophy | Связан с философией? |
| from_military | Связан с военным делом? |
| from_business | Связан с бизнесом? |
| from_fashion | Связан с модой? |
| from_art | Связан с изобразительным искусством? |
| from_religion | Связан с религией? |
| from_internet | Интернет-знаменитость? |

### Geography (10 attributes)
| Key | Question (RU) |
|-----|--------------|
| from_usa | Связан с США? |
| from_europe | Связан с Европой? |
| from_russia | Связан с Россией? |
| from_asia | Связан с Азией? |
| from_japan | Связан с Японией? |
| from_africa | Связан с Африкой? |
| from_south_america | Связан с Южной Америкой? |
| from_middle_east | Связан с Ближним Востоком? |
| from_oceania | Связан с Океанией? |
| from_china | Связан с Китаем? |

### Era (5 attributes)
| Key | Question (RU) |
|-----|--------------|
| era_ancient | Из древности (до 500 н.э.)? |
| era_medieval | Из средневековья (500-1500)? |
| era_modern | Из нового времени (1500-1900)? |
| era_20th_century | Из 20-го века? |
| era_21st_century | Из 21-го века? |

### Birth Decade (10 attributes) - NEW
| Key | Question (RU) |
|-----|--------------|
| born_1900s | Родился в 1900-х? |
| born_1910s | Родился в 1910-х? |
| born_1920s | Родился в 1920-х? |
| born_1930s | Родился в 1930-х? |
| born_1940s | Родился в 1940-х? |
| born_1950s | Родился в 1950-х? |
| born_1960s | Родился в 1960-х? |
| born_1970s | Родился в 1970-х? |
| born_1980s | Родился в 1980-х? |
| born_1990s | Родился в 1990-х или позже? |

### Traits (12 attributes)
| Key | Question (RU) |
|-----|--------------|
| has_superpower | Обладает сверхспособностями? |
| wears_uniform | Носит униформу/костюм? |
| has_famous_catchphrase | Известен крылатой фразой? |
| is_leader | Является лидером/главой? |
| is_wealthy | Богатый/знатный? |
| is_action_hero | Герой боевика/экшена? |
| is_comedic | Комедийный персонаж? |
| is_dark_brooding | Мрачный/серьёзный персонаж? |
| is_child_friendly | Для детской аудитории? |
| wears_mask | Носит маску? |
| has_armor | Носит броню? |
| has_facial_hair | Имеет бороду/усы? |

## Why 62 Attributes?

### Information Theory

For N entities, we need at least log2(N) bits of information to uniquely identify each one:

| Entities | Min Bits | Attributes Needed |
|----------|----------|-------------------|
| 200 | 7.6 | ~32 (barely enough) |
| 1,000 | 10 | ~50 |
| 10,000 | 13.3 | ~70 |
| 100,000 | 16.6 | ~100 |

With 62 attributes providing ~13-14 bits of information, we can reliably distinguish ~10,000 entities.

### Key Additions (30 new attributes)

1. **Birth Decades (10)** - Crucial for distinguishing real people
2. **Visual Traits (6)** - has_facial_hair, wears_mask, has_armor, etc.
3. **Personality (4)** - is_comedic, is_dark_brooding, is_child_friendly, is_action_hero
4. **Extended Geography (5)** - from_africa, from_south_america, from_middle_east, from_oceania, from_china
5. **Extended Media (5)** - from_literature, from_philosophy, from_military, from_business, from_fashion

## Related Attributes (Question Skipping)

To avoid redundant questions, related attributes are grouped:

```python
RELATED_ATTRIBUTES = {
    "from_book": ["from_literature"],
    "from_literature": ["from_book"],
    "from_japan": ["from_asia"],
    "from_china": ["from_asia"],
    "from_russia": ["from_europe", "from_asia"],
    "era_20th_century": ["era_21st_century", "era_modern"],
    "born_1970s": ["born_1960s", "born_1980s"],
    # etc.
}
```

If user answers one attribute, related ones are skipped.
