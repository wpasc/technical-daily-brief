import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Learning Center",
  description: "Private learning center — daily brief, review queue, library.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
