# Frontend-Backend Integration Guide

## Overview

This document describes the integration between the Next.js frontend and FastAPI backend for the Invox application.

## What Was Changed

### 1. **API Client Setup** (`lib/api/client.ts`)

Created a centralized API client with:

-   Axios instance configured for the backend API
-   Token management (storage, retrieval, removal)
-   Automatic authentication header injection
-   Automatic 401 error handling with redirect to signin
-   API endpoints for authentication and invoice operations

### 2. **Authentication Flow**

#### Google OAuth Flow:

1. User clicks "Login" button on homepage → Redirects to `/signin`
2. `/signin` page automatically redirects to backend Google OAuth endpoint: `http://127.0.0.1:8000/api/v1/auth/google`
3. Backend redirects user to Google login page
4. User authenticates with Google
5. Google redirects back to backend callback: `http://127.0.0.1:8000/api/v1/auth/google/callback`
6. Backend creates/retrieves user, generates JWT token
7. Backend redirects to frontend callback: `http://localhost:3000/auth/callback#token=<JWT>`
8. Frontend callback page extracts token from URL hash, stores in localStorage
9. User is redirected to `/dashboard`

#### Files Modified/Created:

-   **Created**: `app/auth/callback/page.tsx` - Handles OAuth callback and token storage
-   **Modified**: `app/signin/page.tsx` - Auto-redirects to backend OAuth
-   **Modified**: `app/dashboard/page.tsx` - Added authentication guard
-   **Modified**: `components\nav-user.tsx` - Added logout functionality

### 3. **Dashboard Invoice Fetching**

#### Invoice List:

-   **Modified**: `components/AnimatedListItemUse.tsx`
    -   Removed NextAuth session dependency
    -   Uses `invoiceApi.getMyInvoices()` to fetch from backend
    -   Token automatically included in request headers
    -   Displays invoices in proper format matching backend schema
    -   "Verify" button updates invoice status to "approved"

#### Backend Endpoint Used:

```
GET /api/v1/invoices/my_invoices
Headers: Authorization: Bearer <token>
Returns: Array of Invoice objects
```

### 4. **Invoice Upload**

#### Upload Dialog:

-   **Modified**: `components/UploadDialog.tsx`
    -   Integrated with backend upload API
    -   Shows upload progress for each file
    -   Displays success/error status per file
    -   Supports PDF, PNG, JPG, JPEG files
    -   Refreshes invoice list after successful upload

#### Backend Endpoint Used:

```
POST /api/v1/invoices/upload_pdf
Headers: Authorization: Bearer <token>
Content-Type: multipart/form-data
Body: file (FormData)
Returns: Invoice object
```

### 5. **Invoice Update/Verification**

#### Verify Functionality:

-   **Modified**: `components/AnimatedListItemUse.tsx`
    -   "Verify" button calls `invoiceApi.updateInvoice()`
    -   Updates invoice status to "approved"
    -   Refreshes invoice list after update

#### Backend Endpoint Used:

```
PUT /api/v1/invoices/{invoice_id}
Headers: Authorization: Bearer <token>
Body: { status: "approved" }
Returns: Updated Invoice object
```

### 6. **Other UI Updates**

-   **Modified**: `pages/home/HeroSection.tsx` - "Upload Document" button redirects to signup
-   **Modified**: `components/NavBarMenu.tsx` - Login button redirects to `/signin`

## Backend API Endpoints Used

All endpoints are prefixed with `http://127.0.0.1:8000`

### Authentication

| Endpoint                       | Method | Description                   | Auth Required |
| ------------------------------ | ------ | ----------------------------- | ------------- |
| `/api/v1/auth/google`          | GET    | Redirects to Google OAuth     | No            |
| `/api/v1/auth/google/callback` | GET    | Handles Google OAuth callback | No            |

### Invoices

| Endpoint                        | Method | Description         | Auth Required |
| ------------------------------- | ------ | ------------------- | ------------- |
| `/api/v1/invoices/my_invoices`  | GET    | Get user's invoices | Yes           |
| `/api/v1/invoices/upload_pdf`   | POST   | Upload invoice file | Yes           |
| `/api/v1/invoices/{invoice_id}` | PUT    | Update invoice      | Yes           |

## Environment Variables

### Frontend (`.env.local`)

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Backend (`.env`)

The backend should have these variables set (in `backend/.env`):

```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend will run on: `http://127.0.0.1:8000`

### 2. Frontend Setup

