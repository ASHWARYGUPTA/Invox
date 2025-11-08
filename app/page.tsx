"use client";

import Navbar from "@/components/ui/Navbar";
import Prism from "@/components/Prism";
import NavbarMenu from "@/components/NavBarMenu";
import HeroSection from "@/pages/home/HeroSection";
import {
  organizationSchema,
  webApplicationSchema,
  faqSchema,
} from "@/lib/structured-data";
import CardSection from "@/components/ui/CreatedBySection";
import InfoCards from "@/components/ui/InfoCards";
import WhoWeAre from "@/components/ui/WhoWeAre";
import MagicBento from "@/components/MagicBento";

export default function Home() {
  return (
    <main className="relative">
      {/* Structured Data for SEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(organizationSchema),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(webApplicationSchema),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      {/* Navbar */}
      <div className="fixed top-0 w-full z-50"></div>
      <Navbar />
      <div className=""></div>

      <NavbarMenu />
      {/* Hero Section with Prism */}
      <section className="h-screen w-screen flex items-center justify-center relative overflow-hidden">
        <Prism
          animationType="hover"
          timeScale={2}
          height={3.5}
          baseWidth={9}
          scale={3.6}
          hueShift={0}
          colorFrequency={1}
          noise={0.2}
          glow={0.5}
        />

        {/* Hero Content */}
        <HeroSection />

        {/* Gradient Fade Transition
				<div className="absolute bottom-0 left-0 right-0 h-[60px] bg-gradient-to-b from-transparent to-[#001133]/90 backdrop-blur-sm"></div> */}
      </section>

      {/* About Us Section */}
      <WhoWeAre />

      {/* Next Section */}
      <div
        className="min-h-screen w-full flex items-center justify-center bg-gradient-to-b from-[#001133] to-black"
        id="features"
      >
        <InfoCards />
      </div>

      <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-b from-[#001133] to-black">
        <MagicBento
          textAutoHide={true}
          enableStars={true}
          enableSpotlight={true}
          enableBorderGlow={true}
          enableTilt={true}
          enableMagnetism={true}
          clickEffect={true}
          spotlightRadius={300}
          particleCount={12}
          glowColor="132, 0, 255"
        />
      </div>

      {/* About Us Section */}
      <div className="min-h-screen w-full flex items-baseline justify-center bg-gradient-to-b from-[#001133] to-black">
        <section
          id="about"
          className="min-h-screen w-full bg-gradient-to-b from-black to-[#001133] py-20 px-6 flex items-center"
        >
          <CardSection />
        </section>
      </div>
    </main>
  );
}
