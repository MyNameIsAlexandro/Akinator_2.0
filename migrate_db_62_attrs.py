"""Migrate database from 32 to 62 attributes.

This script:
1. Loads all entities from the existing database (32 attrs)
2. Creates a new database with 62 attributes
3. Re-applies category templates with all 62 attributes
4. Preserves entity names, descriptions, types, and overrides

Usage:
    python migrate_db_62_attrs.py
"""

from __future__ import annotations

import asyncio
import logging
import os

from akinator.data.categories import TEMPLATES
from akinator.db.repository import Repository
from entity_to_category_map import get_category, get_overrides

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate")

# All 62 attributes in order
ATTRIBUTES_62 = [
    # Identity
    ("is_fictional", "Этот персонаж вымышленный?", "Is this character fictional?", "identity"),
    ("is_male", "Это мужчина/мужской персонаж?", "Is this a male character?", "identity"),
    ("is_human", "Это человек (или человекоподобный)?", "Is this a human (or humanoid)?", "identity"),
    ("is_alive", "Этот персонаж/человек жив?", "Is this character/person alive?", "identity"),
    ("is_adult", "Это взрослый персонаж?", "Is this an adult character?", "identity"),
    ("is_villain", "Это злодей/антигерой?", "Is this a villain/antagonist?", "identity"),

    # Media
    ("from_movie", "Связан с кино?", "Related to movies?", "media"),
    ("from_tv_series", "Связан с сериалами?", "Related to TV series?", "media"),
    ("from_anime", "Связан с аниме/мангой?", "Related to anime/manga?", "media"),
    ("from_game", "Связан с видеоиграми?", "Related to video games?", "media"),
    ("from_book", "Связан с книгами/литературой?", "Related to books/literature?", "media"),
    ("from_comics", "Связан с комиксами?", "Related to comics?", "media"),
    ("from_music", "Связан с музыкой?", "Related to music?", "media"),
    ("from_sport", "Связан со спортом?", "Related to sports?", "media"),
    ("from_politics", "Связан с политикой?", "Related to politics?", "media"),
    ("from_science", "Связан с наукой?", "Related to science?", "media"),
    ("from_history", "Историческая личность/персонаж?", "Historical figure/character?", "media"),
    ("from_literature", "Связан с литературой?", "Related to literature?", "media"),
    ("from_philosophy", "Связан с философией?", "Related to philosophy?", "media"),
    ("from_military", "Связан с военным делом?", "Related to military?", "media"),
    ("from_business", "Связан с бизнесом?", "Related to business?", "media"),
    ("from_fashion", "Связан с модой?", "Related to fashion?", "media"),
    ("from_art", "Связан с изобразительным искусством?", "Related to visual arts?", "media"),
    ("from_religion", "Связан с религией?", "Related to religion?", "media"),
    ("from_internet", "Интернет-знаменитость?", "Internet celebrity?", "media"),

    # Geography
    ("from_usa", "Связан с США?", "Related to USA?", "geography"),
    ("from_europe", "Связан с Европой?", "Related to Europe?", "geography"),
    ("from_russia", "Связан с Россией?", "Related to Russia?", "geography"),
    ("from_asia", "Связан с Азией?", "Related to Asia?", "geography"),
    ("from_japan", "Связан с Японией?", "Related to Japan?", "geography"),
    ("from_africa", "Связан с Африкой?", "Related to Africa?", "geography"),
    ("from_south_america", "Связан с Южной Америкой?", "Related to South America?", "geography"),
    ("from_middle_east", "Связан с Ближним Востоком?", "Related to Middle East?", "geography"),
    ("from_oceania", "Связан с Океанией?", "Related to Oceania?", "geography"),
    ("from_china", "Связан с Китаем?", "Related to China?", "geography"),

    # Era
    ("era_ancient", "Из древности (до 500 н.э.)?", "From ancient times (before 500 AD)?", "era"),
    ("era_medieval", "Из средневековья (500-1500)?", "From medieval era (500-1500)?", "era"),
    ("era_modern", "Из нового времени (1500-1900)?", "From modern era (1500-1900)?", "era"),
    ("era_20th_century", "Из 20-го века?", "From the 20th century?", "era"),
    ("era_21st_century", "Из 21-го века?", "From the 21st century?", "era"),

    # Birth Decades
    ("born_1900s", "Родился в 1900-х?", "Born in 1900s?", "birth_decade"),
    ("born_1910s", "Родился в 1910-х?", "Born in 1910s?", "birth_decade"),
    ("born_1920s", "Родился в 1920-х?", "Born in 1920s?", "birth_decade"),
    ("born_1930s", "Родился в 1930-х?", "Born in 1930s?", "birth_decade"),
    ("born_1940s", "Родился в 1940-х?", "Born in 1940s?", "birth_decade"),
    ("born_1950s", "Родился в 1950-х?", "Born in 1950s?", "birth_decade"),
    ("born_1960s", "Родился в 1960-х?", "Born in 1960s?", "birth_decade"),
    ("born_1970s", "Родился в 1970-х?", "Born in 1970s?", "birth_decade"),
    ("born_1980s", "Родился в 1980-х?", "Born in 1980s?", "birth_decade"),
    ("born_1990s", "Родился в 1990-х или позже?", "Born in 1990s or later?", "birth_decade"),

    # Traits
    ("has_superpower", "Обладает сверхспособностями?", "Has superpowers?", "traits"),
    ("wears_uniform", "Носит униформу/костюм?", "Wears a uniform/costume?", "traits"),
    ("has_famous_catchphrase", "Известен крылатой фразой?", "Known for a famous catchphrase?", "traits"),
    ("is_leader", "Является лидером/главой?", "Is a leader/head?", "traits"),
    ("is_wealthy", "Богатый/знатный?", "Wealthy/noble?", "traits"),
    ("is_action_hero", "Герой боевика/экшена?", "Action hero?", "traits"),
    ("is_comedic", "Комедийный персонаж?", "Comedic character?", "traits"),
    ("is_dark_brooding", "Мрачный/серьёзный персонаж?", "Dark/brooding character?", "traits"),
    ("is_child_friendly", "Детский персонаж?", "Child-friendly character?", "traits"),
    ("wears_mask", "Носит маску?", "Wears a mask?", "traits"),
    ("has_armor", "Носит броню/доспехи?", "Wears armor?", "traits"),
    ("has_facial_hair", "Имеет бороду/усы?", "Has facial hair?", "traits"),
]


