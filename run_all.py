import os
import sys
import subprocess
from datetime import datetime

def run_all():
    """
    Run analysis for all symbols
    """
    symbols = ["NQ", "ES", "YM"]
    
    print(f"Starting analysis for all symbols: {', '.join(symbols)}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    for symbol in symbols:
        print(f"\nRunning analysis for {symbol}...")
        try:
            subprocess.run([sys.executable, "main.py", symbol], check=True)
            print(f"Analysis for {symbol} completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error running analysis for {symbol}: {e}")
        print("-" * 50)
    
    print("\nAll analyses completed.")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Print paths to interactive charts
    print("\nInteractive charts:")
    for symbol in symbols:
        html_path = os.path.join("data", "mean_analysis", symbol, "analysis.html")
        if os.path.exists(html_path):
            print(f"- {symbol}: {html_path}")

if __name__ == "__main__":
    run_all()
