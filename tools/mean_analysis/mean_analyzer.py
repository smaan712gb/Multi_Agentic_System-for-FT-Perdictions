import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
import os
from datetime import datetime
import json

class MeanAnalyzer:
    """
    A tool for combining predictions from multiple agents (deepseek, gemini, groq) for futures markets (NQ, ES, YM)
    """
    
    # Timeframes for predictions
    PREDICTION_TIMEFRAMES = ["intraday", "5d", "30d"]
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the MeanAnalyzer
        
        Args:
            data_dir: Directory to store the mean analysis data
        """
        self.data_dir = data_dir
        self.mean_analysis_dir = os.path.join(data_dir, "mean_analysis")
        os.makedirs(self.mean_analysis_dir, exist_ok=True)
    
    def load_agent_prediction(self, agent: str, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Load a prediction from a specific agent for a specific symbol and timeframe
        
        Args:
            agent: The agent name (deepseek, gemini, groq)
            symbol: The futures symbol (NQ, ES, YM)
            timeframe: The timeframe to load prediction for
            
        Returns:
            Dictionary containing the prediction
        """
        prediction_path = os.path.join(self.data_dir, "predictions", agent, symbol, f"{timeframe}.json")
        
        if not os.path.exists(prediction_path):
            # If the prediction file doesn't exist, create a default one for Groq
            if agent == "groq":
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(prediction_path), exist_ok=True)
                
                # Create a default prediction
                default_prediction = {
                    "timeframe": timeframe,
                    "technical_analysis": "N/A",
                    "sentiment_analysis": "N/A",
                    "prediction_label": "Hold",
                    "signal_strength": 0.5,
                    "key_factors": ["Default prediction"],
                    "symbol": symbol,
                    "agent": "groq",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Save the default prediction
                with open(prediction_path, "w") as f:
                    json.dump(default_prediction, f, indent=2)
                
                return default_prediction
            else:
                raise FileNotFoundError(f"Prediction not found for agent {agent}, symbol {symbol}, timeframe {timeframe}.")
        
        with open(prediction_path, "r") as f:
            return json.load(f)
    
    def combine_predictions(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Combine predictions from all agents for a specific symbol and timeframe
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            timeframe: The timeframe to combine predictions for
            
        Returns:
            Dictionary containing the combined prediction
        """
        agents = ["deepseek", "gemini", "groq"]
        predictions = {}
        
        # Load predictions from all agents
        for agent in agents:
            try:
                predictions[agent] = self.load_agent_prediction(agent, symbol, timeframe)
            except FileNotFoundError:
                print(f"Warning: Prediction not found for agent {agent}, symbol {symbol}, timeframe {timeframe}.")
        
        if not predictions:
            raise ValueError(f"No predictions found for symbol {symbol}, timeframe {timeframe}.")
        
        # Count buy/sell/hold signals
        signal_counts = {"Buy": 0, "Sell": 0, "Hold": 0}
        
        for agent, prediction in predictions.items():
            label = prediction.get("prediction_label", "Hold")
            signal_counts[label] += 1
        
        # Determine the mean prediction label
        max_count = max(signal_counts.values())
        mean_labels = [label for label, count in signal_counts.items() if count == max_count]
        
        # If there's a tie, prefer Hold
        if len(mean_labels) > 1 and "Hold" in mean_labels:
            mean_label = "Hold"
        else:
            mean_label = mean_labels[0]
        
        # Calculate mean signal strength
        signal_strengths = [prediction.get("signal_strength", 0) for prediction in predictions.values()]
        mean_signal_strength = sum(signal_strengths) / len(signal_strengths) if signal_strengths else 0
        
        # Create mean prediction result
        mean_prediction = {
            "symbol": symbol,
            "timeframe": timeframe,
            "prediction_label": mean_label,
            "signal_strength": mean_signal_strength,
            "agent_predictions": predictions,
            "signal_counts": signal_counts,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save mean prediction to file
        os.makedirs(os.path.join(self.mean_analysis_dir, symbol), exist_ok=True)
        mean_prediction_path = os.path.join(self.mean_analysis_dir, symbol, f"{timeframe}.json")
        
        with open(mean_prediction_path, "w") as f:
            json.dump(mean_prediction, f, indent=2)
        
        return mean_prediction
    
    def get_mean_prediction_path(self, symbol: str, timeframe: str) -> str:
        """
        Get the path to the mean prediction file for a specific symbol and timeframe
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            timeframe: The timeframe
            
        Returns:
            Path to the mean prediction file
        """
        return os.path.join(self.mean_analysis_dir, symbol, f"{timeframe}.json")
    
    def get_chart_path(self, symbol: str, timeframe: str) -> str:
        """
        Get the path to the mean prediction chart for a specific symbol and timeframe
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            timeframe: The timeframe
            
        Returns:
            Path to the mean prediction chart
        """
        return os.path.join(self.mean_analysis_dir, symbol, "charts", f"{timeframe}.png")
    
    def get_html_path(self, symbol: str) -> str:
        """
        Get the path to the interactive HTML chart for a specific symbol
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            
        Returns:
            Path to the interactive HTML chart
        """
        return os.path.join(self.mean_analysis_dir, symbol, "analysis.html")
