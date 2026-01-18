"use client";

import React from "react";
import TiltedCard from "../TiltedCard";

interface CardData {
  imageSrc: string;
  altText: string;
  captionText: string;
  name: string;
  role: string;
  linkedin: string;
}

const cardsData: CardData[] = [
  {
    imageSrc: "/abhinav.png",
    altText: "Team Member 1",
    captionText: "Lead Developer",
    name: "Abhinav Mishra",
    role: "Full Stack Developer",
    linkedin: "https://www.linkedin.com/in/dev-abhinav-mishra",
  },
  {
    imageSrc: "/ashwary.jpg",
    altText: "Team Member 2",
    captionText: "AI Engineer",
    name: "Ashwary Gupta",
    role: "Full Stack Developer",
    linkedin: "https://www.linkedin.com/in/ashwarygupta",
  },
  {
    imageSrc: "/sujal.jpg",
    altText: "Team Member 3",
    captionText: "UI/UX Designer",
    name: "Sujal Ahar",
    role: "Backend Developer",
    linkedin: "https://www.linkedin.com/in/sujal-ahar-0418bb2a8/",
  },
  {
    imageSrc: "/shivang.jpg",
    altText: "Team Member 4",
    captionText: "Backend Architect",
    name: "Shivang Baranwal",
    role: "Frontend Developer",
    linkedin:
      "https://www.linkedin.com/in/shivangbarnwal?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app",
  },
];

const CardSection: React.FC = () => {
  return (
    <>
      <style jsx>{`
        @media (max-width: 768px) {
          .team-section {
            padding: 50px 20px !important;
          }

          .team-heading {
            font-size: 2rem !important;
          }

          .team-description {
            font-size: 1rem !important;
            margin-bottom: 40px !important;
          }

          .team-cards-container > div {
            width: 220px !important;
          }
        }

        @media (max-width: 480px) {
          .team-section {
            padding: 40px 15px !important;
          }

          .team-heading {
            font-size: 1.75rem !important;
          }

          .team-description {
            font-size: 0.95rem !important;
          }

          .team-cards-container {
            gap: 24px !important;
          }

          .team-cards-container > div {
            width: 200px !important;
          }
        }
      `}</style>
      <section
        className="team-section"
        style={{
          width: "100vw",
          padding: "80px 40px",
          boxSizing: "border-box",
          backgroundColor: "#000",
        }}
      >
        <div style={{ maxWidth: "1400px", margin: "0 auto" }}>
          <h2
            className="team-heading"
            style={{
              color: "#fff",
              textAlign: "center",
              fontSize: "2.75rem",
              fontWeight: "700",
              letterSpacing: "-0.02em",
              marginBottom: "16px",
              lineHeight: "1.2",
            }}
          >
            Meet the Team
          </h2>
          <p
            className="team-description"
            style={{
              color: "#a0a0a0",
              textAlign: "center",
              fontSize: "1.125rem",
              marginBottom: "60px",
              maxWidth: "600px",
              margin: "0 auto 60px",
              lineHeight: "1.6",
            }}
          >
            The passionate individuals behind Invox who are revolutionizing
            invoice management
          </p>
          <div
            className="team-cards-container"
            style={{
              display: "flex",
              flexDirection: "row",
              gap: "32px",
              justifyContent: "center",
              alignItems: "center",
              flexWrap: "wrap",
            }}
          >
            {cardsData.map(({ imageSrc, altText, name, role }, index) => (
              <div
                key={index}
                style={{
                  flex: "0 0 auto",
                  width: "280px",
                  cursor: "pointer",
                }}
                onClick={() => {
                  window.open(cardsData[index].linkedin, "_blank");
                }}
              >
                <TiltedCard
                  imageSrc={imageSrc}
                  altText={altText}
                  captionText={`${name} - ${role}`}
                  containerHeight="320px"
                  containerWidth="280px"
                  imageHeight="280px"
                  imageWidth="280px"
                  rotateAmplitude={15}
                  scaleOnHover={1.08}
                  showMobileWarning={false}
                  showTooltip={true}
                  displayOverlayContent={false}
                />
                <div
                  style={{
                    textAlign: "center",
                    marginTop: "20px",
                    color: "#fff",
                  }}
                >
                  <h3
                    style={{
                      fontSize: "1.25rem",
                      fontWeight: "600",
                      marginBottom: "4px",
                      color: "#fff",
                    }}
                  >
                    {name}
                  </h3>
                  <p
                    style={{
                      fontSize: "0.95rem",
                      color: "#888",
                      fontWeight: "400",
                    }}
                  >
                    {role}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
};

export default CardSection;