async def migrate():
    """Migrate database from 32 to 62 attributes."""

    old_db_path = "data/akinator.db"
    new_db_path = "data/akinator_62.db"

    # Backup old DB
    if os.path.exists(old_db_path):
        import shutil
        backup_path = "data/akinator_32_backup.db"
        shutil.copy2(old_db_path, backup_path)
        logger.info(f"Backed up old DB to {backup_path}")

    # Load entities from old DB
    old_repo = Repository(old_db_path)
    await old_repo.init_db()

    entities = await old_repo.get_all_entities()
    all_attrs = await old_repo.get_all_entity_attributes()

    logger.info(f"Loaded {len(entities)} entities from old DB")

    # Get entity aliases
    entity_aliases = {}
    for entity in entities:
        aliases = await old_repo.get_aliases(entity.id)
        entity_aliases[entity.id] = aliases

    await old_repo.close()

    # Create new DB
    if os.path.exists(new_db_path):
        os.remove(new_db_path)

    new_repo = Repository(new_db_path)
    await new_repo.init_db()

    # Add all 62 attributes
    attr_ids = {}
    for key, q_ru, q_en, cat in ATTRIBUTES_62:
        aid = await new_repo.add_attribute(key, q_ru, q_en, cat)
        attr_ids[key] = aid

    logger.info(f"Created {len(attr_ids)} attributes in new DB")

    # Migrate entities
    skipped = 0
    for old_entity in entities:
        # Get category from mapping
        category = get_category(old_entity.name)
        if category is None or category not in TEMPLATES:
            logger.warning(f"No category mapping for '{old_entity.name}', skipping")
            skipped += 1
            continue

        # Create entity
        new_eid = await new_repo.add_entity(
            old_entity.name,
            category,
            old_entity.entity_type,
            old_entity.language,
        )

        # Add aliases
        for alias_text, alias_lang in entity_aliases.get(old_entity.id, []):
            await new_repo.add_alias(new_eid, alias_text, alias_lang)

        # Get full attribute set from template
        template = TEMPLATES[category]
        old_attrs = all_attrs.get(old_entity.id, {})

        # Get entity-specific overrides
        entity_overrides = get_overrides(old_entity.name) or {}

        # Merge: template → old values → entity overrides
        for attr_key in template.keys():
            if attr_key not in attr_ids:
                continue

            # Priority: entity overrides > old values > template
            if attr_key in entity_overrides:
                value = entity_overrides[attr_key]
            else:
                value = old_attrs.get(attr_key, template[attr_key])

            await new_repo.set_entity_attribute(new_eid, attr_ids[attr_key], value)

        if new_eid % 50 == 0:
            logger.info(f"  ... migrated {new_eid} entities")

    logger.info(f"Migration complete! New DB at {new_db_path}")
    logger.info(f"Total entities: {len(entities)}")
    logger.info(f"Migrated: {len(entities) - skipped}, Skipped: {skipped}")

    # Replace old DB with new one
    await new_repo.close()

    os.replace(new_db_path, old_db_path)
    logger.info(f"Replaced {old_db_path} with expanded 62-attribute version")

    # Also update bundled DB
    bundled_path = "akinator/data/akinator.db"
    if os.path.exists(bundled_path):
        import shutil
        shutil.copy2(old_db_path, bundled_path)
        logger.info(f"Updated bundled DB at {bundled_path}")


if __name__ == "__main__":
    asyncio.run(migrate())
