#!/bin/bash

# RAG Chat System Setup Script
# Automated installation for Invoice RAG Chat

echo "🚀 Setting up RAG Chat System for Invox..."
echo ""

# Check if we're in the project root
if [ ! -d "backend" ] || [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Backend setup
echo "📦 Installing backend dependencies..."
cd backend

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment in ./venv..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        cd ..
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip first
echo "Upgrading pip..."
pip install --upgrade pip -q

# Install requirements (including existing requirements.txt)
echo "Installing Python packages..."
pip install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install requirements.txt dependencies"
    cd ..
    exit 1
fi

# Install RAG-specific dependencies
echo "Installing RAG-specific packages (this may take a few minutes)..."
echo "Note: sentence-transformers will download a small model (~80MB) on first use"
pip install -q chromadb==0.5.23 sentence-transformers==3.3.1

if [ $? -eq 0 ]; then
    echo "✅ Backend dependencies installed successfully"
else
    echo "❌ Failed to install RAG dependencies"
    cd ..
    exit 1
fi

# Check for GEMINI_API_KEY
if ! grep -q "GEMINI_API_KEY" .env 2>/dev/null; then
    echo ""
    echo "⚠️  Warning: GEMINI_API_KEY not found in backend/.env"
    echo "Please add your Gemini API key to backend/.env:"
    echo "GEMINI_API_KEY=your-api-key-here"
fi

# Deactivate venv before moving to frontend
deactivate 2>/dev/null

cd ..

# Frontend setup
echo ""
echo "📦 Installing frontend dependencies..."
pnpm install --silent

if [ $? -eq 0 ]; then
    echo "✅ Frontend dependencies installed successfully"
else
    echo "⚠️  Frontend installation had issues (may be okay if packages already installed)"
fi

# Create chroma_db directory if it doesn't exist
echo ""
echo "📁 Creating ChromaDB directory..."
mkdir -p chroma_db
chmod 755 chroma_db
echo "✅ ChromaDB directory created"

cd ..

# Summary
echo ""
echo "═══════════════════════════════════════════"
echo "✅ RAG Chat System Setup Complete!"
echo "═══════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Start backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
echo ""
echo "2. Start frontend (in new terminal):"
echo "   pnpm dev"
echo ""
echo "3. Navigate to: http://localhost:3000/chat"
echo "4. Click 'Re-index Invoices' to index your invoices"
echo "5. Start chatting with your invoices!"
echo ""
echo "📚 Documentation:"
echo "   - RAG_COMPLETE_GUIDE.md - Complete usage guide"
echo "   - RAG_SETUP_GUIDE.md - Quick setup guide"
echo "   - backend/RAG_CHAT_README.md - Full documentation"
echo ""
echo "💬 Example queries to try:"
echo "   • Show all pending invoices"
echo "   • What's the total amount due?"
echo "   • Find invoices related to office supplies"
echo ""
echo "⚙️  Troubleshooting:"
echo "   If you encounter any issues, check RAG_COMPLETE_GUIDE.md"
echo ""
