"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";
import Link from "next/link";

export default function NavbarMenu() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <>
      {/* Desktop Buttons (Hidden on Mobile) */}
      <div className="hidden md:flex fixed top-0 right-0 z-50 mt-10">
        <Button variant="secondary" className="mx-2" asChild>
          <Link href="/signin">Login</Link>
        </Button>
        <Button className="mx-4" asChild>
          <Link href="/signup">Signup</Link>
        </Button>
      </div>

      {/* Mobile Menu Button (Hidden on Desktop) */}
      <div className="flex md:hidden fixed top-0 right-0 mt-10 mr-4 z-50">
        <Button
          variant="secondary"
          size="icon"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          {menuOpen ? <X /> : <Menu />}
        </Button>
      </div>

      {/* Mobile Dropdown Menu */}
      {menuOpen && (
        <div className="fixed top-16 right-4 bg-muted/90 backdrop-blur-md rounded-xl shadow-lg p-4 flex flex-col items-start space-y-2 md:hidden z-40">
          <Button variant="outline" className="w-full" asChild>
            <Link href="/signin">Login</Link>
          </Button>
          <Button className="w-full" asChild>
            <Link href="/signup">Signup</Link>
          </Button>
        </div>
      )}
    </>
  );
}
