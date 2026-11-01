import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sahayaka — Government Scheme Assistant",
  description: "Find government schemes in English or Kannada with transparent eligibility guidance.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
