"""Tests for news analysis functionality."""
import pytest
from app.analyze_news import NewsAnalyzer

def test_analyze_article(news_analyzer, mock_anthropic_client):
    # Setup mock response
    mock_anthropic_client.messages.create.return_value.content = [
        Mock(text="Test analysis result")
    ]
    
    # Test input
    article = {
        'title': 'Test Article',
        'content': 'Test content',
        'source': 'test.com',
        'url': 'http://test.com'
    }
    
    # Run analysis
    result = news_analyzer.analyze_article(article, "Test context")
    
    # Verify results
    assert result['title'] == 'Test Article'
    assert result['source'] == 'test.com'
    assert result['analysis'] == "Test analysis result"
    assert 'error' not in result
