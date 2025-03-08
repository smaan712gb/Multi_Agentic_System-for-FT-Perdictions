from typing import Dict, Any, List, Optional
import os
import json
from .volume_profile import VolumeProfileAnalyzer

# Get Alpha Vantage API key from environment variables
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "4M6VASN5R8SRDP29")

# Create a single instance of the VolumeProfileAnalyzer
_analyzer = VolumeProfileAnalyzer(api_key=ALPHA_VANTAGE_API_KEY, data_dir="data")

def get_volume_profile(symbol: str, interval: str = "60min") -> str:
    """Get volume profile analysis for a specific symbol and interval.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        interval: Time interval between data points (1min, 5min, 15min, 30min, 60min)
        
    Returns:
        String containing volume profile analysis
    """
    return _analyzer.format_volume_profile_for_agents(symbol, interval)

def analyze_volume_profile(symbol: str, interval: str = "5min") -> Dict[str, Any]:
    """Analyze volume profile for a specific symbol and interval.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        interval: Time interval between data points (1min, 5min, 15min, 30min, 60min)
        
    Returns:
        Dictionary containing volume profile analysis results
    """
    return _analyzer.analyze_volume_profile(symbol, interval)

def get_intraday_data(symbol: str, interval: str = "5min") -> str:
    """Get intraday data for a specific symbol and interval.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        interval: Time interval between data points (1min, 5min, 15min, 30min, 60min)
        
    Returns:
        String containing information about the intraday data
    """
    data = _analyzer.get_intraday_data(symbol, interval)
    
    # Get basic statistics
    stats = {
        "symbol": symbol,
        "interval": interval,
        "start_date": data.index[0].strftime("%Y-%m-%d %H:%M:%S") if len(data) > 0 else None,
        "end_date": data.index[-1].strftime("%Y-%m-%d %H:%M:%S") if len(data) > 0 else None,
        "num_points": len(data),
        "latest_close": float(data['Close'].iloc[-1]) if len(data) > 0 else None,
        "data_path": os.path.join("data", symbol, "volume_profile", f"intraday_{interval}.csv")
    }
    
    # Return a string representation
    return f"""Intraday data for {symbol} ({interval}): {len(data)} data points from {stats['start_date']} to {stats['end_date']}. 
Latest close: {stats['latest_close']}. 
Data saved to {stats['data_path']}"""

def plot_volume_profile(symbol: str, interval: str = "5min") -> str:
    """Plot volume profile for a specific symbol and interval.
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        interval: Time interval between data points (1min, 5min, 15min, 30min, 60min)
        
    Returns:
        String containing information about the volume profile chart
    """
    # Get intraday data
    data = _analyzer.get_intraday_data(symbol, interval)
    
    # Calculate volume profile
    volume_profile = _analyzer.calculate_volume_profile(data)
    
    # Plot volume profile
    _analyzer.plot_volume_profile(symbol, data, volume_profile)
    
    # Return a string representation
    chart_path = os.path.join("data", symbol, "volume_profile", "charts", "volume_profile.png")
    return f"Volume profile for {symbol} ({interval}) plotted and saved to {chart_path}"
