"use client";
import AnimatedList from "./AnimatedList";
import { invoiceApi } from "@/lib/api/client";
import { useEffect, useState, useRef, useCallback } from "react";
import { Button } from "./ui/button";
import { InvoiceEditDialog } from "./InvoiceEditDialog";
import { RefreshCw, Pause, Play, Mail } from "lucide-react";

interface Invoice {
	id: number;
	file_name: string;
	invoice_id: string | null;
	vendor_name: string | null;
	amount_due: number | null;
	due_date: string | null;
	invoice_date: string | null;
	currency_code: string | null;
	confidence_score: number | null;
	status: string;
	created_at: string;
	updated_at: string;
	owner_id: number;
}

export default function AnimatedListItemUse() {
	const [items, setItems] = useState<Invoice[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(
		null
	);
	const [dialogOpen, setDialogOpen] = useState(false);
	const [isAutoRefresh, setIsAutoRefresh] = useState(false);
	const [isPolling, setIsPolling] = useState(false);
	const [lastPollTime, setLastPollTime] = useState<Date | null>(null);
	const intervalRef = useRef<NodeJS.Timeout | null>(null);

	const fetchInvoices = async () => {
		try {
			setLoading(true);
			setError(null);
			const data = await invoiceApi.getMyInvoices();
			console.log("Fetched invoices:", data);
			setItems(data);
		} catch (error) {
			console.error("Error fetching invoices:", error);
			const errorMessage =
				error instanceof Error
					? error.message
					: "Failed to fetch invoices";
			setError(errorMessage);
		} finally {
			setLoading(false);
		}
	};

	const handleManualRefresh = async () => {
		await fetchInvoices();
	};

	const handlePollEmails = useCallback(async () => {
		try {
			setIsPolling(true);
			const result = await invoiceApi.pollEmails();
			console.log("Email polling result:", result);
			setLastPollTime(new Date());

			// Refresh the invoice list to show new invoices
			const data = await invoiceApi.getMyInvoices();
			setItems(data);

			// Show a notification about the result
			if (result.invoices_count > 0) {
				alert(
					`✅ ${result.invoices_count} new invoice(s) found and added!`
				);
			} else {
				alert("📧 No new invoices found in emails.");
			}
		} catch (error) {
			console.error("Error polling emails:", error);
			alert("❌ Failed to poll emails. Please try again.");
		} finally {
			setIsPolling(false);
		}
	}, []);

	const toggleAutoRefresh = () => {
		setIsAutoRefresh(!isAutoRefresh);
	};

	// Auto-refresh effect
	useEffect(() => {
		const pollAndRefresh = async () => {
			await handlePollEmails();
		};

		if (isAutoRefresh) {
			// Poll immediately when enabled
			pollAndRefresh();

			// Set up interval to poll every 30 seconds
			intervalRef.current = setInterval(() => {
				pollAndRefresh();
			}, 30000); // 30 seconds
		} else {
			// Clear interval when disabled
			if (intervalRef.current) {
				clearInterval(intervalRef.current);
				intervalRef.current = null;
			}
		}

		// Cleanup on unmount
		return () => {
			if (intervalRef.current) {
				clearInterval(intervalRef.current);
			}
		};
	}, [isAutoRefresh, handlePollEmails]);

	useEffect(() => {
		fetchInvoices();
	}, []);

	const handleOpenDialog = (invoice: Invoice) => {
		setSelectedInvoice(invoice);
		setDialogOpen(true);
	};

	if (loading) {
		return (
			<div className="flex items-center justify-center p-8">
				<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
				<span className="ml-3">Loading invoices...</span>
			</div>
		);
	}

	if (error) {
		return (
			<div className="p-8 text-center">
				<p className="text-red-500 mb-4">{error}</p>
				<Button onClick={fetchInvoices}>Retry</Button>
			</div>
		);
	}

	if (items.length === 0) {
		return (
			<div className="p-8 text-center text-muted-foreground">
				No invoices found. Upload your first invoice to get started!
			</div>
		);
	}

	// Transform backend data to match the AnimatedList component format
	const transformedItems = items.map((item) => ({
		invoiceNumber: item.invoice_id || "N/A",
		invoiceDate: item.invoice_date || "N/A",
		dueDate: item.due_date || "N/A",
		amountPayable: item.amount_due?.toString() || "N/A",
		currency: item.currency_code || "USD",
		vendorName: item.vendor_name || "N/A",
		customerName: "N/A", // Backend doesn't have customer name
		ConfidenceScore: item.confidence_score
			? `${(item.confidence_score * 100).toFixed(0)}%`
			: "N/A",
		status: item.status,
		actions: (
			<Button
				onClick={(e) => {
					e.stopPropagation();
					handleOpenDialog(item);
				}}
				variant={item.status === "approved" ? "secondary" : "default"}
				size="sm"
			>
				{item.status === "approved" ? "View" : "Review"}
			</Button>
		),
	}));

	return (
		<div className="w-full">
			{/* Control Panel */}
			<div className="mb-4 flex items-center gap-3 p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
				<Button
					onClick={handleManualRefresh}
					disabled={loading}
					variant="outline"
					size="sm"
					className="flex items-center gap-2"
				>
					<RefreshCw
						className={`w-4 h-4 ${loading ? "animate-spin" : ""}`}
					/>
					Refresh
				</Button>

				<Button
					onClick={handlePollEmails}
					disabled={isPolling || loading}
					variant="outline"
					size="sm"
					className="flex items-center gap-2"
				>
					<Mail
						className={`w-4 h-4 ${
							isPolling ? "animate-pulse" : ""
						}`}
					/>
					{isPolling ? "Checking Emails..." : "Check Emails"}
				</Button>

				<Button
					onClick={toggleAutoRefresh}
					variant={isAutoRefresh ? "default" : "outline"}
					size="sm"
					className="flex items-center gap-2"
				>
					{isAutoRefresh ? (
						<>
							<Pause className="w-4 h-4" />
							Pause Auto-Poll
						</>
					) : (
						<>
							<Play className="w-4 h-4" />
							Start Auto-Poll (30s)
						</>
					)}
				</Button>

				{lastPollTime && (
					<span className="text-xs text-gray-500 ml-auto">
						Last checked: {lastPollTime.toLocaleTimeString()}
					</span>
				)}
			</div>

			<AnimatedList
				items={transformedItems}
				onItemSelect={(item, index) =>
					console.log("Selected:", item, index)
				}
				showGradients={false}
				enableArrowNavigation={true}
				displayScrollbar={true}
			/>

			{/* Invoice Edit/Review Dialog */}
			{selectedInvoice && (
				<InvoiceEditDialog
					invoice={selectedInvoice}
					open={dialogOpen}
					onOpenChange={setDialogOpen}
					onSuccess={fetchInvoices}
				/>
			)}
		</div>
	);
}
