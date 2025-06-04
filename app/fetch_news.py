from datetime import datetime
from anthropic import Anthropic
from tavily import TavilyClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import get_api_key
from app.rag_utils import VectorStore

def fetch_news(domain: str, context: str, num_articles: int = 5, search_depth: str = "advanced", 
               time_range: str = "day", include_domains: str = "", exclude_domains: str = ""):
    """Fetch news articles based on domain and context with Tavily API
    Args:
        domain: Business domain to search for
        context: Additional context for the search
        num_articles: Number of articles to fetch (default: 5)
        search_depth: Either 'basic' or 'advanced' (default: advanced)
        time_range: One of 'day', 'week', or 'month' (default: day)
        include_domains: Newline-separated list of domains to include
        exclude_domains: Newline-separated list of domains to exclude
    Returns:
        List of article dictionaries with title, url, content, score, and metadata
    """
    print(f"[fetch_news] Starting search for: {domain} with context: {context}")
    
    # Validate search_depth
    if search_depth not in ["basic", "advanced"]:
        print(f"[fetch_news] Invalid search_depth '{search_depth}', defaulting to 'advanced'")
        search_depth = "advanced"
    
    query = f"{domain} for {context}" if context else domain
    
    # Initialize Tavily client
    tavily_api_key = get_api_key("TAVILY_API_KEY")
    if not tavily_api_key:
        raise ValueError("Tavily API key not found. Please check your API key configuration.")
    print(f"[fetch_news] Initializing Tavily client with API key: {tavily_api_key[:4]}...")
    tavily = TavilyClient(api_key=tavily_api_key)
    
    # Process include/exclude domains
    include_domain_list = [d.strip() for d in include_domains.split('\n') if d.strip()] if include_domains else []
    exclude_domain_list = [d.strip() for d in exclude_domains.split('\n') if d.strip()] if exclude_domains else []
    print(f"[fetch_news] Include domains: {include_domain_list}")
    print(f"[fetch_news] Exclude domains: {exclude_domain_list}")
    print(f"[fetch_news] Querying Tavily API with query='{query}', depth='{search_depth}', time_range='{time_range}'")
    
    try:
        response = tavily.search(
            query=query,
            search_depth=search_depth,
            max_results=num_articles,
            time_range=time_range,
            include_answer="advanced",
            include_raw_content=True,
            include_domains=include_domain_list if include_domain_list else None,
            exclude_domains=exclude_domain_list if exclude_domain_list else None
        )
        
        # Process and validate each article
        articles = []
        for article in response.get('results', []):
            if not article.get('title') or not article.get('content'):
                print(f"[fetch_news] Skipping article with missing title or content: {article.get('url')}")
                continue
                
            articles.append({
                'title': article['title'],
                'url': article['url'],
                'content': article['content'],
                'score': article.get('relevance_score', 0),
                'published_date': article.get('published_date', ''),
                'source': article.get('domain', ''),
                'snippet': article.get('description', '')[:200] + '...' if article.get('description') else ''
            })
            
        print(f"[fetch_news] Successfully fetched {len(articles)} valid articles")
        return articles
        
    except Exception as e:
        print(f"[fetch_news] Error fetching news: {str(e)}")
        raise Exception(f"Failed to fetch news articles: {str(e)}")