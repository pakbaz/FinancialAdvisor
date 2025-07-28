import os
import asyncio
import base64
import io
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web service
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Import existing analysis functions
from main import fetch_stock_data, create_model_client, create_agents_and_team

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI(
    title="Financial Advisor API",
    description="Multi-Agent Stock Analysis System powered by AutoGen",
    version="1.0.0"
)

# Request/Response models
class StockAnalysisRequest(BaseModel):
    ticker: str
    
class StockAnalysisResponse(BaseModel):
    ticker: str
    analysis: str
    data: Dict[str, Any]
    chart_image: Optional[str] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str

def create_stock_chart(data: dict, ticker: str) -> str:
    """Creates a stock chart and returns it as base64 encoded image."""
    try:
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

        # Save plot to bytes
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        
        # Convert to base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        plt.close()  # Close the figure to free memory
        buffer.close()
        
        return image_base64
    except Exception as e:
        print(f"Error creating chart: {e}")
        return None

async def run_stock_analysis(ticker: str) -> tuple[str, dict]:
    """Runs the multi-agent analysis and returns results."""
    try:
        # Create analysis team
        team = create_agents_and_team()
        
        # Create a custom stream handler to capture results
        analysis_results = []
        
        user_task = f"Analyze the stock {ticker} and provide a buy/hold/sell recommendation along with fundamental and technical insights."
        
        # Run the team analysis
        stream = team.run_stream(task=user_task)
        
        # Collect all messages from the stream
        async for message in stream:
            if hasattr(message, 'content'):
                analysis_results.append(message.content)
            elif hasattr(message, 'text'):
                analysis_results.append(message.text)
            elif isinstance(message, str):
                analysis_results.append(message)
        
        # Join all analysis results
        analysis_text = "\n\n".join(analysis_results)
        
        # Get the stock data
        stock_data = fetch_stock_data(ticker)
        
        # Prepare clean data for response (remove matplotlib objects)
        clean_data = {
            "current_price": float(stock_data['current_price']),
            "market_cap": stock_data['market_cap'],
            "pe_ratio": stock_data['pe_ratio'],
            "eps": stock_data['eps'],
            "50d_ma": stock_data['50d_ma'],
            "200d_ma": stock_data['200d_ma'],
            "rsi": float(stock_data['rsi']),
            "bollinger_upper": float(stock_data['bollinger_upper']),
            "bollinger_lower": float(stock_data['bollinger_lower'])
        }
        
        return analysis_text, clean_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check if API keys are configured
        alpha_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")
        azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        
        if not alpha_key:
            return HealthResponse(
                status="error",
                message="Alpha Vantage API key not configured"
            )
        
        if not openai_key and not azure_endpoint:
            return HealthResponse(
                status="error", 
                message="No OpenAI or Azure OpenAI configuration found"
            )
        
        return HealthResponse(
            status="healthy",
            message="Financial Advisor API is running"
        )
    except Exception as e:
        return HealthResponse(
            status="error",
            message=f"Health check failed: {str(e)}"
        )

@app.post("/analyze", response_model=StockAnalysisResponse)
async def analyze_stock(request: StockAnalysisRequest):
    """Analyze a stock ticker and provide buy/hold/sell recommendation."""
    ticker = request.ticker.upper().strip()
    
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker symbol is required")
    
    try:
        # Run analysis
        analysis_text, stock_data = await run_stock_analysis(ticker)
        
        # Create chart
        full_data = fetch_stock_data(ticker)  # Get full data for chart
        chart_image = create_stock_chart(full_data, ticker)
        
        return StockAnalysisResponse(
            ticker=ticker,
            analysis=analysis_text,
            data=stock_data,
            chart_image=chart_image
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Financial Advisor API",
        "description": "Multi-Agent Stock Analysis System",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)