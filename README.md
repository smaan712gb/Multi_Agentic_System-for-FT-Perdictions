# Futures Market Analysis AI Agents

This project uses the agno framework to build a team of AI agents that perform comprehensive analysis and predictions on futures markets (NQ, ES, YM). The agents leverage tools to gather and analyze multi-timeframe chart data and market sentiment, generating clear buy/sell indicators based on their analysis.

## Architecture

The system consists of the following components:

1. **Chart Scraping Tool**: Scrapes chart data for futures markets (NQ, ES, YM) from Yahoo Finance for multiple timeframes.
2. **Sentiment Analysis Tool**: Analyzes market sentiment and aggregates news from major financial news outlets.
3. **AI Analysis Agents**: Three different AI models (DeepSeek, Gemini, Groq) analyze the chart data and sentiment to make predictions.
4. **Mean Analysis Tool**: Combines the individual analyses from the three agents to produce a final analysis with clear buy/sell indicators.

## Setup

### Prerequisites

- Python 3.8+
- API keys for DeepSeek, Gemini, and Groq

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment:
   ```
   python -m venv qaidi804ft_env
   ```

3. Activate the virtual environment:
   - Windows: `.\qaidi804ft_env\Scripts\activate`
   - macOS/Linux: `source qaidi804ft_env/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up API keys:
   - Create a `.env` file in the `agents` directory based on the `.env.example` template:
     ```
     cp agents/.env.example agents/.env
     ```
   - Edit the `agents/.env` file and add your API keys:
     ```
     DEEPSEEK_API_KEY=your_deepseek_api_key
     GEMINI_API_KEY=your_gemini_api_key
     GROQ_API_KEY=your_groq_api_key
     ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
     ```
   - Alternatively, you can run the update_api_keys.py script to set up your API keys:
     ```
     python update_api_keys.py
     ```

   Note: The `.env` file is ignored by Git to protect your API keys.

## Usage

You can run the analysis for a single symbol:

```
python main.py <symbol>
```

Where `<symbol>` is one of: NQ, ES, YM.

Or you can run the analysis for all symbols:

```
python run_all.py
```

If you want to clean up the data directory and start fresh:

```
python cleanup.py
```

To view the latest analysis results:

```
python view_results.py [symbol]
```

Where `[symbol]` is optional. If not provided, it will show results for all symbols.

The script will:
1. Scrape chart data for the specified symbol
2. Analyze market sentiment
3. Run analysis with each AI agent
4. Combine the predictions
5. Generate an interactive chart with buy/sell indicators

The interactive chart will be saved in the `data/mean_analysis/<symbol>/analysis.html` file. Open this file in a web browser to view the analysis.

## Components

### Chart Scraper

The chart scraper tool uses yfinance to scrape chart data for futures markets. It supports the following timeframes:
- Intraday
- 5 days
- 30 days
- 60 days
- 90 days
- 6 months
- 1 year

### Sentiment Analyzer

The sentiment analyzer tool searches for news articles related to the futures markets and analyzes the sentiment. It uses DuckDuckGo to search for news from major financial news outlets like Yahoo Finance, CNBC, WSJ, etc.

### AI Analysis Agents

Three different AI models are used to analyze the chart data and sentiment:
- DeepSeek
- Gemini
- Groq

Each agent provides a technical analysis, sentiment analysis, prediction (Buy, Sell, or Hold), confidence score, and key factors influencing the decision.

### Mean Analysis

The mean analysis tool combines the predictions from the three agents to produce a final analysis. It uses a voting system to determine the final prediction and calculates a mean signal strength.

## Output

The system generates the following outputs:
- Chart data and images for each timeframe
- Sentiment analysis
- Individual predictions from each agent
- Combined mean prediction
- Interactive HTML chart with tabs for different timeframes

## Directory Structure

```
.
├── agents/                  # AI agent implementations
│   ├── deepseek.py          # DeepSeek agent
│   ├── gemini.py            # Gemini agent
│   ├── groq.py              # Groq agent
│   └── .env                 # API keys
├── tools/                   # Tools used by the agents
│   ├── chart_scraper/       # Chart scraping tool
│   ├── sentiment_analyzer/  # Sentiment analysis tool
│   └── mean_analysis/       # Mean analysis tool
├── data/                    # Data directory (created at runtime)
├── main.py                  # Main script for single symbol analysis
├── run_all.py               # Script to run analysis for all symbols
├── setup_env.py             # Script to set up environment variables
├── update_api_keys.py       # Script to update API keys
├── cleanup.py               # Script to clean up the data directory
├── view_results.py          # Script to view the latest analysis results
├── requirements.txt         # Dependencies
└── README.md                # This file
```

## Deployment to GitHub

To deploy this project to GitHub:

1. Create a new repository on GitHub.

2. Initialize Git in your local project directory (if not already done):
   ```
   git init
   ```

3. Add your files to the staging area:
   ```
   git add .
   ```
   Note: The `.gitignore` file is already configured to exclude sensitive files like `.env` and the `data/` directory.

4. Commit your changes:
   ```
   git commit -m "Initial commit"
   ```

5. Add your GitHub repository as a remote:
   ```
   git remote add origin https://github.com/yourusername/your-repo-name.git
   ```

6. Push your code to GitHub:
   ```
   git push -u origin main
   ```
   (Use `master` instead of `main` if your default branch is named `master`)

7. Verify that your `.env` file is not included in the repository by checking the files on GitHub.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
