"use client";

import React from "react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f0f0f] via-gray-900 to-[#0f0f0f] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-block">
            <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-gradient-to-br from-red-600 to-red-700 mb-4 mx-auto">
              <span className="text-white font-bold text-lg">AR</span>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-white">AgentRed</h1>
          <p className="text-gray-400 mt-2">AI Red Teaming Platform</p>
        </div>

        {/* Form Container */}
        <div className="backdrop-blur-xl bg-gray-900/50 border border-gray-800 rounded-xl p-8 shadow-2xl">
          {children}
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>
            Protected by industry-leading security protocols during beta phase
          </p>
        </div>
      </div>
    </div>
  );
}
