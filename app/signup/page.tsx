import Prism from "@/components/Prism";
import { SignupForm } from "@/components/signup-form";
import Navbar from "@/components/ui/Navbar";
export default function SignupPage() {
  return (
    <>
      <div className="flex justify-center items-center h-screen w-screen ">
        <Navbar />
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
        <div className="absolute  mt-[30px] inset-0 flex items-center justify-center pointer-events-none">
          <div className="bg-black p-10 max-w-[450] md:max-w rounded-4xl">
            <SignupForm />
          </div>
        </div>
      </div>
    </>
  );
}
