import pandas as pd
from typing import Dict, Any, List, Optional, Union
from .technical_indicators import TechnicalIndicators

# Initialize the technical indicators calculator
technical_indicators = TechnicalIndicators()

def calculate_indicators(data: pd.DataFrame) -> Dict[str, Union[pd.Series, Dict[str, pd.Series]]]:
    """
    Calculate technical indicators for the given data
    
    Args:
        data: DataFrame containing price data with 'Open', 'High', 'Low', 'Close', and 'Volume' columns
        
    Returns:
        Dictionary containing technical indicators
    """
    return technical_indicators.calculate_all_indicators(data)

def format_indicators(data: pd.DataFrame) -> str:
    """
    Calculate and format technical indicators for agents
    
    Args:
        data: DataFrame containing price data with 'Open', 'High', 'Low', 'Close', and 'Volume' columns
        
    Returns:
        Formatted string containing technical indicators
    """
    return technical_indicators.format_indicators_for_agents(data)
