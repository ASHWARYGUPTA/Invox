import { getServerSession } from "next-auth";
import { authOptions } from "../api/auth/[...nextauth]/route";
import ClientComponent from "./client";

export default async function TempPage() {
  const session = await getServerSession(authOptions);

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-2xl font-bold mb-4">Next-Auth Demo Page</h1>
      
      <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 shadow-lg">
        <h2 className="text-xl font-semibold mb-2">Server-Side Session Status:</h2>
        <p className="mb-4">
          {session ? "✅ Authenticated" : "❌ Not authenticated"}
        </p>

        {session && (
          <>
            <h2 className="text-xl font-semibold mb-2">Server-Side Session Info:</h2>
            <pre className="bg-gray-800 p-4 rounded-lg overflow-auto">
              {JSON.stringify(session, null, 2)}
            </pre>
          </>
        )}

        {!session && (
          <p className="text-yellow-500">
            Please sign in to view session details
          </p>
        )}
      </div>

      {/* Client-side component demonstrating useSession, signIn, and signOut */}
      <ClientComponent />
    </div>
  );
}
