import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional, Tuple, Union
import os
from datetime import datetime, timedelta

class VolumeProfileAnalyzer:
    """
    A tool for analyzing volume profile for futures markets (NQ, ES, YM)
    """
    
    # Mapping of futures symbols to their Alpha Vantage tickers
    FUTURES_MAPPING = {
        "NQ": "QQQ",   # Invesco QQQ Trust (proxy for NASDAQ 100)
        "ES": "SPY",   # SPDR S&P 500 ETF Trust (proxy for S&P 500)
        "YM": "DIA",   # SPDR Dow Jones Industrial Average ETF Trust (proxy for Dow Jones)
    }
    
    def __init__(self, api_key: str, data_dir: str = "data"):
        """
        Initialize the VolumeProfileAnalyzer
        
        Args:
            api_key: Alpha Vantage API key
            data_dir: Directory to store the data
        """
        self.api_key = api_key
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def get_intraday_data(self, symbol: str, interval: str = "5min", output_size: str = "full", adjusted: bool = True, extended_hours: bool = True) -> pd.DataFrame:
        """
        Get intraday data for a specific symbol
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            interval: Time interval between data points (1min, 5min, 15min, 30min, 60min)
            output_size: Size of the data (compact or full)
            adjusted: Whether to adjust for splits and dividends
            extended_hours: Whether to include extended hours data
            
        Returns:
            DataFrame containing the intraday data
        """
        if symbol not in self.FUTURES_MAPPING:
            raise ValueError(f"Symbol {symbol} not supported. Choose from {list(self.FUTURES_MAPPING.keys())}")
        
        ticker = self.FUTURES_MAPPING[symbol]
        
        # Alpha Vantage API endpoint for intraday data
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval={interval}&outputsize={output_size}&adjusted={str(adjusted).lower()}&extended_hours={str(extended_hours).lower()}&apikey={self.api_key}"
        
        # Get data from Alpha Vantage
        response = requests.get(url)
        data = response.json()
        
        # Check if there's an error
        if "Error Message" in data:
            raise ValueError(f"Alpha Vantage API error: {data['Error Message']}")
        
        # Parse the data
        time_series_key = f"Time Series ({interval})"
        if time_series_key not in data:
            print(f"Warning: No data found for {symbol} with interval {interval} from Alpha Vantage API")
            # Return an empty DataFrame with the expected columns
            return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        
        time_series = data[time_series_key]
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient="index")
        
        # Convert column names
        df.columns = [col.split(". ")[1] for col in df.columns]
        
        # Convert to numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])
        
        # Sort by date
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Rename columns to match our convention
        df = df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        })
        
        # Save data to CSV
        os.makedirs(os.path.join(self.data_dir, symbol, "volume_profile"), exist_ok=True)
        csv_path = os.path.join(self.data_dir, symbol, "volume_profile", f"intraday_{interval}.csv")
        df.to_csv(csv_path)
        
        return df
    
    def calculate_volume_profile(self, data: pd.DataFrame, num_bins: int = 20) -> pd.DataFrame:
        """
        Calculate volume profile for the given data
        
        Args:
            data: DataFrame containing price data with 'High', 'Low', 'Close', and 'Volume' columns
            num_bins: Number of price bins to use
            
        Returns:
            DataFrame containing the volume profile
        """
        # Check if data is empty
        if data.empty:
            # Create an empty volume profile DataFrame with the expected columns
            volume_profile = pd.DataFrame(columns=['PriceLow', 'PriceHigh', 'PriceMid', 'Volume', 'ValueArea', 'PointOfControl'])
            # Add a single row with default values
            volume_profile.loc[0] = [0, 0, 0, 0, False, True]
            return volume_profile
            
        # Calculate price range
        price_high = data['High'].max()
        price_low = data['Low'].min()
        
        # Create price bins
        price_bins = np.linspace(price_low, price_high, num_bins + 1)
        
        # Initialize volume profile
        volume_profile = pd.DataFrame(index=range(num_bins))
        volume_profile['PriceLow'] = price_bins[:-1]
        volume_profile['PriceHigh'] = price_bins[1:]
        volume_profile['PriceMid'] = (volume_profile['PriceLow'] + volume_profile['PriceHigh']) / 2
        volume_profile['Volume'] = 0.0  # Initialize as float
        
        # Calculate volume for each price bin
        for i, row in data.iterrows():
            # Find which bins this candle spans
            low_bin = np.searchsorted(price_bins, row['Low']) - 1
            high_bin = np.searchsorted(price_bins, row['High'])
            
            # Distribute volume across bins
            if low_bin == high_bin - 1:
                # Candle fits in one bin
                volume_profile.loc[low_bin, 'Volume'] += row['Volume']
            else:
                # Candle spans multiple bins
                price_range = row['High'] - row['Low']
                for bin_idx in range(low_bin, high_bin):
                    if bin_idx < 0 or bin_idx >= num_bins:
                        continue
                    
                    # Calculate how much of the candle is in this bin
                    bin_low = max(volume_profile.loc[bin_idx, 'PriceLow'], row['Low'])
                    bin_high = min(volume_profile.loc[bin_idx, 'PriceHigh'], row['High'])
                    bin_range = bin_high - bin_low
                    
                    # Allocate volume proportionally
                    bin_volume = row['Volume'] * (bin_range / price_range)
                    volume_profile.loc[bin_idx, 'Volume'] += float(bin_volume)
        
        # Sort by price
        volume_profile = volume_profile.sort_values('PriceMid')
        
        # Calculate value area (70% of volume)
        total_volume = volume_profile['Volume'].sum()
        value_area_volume = total_volume * 0.7
        
        # Sort by volume to find point of control
        volume_profile_sorted = volume_profile.sort_values('Volume', ascending=False)
        
        # Point of Control (price level with highest volume)
        poc_idx = volume_profile_sorted.index[0]
        poc_price = volume_profile.loc[poc_idx, 'PriceMid']
        
        # Calculate Value Area
        cumulative_volume = 0
        value_area_indices = []
        
        for idx in volume_profile_sorted.index:
            cumulative_volume += volume_profile_sorted.loc[idx, 'Volume']
            value_area_indices.append(idx)
            
            if cumulative_volume >= value_area_volume:
                break
        
        # Mark Value Area
        volume_profile['ValueArea'] = False
        volume_profile.loc[value_area_indices, 'ValueArea'] = True
        
        # Mark Point of Control
        volume_profile['PointOfControl'] = False
        volume_profile.loc[poc_idx, 'PointOfControl'] = True
        
        return volume_profile
    
    def plot_volume_profile(self, symbol: str, data: pd.DataFrame, volume_profile: pd.DataFrame, save: bool = True) -> plt.Figure:
        """
        Plot volume profile alongside price chart
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            data: DataFrame containing price data
            volume_profile: DataFrame containing volume profile data
            save: Whether to save the chart to disk
            
        Returns:
            Matplotlib figure object
        """
        # Create figure with 2 subplots (price and volume profile)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8), gridspec_kw={'width_ratios': [3, 1]})
        
        # Check if data is empty
        if data.empty:
            ax1.text(0.5, 0.5, f"No data available for {symbol}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax1.transAxes, fontsize=14)
            ax2.text(0.5, 0.5, "No volume profile available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax2.transAxes, fontsize=14)
            
            # Add title
            fig.suptitle(f"No Data Available for {symbol}", fontsize=16)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save the figure if requested
            if save:
                os.makedirs(os.path.join(self.data_dir, symbol, "volume_profile", "charts"), exist_ok=True)
                fig_path = os.path.join(self.data_dir, symbol, "volume_profile", "charts", "volume_profile.png")
                fig.savefig(fig_path)
            
            return fig
        
        # Plot the price data
        ax1.plot(data.index, data['Close'], label=f"{symbol} Close Price", color='blue')
        
        # Add title and labels
        ax1.set_title(f"{symbol} Futures with Volume Profile")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Price")
        ax1.legend()
        ax1.grid(True)
        
        # Format x-axis dates
        fig.autofmt_xdate()
        
        # Plot volume profile as horizontal bars
        colors = ['green' if row['ValueArea'] else 'gray' for _, row in volume_profile.iterrows()]
        colors = ['red' if row['PointOfControl'] else color for color, (_, row) in zip(colors, volume_profile.iterrows())]
        
        ax2.barh(volume_profile['PriceMid'], volume_profile['Volume'], 
                height=(volume_profile['PriceHigh'] - volume_profile['PriceLow']), 
                color=colors, alpha=0.6)
        
        # Add labels
        ax2.set_title("Volume Profile")
        ax2.set_xlabel("Volume")
        
        # Set y-axis limits to match price chart
        ax2.set_ylim(ax1.get_ylim())
        
        # Add legend for volume profile
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='red', alpha=0.6, label='Point of Control'),
            Patch(facecolor='green', alpha=0.6, label='Value Area'),
            Patch(facecolor='gray', alpha=0.6, label='Low Volume')
        ]
        ax2.legend(handles=legend_elements, loc='upper right')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the figure if requested
        if save:
            os.makedirs(os.path.join(self.data_dir, symbol, "volume_profile", "charts"), exist_ok=True)
            fig_path = os.path.join(self.data_dir, symbol, "volume_profile", "charts", "volume_profile.png")
            fig.savefig(fig_path)
        
        return fig
    
    def analyze_volume_profile(self, symbol: str, interval: str = "5min") -> Dict[str, Any]:
        """
        Analyze volume profile for a specific symbol
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            interval: Time interval between data points (1min, 5min, 15min, 30min, 60min)
            
        Returns:
            Dictionary containing the analysis results
        """
        # Get intraday data
        data = self.get_intraday_data(symbol, interval)
        
        # Check if data is empty
        if data.empty:
            print(f"Warning: No data available for {symbol} with interval {interval}")
            # Return default values
            return {
                "symbol": symbol,
                "interval": interval,
                "current_price": 0,
                "point_of_control": 0,
                "value_area_high": 0,
                "value_area_low": 0,
                "position_relative_to_poc": "unknown",
                "position_relative_to_va": "unknown",
                "volume_profile_path": "",
                "analysis_timestamp": datetime.now().isoformat(),
                "data_available": False
            }
        
        # Calculate volume profile
        volume_profile = self.calculate_volume_profile(data)
        
        # Plot volume profile
        self.plot_volume_profile(symbol, data, volume_profile)
        
        # Get Point of Control
        poc_row = volume_profile[volume_profile['PointOfControl']].iloc[0]
        poc_price = poc_row['PriceMid']
        
        # Get Value Area
        value_area = volume_profile[volume_profile['ValueArea']]
        value_area_high = value_area['PriceHigh'].max() if not value_area.empty else poc_price
        value_area_low = value_area['PriceLow'].min() if not value_area.empty else poc_price
        
        # Get current price
        current_price = data['Close'].iloc[-1]
        
        # Determine if current price is above or below POC
        position_relative_to_poc = "above" if current_price > poc_price else "below"
        
        # Determine if current price is inside or outside Value Area
        in_value_area = value_area_low <= current_price <= value_area_high
        position_relative_to_va = "inside" if in_value_area else "outside"
        
        # Create analysis results
        results = {
            "symbol": symbol,
            "interval": interval,
            "current_price": current_price,
            "point_of_control": poc_price,
            "value_area_high": value_area_high,
            "value_area_low": value_area_low,
            "position_relative_to_poc": position_relative_to_poc,
            "position_relative_to_va": position_relative_to_va,
            "volume_profile_path": os.path.join(self.data_dir, symbol, "volume_profile", "charts", "volume_profile.png"),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return results
    
    def format_volume_profile_for_agents(self, symbol: str, interval: str = "5min") -> str:
        """
        Format volume profile analysis for agents
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            interval: Time interval between data points (1min, 5min, 15min, 30min, 60min)
            
        Returns:
            Formatted string containing volume profile analysis
        """
        # Analyze volume profile
        results = self.analyze_volume_profile(symbol, interval)
        
        # Check if data is available
        if 'data_available' in results and results['data_available'] == False:
            return f"""
Volume Profile Analysis:
No volume profile data available for {symbol} with interval {interval}.
This could be due to API limitations or the symbol not being available through Alpha Vantage.
"""
        
        # Format the results
        formatted_results = f"""
Volume Profile Analysis:
- Point of Control (POC): {results['point_of_control']:.2f} (price level with highest trading volume)
- Value Area High (VAH): {results['value_area_high']:.2f}
- Value Area Low (VAL): {results['value_area_low']:.2f}
- Current Price: {results['current_price']:.2f}
- Position: Price is {results['position_relative_to_poc']} POC and {results['position_relative_to_va']} Value Area

Trading Implications:
- POC acts as a magnet for price and often serves as support/resistance
- Value Area represents where 70% of trading occurred, suggesting fair value range
- Price tends to revert to Value Area when trading outside it
- Breakouts above VAH or below VAL with strong volume suggest potential trend continuation
"""
        
        return formatted_results
