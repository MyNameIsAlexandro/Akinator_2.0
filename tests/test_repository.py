"""Tests for the Database Repository (SQLite).

Covers:
- Schema creation
- Entity CRUD (create, read, update)
- Attribute CRUD
- Entity attribute values
- Alias management
- Querying entities by type / with attributes
- Embedding storage and retrieval
"""

from __future__ import annotations

import pytest

from akinator.db.models import Attribute, Entity
from akinator.db.repository import Repository


class TestSchemaCreation:
    """Database schema initialization."""

    @pytest.mark.asyncio
    async def test_create_tables(self, tmp_db_path: str):
        """All required tables should be created."""
        repo = Repository(tmp_db_path)
        await repo.init_db()
        tables = await repo.list_tables()
        assert "entities" in tables
        assert "entity_aliases" in tables
        assert "entity_attributes" in tables
        assert "attributes" in tables
        assert "entity_embeddings" in tables
        await repo.close()

    @pytest.mark.asyncio
    async def test_idempotent_init(self, tmp_db_path: str):
        """Calling init_db twice should not raise."""
        repo = Repository(tmp_db_path)
        await repo.init_db()
        await repo.init_db()  # Should not fail
        await repo.close()


class TestEntityCRUD:
    """Create, read, update entities."""

    @pytest.mark.asyncio
    async def test_add_entity(self, tmp_db_path: str):
        repo = Repository(tmp_db_path)
        await repo.init_db()
        entity_id = await repo.add_entity(
            name="Darth Vader",
            description="Star Wars villain",
            entity_type="character",
            language="en",
        )
        assert entity_id is not None
        assert isinstance(entity_id, int)
        await repo.close()

    @pytest.mark.asyncio
    async def test_get_entity_by_id(self, tmp_db_path: str):
        repo = Repository(tmp_db_path)
        await repo.init_db()
        entity_id = await repo.add_entity(
            name="Mario", description="Nintendo plumber",
            entity_type="character", language="en",
        )
        entity = await repo.get_entity(entity_id)
        assert entity is not None
        assert entity.name == "Mario"
        assert entity.description == "Nintendo plumber"
        assert entity.entity_type == "character"
        await repo.close()

    @pytest.mark.asyncio
    async def test_get_nonexistent_entity(self, tmp_db_path: str):
        repo = Repository(tmp_db_path)
        await repo.init_db()
        entity = await repo.get_entity(9999)
        assert entity is None
        await repo.close()

    @pytest.mark.asyncio
    async def test_get_all_entities(self, tmp_db_path: str):
        repo = Repository(tmp_db_path)
        await repo.init_db()
        await repo.add_entity("A", "desc", "person", "en")
        await repo.add_entity("B", "desc", "character", "en")
        await repo.add_entity("C", "desc", "person", "ru")
        entities = await repo.get_all_entities()
        assert len(entities) == 3
        await repo.close()

    @pytest.mark.asyncio
    async def test_update_play_count(self, tmp_db_path: str):
        repo = Repository(tmp_db_path)
        await repo.init_db()
        eid = await repo.add_entity("A", "desc", "person", "en")
        await repo.increment_play_count(eid)
        await repo.increment_play_count(eid)
        entity = await repo.get_entity(eid)
        assert entity.play_count == 2
        await repo.close()


