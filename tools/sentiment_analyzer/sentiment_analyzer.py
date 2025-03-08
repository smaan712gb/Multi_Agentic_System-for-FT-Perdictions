import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import json
from duckduckgo_search import DDGS
import time
import random

class SentimentAnalyzer:
    """
    A tool for analyzing market sentiment and aggregating news for futures markets (NQ, ES, YM)
    """
    
    # Mapping of futures symbols to their search terms
    FUTURES_MAPPING = {
        "NQ": [
            "NASDAQ market outlook", 
            "tech stocks forecast", 
            "technology sector trends", 
            "semiconductor stocks", 
            "AI stocks impact", 
            "tech earnings impact", 
            "NASDAQ market sentiment"
        ],
        "ES": [
            "S&P 500 market outlook", 
            "stock market forecast", 
            "market breadth analysis", 
            "economic indicators impact stocks", 
            "Fed policy stock market", 
            "inflation impact stocks", 
            "S&P 500 market sentiment"
        ],
        "YM": [
            "Dow Jones market outlook", 
            "industrial stocks forecast", 
            "manufacturing sector trends", 
            "blue chip stocks", 
            "trade policy impact stocks", 
            "infrastructure spending stocks", 
            "Dow Jones market sentiment"
        ]
    }
    
    # Broader market search terms that apply to all symbols
    MARKET_TERMS = [
        "stock market trend",
        "market volatility",
        "investor sentiment",
        "economic outlook",
        "Fed interest rates",
        "inflation data",
        "job market report",
        "GDP growth",
        "geopolitical tensions market",
        "treasury yields stocks"
    ]
    
    # News sources to search
    NEWS_SOURCES = [
        "yahoo.com/finance",
        "cnbc.com",
        "wsj.com",
        "bloomberg.com",
        "marketwatch.com",
        "investing.com",
        "reuters.com",
        "ft.com",
        "seekingalpha.com"
    ]
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the SentimentAnalyzer
        
        Args:
            data_dir: Directory to store the scraped data
        """
        self.data_dir = data_dir
        self.news_dir = os.path.join(data_dir, "news")
        os.makedirs(self.news_dir, exist_ok=True)
    
    def search_news(self, symbol: str, max_results: int = 20, max_retries: int = 3) -> List[Dict[str, Any]]:
        """
        Search for news articles related to a specific futures symbol
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            max_results: Maximum number of results to return
            max_retries: Maximum number of retries for rate-limited requests
            
        Returns:
            List of news articles
        """
        if symbol not in self.FUTURES_MAPPING:
            raise ValueError(f"Symbol {symbol} not supported. Choose from {list(self.FUTURES_MAPPING.keys())}")
        
        # Combine symbol-specific terms with broader market terms
        search_terms = self.FUTURES_MAPPING[symbol] + self.MARKET_TERMS
        
        # Create a directory for the symbol if it doesn't exist
        symbol_dir = os.path.join(self.news_dir, symbol)
        os.makedirs(symbol_dir, exist_ok=True)
        
        # Get the current date for the filename
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Check if we already have news for today
        news_file = os.path.join(symbol_dir, f"{current_date}.json")
        if os.path.exists(news_file):
            with open(news_file, "r") as f:
                return json.load(f)
        
        # We don't use mock data anymore - we want real news data only
        
        # Search for news using DuckDuckGo with retry mechanism
        all_results = []
        try:
            with DDGS() as ddgs:
                for term in search_terms:
                    # Create site-specific search queries for each news source
                    for source in self.NEWS_SOURCES:
                        site_query = f"{term} site:{source}"
                        
                        # Try to get results with retries
                        for retry in range(max_retries):
                            try:
                                results = list(ddgs.news(site_query, max_results=3))
                                all_results.extend(results)
                                
                                # Add a delay between requests to avoid rate limiting
                                time.sleep(random.uniform(1.0, 2.0))
                                break  # Break the retry loop if successful
                            except Exception as e:
                                # Log the error and continue to the next source
                                print(f"Error searching for news: {site_query} return None. params={{'q': '{site_query}'}} content=None data=None")
                                # Don't retry, just move on to the next source
                                break
                        
                        # Break if we have enough results
                        if len(all_results) >= max_results:
                            break
                    
                    # Break if we have enough results
                    if len(all_results) >= max_results:
                        break
        except Exception as e:
            print(f"Error in DuckDuckGo search: {e}")
            # If we couldn't get any results, raise an error
            if not all_results:
                raise ValueError(f"Failed to get news data for {symbol}. Error: {e}")
        
        # Limit the number of results
        all_results = all_results[:max_results]
        
        # Add timestamp to each result
        for result in all_results:
            result["timestamp"] = datetime.now().isoformat()
        
        # Save the results to a JSON file
        with open(news_file, "w") as f:
            json.dump(all_results, f, indent=2)
        
        return all_results
    
    def analyze_sentiment(self, news_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the sentiment of news articles
        
        Args:
            news_articles: List of news articles
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        # This is a simple sentiment analysis based on keywords
        # In a real-world scenario, you would use a more sophisticated approach
        
        positive_keywords = [
            "bullish", "rally", "surge", "gain", "positive", "optimistic", "upbeat",
            "growth", "recovery", "strong", "outperform", "beat", "exceed", "upside",
            "upgrade", "buy", "overweight", "rise", "climb", "jump", "soar"
        ]
        
        negative_keywords = [
            "bearish", "decline", "drop", "fall", "negative", "pessimistic", "downbeat",
            "contraction", "recession", "weak", "underperform", "miss", "disappoint", "downside",
            "downgrade", "sell", "underweight", "sink", "plunge", "tumble", "crash"
        ]
        
        # Count the occurrences of positive and negative keywords
        positive_count = 0
        negative_count = 0
        
        for article in news_articles:
            title = article.get("title", "").lower()
            snippet = article.get("body", "").lower()
            
            for keyword in positive_keywords:
                if keyword in title or keyword in snippet:
                    positive_count += 1
            
            for keyword in negative_keywords:
                if keyword in title or keyword in snippet:
                    negative_count += 1
        
        # Calculate sentiment score (-1 to 1)
        total_count = positive_count + negative_count
        if total_count > 0:
            sentiment_score = (positive_count - negative_count) / total_count
        else:
            sentiment_score = 0
        
        # Determine sentiment label
        if sentiment_score > 0.2:
            sentiment_label = "Bullish"
        elif sentiment_score < -0.2:
            sentiment_label = "Bearish"
        else:
            sentiment_label = "Neutral"
        
        return {
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "total_articles": len(news_articles)
        }
    
    def get_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Get sentiment analysis for a specific futures symbol
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        news_articles = self.search_news(symbol)
        sentiment = self.analyze_sentiment(news_articles)
        
        # Add the symbol to the result
        sentiment["symbol"] = symbol
        
        # Add the news articles to the result
        sentiment["news_articles"] = news_articles
        
        return sentiment
    
    def summarize_news(self, news_articles: List[Dict[str, Any]], max_articles: int = 5) -> List[Dict[str, Any]]:
        """
        Summarize news articles
        
        Args:
            news_articles: List of news articles
            max_articles: Maximum number of articles to summarize
            
        Returns:
            List of summarized news articles
        """
        # Sort articles by date (newest first)
        sorted_articles = sorted(
            news_articles,
            key=lambda x: x.get("date", ""),
            reverse=True
        )
        
        # Take the top N articles
        top_articles = sorted_articles[:max_articles]
        
        # Create summaries
        summaries = []
        for article in top_articles:
            summary = {
                "title": article.get("title", ""),
                "source": article.get("source", ""),
                "url": article.get("url", ""),
                "date": article.get("date", ""),
                "snippet": article.get("body", "")[:200] + "..." if len(article.get("body", "")) > 200 else article.get("body", "")
            }
            summaries.append(summary)
        
        return summaries
