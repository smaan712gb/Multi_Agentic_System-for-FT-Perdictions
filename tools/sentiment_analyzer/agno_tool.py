from typing import Dict, Any, List, Optional
import os
import json
from .sentiment_analyzer import SentimentAnalyzer
from .alpha_vantage_sentiment import AlphaVantageSentimentAnalyzer

# Get Alpha Vantage API key from environment variables
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "4M6VASN5R8SRDP29")

# Initialize the sentiment analyzers
_analyzer = SentimentAnalyzer(data_dir="data")
_alpha_vantage_analyzer = AlphaVantageSentimentAnalyzer(api_key=ALPHA_VANTAGE_API_KEY, data_dir="data")

def get_news(symbol: str, max_results: int = 20) -> Dict[str, Any]:
    """Get news articles for a specific symbol.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary containing the news articles
    """
    news_articles = _analyzer.search_news(symbol, max_results=max_results)
    
    return {
        "symbol": symbol,
        "news_articles": news_articles,
        "count": len(news_articles)
    }

def get_sentiment(symbol: str) -> Dict[str, Any]:
    """Get sentiment analysis for a specific symbol.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        
    Returns:
        Dictionary containing the sentiment analysis
    """
    return _analyzer.get_sentiment(symbol)

def summarize_news(symbol: str, max_articles: int = 5) -> Dict[str, Any]:
    """Summarize news articles for a specific symbol.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        max_articles: Maximum number of articles to summarize
        
    Returns:
        Dictionary containing the summarized news articles
    """
    news_articles = _analyzer.search_news(symbol)
    summaries = _analyzer.summarize_news(news_articles, max_articles=max_articles)
    
    return {
        "symbol": symbol,
        "summaries": summaries,
        "count": len(summaries)
    }

def get_alpha_vantage_sentiment(symbol: str) -> str:
    """Get Alpha Vantage news sentiment analysis for a specific symbol.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        
    Returns:
        String containing the Alpha Vantage news sentiment analysis
    """
    return _alpha_vantage_analyzer.format_sentiment_for_agents(symbol)
