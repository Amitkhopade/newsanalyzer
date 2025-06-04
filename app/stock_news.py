"""Stock news functionality for the Business News Analyzer."""
from typing import List, Dict, Any
import yfinance as yf
from datetime import datetime

# Default company tickers and their display names
DEFAULT_TICKERS = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft',
    'GOOGL': 'Alphabet (Google)',
    'AMZN': 'Amazon',
    'META': 'Meta Platforms',
    'TSLA': 'Tesla',
    'NVDA': 'NVIDIA',
    'JPM': 'JPMorgan Chase',
    'BAC': 'Bank of America',
    'WMT': 'Walmart'
}

def fetch_stock_news(ticker_symbol: str) -> List[Dict[str, Any]]:
    """Fetch news for a given stock ticker.
    
    Args:
        ticker_symbol: The stock ticker symbol (e.g., 'AAPL')
        
    Returns:
        List of news items with title, publisher, url, and published date
    """
    try:
        # Create ticker object
        ticker = yf.Ticker(ticker_symbol)
        
        # Fetch news
        news_items = ticker.news
        
        # Process and format news items
        formatted_news = []
        for item in news_items:
            formatted_news.append({
                'title': item.get('title', 'No title available'),
                'publisher': item.get('publisher', 'Unknown publisher'),
                'link': item.get('link', '#'),
                'published': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                'summary': item.get('summary', 'No summary available'),
                'sentiment': 'Unknown',  # Could be enhanced with sentiment analysis
                'type': item.get('type', 'article')
            })
        
        return formatted_news
        
    except Exception as e:
        print(f"Error fetching news for {ticker_symbol}: {str(e)}")
        return []

def get_stock_info(ticker_symbol: str) -> Dict[str, Any]:
    """Get basic stock information.
    
    Args:
        ticker_symbol: The stock ticker symbol
        
    Returns:
        Dictionary containing basic stock information
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        return {
            'name': info.get('longName', DEFAULT_TICKERS.get(ticker_symbol, ticker_symbol)),
            'sector': info.get('sector', 'Unknown sector'),
            'industry': info.get('industry', 'Unknown industry'),
            'market_cap': info.get('marketCap', 0),
            'current_price': info.get('currentPrice', 0),
            'currency': info.get('currency', 'USD'),
            'website': info.get('website', ''),
            'description': info.get('longBusinessSummary', 'No description available')
        }
        
    except Exception as e:
        print(f"Error fetching stock info for {ticker_symbol}: {str(e)}")
        return {
            'name': DEFAULT_TICKERS.get(ticker_symbol, ticker_symbol),
            'error': str(e)
        }
