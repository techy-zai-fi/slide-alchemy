import asyncio
import pytest
from app.services.research_engine import ResearchEngine
from app.models.resource import ParsedContent


@pytest.fixture
def engine():
    return ResearchEngine()


def test_engine_init():
    engine = ResearchEngine()
    assert engine.serper_api_key is None
    assert engine.reddit_client_id is None


def test_engine_init_with_keys():
    engine = ResearchEngine(serper_api_key="test-key", reddit_client_id="reddit-id")
    assert engine.serper_api_key == "test-key"
    assert engine.reddit_client_id == "reddit-id"


def test_cluster_keywords(engine):
    keywords = ["artificial", "intelligence", "machine", "learning"]
    clusters = engine._cluster_keywords(keywords)
    assert len(clusters) > 0
    assert all(isinstance(c, str) for c in clusters)


def test_cluster_keywords_filters_short(engine):
    keywords = ["AI", "ML", "deep", "learning", "neural", "networks"]
    clusters = engine._cluster_keywords(keywords)
    # Should filter out "AI" and "ML" (len <= 3)
    for cluster in clusters:
        words = cluster.split()
        for word in words:
            assert len(word) > 3


def test_analyze_gaps(engine):
    resources = [ParsedContent(text="This document covers machine learning basics and neural networks.")]
    qa_context = {
        "sections": "Introduction, Deep Learning, Transformers, Conclusion",
        "key_message": "transformers revolutionized NLP",
    }
    gaps = asyncio.run(engine.analyze_gaps(resources, qa_context))
    assert isinstance(gaps, list)
    assert len(gaps) <= 5


def test_search_web_no_key(engine):
    results = asyncio.run(engine.search_web("test query"))
    assert results == []


def test_search_reddit_no_key(engine):
    results = asyncio.run(engine.search_reddit("test query"))
    assert results == []


def test_search_all_no_keys(engine):
    results = asyncio.run(engine.search_all("test query"))
    assert isinstance(results, list)
