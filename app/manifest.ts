import { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
	return {
		name: "Invox - Invoice Management System",
		short_name: "Invox",
		description: "AI-powered invoice management and automation platform",
		start_url: "/",
		display: "standalone",
		background_color: "#ffffff",
		theme_color: "#000000",
		orientation: "portrait-primary",
		icons: [
			{
				src: "/icon-192.png",
				sizes: "192x192",
				type: "image/png",
				purpose: "maskable",
			},
			{
				src: "/icon-512.png",
				sizes: "512x512",
				type: "image/png",
				purpose: "any",
			},
		],
		categories: ["business", "finance", "productivity"],
		shortcuts: [
			{
				name: "Upload Invoice",
				short_name: "Upload",
				description: "Upload a new invoice",
				url: "/dashboard?action=upload",
				icons: [{ src: "/icon-upload.png", sizes: "96x96" }],
			},
			{
				name: "Check Emails",
				short_name: "Check",
				description: "Check emails for new invoices",
				url: "/dashboard?action=check-emails",
				icons: [{ src: "/icon-email.png", sizes: "96x96" }],
			},
		],
	};
}
