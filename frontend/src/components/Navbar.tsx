"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { LogOut, Settings, User } from "lucide-react";
import { logout, getUser } from "@/lib/auth";

export default function Navbar() {
  const router = useRouter();
  const user = getUser();
  const [isOpen, setIsOpen] = useState(false);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <nav className="fixed top-0 right-0 left-64 lg:left-64 h-16 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-6 z-30">
      {/* Spacer for mobile */}
      <div className="lg:hidden" />

      {/* User Menu */}
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-800/50 transition-colors"
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-red-600 to-red-700 flex items-center justify-center text-white text-sm font-bold">
            {user?.full_name?.charAt(0) || "U"}
          </div>
          <div className="text-sm">
            <p className="font-medium text-white">{user?.full_name || "User"}</p>
            <p className="text-xs text-gray-400">{user?.email}</p>
          </div>
        </button>

        {/* Dropdown Menu */}
        {isOpen && (
          <div className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-lg overflow-hidden z-50">
            <button className="w-full px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 flex items-center gap-2 border-b border-gray-700">
              <User size={16} />
              Profile
            </button>
            <button className="w-full px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 flex items-center gap-2 border-b border-gray-700">
              <Settings size={16} />
              Settings
            </button>
            <button
              onClick={handleLogout}
              className="w-full px-4 py-2 text-sm text-red-400 hover:bg-gray-700 flex items-center gap-2"
            >
              <LogOut size={16} />
              Sign Out
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
