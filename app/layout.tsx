import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ThemeProvider } from "@/components/theme-provider";
import AuthProvider from "@/providers/auth-provider";
import "./globals.css";

const inter = Inter({
	subsets: ["latin"],
	display: "swap",
	variable: "--font-inter",
});

export const metadata: Metadata = {
	title: {
		default: "Invox - AI-Powered Invoice Management System",
		template: "%s | Invox",
	},
	description:
		"Invox is an intelligent invoice management platform that automates invoice processing with AI. Upload invoices, extract data automatically, manage approvals, and streamline your accounts payable workflow with Gmail integration and smart automation.",
	keywords: [
		"invoice management",
		"invoice automation",
		"AI invoice processing",
		"automated invoice extraction",
		"invoice OCR",
		"accounts payable",
		"invoice tracking",
		"Gmail invoice integration",
		"invoice approval workflow",
		"expense management",
		"invoice parser",
		"document processing",
		"financial automation",
		"invoice software",
		"business automation",
		"invoice dashboard",
		"AI document extraction",
		"invoice verification",
		"automated bookkeeping",
		"invoice analytics",
	],
	authors: [{ name: "Invox Team" }],
	creator: "Invox",
	publisher: "Invox",
	formatDetection: {
		email: false,
		address: false,
		telephone: false,
	},
	icons: {
		icon: "/logo.png",
		shortcut: "/logo.png",
		apple: "/logo.png",
	},
	metadataBase: new URL("http://localhost:3000"),
	alternates: {
		canonical: "/",
	},
	openGraph: {
		type: "website",
		locale: "en_US",
		url: "http://localhost:3000",
		title: "Invox - AI-Powered Invoice Management System",
		description:
			"Automate your invoice processing with AI. Extract data from invoices, manage approvals, and integrate with Gmail for seamless accounts payable workflow.",
		siteName: "Invox",
		images: [
			{
				url: "/og-image.png",
				width: 1200,
				height: 630,
				alt: "Invox - Invoice Management Platform",
			},
		],
	},
	twitter: {
		card: "summary_large_image",
		title: "Invox - AI-Powered Invoice Management System",
		description:
			"Automate your invoice processing with AI. Extract data, manage approvals, and streamline accounts payable.",
		images: ["/twitter-image.png"],
		creator: "@invox",
	},
	robots: {
		index: true,
		follow: true,
		googleBot: {
			index: true,
			follow: true,
			"max-video-preview": -1,
			"max-image-preview": "large",
			"max-snippet": -1,
		},
	},
	category: "Business Software",
	classification:
		"Invoice Management, Financial Software, Business Automation",
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en" suppressHydrationWarning>
			<body className={inter.variable} suppressHydrationWarning>
				<AuthProvider>
					<ThemeProvider
						attribute="class"
						defaultTheme="light"
						enableSystem
						disableTransitionOnChange
					>
						{children}
					</ThemeProvider>
				</AuthProvider>
			</body>
		</html>
	);
}
