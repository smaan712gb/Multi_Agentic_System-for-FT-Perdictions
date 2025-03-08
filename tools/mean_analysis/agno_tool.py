from typing import Dict, Any, List, Optional
import os
import json
import pandas as pd
from .mean_analyzer import MeanAnalyzer
from ..chart_scraper.chart_scraper import ChartScraper

# Create single instances of the analyzers
_analyzer = MeanAnalyzer(data_dir="data")
_chart_scraper = ChartScraper(data_dir="data")

def combine_predictions(symbol: str, timeframe: str) -> Dict[str, Any]:
    """Combine predictions from all agents for a specific symbol and timeframe.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        timeframe: The timeframe to combine predictions for
        
    Returns:
        Dictionary containing the combined prediction
    """
    return _analyzer.combine_predictions(symbol, timeframe)

def plot_mean_prediction(symbol: str, timeframe: str) -> Dict[str, Any]:
    """Plot a chart with mean prediction signals.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        timeframe: The timeframe to plot
        
    Returns:
        Dictionary containing the chart path
    """
    # Load chart data
    chart_data = _chart_scraper.get_ticker_data(symbol, timeframe)
    
    # Plot mean prediction
    _analyzer.plot_mean_prediction(symbol, timeframe, chart_data)
    
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "chart_path": _analyzer.get_chart_path(symbol, timeframe)
    }

def create_interactive_chart(symbol: str) -> Dict[str, Any]:
    """Create an interactive chart with tabs for different timeframes.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        
    Returns:
        Dictionary containing paths to the charts
    """
    # First, make sure we have mean predictions for all timeframes
    for timeframe in _analyzer.PREDICTION_TIMEFRAMES:
        try:
            # Load chart data
            chart_data = _chart_scraper.get_ticker_data(symbol, timeframe)
            
            # Plot mean prediction
            _analyzer.plot_mean_prediction(symbol, timeframe, chart_data)
        except Exception as e:
            print(f"Warning: Failed to plot mean prediction for {symbol} {timeframe}: {e}")
    
    # Create interactive chart
    return _analyzer.create_interactive_chart(symbol)
