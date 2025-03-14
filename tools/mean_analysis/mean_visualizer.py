import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional, Tuple, Union
import os
from datetime import datetime
import json
from tools.volume_profile.agno_tool import get_volume_profile
from tools.sentiment_analyzer.agno_tool import get_alpha_vantage_sentiment
from .mean_analyzer import MeanAnalyzer

class MeanVisualizer:
    """
    A tool for visualizing predictions from the MeanAnalyzer
    """
    
    def __init__(self, analyzer: MeanAnalyzer):
        """
        Initialize the MeanVisualizer
        
        Args:
            analyzer: The MeanAnalyzer instance to use for predictions
        """
        self.analyzer = analyzer
        self.mean_analysis_dir = analyzer.mean_analysis_dir
    
    def plot_mean_prediction(self, symbol: str, timeframe: str, chart_data: pd.DataFrame, save: bool = True) -> plt.Figure:
        """
        Plot a chart with mean prediction signals and future price forecast
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            timeframe: The timeframe to plot
            chart_data: DataFrame containing the chart data
            save: Whether to save the chart to disk
            
        Returns:
            Matplotlib figure object
        """
        # Load mean prediction
        try:
            mean_prediction = self.analyzer.combine_predictions(symbol, timeframe)
        except (FileNotFoundError, ValueError) as e:
            print(f"Warning: {e}")
            mean_prediction = {"prediction_label": "Hold", "signal_strength": 0}
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the closing price
        ax.plot(chart_data.index, chart_data['Close'], label=f"{symbol} Close Price")
        
        # Add buy/sell markers based on mean prediction
        last_date = chart_data.index[-1]
        last_price = chart_data['Close'].iloc[-1]
        
        # Add forecast line based on prediction
        # Determine the number of days to forecast based on timeframe
        if timeframe == "intraday":
            forecast_days = 1  # 1 day for intraday
        elif timeframe == "5d":
            forecast_days = 5  # 5 days for 5d
        elif timeframe == "30d":
            forecast_days = 30  # 30 days for 30d
        else:
            forecast_days = 7  # Default
        
        # Create forecast dates - always create new dates for the full forecast period
        # Calculate the average time delta in the data
        if len(chart_data.index) > 1:
            # For 5d and 30d, use business day frequency
            if timeframe in ["5d", "30d"]:
                # Use business day frequency for 5d and 30d
                forecast_dates = pd.date_range(start=last_date, periods=forecast_days+1, freq='B')[1:]
            else:
                # For intraday, calculate appropriate frequency
                avg_delta = (chart_data.index[-1] - chart_data.index[0]) / (len(chart_data.index) - 1)
                forecast_dates = pd.date_range(start=last_date + avg_delta, periods=forecast_days, freq=avg_delta)
        else:
            # Fallback if we only have one data point
            if timeframe == "intraday":
                forecast_dates = pd.date_range(start=last_date + pd.Timedelta(minutes=5), periods=forecast_days, freq='5min')
            elif timeframe == "5d":
                forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days, freq='B')
            elif timeframe == "30d":
                forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days, freq='B')
            else:
                forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days, freq='D')
        
        # Calculate forecast prices
        signal_strength = mean_prediction.get("signal_strength", 0.5)
        
        # Calculate price volatility to scale the forecast
        if len(chart_data) > 1:
            price_volatility = chart_data['Close'].pct_change().std() * 100  # Convert to percentage
        else:
            price_volatility = 0.01  # Default 1% volatility
        
        # Scale the forecast based on signal strength and volatility
        max_move_pct = price_volatility * 5 * signal_strength  # Maximum percentage move
        
        # Add some randomness to make the forecast more realistic
        np.random.seed(42)  # For reproducibility
        
        # Calculate the daily volatility based on historical data
        daily_volatility = price_volatility / np.sqrt(252)  # Annualized to daily
        
        if mean_prediction["prediction_label"] == "Buy":
            # Upward trend for Buy with realistic price movements and non-linear pattern
            # Use a combination of exponential growth and sine wave for more realistic pattern
            forecast_prices = []
            for i in range(forecast_days):
                # Base trend component (exponential growth)
                day_factor = (i+1) / forecast_days
                trend = last_price * (1 + max_move_pct * day_factor * day_factor / 100)
                
                # Oscillation component (sine wave with increasing amplitude)
                wave_amplitude = daily_volatility * last_price * 3 * day_factor
                wave = wave_amplitude * np.sin(i * np.pi / 3)
                
                # Random noise component
                noise = np.random.normal(0, daily_volatility * last_price / 100)
                
                # Combine components
                forecast_price = trend + wave + noise
                forecast_prices.append(forecast_price)
            
            ax.scatter([last_date], [last_price], marker='^', color='green', s=200, label='Buy Signal')
            ax.plot([last_date] + list(forecast_dates), [last_price] + forecast_prices, 'g--', label='Price Forecast')
            
        elif mean_prediction["prediction_label"] == "Sell":
            # Downward trend for Sell with realistic price movements and non-linear pattern
            # Use a combination of exponential decline and sine wave for more realistic pattern
            forecast_prices = []
            for i in range(forecast_days):
                # Base trend component (exponential decline)
                day_factor = (i+1) / forecast_days
                trend = last_price * (1 - max_move_pct * day_factor * day_factor / 100)
                
                # Oscillation component (sine wave with increasing amplitude)
                wave_amplitude = daily_volatility * last_price * 3 * day_factor
                wave = wave_amplitude * np.sin(i * np.pi / 3)
                
                # Random noise component
                noise = np.random.normal(0, daily_volatility * last_price / 100)
                
                # Combine components
                forecast_price = trend + wave + noise
                forecast_prices.append(forecast_price)
            
            ax.scatter([last_date], [last_price], marker='v', color='red', s=200, label='Sell Signal')
            ax.plot([last_date] + list(forecast_dates), [last_price] + forecast_prices, 'r--', label='Price Forecast')
            
        else:
            # Sideways trend for Hold with realistic price movements but more pronounced non-linear pattern
            # Add a slight upward or downward bias based on recent trend
            if len(chart_data) > 5:
                recent_trend = (chart_data['Close'].iloc[-1] - chart_data['Close'].iloc[-5]) / chart_data['Close'].iloc[-5]
            else:
                recent_trend = 0
            
            # Create a more pronounced non-linear pattern for Hold
            forecast_prices = []
            
            # Use a sine wave pattern with increasing amplitude
            for i in range(forecast_days):
                # Base price with slight trend
                base_price = last_price * (1 + recent_trend * 0.2 * (i+1) / forecast_days)
                
                # Add sine wave pattern with increasing amplitude
                wave_amplitude = daily_volatility * last_price * 2 * (i+1) / forecast_days
                wave_component = wave_amplitude * np.sin(i * np.pi / 2)
                
                # Add some random noise
                noise = np.random.normal(0, daily_volatility * last_price / 100)
                
                # Combine components
                forecast_price = base_price + wave_component + noise
                forecast_prices.append(forecast_price)
            
            ax.plot([last_date] + list(forecast_dates), [last_price] + forecast_prices, 'b--', label='Price Forecast')
        
        # Add title and labels
        ax.set_title(f"{symbol} Futures - {timeframe} with Mean Prediction")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        ax.grid(True)
        
        # Format x-axis dates
        fig.autofmt_xdate()
        
        # Add text annotation with prediction details
        prediction_text = f"Mean Prediction: {mean_prediction['prediction_label']}\n"
        prediction_text += f"Signal Strength: {mean_prediction['signal_strength']:.2f}\n"
        
        if "signal_counts" in mean_prediction:
            prediction_text += f"Agent Votes:\n"
            prediction_text += f"•••\nBuy={mean_prediction['signal_counts']['Buy']}\n•••\nSell={mean_prediction['signal_counts']['Sell']}\n•••\nHold={mean_prediction['signal_counts']['Hold']}"
        
        ax.annotate(prediction_text, xy=(0.02, 0.02), xycoords='axes fraction', 
                   bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.8))
        
        # Save the figure if requested
        if save:
            os.makedirs(os.path.join(self.mean_analysis_dir, symbol, "charts"), exist_ok=True)
            fig_path = os.path.join(self.mean_analysis_dir, symbol, "charts", f"{timeframe}.png")
            fig.savefig(fig_path)
        
        return fig
    
    def create_interactive_chart(self, symbol: str, save: bool = True) -> Dict[str, Any]:
        """
        Create an interactive chart with tabs for different timeframes
        
        Args:
            symbol: The futures symbol (NQ, ES, YM)
            save: Whether to save the chart to disk
            
        Returns:
            Dictionary containing paths to the charts
        """
        # This is a placeholder for creating an interactive chart
        # In a real implementation, you would use a library like Plotly or Bokeh
        # to create an interactive chart with tabs for different timeframes
        
        result = {
            "symbol": symbol,
            "timeframes": {},
            "html_path": None
        }
        
        # Create a professional HTML file with tabs
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{symbol} Futures Analysis | Institutional Research</title>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
            <style>
                :root {{
                    --primary-color: #1a3a5f;
                    --secondary-color: #0077b6;
                    --accent-color: #00b4d8;
                    --light-color: #f8f9fa;
                    --dark-color: #212529;
                    --success-color: #198754;
                    --danger-color: #dc3545;
                    --warning-color: #ffc107;
                    --info-color: #0dcaf0;
                    --border-radius: 4px;
                    --box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                }}
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Roboto', Arial, sans-serif;
                    line-height: 1.6;
                    color: var(--dark-color);
                    background-color: #f5f7fa;
                    margin: 0;
                    padding: 0;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                
                header {{
                    background-color: var(--primary-color);
                    color: white;
                    padding: 20px 0;
                    margin-bottom: 30px;
                    box-shadow: var(--box-shadow);
                }}
                
                .header-content {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 0 20px;
                }}
                
                .logo {{
                    font-size: 24px;
                    font-weight: 700;
                }}
                
                .timestamp {{
                    font-size: 14px;
                    opacity: 0.8;
                }}
                
                h1, h2, h3, h4, h5, h6 {{
                    font-weight: 500;
                    margin-bottom: 15px;
                    color: var(--primary-color);
                }}
                
                h1 {{
                    font-size: 28px;
                    margin-bottom: 20px;
                }}
                
                h2 {{
                    font-size: 24px;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                
                h3 {{
                    font-size: 20px;
                    margin-top: 25px;
                }}
                
                .dashboard {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                
                .dashboard-card {{
                    background-color: white;
                    border-radius: var(--border-radius);
                    box-shadow: var(--box-shadow);
                    padding: 20px;
                    display: flex;
                    flex-direction: column;
                }}
                
                .dashboard-card h3 {{
                    margin-top: 0;
                    font-size: 18px;
                    color: var(--primary-color);
                }}
                
                .dashboard-value {{
                    font-size: 24px;
                    font-weight: 700;
                    margin: 10px 0;
                }}
                
                .dashboard-label {{
                    font-size: 14px;
                    color: #666;
                }}
                
                .tab {{
                    overflow: hidden;
                    background-color: white;
                    border-radius: var(--border-radius) var(--border-radius) 0 0;
                    box-shadow: var(--box-shadow);
                    display: flex;
                }}
                
                .tab button {{
                    background-color: inherit;
                    border: none;
                    outline: none;
                    cursor: pointer;
                    padding: 15px 20px;
                    transition: 0.3s;
                    font-size: 16px;
                    font-weight: 500;
                    color: var(--dark-color);
                    flex: 1;
                    text-align: center;
                }}
                
                .tab button:hover {{
                    background-color: #f1f5f9;
                }}
                
                .tab button.active {{
                    background-color: var(--primary-color);
                    color: white;
                }}
                
                .tabcontent {{
                    display: none;
                    padding: 25px;
                    background-color: white;
                    border-radius: 0 0 var(--border-radius) var(--border-radius);
                    box-shadow: var(--box-shadow);
                    margin-bottom: 30px;
                }}
                
                .chart-container {{
                    margin-bottom: 25px;
                    text-align: center;
                }}
                
                img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: var(--border-radius);
                    box-shadow: var(--box-shadow);
                }}
                
                .analysis-section {{
                    margin-top: 25px;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-radius: var(--border-radius);
                    box-shadow: var(--box-shadow);
                }}
                
                .analysis-section h3 {{
                    color: var(--primary-color);
                    margin-top: 0;
                    margin-bottom: 15px;
                    font-size: 18px;
                    font-weight: 500;
                }}
                
                .agent-analysis {{
                    margin-top: 15px;
                    padding: 15px;
                    background-color: white;
                    border-radius: var(--border-radius);
                    box-shadow: var(--box-shadow);
                }}
                
                .agent-name {{
                    font-weight: 500;
                    color: var(--primary-color);
                    font-size: 16px;
                }}
                
                .prediction {{
                    font-weight: 500;
                    margin: 10px 0;
                    padding: 5px 10px;
                    display: inline-block;
                    border-radius: var(--border-radius);
                }}
                
                .prediction.Buy {{
                    background-color: rgba(25, 135, 84, 0.1);
                    color: var(--success-color);
                    border: 1px solid rgba(25, 135, 84, 0.2);
                }}
                
                .prediction.Sell {{
                    background-color: rgba(220, 53, 69, 0.1);
                    color: var(--danger-color);
                    border: 1px solid rgba(220, 53, 69, 0.2);
                }}
                
                .prediction.Hold {{
                    background-color: rgba(13, 202, 240, 0.1);
                    color: var(--info-color);
                    border: 1px solid rgba(13, 202, 240, 0.2);
                }}
                
                pre {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: var(--border-radius);
                    overflow-x: auto;
                    font-family: 'Roboto Mono', monospace;
                    font-size: 14px;
                    line-height: 1.5;
                    white-space: pre-wrap;
                }}
                
                footer {{
                    background-color: var(--primary-color);
                    color: white;
                    padding: 20px 0;
                    margin-top: 30px;
                }}
                
                .footer-content {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 0 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                
                .disclaimer {{
                    font-size: 12px;
                    opacity: 0.8;
                    max-width: 800px;
                }}
                
                .contact {{
                    font-size: 14px;
                }}
                
                @media (max-width: 768px) {{
                    .dashboard {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .tab {{
                        flex-direction: column;
                    }}
                    
                    .footer-content {{
                        flex-direction: column;
                        text-align: center;
                    }}
                    
                    .disclaimer {{
                        margin-bottom: 15px;
                    }}
                }}
            </style>
        </head>
        <body>
            <header>
                <div class="header-content">
                    <div class="logo">Futures Market Analysis</div>
                    <div class="timestamp">Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
                </div>
            </header>
            
            <div class="container">
                <h1>{symbol} Futures Analysis</h1>
                
                <!-- Dashboard with key metrics -->
                <div class="dashboard">
        """
        
        # Try to get the latest price and prediction for the dashboard
        try:
            # Get the intraday prediction
            intraday_prediction = self.analyzer.combine_predictions(symbol, "intraday")
            
            # Get the latest price from the prediction
            latest_price = "---"
            for agent, prediction in intraday_prediction.get("agent_predictions", {}).items():
                if "latest_price" in prediction:
                    latest_price = f"${prediction['latest_price']:.2f}"
                    break
            
            # Get the mean prediction and signal strength
            mean_prediction_label = intraday_prediction.get("prediction_label", "---")
            signal_strength = intraday_prediction.get("signal_strength", 0)
            
            # Add the dashboard cards with actual data
            html_content += f"""
                    <div class="dashboard-card">
                        <h3>Current Price</h3>
                        <div class="dashboard-value">{latest_price}</div>
                        <div class="dashboard-label">Last updated: {datetime.now().strftime("%Y-%m-%d")}</div>
                    </div>
                    
                    <div class="dashboard-card">
                        <h3>Mean Prediction</h3>
                        <div class="dashboard-value {mean_prediction_label}">{mean_prediction_label}</div>
                        <div class="dashboard-label">Consensus from all agents</div>
                    </div>
                    
                    <div class="dashboard-card">
                        <h3>Signal Strength</h3>
                        <div class="dashboard-value">{signal_strength:.2f}</div>
                        <div class="dashboard-label">Confidence level (0-1)</div>
                    </div>
            """
        except Exception as e:
            # If there's an error, use default values
            html_content += f"""
                    <div class="dashboard-card">
                        <h3>Current Price</h3>
                        <div class="dashboard-value">$---.--</div>
                        <div class="dashboard-label">Last updated: {datetime.now().strftime("%Y-%m-%d")}</div>
                    </div>
                    
                    <div class="dashboard-card">
                        <h3>Mean Prediction</h3>
                        <div class="dashboard-value">---</div>
                        <div class="dashboard-label">Consensus from all agents</div>
                    </div>
                    
                    <div class="dashboard-card">
                        <h3>Signal Strength</h3>
                        <div class="dashboard-value">-.-</div>
                        <div class="dashboard-label">Confidence level (0-1)</div>
                    </div>
            """
        
        html_content += """
                </div>
            
                <div class="tab">
        """
        
        # Add tabs for each timeframe
        for i, timeframe in enumerate(self.analyzer.PREDICTION_TIMEFRAMES):
            active = "active" if i == 0 else ""
            html_content += f'<button class="tablinks {active}" onclick="openTimeframe(event, \'{timeframe}\')">{timeframe}</button>\n'
        
        html_content += """
                </div>
        """
        
        # Add content for each timeframe
        for i, timeframe in enumerate(self.analyzer.PREDICTION_TIMEFRAMES):
            display = "block" if i == 0 else "none"
            
            # Get the path to the chart image
            chart_path = os.path.join(self.mean_analysis_dir, symbol, "charts", f"{timeframe}.png")
            
            # Check if the chart file exists
            if os.path.exists(chart_path):
                # Use a simple relative path from the HTML file to the chart
                relative_path = f"charts/{timeframe}.png"
                
                # Add to result
                result["timeframes"][timeframe] = {
                    "chart_path": chart_path
                }
                
                # Load mean prediction to get agent analyses
                try:
                    mean_prediction = self.analyzer.combine_predictions(symbol, timeframe)
                    agent_predictions = mean_prediction.get("agent_predictions", {})
                    
                    # Get volume profile analysis
                    try:
                        volume_profile_analysis = get_volume_profile(symbol)
                    except Exception as e:
                        volume_profile_analysis = f"Error loading volume profile analysis: {str(e)}"
                    
                    # Get news sentiment analysis
                    try:
                        news_sentiment_analysis = get_alpha_vantage_sentiment(symbol)
                    except Exception as e:
                        news_sentiment_analysis = f"Error loading news sentiment analysis: {str(e)}"
                    
                    html_content += f"""
                    <div id="{timeframe}" class="tabcontent" style="display: {display};">
                        <h2>{symbol} - {timeframe}</h2>
                        <img src="{relative_path}" alt="{symbol} {timeframe} chart">
                        
                        <div class="analysis-section">
                            <h3>Volume Profile Analysis</h3>
                            <pre>{volume_profile_analysis}</pre>
                        </div>
                        
                        <div class="analysis-section">
                            <h3>News Sentiment Analysis</h3>
                            <pre>{news_sentiment_analysis}</pre>
                        </div>
                        
                        <div class="analysis-section">
                            <h3>Agent Analyses</h3>
                    """
                    
                    # Add each agent's analysis
                    for agent, prediction in agent_predictions.items():
                        prediction_label = prediction.get("prediction_label", "Hold")
                        signal_strength = prediction.get("signal_strength", 0.5)
                        technical_analysis = prediction.get("technical_analysis", "No technical analysis provided.")
                        sentiment_analysis = prediction.get("sentiment_analysis", "No sentiment analysis provided.")
                        key_factors = prediction.get("key_factors", [])
                        
                        html_content += f"""
                            <div class="agent-analysis">
                                <div class="agent-name">{agent.capitalize()} Analysis:</div>
                                <div class="prediction {prediction_label}">Prediction: {prediction_label} (Confidence: {signal_strength:.2f})</div>
                                <p><strong>Technical Analysis:</strong> {technical_analysis}</p>
                                <p><strong>Sentiment Analysis:</strong> {sentiment_analysis}</p>
                                <p><strong>Key Factors:</strong> {', '.join(key_factors)}</p>
                            </div>
                        """
                    
                    html_content += """
                        </div>
                    </div>
                    """
                except Exception as e:
                    html_content += f"""
                    <div id="{timeframe}" class="tabcontent" style="display: {display};">
                        <h2>{symbol} - {timeframe}</h2>
                        <img src="{relative_path}" alt="{symbol} {timeframe} chart">
                        <p>Error loading agent analyses: {str(e)}</p>
                    </div>
                    """
            else:
                # Add a message if the chart doesn't exist
                html_content += f"""
                <div id="{timeframe}" class="tabcontent" style="display: {display};">
                    <h2>{symbol} - {timeframe}</h2>
                    <p>No predictions available for this timeframe. Please run the analysis again later.</p>
                </div>
                """
        
        # Add footer and JavaScript for tab functionality
        html_content += """
            </div>
            
            <footer>
                <div class="footer-content">
                    <div class="disclaimer">
                        DISCLAIMER: This analysis is for informational purposes only and does not constitute investment advice. 
                        Past performance is not indicative of future results. Trading futures involves substantial risk of loss.
                    </div>
                    <div class="contact">
                        Contact: research@example.com
                    </div>
                </div>
            </footer>
            
            <script>
                function openTimeframe(evt, timeframe) {
                    var i, tabcontent, tablinks;
                    tabcontent = document.getElementsByClassName("tabcontent");
                    for (i = 0; i < tabcontent.length; i++) {
                        tabcontent[i].style.display = "none";
                    }
                    tablinks = document.getElementsByClassName("tablinks");
                    for (i = 0; i < tablinks.length; i++) {
                        tablinks[i].className = tablinks[i].className.replace(" active", "");
                    }
                    document.getElementById(timeframe).style.display = "block";
                    evt.currentTarget.className += " active";
                }
            </script>
        </body>
        </html>
        """
        
        # Save the HTML file
        if save:
            os.makedirs(os.path.join(self.mean_analysis_dir, symbol), exist_ok=True)
            html_path = os.path.join(self.mean_analysis_dir, symbol, "analysis.html")
            
            with open(html_path, "w") as f:
                f.write(html_content)
            
            result["html_path"] = html_path
        
        return result
