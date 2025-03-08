import os
import sys
import json
import webbrowser
from datetime import datetime

def view_results(symbol=None):
    """
    View the latest analysis results
    
    Args:
        symbol: The futures symbol (NQ, ES, YM) to view results for. If None, show all symbols.
    """
    data_dir = "data"
    mean_analysis_dir = os.path.join(data_dir, "mean_analysis")
    
    if not os.path.exists(mean_analysis_dir):
        print(f"Mean analysis directory '{mean_analysis_dir}' does not exist.")
        print("Please run the analysis first.")
        return
    
    symbols = ["NQ", "ES", "YM"] if symbol is None else [symbol.upper()]
    
    # Validate symbol
    if symbol is not None and symbol.upper() not in ["NQ", "ES", "YM"]:
        print(f"Invalid symbol: {symbol}. Choose from NQ, ES, YM.")
        return
    
    # Check if results exist for the specified symbols
    available_symbols = []
    for sym in symbols:
        sym_dir = os.path.join(mean_analysis_dir, sym)
        if os.path.exists(sym_dir):
            available_symbols.append(sym)
    
    if not available_symbols:
        print(f"No results found for symbol(s): {', '.join(symbols)}")
        print("Please run the analysis first.")
        return
    
    # Print summary of available results
    print("Available results:")
    for sym in available_symbols:
        sym_dir = os.path.join(mean_analysis_dir, sym)
        html_path = os.path.join(sym_dir, "analysis.html")
        
        if os.path.exists(html_path):
            # Get the modification time of the HTML file
            mod_time = datetime.fromtimestamp(os.path.getmtime(html_path))
            mod_time_str = mod_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Get the predictions for each timeframe
            predictions = {}
            for timeframe in ["intraday", "5d", "30d"]:
                json_path = os.path.join(sym_dir, f"{timeframe}.json")
                if os.path.exists(json_path):
                    with open(json_path, "r") as f:
                        data = json.load(f)
                        predictions[timeframe] = data.get("prediction_label", "Unknown")
            
            # Print summary
            print(f"\n{sym} (Last updated: {mod_time_str}):")
            for timeframe, prediction in predictions.items():
                print(f"  - {timeframe}: {prediction}")
            
            print(f"  HTML report: {html_path}")
    
    # Ask if the user wants to open the HTML reports
    print("\nDo you want to open the HTML reports in your browser? (y/n)")
    choice = input().lower()
    if choice == 'y':
        for sym in available_symbols:
            html_path = os.path.join(mean_analysis_dir, sym, "analysis.html")
            if os.path.exists(html_path):
                print(f"Opening {html_path}...")
                try:
                    webbrowser.open(f"file://{os.path.abspath(html_path)}")
                except Exception as e:
                    print(f"Error opening {html_path}: {e}")

def main():
    """
    Main function
    """
    if len(sys.argv) > 1:
        symbol = sys.argv[1].upper()
        view_results(symbol)
    else:
        view_results()

if __name__ == "__main__":
    main()
