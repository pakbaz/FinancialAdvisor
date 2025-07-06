#!/usr/bin/env python3
"""
Test client for the Financial Advisor Web Service
This script demonstrates how to interact with the API.
"""

import requests
import json
import base64
import time

def test_health():
    """Test the health endpoint."""
    print("🏥 Testing health endpoint...")
    response = requests.get("http://localhost:8000/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_root():
    """Test the root endpoint."""
    print("🏠 Testing root endpoint...")
    response = requests.get("http://localhost:8000/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_analysis(ticker="AAPL"):
    """Test the analysis endpoint."""
    print(f"📊 Testing analysis endpoint with {ticker}...")
    
    payload = {"ticker": ticker}
    response = requests.post("http://localhost:8000/analyze", json=payload)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Analysis successful!")
        print(f"Ticker: {data['ticker']}")
        print(f"Analysis length: {len(data['analysis'])} characters")
        print(f"Data points: {list(data['data'].keys())}")
        print(f"Chart image: {'Available' if data['chart_image'] else 'Not available'}")
        
        # Save chart if available
        if data['chart_image']:
            try:
                chart_data = base64.b64decode(data['chart_image'])
                with open(f"{ticker}_chart.png", "wb") as f:
                    f.write(chart_data)
                print(f"📈 Chart saved as {ticker}_chart.png")
            except Exception as e:
                print(f"❌ Error saving chart: {e}")
        
        # Print first 500 characters of analysis
        print("\n📝 Analysis preview:")
        print(data['analysis'][:500] + "..." if len(data['analysis']) > 500 else data['analysis'])
        
    else:
        print(f"❌ Analysis failed: {response.text}")
    print()

def test_invalid_ticker():
    """Test with an invalid ticker."""
    print("❌ Testing with invalid ticker...")
    payload = {"ticker": "INVALID_TICKER_123"}
    response = requests.post("http://localhost:8000/analyze", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    print()

def main():
    """Run all tests."""
    print("🚀 Financial Advisor API Test Client")
    print("=" * 50)
    
    # Test basic endpoints
    test_root()
    test_health()
    
    # Check if API keys are configured
    health_response = requests.get("http://localhost:8000/health").json()
    if health_response["status"] == "error":
        print("⚠️  API keys not configured. Skipping analysis tests.")
        print("Configure your .env file with Alpha Vantage and OpenAI/Azure OpenAI keys to test analysis.")
        return
    
    # Test analysis endpoints
    print("🧪 Testing analysis functionality...")
    test_analysis("AAPL")
    
    # Test error handling
    test_invalid_ticker()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()