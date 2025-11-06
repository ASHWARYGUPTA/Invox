# Email Polling Feature

## Overview

The email polling feature automatically checks your Gmail inbox for invoice attachments and processes them into the database. This feature includes both manual and automatic polling capabilities.

## Features

### 1. **Manual Refresh Button**

-   **Icon**: Refresh icon (spinning when loading)
-   **Action**: Manually refreshes the invoice list from the database
-   **Use Case**: Quick update to see latest invoices without polling emails

### 2. **Check Emails Button**

-   **Icon**: Mail icon (pulsing when checking)
-   **Action**: Manually triggers email polling to check for new invoices
-   **Process**:
    -   Connects to Gmail API
    -   Checks last 5 unread emails
    -   Extracts PDF/image attachments
    -   Processes invoices with AI
    -   Adds new invoices to database
    -   Shows notification with results
    -   Refreshes invoice list

### 3. **Auto-Poll Toggle Button**

-   **Icon**: Play/Pause icon
-   **Action**: Starts/stops automatic email polling every 30 seconds
-   **States**:
    -   **Paused** (default): Click "Start Auto-Poll (30s)" to begin
    -   **Active**: Click "Pause Auto-Poll" to stop
-   **Behavior**:
    -   When started, immediately checks emails
    -   Then checks every 30 seconds automatically
    -   Shows "Last checked" timestamp
    -   Continues until paused or page closed

### 4. **Last Checked Timestamp**

-   **Display**: Shows time of last email poll
-   **Format**: "Last checked: HH:MM:SS AM/PM"
-   **Updates**: After each successful email poll

## Backend API

### New Endpoint: `POST /api/v1/invoices/poll-emails`

**Authentication**: Required (JWT token)

**Response**:

```json
{
  "success": true,
  "message": "Email polling completed. X new invoice(s) processed.",
  "invoices_count": X
}
```

**Process**:

1. Authenticates with Gmail API
2. Fetches unread emails (max 5)
3. Processes invoice attachments (PDF, PNG, JPG, JPEG)
4. Extracts data using Gemini AI
5. Saves to database linked to current user
6. Marks emails as read
7. Returns count of new invoices

## Frontend Integration

### Updated Components

**`components/AnimatedListItemUse.tsx`**:

-   Added three control buttons at the top
-   Implemented auto-refresh with 30-second interval
-   Added polling state management
-   Shows visual feedback (spinning icons, timestamps)

**`lib/api/client.ts`**:

-   Added `pollEmails()` function
-   Calls the new backend endpoint

## Usage

### Manual Check

1. Click **"Check Emails"** button
2. Wait for the polling process to complete
3. Alert shows how many new invoices were found
4. Invoice list automatically refreshes

### Automatic Polling

1. Click **"Start Auto-Poll (30s)"** button
2. System immediately checks emails
3. Then automatically checks every 30 seconds
4. "Last checked" timestamp updates after each check
5. Click **"Pause Auto-Poll"** to stop

### Just Refresh List

1. Click **"Refresh"** button
2. Invoice list reloads from database
3. No email polling occurs

## Configuration

### Polling Interval

-   Default: **30 seconds**
-   Can be changed in `AnimatedListItemUse.tsx`:
    ```typescript
    setInterval(() => {
    	pollAndRefresh();
    }, 30000); // Change this value (milliseconds)
    ```

### Max Emails to Check

-   Default: **5 most recent unread emails**
-   Can be changed in:
    -   `backend/app/worker/email_poller.py`: `MAX_EMAILS_TO_CHECK = 5`
    -   Backend endpoint calls: `check_for_invoices(service, db, max_emails=5)`

## Email Worker (Background Process)

The standalone email worker (`backend/app/worker/email_poller.py`) can still run independently:

```bash
cd backend
python -m app.worker.email_poller
```

This runs continuously in the background, checking every 30 seconds, independent of the web UI.

## Gmail API Setup

**Required**:

1. Google Cloud Project with Gmail API enabled
2. OAuth 2.0 credentials (`credentials.json`)
3. First-time authentication generates `token.json`

**Files**:

-   `backend/app/worker/credentials.json` - OAuth credentials
-   `backend/app/worker/token.json` - Generated auth token

## Notifications

### Success Messages

-   ✅ "X new invoice(s) found and added!"
-   📧 "No new invoices found in emails."

### Error Messages

-   ❌ "Failed to poll emails. Please try again."

## Technical Details

### State Management

```typescript
isAutoRefresh: boolean; // Auto-poll enabled/disabled
isPolling: boolean; // Currently checking emails
lastPollTime: Date | null; // Timestamp of last poll
```

### Interval Management

-   Uses `setInterval` for 30-second polling
-   Properly cleans up on unmount
-   Clears interval when paused

### API Flow

```
Frontend Button Click
  ↓
invoiceApi.pollEmails()
  ↓
POST /api/v1/invoices/poll-emails
  ↓
get_gmail_service()
  ↓
check_for_invoices()
  ↓
process_attachment()
  ↓
Save to Database
  ↓
Return count to frontend
  ↓
Refresh invoice list
  ↓
Show notification
```

## Security

-   **Authentication**: All API calls require valid JWT token
-   **User Isolation**: Invoices linked to authenticated user
-   **Gmail Access**: Uses OAuth 2.0 (user must authorize)
-   **Token Storage**: Refresh tokens stored securely server-side

## Limitations

1. **Gmail API Quotas**: Respect Gmail API rate limits
2. **Processing Time**: Large attachments may take longer
3. **Email Formats**: Only processes PDF/PNG/JPG/JPEG attachments
4. **Duplicates**: Automatically skipped (based on invoice ID + vendor)

## Future Enhancements

-   [ ] Configurable polling interval from UI
-   [ ] Email filter rules (from, subject, etc.)
-   [ ] Notification badges for new invoices
-   [ ] Background service worker for offline polling
-   [ ] Support for more file formats
-   [ ] Email preview before processing
