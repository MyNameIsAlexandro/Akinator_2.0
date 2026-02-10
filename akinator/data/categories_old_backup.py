"""Category templates — default attribute values for each category.

Each entity belongs to a category. The category defines default values
for all 62 attributes. Entity-specific overrides can change individual values.
"""

TEMPLATES: dict[str, dict[str, float]] = {
    # ═══════════════════ FICTIONAL — Superheroes / Comics ═══════════════════
    "marvel_hero": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.8, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.0, "from_movie": 0.9, "from_tv_series": 0.3,
        "from_comics": 1.0, "from_usa": 1.0, "has_superpower": 0.9,
        "wears_uniform": 0.9, "era_21st_century": 1.0,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.3,
        "from_business": 0.2, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.9, "is_comedic": 0.3, "is_dark_brooding": 0.3,
        "is_child_friendly": 0.7,
        # Visual traits
        "wears_mask": 0.5, "has_armor": 0.4, "has_facial_hair": 0.3,
    },
    "marvel_villain": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.6, "is_alive": 0.8,
        "is_adult": 1.0, "is_villain": 1.0, "from_movie": 0.8, "from_comics": 1.0,
        "from_usa": 1.0, "has_superpower": 0.8, "wears_uniform": 0.7,
        "era_21st_century": 1.0,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.2,
        "from_business": 0.3, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.7, "is_comedic": 0.2, "is_dark_brooding": 0.6,
        "is_child_friendly": 0.5,
        # Visual traits
        "wears_mask": 0.4, "has_armor": 0.5, "has_facial_hair": 0.3,
    },
    "dc_hero": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.7, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.0, "from_movie": 0.8, "from_tv_series": 0.4,
        "from_comics": 1.0, "from_usa": 1.0, "has_superpower": 0.9,
        "wears_uniform": 1.0, "era_21st_century": 1.0,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.2,
        "from_business": 0.3, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.9, "is_comedic": 0.2, "is_dark_brooding": 0.4,
        "is_child_friendly": 0.6,
        # Visual traits
        "wears_mask": 0.7, "has_armor": 0.3, "has_facial_hair": 0.2,
    },
    "dc_villain": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.6, "is_alive": 0.8,
        "is_adult": 1.0, "is_villain": 1.0, "from_movie": 0.7, "from_comics": 1.0,
        "from_usa": 1.0, "has_superpower": 0.7, "wears_uniform": 0.6,
        "era_21st_century": 1.0,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.2,
        "from_business": 0.4, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.6, "is_comedic": 0.3, "is_dark_brooding": 0.7,
        "is_child_friendly": 0.4,
        # Visual traits
        "wears_mask": 0.5, "has_armor": 0.4, "has_facial_hair": 0.3,
    },

    # ═══════════════════ FICTIONAL — Star Wars ═══════════════════
    "star_wars_light": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.7, "is_alive": 0.6,
        "is_adult": 1.0, "is_villain": 0.0, "from_movie": 1.0, "from_tv_series": 0.3,
        "from_usa": 1.0, "has_superpower": 0.7, "wears_uniform": 0.6,
        "era_20th_century": 0.8,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.2, "from_military": 0.6,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.3, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.8, "is_comedic": 0.1, "is_dark_brooding": 0.3,
        "is_child_friendly": 0.8,
        # Visual traits
        "wears_mask": 0.2, "has_armor": 0.4, "has_facial_hair": 0.5,
    },
    "star_wars_dark": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.6, "is_alive": 0.5,
        "is_adult": 1.0, "is_villain": 1.0, "from_movie": 1.0, "from_usa": 1.0,
        "has_superpower": 0.8, "wears_uniform": 0.8, "era_20th_century": 0.8,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.1, "from_military": 0.7,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.2, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.7, "is_comedic": 0.0, "is_dark_brooding": 0.9,
        "is_child_friendly": 0.5,
        # Visual traits
        "wears_mask": 0.6, "has_armor": 0.7, "has_facial_hair": 0.3,
    },

    # ═══════════════════ FICTIONAL — Harry Potter ═══════════════════
    "hp_good": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.8,
        "is_adult": 0.6, "is_villain": 0.0, "from_movie": 1.0, "from_book": 1.0,
        "from_europe": 1.0, "has_superpower": 0.9, "wears_uniform": 0.7,
        "era_21st_century": 1.0,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 1.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.5, "is_comedic": 0.3, "is_dark_brooding": 0.2,
        "is_child_friendly": 0.9,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.2,
    },
    "hp_dark": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.5,
        "is_adult": 1.0, "is_villain": 1.0, "from_movie": 1.0, "from_book": 1.0,
        "from_europe": 1.0, "has_superpower": 0.9, "wears_uniform": 0.6,
        "era_21st_century": 1.0,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 1.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.3, "is_comedic": 0.1, "is_dark_brooding": 0.9,
        "is_child_friendly": 0.6,
        # Visual traits
        "wears_mask": 0.1, "has_armor": 0.0, "has_facial_hair": 0.3,
    },

    # ═══════════════════ FICTIONAL — Lord of the Rings ═══════════════════
    "lotr_good": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 0.6,
        "is_adult": 1.0, "is_villain": 0.0, "from_movie": 1.0, "from_book": 1.0,
        "from_europe": 0.7, "era_20th_century": 1.0,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 1.0, "from_philosophy": 0.0, "from_military": 0.5,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.7, "is_comedic": 0.2, "is_dark_brooding": 0.3,
        "is_child_friendly": 0.7,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.5, "has_facial_hair": 0.6,
    },
    "lotr_evil": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.3, "is_alive": 0.5,
        "is_adult": 1.0, "is_villain": 1.0, "from_movie": 1.0, "from_book": 1.0,
        "from_europe": 0.7, "has_superpower": 0.8, "era_20th_century": 1.0,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 1.0, "from_philosophy": 0.0, "from_military": 0.6,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.5, "is_comedic": 0.0, "is_dark_brooding": 0.9,
        "is_child_friendly": 0.4,
        # Visual traits
        "wears_mask": 0.3, "has_armor": 0.7, "has_facial_hair": 0.2,
    },

    # ═══════════════════ FICTIONAL — Disney / Pixar ═══════════════════
    "disney_princess": {
        "is_fictional": 1.0, "is_male": 0.0, "is_human": 0.8, "is_alive": 1.0,
        "is_adult": 0.7, "is_villain": 0.0, "from_movie": 1.0, "from_usa": 0.5,
        "is_wealthy": 0.8,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.1, "from_south_america": 0.0, "from_middle_east": 0.2,
        "from_oceania": 0.2, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.5, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.0, "from_fashion": 0.4, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.3, "is_comedic": 0.2, "is_dark_brooding": 0.0,
        "is_child_friendly": 1.0,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.0,
    },
    "disney_hero": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.7, "is_alive": 1.0,
        "is_adult": 0.8, "is_villain": 0.0, "from_movie": 1.0,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.1, "from_south_america": 0.1, "from_middle_east": 0.2,
        "from_oceania": 0.2, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.4, "from_philosophy": 0.0, "from_military": 0.2,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.6, "is_comedic": 0.3, "is_dark_brooding": 0.1,
        "is_child_friendly": 1.0,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.1, "has_facial_hair": 0.2,
    },
    "disney_villain": {
        "is_fictional": 1.0, "is_male": 0.6, "is_human": 0.6, "is_alive": 0.7,
        "is_adult": 1.0, "is_villain": 1.0, "from_movie": 1.0,
        "has_superpower": 0.6, "is_wealthy": 0.7,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.1,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.4, "from_philosophy": 0.0, "from_military": 0.1,
        "from_business": 0.2, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.2, "is_comedic": 0.4, "is_dark_brooding": 0.6,
        "is_child_friendly": 0.7,
        # Visual traits
        "wears_mask": 0.1, "has_armor": 0.1, "has_facial_hair": 0.3,
    },
    "disney_sidekick": {
        "is_fictional": 1.0, "is_male": 0.6, "is_human": 0.3, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.0, "from_movie": 1.0,
        "has_famous_catchphrase": 0.5,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.1, "from_south_america": 0.1, "from_middle_east": 0.1,
        "from_oceania": 0.1, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.3, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.2, "is_comedic": 0.8, "is_dark_brooding": 0.0,
        "is_child_friendly": 1.0,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.2,
    },
    "pixar_character": {
        "is_fictional": 1.0, "is_male": 0.6, "is_human": 0.4, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.0, "from_movie": 1.0, "from_usa": 1.0,
        "era_21st_century": 1.0,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.1, "from_middle_east": 0.0,
        "from_oceania": 0.1, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.3, "is_comedic": 0.6, "is_dark_brooding": 0.1,
        "is_child_friendly": 1.0,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.1,
    },

    # ═══════════════════ FICTIONAL — Anime ═══════════════════
    "anime_shonen_hero": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.8, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.0, "from_anime": 1.0, "from_japan": 1.0,
        "from_asia": 1.0, "has_superpower": 0.9, "wears_uniform": 0.5,
        "has_famous_catchphrase": 0.6,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.1, "from_military": 0.3,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.9, "is_comedic": 0.3, "is_dark_brooding": 0.2,
        "is_child_friendly": 0.8,
        # Visual traits
        "wears_mask": 0.1, "has_armor": 0.1, "has_facial_hair": 0.1,
    },
    "anime_shonen_villain": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.7, "is_alive": 0.7,
        "is_adult": 1.0, "is_villain": 1.0, "from_anime": 1.0, "from_japan": 1.0,
        "from_asia": 1.0, "has_superpower": 0.9,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.1, "from_military": 0.3,
        "from_business": 0.1, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.5, "is_comedic": 0.2, "is_dark_brooding": 0.7,
        "is_child_friendly": 0.6,
        # Visual traits
        "wears_mask": 0.2, "has_armor": 0.2, "has_facial_hair": 0.3,
    },
    "anime_female": {
        "is_fictional": 1.0, "is_male": 0.0, "is_human": 0.9, "is_alive": 1.0,
        "is_adult": 0.6, "is_villain": 0.0, "from_anime": 1.0, "from_japan": 1.0,
        "from_asia": 1.0, "has_superpower": 0.5,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.1,
        "from_business": 0.0, "from_fashion": 0.1, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.4, "is_comedic": 0.3, "is_dark_brooding": 0.2,
        "is_child_friendly": 0.7,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.1, "has_facial_hair": 0.0,
    },
    "anime_mecha": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.0, "from_anime": 1.0, "from_japan": 1.0,
        "from_asia": 1.0, "has_superpower": 0.3, "wears_uniform": 0.7,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.5,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.8, "is_comedic": 0.2, "is_dark_brooding": 0.3,
        "is_child_friendly": 0.7,
        # Visual traits
        "wears_mask": 0.1, "has_armor": 0.8, "has_facial_hair": 0.1,
    },

    # ═══════════════════ FICTIONAL — Video Games ═══════════════════
    "game_hero": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.7, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.0, "from_game": 1.0,
        "has_superpower": 0.5, "wears_uniform": 0.5,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.4,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.9, "is_comedic": 0.2, "is_dark_brooding": 0.3,
        "is_child_friendly": 0.6,
        # Visual traits
        "wears_mask": 0.2, "has_armor": 0.5, "has_facial_hair": 0.3,
    },
    "game_villain": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 0.7,
        "is_adult": 1.0, "is_villain": 1.0, "from_game": 1.0,
        "has_superpower": 0.7,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.3,
        "from_business": 0.1, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.4, "is_comedic": 0.1, "is_dark_brooding": 0.8,
        "is_child_friendly": 0.4,
        # Visual traits
        "wears_mask": 0.3, "has_armor": 0.6, "has_facial_hair": 0.4,
    },
    "game_nintendo": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.0, "from_game": 1.0, "from_japan": 1.0,
        "from_asia": 1.0, "has_famous_catchphrase": 0.4,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.7, "is_comedic": 0.6, "is_dark_brooding": 0.0,
        "is_child_friendly": 1.0,
        # Visual traits
        "wears_mask": 0.1, "has_armor": 0.1, "has_facial_hair": 0.4,
    },
    "game_fighting": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.8, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.3, "from_game": 1.0,
        "has_superpower": 0.6, "wears_uniform": 0.7,
        "has_famous_catchphrase": 0.7,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.1, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.2,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.5,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.8, "is_comedic": 0.2, "is_dark_brooding": 0.3,
        "is_child_friendly": 0.5,
        # Visual traits
        "wears_mask": 0.3, "has_armor": 0.3, "has_facial_hair": 0.4,
    },

    # ═══════════════════ FICTIONAL — TV Series ═══════════════════
    "tv_drama": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.8,
        "is_adult": 1.0, "is_villain": 0.3, "from_tv_series": 1.0, "from_usa": 0.7,
        "era_21st_century": 1.0,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.2,
        "from_business": 0.3, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.4, "is_comedic": 0.1, "is_dark_brooding": 0.4,
        "is_child_friendly": 0.3,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.4,
    },
    "tv_comedy": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.0, "from_tv_series": 1.0, "from_usa": 0.8,
        "has_famous_catchphrase": 0.6, "era_21st_century": 1.0,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.2, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.1, "is_comedic": 0.9, "is_dark_brooding": 0.0,
        "is_child_friendly": 0.5,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.3,
    },
    "tv_fantasy": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.8, "is_alive": 0.7,
        "is_adult": 1.0, "is_villain": 0.3, "from_tv_series": 1.0, "from_book": 0.6,
        "has_superpower": 0.5, "era_medieval": 0.5,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.6, "from_philosophy": 0.0, "from_military": 0.4,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.6, "is_comedic": 0.2, "is_dark_brooding": 0.4,
        "is_child_friendly": 0.5,
        # Visual traits
        "wears_mask": 0.1, "has_armor": 0.6, "has_facial_hair": 0.5,
    },
    "tv_animated": {
        "is_fictional": 1.0, "is_male": 0.6, "is_human": 0.5, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.1, "from_tv_series": 1.0,
        "has_famous_catchphrase": 0.5,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.3, "is_comedic": 0.7, "is_dark_brooding": 0.0,
        "is_child_friendly": 0.8,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.2,
    },

    # ═══════════════════ FICTIONAL — Literature ═══════════════════
    "literature_classic": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.2, "from_book": 1.0,
        "from_movie": 0.5, "from_europe": 0.7, "era_modern": 0.7,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 1.0, "from_philosophy": 0.2, "from_military": 0.2,
        "from_business": 0.1, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.3, "is_comedic": 0.2, "is_dark_brooding": 0.4,
        "is_child_friendly": 0.4,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.1, "has_facial_hair": 0.5,
    },
    "literature_russian": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.2, "from_book": 1.0,
        "from_russia": 1.0, "era_modern": 0.7,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 1.0, "from_philosophy": 0.3, "from_military": 0.2,
        "from_business": 0.1, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.2, "is_comedic": 0.2, "is_dark_brooding": 0.5,
        "is_child_friendly": 0.3,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.6,
    },
    "horror_character": {
        "is_fictional": 1.0, "is_male": 0.7, "is_human": 0.4, "is_alive": 0.5,
        "is_adult": 1.0, "is_villain": 0.9, "from_movie": 1.0, "from_book": 0.6,
        "has_superpower": 0.6,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.6, "from_philosophy": 0.0, "from_military": 0.1,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.1, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.3, "is_comedic": 0.0, "is_dark_brooding": 1.0,
        "is_child_friendly": 0.0,
        # Visual traits
        "wears_mask": 0.6, "has_armor": 0.0, "has_facial_hair": 0.2,
    },

    # ═══════════════════ FICTIONAL — Mythology / Fairy tales ═══════════════════
    "myth_greek": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.3, "from_book": 1.0, "from_europe": 1.0,
        "has_superpower": 0.8, "from_history": 0.5, "era_ancient": 1.0,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.1,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.8, "from_philosophy": 0.2, "from_military": 0.5,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.6, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.6, "is_comedic": 0.1, "is_dark_brooding": 0.3,
        "is_child_friendly": 0.5,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.6, "has_facial_hair": 0.7,
    },
    "myth_norse": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.3, "from_book": 1.0, "from_europe": 1.0,
        "has_superpower": 0.9, "era_medieval": 0.8,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.8, "from_philosophy": 0.1, "from_military": 0.7,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.7, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.7, "is_comedic": 0.1, "is_dark_brooding": 0.4,
        "is_child_friendly": 0.5,
        # Visual traits
        "wears_mask": 0.1, "has_armor": 0.7, "has_facial_hair": 0.8,
    },
    "fairy_tale_russian": {
        "is_fictional": 1.0, "is_male": 0.5, "is_human": 0.5, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.3, "from_book": 1.0, "from_russia": 1.0,
        "has_superpower": 0.5, "era_medieval": 0.7,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 1.0, "from_philosophy": 0.0, "from_military": 0.2,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.1, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.4, "is_comedic": 0.3, "is_dark_brooding": 0.2,
        "is_child_friendly": 0.8,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.2, "has_facial_hair": 0.3,
    },
    "fairy_tale_western": {
        "is_fictional": 1.0, "is_male": 0.5, "is_human": 0.7, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.2, "from_book": 1.0, "from_europe": 0.8,
        "from_movie": 0.5, "era_medieval": 0.6,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.1,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 1.0, "from_philosophy": 0.0, "from_military": 0.1,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.4, "is_comedic": 0.3, "is_dark_brooding": 0.1,
        "is_child_friendly": 0.9,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.1, "has_facial_hair": 0.2,
    },

    # ═══════════════════ FICTIONAL — Russian culture ═══════════════════
    "soviet_cartoon": {
        "is_fictional": 1.0, "is_male": 0.6, "is_human": 0.4, "is_alive": 1.0,
        "is_adult": 0.4, "is_villain": 0.1, "from_tv_series": 0.8, "from_movie": 0.5,
        "from_russia": 1.0, "era_20th_century": 1.0,
        "has_famous_catchphrase": 0.5,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.3, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.2, "is_comedic": 0.6, "is_dark_brooding": 0.0,
        "is_child_friendly": 1.0,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.2,
    },
    "russian_film_character": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.7,
        "is_adult": 1.0, "is_villain": 0.2, "from_movie": 1.0, "from_russia": 1.0,
        "era_20th_century": 0.8,
        # Birth decades (fictional)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.2, "from_philosophy": 0.0, "from_military": 0.3,
        "from_business": 0.1, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.4, "is_comedic": 0.3, "is_dark_brooding": 0.3,
        "is_child_friendly": 0.5,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.1, "has_facial_hair": 0.5,
    },

    # ═══════════════════ REAL — Politicians ═══════════════════
    "politician_modern": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.2, "from_politics": 1.0,
        "is_leader": 1.0, "era_21st_century": 1.0,
        # Birth decades (modern politicians - typically 1940s-1960s)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.3, "born_1950s": 0.4, "born_1960s": 0.3, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.1, "from_south_america": 0.1, "from_middle_east": 0.1,
        "from_oceania": 0.0, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.2,
        "from_business": 0.3, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.0, "is_dark_brooding": 0.1,
        "is_child_friendly": 0.5,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.3,
    },
    "politician_historical": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.3, "from_politics": 1.0, "from_history": 1.0,
        "is_leader": 1.0,
        # Birth decades (historical - pre-1940s)
        "born_1900s": 0.2, "born_1910s": 0.2, "born_1920s": 0.2, "born_1930s": 0.1,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.1, "from_south_america": 0.1, "from_middle_east": 0.1,
        "from_oceania": 0.0, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.1, "from_philosophy": 0.1, "from_military": 0.5,
        "from_business": 0.1, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.0, "is_dark_brooding": 0.2,
        "is_child_friendly": 0.5,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.6,
    },
    "ruler_ancient": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.3, "from_politics": 1.0, "from_history": 1.0,
        "is_leader": 1.0, "era_ancient": 1.0, "is_wealthy": 1.0,
        # Birth decades (ancient - all 0.0)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.2, "from_south_america": 0.0, "from_middle_east": 0.3,
        "from_oceania": 0.0, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.2, "from_military": 0.8,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.3, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.3, "is_comedic": 0.0, "is_dark_brooding": 0.3,
        "is_child_friendly": 0.6,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.5, "has_facial_hair": 0.7,
    },
    "ruler_medieval": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.3, "from_politics": 1.0, "from_history": 1.0,
        "is_leader": 1.0, "era_medieval": 1.0, "is_wealthy": 1.0,
        # Birth decades (medieval - all 0.0)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.1, "from_south_america": 0.0, "from_middle_east": 0.2,
        "from_oceania": 0.0, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.1, "from_military": 0.8,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.4, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.3, "is_comedic": 0.0, "is_dark_brooding": 0.3,
        "is_child_friendly": 0.6,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.7, "has_facial_hair": 0.7,
    },

    # ═══════════════════ REAL — Scientists ═══════════════════
    "scientist": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.3,
        "is_adult": 1.0, "is_villain": 0.0, "from_science": 1.0,
        "from_europe": 0.6, "era_modern": 0.5,
        # Birth decades (historical scientists - 1900s-1930s)
        "born_1900s": 0.3, "born_1910s": 0.2, "born_1920s": 0.2, "born_1930s": 0.1,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.3, "from_military": 0.1,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.0, "is_dark_brooding": 0.1,
        "is_child_friendly": 0.8,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.6,
    },
    "scientist_modern": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.5,
        "is_adult": 1.0, "is_villain": 0.0, "from_science": 1.0,
        "era_20th_century": 0.8,
        # Birth decades (modern scientists - 1920s-1950s)
        "born_1900s": 0.1, "born_1910s": 0.2, "born_1920s": 0.3, "born_1930s": 0.3,
        "born_1940s": 0.1, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.2, "from_military": 0.2,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.0, "is_dark_brooding": 0.1,
        "is_child_friendly": 0.8,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.5,
    },
    "tech_leader": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.1, "from_science": 0.5,
        "from_usa": 0.8, "era_21st_century": 1.0, "is_leader": 0.9,
        "is_wealthy": 1.0,
        # Birth decades (tech leaders - 1950s-1970s)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.1, "born_1950s": 0.3, "born_1960s": 0.3, "born_1970s": 0.3,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.1, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 1.0, "from_fashion": 0.0, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.8,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.0, "is_dark_brooding": 0.0,
        "is_child_friendly": 0.7,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.2,
    },

    # ═══════════════════ REAL — Musicians ═══════════════════
    "musician_rock": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.5,
        "is_adult": 1.0, "is_villain": 0.0, "from_music": 1.0,
        "from_usa": 0.4, "from_europe": 0.5, "era_20th_century": 0.8,
        # Birth decades (rock musicians - 1940s-1960s)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.1,
        "born_1940s": 0.3, "born_1950s": 0.3, "born_1960s": 0.2, "born_1970s": 0.1,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.1, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.1, "from_fashion": 0.2, "from_art": 0.3,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.1, "is_dark_brooding": 0.3,
        "is_child_friendly": 0.5,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.6,
    },
    "musician_pop": {
        "is_fictional": 0.0, "is_male": 0.5, "is_human": 1.0, "is_alive": 0.9,
        "is_adult": 1.0, "is_villain": 0.0, "from_music": 1.0,
        "from_usa": 0.6, "era_21st_century": 0.7,
        # Birth decades (pop musicians - 1960s-1990s)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.1, "born_1950s": 0.2, "born_1960s": 0.2, "born_1970s": 0.2,
        "born_1980s": 0.2, "born_1990s": 0.1,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.1, "from_middle_east": 0.0,
        "from_oceania": 0.1, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.3, "from_fashion": 0.5, "from_art": 0.2,
        "from_religion": 0.0, "from_internet": 0.3,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.1, "is_dark_brooding": 0.1,
        "is_child_friendly": 0.7,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.2,
    },
    "musician_hiphop": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.8,
        "is_adult": 1.0, "is_villain": 0.1, "from_music": 1.0,
        "from_usa": 0.8, "era_21st_century": 0.7,
        # Birth decades (hip-hop musicians - 1960s-1990s)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.1, "born_1960s": 0.2, "born_1970s": 0.3,
        "born_1980s": 0.3, "born_1990s": 0.1,
        # Expanded geography
        "from_africa": 0.1, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.5, "from_fashion": 0.6, "from_art": 0.3,
        "from_religion": 0.0, "from_internet": 0.4,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.2, "is_dark_brooding": 0.2,
        "is_child_friendly": 0.4,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.5,
    },
    "musician_classical": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.0, "from_music": 1.0,
        "from_europe": 1.0, "era_modern": 0.8,
        # Birth decades (classical musicians - historical, all 0.0)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.1, "from_military": 0.0,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.6,
        "from_religion": 0.1, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.0, "is_dark_brooding": 0.3,
        "is_child_friendly": 0.8,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.6,
    },
    "musician_russian": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.4,
        "is_adult": 1.0, "is_villain": 0.0, "from_music": 1.0,
        "from_russia": 1.0, "era_20th_century": 0.7,
        # Birth decades (Russian musicians - 1940s-1970s)
        "born_1900s": 0.1, "born_1910s": 0.1, "born_1920s": 0.1, "born_1930s": 0.1,
        "born_1940s": 0.2, "born_1950s": 0.2, "born_1960s": 0.1, "born_1970s": 0.1,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.4,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.1, "is_dark_brooding": 0.2,
        "is_child_friendly": 0.7,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.4,
    },

    # ═══════════════════ REAL — Athletes ═══════════════════
    "athlete_football": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.9,
        "is_adult": 1.0, "is_villain": 0.0, "from_sport": 1.0,
        "from_europe": 0.5, "era_21st_century": 0.7, "is_wealthy": 0.8,
        "wears_uniform": 1.0,
        # Birth decades (football/soccer players - 1970s-1990s)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.1, "born_1960s": 0.1, "born_1970s": 0.2,
        "born_1980s": 0.4, "born_1990s": 0.2,
        # Expanded geography
        "from_africa": 0.2, "from_south_america": 0.3, "from_middle_east": 0.1,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.2, "from_fashion": 0.2, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.2,
        # Character traits
        "is_action_hero": 0.1, "is_comedic": 0.1, "is_dark_brooding": 0.0,
        "is_child_friendly": 0.8,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.4,
    },
    "athlete_basketball": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.9,
        "is_adult": 1.0, "is_villain": 0.0, "from_sport": 1.0,
        "from_usa": 1.0, "era_21st_century": 0.7, "is_wealthy": 0.9,
        "wears_uniform": 1.0,
        # Birth decades (basketball players - 1960s-1990s)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.1, "born_1960s": 0.2, "born_1970s": 0.2,
        "born_1980s": 0.3, "born_1990s": 0.2,
        # Expanded geography
        "from_africa": 0.1, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.3, "from_fashion": 0.3, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.2,
        # Character traits
        "is_action_hero": 0.1, "is_comedic": 0.1, "is_dark_brooding": 0.0,
        "is_child_friendly": 0.9,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.3,
    },
    "athlete_tennis": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.9,
        "is_adult": 1.0, "is_villain": 0.0, "from_sport": 1.0,
        "era_21st_century": 0.7, "is_wealthy": 0.8, "wears_uniform": 0.7,
        # Birth decades (tennis players - 1970s-1990s)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.1, "born_1960s": 0.1, "born_1970s": 0.2,
        "born_1980s": 0.4, "born_1990s": 0.2,
        # Expanded geography
        "from_africa": 0.1, "from_south_america": 0.1, "from_middle_east": 0.0,
        "from_oceania": 0.2, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.3, "from_fashion": 0.4, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.1,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.0, "is_dark_brooding": 0.0,
        "is_child_friendly": 0.9,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.3,
    },
    "athlete_boxing_mma": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.8,
        "is_adult": 1.0, "is_villain": 0.1, "from_sport": 1.0,
        "era_21st_century": 0.6, "is_wealthy": 0.7,
        # Birth decades (boxers/MMA - 1960s-1990s)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.1, "born_1950s": 0.1, "born_1960s": 0.2, "born_1970s": 0.3,
        "born_1980s": 0.2, "born_1990s": 0.1,
        # Expanded geography
        "from_africa": 0.2, "from_south_america": 0.1, "from_middle_east": 0.1,
        "from_oceania": 0.1, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.2,
        "from_business": 0.2, "from_fashion": 0.1, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.1,
        # Character traits
        "is_action_hero": 0.2, "is_comedic": 0.1, "is_dark_brooding": 0.2,
        "is_child_friendly": 0.5,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.5,
    },
    "athlete_other": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.8,
        "is_adult": 1.0, "is_villain": 0.0, "from_sport": 1.0,
        "era_21st_century": 0.6, "is_wealthy": 0.6, "wears_uniform": 0.7,
        # Birth decades (other athletes - 1960s-1990s)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.1, "born_1950s": 0.1, "born_1960s": 0.2, "born_1970s": 0.2,
        "born_1980s": 0.3, "born_1990s": 0.1,
        # Expanded geography
        "from_africa": 0.1, "from_south_america": 0.1, "from_middle_east": 0.1,
        "from_oceania": 0.1, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.1,
        "from_business": 0.2, "from_fashion": 0.1, "from_art": 0.0,
        "from_religion": 0.0, "from_internet": 0.1,
        # Character traits
        "is_action_hero": 0.1, "is_comedic": 0.1, "is_dark_brooding": 0.0,
        "is_child_friendly": 0.8,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.1, "has_facial_hair": 0.3,
    },

    # ═══════════════════ REAL — Actors / Directors ═══════════════════
    "actor_hollywood": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.8,
        "is_adult": 1.0, "is_villain": 0.0, "from_movie": 1.0,
        "from_usa": 0.7, "era_21st_century": 0.7, "is_wealthy": 0.7,
        # Birth decades (Hollywood actors - 1950s-1980s)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.1,
        "born_1940s": 0.1, "born_1950s": 0.2, "born_1960s": 0.3, "born_1970s": 0.2,
        "born_1980s": 0.1, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.1, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.2, "from_fashion": 0.2, "from_art": 0.5,
        "from_religion": 0.0, "from_internet": 0.1,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.2, "is_dark_brooding": 0.1,
        "is_child_friendly": 0.7,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.4,
    },
    "actor_russian": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.6,
        "is_adult": 1.0, "is_villain": 0.0, "from_movie": 0.8,
        "from_tv_series": 0.5, "from_russia": 1.0, "era_20th_century": 0.6,
        # Birth decades (Russian actors - 1930s-1970s)
        "born_1900s": 0.1, "born_1910s": 0.1, "born_1920s": 0.1, "born_1930s": 0.2,
        "born_1940s": 0.2, "born_1950s": 0.2, "born_1960s": 0.1, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.1,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.5,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.3, "is_dark_brooding": 0.2,
        "is_child_friendly": 0.7,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.5,
    },
    "director": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.6,
        "is_adult": 1.0, "is_villain": 0.0, "from_movie": 1.0,
        "era_20th_century": 0.7, "is_wealthy": 0.6,
        # Birth decades (directors - 1930s-1960s)
        "born_1900s": 0.1, "born_1910s": 0.1, "born_1920s": 0.1, "born_1930s": 0.2,
        "born_1940s": 0.2, "born_1950s": 0.2, "born_1960s": 0.1, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.1, "from_philosophy": 0.1, "from_military": 0.0,
        "from_business": 0.3, "from_fashion": 0.0, "from_art": 0.8,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.1, "is_dark_brooding": 0.2,
        "is_child_friendly": 0.6,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.5,
    },

    # ═══════════════════ REAL — Writers ═══════════════════
    "writer_western": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.3,
        "is_adult": 1.0, "is_villain": 0.0, "from_book": 1.0,
        "from_europe": 0.6, "from_usa": 0.3,
        # Birth decades (Western writers - 1900s-1940s)
        "born_1900s": 0.2, "born_1910s": 0.2, "born_1920s": 0.2, "born_1930s": 0.2,
        "born_1940s": 0.1, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.1, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 1.0, "from_philosophy": 0.3, "from_military": 0.1,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.3,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.1, "is_dark_brooding": 0.2,
        "is_child_friendly": 0.6,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.5,
    },
    "writer_russian": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.2,
        "is_adult": 1.0, "is_villain": 0.0, "from_book": 1.0,
        "from_russia": 1.0,
        # Birth decades (Russian writers - 1900s-1940s)
        "born_1900s": 0.2, "born_1910s": 0.2, "born_1920s": 0.2, "born_1930s": 0.2,
        "born_1940s": 0.1, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.0, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 1.0, "from_philosophy": 0.4, "from_military": 0.1,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 0.2,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.1, "is_dark_brooding": 0.3,
        "is_child_friendly": 0.5,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.7,
    },

    # ═══════════════════ REAL — Artists ═══════════════════
    "visual_artist": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.2,
        "is_adult": 1.0, "is_villain": 0.0, "from_europe": 0.8,
        # Birth decades (visual artists - historical, mostly pre-1940s)
        "born_1900s": 0.2, "born_1910s": 0.2, "born_1920s": 0.1, "born_1930s": 0.1,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.0,
        "born_1980s": 0.0, "born_1990s": 0.0,
        # Expanded geography
        "from_africa": 0.0, "from_south_america": 0.1, "from_middle_east": 0.0,
        "from_oceania": 0.0, "from_china": 0.0,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.2, "from_military": 0.0,
        "from_business": 0.0, "from_fashion": 0.0, "from_art": 1.0,
        "from_religion": 0.0, "from_internet": 0.0,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.0, "is_dark_brooding": 0.3,
        "is_child_friendly": 0.7,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.6,
    },

    # ═══════════════════ REAL — Internet / Modern ═══════════════════
    "youtuber": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.0, "from_usa": 0.5,
        "era_21st_century": 1.0, "is_wealthy": 0.6,
        # Birth decades (YouTubers - 1980s-1990s)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.1,
        "born_1980s": 0.4, "born_1990s": 0.5,
        # Expanded geography
        "from_africa": 0.1, "from_south_america": 0.1, "from_middle_east": 0.1,
        "from_oceania": 0.1, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.3, "from_fashion": 0.2, "from_art": 0.2,
        "from_religion": 0.0, "from_internet": 1.0,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.5, "is_dark_brooding": 0.0,
        "is_child_friendly": 0.6,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.4,
    },
    "model_influencer": {
        "is_fictional": 0.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.0, "era_21st_century": 1.0,
        "is_wealthy": 0.7,
        # Birth decades (models/influencers - 1980s-1990s)
        "born_1900s": 0.0, "born_1910s": 0.0, "born_1920s": 0.0, "born_1930s": 0.0,
        "born_1940s": 0.0, "born_1950s": 0.0, "born_1960s": 0.0, "born_1970s": 0.1,
        "born_1980s": 0.4, "born_1990s": 0.5,
        # Expanded geography
        "from_africa": 0.1, "from_south_america": 0.2, "from_middle_east": 0.1,
        "from_oceania": 0.1, "from_china": 0.1,
        # Additional professions
        "from_literature": 0.0, "from_philosophy": 0.0, "from_military": 0.0,
        "from_business": 0.4, "from_fashion": 1.0, "from_art": 0.2,
        "from_religion": 0.0, "from_internet": 0.9,
        # Character traits
        "is_action_hero": 0.0, "is_comedic": 0.2, "is_dark_brooding": 0.0,
        "is_child_friendly": 0.6,
        # Visual traits
        "wears_mask": 0.0, "has_armor": 0.0, "has_facial_hair": 0.0,
    },
}
