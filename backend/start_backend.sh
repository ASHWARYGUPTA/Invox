#!/bin/bash

# Start Backend2 (FastAPI)
# This script starts the FastAPI backend with uvicorn

echo "🚀 Starting Invox Backend2 (FastAPI)..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.installed
    echo "✅ Dependencies installed!"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "📝 Please edit .env file with your configuration:"
        echo "   - DATABASE_URL (use postgresql+psycopg:// dialect)"
        echo "   - NEXTAUTH_SECRET"
        echo "   - GOOGLE_CLIENT_ID"
        echo "   - GOOGLE_CLIENT_SECRET"
        exit 1
    else
        echo "❌ Error: .env.example not found!"
        exit 1
    fi
fi

# Check if database tables exist, if not run migrations
echo "🗄️  Checking database migrations..."
python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)" 2>/dev/null || {
    echo "ℹ️  Note: If you need to run migrations, use: alembic upgrade head"
}

# Run the FastAPI application
echo ""
echo "✨ Starting server..."
echo "📍 URL: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo "🏥 Health: http://localhost:8000/health"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
