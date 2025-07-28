# AutoGen Financial Advisor: Multi-Agent Stock Analysis System

A sophisticated multi-agent financial analysis system built with Microsoft's AutoGen framework that provides comprehensive stock analysis and investment recommendations. The system uses specialized AI agents to analyze both fundamental and technical indicators, delivering actionable insights with clear buy/hold/sell recommendations.

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Alpha Vantage API key (free)
- Either OpenAI API key OR Azure OpenAI access

### 1. Clone and Setup Environment

```powershell
# Clone the repository
git clone <your-repo-url>
cd FinancialAdvisor

# Create conda environment
conda env create -f environment.yml
conda activate financial-advisor

# Or use pip with virtual environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file and configure your API keys:

```powershell
Copy-Item .env.example .env
```

Edit `.env` file with your API keys:

**Option A: Using OpenAI (Recommended for beginners)**
```env
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
OPENAI_API_KEY=sk-your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

**Option B: Using Azure OpenAI**
```env
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
AZURE_OPENAI_MODEL=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 3. Get Your API Keys

**Alpha Vantage (Required)**
1. Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Sign up for a free account
3. Copy your API key

**OpenAI (Option A)**
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account and add billing information
3. Generate an API key

**Azure OpenAI (Option B)**
1. Create an Azure OpenAI resource in the Azure portal
2. Deploy a model (e.g., gpt-4o, gpt-4o-mini)
3. Get your endpoint, API key, and deployment name from the Azure portal

### 4. Run the Application

**Option A: Command Line Interface (CLI)**
```powershell
python main.py
```

**Option B: Web Service API**
```powershell
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```
or simply:
```powershell
python app.py
```

For the CLI, enter a stock ticker when prompted (e.g., `AAPL`, `MSFT`, `GOOGL`) and watch the AI agents collaborate to provide comprehensive analysis!

For the Web API, the service will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## 🌐 Web API Usage

The Financial Advisor is now available as a RESTful web service in addition to the CLI interface.

### Starting the Web Service

```bash
# Start the web service
python -m uvicorn app:app --host 0.0.0.0 --port 8000

# Or use the convenience script
python app.py
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Health Check
```bash
GET /health
```
Returns the service health status and configuration check.

#### Stock Analysis  
```bash
POST /analyze
Content-Type: application/json

{
  "ticker": "AAPL"
}
```

Returns comprehensive stock analysis including:
- Multi-agent AI analysis text
- Financial data (price, ratios, technical indicators)
- Base64-encoded chart image

#### API Documentation
- Interactive docs: `http://localhost:8000/docs`
- OpenAPI spec: `http://localhost:8000/openapi.json`

### Example Usage

**Using curl:**
```bash
# Health check
curl http://localhost:8000/health

# Analyze a stock
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"ticker": "AAPL"}'
```

**Using Python:**
```python
import requests

# Analyze Apple stock
response = requests.post(
    "http://localhost:8000/analyze",
    json={"ticker": "AAPL"}
)

if response.status_code == 200:
    data = response.json()
    print(f"Analysis: {data['analysis']}")
    print(f"Current Price: ${data['data']['current_price']}")
```

**Test the API:**
```bash
python test_client.py
```

## 🤖 How It Works

### Multi-Agent Architecture

The system employs four specialized AI agents working in collaboration:

1. **Data Fetcher Agent** - Retrieves real-time and historical stock data from Alpha Vantage
2. **Fundamental Analysis Agent** - Analyzes P/E ratios, EPS, market cap, and valuation metrics
3. **Technical Analysis Agent** - Examines moving averages, RSI, Bollinger Bands, and trend indicators  
4. **Recommendation Agent** - Synthesizes all analyses into clear buy/hold/sell recommendations

### Analysis Components

**Fundamental Analysis:**
- Price-to-Earnings (P/E) ratio evaluation
- Earnings Per Share (EPS) assessment
- Market capitalization analysis
- Valuation comparison with industry standards

**Technical Analysis:**
- 50-day and 200-day moving averages
- Relative Strength Index (RSI)
- Bollinger Bands analysis
- Price momentum and trend identification

**Visual Output:**
- Interactive stock price charts
- Technical indicator overlays
- Moving averages visualization
- Bollinger Bands with price action

### Decision Logic

The system uses sophisticated logic to generate recommendations:

