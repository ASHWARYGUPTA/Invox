/**
 * Invox Application Configuration
 * Centralized configuration values for the application
 */

/**
 * Invoice confidence score threshold (0.0 to 1.0)
 * Invoices with confidence scores below this threshold will be flagged for review
 *
 * Default: 0.87 (87%)
 *
 * Interpretation:
 * - 0.90+ : High confidence - AI is very sure about extraction
 * - 0.80-0.89 : Medium confidence - Should be reviewed
 * - Below 0.80 : Low confidence - Definitely needs review
 */
export const INVOICE_CONFIDENCE_THRESHOLD = 0.87;

/**
 * API Configuration
 */
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000",
  TIMEOUT: 30000, // 30 seconds
};

/**
 * Email Polling Configuration
 */
export const EMAIL_CONFIG = {
  DEFAULT_POLLING_INTERVAL: 60, // seconds
  MAX_EMAILS_PER_POLL: 5,
};

/**
 * Invoice Upload Configuration
 */
export const UPLOAD_CONFIG = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: ["application/pdf", "image/jpeg", "image/jpg", "image/png"],
};

/**
 * UI Configuration
 */
export const UI_CONFIG = {
  INVOICES_PER_PAGE: 10,
  AUTO_REFRESH_INTERVAL: 30000, // 30 seconds
};

/**
 * Status Color Mapping
 */
export const STATUS_COLORS = {
  completed: {
    bg: "bg-green-100",
    text: "text-green-700",
    border: "border-green-500/30",
  },
  pending: {
    bg: "bg-yellow-100",
    text: "text-yellow-700",
    border: "border-yellow-500/30",
  },
  processing: {
    bg: "bg-blue-100",
    text: "text-blue-700",
    border: "border-blue-500/30",
  },
  failed: {
    bg: "bg-red-100",
    text: "text-red-700",
    border: "border-red-500/30",
  },
};

/**
 * Status Display Names
 */
export const STATUS_LABELS = {
  completed: "Completed",
  pending: "Pending",
  processing: "Processing",
  failed: "Failed",
};
