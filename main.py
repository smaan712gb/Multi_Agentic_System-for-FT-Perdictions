import os
import sys
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
from setup_env import setup_env

# Import our agents
from agents.deepseek import analyze_futures as deepseek_analyze
from agents.gemini import analyze_futures as gemini_analyze
from agents.groq import analyze_futures as groq_analyze

# Import our tools
from tools.chart_scraper.chart_scraper import ChartScraper
from tools.mean_analysis.mean_analyzer import MeanAnalyzer
from tools.mean_analysis.mean_visualizer import MeanVisualizer
from tools.volume_profile.agno_tool import get_volume_profile
from tools.sentiment_analyzer.agno_tool import get_alpha_vantage_sentiment

def run_analysis(symbol: str) -> Dict[str, Any]:
    """
    Run analysis for a specific symbol using all agents
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        
    Returns:
        Dictionary containing the combined analysis
    """
    print(f"Running analysis for {symbol}...")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Initialize chart scraper
    chart_scraper = ChartScraper(data_dir="data")
    
    # Scrape chart data for all timeframes
    print(f"Scraping chart data for {symbol}...")
    chart_data = {}
    for timeframe in chart_scraper.TIMEFRAMES:
        print(f"  - {timeframe}")
        chart_data[timeframe] = chart_scraper.get_ticker_data(symbol, timeframe)
        chart_scraper.plot_chart(symbol, timeframe)
    
    # Get volume profile analysis from Alpha Vantage
    print(f"Analyzing volume profile for {symbol} using Alpha Vantage API...")
    volume_profile_analysis = get_volume_profile(symbol, interval="5min")
    print(f"Alpha Vantage volume profile analysis complete.")
    
    # Get news sentiment analysis from Alpha Vantage
    print(f"Analyzing news sentiment for {symbol} using Alpha Vantage API...")
    news_sentiment_analysis = get_alpha_vantage_sentiment(symbol)
    print(f"Alpha Vantage news sentiment analysis complete.")
    
    # Run analysis with each agent
    print(f"Running analysis with DeepSeek...")
    deepseek_result = deepseek_analyze(symbol)
    
    print(f"Running analysis with Gemini...")
    gemini_result = gemini_analyze(symbol)
    
    # Run analysis with Groq
    print(f"Running analysis with Groq...")
    groq_result = groq_analyze(symbol)
    
    # Combine predictions using mean analyzer and visualize
    print(f"Combining predictions...")
    mean_analyzer = MeanAnalyzer(data_dir="data")
    mean_visualizer = MeanVisualizer(analyzer=mean_analyzer)
    
    mean_predictions = {}
    for timeframe in mean_analyzer.PREDICTION_TIMEFRAMES:
        print(f"  - {timeframe}")
        try:
            # First combine predictions
            mean_predictions[timeframe] = mean_analyzer.combine_predictions(symbol, timeframe)
            # Then visualize them
            mean_visualizer.plot_mean_prediction(symbol, timeframe, chart_data[timeframe])
        except Exception as e:
            print(f"    Error: {e}")
    
    # Create interactive chart
    print(f"Creating interactive chart...")
    interactive_chart = mean_visualizer.create_interactive_chart(symbol)
    
    return {
        "symbol": symbol,
        "chart_data": {timeframe: chart_data[timeframe].to_dict() for timeframe in chart_data},
        "volume_profile_analysis": volume_profile_analysis,
        "news_sentiment_analysis": news_sentiment_analysis,
        "deepseek_result": deepseek_result,
        "gemini_result": gemini_result,
        "groq_result": groq_result,
        "mean_predictions": mean_predictions,
        "interactive_chart_path": interactive_chart.get("html_path"),
        "timestamp": datetime.now().isoformat()
    }

def main():
    """
    Main function
    """
    # Set up environment variables
    setup_env()
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <symbol>")
        print("Available symbols: NQ, ES, YM")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    if symbol not in ["NQ", "ES", "YM"]:
        print(f"Invalid symbol: {symbol}. Choose from NQ, ES, YM.")
        sys.exit(1)
    
    result = run_analysis(symbol)
    
    # Print the path to the interactive chart
    if result.get("interactive_chart_path"):
        print(f"\nInteractive chart created at: {result['interactive_chart_path']}")
        print(f"Open this file in a web browser to view the analysis.")

if __name__ == "__main__":
    main()
