"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { tokenManager, authApi } from "@/lib/api/client";

export default function AuthCallback() {
	const router = useRouter();
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		const handleAuth = async () => {
			// Extract token from URL hash (#token=xxx)
			const hash = window.location.hash;

			if (hash) {
				const params = new URLSearchParams(hash.substring(1));
				const token = params.get("token");

				if (token) {
					// Store the token
					tokenManager.setToken(token);

					try {
						// Fetch user information
						const userData = await authApi.getCurrentUser();

						// Store user data
						tokenManager.setUser(userData);

						// Redirect to dashboard
						router.push("/dashboard");
					} catch (err) {
						console.error("Error fetching user data:", err);
						setTimeout(
							() => setError("Failed to fetch user information"),
							0
						);
					}
				} else {
					// Use setTimeout to avoid setState during render
					setTimeout(
						() => setError("No authentication token received"),
						0
					);
				}
			} else {
				setTimeout(() => setError("Authentication failed"), 0);
			}
		};

		handleAuth();
	}, [router]);

	if (error) {
		return (
			<div className="flex items-center justify-center min-h-screen bg-background">
				<div className="text-center">
					<h1 className="text-2xl font-bold text-red-500 mb-4">
						Authentication Error
					</h1>
					<p className="text-muted-foreground mb-4">{error}</p>
					<button
						onClick={() => router.push("/signin")}
						className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 cursor-pointer transition-all duration-200 hover:shadow-md active:scale-95"
					>
						Try Again
					</button>
				</div>
			</div>
		);
	}

	return (
		<div className="flex items-center justify-center min-h-screen bg-background">
			<div className="text-center">
				<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
				<p className="text-lg text-muted-foreground">
					Completing authentication...
				</p>
			</div>
		</div>
	);
}
