# Invox - Quick Start Guide

## Prerequisites

-   Node.js (v18 or higher)
-   pnpm
-   Python 3.9+
-   PostgreSQL database

## Quick Setup (5 minutes)

### 1. Backend Setup

```powershell
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database (make sure PostgreSQL is running)
# Update DATABASE_URL in backend/.env
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend runs at: http://127.0.0.1:8000

### 2. Frontend Setup

```powershell
# From project root
pnpm install

# Create environment file
copy .env.example .env.local

# Start frontend
pnpm dev
```

Frontend runs at: http://localhost:3000

## Testing the Integration

### ✅ Test Authentication

1. Visit http://localhost:3000
2. Click **Login** in navbar
3. Authenticate with Google
4. Should redirect to dashboard

### ✅ Test Invoice Upload

1. In dashboard, click **Upload Documents**
2. Select PDF or image file
3. Click **Upload**
4. Invoice appears in list below

### ✅ Test Invoice Verification

1. Find invoice with "Verify" button
2. Click **Verify**
3. Status changes to "Verified"

### ✅ Test Logout

1. Click user avatar (bottom left)
2. Click **Log out**
3. Redirects to homepage

## Environment Variables

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Backend (.env)

```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SECRET_KEY=your_secret_key_for_jwt
DATABASE_URL=postgresql://user:password@localhost/dbname
GOOGLE_API_KEY=your_gemini_api_key
```

## What Changed?

All frontend pages now use the **FastAPI backend** for:

-   ✅ Google OAuth authentication
-   ✅ JWT token management
-   ✅ Invoice fetching (`GET /api/v1/invoices/my_invoices`)
-   ✅ Invoice upload (`POST /api/v1/invoices/upload_pdf`)
-   ✅ Invoice update (`PUT /api/v1/invoices/{id}`)

### Key Files:

-   `lib/api/client.ts` - API client with axios
-   `app/auth/callback/page.tsx` - OAuth callback handler
-   `app/signin/page.tsx` - Redirects to backend OAuth
-   `components/AnimatedListItemUse.tsx` - Fetches invoices from backend
-   `components/UploadDialog.tsx` - Uploads to backend

## Troubleshooting

**Issue: CORS errors**

-   Make sure backend CORS allows `http://localhost:3000`
-   Check `backend/app/main.py`

**Issue: 401 Unauthorized**

-   Clear localStorage: `localStorage.clear()`
-   Login again

**Issue: Backend not responding**

-   Verify backend is running on port 8000
-   Check backend terminal for errors

**Issue: Database errors**

-   Ensure PostgreSQL is running
-   Run migrations: `alembic upgrade head`

## Full Documentation

See `INTEGRATION_GUIDE.md` for complete details on:

-   Authentication flow
-   API endpoints
-   Response formats
-   Security features
-   Troubleshooting
-   Future improvements

## Support

For issues or questions, check the console logs:

-   **Frontend**: Browser DevTools Console
-   **Backend**: Terminal running uvicorn
