"use client";
import Link from "next/link";
import { useState, useEffect } from "react";

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      // Change text color when scrolled past the first screen (viewport height)
      setIsScrolled(window.scrollY > window.innerHeight);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  // Dynamic text color classes based on scroll position
  const textColorClass = isScrolled ? "text-white/90" : "text-foreground/70";
  const hoverColorClass = isScrolled
    ? "hover:text-white"
    : "hover:text-primary";
  const logoColorClass = isScrolled ? "text-white" : "text-foreground";

  return (
    <div>
      <nav className="fixed top-6 left-1/2 -translate-x-1/2 w-[90%] max-w-4xl z-50">
        <div className="flex justify-between items-center bg-background/10 backdrop-blur-xl border border-white/20 rounded-full shadow-lg shadow-black/5 px-6 py-2.5 transition-colors duration-300">
          <div className="flex-shrink-0">
            <Link
              href="/"
              className={`flex items-center gap-2 hover:opacity-80 transition-all duration-300`}
            >
              <img src="/favicon.ico" alt="Invox Logo" className="w-8 h-8" />
              <span className={`text-3xl font-bold ${logoColorClass}`}>
                Invox
              </span>
            </Link>
          </div>
          <div className="hidden md:flex flex-1 justify-center">
            <ul className="flex items-center gap-8">
              <li>
                <button
                  onClick={() => scrollToSection("features")}
                  className={`text-sm font-medium ${textColorClass} ${hoverColorClass} transition-colors duration-300 cursor-pointer`}
                >
                  Features
                </button>
              </li>
              <li>
                <button
                  onClick={() => scrollToSection("how-it-works")}
                  className={`text-sm font-medium ${textColorClass} ${hoverColorClass} transition-colors duration-300 cursor-pointer`}
                >
                  How It Works
                </button>
              </li>
              <li>
                <Link
                  href="/documentation"
                  className={`text-sm font-medium ${textColorClass} ${hoverColorClass} transition-colors duration-300`}
                >
                  Documentation
                </Link>
              </li>
              <li>
                <Link
                  href="/dashboard"
                  className={`text-sm font-medium ${textColorClass} ${hoverColorClass} transition-colors duration-300`}
                >
                  Demo
                </Link>
              </li>
              <li>
                <button
                  onClick={() => scrollToSection("about")}
                  className={`text-sm font-medium ${textColorClass} ${hoverColorClass} transition-colors duration-300 cursor-pointer`}
                >
                  About Us
                </button>
              </li>
            </ul>
          </div>
          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className={`${textColorClass} ${hoverColorClass} transition-colors duration-300 cursor-pointer active:scale-90`}
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                {mobileMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile menu dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-2 bg-background/95 backdrop-blur-xl border border-white/20 rounded-2xl shadow-lg overflow-hidden">
            <ul className="flex flex-col py-2">
              <li>
                <button
                  onClick={() => {
                    scrollToSection("features");
                    setMobileMenuOpen(false);
                  }}
                  className={`w-full text-left px-6 py-3 text-sm font-medium ${textColorClass} ${hoverColorClass} transition-colors duration-300 cursor-pointer`}
                >
                  Features
                </button>
              </li>
              <li>
                <button
                  onClick={() => {
                    scrollToSection("how-it-works");
                    setMobileMenuOpen(false);
                  }}
                  className={`w-full text-left px-6 py-3 text-sm font-medium ${textColorClass} ${hoverColorClass} transition-colors duration-300 cursor-pointer`}
                >
                  How It Works
                </button>
              </li>
              <li>
                <Link
                  href="/documentation"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block px-6 py-3 text-sm font-medium ${textColorClass} ${hoverColorClass} transition-colors duration-300`}
                >
                  Documentation
                </Link>
              </li>
              <li>
                <Link
                  href="/dashboard"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block px-6 py-3 text-sm font-medium ${textColorClass} ${hoverColorClass} transition-colors duration-300`}
                >
                  Demo
                </Link>
              </li>
              <li>
                <button
                  onClick={() => {
                    scrollToSection("about");
                    setMobileMenuOpen(false);
                  }}
                  className={`w-full text-left px-6 py-3 text-sm font-medium ${textColorClass} ${hoverColorClass} transition-colors duration-300 cursor-pointer`}
                >
                  About Us
                </button>
              </li>
            </ul>
          </div>
        )}
      </nav>
    </div>
  );
}
