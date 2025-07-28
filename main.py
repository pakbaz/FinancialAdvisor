import os
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData

# --- AutoGen Imports ---
from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
from autogen_agentchat.ui import Console

# --- Load environment variables ---
load_dotenv()

# --- Stock Data Fetching ---
def fetch_stock_data(ticker: str) -> dict:
    """Fetches price, technicals, and fundamentals for a stock ticker using Alpha Vantage."""
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("ALPHA_VANTAGE_API_KEY not set in environment.")
    ts = TimeSeries(key=api_key, output_format='pandas')
    fd = FundamentalData(key=api_key, output_format='pandas')

    # Fetch daily price data
    data, _ = ts.get_daily(symbol=ticker, outputsize='full')
    data = data.sort_index()
    close_prices = data['4. close']

    # Technical indicators
    ma50 = close_prices.rolling(window=50).mean().iloc[-1]
    ma200 = close_prices.rolling(window=200).mean().iloc[-1]
    delta = close_prices.diff().dropna()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean().iloc[-1]
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean().iloc[-1]
    rsi = 100 - (100 / (1 + (gain / loss))) if loss != 0 else 100
    ma20 = close_prices.rolling(window=20).mean().iloc[-1]
    std20 = close_prices.rolling(window=20).std().iloc[-1]
    upper_band = ma20 + 2 * std20
    lower_band = ma20 - 2 * std20

    # Fundamentals
    try:
        overview, _ = fd.get_company_overview(symbol=ticker)
        pe_ratio = float(overview['PERatio'].iloc[0]) if not overview['PERatio'].isnull().iloc[0] else None
        eps = float(overview['EPS'].iloc[0]) if not overview['EPS'].isnull().iloc[0] else None
        market_cap = float(overview['MarketCapitalization'].iloc[0]) if not overview['MarketCapitalization'].isnull().iloc[0] else None
    except Exception:
        pe_ratio = None
        eps = None
        market_cap = None

    return {
        "current_price": close_prices.iloc[-1],
        "market_cap": market_cap,
        "pe_ratio": pe_ratio,
        "eps": eps,
        "50d_ma": float(ma50) if ma50 is not None else None,
        "200d_ma": float(ma200) if ma200 is not None else None,
        "rsi": float(rsi),
        "bollinger_upper": float(upper_band),
        "bollinger_lower": float(lower_band),
        "hist": data,
        "close_prices": close_prices
    }

# --- Plotting ---
def plot_stock_data(data: dict, ticker: str):
    """Plots price, moving averages, and Bollinger Bands for a stock."""
    hist = data["hist"]
    close_prices = data["close_prices"]
    ma50 = close_prices.rolling(window=50).mean()
    ma200 = close_prices.rolling(window=200).mean()
    ma20 = close_prices.rolling(window=20).mean()
    std20 = close_prices.rolling(window=20).std()
    upper_band = ma20 + 2 * std20
    lower_band = ma20 - 2 * std20

    plt.figure(figsize=(12, 6))
    plt.plot(hist.index, close_prices, label="Close Price", color="blue")
    plt.plot(hist.index, ma50, label="50-day MA", color="green")
    plt.plot(hist.index, ma200, label="200-day MA", color="red")
    plt.plot(hist.index, upper_band, label="Upper Bollinger Band", color="orange", linestyle="--")
    plt.plot(hist.index, lower_band, label="Lower Bollinger Band", color="orange", linestyle="--")
    plt.fill_between(hist.index, lower_band, upper_band, color="gray", alpha=0.3)

    plt.title(f"{ticker} Stock Price and Technical Indicators")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# --- Model Client Configuration ---
def create_model_client():
    """
    Creates and returns the appropriate OpenAI model client based on environment variables.
    Supports both OpenAI and Azure OpenAI configurations.
    Priority: Azure OpenAI > OpenAI
    """
    # Check for Azure OpenAI configuration
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    azure_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
    azure_api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
    
    if all([azure_endpoint, azure_api_key, azure_deployment, azure_api_version]):
        print("Using Azure OpenAI configuration...")
        model_name = os.environ.get("AZURE_OPENAI_MODEL", "gpt-4o")
        return AzureOpenAIChatCompletionClient(
            model=model_name,
            azure_deployment=azure_deployment,
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=azure_api_version
        )
    
    # Fallback to OpenAI
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        print("Using OpenAI configuration...")
        model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        return OpenAIChatCompletionClient(
            model=model_name,
            api_key=openai_api_key
        )
    
    # No valid configuration found
    raise ValueError(
        "No valid OpenAI configuration found. Please set either:\n"
        "For Azure OpenAI: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION\n"
        "For OpenAI: OPENAI_API_KEY"
    )

