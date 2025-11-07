import Link from "next/link";
import { Metadata } from "next";

export const metadata: Metadata = {
	title: "404 - Page Not Found",
	description: "The page you are looking for does not exist.",
};

export default function NotFound() {
	return (
		<div className="flex flex-col items-center justify-center min-h-screen bg-background">
			<div className="text-center space-y-6 p-8">
				<h1 className="text-9xl font-bold text-primary">404</h1>
				<h2 className="text-3xl font-semibold">Page Not Found</h2>
				<p className="text-muted-foreground max-w-md">
					Sorry, we couldn’t find the page you're looking for. The
					page might have been moved or doesn't exist.
				</p>
				<div className="flex gap-4 justify-center mt-8">
					<Link
						href="/"
						className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
					>
						Go Home
					</Link>
					<Link
						href="/dashboard"
						className="px-6 py-3 border border-border rounded-lg hover:bg-accent transition-colors"
					>
						Go to Dashboard
					</Link>
				</div>
			</div>
		</div>
	);
}
