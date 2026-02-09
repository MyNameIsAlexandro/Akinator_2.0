"""Category templates — default attribute values for each category.

Each entity belongs to a category. The category defines default values
for all 32 attributes. Entity-specific overrides can change individual values.
"""

TEMPLATES: dict[str, dict[str, float]] = {
    # ═══════════════════ FICTIONAL — Superheroes / Comics ═══════════════════
    "marvel_hero": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.8, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.0, "from_movie": 0.9, "from_tv_series": 0.3,
        "from_comics": 1.0, "from_usa": 1.0, "has_superpower": 0.9,
        "wears_uniform": 0.9, "era_21st_century": 1.0,
    },
    "marvel_villain": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.6, "is_alive": 0.8,
        "is_adult": 1.0, "is_villain": 1.0, "from_movie": 0.8, "from_comics": 1.0,
        "from_usa": 1.0, "has_superpower": 0.8, "wears_uniform": 0.7,
        "era_21st_century": 1.0,
    },
    "dc_hero": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.7, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.0, "from_movie": 0.8, "from_tv_series": 0.4,
        "from_comics": 1.0, "from_usa": 1.0, "has_superpower": 0.9,
        "wears_uniform": 1.0, "era_21st_century": 1.0,
    },
    "dc_villain": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.6, "is_alive": 0.8,
        "is_adult": 1.0, "is_villain": 1.0, "from_movie": 0.7, "from_comics": 1.0,
        "from_usa": 1.0, "has_superpower": 0.7, "wears_uniform": 0.6,
        "era_21st_century": 1.0,
    },

    # ═══════════════════ FICTIONAL — Star Wars ═══════════════════
    "star_wars_light": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.7, "is_alive": 0.6,
        "is_adult": 1.0, "is_villain": 0.0, "from_movie": 1.0, "from_tv_series": 0.3,
        "from_usa": 1.0, "has_superpower": 0.7, "wears_uniform": 0.6,
        "era_20th_century": 0.8,
    },
    "star_wars_dark": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.6, "is_alive": 0.5,
        "is_adult": 1.0, "is_villain": 1.0, "from_movie": 1.0, "from_usa": 1.0,
        "has_superpower": 0.8, "wears_uniform": 0.8, "era_20th_century": 0.8,
    },

    # ═══════════════════ FICTIONAL — Harry Potter ═══════════════════
    "hp_good": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.8,
        "is_adult": 0.6, "is_villain": 0.0, "from_movie": 1.0, "from_book": 1.0,
        "from_europe": 1.0, "has_superpower": 0.9, "wears_uniform": 0.7,
        "era_21st_century": 1.0,
    },
    "hp_dark": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.5,
        "is_adult": 1.0, "is_villain": 1.0, "from_movie": 1.0, "from_book": 1.0,
        "from_europe": 1.0, "has_superpower": 0.9, "wears_uniform": 0.6,
        "era_21st_century": 1.0,
    },

    # ═══════════════════ FICTIONAL — Lord of the Rings ═══════════════════
    "lotr_good": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 0.6,
        "is_adult": 1.0, "is_villain": 0.0, "from_movie": 1.0, "from_book": 1.0,
        "from_europe": 0.7, "era_20th_century": 1.0,
    },
    "lotr_evil": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.3, "is_alive": 0.5,
        "is_adult": 1.0, "is_villain": 1.0, "from_movie": 1.0, "from_book": 1.0,
        "from_europe": 0.7, "has_superpower": 0.8, "era_20th_century": 1.0,
    },

    # ═══════════════════ FICTIONAL — Disney / Pixar ═══════════════════
    "disney_princess": {
        "is_fictional": 1.0, "is_male": 0.0, "is_human": 0.8, "is_alive": 1.0,
        "is_adult": 0.7, "is_villain": 0.0, "from_movie": 1.0, "from_usa": 0.5,
        "is_wealthy": 0.8,
    },
    "disney_hero": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.7, "is_alive": 1.0,
        "is_adult": 0.8, "is_villain": 0.0, "from_movie": 1.0,
    },
    "disney_villain": {
        "is_fictional": 1.0, "is_male": 0.6, "is_human": 0.6, "is_alive": 0.7,
        "is_adult": 1.0, "is_villain": 1.0, "from_movie": 1.0,
        "has_superpower": 0.6, "is_wealthy": 0.7,
    },
    "disney_sidekick": {
        "is_fictional": 1.0, "is_male": 0.6, "is_human": 0.3, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.0, "from_movie": 1.0,
        "has_famous_catchphrase": 0.5,
    },
    "pixar_character": {
        "is_fictional": 1.0, "is_male": 0.6, "is_human": 0.4, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.0, "from_movie": 1.0, "from_usa": 1.0,
        "era_21st_century": 1.0,
    },

    # ═══════════════════ FICTIONAL — Anime ═══════════════════
    "anime_shonen_hero": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.8, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.0, "from_anime": 1.0, "from_japan": 1.0,
        "from_asia": 1.0, "has_superpower": 0.9, "wears_uniform": 0.5,
        "has_famous_catchphrase": 0.6,
    },
    "anime_shonen_villain": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.7, "is_alive": 0.7,
        "is_adult": 1.0, "is_villain": 1.0, "from_anime": 1.0, "from_japan": 1.0,
        "from_asia": 1.0, "has_superpower": 0.9,
    },
    "anime_female": {
        "is_fictional": 1.0, "is_male": 0.0, "is_human": 0.9, "is_alive": 1.0,
        "is_adult": 0.6, "is_villain": 0.0, "from_anime": 1.0, "from_japan": 1.0,
        "from_asia": 1.0, "has_superpower": 0.5,
    },
    "anime_mecha": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.0, "from_anime": 1.0, "from_japan": 1.0,
        "from_asia": 1.0, "has_superpower": 0.3, "wears_uniform": 0.7,
    },

    # ═══════════════════ FICTIONAL — Video Games ═══════════════════
    "game_hero": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.7, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.0, "from_game": 1.0,
        "has_superpower": 0.5, "wears_uniform": 0.5,
    },
    "game_villain": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 0.7,
        "is_adult": 1.0, "is_villain": 1.0, "from_game": 1.0,
        "has_superpower": 0.7,
    },
    "game_nintendo": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.0, "from_game": 1.0, "from_japan": 1.0,
        "from_asia": 1.0, "has_famous_catchphrase": 0.4,
    },
    "game_fighting": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.8, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.3, "from_game": 1.0,
        "has_superpower": 0.6, "wears_uniform": 0.7,
        "has_famous_catchphrase": 0.7,
    },

    # ═══════════════════ FICTIONAL — TV Series ═══════════════════
    "tv_drama": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.8,
        "is_adult": 1.0, "is_villain": 0.3, "from_tv_series": 1.0, "from_usa": 0.7,
        "era_21st_century": 1.0,
    },
    "tv_comedy": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.0, "from_tv_series": 1.0, "from_usa": 0.8,
        "has_famous_catchphrase": 0.6, "era_21st_century": 1.0,
    },
    "tv_fantasy": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.8, "is_alive": 0.7,
        "is_adult": 1.0, "is_villain": 0.3, "from_tv_series": 1.0, "from_book": 0.6,
        "has_superpower": 0.5, "era_medieval": 0.5,
    },
    "tv_animated": {
        "is_fictional": 1.0, "is_male": 0.6, "is_human": 0.5, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.1, "from_tv_series": 1.0,
        "has_famous_catchphrase": 0.5,
    },

    # ═══════════════════ FICTIONAL — Literature ═══════════════════
    "literature_classic": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.2, "from_book": 1.0,
        "from_movie": 0.5, "from_europe": 0.7, "era_modern": 0.7,
    },
    "literature_russian": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.2, "from_book": 1.0,
        "from_russia": 1.0, "era_modern": 0.7,
    },
    "horror_character": {
        "is_fictional": 1.0, "is_male": 0.7, "is_human": 0.4, "is_alive": 0.5,
        "is_adult": 1.0, "is_villain": 0.9, "from_movie": 1.0, "from_book": 0.6,
        "has_superpower": 0.6,
    },

    # ═══════════════════ FICTIONAL — Mythology / Fairy tales ═══════════════════
    "myth_greek": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.3, "from_book": 1.0, "from_europe": 1.0,
        "has_superpower": 0.8, "from_history": 0.5, "era_ancient": 1.0,
    },
    "myth_norse": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 0.5, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.3, "from_book": 1.0, "from_europe": 1.0,
        "has_superpower": 0.9, "era_medieval": 0.8,
    },
    "fairy_tale_russian": {
        "is_fictional": 1.0, "is_male": 0.5, "is_human": 0.5, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.3, "from_book": 1.0, "from_russia": 1.0,
        "has_superpower": 0.5, "era_medieval": 0.7,
    },
    "fairy_tale_western": {
        "is_fictional": 1.0, "is_male": 0.5, "is_human": 0.7, "is_alive": 1.0,
        "is_adult": 0.5, "is_villain": 0.2, "from_book": 1.0, "from_europe": 0.8,
        "from_movie": 0.5, "era_medieval": 0.6,
    },

    # ═══════════════════ FICTIONAL — Russian culture ═══════════════════
    "soviet_cartoon": {
        "is_fictional": 1.0, "is_male": 0.6, "is_human": 0.4, "is_alive": 1.0,
        "is_adult": 0.4, "is_villain": 0.1, "from_tv_series": 0.8, "from_movie": 0.5,
        "from_russia": 1.0, "era_20th_century": 1.0,
        "has_famous_catchphrase": 0.5,
    },
    "russian_film_character": {
        "is_fictional": 1.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.7,
        "is_adult": 1.0, "is_villain": 0.2, "from_movie": 1.0, "from_russia": 1.0,
        "era_20th_century": 0.8,
    },

    # ═══════════════════ REAL — Politicians ═══════════════════
    "politician_modern": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.2, "from_politics": 1.0,
        "is_leader": 1.0, "era_21st_century": 1.0,
    },
    "politician_historical": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.3, "from_politics": 1.0, "from_history": 1.0,
        "is_leader": 1.0,
    },
    "ruler_ancient": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.3, "from_politics": 1.0, "from_history": 1.0,
        "is_leader": 1.0, "era_ancient": 1.0, "is_wealthy": 1.0,
    },
    "ruler_medieval": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.3, "from_politics": 1.0, "from_history": 1.0,
        "is_leader": 1.0, "era_medieval": 1.0, "is_wealthy": 1.0,
    },

    # ═══════════════════ REAL — Scientists ═══════════════════
    "scientist": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.3,
        "is_adult": 1.0, "is_villain": 0.0, "from_science": 1.0,
        "from_europe": 0.6, "era_modern": 0.5,
    },
    "scientist_modern": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.5,
        "is_adult": 1.0, "is_villain": 0.0, "from_science": 1.0,
        "era_20th_century": 0.8,
    },
    "tech_leader": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.1, "from_science": 0.5,
        "from_usa": 0.8, "era_21st_century": 1.0, "is_leader": 0.9,
        "is_wealthy": 1.0,
    },

    # ═══════════════════ REAL — Musicians ═══════════════════
    "musician_rock": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.5,
        "is_adult": 1.0, "is_villain": 0.0, "from_music": 1.0,
        "from_usa": 0.4, "from_europe": 0.5, "era_20th_century": 0.8,
    },
    "musician_pop": {
        "is_fictional": 0.0, "is_male": 0.5, "is_human": 1.0, "is_alive": 0.9,
        "is_adult": 1.0, "is_villain": 0.0, "from_music": 1.0,
        "from_usa": 0.6, "era_21st_century": 0.7,
    },
    "musician_hiphop": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.8,
        "is_adult": 1.0, "is_villain": 0.1, "from_music": 1.0,
        "from_usa": 0.8, "era_21st_century": 0.7,
    },
    "musician_classical": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.0,
        "is_adult": 1.0, "is_villain": 0.0, "from_music": 1.0,
        "from_europe": 1.0, "era_modern": 0.8,
    },
    "musician_russian": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.4,
        "is_adult": 1.0, "is_villain": 0.0, "from_music": 1.0,
        "from_russia": 1.0, "era_20th_century": 0.7,
    },

    # ═══════════════════ REAL — Athletes ═══════════════════
    "athlete_football": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.9,
        "is_adult": 1.0, "is_villain": 0.0, "from_sport": 1.0,
        "from_europe": 0.5, "era_21st_century": 0.7, "is_wealthy": 0.8,
        "wears_uniform": 1.0,
    },
    "athlete_basketball": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.9,
        "is_adult": 1.0, "is_villain": 0.0, "from_sport": 1.0,
        "from_usa": 1.0, "era_21st_century": 0.7, "is_wealthy": 0.9,
        "wears_uniform": 1.0,
    },
    "athlete_tennis": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.9,
        "is_adult": 1.0, "is_villain": 0.0, "from_sport": 1.0,
        "era_21st_century": 0.7, "is_wealthy": 0.8, "wears_uniform": 0.7,
    },
    "athlete_boxing_mma": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.8,
        "is_adult": 1.0, "is_villain": 0.1, "from_sport": 1.0,
        "era_21st_century": 0.6, "is_wealthy": 0.7,
    },
    "athlete_other": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.8,
        "is_adult": 1.0, "is_villain": 0.0, "from_sport": 1.0,
        "era_21st_century": 0.6, "is_wealthy": 0.6, "wears_uniform": 0.7,
    },

    # ═══════════════════ REAL — Actors / Directors ═══════════════════
    "actor_hollywood": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.8,
        "is_adult": 1.0, "is_villain": 0.0, "from_movie": 1.0,
        "from_usa": 0.7, "era_21st_century": 0.7, "is_wealthy": 0.7,
    },
    "actor_russian": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.6,
        "is_adult": 1.0, "is_villain": 0.0, "from_movie": 0.8,
        "from_tv_series": 0.5, "from_russia": 1.0, "era_20th_century": 0.6,
    },
    "director": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.6,
        "is_adult": 1.0, "is_villain": 0.0, "from_movie": 1.0,
        "era_20th_century": 0.7, "is_wealthy": 0.6,
    },

    # ═══════════════════ REAL — Writers ═══════════════════
    "writer_western": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.3,
        "is_adult": 1.0, "is_villain": 0.0, "from_book": 1.0,
        "from_europe": 0.6, "from_usa": 0.3,
    },
    "writer_russian": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.2,
        "is_adult": 1.0, "is_villain": 0.0, "from_book": 1.0,
        "from_russia": 1.0,
    },

    # ═══════════════════ REAL — Artists ═══════════════════
    "visual_artist": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 0.2,
        "is_adult": 1.0, "is_villain": 0.0, "from_europe": 0.8,
    },

    # ═══════════════════ REAL — Internet / Modern ═══════════════════
    "youtuber": {
        "is_fictional": 0.0, "is_male": 1.0, "is_human": 1.0, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.0, "from_usa": 0.5,
        "era_21st_century": 1.0, "is_wealthy": 0.6,
    },
    "model_influencer": {
        "is_fictional": 0.0, "is_male": 0.0, "is_human": 1.0, "is_alive": 1.0,
        "is_adult": 1.0, "is_villain": 0.0, "era_21st_century": 1.0,
        "is_wealthy": 0.7,
    },
}
