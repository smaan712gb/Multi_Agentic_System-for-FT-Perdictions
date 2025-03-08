import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

class AlphaVantageSentimentAnalyzer:
    """
    A tool for analyzing news sentiment using Alpha Vantage's News Sentiment API
    """
    
    def __init__(self, api_key: str, data_dir: str = "data"):
        """
        Initialize the AlphaVantageSentimentAnalyzer
        
        Args:
            api_key: Alpha Vantage API key
            data_dir: Directory to store the data
        """
        self.api_key = api_key
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def get_news_sentiment(self, symbol: str, time_from: Optional[str] = None, 
                          time_to: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """
        Get news sentiment for a specific symbol
        
        Args:
            symbol: The futures symbol (NQ, ES, YM) or related ticker
            time_from: Start time for news articles (YYYYMMDDTHHMM format)
            time_to: End time for news articles (YYYYMMDDTHHMM format)
            limit: Maximum number of news items to return
            
        Returns:
            Dictionary containing the news sentiment data
        """
        # Map futures symbols to relevant market-moving keywords
        symbol_mapping = {
            "NQ": "NASDAQ technology earnings tech stocks",
            "ES": "S&P 500 market economy Fed interest rates",
            "YM": "Dow Jones industrial stocks economy",
        }
        
        # Use the mapped keywords if available, otherwise use the original symbol
        keywords = symbol_mapping.get(symbol, symbol)
        
        # Set default time range if not provided (last 7 days)
        if not time_from:
            time_from = (datetime.now() - timedelta(days=7)).strftime("%Y%m%dT0000")
        if not time_to:
            time_to = datetime.now().strftime("%Y%m%dT2359")
        
        # Alpha Vantage API endpoint for news sentiment
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&keywords={keywords}&time_from={time_from}&time_to={time_to}&limit={limit}&apikey={self.api_key}"
        
        # Get data from Alpha Vantage
        response = requests.get(url)
        data = response.json()
        
        # Check if there's an error
        if "Error Message" in data:
            raise ValueError(f"Alpha Vantage API error: {data['Error Message']}")
        
        # Check if there's information
        if "Information" in data:
            print(f"Information: {data['Information']}")
            return {"error": data['Information']}
        
        # Save data to JSON
        os.makedirs(os.path.join(self.data_dir, symbol, "sentiment"), exist_ok=True)
        import json
        with open(os.path.join(self.data_dir, symbol, "sentiment", "alpha_vantage_news.json"), "w") as f:
            json.dump(data, f, indent=2)
        
        # Process the sentiment data
        feed = data.get("feed", [])
        
        # Calculate overall sentiment
        overall_sentiment_score = 0
        overall_sentiment_label = "Neutral"
        relevant_articles = 0
        
        # When using keywords, we analyze all articles returned
        for article in feed:
            # Get the overall sentiment of the article
            overall_sentiment = article.get("overall_sentiment_score", 0)
            if overall_sentiment:
                overall_sentiment_score += float(overall_sentiment)
                relevant_articles += 1
        
        # Calculate average sentiment score
        if relevant_articles > 0:
            overall_sentiment_score /= relevant_articles
            
            # Determine sentiment label
            if overall_sentiment_score > 0.25:
                overall_sentiment_label = "Bullish"
            elif overall_sentiment_score > 0:
                overall_sentiment_label = "Somewhat Bullish"
            elif overall_sentiment_score > -0.25:
                overall_sentiment_label = "Somewhat Bearish"
            else:
                overall_sentiment_label = "Bearish"
        
        # Prepare the result
        result = {
            "symbol": symbol,
            "keywords": keywords,
            "overall_sentiment_score": overall_sentiment_score,
            "overall_sentiment_label": overall_sentiment_label,
            "relevant_articles": relevant_articles,
            "total_articles": len(feed),
            "time_from": time_from,
            "time_to": time_to,
            "articles": []
        }
        
        # Add top articles with their sentiment
        for article in feed[:10]:  # Include only top 10 articles in the result
            result["articles"].append({
                "title": article.get("title", ""),
                "summary": article.get("summary", ""),
                "published": article.get("time_published", ""),
                "url": article.get("url", ""),
                "sentiment_score": article.get("overall_sentiment_score", 0),
                "sentiment_label": article.get("overall_sentiment_label", "Neutral")
            })
        
        return result
    
    def format_sentiment_for_agents(self, symbol: str) -> str:
        """
        Format news sentiment analysis for agents
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            
        Returns:
            Formatted string containing news sentiment analysis
        """
        try:
            # Get news sentiment
            sentiment_data = self.get_news_sentiment(symbol)
            
            # Check if there's an error
            if "error" in sentiment_data:
                return f"""
News Sentiment Analysis (Alpha Vantage):
Error retrieving news sentiment data: {sentiment_data['error']}
"""
            
            # Format the results
            formatted_results = f"""
News Sentiment Analysis (Alpha Vantage):
- Overall Sentiment: {sentiment_data['overall_sentiment_label']} (Score: {sentiment_data['overall_sentiment_score']:.2f})
- Analyzed {sentiment_data['relevant_articles']} relevant articles out of {sentiment_data['total_articles']} total articles
- Time Period: {sentiment_data['time_from']} to {sentiment_data['time_to']}

Top Recent Headlines:
"""
            
            # Add top headlines with sentiment
            for i, article in enumerate(sentiment_data['articles'][:5], 1):
                formatted_results += f"""
{i}. {article['title']}
   Sentiment: {article.get('sentiment_label', 'Neutral')} (Score: {article.get('sentiment_score', 0) if isinstance(article.get('sentiment_score', 0), (int, float)) else float(article.get('sentiment_score', 0).iloc[0] if hasattr(article.get('sentiment_score', 0), 'iloc') else article.get('sentiment_score', 0)):.2f})
   Published: {article['published']}
"""
            
            # Add trading implications
            formatted_results += f"""
Trading Implications:
- {'Positive sentiment suggests potential upward price movement' if sentiment_data['overall_sentiment_score'] > 0 else 'Negative sentiment suggests potential downward price movement'}
- News sentiment should be considered alongside technical indicators and volume profile
- Recent headlines indicate {'bullish' if sentiment_data['overall_sentiment_score'] > 0 else 'bearish'} market perception
- Monitor for significant news events that could cause volatility
"""
            
            return formatted_results
            
        except Exception as e:
            return f"""
News Sentiment Analysis (Alpha Vantage):
Error analyzing news sentiment: {str(e)}
"""
