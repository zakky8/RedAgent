import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AgentRed — AI Red Teaming Platform",
  description: "The world's most comprehensive AI security testing platform. Test any AI system against 456 attack techniques.",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-[#0f0f0f] text-white min-h-screen`}>
        {children}
      </body>
    </html>
  );
}
