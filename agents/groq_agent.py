from agno.agent import Agent, RunResponse
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import groq

# Import our tools
from tools.chart_scraper.agno_tool import get_chart_data, get_all_timeframes, plot_chart, plot_all_charts
from tools.sentiment_analyzer.agno_tool import get_news, get_sentiment, summarize_news

# Get the API key from the .env file
with open(os.path.join("agents", ".env"), "r") as f:
    for line in f:
        if line.startswith("GROQ_API_KEY="):
            groq_api_key = line.strip().split("=")[1]
            break

# Create a custom Groq client
groq_client = groq.Groq(
    api_key=groq_api_key
)

# Create a custom Groq model class
class GroqModel:
    def __init__(self, id):
        self.id = id
        self.client = groq_client
    
    def response(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.id,
                messages=[{"role": m.role, "content": m.content} for m in messages]
            )
            return RunResponse(content=response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Error calling Groq API: {e}")
    
    def get_instructions_for_model(self):
        return ""
    
    def get_system_message_for_model(self):
        return ""

# Initialize the agent
agent = Agent(
    model=GroqModel(id="llama-3.3-70b-versatile"),
    name="Groq Futures Analyst",
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
    predictions_dir = os.path.join("data", "predictions", "groq", symbol)
    os.makedirs(predictions_dir, exist_ok=True)
    
    # Get chart data and sentiment data
    chart_data = get_all_timeframes(symbol)
    sentiment_data = get_sentiment(symbol)
    
    # Prepare the prompt for the agent
    prompt = f"""
    You are a futures market analyst specializing in technical analysis and market sentiment.
    
    Please analyze the {symbol} futures market and make predictions for the following timeframes:
    - intraday
    - 5d
    - 30d
    
    Here is the chart data for each timeframe:
    
    {chart_data}
    
    Here is the sentiment data:
    {sentiment_data}
    
    For each timeframe, provide:
    1. A technical analysis of the chart data
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
            
        # Save the analysis to files
        for item in analysis:
            if isinstance(item, dict) and "timeframe" in item:
                timeframe = item["timeframe"]
                # Add metadata
                item["symbol"] = symbol
                item["agent"] = "groq"
                item["timestamp"] = datetime.now().isoformat()
                
                # Save to file
                with open(os.path.join(predictions_dir, f"{timeframe}.json"), "w") as f:
                    json.dump(item, f, indent=2)
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
                        item["agent"] = "groq"
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
        print("Usage: python groq_agent.py <symbol>")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    if symbol not in ["NQ", "ES", "YM"]:
        print(f"Invalid symbol: {symbol}. Choose from NQ, ES, YM.")
        sys.exit(1)
    
    result = analyze_futures(symbol)
    print(json.dumps(result, indent=2))
