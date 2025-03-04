# AutoGen Example: Multiple AI Agents Collaborating Giving Financial Advise

Analyzing a stock involves looking at both fundamental factors (like earnings and valuation) and technical indicators (like price trends and momentum). In this tutorial, we’ll develop a multi-agent financial analysis system using the AutoGen framework. The system will accept a stock ticker (e.g. "AAPL") as input, have different agents fetch and analyze data, and then produce insights in text and chart format with a clear buy/hold/sell recommendation. We’ll walk through the implementation step-by-step, with code snippets and explanations for each part.
Overview of the Multi-Agent Approach
Our system will consist of four specialized AI agents, each with a distinct role:
- Data Fetcher Agent – retrieves fundamental and technical data for the given stock from Yahoo Finance (e.g. price, P/E ratio, EPS, market cap, moving averages, RSI, etc.).
- Fundamental Analysis Agent – interprets fundamental metrics (like P/E ratio vs. EPS) to assess valuation and financial health.
- Technical Analysis Agent – examines technical indicators (moving average crossover, RSI levels, Bollinger Bands) to gauge market momentum and trends.
- Recommendation Agent – aggregates the insights and provides a final recommendation: Strong Buy, Hold, or Sell, based on predefined decision logic (positive fundamentals + positive technicals = buy​, mixed signals = hold, both negative = sell).
Using AutoGen, these agents will communicate in a conversation, each contributing their analysis. We’ll orchestrate this conversation such that their responses stream progressively (simulating real-time analysis). Finally, we’ll combine their outputs into a summary report containing written insights and a chart visualization of the stock’s technical trend.

## Setup

You only need the OpenAI's key and install dependencies in order to run this example. User venv or use conda to create virtual environment and use python 3.12
Then:

```shell
# requirements
pip install yfinance
pip install matplotlib
pip install -U "autogen-agentchat" "autogen-ext[openai]"

# OpenAI key
export OPENAI_API_KEY=sk-******* # put your api key here
python main.py
```


## Full Blog Post

[AutoGen - A Modern AI Agent Framework for Multi‑Agent Collaboration](https://starspak.com/Blog/AutoGen+-+A+Modern+AI+Agent+Framework+for+Multi%E2%80%91Agent+Collaboration)
