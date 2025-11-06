"use client";

import { signIn } from "next-auth/react";
import { Button } from "@/components/ui/button";

export default function SignIn() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-sm space-y-4 rounded-lg p-6 shadow-lg">
        <h1 className="text-2xl font-bold text-center">Sign In</h1>
        <Button
          onClick={() => signIn("google", { callbackUrl: "/" })}
          className="w-full"
        >
          Sign in with Google
        </Button>
      </div>
    </div>
  );
}
