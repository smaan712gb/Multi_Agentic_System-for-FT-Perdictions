import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union

class TechnicalIndicators:
    """
    A tool for calculating technical indicators for financial data
    """
    
    def __init__(self):
        """
        Initialize the TechnicalIndicators class
        """
        pass
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate the Relative Strength Index (RSI)
        
        Args:
            data: DataFrame containing price data with 'Close' column
            period: Period for RSI calculation (default: 14)
            
        Returns:
            Series containing RSI values
        """
        # Handle case where data['Close'] is a DataFrame rather than a Series
        close_series = data['Close'].iloc[:, 0] if isinstance(data['Close'], pd.DataFrame) else data['Close']
        
        # Calculate price changes
        delta = close_series.diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # Calculate RS
        rs = avg_gain / avg_loss
        
        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, data: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, pd.Series]:
        """
        Calculate the Moving Average Convergence Divergence (MACD)
        
        Args:
            data: DataFrame containing price data with 'Close' column
            fast_period: Period for fast EMA (default: 12)
            slow_period: Period for slow EMA (default: 26)
            signal_period: Period for signal line (default: 9)
            
        Returns:
            Dictionary containing MACD line, signal line, and histogram
        """
        # Handle case where data['Close'] is a DataFrame rather than a Series
        close_series = data['Close'].iloc[:, 0] if isinstance(data['Close'], pd.DataFrame) else data['Close']
        
        # Calculate EMAs
        ema_fast = close_series.ewm(span=fast_period, adjust=False).mean()
        ema_slow = close_series.ewm(span=slow_period, adjust=False).mean()
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return {
            'macd_line': macd_line,
            'signal_line': signal_line,
            'histogram': histogram
        }
    
    def calculate_vwap(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate the Volume Weighted Average Price (VWAP)
        
        Args:
            data: DataFrame containing price data with 'High', 'Low', 'Close', and 'Volume' columns
            
        Returns:
            Series containing VWAP values
        """
        # Handle case where data columns are DataFrames rather than Series
        high_series = data['High'].iloc[:, 0] if isinstance(data['High'], pd.DataFrame) else data['High']
        low_series = data['Low'].iloc[:, 0] if isinstance(data['Low'], pd.DataFrame) else data['Low']
        close_series = data['Close'].iloc[:, 0] if isinstance(data['Close'], pd.DataFrame) else data['Close']
        volume_series = data['Volume'].iloc[:, 0] if isinstance(data['Volume'], pd.DataFrame) else data['Volume']
        
        # Calculate typical price
        typical_price = (high_series + low_series + close_series) / 3
        
        # Calculate VWAP
        vwap = (typical_price * volume_series).cumsum() / volume_series.cumsum()
        
        return vwap
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            data: DataFrame containing price data with 'Close' column
            period: Period for moving average (default: 20)
            std_dev: Number of standard deviations (default: 2)
            
        Returns:
            Dictionary containing upper band, middle band, and lower band
        """
        # Handle case where data['Close'] is a DataFrame rather than a Series
        close_series = data['Close'].iloc[:, 0] if isinstance(data['Close'], pd.DataFrame) else data['Close']
        
        # Calculate middle band (SMA)
        middle_band = close_series.rolling(window=period).mean()
        
        # Calculate standard deviation
        std = close_series.rolling(window=period).std()
        
        # Calculate upper and lower bands
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return {
            'upper_band': upper_band,
            'middle_band': middle_band,
            'lower_band': lower_band
        }
    
    def calculate_all_indicators(self, data: pd.DataFrame) -> Dict[str, Union[pd.Series, Dict[str, pd.Series]]]:
        """
        Calculate all technical indicators
        
        Args:
            data: DataFrame containing price data with 'Open', 'High', 'Low', 'Close', and 'Volume' columns
            
        Returns:
            Dictionary containing all technical indicators
        """
        # Check if data has required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise ValueError(f"Data is missing required columns: {missing_columns}")
        
        # Check if there are enough data points for calculating indicators
        min_data_points = 30  # Minimum number of data points needed for reliable indicators
        if len(data) < min_data_points:
            print(f"Warning: Only {len(data)} data points available. At least {min_data_points} recommended for reliable indicators.")
        
        # Calculate all indicators
        indicators = {}
        
        try:
            # RSI (requires at least 14 data points)
            if len(data) >= 14:
                indicators['rsi'] = self.calculate_rsi(data)
            else:
                indicators['rsi'] = pd.Series(dtype='float64')  # Empty series
                print(f"Warning: Not enough data points ({len(data)}) for RSI calculation. Minimum 14 required.")
            
            # MACD (requires at least 26 data points)
            if len(data) >= 26:
                indicators['macd'] = self.calculate_macd(data)
            else:
                indicators['macd'] = {
                    'macd_line': pd.Series(dtype='float64'),
                    'signal_line': pd.Series(dtype='float64'),
                    'histogram': pd.Series(dtype='float64')
                }
                print(f"Warning: Not enough data points ({len(data)}) for MACD calculation. Minimum 26 required.")
            
            # VWAP (requires at least 1 data point)
            indicators['vwap'] = self.calculate_vwap(data)
            
            # Bollinger Bands (requires at least 20 data points)
            if len(data) >= 20:
                indicators['bollinger_bands'] = self.calculate_bollinger_bands(data)
            else:
                indicators['bollinger_bands'] = {
                    'upper_band': pd.Series(dtype='float64'),
                    'middle_band': pd.Series(dtype='float64'),
                    'lower_band': pd.Series(dtype='float64')
                }
                print(f"Warning: Not enough data points ({len(data)}) for Bollinger Bands calculation. Minimum 20 required.")
        except Exception as e:
            print(f"Error calculating indicators: {str(e)}")
            # Provide empty indicators in case of error
            indicators = {
                'rsi': pd.Series(dtype='float64'),
                'macd': {
                    'macd_line': pd.Series(dtype='float64'),
                    'signal_line': pd.Series(dtype='float64'),
                    'histogram': pd.Series(dtype='float64')
                },
                'vwap': pd.Series(dtype='float64'),
                'bollinger_bands': {
                    'upper_band': pd.Series(dtype='float64'),
                    'middle_band': pd.Series(dtype='float64'),
                    'lower_band': pd.Series(dtype='float64')
                }
            }
        
        return indicators
    
    def format_indicators_for_agents(self, data: pd.DataFrame) -> str:
        """
        Calculate and format technical indicators for agents
        
        Args:
            data: DataFrame containing price data with 'Open', 'High', 'Low', 'Close', and 'Volume' columns
            
        Returns:
            Formatted string containing technical indicators
        """
        try:
            # Calculate indicators
            indicators = self.calculate_all_indicators(data)
            
            # Get the latest values
            latest_rsi = indicators['rsi'].iloc[-1] if not indicators['rsi'].empty else None
            latest_macd_line = indicators['macd']['macd_line'].iloc[-1] if not indicators['macd']['macd_line'].empty else None
            latest_macd_signal = indicators['macd']['signal_line'].iloc[-1] if not indicators['macd']['signal_line'].empty else None
            latest_macd_hist = indicators['macd']['histogram'].iloc[-1] if not indicators['macd']['histogram'].empty else None
            latest_vwap = indicators['vwap'].iloc[-1] if not indicators['vwap'].empty else None
            latest_bb_upper = indicators['bollinger_bands']['upper_band'].iloc[-1] if not indicators['bollinger_bands']['upper_band'].empty else None
            latest_bb_middle = indicators['bollinger_bands']['middle_band'].iloc[-1] if not indicators['bollinger_bands']['middle_band'].empty else None
            latest_bb_lower = indicators['bollinger_bands']['lower_band'].iloc[-1] if not indicators['bollinger_bands']['lower_band'].empty else None
            
            # Check if we have enough data points for meaningful indicators
            if len(data) < 30:
                data_warning = f"\nNote: Limited data points ({len(data)}) may affect indicator reliability. Some indicators may not be available."
            else:
                data_warning = ""
            
            # Format the indicators
            formatted_indicators = f"""
Technical Indicators:{data_warning}
- RSI: {latest_rsi:.2f if latest_rsi is not None else 'N/A'}
- MACD:
  - MACD Line: {latest_macd_line:.2f if latest_macd_line is not None else 'N/A'}
  - Signal Line: {latest_macd_signal:.2f if latest_macd_signal is not None else 'N/A'}
  - Histogram: {latest_macd_hist:.2f if latest_macd_hist is not None else 'N/A'}
- VWAP: {latest_vwap:.2f if latest_vwap is not None else 'N/A'}
- Bollinger Bands:
  - Upper Band: {latest_bb_upper:.2f if latest_bb_upper is not None else 'N/A'}
  - Middle Band: {latest_bb_middle:.2f if latest_bb_middle is not None else 'N/A'}
  - Lower Band: {latest_bb_lower:.2f if latest_bb_lower is not None else 'N/A'}
"""
        except Exception as e:
            formatted_indicators = f"""
Technical Indicators:
Note: Unable to calculate technical indicators due to data format or insufficient data points.
Error details: {str(e)}
"""
        
        return formatted_indicators
