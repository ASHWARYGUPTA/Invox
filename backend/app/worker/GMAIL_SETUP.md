# Gmail API Setup Guide

This guide explains how to set up Gmail API authentication for the Invoice Email Poller.

## Prerequisites

-   Google Cloud Project with Gmail API enabled
-   OAuth 2.0 credentials (credentials.json)
-   Python virtual environment activated

## Quick Setup

### 1. Activate Virtual Environment

```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Gmail API Credentials

1. **Get credentials.json:**
    - Go to [Google Cloud Console](https://console.cloud.google.com/)
    - Enable Gmail API for your project
    - Create OAuth 2.0 credentials (Web application type)
    - Add authorized redirect URIs:
        - `http://localhost:8080/`
        - `http://127.0.0.1:8080/`
    - Download the credentials JSON file
    - Save it as `credentials.json` in `backend/app/worker/` directory

### 4. Run Authentication Script

```powershell
python app\worker\authenticate_gmail.py
```

This script will:

-   Open a browser window for OAuth authorization
-   Ask you to sign in with your Gmail account
-   Generate a `token.json` file with refresh token
-   Test the Gmail API connection

**Important:** Make sure to:

-   Grant ALL requested permissions
-   Use the same Google account that will send/receive invoices

### 5. Verify Setup

After successful authentication, you should see:

```
✅ Successfully connected to Gmail!
   Email: your-email@gmail.com
   Total messages: XXXX

🎉 Authentication Complete!
```

## Troubleshooting

### Error: "missing fields refresh_token"

**Problem:** The token.json file doesn't contain a refresh_token.

**Solution:**

1. Delete the existing token.json:
    ```powershell
    Remove-Item app\worker\token.json
    ```
2. Run the authentication script again:
    ```powershell
    python app\worker\authenticate_gmail.py
    ```
3. Make sure to grant consent when prompted in the browser

### Error: "Credentials file not found"

**Problem:** credentials.json is missing or in the wrong location.

**Solution:**

1. Download OAuth 2.0 credentials from Google Cloud Console
2. Save as `credentials.json` in `backend/app/worker/` directory
3. Verify the file exists:
    ```powershell
    Test-Path app\worker\credentials.json
    ```

### Error: Port 8080 is already in use

**Problem:** Another application is using port 8080.

**Solution:**

1. Stop the application using port 8080, or
2. Modify the port in `authenticate_gmail.py` (lines 64-68)
3. Update the redirect URIs in Google Cloud Console to match the new port

### Error: "redirect_uri_mismatch"

**Problem:** The redirect URI is not authorized in Google Cloud Console.

**Solution:**

1. Go to Google Cloud Console → APIs & Services → Credentials
2. Edit your OAuth 2.0 Client ID
3. Add `http://localhost:8080/` to Authorized redirect URIs
4. Save and wait a few minutes for changes to propagate

## Using the Email Poller

### Manual Polling (Frontend Button)

Once authenticated, you can use the "Check Email" button in the frontend to manually trigger email polling.

### Automatic Polling (Background Worker)

To run continuous email monitoring:

```powershell
python app\worker\email_poller.py
```

This will:

-   Check for new emails every 30 seconds
-   Process invoice attachments automatically
-   Save invoices to the database
-   Mark processed emails as read

### Configuration

Edit `email_poller.py` to customize:

```python
MAX_EMAILS_TO_CHECK = 5      # Number of recent emails to check
POLLING_INTERVAL = 30        # Check every 30 seconds
DEFAULT_OWNER_ID = 1         # User ID to assign invoices to
```

## Security Notes

-   **Never commit credentials.json or token.json to version control**
-   Both files are already in `.gitignore`
-   The token.json file contains sensitive access tokens
-   Keep these files secure and private

## File Locations

```
backend/
├── app/
│   └── worker/
│       ├── credentials.json     # OAuth 2.0 credentials (required)
│       ├── token.json           # Generated access token (auto-created)
│       ├── email_poller.py      # Main email polling script
│       └── authenticate_gmail.py # Setup authentication script
```

## Next Steps

After successful setup:

1. ✅ Start the backend server:

    ```powershell
    uvicorn app.main:app --reload
    ```

2. ✅ Test the "Check Email" button in your frontend

3. ✅ (Optional) Run the background email poller:
    ```powershell
    python app\worker\email_poller.py
    ```

## Additional Resources

-   [Gmail API Documentation](https://developers.google.com/gmail/api)
-   [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
-   [Python Quickstart for Gmail API](https://developers.google.com/gmail/api/quickstart/python)
