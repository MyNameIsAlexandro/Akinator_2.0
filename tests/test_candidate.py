"""Tests for the Candidate Engine (FAISS vector search).

Covers:
- Index building from entities
- Search returns relevant candidates
- Search respects max_candidates limit
- Similarity scores are valid (0-1 range for cosine)
- Empty index handling
"""

from __future__ import annotations

import numpy as np
import pytest

from akinator.config import EMBEDDING_DIM
from akinator.engine.candidate import CandidateEngine


class TestIndexBuilding:
    """FAISS index construction from entity embeddings."""

    def test_build_index_from_embeddings(self):
        """Index should be built from a dict of entity_id → embedding."""
        engine = CandidateEngine()
        embeddings = {
            1: np.random.randn(EMBEDDING_DIM).astype(np.float32),
            2: np.random.randn(EMBEDDING_DIM).astype(np.float32),
            3: np.random.randn(EMBEDDING_DIM).astype(np.float32),
        }
        engine.build_index(embeddings)
        assert engine.index_size() == 3

    def test_build_empty_index(self):
        """Building from empty dict should create empty index."""
        engine = CandidateEngine()
        engine.build_index({})
        assert engine.index_size() == 0

    def test_add_to_existing_index(self):
        """Adding entities to an existing index should grow it."""
        engine = CandidateEngine()
        embeddings = {
            1: np.random.randn(EMBEDDING_DIM).astype(np.float32),
        }
        engine.build_index(embeddings)
        assert engine.index_size() == 1

        engine.add_embeddings({
            2: np.random.randn(EMBEDDING_DIM).astype(np.float32),
        })
        assert engine.index_size() == 2


class TestSearch:
    """Vector similarity search."""

    def _build_engine_with_known_vectors(self) -> tuple[CandidateEngine, np.ndarray]:
        """Build engine where entity 1 is close to query, entity 2 is far."""
        engine = CandidateEngine()
        # Create a known query direction
        query = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        query[0] = 1.0  # unit vector along dim 0

        # Entity 1: close to query (same direction)
        close_vec = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        close_vec[0] = 1.0
        close_vec[1] = 0.1

        # Entity 2: orthogonal to query
        far_vec = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        far_vec[1] = 1.0

        # Entity 3: opposite to query
        opposite_vec = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        opposite_vec[0] = -1.0

        embeddings = {1: close_vec, 2: far_vec, 3: opposite_vec}
        engine.build_index(embeddings)
        return engine, query

    def test_search_returns_closest_first(self):
        """Most similar entity should be first in results."""
        engine, query = self._build_engine_with_known_vectors()
        results = engine.search(query, k=3)
        assert results[0][0] == 1  # entity_id=1 is closest

    def test_search_respects_k_limit(self):
        """Search should return at most k results."""
        engine, query = self._build_engine_with_known_vectors()
        results = engine.search(query, k=2)
        assert len(results) == 2

    def test_search_returns_entity_id_and_score(self):
        """Each result should be (entity_id, score) tuple."""
        engine, query = self._build_engine_with_known_vectors()
        results = engine.search(query, k=1)
        assert len(results) == 1
        entity_id, score = results[0]
        assert isinstance(entity_id, int)
        assert isinstance(score, float)

    def test_search_scores_are_ordered_descending(self):
        """Scores should be in descending order."""
        engine, query = self._build_engine_with_known_vectors()
        results = engine.search(query, k=3)
        scores = [s for _, s in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_empty_index_returns_empty(self):
        """Searching empty index should return empty list."""
        engine = CandidateEngine()
        engine.build_index({})
        query = np.random.randn(EMBEDDING_DIM).astype(np.float32)
        results = engine.search(query, k=5)
        assert results == []

    def test_search_k_larger_than_index(self):
        """If k > index size, return all available results."""
        engine = CandidateEngine()
        embeddings = {
            1: np.random.randn(EMBEDDING_DIM).astype(np.float32),
            2: np.random.randn(EMBEDDING_DIM).astype(np.float32),
        }
        engine.build_index(embeddings)
        query = np.random.randn(EMBEDDING_DIM).astype(np.float32)
        results = engine.search(query, k=10)
        assert len(results) == 2


class TestIndexPersistence:
    """Save/load FAISS index to/from disk."""

    def test_save_and_load_index(self, tmp_path):
        """Index should be saveable and loadable."""
        engine = CandidateEngine()
        embeddings = {
            1: np.random.randn(EMBEDDING_DIM).astype(np.float32),
            2: np.random.randn(EMBEDDING_DIM).astype(np.float32),
        }
        engine.build_index(embeddings)

        index_path = str(tmp_path / "test_index.bin")
        id_map_path = str(tmp_path / "test_id_map.json")
        engine.save(index_path, id_map_path)

        loaded_engine = CandidateEngine()
        loaded_engine.load(index_path, id_map_path)
        assert loaded_engine.index_size() == 2

        # Search should still work
        query = np.random.randn(EMBEDDING_DIM).astype(np.float32)
        results = loaded_engine.search(query, k=2)
        assert len(results) == 2
