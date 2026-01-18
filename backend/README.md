# Invox Backend 2 - FastAPI with OAuth

A production-ready FastAPI backend with NextAuth-compatible OAuth authentication and PostgreSQL database, designed to work seamlessly with the Next.js frontend.

## 🌟 Features

- 🔐 **OAuth Authentication** - Google OAuth with NextAuth integration
- 🗄️ **PostgreSQL Database** - Robust data storage with SQLAlchemy ORM
- 🔑 **JWT Tokens** - Secure token-based authentication
- 📝 **Database Migrations** - Version-controlled schema changes with Alembic
- 🎯 **RESTful API** - Clean, intuitive API design
- 📚 **Auto Documentation** - Interactive API docs with Swagger UI
- 🔒 **Security First** - Password hashing, CORS protection, token verification
- 🚀 **Production Ready** - Proper error handling, logging, and configuration

## 📋 Quick Links

| Document                                               | Description                        |
| ------------------------------------------------------ | ---------------------------------- |
| [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)               | ✅ Step-by-step setup checklist    |
| [SETUP_GUIDE.md](SETUP_GUIDE.md)                       | 📖 Detailed setup instructions     |
| [ARCHITECTURE.md](ARCHITECTURE.md)                     | 🏗️ System architecture & diagrams  |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | 📊 Complete implementation details |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md)               | ⚡ Common commands & tips          |

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Google OAuth credentials

### 1. Database Setup

```bash
createdb invox_db
createuser invox_user -P
```

### 2. Backend Configuration

```bash
cd backend2
cp .env.example .env
# Edit .env with your credentials
```

### 3. Install & Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

Visit http://localhost:8001/docs for API documentation!

## 📁 Project Structure

```
backend2/
├── app/
│   ├── api/
│   │   ├── deps.py              # Dependencies (auth, db)
│   │   └── v1/
│   │       ├── api.py           # API router
│   │       └── endpoints/
│   │           ├── auth.py      # OAuth endpoints
│   │           └── users.py     # User endpoints
│   ├── core/
│   │   ├── config.py            # Configuration
│   │   └── security.py          # JWT & password utilities
│   ├── db/
│   │   ├── base.py              # Base model
│   │   └── session.py           # Database session
│   ├── models/
│   │   └── user.py              # User, Account, Session models
│   ├── schemas/
│   │   └── user.py              # Pydantic schemas
│   ├── services/
│   │   └── auth.py              # Authentication service
│   └── main.py                  # FastAPI application
├── alembic/                     # Database migrations
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
cd backend2
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/invox_db
NEXTAUTH_SECRET=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 3. Create Database

```bash
# Create PostgreSQL database
createdb invox_db
```

### 4. Run Migrations

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 5. Run the Server

```bash
uvicorn app.main:app --reload --port 8001
```

The API will be available at:

- API: http://localhost:8001
- Documentation: http://localhost:8001/docs
- Alternative docs: http://localhost:8001/redoc

## API Endpoints

### Authentication

- `POST /api/v1/auth/oauth/callback` - Handle OAuth callback from NextAuth
- `POST /api/v1/auth/verify-email` - Check if email exists
- `GET /api/v1/auth/me` - Get current user info (requires auth)

### Users

- `GET /api/v1/users/me` - Get current user profile (requires auth)
- `PUT /api/v1/users/me` - Update current user profile (requires auth)
- `GET /api/v1/users/{user_id}` - Get user by ID (requires auth)

## Database Models

### User

- Stores user profile information
- Compatible with NextAuth User model

### Account

- Stores OAuth provider information
- Links users to their OAuth accounts
- Compatible with NextAuth Account model

### Session

- Stores session information (when using database sessions)
- Compatible with NextAuth Session model

### VerificationToken

- For email verification tokens
- Compatible with NextAuth VerificationToken model

## Integration with NextAuth

The backend is designed to work seamlessly with NextAuth. Here's how to integrate:

1. **OAuth Flow**: When a user signs in with OAuth on the frontend, NextAuth handles the OAuth flow
2. **Backend Callback**: After successful OAuth, call the `/api/v1/auth/oauth/callback` endpoint with the user data
3. **JWT Token**: The backend returns a JWT token that can be used for subsequent API calls
4. **Store Token**: Store this token in the NextAuth session for use with backend API calls

## Development

### Create New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### Check Current Migration

```bash
alembic current
```

## Testing

```bash
pytest
```

## Security Notes

- Always use HTTPS in production
- Keep `NEXTAUTH_SECRET` secure and never commit it
- Rotate OAuth credentials regularly
- Use environment variables for sensitive data
- Implement rate limiting for production

## License

MIT
