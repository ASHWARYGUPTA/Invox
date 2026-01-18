"use client";

import { signIn, useSession } from "next-auth/react";
import { useState } from "react";

export default function TestAuth() {
  const { data: session, status } = useSession();
  const [error, setError] = useState<string | null>(null);

  const handleSignIn = async () => {
    try {
      console.log("🔵 Attempting to sign in with Google...");
      setError(null);

      const result = await signIn("google", {
        callbackUrl: "/dashboard",
        redirect: true,
      });

      console.log("🔵 SignIn result:", result);

      if (result?.error) {
        console.error("🔴 SignIn error:", result.error);
        setError(result.error);
      }
    } catch (err) {
      console.error("🔴 Exception during sign in:", err);
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full space-y-6">
        <h1 className="text-2xl font-bold text-center">Auth Test Page</h1>

        <div className="space-y-4">
          <div className="p-4 bg-gray-50 rounded">
            <p className="font-semibold">Session Status:</p>
            <p className="text-sm">{status}</p>
          </div>

          {session && (
            <div className="p-4 bg-green-50 rounded">
              <p className="font-semibold text-green-800">Logged In As:</p>
              <p className="text-sm">{session.user?.email}</p>
              <p className="text-sm">{session.user?.name}</p>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 rounded border border-red-200">
              <p className="font-semibold text-red-800">Error:</p>
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <button
            onClick={handleSignIn}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            Test Google Sign In
          </button>

          <div className="text-xs text-gray-500 space-y-1">
            <p>
              <strong>GOOGLE_CLIENT_ID:</strong>{" "}
              {process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID
                ? "✅ Set"
                : "❌ Missing"}
            </p>
            <p>
              <strong>NEXTAUTH_URL:</strong>{" "}
              {process.env.NEXTAUTH_URL || "❌ Missing"}
            </p>
            <p>
              <strong>BACKEND_URL:</strong>{" "}
              {process.env.NEXT_PUBLIC_BACKEND_URL || "❌ Missing"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
