"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";

export default function GmailCallbackPage() {
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );
  const [message, setMessage] = useState("Processing authorization...");

  useEffect(() => {
    if (!searchParams) return;

    const code = searchParams.get("code");
    const state = searchParams.get("state");
    const error = searchParams.get("error");

    if (error) {
      setStatus("error");
      setMessage(`Authorization failed: ${error}`);

      // Send error to parent window
      if (window.opener) {
        window.opener.postMessage(
          {
            type: "gmail-oauth-error",
            error: error,
          },
          window.location.origin
        );
      }

      // Close after 3 seconds
      setTimeout(() => {
        window.close();
      }, 3000);
      return;
    }

    if (!code || !state) {
      setStatus("error");
      setMessage("Missing authorization code or state parameter");

      // Send error to parent window
      if (window.opener) {
        window.opener.postMessage(
          {
            type: "gmail-oauth-error",
            error: "Missing authorization parameters",
          },
          window.location.origin
        );
      }

      // Close after 3 seconds
      setTimeout(() => {
        window.close();
      }, 3000);
      return;
    }

    // Send callback data to parent window
    if (window.opener) {
      try {
        window.opener.postMessage(
          {
            type: "gmail-oauth-callback",
            code,
            state,
          },
          window.location.origin
        );

        setStatus("success");
        setMessage(
          "Authorization successful! Connecting your Gmail account..."
        );

        // Close after 2 seconds
        setTimeout(() => {
          window.close();
        }, 2000);
      } catch (err) {
        setStatus("error");
        setMessage("Failed to communicate with parent window");

        setTimeout(() => {
          window.close();
        }, 3000);
      }
    } else {
      setStatus("error");
      setMessage(
        "Parent window not found. Please reopen from the main application."
      );

      setTimeout(() => {
        window.close();
      }, 3000);
    }
  }, [searchParams]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-linear-to-br from-blue-50 to-indigo-50">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full mx-4">
        <div className="text-center">
          {status === "loading" && (
            <>
              <div className="flex justify-center mb-4">
                <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
              </div>
              <h1 className="text-2xl font-bold mb-2 text-gray-900">
                Connecting to Gmail
              </h1>
              <p className="text-gray-600">{message}</p>
            </>
          )}

          {status === "success" && (
            <>
              <div className="flex justify-center mb-4">
                <div className="bg-green-100 rounded-full p-3">
                  <CheckCircle2 className="h-12 w-12 text-green-600" />
                </div>
              </div>
              <h1 className="text-2xl font-bold mb-2 text-gray-900">
                Success!
              </h1>
              <p className="text-gray-600">{message}</p>
              <p className="text-sm text-gray-500 mt-4">
                This window will close automatically...
              </p>
            </>
          )}

          {status === "error" && (
            <>
              <div className="flex justify-center mb-4">
                <div className="bg-red-100 rounded-full p-3">
                  <XCircle className="h-12 w-12 text-red-600" />
                </div>
              </div>
              <h1 className="text-2xl font-bold mb-2 text-gray-900">
                Authorization Failed
              </h1>
              <p className="text-gray-600">{message}</p>
              <p className="text-sm text-gray-500 mt-4">
                This window will close automatically...
              </p>
            </>
          )}
        </div>

        <div className="mt-6 text-center">
          <button
            onClick={() => window.close()}
            className="text-sm text-blue-600 hover:text-blue-700 underline"
          >
            Close this window
          </button>
        </div>
      </div>
    </div>
  );
}
