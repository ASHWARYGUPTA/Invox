"use client";
import React from "react";
import Image from "next/image";

const WhoWeAre: React.FC = () => {
	return (
		<section
			style={{
				width: "100vw",
				padding: "80px 40px",
				boxSizing: "border-box",
				backgroundColor: "#0a0e27",
				color: "#fff",
			}}
		>
			<div
				style={{
					maxWidth: "1200px",
					margin: "0 auto",
					display: "grid",
					gridTemplateColumns: "1fr 1fr",
					gap: "60px",
					alignItems: "center",
				}}
			>
				{/* Left Side - Content Card */}
				<div>
					{/* Main Content Card */}
					<div
						style={{
							backgroundColor: "rgba(255, 255, 255, 0.05)",
							border: "1px solid rgba(255, 255, 255, 0.1)",
							borderRadius: "16px",
							overflow: "hidden",
							boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3)",
						}}
					>
						{/* Image and Title Section */}
						<div style={{ padding: "32px" }}>
							<div
								style={{
									display: "flex",
									alignItems: "flex-start",
									gap: "24px",
									marginBottom: "24px",
								}}
							>
								{/* Image */}
								<div
									style={{
										flex: "0 0 240px",
										height: "180px",
										borderRadius: "12px",
										overflow: "hidden",
										backgroundColor: "#1a1f3a",
										position: "relative",
									}}
								>
									<Image
										src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=500&h=400&fit=crop"
										alt="Invoice Management"
										fill
										style={{
											objectFit: "cover",
										}}
									/>
								</div>

								{/* Title and Arrow */}
								<div style={{ flex: 1 }}>
									<div
										style={{
											width: "48px",
											height: "48px",
											backgroundColor:
												"rgba(99, 102, 241, 0.2)",
											borderRadius: "12px",
											display: "flex",
											alignItems: "center",
											justifyContent: "center",
											marginBottom: "16px",
										}}
									>
										<svg
											width="24"
											height="24"
											viewBox="0 0 24 24"
											fill="none"
											stroke="#6366f1"
											strokeWidth="2"
										>
											<path d="M7 17l9.2-9.2M17 17V7H7" />
										</svg>
									</div>
									<h3
										style={{
											fontSize: "1.75rem",
											fontWeight: "700",
											marginBottom: "12px",
											lineHeight: "1.2",
										}}
									>
										Automated Invoice Processing
									</h3>
									<p
										style={{
											color: "#b4b7c9",
											fontSize: "0.95rem",
											lineHeight: "1.6",
										}}
									>
										Transform your invoice workflow with
										AI-powered automation. Process invoices
										10x faster with 99% accuracy.
									</p>
								</div>
							</div>
						</div>
					</div>

					{/* Stats Bar */}
					<div
						style={{
							display: "grid",
							gridTemplateColumns: "repeat(3, 1fr)",
							gap: "16px",
							marginTop: "20px",
						}}
					>
						<div
							style={{
								backgroundColor: "rgba(139, 92, 246, 0.15)",
								padding: "24px",
								borderRadius: "12px",
								textAlign: "center",
								border: "1px solid rgba(139, 92, 246, 0.2)",
							}}
						>
							<div
								style={{
									fontSize: "2.5rem",
									fontWeight: "800",
									color: "#a78bfa",
									marginBottom: "8px",
									lineHeight: "1",
								}}
							>
								5+
							</div>
							<div
								style={{
									fontSize: "0.9rem",
									color: "#b4b7c9",
									fontWeight: "500",
								}}
							>
								Years of Experience
							</div>
						</div>

						<div
							style={{
								backgroundColor: "rgba(139, 92, 246, 0.15)",
								padding: "24px",
								borderRadius: "12px",
								textAlign: "center",
								border: "1px solid rgba(139, 92, 246, 0.2)",
							}}
						>
							<div
								style={{
									fontSize: "2.5rem",
									fontWeight: "800",
									color: "#a78bfa",
									marginBottom: "8px",
									lineHeight: "1",
								}}
							>
								50+
							</div>
							<div
								style={{
									fontSize: "0.9rem",
									color: "#b4b7c9",
									fontWeight: "500",
								}}
							>
								Enterprise Clients
							</div>
						</div>

						<div
							style={{
								backgroundColor: "rgba(139, 92, 246, 0.15)",
								padding: "24px",
								borderRadius: "12px",
								textAlign: "center",
								border: "1px solid rgba(139, 92, 246, 0.2)",
							}}
						>
							<div
								style={{
									fontSize: "2.5rem",
									fontWeight: "800",
									color: "#a78bfa",
									marginBottom: "8px",
									lineHeight: "1",
								}}
							>
								1M+
							</div>
							<div
								style={{
									fontSize: "0.9rem",
									color: "#b4b7c9",
									fontWeight: "500",
								}}
							>
								Invoices Processed
							</div>
						</div>
					</div>
				</div>

				{/* Right Side - Main Content */}
				<div>
					{/* Who We Are Badge */}
					<div style={{ textAlign: "right", marginBottom: "20px" }}>
						<div
							style={{
								display: "inline-block",
								backgroundColor: "rgba(139, 92, 246, 0.15)",
								color: "#a78bfa",
								padding: "8px 20px",
								borderRadius: "24px",
								fontSize: "0.85rem",
								fontWeight: "600",
								letterSpacing: "0.5px",
								border: "1px solid rgba(139, 92, 246, 0.3)",
							}}
						>
							WHO WE ARE
						</div>
					</div>

					{/* Main Heading */}
					<h2
						style={{
							fontSize: "3rem",
							fontWeight: "600",
							lineHeight: "1.1",
							marginBottom: "24px",
							letterSpacing: "-0.02em",
							textAlign: "right",
						}}
					>
						Your Financial Partner For Success
					</h2>

					{/* Quote */}
					<p
						style={{
							fontSize: "1.15rem",
							color: "#b4b7c9",
							lineHeight: "1.7",
							marginBottom: "32px",
							fontStyle: "italic",
							textAlign: "right",
						}}
					>
						Automation is the eighth wonder of the world. Those who
						understand it, thrive with it. Those who don’t, struggle
						without it.
					</p>

					{/* Feature Card */}
					<div
						style={{
							backgroundColor: "rgba(255, 255, 255, 0.03)",
							border: "1px solid rgba(255, 255, 255, 0.1)",
							borderRadius: "16px",
							padding: "32px",
							marginBottom: "24px",
						}}
					>
						<div
							style={{
								display: "flex",
								alignItems: "center",
								gap: "16px",
							}}
						>
							<div>
								<h3
									style={{
										fontSize: "1.5rem",
										fontWeight: "700",
										marginBottom: "8px",
									}}
								>
									Smart & Efficient
								</h3>
								<p
									style={{
										color: "#b4b7c9",
										fontSize: "0.95rem",
									}}
								>
									The biggest risk of all is not taking one.
									Automate your invoice processing today.
								</p>
							</div>

							<div
								style={{
									width: "56px",
									height: "56px",
									backgroundColor: "rgba(99, 102, 241, 0.15)",
									borderRadius: "12px",
									display: "flex",
									alignItems: "center",
									justifyContent: "center",
								}}
							>
								<svg
									width="28"
									height="28"
									viewBox="0 0 24 24"
									fill="none"
									stroke="#6366f1"
									strokeWidth="2"
								>
									<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
									<polyline points="14 2 14 8 20 8" />
									<line x1="16" y1="13" x2="8" y2="13" />
									<line x1="16" y1="17" x2="8" y2="17" />
									<polyline points="10 9 9 9 8 9" />
								</svg>
							</div>
						</div>
					</div>

					{/* CTA Button */}
					<div style={{ textAlign: "right" }}>
						<button
							style={{
								backgroundColor: "#6366f1",
								color: "#fff",
								padding: "12px 40px",
								fontSize: "1rem",
								fontWeight: "600",
								borderRadius: "12px",
								border: "none",
								cursor: "pointer",
								transition: "all 0.3s ease",
								boxShadow: "0 4px 20px rgba(99, 102, 241, 0.4)",
							}}
							onClick={() => {
								const nextSection = document.querySelector(
									'section[id="features"], section[id="how-it-works"]'
								);
								if (nextSection) {
									nextSection.scrollIntoView({
										behavior: "smooth",
										block: "start",
									});
								} else {
									window.scrollBy({
										top: window.innerHeight,
										behavior: "smooth",
									});
								}
							}}
							onMouseEnter={(e) => {
								e.currentTarget.style.backgroundColor =
									"#4f46e5";
								e.currentTarget.style.transform =
									"translateY(-2px)";
								e.currentTarget.style.boxShadow =
									"0 6px 24px rgba(99, 102, 241, 0.5)";
							}}
							onMouseLeave={(e) => {
								e.currentTarget.style.backgroundColor =
									"#6366f1";
								e.currentTarget.style.transform =
									"translateY(0)";
								e.currentTarget.style.boxShadow =
									"0 4px 20px rgba(99, 102, 241, 0.4)";
							}}
						>
							Learn More
						</button>
					</div>
				</div>
			</div>
		</section>
	);
};

export default WhoWeAre;
