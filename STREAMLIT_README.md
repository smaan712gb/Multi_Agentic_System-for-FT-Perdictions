# Futures Market Analysis Streamlit App

This Streamlit app provides a mobile-friendly interface for analyzing futures markets (ES, NQ, YM) using multiple AI agents.

## Features

- **Symbol Selection**: Choose between ES (S&P 500), NQ (NASDAQ), or YM (Dow Jones) futures
- **Real-time Analysis**: Run analysis on demand with progress tracking
- **Multi-agent Analysis**: Combines predictions from DeepSeek, Gemini, and Groq models
- **Technical Indicators**: Volume profile, price patterns, and trend analysis
- **Sentiment Analysis**: News sentiment from Alpha Vantage API
- **Interactive Charts**: View predictions for different timeframes (Intraday, 5 Days, 30 Days)
- **Mobile-friendly**: Responsive design works on desktop and mobile devices

## Installation

1. Make sure you have Python 3.8+ installed
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Set up your API keys in a `.env` file (see `.env.example` for format)

## Running the App

To run the Streamlit app:

```bash
streamlit run streamlit_app.py
```

This will start the app and open it in your default web browser. If you're running this on a server, you can access it from other devices using the server's IP address and the port (default is 8501).

## Mobile Access

To access the app from a mobile device:

1. Run the app on a computer/server that's accessible on your network
2. Find the IP address of the computer running the app
3. On your mobile device, open a browser and navigate to: `http://<ip-address>:8501`

## Usage

1. Select a symbol (ES, NQ, or YM) from the dropdown menu
2. Click "Start Analysis" to begin the analysis process
3. Wait for the analysis to complete (progress is shown in the sidebar)
4. View the results in the different tabs (Intraday, 5 Days, 30 Days)

## Architecture

The app uses a multi-threaded approach to run the analysis in the background while keeping the UI responsive:

1. User selects a symbol and starts analysis
2. Analysis runs in a background thread
3. UI shows progress updates
4. Results are displayed when analysis completes

## Customization

You can customize the app by:

- Modifying the CSS in the `st.markdown` section to change the appearance
- Adding more timeframes to the tabs
- Extending the analysis with additional indicators or models
