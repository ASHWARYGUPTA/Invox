"use client";

import { useSession, signIn, signOut } from "next-auth/react";
import { Button } from "@/components/ui/button";

export default function ClientComponent() {
  const { data: session, status } = useSession();

  return (
    <div className="mt-8 bg-white/10 backdrop-blur-lg rounded-lg p-6 shadow-lg">
      <h2 className="text-xl font-semibold mb-4">Client Side Session</h2>

      <div className="mb-4">
        <p>Status: {status}</p>
        {session?.user?.email && <p>Email: {session.user.email}</p>}
      </div>

      <div className="space-x-4">
        {session ? (
          <Button onClick={() => signOut()}>Sign Out</Button>
        ) : (
          <Button onClick={() => signIn("google")}>Sign In</Button>
        )}
      </div>

      {session && (
        <div className="mt-4">
          <h3 className="text-lg font-semibold mb-2">Session Data:</h3>
          <pre className="bg-gray-800 p-4 rounded-lg overflow-auto">
            {JSON.stringify(session, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
