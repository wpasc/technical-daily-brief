export { auth as middleware } from "@/auth";

// Gate everything except the auth endpoints themselves and Next.js statics.
export const config = {
  matcher: ["/((?!api/auth|_next/static|_next/image|favicon.ico).*)"],
};
