import { getSession } from "next-auth/react";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8001";

interface RequestOptions extends RequestInit {
  authenticated?: boolean;
}

/**
 * Make an authenticated API call to the FastAPI backend
 */
export async function backendFetch<T = any>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { authenticated = true, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(fetchOptions.headers as Record<string, string>),
  };

  // Add authentication token if required
  if (authenticated) {
    const session = await getSession();
    if (session?.backendToken) {
      headers["Authorization"] = `Bearer ${session.backendToken}`;
    }
  }

  const url = `${BACKEND_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Backend API error: ${response.status} ${response.statusText} - ${errorText}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error(`Error calling backend API ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Get current user from backend
 */
export async function getCurrentUser() {
  return backendFetch("/api/v1/users/me");
}

/**
 * Update current user profile
 */
export async function updateUserProfile(data: {
  name?: string;
  email?: string;
  image?: string;
}) {
  return backendFetch("/api/v1/users/me", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * Get user by ID
 */
export async function getUserById(userId: string) {
  return backendFetch(`/api/v1/users/${userId}`);
}

/**
 * Check if email exists in database
 */
export async function verifyEmail(email: string) {
  return backendFetch("/api/v1/auth/verify-email", {
    method: "POST",
    authenticated: false,
    body: JSON.stringify({ email }),
  });
}
