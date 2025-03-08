from typing import Dict, Any, List, Optional
import os
import json
import base64
import pandas as pd
from .chart_scraper import ChartScraper
from tools.technical_indicators.agno_tool import format_indicators

# Create a single instance of the ChartScraper
_scraper = ChartScraper(data_dir="data")

def get_chart_data(symbol: str, timeframe: str) -> str:
    """Get chart data for a specific symbol and timeframe.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        timeframe: The timeframe to fetch data for
        
    Returns:
        String containing information about the chart data
    """
    data = _scraper.get_ticker_data(symbol, timeframe)
    
    # Get basic statistics
    stats = {
        "symbol": symbol,
        "timeframe": timeframe,
        "start_date": data.index[0].strftime("%Y-%m-%d") if len(data) > 0 else None,
        "end_date": data.index[-1].strftime("%Y-%m-%d") if len(data) > 0 else None,
        "num_points": len(data),
        "latest_close": float(data['Close'].iloc[-1].iloc[0]) if len(data) > 0 else None,
        "data_path": _scraper.get_data_path(symbol, timeframe)
    }
    
    # Calculate technical indicators - don't catch exceptions here
    # Let the format_indicators function handle errors internally
    indicators_text = format_indicators(data)
    
    # Calculate some basic technical indicators directly if we have enough data points
    if len(data) >= 20:
        # Handle case where data['Close'] is a DataFrame rather than a Series
        close_series = data['Close'].iloc[:, 0] if isinstance(data['Close'], pd.DataFrame) else data['Close']
        
        # Calculate simple moving averages
        sma20 = close_series.rolling(window=20).mean().iloc[-1] if len(close_series) >= 20 else None
        sma50 = close_series.rolling(window=50).mean().iloc[-1] if len(close_series) >= 50 else None
        sma200 = close_series.rolling(window=200).mean().iloc[-1] if len(close_series) >= 200 else None
        
        # Add basic trend analysis
        sma20_str = f"{sma20:.2f}" if sma20 is not None else "N/A"
        sma50_str = f"{sma50:.2f}" if sma50 is not None else "N/A"
        sma200_str = f"{sma200:.2f}" if sma200 is not None else "N/A"
        
        if sma20 is not None and sma50 is not None:
            if sma20 > sma50:
                trend = "Bullish"
            elif sma20 < sma50:
                trend = "Bearish"
            else:
                trend = "Neutral"
        else:
            trend = "Neutral"
        
        basic_analysis = f"""
Basic Technical Analysis:
- Latest Close: {stats['latest_close']}
- 20-day SMA: {sma20_str}
- 50-day SMA: {sma50_str}
- 200-day SMA: {sma200_str}
- Trend: {trend}
"""
        indicators_text += basic_analysis
    
    # Return a string representation with technical indicators
    return f"""Chart data for {symbol} ({timeframe}): {len(data)} data points from {stats['start_date']} to {stats['end_date']}. 
Latest close: {stats['latest_close']}. 
Data saved to {stats['data_path']}

{indicators_text}"""

def get_all_timeframes(symbol: str) -> str:
    """Get data for all timeframes for a specific symbol.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        
    Returns:
        String containing information about all timeframes
    """
    results = []
    for timeframe in _scraper.TIMEFRAMES:
        results.append(get_chart_data(symbol, timeframe))
    
    return "\n".join(results)

def plot_chart(symbol: str, timeframe: str) -> str:
    """Plot a chart for a specific symbol and timeframe.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        timeframe: The timeframe to plot
        
    Returns:
        String containing information about the chart
    """
    _scraper.plot_chart(symbol, timeframe)
    chart_path = _scraper.get_chart_path(symbol, timeframe)
    
    return f"Chart for {symbol} ({timeframe}) plotted and saved to {chart_path}"

def plot_all_charts(symbol: str) -> str:
    """Plot charts for all timeframes for a specific symbol.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        
    Returns:
        String containing information about all charts
    """
    results = []
    for timeframe in _scraper.TIMEFRAMES:
        results.append(plot_chart(symbol, timeframe))
    
    return "\n".join(results)
