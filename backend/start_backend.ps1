# Quick Start Script for Backend
# This script helps you start the backend server quickly

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "  Invoice Backend - Quick Start" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Check if we're in the backend directory
if (-not (Test-Path "app\main.py")) {
    Write-Host "❌ Error: Please run this script from the backend directory" -ForegroundColor Red
    Write-Host "   cd backend" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "1️⃣  Activating virtual environment..." -ForegroundColor Cyan
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Please create it first: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if Gmail API is set up
Write-Host ""
Write-Host "2️⃣  Checking Gmail API setup..." -ForegroundColor Cyan
$gmailSetup = $true

if (-not (Test-Path "app\worker\credentials.json")) {
    Write-Host "⚠️  credentials.json not found" -ForegroundColor Yellow
    $gmailSetup = $false
}

if (-not (Test-Path "app\worker\token.json")) {
    Write-Host "⚠️  token.json not found - authentication needed" -ForegroundColor Yellow
    $gmailSetup = $false
} else {
    $token = Get-Content "app\worker\token.json" | ConvertFrom-Json
    if (-not $token.refresh_token) {
        Write-Host "⚠️  token.json missing refresh_token - re-authentication needed" -ForegroundColor Yellow
        $gmailSetup = $false
    }
}

if ($gmailSetup) {
    Write-Host "✅ Gmail API is configured" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "📋 To set up Gmail API:" -ForegroundColor Yellow
    Write-Host "   python app\worker\authenticate_gmail.py" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  The 'Check Email' feature will not work until Gmail API is set up." -ForegroundColor Yellow
    Write-Host "   Other features will work normally." -ForegroundColor White
    Write-Host ""
    
    $response = Read-Host "Do you want to continue starting the server? (Y/n)"
    if ($response -eq "n" -or $response -eq "N") {
        Write-Host "Cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Start the server
Write-Host ""
Write-Host "3️⃣  Starting FastAPI server..." -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Start uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
