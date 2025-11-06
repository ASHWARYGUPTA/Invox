# Export Feature Documentation

## Overview

The export feature allows users to download their invoices in CSV or JSON format with advanced filtering options.

## Features

### Export Formats

-   **CSV**: Comma-separated values file, perfect for Excel/Google Sheets
-   **JSON**: Structured JSON format for programmatic use

### Available Filters

#### 1. **Status**

Filter invoices by their approval status:

-   `All` - Export all invoices
-   `Approved` - Only verified/approved invoices
-   `Needs Review` - Only invoices pending review

#### 2. **Date Range**

Filter by invoice date:

-   **Start Date**: Include invoices from this date onwards
-   **End Date**: Include invoices up to this date

#### 3. **Amount Range**

Filter by invoice amount:

-   **Min Amount**: Include invoices with amount >= this value
-   **Max Amount**: Include invoices with amount <= this value

#### 4. **Vendor Name**

Search and filter by vendor name (partial match supported)

## How to Use

### From Dashboard

1. Click the **"Export"** button in the Invoice Overview section
2. A dialog will open with export options
3. Select your preferred format (CSV or JSON)
4. (Optional) Apply any filters you need
5. Click **"Export"** to download the file
6. Use **"Reset"** to clear all filters

### API Endpoint

**Endpoint**: `GET /api/v1/invoices/export`

**Query Parameters**:

-   `format` (required): "csv" or "json"
-   `status` (optional): "approved" or "needs_review"
-   `start_date` (optional): YYYY-MM-DD format
-   `end_date` (optional): YYYY-MM-DD format
-   `min_amount` (optional): Number
-   `max_amount` (optional): Number
-   `vendor_name` (optional): String (partial match)

**Example Request**:

```bash
GET /api/v1/invoices/export?format=csv&status=approved&start_date=2025-01-01&end_date=2025-12-31
```

**Response**:

-   Returns file as attachment download
-   Filename includes timestamp: `invoices_export_YYYYMMDD_HHMMSS.csv`

## CSV Export Format

Columns included:

-   Invoice ID
-   Vendor Name
-   Amount Due
-   Currency
-   Invoice Date
-   Due Date
-   Status
-   Confidence Score
-   File Name
-   Created At

## JSON Export Format

Each invoice includes:

```json
{
	"id": 1,
	"invoice_id": "INV-001",
	"vendor_name": "Acme Corp",
	"amount_due": 1250.0,
	"currency_code": "USD",
	"invoice_date": "2025-01-15",
	"due_date": "2025-02-15",
	"status": "approved",
	"confidence_score": 0.95,
	"file_name": "invoice_001.pdf",
	"created_at": "2025-01-15T10:30:00",
	"updated_at": "2025-01-15T14:20:00"
}
```

## Use Cases

### 1. **Accounting Reports**

Export all approved invoices for a specific month:

-   Format: CSV
-   Status: Approved
-   Start Date: 2025-01-01
-   End Date: 2025-01-31

### 2. **Vendor Analysis**

Export all invoices from a specific vendor:

-   Format: JSON
-   Vendor Name: "Acme"

### 3. **High-Value Invoices**

Export invoices above a certain amount:

-   Format: CSV
-   Min Amount: 5000
-   Status: All

### 4. **Pending Review**

Export all invoices needing verification:

-   Format: CSV
-   Status: Needs Review

## Implementation Details

### Frontend

-   **Component**: `components/ExportDialog.tsx`
-   **API Client**: `lib/api/client.ts` - `invoiceApi.exportInvoices()`
-   **Usage**: Integrated in `DashboardContent.tsx`

### Backend

-   **Endpoint**: `backend/app/api/endpoints/invoices.py` - `/export` route
-   **Authentication**: Requires JWT token (user-specific data only)
-   **Response**: StreamingResponse with file attachment

## Security

-   ✅ User can only export their own invoices
-   ✅ JWT authentication required
-   ✅ All filters are server-side validated
-   ✅ No SQL injection vulnerability (using SQLAlchemy ORM)

## Future Enhancements

-   [ ] Export to Excel (.xlsx) format
-   [ ] Email export results
-   [ ] Scheduled exports
-   [ ] Custom column selection
-   [ ] Multiple status selection
-   [ ] Currency conversion options
