"""Candidate Engine — FAISS vector search."""

from __future__ import annotations

import json

import faiss
import numpy as np

from akinator.config import EMBEDDING_DIM


def _normalize(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v)
    if norm > 0:
        return v / norm
    return v


class CandidateEngine:

    def __init__(self) -> None:
        self._index: faiss.IndexFlatIP | None = None
        self._id_list: list[int] = []

    def build_index(self, embeddings: dict[int, np.ndarray]) -> None:
        self._index = faiss.IndexFlatIP(EMBEDDING_DIM)
        self._id_list = []
        if embeddings:
            self.add_embeddings(embeddings)

    def add_embeddings(self, embeddings: dict[int, np.ndarray]) -> None:
        if self._index is None:
            self.build_index({})
        for eid, vec in embeddings.items():
            normed = _normalize(vec.astype(np.float32)).reshape(1, -1)
            self._index.add(normed)
            self._id_list.append(eid)

    def search(self, query: np.ndarray, k: int) -> list[tuple[int, float]]:
        if self._index is None or self._index.ntotal == 0:
            return []
        actual_k = min(k, self._index.ntotal)
        q = _normalize(query.astype(np.float32)).reshape(1, -1)
        scores, indices = self._index.search(q, actual_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            results.append((self._id_list[idx], float(score)))
        return results

    def index_size(self) -> int:
        if self._index is None:
            return 0
        return self._index.ntotal

    def save(self, index_path: str, id_map_path: str) -> None:
        if self._index is not None:
            faiss.write_index(self._index, index_path)
        with open(id_map_path, "w") as f:
            json.dump(self._id_list, f)

    def load(self, index_path: str, id_map_path: str) -> None:
        self._index = faiss.read_index(index_path)
        with open(id_map_path) as f:
            self._id_list = json.load(f)
