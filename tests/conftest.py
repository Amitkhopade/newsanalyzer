"""Test fixtures and configuration."""
import pytest
from unittest.mock import Mock
from app.analyze_news import NewsAnalyzer
from app.rag_utils import VectorStore

@pytest.fixture
def mock_anthropic_client():
    return Mock()

@pytest.fixture
def mock_vector_store():
    return Mock(spec=VectorStore)

@pytest.fixture
def news_analyzer(mock_anthropic_client):
    analyzer = NewsAnalyzer()
    analyzer.client = mock_anthropic_client
    return analyzer
