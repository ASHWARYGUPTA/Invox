"use client";

import { useEffect } from "react";
import { signIn } from "next-auth/react";
import Prism from "@/components/Prism";
import Navbar from "@/components/ui/Navbar";

export default function Signin() {
  useEffect(() => {
    // Automatically trigger NextAuth Google sign in
    // After successful auth, NextAuth will redirect to /dashboard
    signIn("google", { callbackUrl: "/dashboard" });
  }, []);

  return (
    <>
      <div className="flex justify-center items-center h-screen w-screen">
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
        />
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none pt-24 md:pt-0">
          <div className="bg-black/80 backdrop-blur-md p-8 md:p-10 max-w-[450px] rounded-3xl pointer-events-auto mx-4">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <h2 className="text-xl font-semibold text-white mb-2">
                Redirecting to Google Login
              </h2>
              <p className="text-sm text-muted-foreground">Please wait...</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
