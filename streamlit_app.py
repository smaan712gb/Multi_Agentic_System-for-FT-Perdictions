import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
import time
import json
from datetime import datetime
import threading
import queue

# Import our analysis functions
from tools.chart_scraper.chart_scraper import ChartScraper
from tools.mean_analysis.mean_analyzer import MeanAnalyzer
from tools.mean_analysis.mean_visualizer import MeanVisualizer
from tools.volume_profile.agno_tool import get_volume_profile
from tools.sentiment_analyzer.agno_tool import get_alpha_vantage_sentiment
from agents.deepseek import analyze_futures as deepseek_analyze
from agents.gemini import analyze_futures as gemini_analyze
from agents.groq import analyze_futures as groq_analyze
from setup_env import setup_env

# Set up environment variables
setup_env()

# Set page config for dark theme
st.set_page_config(
    page_title="Futures Market Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply dark theme
st.markdown("""
<style>
    .reportview-container {
        background-color: #0e1117;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #0e1117;
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1a3a5f;
        border-radius: 4px 4px 0 0;
        gap: 10px;
        padding-top: 10px;
        padding-bottom: 10px;
        padding-left: 20px;
        padding-right: 20px;
        margin-right: 5px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0077b6;
    }
    .stMarkdown a {
        color: #00b4d8;
    }
    .stDataFrame {
        border: 1px solid #1a3a5f;
    }
    .css-1aumxhk {
        background-color: #1a3a5f;
    }
    .css-1r6slb0 {
        background-color: #1a3a5f;
        border: 1px solid #1a3a5f;
    }
    .css-12oz5g7 {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    .css-1v3fvcr {
        max-width: 100%;
    }
    .css-18e3th9 {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    .css-1kyxreq {
        display: flex;
        flex-flow: row wrap;
        row-gap: 1rem;
    }
    .css-12w0qpk {
        background-color: #1a3a5f;
        border: 1px solid #1a3a5f;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .css-1fcdlhc {
        background-color: #1a3a5f;
        border: 1px solid #1a3a5f;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #0077b6;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00b4d8;
    }
    .stProgress > div > div > div > div {
        background-color: #0077b6;
    }
</style>
""", unsafe_allow_html=True)

# Create a session state to store analysis results
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'analysis_running' not in st.session_state:
    st.session_state.analysis_running = False
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'status' not in st.session_state:
    st.session_state.status = ""
if 'selected_timeframe' not in st.session_state:
    st.session_state.selected_timeframe = "5d"

# Define analysis steps
def run_analysis(symbol):
    """Run the full analysis for a symbol"""
    results = {}
    
    # Step 1: Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Step 2: Initialize chart scraper
    chart_scraper = ChartScraper(data_dir="data")
    
    # Step 3: Scrape chart data
    chart_data = {}
    for timeframe in chart_scraper.TIMEFRAMES:
        chart_data[timeframe] = chart_scraper.get_ticker_data(symbol, timeframe)
        chart_scraper.plot_chart(symbol, timeframe)
    
    # Step 4: Get volume profile analysis
    volume_profile_analysis = get_volume_profile(symbol, interval="5min")
    
    # Step 5: Get news sentiment analysis
    news_sentiment_analysis = get_alpha_vantage_sentiment(symbol)
    
    # Step 6: Run analysis with DeepSeek
    deepseek_result = deepseek_analyze(symbol)
    
    # Step 7: Run analysis with Gemini
    gemini_result = gemini_analyze(symbol)
    
    # Step 8: Run analysis with Groq
    groq_result = groq_analyze(symbol)
    
    # Step 9: Combine predictions
    mean_analyzer = MeanAnalyzer(data_dir="data")
    mean_visualizer = MeanVisualizer(analyzer=mean_analyzer)
    
    mean_predictions = {}
    for timeframe in mean_analyzer.PREDICTION_TIMEFRAMES:
        try:
            mean_predictions[timeframe] = mean_analyzer.combine_predictions(symbol, timeframe)
            mean_visualizer.plot_mean_prediction(symbol, timeframe, chart_data[timeframe])
        except Exception as e:
            print(f"Error with {timeframe}: {e}")
    
    # Step 10: Create interactive chart
    interactive_chart = mean_visualizer.create_interactive_chart(symbol)
    
    # Prepare result
    results = {
        "symbol": symbol,
        "chart_data": {timeframe: chart_data[timeframe].to_dict() for timeframe in chart_data},
        "volume_profile_analysis": volume_profile_analysis,
        "news_sentiment_analysis": news_sentiment_analysis,
        "deepseek_result": deepseek_result,
        "gemini_result": gemini_result,
        "groq_result": groq_result,
        "mean_predictions": mean_predictions,
        "interactive_chart_path": interactive_chart.get("html_path"),
        "timestamp": datetime.now().isoformat(),
        "chart_paths": {
            timeframe: os.path.join("data", "mean_analysis", symbol, "charts", f"{timeframe}.png")
            for timeframe in mean_analyzer.PREDICTION_TIMEFRAMES
        }
    }
    
    return results

# Function to start analysis
def start_analysis(symbol):
    """Start the analysis process and update the session state"""
    if st.session_state.analysis_running:
        st.warning("Analysis is already running. Please wait for it to complete.")
        return
    
    # Set initial state
    st.session_state.analysis_running = True
    st.session_state.progress = 0
    st.session_state.status = "Starting analysis..."
    st.session_state.analysis_results = None
    st.session_state.start_time = time.time()
    
    # Create a placeholder for the progress bar
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # Run analysis step by step with progress updates
    try:
        # Step 1: Create data directory
        os.makedirs("data", exist_ok=True)
        progress_placeholder.progress(5)
        status_placeholder.text("Creating data directory...")
        
        # Step 2: Initialize chart scraper
        chart_scraper = ChartScraper(data_dir="data")
        progress_placeholder.progress(10)
        status_placeholder.text("Initializing chart scraper...")
        
        # Step 3: Scrape chart data
        chart_data = {}
        for i, timeframe in enumerate(chart_scraper.TIMEFRAMES):
            status_placeholder.text(f"Scraping chart data for {timeframe}...")
            chart_data[timeframe] = chart_scraper.get_ticker_data(symbol, timeframe)
            chart_scraper.plot_chart(symbol, timeframe)
            progress = 10 + int(20 * (i + 1) / len(chart_scraper.TIMEFRAMES))
            progress_placeholder.progress(progress)
        
        # Step 4: Get volume profile analysis
        status_placeholder.text("Analyzing volume profile...")
        progress_placeholder.progress(30)
        volume_profile_analysis = get_volume_profile(symbol, interval="5min")
        
        # Step 5: Get news sentiment analysis
        status_placeholder.text("Analyzing news sentiment...")
        progress_placeholder.progress(40)
        news_sentiment_analysis = get_alpha_vantage_sentiment(symbol)
        
        # Step 6: Run analysis with DeepSeek
        status_placeholder.text("Running DeepSeek analysis...")
        progress_placeholder.progress(50)
        deepseek_result = deepseek_analyze(symbol)
        
        # Step 7: Run analysis with Gemini
        status_placeholder.text("Running Gemini analysis...")
        progress_placeholder.progress(60)
        gemini_result = gemini_analyze(symbol)
        
        # Step 8: Run analysis with Groq
        status_placeholder.text("Running Groq analysis...")
        progress_placeholder.progress(70)
        groq_result = groq_analyze(symbol)
        
        # Step 9: Combine predictions
        status_placeholder.text("Combining predictions...")
        progress_placeholder.progress(80)
        mean_analyzer = MeanAnalyzer(data_dir="data")
        mean_visualizer = MeanVisualizer(analyzer=mean_analyzer)
        
        mean_predictions = {}
        for timeframe in mean_analyzer.PREDICTION_TIMEFRAMES:
            try:
                mean_predictions[timeframe] = mean_analyzer.combine_predictions(symbol, timeframe)
                mean_visualizer.plot_mean_prediction(symbol, timeframe, chart_data[timeframe])
            except Exception as e:
                print(f"Error with {timeframe}: {e}")
        
        # Step 10: Create interactive chart
        status_placeholder.text("Creating interactive chart...")
        progress_placeholder.progress(90)
        interactive_chart = mean_visualizer.create_interactive_chart(symbol)
        
        # Prepare result
        results = {
            "symbol": symbol,
            "chart_data": {timeframe: chart_data[timeframe].to_dict() for timeframe in chart_data},
            "volume_profile_analysis": volume_profile_analysis,
            "news_sentiment_analysis": news_sentiment_analysis,
            "deepseek_result": deepseek_result,
            "gemini_result": gemini_result,
            "groq_result": groq_result,
            "mean_predictions": mean_predictions,
            "interactive_chart_path": interactive_chart.get("html_path"),
            "timestamp": datetime.now().isoformat(),
            "chart_paths": {
                timeframe: os.path.join("data", "mean_analysis", symbol, "charts", f"{timeframe}.png")
                for timeframe in mean_analyzer.PREDICTION_TIMEFRAMES
            }
        }
        
        # Update session state with results
        st.session_state.analysis_results = results
        st.session_state.analysis_running = False
        progress_placeholder.progress(100)
        status_placeholder.text("Analysis complete!")
        
        # Force a rerun to update the UI with the results
        st.rerun()
        
    except Exception as e:
        # Handle errors
        st.session_state.status = f"Error: {str(e)}"
        st.session_state.progress = 0
        st.session_state.analysis_running = False
        status_placeholder.text(f"Error: {str(e)}")
        progress_placeholder.empty()

# Main app layout
st.title("📈 Futures Market Analysis")

# Sidebar
st.sidebar.header("Analysis Options")

# Symbol selection
symbol = st.sidebar.selectbox(
    "Select Symbol",
    ["ES", "NQ", "YM"],
    help="ES = S&P 500, NQ = NASDAQ, YM = Dow Jones"
)

# Start analysis button
if st.sidebar.button("Start Analysis"):
    start_analysis(symbol)

# Show progress
if st.session_state.analysis_running:
    st.sidebar.progress(st.session_state.progress)
    st.sidebar.text(st.session_state.status)

# Display results
if st.session_state.analysis_results:
    results = st.session_state.analysis_results
    
    # Display dashboard
    st.header(f"{results['symbol']} Futures Analysis")
    st.subheader(f"Generated on: {datetime.fromisoformat(results['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create dashboard cards
    col1, col2, col3 = st.columns(3)
    
    # Get the latest prediction
    mean_prediction = results['mean_predictions'].get('intraday', {})
    prediction_label = mean_prediction.get('prediction_label', 'Hold')
    signal_strength = mean_prediction.get('signal_strength', 0.5)
    
    # Display dashboard cards
    with col1:
        st.markdown("""
        <div style="background-color: #1a3a5f; padding: 20px; border-radius: 10px; text-align: center;">
            <h3 style="margin-top: 0;">Symbol</h3>
            <div style="font-size: 24px; font-weight: bold; margin: 10px 0;">{}</div>
            <div style="font-size: 14px; color: #ccc;">Futures Contract</div>
        </div>
        """.format(results['symbol']), unsafe_allow_html=True)
    
    with col2:
        color = "#198754" if prediction_label == "Buy" else "#dc3545" if prediction_label == "Sell" else "#0dcaf0"
        st.markdown("""
        <div style="background-color: #1a3a5f; padding: 20px; border-radius: 10px; text-align: center;">
            <h3 style="margin-top: 0;">Mean Prediction</h3>
            <div style="font-size: 24px; font-weight: bold; margin: 10px 0; color: {};">{}</div>
            <div style="font-size: 14px; color: #ccc;">Consensus from all agents</div>
        </div>
        """.format(color, prediction_label), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background-color: #1a3a5f; padding: 20px; border-radius: 10px; text-align: center;">
            <h3 style="margin-top: 0;">Signal Strength</h3>
            <div style="font-size: 24px; font-weight: bold; margin: 10px 0;">{:.2f}</div>
            <div style="font-size: 14px; color: #ccc;">Confidence level (0-1)</div>
        </div>
        """.format(signal_strength), unsafe_allow_html=True)
    
    # Create tabs for different timeframes
    timeframe_tabs = st.tabs(["Intraday", "5 Days", "30 Days"])
    
    # Display charts and analysis for each timeframe
    for i, (tab, timeframe) in enumerate(zip(timeframe_tabs, ["intraday", "5d", "30d"])):
        with tab:
            # Display chart
            chart_path = results['chart_paths'].get(timeframe)
            if chart_path and os.path.exists(chart_path):
                st.image(chart_path, use_container_width=True)
            else:
                st.warning(f"Chart for {timeframe} not found.")
            
            # Display agent analyses
            st.subheader("Agent Analyses")
            
            # Create columns for each agent
            agent_cols = st.columns(3)
            
            # Get mean prediction for this timeframe
            mean_prediction = results['mean_predictions'].get(timeframe, {})
            agent_predictions = mean_prediction.get('agent_predictions', {})
            
            # Display agent predictions
            for i, (agent, col) in enumerate(zip(["deepseek", "gemini", "groq"], agent_cols)):
                if agent in agent_predictions:
                    prediction = agent_predictions[agent]
                    prediction_label = prediction.get('prediction_label', 'Hold')
                    signal_strength = prediction.get('signal_strength', 0.5)
                    
                    # Set color based on prediction
                    color = "#198754" if prediction_label == "Buy" else "#dc3545" if prediction_label == "Sell" else "#0dcaf0"
                    
                    with col:
                        st.markdown(f"""
                        <div style="background-color: #1a3a5f; padding: 15px; border-radius: 10px;">
                            <h4 style="margin-top: 0;">{agent.capitalize()}</h4>
                            <div style="background-color: rgba(30, 30, 30, 0.5); padding: 5px 10px; border-radius: 4px; display: inline-block; margin: 10px 0; color: {color};">
                                {prediction_label} (Confidence: {signal_strength:.2f})
                            </div>
                            <p><strong>Technical Analysis:</strong> {prediction.get('technical_analysis', 'N/A')}</p>
                            <p><strong>Sentiment Analysis:</strong> {prediction.get('sentiment_analysis', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Display additional analyses
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Volume Profile Analysis")
                st.text(results['volume_profile_analysis'])
            
            with col2:
                st.subheader("News Sentiment Analysis")
                st.text(results['news_sentiment_analysis'])

# Display instructions if no analysis has been run
if not st.session_state.analysis_results and not st.session_state.analysis_running:
    st.info("👈 Select a symbol and click 'Start Analysis' to begin.")
    
    # Display sample images
    st.markdown("### Sample Analysis")
    st.markdown("Here's what the analysis will look like:")
    
    sample_image_path = "data/mean_analysis/NQ/charts/5d.png"
    if os.path.exists(sample_image_path):
        st.image(sample_image_path, use_container_width=True)
    else:
        st.markdown("Run an analysis first to see sample results.")
