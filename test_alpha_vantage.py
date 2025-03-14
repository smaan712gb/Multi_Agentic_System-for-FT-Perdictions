import requests
import json
import pandas as pd
from tools.volume_profile.agno_tool import ALPHA_VANTAGE_API_KEY

def test_alpha_vantage(symbol, interval="5min"):
    """
    Test the Alpha Vantage API for a specific symbol and interval
    
    Args:
        symbol: The symbol to test
        interval: Time interval between data points (1min, 5min, 15min, 30min, 60min)
    """
    # Alpha Vantage API endpoint for intraday data
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&outputsize=full&adjusted=true&extended_hours=true&apikey={ALPHA_VANTAGE_API_KEY}"
    
    print(f"Testing Alpha Vantage API for symbol {symbol} with interval {interval}...")
    print(f"URL: {url}")
    
    # Get data from Alpha Vantage
    response = requests.get(url)
    data = response.json()
    
    # Check if there's an error
    if "Error Message" in data:
        print(f"Error: {data['Error Message']}")
        return
    
    # Check if there's information
    if "Information" in data:
        print(f"Information: {data['Information']}")
        return
    
    # Parse the data
    time_series_key = f"Time Series ({interval})"
    if time_series_key not in data:
        print(f"Warning: No data found for {symbol} with interval {interval} from Alpha Vantage API")
        print(f"Response: {json.dumps(data, indent=2)}")
        return
    
    time_series = data[time_series_key]
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(time_series, orient="index")
    
    # Print the first few rows
    print(f"Data for {symbol} with interval {interval}:")
    print(f"Number of data points: {len(df)}")
    print(f"First few rows:")
    print(df.head())
    
    # Print the last few rows
    print(f"Last few rows:")
    print(df.tail())

# Test QQQ (NASDAQ 100 ETF)
test_alpha_vantage("QQQ", "5min")

# Test SPY (S&P 500 ETF)
test_alpha_vantage("SPY", "5min")

# Test DIA (Dow Jones ETF)
test_alpha_vantage("DIA", "5min")