```bash
# From project root directory

# Install dependencies
pnpm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > .env.local

# Start development server
pnpm dev
```

Frontend will run on: `http://localhost:3000`

## How to Test the Integration

### 1. Test Authentication Flow

1. Navigate to `http://localhost:3000`
2. Click "Login" button in navbar
3. You'll be redirected through Google OAuth
4. After successful authentication, you'll land on `/dashboard`
5. Your JWT token is stored in `localStorage` as `invox_access_token`

### 2. Test Invoice Upload

1. Login to dashboard
2. Click "Upload Documents" button
3. Select one or more PDF/image files
4. Click "Upload"
5. Watch upload progress
6. Invoices should appear in the list below

### 3. Test Invoice Fetching

1. On dashboard, invoice list loads automatically
2. Should display all invoices for the logged-in user
3. Each invoice shows: Invoice ID, Vendor, Amount, Dates, Confidence Score

### 4. Test Invoice Verification

1. Find an invoice with status "needs_review"
2. Click "Verify" button
3. Invoice status changes to "approved"
4. List refreshes automatically

### 5. Test Logout

1. Click user avatar in sidebar (bottom left)
2. Click "Log out"
3. You're redirected to homepage
4. Token is cleared from localStorage

## Security Features

✅ **JWT Token Authentication**: All protected API calls include Bearer token
✅ **Automatic Token Injection**: API client adds token to all requests
✅ **401 Auto-Redirect**: Expired/invalid tokens redirect to signin
✅ **Route Protection**: Dashboard checks authentication before rendering
✅ **Secure Token Storage**: Token stored in localStorage (client-side only)
✅ **CORS Configuration**: Backend allows frontend origin

## Troubleshooting

### Issue: "Could not validate credentials"

-   **Cause**: Token expired or invalid
-   **Solution**: Clear localStorage and login again

```javascript
localStorage.removeItem("invox_access_token");
```

### Issue: "Network Error" on API calls

-   **Cause**: Backend not running
-   **Solution**: Start backend server on port 8000

### Issue: CORS errors

-   **Cause**: Backend CORS not configured for frontend URL
-   **Solution**: Check `backend/app/main.py` CORS settings include `http://localhost:3000`

### Issue: Upload fails silently

-   **Cause**: File type not supported or backend processing error
-   **Solution**: Check browser console and backend logs for detailed error

### Issue: Invoices not loading

-   **Cause**: Not authenticated or backend database empty
-   **Solution**: Login first, then upload some invoices

## API Response Formats

### Invoice Object

```typescript
{
	id: number;
	file_name: string;
	invoice_id: string | null;
	vendor_name: string | null;
	amount_due: number | null;
	due_date: string | null;
	invoice_date: string | null;
	currency_code: string | null;
	confidence_score: number | null; // 0.0 to 1.0
	status: "needs_review" | "approved";
	created_at: string;
	updated_at: string;
	owner_id: number;
}
```

## Next Steps / Future Improvements

1. **Error Boundaries**: Add React error boundaries for better error handling
2. **Toast Notifications**: Add toast/notification system for user feedback
3. **Optimistic Updates**: Update UI before API response for better UX
4. **Invoice Editing**: Add UI for editing invoice fields before verification
5. **Export Functionality**: Implement CSV/JSON export using backend data
6. **Pagination**: Add pagination for invoice list
7. **Search/Filter**: Add search and filter capabilities
8. **Refresh Token**: Implement refresh token mechanism for better security
9. **User Profile**: Display actual user info from backend in sidebar
10. **Invoice Details**: Add detail view for individual invoices

## Files Modified Summary

### Created Files:

-   `lib/api/client.ts` - API client and utilities
-   `app/auth/callback/page.tsx` - OAuth callback handler
-   `.env.example` - Environment variable template

### Modified Files:

-   `app/signin/page.tsx` - Auto-redirect to backend OAuth
-   `app/dashboard/page.tsx` - Authentication guard
-   `components/AnimatedListItemUse.tsx` - Fetch and display invoices from backend
-   `components/UploadDialog.tsx` - Upload to backend API
-   `components/nav-user.tsx` - Logout functionality
-   `pages/home/HeroSection.tsx` - Upload button behavior

## Notes

-   The application uses **client-side routing** (Next.js App Router)
-   Authentication tokens are stored in **browser localStorage**
-   All API calls go through the centralized **apiClient** instance
-   The backend handles all business logic and data processing
-   Frontend focuses on presentation and user interaction
