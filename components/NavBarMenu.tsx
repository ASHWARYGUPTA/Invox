"use client";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Menu, X, LogOut, LayoutDashboard } from "lucide-react";
import Link from "next/link";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { tokenManager } from "@/lib/api/client";
import { useRouter } from "next/navigation";
import { useSession, signOut } from "next-auth/react";

interface UserData {
  name?: string;
  email?: string;
  picture?: string;
}

export default function NavbarMenu() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { data: session, status } = useSession();
  const router = useRouter();

  const isAuthenticated = status === "authenticated";
  const user = session?.user
    ? {
        name: session.user.name || undefined,
        email: session.user.email || undefined,
        picture: session.user.image || undefined,
      }
    : null;

  const handleLogout = async () => {
    // Clear localStorage token
    tokenManager.removeToken();
    localStorage.removeItem("user");
    // Sign out with NextAuth
    await signOut({ callbackUrl: "/" });
  };

  const getUserInitials = (name?: string, email?: string) => {
    if (name) {
      const parts = name.split(" ");
      if (parts.length >= 2) {
        return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
      }
      return name.substring(0, 2).toUpperCase();
    }
    if (email) {
      return email.substring(0, 2).toUpperCase();
    }
    return "U";
  };

  return (
    <>
      {/* Desktop View */}
      <div className="hidden md:flex fixed top-0 right-0 z-50 mt-10 mr-8">
        {isAuthenticated && user ? (
          // Authenticated User - Show Avatar Only (No Name)
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center p-1 rounded-full bg-background/10 backdrop-blur-xl border border-white/20 hover:bg-background/20 transition-all duration-300 hover:scale-105 cursor-pointer">
                <Avatar className="h-9 w-9 ring-2 ring-white/60 hover:ring-white/80 transition-all duration-300">
                  <AvatarImage
                    src={user.picture}
                    alt={user.name || user.email}
                  />
                  <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold">
                    {getUserInitials(user.name, user.email)}
                  </AvatarFallback>
                </Avatar>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="w-56 bg-background/95 backdrop-blur-xl border-white/20"
            >
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">
                    {user.name}
                  </p>
                  <p className="text-xs leading-none text-muted-foreground">
                    {user.email}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-white/10" />
              <DropdownMenuItem asChild className="cursor-pointer">
                <Link href="/dashboard" className="flex items-center">
                  <LayoutDashboard className="mr-2 h-4 w-4" />
                  <span>Dashboard</span>
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={handleLogout}
                className="cursor-pointer text-red-400 focus:text-red-400"
              >
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          // Not Authenticated - Show Enhanced Join With Google Button
          <Link href="/auth/signin">
            <button className="group relative px-4 py-2 rounded-full bg-white hover:bg-gray-50 border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 flex items-center gap-2 overflow-hidden cursor-pointer">
              {/* Animated gradient background on hover */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-full" />

              {/* Google Logo */}
              <div className="relative z-10 flex items-center justify-center shrink-0">
                <svg
                  className="w-4 h-4 transition-transform duration-300 group-hover:rotate-12"
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
              <span className="relative z-10 text-sm font-semibold text-gray-700 group-hover:text-gray-900 transition-colors duration-300 whitespace-nowrap">
                Join with Google
              </span>

              {/* Shimmer effect */}
              <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/30 to-transparent" />
            </button>
          </Link>
        )}
      </div>

      {/* Mobile View */}
      <div className="flex md:hidden fixed top-6 right-4 z-50">
        {isAuthenticated && user ? (
          // Mobile Authenticated - Avatar with Menu
          <>
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="flex items-center gap-2 p-2 rounded-full bg-background/10 backdrop-blur-xl border border-white/20 cursor-pointer hover:bg-background/20 transition-all duration-200 active:scale-95"
            >
              <Avatar className="h-9 w-9 ring-2 ring-white/60 hover:ring-white/80 transition-all duration-300">
                <AvatarImage src={user.picture} alt={user.name || user.email} />
                <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold text-sm">
                  {getUserInitials(user.name, user.email)}
                </AvatarFallback>
              </Avatar>
              {menuOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>

            {/* Mobile Dropdown - Authenticated */}
            {menuOpen && (
              <div className="absolute top-16 right-0 bg-background/95 backdrop-blur-xl border border-white/20 rounded-xl shadow-lg p-4 min-w-[240px]">
                <Button variant="outline" className="w-full mb-2" asChild>
                  <Link href="/dashboard" onClick={() => setMenuOpen(false)}>
                    <LayoutDashboard className="mr-2 h-4 w-4" />
                    Dashboard
                  </Link>
                </Button>
                <Button
                  variant="destructive"
                  className="w-full"
                  onClick={handleLogout}
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Log out
                </Button>
              </div>
            )}
          </>
        ) : (
          // Mobile Not Authenticated - Enhanced Join Button
          <Link href="/auth/signin">
            <button className="group relative px-4 py-2.5 rounded-full bg-white hover:bg-gray-50 border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 flex items-center gap-2 overflow-hidden cursor-pointer">
              {/* Animated gradient background on hover */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-full" />

              {/* Google Logo - Compact for mobile */}
              <div className="relative z-10 flex items-center justify-center">
                <svg
                  className="w-4 h-4 transition-transform duration-300 group-hover:rotate-12"
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

              {/* Button Text - Shorter for mobile */}
              <span className="relative z-10 font-semibold text-sm text-gray-700 group-hover:text-gray-900 transition-colors duration-300">
                Join
              </span>

              {/* Shimmer effect */}
              <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/30 to-transparent" />
            </button>
          </Link>
        )}
      </div>
    </>
  );
}
