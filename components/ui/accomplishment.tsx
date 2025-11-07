"use client";
import React from "react";

const stats = [
	{
		id: 1,
		title: "$100M+",
		description: "Saved in processing costs annually",
		bgColor: "#d6f1c5", // light green
		icon: (
			<svg
				fill="none"
				width="40"
				height="40"
				viewBox="0 0 24 24"
				stroke="#a4c36d"
				strokeWidth={2}
			>
				<circle cx="12" cy="12" r="10" stroke="none" fill="#a4c36d" />
				<path
					d="M12 7v10M9 10h6a2 2 0 010 4H9"
					stroke="#fff"
					strokeWidth={2}
				/>
			</svg>
		),
	},
	{
		id: 2,
		title: "3.4M+",
		description: "Work hours saved",
		bgColor: "#edd7de", // light pink
		icon: (
			<svg
				width="24"
				height="24"
				fill="none"
				stroke="#bd8791"
				strokeWidth={2}
				viewBox="0 0 24 24"
			>
				<circle cx="12" cy="12" r="10" fill="#bd8791" />
				<path d="M12 6v6l4 2" stroke="#fff" strokeWidth={2} />
			</svg>
		),
	},
	{
		id: 3,
		title: "20M+",
		description: "Invoices processed",
		bgColor: "#f7e8d1", // light orange
		icon: (
			<svg
				width="24"
				height="24"
				fill="none"
				stroke="#d9b99d"
				strokeWidth={2}
				viewBox="0 0 24 24"
			>
				<rect width="24" height="24" rx="4" ry="4" fill="#d9b99d" />
				<path d="M9 12l2 2 4-4" stroke="#fff" strokeWidth={2} />
			</svg>
		),
	},
	{
		id: 4,
		title: "99%",
		description: "Accuracy in data extraction",
		bgColor: "#d9e8ed", // light blue
		icon: (
			<svg
				width="40"
				height="40"
				fill="none"
				stroke="#8dbbca"
				strokeWidth={2}
				viewBox="0 0 24 24"
			>
				<path
					d="M4 20h16M12 14l4-4 4 4"
					stroke="#6698ab"
					strokeWidth={2}
					fill="none"
				/>
			</svg>
		),
	},
];

