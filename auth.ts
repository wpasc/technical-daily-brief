import NextAuth from "next-auth";
import Google from "next-auth/providers/google";

// Single-user gate: only AUTH_ALLOWED_EMAIL ever gets a session.
export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [Google],
  callbacks: {
    signIn({ user, profile }) {
      const email = user?.email ?? profile?.email;
      return !!email && email === process.env.AUTH_ALLOWED_EMAIL;
    },
    authorized({ auth }) {
      return !!auth?.user;
    },
  },
});
