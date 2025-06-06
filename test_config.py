#!/usr/bin/env python3
"""
Configuration Test Script for Financial Advisor
This script helps validate your API keys and environment setup.
"""

import os
from dotenv import load_dotenv

def test_configuration():
    """Test and validate the environment configuration."""
    print("🧪 Testing Financial Advisor Configuration...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Test Alpha Vantage
    alpha_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if alpha_key:
        if alpha_key.startswith("your_") or len(alpha_key) < 10:
            print("❌ Alpha Vantage: Invalid API key format")
        else:
            print("✅ Alpha Vantage: API key configured")
    else:
        print("❌ Alpha Vantage: API key missing (required)")
    
    # Test OpenAI configuration
    openai_key = os.environ.get("OPENAI_API_KEY")
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    
    if openai_key:
        if openai_key.startswith("sk-") and len(openai_key) > 20:
            print(f"✅ OpenAI: API key configured, model: {openai_model}")
            openai_configured = True
        else:
            print("❌ OpenAI: Invalid API key format")
            openai_configured = False
    else:
        print("ℹ️  OpenAI: Not configured")
        openai_configured = False
    
    # Test Azure OpenAI configuration
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    azure_key = os.environ.get("AZURE_OPENAI_API_KEY")
    azure_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
    azure_version = os.environ.get("AZURE_OPENAI_API_VERSION")
    azure_model = os.environ.get("AZURE_OPENAI_MODEL", "gpt-4o")
    
    if all([azure_endpoint, azure_key, azure_deployment, azure_version]):
        if (azure_endpoint.startswith("https://") and 
            len(azure_key) > 20 and 
            not azure_deployment.startswith("your_")):
            print(f"✅ Azure OpenAI: Fully configured, model: {azure_model}")
            azure_configured = True
        else:
            print("❌ Azure OpenAI: Configuration incomplete or invalid")
            azure_configured = False
    else:
        print("ℹ️  Azure OpenAI: Not configured")
        azure_configured = False
    
    # Final validation
    print("\n" + "=" * 50)
    if not alpha_key or alpha_key.startswith("your_"):
        print("❌ CRITICAL: Alpha Vantage API key is required!")
        print("   Get your free key at: https://www.alphavantage.co/support/#api-key")
    elif not (openai_configured or azure_configured):
        print("❌ CRITICAL: Either OpenAI or Azure OpenAI must be configured!")
        print("   OpenAI: https://platform.openai.com/api-keys")
        print("   Azure OpenAI: https://portal.azure.com")
    else:
        provider = "Azure OpenAI" if azure_configured else "OpenAI"
        print(f"✅ SUCCESS: Configuration is valid! Using {provider}")
        print("   You can now run: python main.py")
    
    print("\n💡 Tips:")
    print("   - Copy .env.example to .env and fill in your keys")
    print("   - Azure OpenAI takes priority if both are configured")
    print("   - Use gpt-4o-mini for cost-effective analysis")

def main():
    try:
        test_configuration()
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        print("   Make sure .env file exists and is properly formatted")

if __name__ == "__main__":
    main()
