# Invox Backend2 Setup Guide

This guide will help you set up the FastAPI backend with OAuth authentication integrated with NextAuth.

## Architecture Overview

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Next.js   │ ──────► │   NextAuth   │ ──────► │   FastAPI   │
│   Frontend  │ ◄────── │   (OAuth)    │ ◄────── │   Backend   │
└─────────────┘         └──────────────┘         └─────────────┘
                               │                         │
                               │                         │
                               ▼                         ▼
                        ┌──────────────┐         ┌─────────────┐
                        │    Google    │         │ PostgreSQL  │
                        │    OAuth     │         │  Database   │
                        └──────────────┘         └─────────────┘
```

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Node.js 18+
- Google OAuth credentials

## Step 1: Set up PostgreSQL Database

```bash
# Install PostgreSQL (if not already installed)
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Start PostgreSQL service
sudo service postgresql start  # Linux
brew services start postgresql  # macOS

# Create database
sudo -u postgres psql
CREATE DATABASE invox_db;
CREATE USER invox_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE invox_db TO invox_user;
\q
```

## Step 2: Configure Backend Environment

```bash
cd backend2

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

Update the following in `.env`:

```env
DATABASE_URL=postgresql://invox_user:your_password@localhost:5432/invox_db
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=generate-a-secure-random-string-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**Generate NEXTAUTH_SECRET:**

```bash
openssl rand -base64 32
```

## Step 3: Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Set up Database with Alembic

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration with NextAuth tables"

# Apply migration
alembic upgrade head
```

## Step 5: Configure Frontend Environment

```bash
cd ..  # Back to root

# Copy environment template
cp .env.local.example .env.local

# Edit .env.local
nano .env.local
```

Update `.env.local`:

```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=same-secret-as-backend
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
NEXT_PUBLIC_BACKEND_URL=http://localhost:8001
```

## Step 6: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Configure OAuth consent screen
6. Add authorized redirect URIs:
   - `http://localhost:3000/api/auth/callback/google`
   - `http://localhost:3000/auth/callback`
7. Copy Client ID and Client Secret

## Step 7: Start the Backend

```bash
cd backend2

# Make start script executable
chmod +x start_backend.sh

# Start backend
./start_backend.sh

# Or manually:
uvicorn app.main:app --reload --port 8001
```

Backend will be available at:

- API: http://localhost:8001
- Docs: http://localhost:8001/docs
- Health: http://localhost:8001/health

## Step 8: Start the Frontend

```bash
# In a new terminal, from project root
pnpm install  # or npm install

# Start development server
pnpm dev  # or npm run dev
```

Frontend will be available at: http://localhost:3000

## Testing the Authentication

1. Open http://localhost:3000
2. Click "Sign In"
3. Select "Sign in with Google"
4. Authorize the application
5. You should be redirected back and logged in

## Verify Database

Check that user data was created in PostgreSQL:

```bash
psql -U invox_user -d invox_db

-- View users
SELECT * FROM users;

-- View accounts (OAuth providers)
SELECT * FROM accounts;

-- View sessions
SELECT * FROM sessions;
```

## API Testing with Curl

### Test OAuth Callback (simulated)

```bash
curl -X POST http://localhost:8001/api/v1/auth/oauth/callback \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "image": "https://example.com/avatar.jpg",
    "provider": "google",
    "provider_account_id": "123456789",
    "access_token": "ya29.xxx",
    "token_type": "Bearer",
    "expires_at": 1234567890,
    "scope": "openid email profile"
  }'
```

### Get Current User (with JWT token)

```bash
# Replace YOUR_JWT_TOKEN with actual token from sign-in response
curl -X GET http://localhost:8001/api/v1/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
sudo service postgresql status

# Test connection
psql -U invox_user -d invox_db -h localhost
```

### Migration Issues

```bash
# Reset database (WARNING: Deletes all data)
alembic downgrade base
alembic upgrade head

# Or recreate migration
rm alembic/versions/*.py
alembic revision --autogenerate -m "Recreate initial migration"
alembic upgrade head
```

### Port Already in Use

```bash
# Check what's using port 8001
lsof -i :8001
kill -9 <PID>  # Kill the process

# Or use different port
uvicorn app.main:app --reload --port 8002
```

### CORS Issues

Make sure `BACKEND_CORS_ORIGINS` in `backend2/app/core/config.py` includes your frontend URL.

## Project Structure

```
backend2/
├── app/
│   ├── api/
│   │   ├── deps.py              # Auth dependencies
│   │   └── v1/
│   │       ├── api.py           # Main API router
│   │       └── endpoints/
│   │           ├── auth.py      # OAuth endpoints
│   │           └── users.py     # User endpoints
│   ├── core/
│   │   ├── config.py            # Configuration
│   │   └── security.py          # JWT utilities
│   ├── db/
│   │   ├── base.py              # SQLAlchemy base
│   │   └── session.py           # Database session
│   ├── models/
│   │   └── user.py              # User, Account, Session models
│   ├── schemas/
│   │   └── user.py              # Pydantic schemas
│   ├── services/
│   │   └── auth.py              # Auth business logic
│   └── main.py                  # FastAPI app
├── alembic/                     # Database migrations
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── start_backend.sh             # Start script
```

## Next Steps

1. **Add more OAuth providers** (GitHub, Microsoft, etc.)
2. **Implement email verification**
3. **Add refresh token rotation**
4. **Set up proper logging**
5. **Add rate limiting**
6. **Configure production settings**
7. **Set up CI/CD**
8. **Add comprehensive tests**

## Production Deployment

### Backend

1. Use production database (managed PostgreSQL recommended)
2. Set secure `NEXTAUTH_SECRET`
3. Use HTTPS
4. Configure production CORS origins
5. Set up monitoring and logging
6. Use environment-specific settings
7. Deploy with Gunicorn or similar:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Frontend

1. Update `NEXT_PUBLIC_BACKEND_URL` to production backend URL
2. Configure production OAuth redirect URIs
3. Deploy to Vercel, Netlify, or similar
4. Set environment variables in deployment platform

## Support

For issues, please check:

- Backend logs: `backend2/logs/`
- Frontend console in browser DevTools
- PostgreSQL logs: `/var/log/postgresql/`

## License

MIT
