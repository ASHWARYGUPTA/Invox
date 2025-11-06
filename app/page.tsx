import { Button } from "@/components/ui/button";
import Navbar from "@/components/ui/Navbar";
import Prism from "@/components/Prism";
import MagicBento from "@/components/MagicBento";
import NavbarMenu from "@/components/NavBarMenu";
import HeroSection from "@/pages/home/HeroSection";

export default function Home() {
  return (
    <main className="relative">
      {/* Navbar */}
      <div className="fixed top-0 w-full z-50"></div>
      <Navbar />
      <div className=""></div>
      {/* <div className="hidden md:visible fixed top-0 right-0 z-50 mt-10">
        <Button variant={"secondary"} className="mx-2">
          Login
        </Button>
        <Button className="mx-4">Signup</Button>
      </div> */}
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

        {/* Gradient Fade Transition */}
        <div className="absolute bottom-0 left-0 right-0 h-[60px] bg-gradient-to-b from-transparent to-[#001133]/90 backdrop-blur-sm"></div>
      </section>
      {/* Next Section */}
      <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-b from-[#001133] to-black">
        {/* <MagicBento
          bentoWidth="3000px"
          textAutoHide={true}
          enableStars={false}
          enableSpotlight={true}
          enableBorderGlow={true}
          enableTilt={true}
          enableMagnetism={true}
          clickEffect={true}
          spotlightRadius={300}
          particleCount={12}
          glowColor="132, 0, 255"
        /> */}
      </div>
    </main>
  );
}
