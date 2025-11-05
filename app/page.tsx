import { Button } from "@/components/ui/button";
import Navbar from "@/components/ui/Navbar";
import ReverseTriangleGradient from "@/components/gradient";
import Prism from "@/components/Prism";
import StarBorder from "@/components/StarBorder";
export default function Home() {
  return (
    <>
      <div className="flex justify-center items-center h-screen w-screen">
        <Navbar></Navbar>
        <Button
          className="fixed top-10  right-1 z-50 mr-15 "
          variant={"secondary"}
        >
          Login
        </Button>
        <Button className="fixed top-10  right-1 z-50 mr-39">Signup</Button>
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
        ></Prism>
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="flex flex-col justify-center items-center">
            <div className="text-white text-6xl text-center bg-inherit w-[700px] mb-9">
              AI Platform for Teams Buried in Manual Paperwork
            </div>
            <div className="mb-9">
              Turn complex documents into structured insights to JSON and CSV
              format
            </div>
            <div>
              <Button className="w-[250px] text-[18px] flex">
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
