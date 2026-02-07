"""Candidate Engine — FAISS vector search. (Stub — TDD.)"""

from __future__ import annotations

import numpy as np


class CandidateEngine:

    def build_index(self, embeddings: dict[int, np.ndarray]) -> None:
        raise NotImplementedError

    def add_embeddings(self, embeddings: dict[int, np.ndarray]) -> None:
        raise NotImplementedError

    def search(self, query: np.ndarray, k: int) -> list[tuple[int, float]]:
        raise NotImplementedError

    def index_size(self) -> int:
        raise NotImplementedError

    def save(self, index_path: str, id_map_path: str) -> None:
        raise NotImplementedError

    def load(self, index_path: str, id_map_path: str) -> None:
        raise NotImplementedError
