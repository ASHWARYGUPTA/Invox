import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function DocumentationPage() {
	return (
		<div className="min-h-screen bg-gradient-to-b from-[#001133] to-black">
			{/* Header */}
			<div className="border-b border-white/10 bg-background/10 backdrop-blur-xl">
				<div className="max-w-7xl mx-auto px-6 py-6 flex justify-between items-center">
					<Link href="/" className="text-3xl font-bold">
						Invox
					</Link>
					<Button asChild variant="outline">
						<Link href="/dashboard">Go to Dashboard</Link>
					</Button>
				</div>
			</div>

			{/* Content */}
			<div className="max-w-5xl mx-auto px-6 py-16">
				<h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
					Documentation
				</h1>
				<p className="text-xl text-foreground/70 mb-12">
					Complete guide to using Invox for automated invoice
					management
				</p>

				{/* Quick Start */}
				<section className="mb-16">
					<h2 className="text-4xl font-bold mb-6">Quick Start</h2>
					<div className="bg-background/10 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
						<ol className="space-y-6">
							<li className="flex gap-4">
								<span className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center font-bold">
									1
								</span>
								<div>
									<h3 className="text-xl font-semibold mb-2">
										Sign Up
									</h3>
									<p className="text-foreground/70">
										Create an account using your Google
										account. This will also set up the Gmail
										integration.
									</p>
								</div>
							</li>
							<li className="flex gap-4">
								<span className="flex-shrink-0 w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center font-bold">
									2
								</span>
								<div>
									<h3 className="text-xl font-semibold mb-2">
										Connect Gmail
									</h3>
									<p className="text-foreground/70">
										In the dashboard, click &quot;Check Email&quot; to
										authorize Invox to access your Gmail
										inbox for invoice emails.
									</p>
								</div>
							</li>
							<li className="flex gap-4">
								<span className="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center font-bold">
									3
								</span>
								<div>
									<h3 className="text-xl font-semibold mb-2">
										Upload or Auto-Fetch
									</h3>
									<p className="text-foreground/70">
										Upload invoices manually or click &quot;Check
										Email&quot; to automatically fetch invoices
										from your inbox.
									</p>
								</div>
							</li>
						</ol>
					</div>
				</section>

				{/* Features */}
				<section className="mb-16">
					<h2 className="text-4xl font-bold mb-6">Features</h2>
					<div className="grid md:grid-cols-2 gap-6">
						<div className="bg-background/10 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
							<h3 className="text-2xl font-semibold mb-3">
								AI-Powered Extraction
							</h3>
							<p className="text-foreground/70 mb-4">
								Uses Google Gemini AI to extract invoice data
								including:
							</p>
							<ul className="list-disc list-inside text-foreground/70 space-y-1">
								<li>Invoice number</li>
								<li>Vendor name</li>
								<li>Total amount and currency</li>
								<li>Invoice date and due date</li>
								<li>Line items and descriptions</li>
							</ul>
						</div>
						<div className="bg-background/10 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
							<h3 className="text-2xl font-semibold mb-3">
								Gmail Integration
							</h3>
							<p className="text-foreground/70 mb-4">
								Seamlessly integrates with Gmail to:
							</p>
							<ul className="list-disc list-inside text-foreground/70 space-y-1">
								<li>Automatically monitor your inbox</li>
								<li>Fetch invoice emails and attachments</li>
								<li>Process PDFs and images</li>
								<li>Secure OAuth 2.0 authentication</li>
							</ul>
						</div>
						<div className="bg-background/10 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
							<h3 className="text-2xl font-semibold mb-3">
								Smart Dashboard
							</h3>
							<p className="text-foreground/70 mb-4">
								Manage all your invoices in one place:
							</p>
							<ul className="list-disc list-inside text-foreground/70 space-y-1">
								<li>
									View total, approved, and pending invoices
								</li>
								<li>Filter and search invoices</li>
								<li>Review and edit extracted data</li>
								<li>Export to Excel/CSV</li>
							</ul>
						</div>
						<div className="bg-background/10 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
							<h3 className="text-2xl font-semibold mb-3">
								Manual Upload
							</h3>
							<p className="text-foreground/70 mb-4">
								Upload invoices directly:
							</p>
							<ul className="list-disc list-inside text-foreground/70 space-y-1">
								<li>Drag and drop PDF files</li>
								<li>Support for multiple file formats</li>
								<li>Batch upload multiple invoices</li>
								<li>Instant AI processing</li>
							</ul>
						</div>
					</div>
				</section>

				{/* API Reference */}
				<section className="mb-16">
					<h2 className="text-4xl font-bold mb-6">API Reference</h2>
					<div className="bg-background/10 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
						<h3 className="text-2xl font-semibold mb-4">
							Backend API
						</h3>
						<p className="text-foreground/70 mb-6">
							The Invox backend provides a RESTful API for invoice
							management:
						</p>
						<div className="space-y-4">
							<div className="bg-black/30 rounded-lg p-4">
								<code className="text-green-400">
									POST /api/invoices/upload
								</code>
								<p className="text-foreground/70 mt-2">
									Upload and process invoice files
								</p>
							</div>
							<div className="bg-black/30 rounded-lg p-4">
								<code className="text-green-400">
									GET /api/invoices/my-invoices
								</code>
								<p className="text-foreground/70 mt-2">
									Get all invoices for current user
								</p>
							</div>
							<div className="bg-black/30 rounded-lg p-4">
								<code className="text-green-400">
									PUT /api/invoices/{"{id}"}
								</code>
								<p className="text-foreground/70 mt-2">
									Update invoice data
								</p>
							</div>
							<div className="bg-black/30 rounded-lg p-4">
								<code className="text-green-400">
									POST /api/invoices/check-email
								</code>
								<p className="text-foreground/70 mt-2">
									Fetch invoices from Gmail
								</p>
							</div>
						</div>
					</div>
				</section>

				{/* FAQ */}
				<section className="mb-16">
					<h2 className="text-4xl font-bold mb-6">
						Frequently Asked Questions
					</h2>
					<div className="space-y-4">
						<div className="bg-background/10 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
							<h3 className="text-xl font-semibold mb-2">
								How accurate is the AI extraction?
							</h3>
							<p className="text-foreground/70">
								Our AI achieves 99% accuracy on standard
								invoices. You can always review and edit
								extracted data before approving.
							</p>
						</div>
						<div className="bg-background/10 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
							<h3 className="text-xl font-semibold mb-2">
								Is my Gmail data secure?
							</h3>
							<p className="text-foreground/70">
								Yes! We use OAuth 2.0 authentication and only
								access invoice-related emails. We never store
								your Gmail password.
							</p>
						</div>
						<div className="bg-background/10 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
							<h3 className="text-xl font-semibold mb-2">
								What file formats are supported?
							</h3>
							<p className="text-foreground/70">
								We support PDF files and common image formats
								(JPG, PNG). The AI can extract data from both
								typed and scanned invoices.
							</p>
						</div>
						<div className="bg-background/10 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
							<h3 className="text-xl font-semibold mb-2">
								Can I export my invoice data?
							</h3>
							<p className="text-foreground/70">
								Yes! You can export all your invoices to Excel
								or CSV format for further analysis or
								integration with other tools.
							</p>
						</div>
					</div>
				</section>

				{/* Get Started CTA */}
				<section className="text-center py-12">
					<h2 className="text-4xl font-bold mb-4">
						Ready to get started?
					</h2>
					<p className="text-foreground/70 mb-8">
						Start automating your invoice management today
					</p>
					<div className="flex gap-4 justify-center">
						<Button asChild size="lg">
							<Link href="/signup">Sign Up Free</Link>
						</Button>
						<Button asChild size="lg" variant="outline">
							<Link href="/dashboard">View Demo</Link>
						</Button>
					</div>
				</section>
			</div>
		</div>
	);
}
