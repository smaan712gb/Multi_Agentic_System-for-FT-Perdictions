from agno.agent import Agent, RunResponse
from agno.models.google import Gemini
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import our tools
from tools.chart_scraper.agno_tool import get_chart_data, get_all_timeframes, plot_chart, plot_all_charts
from tools.sentiment_analyzer.agno_tool import get_news, get_sentiment, summarize_news
from tools.technical_indicators.agno_tool import format_indicators
from tools.volume_profile.agno_tool import get_volume_profile

# Get the API key from the .env file
with open(os.path.join("agents", ".env"), "r") as f:
    for line in f:
        if line.startswith("GEMINI_API_KEY="):
            gemini_api_key = line.strip().split("=")[1]
            break

# Initialize the agent
agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp", api_key=gemini_api_key),
    name="Gemini Futures Analyst",
    role="Analyze futures markets (NQ, ES, YM) and make predictions based on chart data and market sentiment.",
    markdown=True
)

def analyze_futures(symbol: str) -> Dict[str, Any]:
    """
    Analyze futures for a specific symbol and make predictions
    
    Args:
        symbol: The futures symbol (NQ, ES, YM)
        
    Returns:
        Dictionary containing the analysis and predictions
    """
    # Create directories for predictions
    predictions_dir = os.path.join("data", "predictions", "gemini", symbol)
    os.makedirs(predictions_dir, exist_ok=True)
    
    # Get chart data, sentiment data, and volume profile
    chart_data = get_all_timeframes(symbol)
    sentiment_data = get_sentiment(symbol)
    volume_profile_data = get_volume_profile(symbol, interval="1min")
    
    # Prepare the prompt for the agent
    prompt = f"""
    You are a futures market analyst specializing in technical analysis and market sentiment.
    
    Please analyze the {symbol} futures market and make predictions for the following timeframes:
    - intraday
    - 5d
    - 30d
    
    Here is the chart data for each timeframe, including technical indicators (RSI, MACD, VWAP, Bollinger Bands) and basic technical analysis with moving averages:
    
    {chart_data}
    
    Here is the sentiment data:
    {sentiment_data}
    
    Here is the volume profile analysis:
    {volume_profile_data}
    
    IMPORTANT: Pay close attention to the number of data points available for each timeframe. The data includes:
    - intraday: ~1000 data points (1-minute intervals)
    - 5d: ~1300 data points (5-minute intervals)
    - 30d: ~450 data points (60-minute intervals)
    
    Also note the Basic Technical Analysis section that includes:
    - 20-day SMA (Simple Moving Average)
    - 50-day SMA
    - 200-day SMA
    - Trend analysis based on these moving averages
    
    The Volume Profile Analysis provides additional insights:
    - Point of Control (POC): The price level with the highest trading volume, often acting as support/resistance
    - Value Area: Where 70% of trading occurred, representing the fair value range
    - Current price position relative to POC and Value Area
    - Trading implications based on these volume levels
    
    Incorporate the volume profile data into your technical analysis to enhance your prediction accuracy.
    
    For each timeframe, provide:
    1. A detailed technical analysis of the chart data, including the technical indicators and moving averages
    2. An analysis of the market sentiment
    3. A clear prediction (Buy, Sell, or Hold)
    4. A confidence score (0-1) for your prediction
    5. Key factors influencing your decision
    
    Format your response as JSON with the following structure for each timeframe:
    {{
        "timeframe": "timeframe_name",
        "technical_analysis": "your detailed technical analysis",
        "sentiment_analysis": "your sentiment analysis",
        "prediction_label": "Buy/Sell/Hold",
        "signal_strength": confidence_score,
        "key_factors": ["factor1", "factor2", ...]
    }}
    
    Only respond with valid JSON.
    """
    
    # Run the agent
    response = agent.run(prompt)
    
    # Parse the response as JSON
    try:
        analysis = json.loads(response.content)
        
        # Check if the analysis is a list
        if not isinstance(analysis, list):
            analysis = [analysis]
        
        # Create a map of timeframes to predictions
        timeframe_predictions = {}
        for item in analysis:
            if isinstance(item, dict) and "timeframe" in item:
                timeframe_predictions[item["timeframe"]] = item
        
        # Ensure we have predictions for all timeframes
        required_timeframes = ["intraday", "5d", "30d"]
        for timeframe in required_timeframes:
            if timeframe not in timeframe_predictions:
                # If we're missing a timeframe, try to infer it from the other predictions
                if len(timeframe_predictions) > 0:
                    # Use the most common prediction label
                    labels = [item.get("prediction_label", "Hold") for item in timeframe_predictions.values()]
                    most_common_label = max(set(labels), key=labels.count)
                    
                    # Use the average signal strength
                    strengths = [item.get("signal_strength", 0.5) for item in timeframe_predictions.values()]
                    avg_strength = sum(strengths) / len(strengths) if strengths else 0.5
                    
                    # Create a prediction for the missing timeframe
                    timeframe_predictions[timeframe] = {
                        "timeframe": timeframe,
                        "technical_analysis": f"Analysis inferred from other timeframes. The {symbol} futures market shows similar patterns across timeframes.",
                        "sentiment_analysis": f"Sentiment analysis inferred from other timeframes. Market sentiment for {symbol} is consistent across different time horizons.",
                        "prediction_label": most_common_label,
                        "signal_strength": avg_strength,
                        "key_factors": ["Inferred from other timeframes", "Similar market conditions", "Consistent sentiment"]
                    }
            
        # Save the analysis to files
        for timeframe, item in timeframe_predictions.items():
            # Add metadata
            item["symbol"] = symbol
            item["agent"] = "gemini"
            item["timestamp"] = datetime.now().isoformat()
            
            # Save to file
            with open(os.path.join(predictions_dir, f"{timeframe}.json"), "w") as f:
                json.dump(item, f, indent=2)
        
        # Update the analysis list with all timeframe predictions
        analysis = list(timeframe_predictions.values())
    except json.JSONDecodeError:
        # If the response is not valid JSON, try to extract JSON from the response
        import re
        json_match = re.search(r'```json\n(.*?)\n```', response.content, re.DOTALL)
        if json_match:
            try:
                analysis = json.loads(json_match.group(1))
                
                # Check if the analysis is a list
                if not isinstance(analysis, list):
                    analysis = [analysis]
                
                # Save the analysis to files
                for item in analysis:
                    if isinstance(item, dict) and "timeframe" in item:
                        timeframe = item["timeframe"]
                        # Add metadata
                        item["symbol"] = symbol
                        item["agent"] = "gemini"
                        item["timestamp"] = datetime.now().isoformat()
                        
                        # Save to file
                        with open(os.path.join(predictions_dir, f"{timeframe}.json"), "w") as f:
                            json.dump(item, f, indent=2)
            except json.JSONDecodeError:
                analysis = [{
                    "error": "Failed to parse JSON from response",
                    "response": response.content
                }]
        else:
            analysis = [{
                "error": "Response is not valid JSON",
                "response": response.content
            }]
    
    return {
        "symbol": symbol,
        "analysis": analysis,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python gemini.py <symbol>")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    if symbol not in ["NQ", "ES", "YM"]:
        print(f"Invalid symbol: {symbol}. Choose from NQ, ES, YM.")
        sys.exit(1)
    
    result = analyze_futures(symbol)
    print(json.dumps(result, indent=2))
