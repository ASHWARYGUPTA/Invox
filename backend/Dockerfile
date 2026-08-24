# ============================================================
# Invox Backend - FastAPI Dockerfile
# Uses Python 3.12 (stable & compatible with all dependencies)
# ============================================================

FROM python:3.12-slim

# System dependencies required by PyMuPDF, psycopg, chromadb, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Upgrade pip and install wheel/setuptools first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first (Docker cache optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for ChromaDB persistence
RUN mkdir -p /app/chroma_db

# Expose the FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
