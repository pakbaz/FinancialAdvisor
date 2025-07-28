#!/usr/bin/env python3
"""
Startup script for Financial Advisor Web Service
"""

import uvicorn
from app import app

if __name__ == "__main__":
    print("🚀 Starting Financial Advisor Web Service...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("📊 Analysis Endpoint: POST http://localhost:8000/analyze")
    print("⚠️  Make sure to configure your .env file with API keys!")
    print("=" * 60)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )