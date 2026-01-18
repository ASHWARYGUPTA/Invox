@echo off
REM RAG Chat System Setup Script for Windows
REM Automated installation for Invoice RAG Chat

echo 🚀 Setting up RAG Chat System for Invox...
echo.

REM Check if we're in the project root
if not exist "backend" (
    echo ❌ Error: Please run this script from the project root directory
    exit /b 1
)
if not exist "package.json" (
    echo ❌ Error: Please run this script from the project root directory
    exit /b 1
)

REM Backend setup
echo 📦 Installing backend dependencies...

REM Check if virtual environment exists in backend folder
if not exist "backend\venv" (
    echo Creating virtual environment in backend\venv...
    python -m venv backend\venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call backend\venv\Scripts\activate.bat

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip -q

REM Install requirements (including existing requirements.txt)
echo Installing Python packages...
cd backend
pip install -q -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install requirements.txt dependencies
    cd ..
    exit /b 1
)

REM Install RAG-specific dependencies
echo Installing RAG-specific packages...
pip install -q chromadb==0.5.23 sentence-transformers==3.3.1

if %errorlevel% equ 0 (
    echo ✅ Backend dependencies installed successfully
) else (
    echo ❌ Failed to install RAG dependencies
    cd ..
    exit /b 1
)

REM Check for GEMINI_API_KEY
findstr /C:"GEMINI_API_KEY" .env >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Warning: GEMINI_API_KEY not found in backend\.env
    echo Please add your Gemini API key to backend\.env:
    echo GEMINI_API_KEY=your-api-key-here
)

REM Deactivate venv before moving to frontend
call deactivate 2>nul

cd ..

REM Frontend setup
echo.
echo 📦 Installing frontend dependencies...
call pnpm install --silent

if %errorlevel% equ 0 (
    echo ✅ Frontend dependencies installed successfully
) else (
    echo ⚠️  Frontend installation had issues (may be okay if packages already installed)
)

REM Create chroma_db directory if it doesn't exist
echo.
echo 📁 Creating ChromaDB directory...
if not exist "backend\chroma_db" mkdir backend\chroma_db
echo ✅ ChromaDB directory created

REM Summary
echo.
echo ═══════════════════════════════════════════
echo ✅ RAG Chat System Setup Complete!
echo ═══════════════════════════════════════════
echo.
echo Next steps:
echo 1. Start backend:
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
echo.
echo 2. Start frontend (in new terminal):
echo    pnpm dev
echo.
echo 3. Navigate to: http://localhost:3000/chat
echo 4. Click 'Re-index Invoices' to index your invoices
echo 5. Start chatting with your invoices!
echo.
echo 📚 Documentation:
echo    - RAG_SETUP_GUIDE.md - Quick setup guide
echo    - backend\RAG_CHAT_README.md - Full documentation
echo    - RAG_IMPLEMENTATION_SUMMARY.md - Implementation details
echo.
echo 💬 Example queries to try:
echo    • Show all pending invoices
echo    • What's the total amount due?
echo    • Find invoices related to office supplies
echo.

pause
