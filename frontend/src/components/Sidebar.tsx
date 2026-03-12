"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import { cn } from "@/lib/utils";

export default function Sidebar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(true);

  const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: "📊" },
    { name: "Scans", href: "/scans", icon: "⚡" },
    { name: "Targets", href: "/targets", icon: "🎯" },
    { name: "Compliance", href: "/compliance", icon: "✓" },
    { name: "Reports", href: "/reports", icon: "📄" },
    { name: "Agents", href: "/agents", icon: "🤖" },
    { name: "Monitor", href: "/monitor", icon: "👁️" },
    { name: "MCP Scanner", href: "/mcp", icon: "🔍" },
    { name: "SBOM", href: "/sbom", icon: "📋" },
    { name: "Shadow AI", href: "/shadow-ai", icon: "👻" },
    { name: "Integrations", href: "/integrations", icon: "🔗" },
    { name: "Playground", href: "/playground", icon: "🎮" },
    { name: "Settings", href: "/settings", icon: "⚙️" },
  ];

  const isActive = (href: string) => {
    return pathname?.startsWith(href) || false;
  };

  return (
    <>
      {/* Mobile Toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 lg:hidden bg-gray-800 hover:bg-gray-700 rounded-lg p-2 text-gray-300"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 h-screen w-64 bg-gray-900 border-r border-gray-800 transition-transform duration-300 z-40 lg:translate-x-0",
          !isOpen && "-translate-x-full"
        )}
      >
        {/* Logo */}
        <div className="flex items-center gap-2 p-6 border-b border-gray-800">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-red-600 to-red-700 flex items-center justify-center">
            <span className="text-white font-bold text-sm">AR</span>
          </div>
          <div>
            <p className="font-bold text-white text-sm">AgentRed</p>
            <p className="text-xs text-gray-400">Red Teaming</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {navigation.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setIsOpen(false)}
              className={cn(
                "flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors text-sm font-medium",
                isActive(item.href)
                  ? "bg-red-600/20 text-red-400 border border-red-600/30"
                  : "text-gray-400 hover:bg-gray-800/50 hover:text-gray-300"
              )}
            >
              <span className="text-lg">{item.icon}</span>
              {item.name}
            </Link>
          ))}
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-800">
          <div className="p-4 rounded-lg bg-blue-900/20 border border-blue-800/30">
            <p className="text-xs text-blue-400 font-medium mb-2">Pro Access</p>
            <p className="text-xs text-gray-400">
              All features unlocked during beta
            </p>
          </div>
        </div>
      </aside>

      {/* Overlay */}
      {isOpen && (
        <div
          onClick={() => setIsOpen(false)}
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
        />
      )}
    </>
  );
}
