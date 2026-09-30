from app.services.knowledge_base import KnowledgeBase


def test_add_and_search_finds_most_similar(tmp_path):
    kb = KnowledgeBase(path=tmp_path / "kb.json")

    kb.add_or_update("doc1", "Sobre IA", "texto 1", [1.0, 0.0, 0.0], "https://drive/doc1")
    kb.add_or_update("doc2", "Sobre cocina", "texto 2", [0.0, 1.0, 0.0], "https://drive/doc2")
    kb.add_or_update("doc3", "Sobre IA otra vez", "texto 3", [0.9, 0.1, 0.0], "https://drive/doc3")

    results = kb.search(query_embedding=[1.0, 0.0, 0.0], top_k=2)

    assert len(results) == 2
    assert results[0]["doc_id"] == "doc1"  # similitud perfecta
    assert results[1]["doc_id"] == "doc3"  # la segunda más parecida
    assert results[0]["score"] > results[1]["score"] > 0


def test_search_on_empty_knowledge_base_returns_empty(tmp_path):
    kb = KnowledgeBase(path=tmp_path / "kb.json")
    assert kb.search(query_embedding=[1.0, 0.0], top_k=3) == []


def test_get_modified_time_roundtrip(tmp_path):
    kb = KnowledgeBase(path=tmp_path / "kb.json")
    assert kb.get_modified_time("doc1") is None

    kb.add_or_update("doc1", "T", "texto", [1.0], "https://drive/doc1", modified_time="2026-09-01T00:00:00Z")
    assert kb.get_modified_time("doc1") == "2026-09-01T00:00:00Z"


def test_add_or_update_overwrites_existing_entry(tmp_path):
    kb = KnowledgeBase(path=tmp_path / "kb.json")
    kb.add_or_update("doc1", "Título viejo", "texto viejo", [1.0, 0.0], "https://drive/doc1")
    kb.add_or_update("doc1", "Título nuevo", "texto nuevo", [0.0, 1.0], "https://drive/doc1")

    docs = kb.all_documents()
    assert len(docs) == 1
    assert docs[0]["title"] == "Título nuevo"


def test_remove_deletes_entry(tmp_path):
    kb = KnowledgeBase(path=tmp_path / "kb.json")
    kb.add_or_update("doc1", "T", "texto", [1.0], "https://drive/doc1")
    kb.remove("doc1")
    assert kb.all_documents() == []


def test_persists_across_instances(tmp_path):
    path = tmp_path / "kb.json"
    KnowledgeBase(path=path).add_or_update("doc1", "T", "texto", [1.0, 0.0], "https://drive/doc1")

    kb2 = KnowledgeBase(path=path)
    assert len(kb2.all_documents()) == 1