# --- AutoGen Agent Setup ---
fetch_tool = FunctionTool(
    fetch_stock_data,
    description="Fetch fundamental and technical data for a stock ticker from Alpha Vantage."
)

def create_agents_and_team():
    """Create model client and agents. Called when needed."""
    # Create model client instance
    model_client = create_model_client()

    data_agent = AssistantAgent(
        name="Data_Fetcher",
        model_client=model_client,
        tools=[fetch_tool],
        description="Fetches fundamental and technical data from Alpha Vantage for a given stock ticker.",
        system_message=(
            "You are a data fetching agent. Given a stock ticker, use the provided tool to retrieve the stock's fundamental and technical metrics. "
            "Return the data as a summary including current price, market cap, P/E ratio, EPS, moving averages, RSI, and Bollinger Bands."
        )
    )

    fundamental_agent = AssistantAgent(
        name="Fundamental_Analyst",
        model_client=model_client,
        description="Analyzes the stock's fundamentals like P/E ratio, EPS, and market cap to determine valuation.",
        system_message=(
            "You are a fundamental analysis expert. Given the stock's fundamental data, analyze the P/E ratio, EPS, and market cap to assess "
            "whether the stock is undervalued, fairly valued, or overvalued. Provide your analysis in a concise manner."
        )
    )

    technical_agent = AssistantAgent(
        name="Technical_Analyst",
        model_client=model_client,
        description="Analyzes technical indicators (moving averages, RSI, Bollinger Bands) to determine trend and momentum.",
        system_message=(
            "You are a technical analysis expert. Evaluate the stock's technical data including the 50-day and 200-day moving averages, "
            "RSI, and Bollinger Bands to determine the stock's trend and momentum. Provide your analysis clearly and concisely."
        )
    )

    recommendation_agent = AssistantAgent(
        name="Recommendation_Agent",
        model_client=model_client,
        description="Provides a final buy/hold/sell recommendation based on the combined fundamental and technical analyses.",
        system_message=(
            "You are a recommendation agent. Based on the provided fundamental and technical analyses, give a final recommendation for the stock: "
            "'Strong Buy', 'Hold', or 'Sell'. Use these criteria: if both fundamental and technical signals are strong, recommend 'Strong Buy'; "
            "if both are weak, recommend 'Sell'; otherwise, recommend 'Hold'. Explain your reasoning briefly."
        )
    )

    agents = [data_agent, fundamental_agent, technical_agent, recommendation_agent]
    team = RoundRobinGroupChat(agents, max_turns=4)
    return team

# --- Main Workflow ---
async def run_analysis(ticker: str):
    """Runs the multi-agent analysis and displays results and chart."""
    team = create_agents_and_team()
    user_task = f"Analyze the stock {ticker} and provide a buy/hold/sell recommendation along with fundamental and technical insights."
    stream = team.run_stream(task=user_task)
    await Console(stream)
    data = fetch_stock_data(ticker)
    print("\nFinal Fetched Data:")
    print(f"Current Price: {data['current_price']}")
    print(f"Market Cap: {data['market_cap']}")
    print(f"P/E Ratio: {data['pe_ratio']}")
    print(f"EPS: {data['eps']}")
    print(f"50-day MA: {data['50d_ma']}")
    print(f"200-day MA: {data['200d_ma']}")
    print(f"RSI: {data['rsi']}")
    print(f"Bollinger Upper: {data['bollinger_upper']}")
    print(f"Bollinger Lower: {data['bollinger_lower']}")
    plot_stock_data(data, ticker)


def main():
    """Entry point for the financial advisor app."""
    ticker = input("Enter a stock ticker (e.g., AAPL): ").strip().upper()
    try:
        asyncio.run(run_analysis(ticker))
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    main()
