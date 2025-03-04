import yfinance as yf
import matplotlib.pyplot as plt
import asyncio

# --- AutoGen Imports (assumes you have the AutoGen packages installed) ---
from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console

# --- Data Fetching Function ---
def fetch_stock_data(ticker: str) -> dict:
    # Retrieve ticker data and basic info from Yahoo Finance
    stock = yf.Ticker(ticker)
    info = stock.info

    # Retrieve historical data for the past year
    hist = stock.history(period="1y")
    if hist.empty:
        raise ValueError(f"No historical data found for ticker {ticker}")

    # Use "Close" column; if not available, fallback to "Adj Close"
    if "Close" in hist.columns:
        close_prices = hist["Close"]
    elif "Adj Close" in hist.columns:
        close_prices = hist["Adj Close"]
    else:
        raise ValueError("Neither 'Close' nor 'Adj Close' found in the historical data.")

    # Calculate technical indicators using the close prices
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

    return {
        "current_price": info.get("regularMarketPrice"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("forwardPE") or info.get("trailingPE"),
        "eps": info.get("trailingEps"),
        "50d_ma": float(ma50) if ma50 is not None else None,
        "200d_ma": float(ma200) if ma200 is not None else None,
        "rsi": float(rsi),
        "bollinger_upper": float(upper_band),
        "bollinger_lower": float(lower_band),
        # Expose the full historical DataFrame for later use
        "hist": hist,
        # Expose the 'Close' prices series for plotting/analysis
        "close_prices": close_prices
    }

# --- Plotting Function ---
def plot_stock_data(data: dict, ticker: str):
    hist = data["hist"]
    close_prices = data["close_prices"]

    # Calculate moving averages and Bollinger Bands for plotting
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

    # Display the plot until the window is manually closed.
    plt.show()

# --- Setup AutoGen Agents ---

# Create a tool wrapper for our fetch_stock_data function
fetch_tool = FunctionTool(fetch_stock_data, description="Fetch fundamental and technical data for a stock ticker from Yahoo Finance")

# Data Fetcher Agent: Uses the tool to gather stock data.
data_agent = AssistantAgent(
    name="Data_Fetcher",
    model_client=OpenAIChatCompletionClient(model="gpt-4o-mini"),
    tools=[fetch_tool],
    description="Fetches fundamental and technical data from Yahoo Finance for a given stock ticker.",
    system_message=(
        "You are a data fetching agent. Given a stock ticker, use the provided tool to retrieve the stock's fundamental and technical metrics. "
        "Return the data as a summary including current price, market cap, P/E ratio, EPS, moving averages, RSI, and Bollinger Bands."
    )
)

# Fundamental Analysis Agent: Evaluates key financial metrics.
fundamental_agent = AssistantAgent(
    name="Fundamental_Analyst",
    model_client=OpenAIChatCompletionClient(model="gpt-4o-mini"),
    description="Analyzes the stock's fundamentals like P/E ratio, EPS, and market cap to determine valuation.",
    system_message=(
        "You are a fundamental analysis expert. Given the stock's fundamental data, analyze the P/E ratio, EPS, and market cap to assess "
        "whether the stock is undervalued, fairly valued, or overvalued. Provide your analysis in a concise manner."
    )
)

# Technical Analysis Agent: Interprets price trends and momentum.
technical_agent = AssistantAgent(
    name="Technical_Analyst",
    model_client=OpenAIChatCompletionClient(model="gpt-4o-mini"),
    description="Analyzes technical indicators (moving averages, RSI, Bollinger Bands) to determine trend and momentum.",
    system_message=(
        "You are a technical analysis expert. Evaluate the stock's technical data including the 50-day and 200-day moving averages, "
        "RSI, and Bollinger Bands to determine the stock's trend and momentum. Provide your analysis clearly and concisely."
    )
)

# Recommendation Agent: Provides the final buy/hold/sell recommendation.
recommendation_agent = AssistantAgent(
    name="Recommendation_Agent",
    model_client=OpenAIChatCompletionClient(model="gpt-4o-mini"),
    description="Provides a final buy/hold/sell recommendation based on the combined fundamental and technical analyses.",
    system_message=(
        "You are a recommendation agent. Based on the provided fundamental and technical analyses, give a final recommendation for the stock: "
        "'Strong Buy', 'Hold', or 'Sell'. Use these criteria: if both fundamental and technical signals are strong, recommend 'Strong Buy'; "
        "if both are weak, recommend 'Sell'; otherwise, recommend 'Hold'. Explain your reasoning briefly."
    )
)

# Create a RoundRobinGroupChat to orchestrate the conversation between agents.
agents = [data_agent, fundamental_agent, technical_agent, recommendation_agent]
team = RoundRobinGroupChat(agents, max_turns=4)

# --- Main Workflow Function ---
async def run_analysis(ticker: str):
    # Build the initial user task for the agents.
    user_task = f"Analyze the stock {ticker} and provide a buy/hold/sell recommendation along with fundamental and technical insights."
    
    # Run the multi-agent conversation with streaming responses.
    stream = team.run_stream(task=user_task)
    await Console(stream)  # Stream the conversation to the console in real-time.
    
    # After the conversation, fetch data directly using our tool function.
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
    
    # Immediately plot the stock data. The window will remain open until manually closed.
    plot_stock_data(data, ticker)

def main():
    ticker = input("Enter a stock ticker (e.g., AAPL): ").strip().upper()
    try:
        asyncio.run(run_analysis(ticker))
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    main()
