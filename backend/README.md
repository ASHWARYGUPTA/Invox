# Invoice Backend

FastAPI backend for the Invoice Management System with Gmail integration.

## Quick Start

### 1. Install Dependencies

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Set Up Gmail API (Required for Email Polling)

Run the authentication script to set up Gmail API:

```powershell
python app\worker\authenticate_gmail.py
```

This will:

-   Open a browser for OAuth authorization
-   Create `token.json` with proper credentials
-   Test the Gmail connection

**Note:** If you skip this step, the "Check Email" button won't work, but other features will function normally.

For detailed setup instructions, see: [`app/worker/GMAIL_SETUP.md`](app/worker/GMAIL_SETUP.md)

### 3. Start the Backend Server

```powershell
# Option 1: Use the helper script
.\start_backend.ps1

# Option 2: Manual start
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

The server will start on: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Features

### ✅ Invoice Management

-   Upload and process invoice files (PDF, PNG, JPG)
-   Extract invoice data using AI (Google Gemini)
-   CRUD operations for invoices
-   Export invoices (CSV, JSON)
-   Status management (Pending, Approved, Rejected)

### ✅ Email Integration

-   Automatic email polling for new invoices
-   Manual email checking via frontend button
-   Processes invoice attachments automatically
-   Marks processed emails as read

### ✅ Authentication

-   User registration and login
-   JWT-based authentication
-   Protected API endpoints

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   └── invoices.py      # Invoice CRUD & email polling
│   │   └── deps.py              # Dependencies (auth, db)
│   ├── core/
│   │   ├── config.py            # Configuration settings
│   │   └── security.py          # Password hashing, JWT
│   ├── crud/
│   │   ├── invoice.py           # Invoice database operations
│   │   └── user.py              # User database operations
│   ├── db/
│   │   ├── base.py              # Database base
│   │   └── session.py           # Database session
│   ├── models/
│   │   ├── invoice.py           # Invoice model
│   │   └── user.py              # User model
│   ├── schemas/
│   │   ├── invoice.py           # Invoice Pydantic schemas
│   │   └── user.py              # User Pydantic schemas
│   ├── services/
│   │   ├── canonicalization.py # Data normalization
│   │   └── processing_service.py # AI invoice processing
│   ├── worker/
│   │   ├── email_poller.py      # Email polling worker
│   │   ├── authenticate_gmail.py # Gmail setup script
│   │   ├── test_gmail_connection.py # Test script
│   │   └── GMAIL_SETUP.md       # Setup documentation
│   └── main.py                  # FastAPI app entry point
├── alembic/                     # Database migrations
├── requirements.txt             # Python dependencies
└── start_backend.ps1            # Quick start script
```

## API Endpoints

### Authentication

-   `POST /api/v1/auth/register` - Register new user
-   `POST /api/v1/auth/login` - Login user
-   `GET /api/v1/auth/me` - Get current user

### Invoices

-   `GET /api/v1/invoices/` - List all invoices
-   `GET /api/v1/invoices/{id}` - Get invoice by ID
-   `POST /api/v1/invoices/upload` - Upload and process invoice file
-   `PUT /api/v1/invoices/{id}` - Update invoice
-   `DELETE /api/v1/invoices/{id}` - Delete invoice
-   `POST /api/v1/invoices/poll-emails` - Check emails for new invoices
-   `GET /api/v1/invoices/export` - Export invoices (CSV/JSON)

## Testing

### Test Gmail Connection

```powershell
python app\worker\test_gmail_connection.py
```

### Test Email Polling

```powershell
python app\worker\email_poller.py
```

### Run Background Email Poller

The email poller continuously monitors for new invoice emails:

```powershell
python app\worker\email_poller.py
```

Configuration in `email_poller.py`:

```python
MAX_EMAILS_TO_CHECK = 5   # Check 5 most recent emails
POLLING_INTERVAL = 30     # Check every 30 seconds
DEFAULT_OWNER_ID = 1      # Assign to user ID 1
```

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/invoicedb

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google AI
GOOGLE_API_KEY=your-gemini-api-key

# CORS
FRONTEND_URL=http://localhost:3000
```

## Database Setup

### Run Migrations

```powershell
alembic upgrade head
```

### Create Default User

```powershell
python create_default_user.py
```

## Troubleshooting

### Gmail API Errors

**Error: "missing fields refresh_token"**

```powershell
# Delete old token and re-authenticate
Remove-Item app\worker\token.json
python app\worker\authenticate_gmail.py
```

**Error: "Credentials file not found"**

-   Download OAuth 2.0 credentials from Google Cloud Console
-   Save as `app/worker/credentials.json`

**Error: "redirect_uri_mismatch"**

-   Add `http://localhost:8080/` to authorized redirect URIs in Google Cloud Console

### Database Errors

**Error: "relation does not exist"**

```powershell
alembic upgrade head
```

**Error: "password authentication failed"**

-   Check DATABASE_URL in `.env` file
-   Verify PostgreSQL is running

### Import Errors

**Error: "ModuleNotFoundError"**

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

## Development

### Add New Dependencies

```powershell
pip install package-name
pip freeze > requirements.txt
```

### Create New Migration

```powershell
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Run with Auto-Reload

```powershell
uvicorn app.main:app --reload
```

## Documentation

-   **Gmail Setup Guide:** [`app/worker/GMAIL_SETUP.md`](app/worker/GMAIL_SETUP.md)
-   **Gmail Fix Summary:** [`../GMAIL_FIX_SUMMARY.md`](../GMAIL_FIX_SUMMARY.md)
-   **API Documentation:** Visit `http://localhost:8000/docs` when server is running

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the Gmail setup guide
3. Check server logs for detailed error messages
4. Ensure all environment variables are set correctly
