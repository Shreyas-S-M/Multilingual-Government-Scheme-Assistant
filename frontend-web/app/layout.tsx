import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sahayaka — Public Benefits, Made Clear",
  description: "Find government welfare schemes across Central, Karnataka, Andhra Pradesh, Tamil Nadu, and Kerala with transparent eligibility guidance.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
