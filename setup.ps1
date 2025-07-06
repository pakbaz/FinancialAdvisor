# Financial Advisor Setup Script
# Run this script to set up the environment and dependencies

Write-Host "🚀 Setting up Financial Advisor Multi-Agent System..." -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Yellow

# Check Python version
Write-Host "`n🐍 Checking Python version..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
    
    # Extract version number and check if it's 3.10+
    $versionMatch = [regex]::Match($pythonVersion, "Python (\d+)\.(\d+)")
    if ($versionMatch.Success) {
        $major = [int]$versionMatch.Groups[1].Value
        $minor = [int]$versionMatch.Groups[2].Value
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-Host "⚠️  Warning: Python 3.10+ recommended (you have $major.$minor)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "❌ Python not found! Please install Python 3.10+ first." -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check if conda is available
Write-Host "`n🔍 Checking for Conda/Miniconda..." -ForegroundColor Cyan
$condaAvailable = $false
try {
    $condaVersion = conda --version 2>&1
    Write-Host "✅ Found: $condaVersion" -ForegroundColor Green
    $condaAvailable = $true
} catch {
    Write-Host "ℹ️  Conda not found, will use pip/venv instead" -ForegroundColor Yellow
}

# Setup environment
Write-Host "`n🛠️  Setting up environment..." -ForegroundColor Cyan

if ($condaAvailable) {
    Write-Host "Using Conda environment..." -ForegroundColor Green
    
    # Create conda environment
    Write-Host "Creating conda environment from environment.yml..."
    conda env create -f environment.yml
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Conda environment created successfully!" -ForegroundColor Green
        Write-Host "   Activate with: conda activate financial-advisor" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Failed to create conda environment" -ForegroundColor Red
        $condaAvailable = $false
    }
}

if (-not $condaAvailable) {
    Write-Host "Using Python virtual environment..." -ForegroundColor Green
    
    # Create virtual environment
    Write-Host "Creating virtual environment..."
    python -m venv venv
    
    # Activate virtual environment
    Write-Host "Activating virtual environment..."
    & "venv\Scripts\Activate.ps1"
    
    # Install dependencies
    Write-Host "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment created successfully!" -ForegroundColor Green
        Write-Host "   Activate with: venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Setup environment file
Write-Host "`n📝 Setting up environment configuration..." -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env file from .env.example" -ForegroundColor Green
        Write-Host "   Please edit .env file with your API keys!" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️  .env.example not found, creating basic .env file..." -ForegroundColor Yellow
        
        $envContent = @"
# Financial Advisor Environment Configuration
# Fill in your API keys below

# Alpha Vantage API Key (Required)
# Get your free API key from: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here

# === OpenAI Configuration (Option 1) ===
# OPENAI_API_KEY=sk-your_openai_api_key_here
# OPENAI_MODEL=gpt-4o-mini

# === Azure OpenAI Configuration (Option 2) ===
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
# AZURE_OPENAI_DEPLOYMENT=your_deployment_name
# AZURE_OPENAI_MODEL=gpt-4o
# AZURE_OPENAI_API_VERSION=2024-02-15-preview
"@
        
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "✅ Created basic .env file" -ForegroundColor Green
    }
} else {
    Write-Host "ℹ️  .env file already exists" -ForegroundColor Yellow
}

# Final instructions
Write-Host "`n🎉 Setup Complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Yellow

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Edit the .env file with your API keys:" -ForegroundColor White
Write-Host "   - Alpha Vantage: https://www.alphavantage.co/support/#api-key" -ForegroundColor Gray
Write-Host "   - OpenAI: https://platform.openai.com/api-keys" -ForegroundColor Gray
Write-Host "   - Azure OpenAI: https://portal.azure.com" -ForegroundColor Gray

Write-Host "`n2. Test your configuration:" -ForegroundColor White
Write-Host "   python test_config.py" -ForegroundColor Gray

Write-Host "`n3. Run the application:" -ForegroundColor White
Write-Host "   CLI: python main.py" -ForegroundColor Gray
Write-Host "   Web API: python app.py" -ForegroundColor Gray
Write-Host "   Or: python start_web_service.py" -ForegroundColor Gray

if ($condaAvailable) {
    Write-Host "`n💡 Remember to activate your conda environment:" -ForegroundColor Yellow
    Write-Host "   conda activate financial-advisor" -ForegroundColor Gray
} else {
    Write-Host "`n💡 Remember to activate your virtual environment:" -ForegroundColor Yellow
    Write-Host "   venv\Scripts\Activate.ps1" -ForegroundColor Gray
}

Write-Host "`n🔗 Need help? Check the README.md file!" -ForegroundColor Cyan
