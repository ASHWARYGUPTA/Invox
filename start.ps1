# Quick Start Script for Invox Application

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Invox Application Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env.local exists
if (-Not (Test-Path ".env.local")) {
    Write-Host "Creating .env.local file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env.local"
    Write-Host "✓ Created .env.local" -ForegroundColor Green
} else {
    Write-Host "✓ .env.local already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Starting Backend Server" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Start backend in new terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

Write-Host "✓ Backend starting at http://127.0.0.1:8000" -ForegroundColor Green

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Starting Frontend Server" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Start frontend
Write-Host "Running pnpm dev..." -ForegroundColor Yellow
pnpm dev
