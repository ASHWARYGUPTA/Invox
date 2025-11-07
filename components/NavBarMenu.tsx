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

interface UserData {
	name?: string;
	email?: string;
	picture?: string;
}

export default function NavbarMenu() {
	const [menuOpen, setMenuOpen] = useState(false);
	const [user, setUser] = useState<UserData | null>(null);
	const [isAuthenticated, setIsAuthenticated] = useState(false);
	const router = useRouter();

	useEffect(() => {
		// Check authentication and load user data
		const loadUserData = () => {
			const token = tokenManager.getToken();
			const hasToken = !!token;

			if (hasToken) {
				const userData = localStorage.getItem("user");
				if (userData) {
					try {
						const parsedUser = JSON.parse(userData);
						setUser(parsedUser);
						setIsAuthenticated(true);
					} catch (e) {
						console.error("Failed to parse user data:", e);
						setIsAuthenticated(false);
					}
				} else {
					setIsAuthenticated(true);
				}
			} else {
				setUser(null);
				setIsAuthenticated(false);
			}
		};

		loadUserData();
	}, []);

	const handleLogout = () => {
		tokenManager.removeToken();
		localStorage.removeItem("user");
		setUser(null);
		setIsAuthenticated(false);
		router.push("/");
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
					// Authenticated User - Show Avatar and Dropdown
					<DropdownMenu>
						<DropdownMenuTrigger asChild>
							<button className="flex items-center gap-3 px-4 py-2 rounded-full bg-background/10 backdrop-blur-xl border border-white/20 hover:bg-background/20 transition-all duration-300 hover:scale-105">
								<Avatar className="h-9 w-9 ring-2 ring-primary/20">
									<AvatarImage
										src={user.picture}
										alt={user.name || user.email}
									/>
									<AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold">
										{getUserInitials(user.name, user.email)}
									</AvatarFallback>
								</Avatar>
								<span className="font-medium text-foreground/90">
									{user.name || user.email?.split("@")[0]}
								</span>
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
							<DropdownMenuItem
								asChild
								className="cursor-pointer"
							>
								<Link
									href="/dashboard"
									className="flex items-center"
								>
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
					// Not Authenticated - Show Join Us Button
					<Button
						asChild
						size="lg"
						className=" hover:shadow-xl transition-all duration-300 hover:scale-105"
					>
						<Link href="/signin" className="flex items-center">
							<Button variant={"default"}>
								<svg
									className="w-5 h-5"
									viewBox="0 0 24 24"
									fill="currentColor"
								>
									<path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
									<path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
									<path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
									<path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
								</svg>
								Join with Google
							</Button>
						</Link>
					</Button>
				)}
			</div>

			{/* Mobile View */}
			<div className="flex md:hidden fixed top-0 right-0 mt-6 mr-4 z-50">
				{isAuthenticated && user ? (
					// Mobile Authenticated - Avatar with Menu
					<>
						<button
							onClick={() => setMenuOpen(!menuOpen)}
							className="flex items-center gap-2 p-2 rounded-full bg-background/10 backdrop-blur-xl border border-white/20"
						>
							<Avatar className="h-9 w-9 ring-2 ring-primary/20">
								<AvatarImage
									src={user.picture}
									alt={user.name || user.email}
								/>
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
								<div className="flex flex-col space-y-1 mb-3 pb-3 border-b border-white/10">
									<p className="text-sm font-medium">
										{user.name}
									</p>
									<p className="text-xs text-muted-foreground">
										{user.email}
									</p>
								</div>
								<Button
									variant="outline"
									className="w-full mb-2"
									asChild
								>
									<Link
										href="/dashboard"
										onClick={() => setMenuOpen(false)}
									>
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
					// Mobile Not Authenticated - Join Us Button
					<Button
						asChild
						className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 text-white font-semibold shadow-lg shadow-purple-500/50"
					>
						<Link
							href="/signin"
							className="flex items-center gap-2"
						>
							<svg
								className="w-4 h-4"
								viewBox="0 0 24 24"
								fill="currentColor"
							>
								<path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
								<path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
								<path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
								<path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
							</svg>
							Join
						</Link>
					</Button>
				)}
			</div>
		</>
	);
}
