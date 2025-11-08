"use client";

import { signIn } from "next-auth/react";
import Prism from "@/components/Prism";
import Navbar from "@/components/ui/Navbar";
import NavbarMenu from "@/components/NavBarMenu";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { useEffect } from "react";

export default function SignIn() {
  const router = useRouter();
  const { status } = useSession();

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (status === "authenticated") {
      router.push("/dashboard");
    }
  }, [status, router]);

  const handleGoogleSignIn = () => {
    signIn("google", { callbackUrl: "/dashboard" });
  };

  return (
    <main className="relative min-h-screen w-screen overflow-hidden">
      {/* Navbar */}
      <div className="fixed top-0 w-full z-50">
        <Navbar />
        <NavbarMenu />
      </div>

      {/* Prism Background */}
      <section className="absolute inset-0 flex items-center justify-center">
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

        {/* Sign In Content */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
          <div className="pointer-events-auto">
            {/* Solid Card Container with Shadow */}
            <div className="relative bg-white rounded-3xl shadow-[0_20px_80px_rgba(0,0,0,0.5)] p-8 md:p-12 max-w-md w-[90vw] md:w-full overflow-hidden">
              {/* Subtle gradient overlay */}
              <div className="absolute inset-0 bg-gradient-to-br from-blue-50/30 via-purple-50/20 to-pink-50/30 rounded-3xl" />

              {/* Content */}
              <div className="relative z-10 space-y-8">
                {/* Logo/Brand */}
                <div className="text-center space-y-3">
                  <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 bg-clip-text text-transparent">
                    Invox
                  </h1>
                  <p className="text-gray-600 text-sm md:text-base">
                    AI-Powered Invoice Management
                  </p>
                </div>

                {/* Google Sign In Button */}
                <div className="space-y-4">
                  <button
                    onClick={handleGoogleSignIn}
                    className="group relative w-full px-6 py-4 rounded-2xl bg-white hover:bg-gray-50 border-2 border-gray-200 shadow-xl hover:shadow-2xl transition-all duration-500 hover:scale-[1.02] flex items-center justify-center gap-4 overflow-hidden"
                  >
                    {/* Animated gradient background on hover */}
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-2xl" />

                    {/* Animated border glow */}
                    <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                      <div
                        className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 blur-sm"
                        style={{ padding: "2px" }}
                      />
                    </div>

                    {/* Google Logo with animation */}
                    <div className="relative z-10 flex items-center justify-center transform transition-all duration-500 group-hover:rotate-[360deg] group-hover:scale-110">
                      <svg
                        className="w-6 h-6 md:w-7 md:h-7"
                        viewBox="0 0 24 24"
                      >
                        <path
                          fill="#4285F4"
                          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                        />
                        <path
                          fill="#34A853"
                          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                        />
                        <path
                          fill="#FBBC05"
                          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                        />
                        <path
                          fill="#EA4335"
                          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                        />
                      </svg>
                    </div>

                    {/* Button Text */}
                    <span className="relative z-10 font-bold text-base md:text-lg text-gray-800 group-hover:text-gray-900 transition-colors duration-300">
                      Sign in with Google
                    </span>

                    {/* Shimmer effect */}
                    <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/40 to-transparent skew-x-12" />
                  </button>

                  {/* Info text */}
                  <p className="text-center text-xs md:text-sm text-gray-500">
                    By signing in, you agree to our{" "}
                    <span className="text-gray-700 hover:text-gray-900 cursor-pointer underline transition-colors">
                      Terms of Service
                    </span>{" "}
                    and{" "}
                    <span className="text-gray-700 hover:text-gray-900 cursor-pointer underline transition-colors">
                      Privacy Policy
                    </span>
                  </p>
                </div>

                {/* Features List */}
                <div className="pt-6 border-t border-gray-200 space-y-3">
                  <p className="text-gray-500 text-xs uppercase tracking-wider text-center mb-4">
                    What you'll get
                  </p>
                  <div className="grid grid-cols-1 gap-3">
                    {[
                      { text: "AI-Powered OCR Extraction" },
                      { text: "Real-time Dashboard Analytics" },
                      { text: "Bank-Level Security" },
                    ].map((feature, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-3 text-gray-700 text-sm group/feature hover:text-gray-900 transition-colors duration-300"
                      >
                        <div className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 group-hover/feature:scale-150 transition-transform duration-300" />
                        <span>{feature.text}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Decorative elements - subtle */}
              <div className="absolute -top-24 -right-24 w-48 h-48 bg-blue-100/40 rounded-full blur-3xl" />
              <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-purple-100/40 rounded-full blur-3xl" />
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