- **Strong Buy**: Positive fundamental metrics + Strong technical signals
- **Hold**: Mixed signals or neutral indicators
- **Sell**: Weak fundamentals + Negative technical trends

## 🔧 Configuration Options

### Model Selection

**OpenAI Models:**
- `gpt-4o-mini` (default, cost-effective)
- `gpt-4o` (more powerful, higher cost)
- `gpt-3.5-turbo` (budget option)

**Azure OpenAI Models:**
- `gpt-4o` (default)
- `gpt-4o-mini`
- `gpt-35-turbo`

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key | ✅ |
| `OPENAI_API_KEY` | OpenAI API key | ✅ (Option A) |
| `OPENAI_MODEL` | OpenAI model name | ❌ |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | ✅ (Option B) |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | ✅ (Option B) |
| `AZURE_OPENAI_DEPLOYMENT` | Azure OpenAI deployment name | ✅ (Option B) |
| `AZURE_OPENAI_MODEL` | Azure OpenAI model name | ❌ |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API version | ✅ (Option B) |

## 📊 Features

- **Real-time Data**: Live stock prices and financial metrics from Alpha Vantage
- **Comprehensive Analysis**: Both fundamental and technical indicators
- **Visual Charts**: Interactive price charts with technical overlays
- **AI Collaboration**: Multiple specialized agents working together
- **Flexible Configuration**: Support for both OpenAI and Azure OpenAI
- **Streaming Output**: Real-time conversation between AI agents
- **Professional Recommendations**: Clear, actionable investment advice
- **Multiple Interfaces**: Available as both CLI application and Web API
- **RESTful API**: Easy integration with other applications

## 🛠️ Troubleshooting

### Common Issues

**"No valid OpenAI configuration found"**
- Ensure you have configured either OpenAI OR Azure OpenAI credentials in your `.env` file
- Check that your `.env` file is in the project root directory
- Verify API key format and validity

**"ALPHA_VANTAGE_API_KEY not set"**
- Sign up for a free Alpha Vantage account
- Add the API key to your `.env` file
- Note: Free tier has rate limits (5 requests/minute, 500 requests/day)

**Import Errors**
- Ensure you've activated the correct conda environment: `conda activate financial-advisor`
- Or activate virtual environment: `venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Rate Limiting**
- Alpha Vantage free tier: 5 requests/minute, 500/day
- Consider upgrading to premium for higher limits
- Add delays between requests if needed

### Performance Tips

- Use `gpt-4o-mini` for faster, cost-effective analysis
- Azure OpenAI often provides better performance and reliability
- Monitor API usage to avoid unexpected costs

## 📈 Example Output

```
Using Azure OpenAI configuration...
Enter a stock ticker (e.g., AAPL): AAPL

Data_Fetcher: Fetching data for AAPL from Alpha Vantage...
Retrieved: Current Price: $189.84, Market Cap: $2.89T, P/E: 28.5, EPS: $6.64

Fundamental_Analyst: Based on the metrics, AAPL shows strong fundamentals. 
The P/E ratio of 28.5 is reasonable for a tech giant with consistent growth...

Technical_Analyst: The stock is trading above both 50-day ($185.2) and 200-day ($175.8) 
moving averages, indicating a strong uptrend. RSI at 62 shows healthy momentum...

Recommendation_Agent: Given the positive fundamental outlook (strong EPS growth, 
reasonable valuation) and bullish technical signals (uptrend, healthy RSI), 
I recommend STRONG BUY with a target price of $200...

Final Analysis Complete!
[Chart displaying price action with technical indicators]
```

## 🔗 Resources

- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [Alpha Vantage API Documentation](https://www.alphavantage.co/documentation/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)

## 🔄 Migration from Yahoo Finance

This project has been updated from Yahoo Finance to Alpha Vantage for more reliable data access. Key changes:

- **Data Source**: Yahoo Finance → Alpha Vantage API
- **AI Models**: Added Azure OpenAI support alongside OpenAI
- **Configuration**: Environment-based configuration with `.env` files
- **Reliability**: More stable API with proper rate limiting

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📖 Full Technical Blog Post

For a detailed technical walkthrough and implementation guide:
[AutoGen - A Modern AI Agent Framework for Multi‑Agent Collaboration](https://starspak.com/Blog/AutoGen+-+A+Modern+AI+Agent+Framework+for+Multi%E2%80%91Agent+Collaboration)
