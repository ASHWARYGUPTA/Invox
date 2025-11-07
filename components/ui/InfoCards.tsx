"use client";
import React from "react";

interface CardData {
	title: string;
	subtitle: string;
	description: string;
	highlights: string[];
	image: string;
}

const cardsData: CardData[] = [
	{
		title: "Effortless Import",
		subtitle: "From Anywhere, Instantly",
		description:
			"Import invoices from Gmail, direct uploads, or APIs. Support for scanned PDFs, images, and handwritten documents.",
		highlights: [
			"Gmail integration",
			"Multi-page documents",
			"Handwritten recognition",
		],
		image: "/upload_pic.png",
	},
	{
		title: "AI-Powered",
		subtitle: "90% Accuracy Guaranteed",
		description:
			"Leverage Google Gemini AI to extract invoice data with precision. Automate workflows from import to approval.",
		highlights: [
			"Intelligent extraction",
			"Real-time processing",
			"Custom workflows",
		],
		image: "/dashboard_pic.png",
	},
	{
		title: "Enterprise Security",
		subtitle: "Bank-Level Protection",
		description:
			"Your financial data protected with AES-256 encryption and OAuth 2.0 authentication. SOC 2 & GDPR compliant.",
		highlights: [
			"End-to-end encryption",
			"OAuth 2.0 secure",
			"24/7 support",
		],
		image: "/review_pic.png",
	},
];

const InfoCards: React.FC = () => {
	return (
		<section
			style={{
				display: "flex",
				flexDirection: "column",
				paddingTop: 80,
				paddingBottom: 80,
				minHeight: "100vh",
				gap: "60px",
				minWidth: "1200px",
			}}
		>
			{cardsData.map((card, index) => (
				<div
					key={index}
					style={{
						display: "flex",
						flexDirection: index % 2 === 0 ? "row" : "row-reverse",
						alignItems: "center",
						width: "90%",
						maxWidth: "1600px",
						minHeight: 450,
						margin: "0 auto",
						backgroundColor: "rgba(15, 15, 20, 0.6)",
						borderRadius: 24,
						overflow: "hidden",
						boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
						border: "1px solid rgba(255, 255, 255, 0.05)",
					}}
				>
					{/* Image (left half) */}
					<div
						style={{
							flex: 1,
							display: "flex",
							alignItems: "center",
							justifyContent: "center",
							background:
								"linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
							minHeight: 450,
						}}
					>
						<img
							src={card.image}
							alt={card.title}
							style={{
								width: "auto",
								height: "100%",
								maxHeight: 350,
								objectFit: "contain",
								borderRadius: 16,
								boxShadow: "0 12px 40px rgba(0,0,0,0.3)",
							}}
						/>
					</div>

					{/* Text content (right half) */}
					<div
						style={{
							flex: 1,
							background: "rgba(20, 22, 30, 0.8)",
							color: "#fff",
							padding: "60px 50px",
							display: "flex",
							flexDirection: "column",
							justifyContent: "center",
							minHeight: 450,
						}}
					>
						{/* Subtitle Badge */}
						<div
							style={{
								display: "inline-block",
								alignSelf: "flex-start",
								padding: "6px 16px",
								background:
									"linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2))",
								border: "1px solid rgba(139, 92, 246, 0.3)",
								borderRadius: "20px",
								fontSize: "0.75rem",
								fontWeight: "600",
								letterSpacing: "0.5px",
								textTransform: "uppercase",
								color: "#a78bfa",
								marginBottom: "20px",
							}}
						>
							{card.subtitle}
						</div>

						{/* Title */}
						<h2
							style={{
								fontSize: "3.5rem",
								fontWeight: "800",
								margin: "0 0 24px 0",
								letterSpacing: "-0.03em",
								lineHeight: "1.1",
								background:
									"linear-gradient(135deg, #ffffff 0%, #a78bfa 100%)",
								WebkitBackgroundClip: "text",
								WebkitTextFillColor: "transparent",
								backgroundClip: "text",
							}}
						>
							{card.title}
						</h2>

						{/* Description */}
						<p
							style={{
								lineHeight: 1.8,
								fontSize: "1.15rem",
								margin: "0 0 32px 0",
								color: "#d1d5db",
								fontWeight: "400",
								maxWidth: "500px",
							}}
						>
							{card.description}
						</p>

						{/* Highlights */}
						<div
							style={{
								display: "flex",
								flexDirection: "column",
								gap: "12px",
							}}
						>
							{card.highlights.map((highlight, i) => (
								<div
									key={i}
									style={{
										display: "flex",
										alignItems: "center",
										gap: "12px",
									}}
								>
									<div
										style={{
											width: "6px",
											height: "6px",
											borderRadius: "50%",
											background:
												"linear-gradient(135deg, #8b5cf6, #6366f1)",
											boxShadow:
												"0 0 8px rgba(139, 92, 246, 0.6)",
										}}
									/>
									<span
										style={{
											fontSize: "1rem",
											color: "#e5e7eb",
											fontWeight: "500",
										}}
									>
										{highlight}
									</span>
								</div>
							))}
						</div>
					</div>
				</div>
			))}
		</section>
	);
};

export default InfoCards;
