# Gmail API Authentication Fix - Summary

## Problem

The "Check Email" button in the frontend was failing with a 500 error:

```
ValueError: Authorized user info was not in the expected format, missing fields refresh_token.
```

## Root Cause

1. The `token.json` file didn't exist (first-time setup required)
2. The OAuth flow wasn't properly configured to request offline access and refresh tokens
3. Error handling was insufficient, making debugging difficult

## Solution Implemented

### 1. Enhanced Authentication Flow (`email_poller.py`)

-   **Improved error handling** for token file loading (catches `ValueError`)
-   **Better OAuth configuration**:
    -   Added `access_type='offline'` to ensure refresh token is requested
    -   Added `prompt='consent'` to force consent screen and guarantee refresh token
-   **Comprehensive error messages** to guide users through troubleshooting
-   **Automatic retry** if token refresh fails

### 2. Created Authentication Setup Script (`authenticate_gmail.py`)

-   Standalone script to properly authenticate with Gmail API
-   Forces fresh OAuth flow with refresh token
-   Validates token after creation
-   Tests the connection to ensure everything works
-   Provides clear success/failure messages

### 3. Created Test Script (`test_gmail_connection.py`)

-   Verifies Gmail API connection is working
-   Tests actual API calls
-   Checks for unread messages
-   Provides helpful troubleshooting tips

### 4. Updated API Endpoint (`invoices.py`)

-   **Better error handling** with specific exception types:
    -   `FileNotFoundError` → credentials.json missing
    -   `ValueError` → token issues (missing refresh_token)
    -   Generic exceptions with helpful messages
-   **Clearer error messages** that tell users exactly how to fix issues
-   **Documentation** in docstring explaining prerequisites

### 5. Updated Requirements (`requirements.txt`)

-   Reorganized with clear section headers
-   Removed duplicates
-   All necessary packages for Gmail API:
    -   `google-api-python-client`
    -   `google-auth-oauthlib`
    -   `google-auth-httplib2`

### 6. Created Documentation (`GMAIL_SETUP.md`)

-   Complete step-by-step setup guide
-   Troubleshooting section for common errors
-   Security notes
-   Configuration options

## Files Modified/Created

### Modified:

-   ✅ `backend/app/worker/email_poller.py` - Enhanced authentication and error handling
-   ✅ `backend/app/api/endpoints/invoices.py` - Better error messages for poll_emails endpoint
-   ✅ `backend/requirements.txt` - Cleaned up and organized

### Created:

-   ✅ `backend/app/worker/authenticate_gmail.py` - Authentication setup script
-   ✅ `backend/app/worker/test_gmail_connection.py` - Connection test script
-   ✅ `backend/app/worker/GMAIL_SETUP.md` - Complete setup documentation
-   ✅ `backend/app/worker/token.json` - Generated OAuth token (not in git)

## How to Use

### First-Time Setup:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python app\worker\authenticate_gmail.py
```

This will:

1. Open your browser for OAuth authorization
2. Create `token.json` with refresh token
3. Test the connection

### Test the Fix:

```powershell
python app\worker\test_gmail_connection.py
```

### Use in Frontend:

1. Start the backend server
2. Click "Check Email" button
3. It should now work without errors!

### Run Background Poller (Optional):

```powershell
python app\worker\email_poller.py
```

## Verification

✅ Authentication script runs successfully
✅ `token.json` created with `refresh_token` field
✅ Gmail API connection tested and working
✅ Email address verified: `abhinav.mishra.x.viii@gmail.com`
✅ Unread messages detected: 5 messages
✅ All packages installed in venv
✅ Error handling improved with helpful messages

## Security

-   ✅ `credentials.json` and `token.json` are in `.gitignore`
-   ✅ Sensitive files will not be committed to version control
-   ✅ Token contains refresh token for long-term access

## Next Steps for Users

1. **If not already done:** Run `python app\worker\authenticate_gmail.py`
2. **Test:** Click the "Check Email" button in the frontend
3. **Optional:** Run background email poller for automatic processing

## Technical Details

### OAuth Flow Changes:

```python
# OLD (problematic):
creds = flow.run_local_server(port=8080)

# NEW (fixed):
creds = flow.run_local_server(
    port=8080,
    access_type='offline',    # Get refresh token
    prompt='consent'          # Force consent screen
)
```

### Token Validation:

The `token.json` file now contains:

```json
{
	"token": "...",
	"refresh_token": "...", // This was missing before!
	"token_uri": "...",
	"client_id": "...",
	"client_secret": "...",
	"scopes": ["..."],
	"expiry": "..."
}
```

## Troubleshooting

If issues persist:

1. **Delete old token:**

    ```powershell
    Remove-Item backend\app\worker\token.json
    ```

2. **Re-authenticate:**

    ```powershell
    python backend\app\worker\authenticate_gmail.py
    ```

3. **Check logs** in backend console for detailed error messages

4. **Verify credentials.json** is valid and in correct location

5. **Ensure Gmail API** is enabled in Google Cloud Console
