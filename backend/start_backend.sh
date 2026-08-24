#!/bin/bash

# Start Invox Backend (FastAPI)
# Run from: /home/ash/Coding/ML/FastAPI Implementation/Invox/backend/
set -e

echo "🚀 Starting Invox Backend (FastAPI)..."

# ── 1. Virtual environment ────────────────────────────────────────────────────
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

PYTHON="venv/bin/python"
PIP="venv/bin/pip"
UVICORN="venv/bin/uvicorn"

# ── 2. Install / sync dependencies (uses hash to skip if unchanged) ───────────
REQ_HASH=$(md5sum requirements.txt 2>/dev/null | awk '{print $1}')
HASH_FILE="venv/.req_hash"

if [ ! -f "$HASH_FILE" ] || [ "$(cat $HASH_FILE 2>/dev/null)" != "$REQ_HASH" ]; then
    echo "📥 Installing / updating dependencies..."
    $PIP install --upgrade pip -q
    $PIP install -r requirements.txt -q
    echo "$REQ_HASH" > "$HASH_FILE"
    echo "✅ Dependencies up to date!"
else
    echo "✅ Dependencies already installed (requirements.txt unchanged)"
fi

# ── 3. Check .env ─────────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "📝 Created .env from .env.example — please fill in your secrets."
    else
        echo "❌ Error: .env.example not found either!"
    fi
    exit 1
fi

# ── 4. Run DB migrations ──────────────────────────────────────────────────────
echo "🗄️  Running database migrations (alembic upgrade head)..."
$PYTHON -m alembic upgrade head && echo "✅ Migrations applied!" || {
    echo "⚠️  Migration step failed or already up to date — continuing..."
}

# ── 5. Start server ───────────────────────────────────────────────────────────
echo ""
echo "✨ Starting server..."
echo "📍 URL:    http://localhost:8000"
echo "📚 Docs:   http://localhost:8000/docs"
echo "🏥 Health: http://localhost:8000/health"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

exec $UVICORN app.main:app --reload --port 8000 --host 0.0.0.0
