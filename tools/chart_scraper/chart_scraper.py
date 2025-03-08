import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any, Optional, Tuple, Union

class ChartScraper:
    """
    A tool for scraping chart data for futures markets (NQ, ES, YM)
    """
    
    # Mapping of futures symbols to their Yahoo Finance tickers
    FUTURES_MAPPING = {
        "NQ": "NQ=F",  # NASDAQ 100 E-Mini Futures
        "ES": "ES=F",  # S&P 500 E-Mini Futures
        "YM": "YM=F",  # Dow Jones E-Mini Futures
    }
    
    # Timeframes available for analysis with their Yahoo Finance period and interval
    TIMEFRAMES = {
        "intraday": {"period": "1d", "interval": "1m"},   # 1-minute intervals for intraday
        "5d": {"period": "5d", "interval": "5m"},         # 5-minute intervals for 5-day (more data points)
        "30d": {"period": "1mo", "interval": "60m"},      # 60-minute intervals for 30-day (more data points)
        "60d": {"period": "2mo", "interval": "60m"},      # 60-minute intervals for 60-day (more data points)
        "90d": {"period": "3mo", "interval": "60m"},      # 60-minute intervals for 90-day (more data points)
        "6mo": {"period": "6mo", "interval": "1d"},       # Daily intervals for 6-month
        "1y": {"period": "1y", "interval": "1d"}          # Daily intervals for 1-year
    }
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the ChartScraper
        
        Args:
            data_dir: Directory to store the scraped data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def get_ticker_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """
        Get ticker data for a specific symbol and timeframe
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            timeframe: The timeframe to fetch data for
            
        Returns:
            DataFrame containing the ticker data
        """
        if symbol not in self.FUTURES_MAPPING:
            raise ValueError(f"Symbol {symbol} not supported. Choose from {list(self.FUTURES_MAPPING.keys())}")
        
        if timeframe not in self.TIMEFRAMES:
            raise ValueError(f"Timeframe {timeframe} not supported. Choose from {list(self.TIMEFRAMES.keys())}")
        
        ticker = self.FUTURES_MAPPING[symbol]
        period = self.TIMEFRAMES[timeframe]["period"]
        interval = self.TIMEFRAMES[timeframe]["interval"]
        
        # Get data from yfinance
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        
        # Print the number of data points for debugging
        print(f"Downloaded {len(data)} data points for {symbol} {timeframe} (interval: {interval})")
        
        # Save data to CSV
        os.makedirs(os.path.join(self.data_dir, symbol), exist_ok=True)
        csv_path = os.path.join(self.data_dir, symbol, f"{timeframe}.csv")
        data.to_csv(csv_path)
        
        return data
    
    def get_all_timeframes(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """
        Get data for all timeframes for a specific symbol
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            
        Returns:
            Dictionary mapping timeframes to DataFrames
        """
        result = {}
        for timeframe in self.TIMEFRAMES:
            result[timeframe] = self.get_ticker_data(symbol, timeframe)
        return result
    
    def plot_chart(self, symbol: str, timeframe: str, save: bool = True) -> plt.Figure:
        """
        Plot an advanced chart for a specific symbol and timeframe
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            timeframe: The timeframe to plot
            save: Whether to save the chart to disk
            
        Returns:
            Matplotlib figure object
        """
        data = self.get_ticker_data(symbol, timeframe)
        
        # Create figure with 2 subplots (price and volume)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
        
        # Plot the price data (OHLC)
        ax1.plot(data.index, data['Close'], label=f"{symbol} Close Price", color='blue')
        
        # Add moving averages (common in advanced charts)
        if len(data) >= 20:
            ma20 = data['Close'].rolling(window=20).mean()
            ax1.plot(data.index, ma20, label='20-day MA', color='orange', linestyle='--')
        
        if len(data) >= 50:
            ma50 = data['Close'].rolling(window=50).mean()
            ax1.plot(data.index, ma50, label='50-day MA', color='red', linestyle='--')
        
        # Add price labels and grid
        ax1.set_title(f"{symbol} Futures - {timeframe} (Advanced Chart)")
        ax1.set_ylabel("Price")
        ax1.legend(loc='upper left')
        ax1.grid(True)
        
        # Plot volume in the bottom subplot
        try:
            # Handle case where Volume might be a DataFrame rather than a Series
            volume_series = data['Volume'].iloc[:, 0] if isinstance(data['Volume'], pd.DataFrame) else data['Volume']
            ax2.bar(data.index, volume_series, label='Volume', color='green', alpha=0.5)
        except Exception as e:
            print(f"Warning: Could not plot volume data: {str(e)}")
            # Create an empty plot for volume if there's an error
            ax2.text(0.5, 0.5, "Volume data not available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax2.transAxes)
        
        ax2.set_ylabel("Volume")
        ax2.set_xlabel("Date")
        ax2.grid(True)
        
        # Format x-axis dates
        fig.autofmt_xdate()
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the figure if requested
        if save:
            os.makedirs(os.path.join(self.data_dir, symbol, "charts"), exist_ok=True)
            fig_path = os.path.join(self.data_dir, symbol, "charts", f"{timeframe}.png")
            fig.savefig(fig_path)
        
        return fig
    
    def get_data_path(self, symbol: str, timeframe: str) -> str:
        """
        Get the path to the CSV file for a specific symbol and timeframe
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            timeframe: The timeframe
            
        Returns:
            Path to the CSV file
        """
        return os.path.join(self.data_dir, symbol, f"{timeframe}.csv")
    
    def get_chart_path(self, symbol: str, timeframe: str) -> str:
        """
        Get the path to the chart image for a specific symbol and timeframe
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            timeframe: The timeframe
            
        Returns:
            Path to the chart image
        """
        return os.path.join(self.data_dir, symbol, "charts", f"{timeframe}.png")