const StatsDarkSection: React.FC = () => {
	return (
		<section
			style={{
				paddingTop: "4rem",
				paddingBottom: "4rem",
				backgroundColor: "#000000",
				width: "100vw",
				padding: "4rem 2rem",
				boxSizing: "border-box",
				maxWidth: "100%",
			}}
		>
			<div style={{ maxWidth: "1100px", margin: "0 auto" }}>
				<h2
					style={{
						color: "#fdfcfb",
						textAlign: "center",
						fontSize: "2.5rem",
						fontWeight: "700",
						marginBottom: "0.75rem",
						letterSpacing: "-0.02em",
						lineHeight: "1.2",
					}}
				>
					Transforming Invoice Management
				</h2>
				<p
					style={{
						color: "#a0a0a0",
						textAlign: "center",
						fontSize: "1.125rem",
						fontWeight: "400",
						marginBottom: "3rem",
						maxWidth: "600px",
						margin: "0 auto 3rem",
						lineHeight: "1.6",
					}}
				>
					Trusted by businesses worldwide to automate and streamline
					their invoice processing workflows
				</p>
				<div
					style={{
						display: "grid",
						gridTemplateColumns: "repeat(3, 1fr)",
						gridTemplateRows: "repeat(2, 130px)",
						gap: "1rem",
						maxWidth: "1100px",
						margin: "0 auto",
						gridTemplateAreas: `
            "big-block small-block-1 small-block-2"
            "big-block small-block-3 small-block-3"
          `,
					}}
				>
					<div
						style={{
							gridArea: "big-block",
							backgroundColor: stats[0].bgColor,
							borderRadius: "12px",
							padding: "2rem",
							display: "flex",
							flexDirection: "column",
							justifyContent: "center",
							position: "relative",
							boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
						}}
					>
						<div
							style={{
								position: "absolute",
								right: "1.5rem",
								top: "1.5rem",
								opacity: 0.15,
							}}
						>
							{stats[0].icon}
						</div>
						<h3
							style={{
								margin: 0,
								fontSize: "2.75rem",
								fontWeight: 800,
								color: "#1a5d1a",
								letterSpacing: "-0.02em",
								lineHeight: "1",
							}}
						>
							{stats[0].title}
						</h3>
						<p
							style={{
								margin: "0.5rem 0 0 0",
								color: "#2d5a2d",
								fontSize: "1.05rem",
								fontWeight: 500,
								lineHeight: "1.4",
							}}
						>
							{stats[0].description}
						</p>
					</div>

					<div
						style={{
							gridArea: "small-block-1",
							backgroundColor: stats[1].bgColor,
							borderRadius: "12px",
							padding: "1.25rem 1.5rem",
							display: "flex",
							alignItems: "center",
							gap: "0.5rem",
							color: "#2b1b20",
							fontWeight: "700",
							fontSize: "1.65rem",
							position: "relative",
							boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
						}}
					>
						<div
							style={{
								backgroundColor: "#fff1f3",
								width: "36px",
								height: "36px",
								borderRadius: "8px",
								display: "flex",
								justifyContent: "center",
								alignItems: "center",
								position: "absolute",
								left: "1.25rem",
								top: "1.25rem",
								boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
							}}
						>
							{stats[1].icon}
						</div>
						<div style={{ marginLeft: "3.5rem" }}>
							<div
								style={{
									fontWeight: "800",
									fontSize: "1.65rem",
									color: "#4a2b35",
									letterSpacing: "-0.01em",
								}}
							>
								{stats[1].title}
							</div>
							<div
								style={{
									fontWeight: "500",
									fontSize: "0.95rem",
									marginTop: "0.15rem",
									color: "#5a3b45",
								}}
							>
								{stats[1].description}
							</div>
						</div>
					</div>

					<div
						style={{
							gridArea: "small-block-2",
							backgroundColor: stats[2].bgColor,
							borderRadius: "12px",
							padding: "1.25rem 1.5rem",
							display: "flex",
							alignItems: "center",
							gap: "0.5rem",
							color: "#382f22",
							fontWeight: "700",
							fontSize: "1.65rem",
							position: "relative",
							boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
						}}
					>
						<div
							style={{
								backgroundColor: "#fff7e8",
								width: "36px",
								height: "36px",
								borderRadius: "8px",
								display: "flex",
								justifyContent: "center",
								alignItems: "center",
								position: "absolute",
								left: "1.25rem",
								top: "1.25rem",
								boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
							}}
						>
							{stats[2].icon}
						</div>
						<div style={{ marginLeft: "3.5rem" }}>
							<div
								style={{
									fontWeight: "800",
									fontSize: "1.65rem",
									color: "#4a3d28",
									letterSpacing: "-0.01em",
								}}
							>
								{stats[2].title}
							</div>
							<div
								style={{
									fontWeight: "500",
									fontSize: "0.95rem",
									marginTop: "0.15rem",
									color: "#5a4d38",
								}}
							>
								{stats[2].description}
							</div>
						</div>
					</div>

					<div
						style={{
							gridArea: "small-block-3",
							backgroundColor: stats[3].bgColor,
							borderRadius: "12px",
							padding: "1.75rem",
							color: "#1f2f3a",
							fontWeight: "700",
							fontSize: "1.65rem",
							display: "flex",
							flexDirection: "column",
							justifyContent: "center",
							position: "relative",
							overflow: "hidden",
							boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
						}}
					>
						<div
							style={{
								position: "absolute",
								right: "0",
								bottom: "0",
								opacity: 0.15,
								width: "100%",
								height: "100%",
								pointerEvents: "none",
							}}
						>
							{stats[3].icon}
						</div>
						<div
							style={{
								fontWeight: "800",
								fontSize: "2.25rem",
								color: "#2a4454",
								letterSpacing: "-0.02em",
								lineHeight: "1",
							}}
						>
							{stats[3].title}
						</div>
						<div
							style={{
								fontWeight: "500",
								fontSize: "1rem",
								marginTop: "0.5rem",
								color: "#3a5464",
								lineHeight: "1.3",
							}}
						>
							{stats[3].description}
						</div>
					</div>
				</div>
			</div>
		</section>
	);
};

export default StatsDarkSection;
