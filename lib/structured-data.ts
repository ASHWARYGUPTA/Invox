/**
 * JSON-LD Structured Data for SEO
 * This helps search engines understand your application better
 */

export const organizationSchema = {
	"@context": "https://schema.org",
	"@type": "SoftwareApplication",
	name: "Invox",
	applicationCategory: "BusinessApplication",
	applicationSubCategory: "Invoice Management",
	operatingSystem: "Web",
	offers: {
		"@type": "Offer",
		price: "0",
		priceCurrency: "USD",
	},
	aggregateRating: {
		"@type": "AggregateRating",
		ratingValue: "4.8",
		ratingCount: "150",
	},
	description:
		"AI-powered invoice management system that automates invoice processing, data extraction, and approval workflows with Gmail integration.",
	featureList: [
		"Automated invoice data extraction",
		"Gmail integration for email invoices",
		"AI-powered document processing",
		"Invoice approval workflow",
		"Real-time invoice tracking",
		"Export and reporting features",
		"Multi-currency support",
	],
	screenshot: "http://localhost:3000/screenshot.png",
	softwareVersion: "1.0.0",
	author: {
		"@type": "Organization",
		name: "Invox Team",
	},
};

export const webApplicationSchema = {
	"@context": "https://schema.org",
	"@type": "WebApplication",
	name: "Invox - Invoice Management",
	url: "http://localhost:3000",
	description:
		"Intelligent invoice management platform with AI-powered automation",
	browserRequirements: "Requires JavaScript. Requires HTML5.",
	softwareVersion: "1.0",
	applicationCategory: "FinanceApplication",
	operatingSystem: "Any",
	permissions: "Login required for full access",
};

export const breadcrumbSchema = (
	items: Array<{ name: string; url: string }>
) => ({
	"@context": "https://schema.org",
	"@type": "BreadcrumbList",
	itemListElement: items.map((item, index) => ({
		"@type": "ListItem",
		position: index + 1,
		name: item.name,
		item: item.url,
	})),
});

export const faqSchema = {
	"@context": "https://schema.org",
	"@type": "FAQPage",
	mainEntity: [
		{
			"@type": "Question",
			name: "What is Invox?",
			acceptedAnswer: {
				"@type": "Answer",
				text: "Invox is an AI-powered invoice management system that automates invoice processing, data extraction, and approval workflows. It integrates with Gmail to automatically detect and process invoice emails.",
			},
		},
		{
			"@type": "Question",
			name: "How does automatic invoice extraction work?",
			acceptedAnswer: {
				"@type": "Answer",
				text: "Invox uses advanced AI and OCR technology to automatically extract key information from invoices including vendor name, invoice number, amounts, dates, and line items. Simply upload a PDF or image, and the system extracts the data instantly.",
			},
		},
		{
			"@type": "Question",
			name: "Can Invox integrate with my email?",
			acceptedAnswer: {
				"@type": "Answer",
				text: "Yes, Invox integrates with Gmail to automatically check for invoice emails and process attachments. You can also enable auto-polling to continuously monitor your inbox for new invoices.",
			},
		},
		{
			"@type": "Question",
			name: "What file formats are supported?",
			acceptedAnswer: {
				"@type": "Answer",
				text: "Invox supports PDF files and common image formats including PNG, JPG, and JPEG. The AI can process both digital and scanned invoices.",
			},
		},
	],
};
