import requests
import json
import os

# Get the API key from the volume profile analyzer
with open(os.path.join("tools", "volume_profile", "agno_tool.py"), "r") as f:
    for line in f:
        if "ALPHA_VANTAGE_API_KEY" in line:
            api_key = line.strip().split("=")[1].strip('"\'')
            break

def search_symbol(keywords):
    """
    Search for symbols using Alpha Vantage SYMBOL_SEARCH API
    
    Args:
        keywords: Keywords to search for
        
    Returns:
        List of matching symbols
    """
    url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={keywords}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if "bestMatches" in data:
        return data["bestMatches"]
    else:
        print(f"Error: {data}")
        return []

# Search for NASDAQ 100 related symbols
print("Searching for NASDAQ 100 related symbols...")
nasdaq_symbols = search_symbol("NASDAQ 100")
print(json.dumps(nasdaq_symbols, indent=2))
print("\n")

# Search for S&P 500 related symbols
print("Searching for S&P 500 related symbols...")
sp500_symbols = search_symbol("S&P 500")
print(json.dumps(sp500_symbols, indent=2))
print("\n")

# Search for Dow Jones related symbols
print("Searching for Dow Jones related symbols...")
dow_symbols = search_symbol("Dow Jones")
print(json.dumps(dow_symbols, indent=2))
print("\n")

# Search for specific ETFs
print("Searching for QQQ...")
qqq_symbols = search_symbol("QQQ")
print(json.dumps(qqq_symbols, indent=2))
print("\n")

print("Searching for SPY...")
spy_symbols = search_symbol("SPY")
print(json.dumps(spy_symbols, indent=2))
print("\n")

print("Searching for DIA...")
dia_symbols = search_symbol("DIA")
print(json.dumps(dia_symbols, indent=2))
print("\n")

# Search for futures symbols
print("Searching for NQ futures...")
nq_symbols = search_symbol("NQ futures")
print(json.dumps(nq_symbols, indent=2))
print("\n")

print("Searching for ES futures...")
es_symbols = search_symbol("ES futures")
print(json.dumps(es_symbols, indent=2))
print("\n")

print("Searching for YM futures...")
ym_symbols = search_symbol("YM futures")
print(json.dumps(ym_symbols, indent=2))
