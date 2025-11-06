"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "@/lib/api/client";
import DashboardContent from "./DashboardContent";

export default function Page() {
	const router = useRouter();
	const [isChecking, setIsChecking] = useState(true);
	const [authenticated, setAuthenticated] = useState(false);

	useEffect(() => {
		// Check authentication on client side only
		const checkAuth = () => {
			const isAuth = isAuthenticated();
			setAuthenticated(isAuth);
			setIsChecking(false);

			if (!isAuth) {
				// Redirect to signin if not authenticated
				router.push("/signin");
			}
		};

		checkAuth();
	}, [router]);

	// Show loading state while checking authentication
	// This prevents hydration mismatch by always rendering the same initial state
	if (isChecking) {
		return (
			<div className="flex items-center justify-center min-h-screen">
				<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
			</div>
		);
	}

	// Don't render dashboard if not authenticated (will redirect)
	if (!authenticated) {
		return (
			<div className="flex items-center justify-center min-h-screen">
				<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
			</div>
		);
	}

	return <DashboardContent />;
}