class TestAttributeCRUD:
    """Attribute definitions and entity attribute values."""

    @pytest.mark.asyncio
    async def test_add_attribute(self, tmp_db_path: str):
        repo = Repository(tmp_db_path)
        await repo.init_db()
        attr_id = await repo.add_attribute(
            key="is_fictional",
            question_ru="Вымышленный?",
            question_en="Is fictional?",
            category="identity",
        )
        assert attr_id is not None
        await repo.close()

    @pytest.mark.asyncio
    async def test_get_all_attributes(self, tmp_db_path: str):
        repo = Repository(tmp_db_path)
        await repo.init_db()
        await repo.add_attribute("is_fictional", "Вымышленный?", "Fictional?", "identity")
        await repo.add_attribute("is_male", "Мужчина?", "Male?", "identity")
        attrs = await repo.get_all_attributes()
        assert len(attrs) == 2
        assert all(isinstance(a, Attribute) for a in attrs)
        await repo.close()

    @pytest.mark.asyncio
    async def test_set_and_get_entity_attribute(self, tmp_db_path: str):
        repo = Repository(tmp_db_path)
        await repo.init_db()
        eid = await repo.add_entity("A", "desc", "person", "en")
        aid = await repo.add_attribute("is_fictional", "Q?", "Q?", "identity")
        await repo.set_entity_attribute(eid, aid, 0.9)
        value = await repo.get_entity_attribute(eid, aid)
        assert value == pytest.approx(0.9)
        await repo.close()

    @pytest.mark.asyncio
    async def test_get_entity_with_attributes(self, tmp_db_path: str):
        repo = Repository(tmp_db_path)
        await repo.init_db()
        eid = await repo.add_entity("A", "desc", "person", "en")
        a1 = await repo.add_attribute("is_fictional", "Q?", "Q?", "identity")
        a2 = await repo.add_attribute("is_male", "Q?", "Q?", "identity")
        await repo.set_entity_attribute(eid, a1, 0.0)
        await repo.set_entity_attribute(eid, a2, 1.0)
        entity = await repo.get_entity(eid, with_attributes=True)
        assert entity.attributes["is_fictional"] == pytest.approx(0.0)
        assert entity.attributes["is_male"] == pytest.approx(1.0)
        await repo.close()

    @pytest.mark.asyncio
    async def test_get_missing_entity_attribute_returns_none(self, tmp_db_path: str):
        repo = Repository(tmp_db_path)
        await repo.init_db()
        eid = await repo.add_entity("A", "desc", "person", "en")
        aid = await repo.add_attribute("is_fictional", "Q?", "Q?", "identity")
        value = await repo.get_entity_attribute(eid, aid)
        assert value is None
        await repo.close()


class TestAliases:
    """Entity alias management."""

    @pytest.mark.asyncio
    async def test_add_and_get_aliases(self, tmp_db_path: str):
        repo = Repository(tmp_db_path)
        await repo.init_db()
        eid = await repo.add_entity("Darth Vader", "desc", "character", "en")
        await repo.add_alias(eid, "Anakin Skywalker", "en")
        await repo.add_alias(eid, "Дарт Вейдер", "ru")
        aliases = await repo.get_aliases(eid)
        assert len(aliases) == 2
        alias_texts = [a[0] for a in aliases]
        assert "Anakin Skywalker" in alias_texts
        assert "Дарт Вейдер" in alias_texts
        await repo.close()


class TestEmbeddings:
    """Embedding storage and retrieval."""

    @pytest.mark.asyncio
    async def test_store_and_retrieve_embedding(self, tmp_db_path: str):
        import numpy as np
        repo = Repository(tmp_db_path)
        await repo.init_db()
        eid = await repo.add_entity("A", "desc", "person", "en")
        embedding = np.random.randn(1536).astype(np.float32)
        await repo.set_embedding(eid, embedding)
        loaded = await repo.get_embedding(eid)
        assert loaded is not None
        np.testing.assert_array_almost_equal(loaded, embedding, decimal=5)
        await repo.close()

    @pytest.mark.asyncio
    async def test_get_all_embeddings(self, tmp_db_path: str):
        import numpy as np
        repo = Repository(tmp_db_path)
        await repo.init_db()
        e1 = await repo.add_entity("A", "desc", "person", "en")
        e2 = await repo.add_entity("B", "desc", "person", "en")
        emb1 = np.random.randn(1536).astype(np.float32)
        emb2 = np.random.randn(1536).astype(np.float32)
        await repo.set_embedding(e1, emb1)
        await repo.set_embedding(e2, emb2)
        all_embs = await repo.get_all_embeddings()
        assert len(all_embs) == 2
        assert e1 in all_embs
        assert e2 in all_embs
        await repo.close()

    @pytest.mark.asyncio
    async def test_get_missing_embedding(self, tmp_db_path: str):
        repo = Repository(tmp_db_path)
        await repo.init_db()
        eid = await repo.add_entity("A", "desc", "person", "en")
        loaded = await repo.get_embedding(eid)
        assert loaded is None
        await repo.close()
