import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import type { NextAuthOptions } from "next-auth";

const BACKEND_URL = (
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"
).replace(/\/$/, "");

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          prompt: "select_account",
        },
      },
    }),
  ],
  session: {
    strategy: "jwt",
  },
  secret: process.env.NEXTAUTH_SECRET,
  pages: {
    signIn: "/auth/signin",
  },
  callbacks: {
    async signIn({ user, account }) {
      try {
        // Send OAuth data to FastAPI backend
        const response = await fetch(
          `${BACKEND_URL}/api/v1/auth/oauth/callback`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              email: user.email,
              name: user.name,
              image: user.image,
              provider: account?.provider || "google",
              provider_account_id: account?.providerAccountId || "",
              access_token: account?.access_token,
              refresh_token: account?.refresh_token,
              expires_at: account?.expires_at,
              id_token: account?.id_token,
              scope: account?.scope,
              token_type: account?.token_type,
              session_state: account?.session_state,
            }),
          }
        );

        if (!response.ok) {
          console.error(
            "Backend authentication failed:",
            await response.text()
          );
          return false;
        }

        const data = await response.json();

        // Store backend JWT token in the user object
        if (user && data.access_token) {
          (user as any).backendToken = data.access_token;
          (user as any).userId = data.user.id;
        }

        return true;
      } catch (error) {
        console.error("Error during sign in:", error);
        return false;
      }
    },
    async jwt({ token, user }) {
      // Initial sign in
      if (user) {
        token.backendToken = (user as any).backendToken;
        token.userId = (user as any).userId;
        token.email = user.email;
        token.name = user.name;
        token.picture = user.image;
      }
      return token;
    },
    async session({ session, token }) {
      // Add backend token to session
      if (session.user) {
        (session as any).backendToken = token.backendToken;
        (session as any).userId = token.userId;
        session.user.email = token.email as string;
        session.user.name = token.name as string;
        session.user.image = token.picture as string;
      }
      return session;
    },
  },
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
