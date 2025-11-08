"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Loader2, Mail, CheckCircle2, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { tokenManager, emailConfigApi } from "@/lib/api/client";

interface GmailOAuthButtonProps {
  onSuccess: (email: string) => void;
  onError?: (error: string) => void;
  disabled?: boolean;
}

export function GmailOAuthButton({
  onSuccess,
  onError,
  disabled,
}: GmailOAuthButtonProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleGmailOAuth = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // Check if user is authenticated
      const token = tokenManager.getToken();
      if (!token) {
        throw new Error("Not authenticated. Please sign in first.");
      }

      // Step 1: Get authorization URL from backend
      const { auth_url, state } = await emailConfigApi.getGmailAuthUrl();

      // Store state for verification
      sessionStorage.setItem("gmail_oauth_state", state);

      // Step 2: Open OAuth popup
      const popup = window.open(
        auth_url,
        "gmail-oauth",
        "width=600,height=700,left=200,top=100,toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes"
      );

      if (!popup) {
        throw new Error(
          "Popup blocked! Please allow popups for this site and try again."
        );
      }

      // Step 3: Listen for callback
      const handleMessage = async (event: MessageEvent) => {
        // Security: Verify origin
        if (event.origin !== window.location.origin) {
          return;
        }

        if (event.data.type === "gmail-oauth-callback") {
          const { code, state: callbackState } = event.data;

          // Verify state matches
          const storedState = sessionStorage.getItem("gmail_oauth_state");
          if (callbackState !== storedState) {
            setError("Security verification failed. Please try again.");
            setLoading(false);
            window.removeEventListener("message", handleMessage);
            return;
          }

          try {
            // Send to backend
            const result = await emailConfigApi.gmailCallback(
              code,
              callbackState
            );

            setSuccess(`Successfully connected to ${result.email_address}! ✓`);
            onSuccess(result.email_address);

            // Close popup
            if (popup && !popup.closed) {
              popup.close();
            }
          } catch (err: any) {
            setError(err.message || "Failed to complete OAuth flow");
            if (onError) {
              onError(err.message);
            }
          } finally {
            setLoading(false);
            window.removeEventListener("message", handleMessage);
            sessionStorage.removeItem("gmail_oauth_state");
          }
        } else if (event.data.type === "gmail-oauth-error") {
          setError(event.data.error || "OAuth authorization failed");
          if (onError) {
            onError(event.data.error);
          }
          setLoading(false);
          window.removeEventListener("message", handleMessage);
          sessionStorage.removeItem("gmail_oauth_state");
        }
      };

      window.addEventListener("message", handleMessage);

      // Monitor popup close
      const checkPopupClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkPopupClosed);
          if (loading && !success) {
            setLoading(false);
            setError("Authorization cancelled. Please try again.");
            window.removeEventListener("message", handleMessage);
            sessionStorage.removeItem("gmail_oauth_state");
          }
        }
      }, 1000);
    } catch (err: any) {
      console.error("Gmail OAuth error:", err);
      setError(err.message || "Failed to initiate OAuth flow");
      if (onError) {
        onError(err.message);
      }
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      <Button
        type="button"
        onClick={handleGmailOAuth}
        disabled={disabled || loading}
        className="w-full gap-2 bg-white hover:bg-gray-50 text-gray-900 border border-gray-300"
      >
        {loading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Connecting...
          </>
        ) : (
          <>
            <svg
              className="h-5 w-5"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                fill="#4285F4"
              />
              <path
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                fill="#34A853"
              />
              <path
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                fill="#FBBC05"
              />
              <path
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                fill="#EA4335"
              />
            </svg>
            Connect with Google
          </>
        )}
      </Button>

      {success && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            {success}
          </AlertDescription>
        </Alert>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {loading && (
        <p className="text-sm text-muted-foreground text-center">
          Please complete the authorization in the popup window...
        </p>
      )}
    </div>
  );
}
