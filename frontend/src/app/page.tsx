"use client";

import React from "react";
import Link from "next/link";
import Button from "@/components/Button";
import Badge from "@/components/Badge";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f0f0f] via-gray-900 to-[#1a1a1a]">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-red-600 to-red-700 flex items-center justify-center">
            <span className="text-white font-bold text-sm">AR</span>
          </div>
          <span className="text-xl font-bold text-white">AgentRed</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/login">
            <Button variant="outline" size="sm">
              Sign In
            </Button>
          </Link>
          <Link href="/register">
            <Button variant="primary" size="sm">
              Get Started
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="px-6 py-20 sm:py-32 max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <Badge variant="info" className="mb-6">
            Now in Open Beta
          </Badge>
          <h1 className="text-5xl sm:text-7xl font-bold text-white mb-6 leading-tight">
            The World's Most <br />
            <span className="bg-gradient-to-r from-red-600 via-red-500 to-red-600 bg-clip-text text-transparent">
              Comprehensive AI Red Teaming
            </span>{" "}
            Platform
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-8">
            Test any AI system against 456 attack techniques across 47 categories. Identify vulnerabilities before threat actors do.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/login">
              <Button variant="primary" size="lg">
                Get Early Access
              </Button>
            </Link>
            <Button variant="outline" size="lg">
              Learn More
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-16">
          {[
            { label: "Attack Techniques", value: "456" },
            { label: "Categories", value: "47" },
            { label: "Compliance Frameworks", value: "6" },
            { label: "Setup Required", value: "0" },
          ].map((stat) => (
            <div
              key={stat.label}
              className="p-6 rounded-lg border border-gray-800 bg-gray-900/50 backdrop-blur-sm text-center"
            >
              <p className="text-3xl font-bold text-white mb-2">{stat.value}</p>
              <p className="text-gray-400 text-sm">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="px-6 py-20 border-t border-gray-800 bg-gray-900/30">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-16">
            Comprehensive Security Testing
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: "📚",
                title: "Attack Library",
                description: "456 pre-built attack patterns covering prompt injection, jailbreaks, data extraction, and more.",
              },
              {
                icon: "⚡",
                title: "Live Scanner",
                description: "Real-time scanning with live progress tracking and streaming results as attacks complete.",
              },
              {
                icon: "📊",
                title: "Compliance Reports",
                description: "Auto-generated reports for EU AI Act, NIST AI RMF, OWASP LLM, ISO 42001, SOC2, and more.",
              },
              {
                icon: "👁️",
                title: "Monitor SDK",
                description: "Embed continuous monitoring in your production systems for real-time threat detection.",
              },
              {
                icon: "💻",
                title: "CLI Tool",
                description: "Command-line interface for CI/CD integration and automated security scanning.",
              },
              {
                icon: "⚙️",
                title: "Real-time Results",
                description: "Stream results as they happen with WebSocket support and live dashboards.",
              },
            ].map((feature) => (
              <div
                key={feature.title}
                className="p-6 rounded-lg border border-gray-800 bg-gray-900/50 hover:bg-gray-900/70 transition-colors"
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-lg font-semibold text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-400 text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Beta Section */}
      <section className="px-6 py-20 border-t border-gray-800">
        <div className="max-w-4xl mx-auto text-center">
          <Badge variant="success" className="mb-6">
            Free During Beta
          </Badge>
          <h2 className="text-3xl font-bold text-white mb-6">
            Coming Soon — Limited Beta Access
          </h2>
          <p className="text-gray-400 text-lg mb-8">
            Join our early adopter program and get unlimited access during the beta phase. No credit card required. All users get full Pro access.
          </p>
          <Link href="/login">
            <Button variant="primary" size="lg">
              Request Beta Access
            </Button>
          </Link>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="px-6 py-16 border-t border-gray-800 bg-gray-900/30">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-gray-400 mb-8">Built with modern security-first technologies</p>
          <div className="flex flex-wrap justify-center gap-4">
            {["FastAPI", "PostgreSQL", "Next.js", "TypeScript", "Tailwind CSS", "LLMs", "OWASP", "MITRE ATT&CK"].map(
              (tech) => (
                <Badge key={tech} variant="secondary">
                  {tech}
                </Badge>
              )
            )}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 px-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <p className="text-gray-500 text-sm">
            © 2024 AgentRed. All rights reserved.
          </p>
          <div className="flex gap-6 text-gray-500 text-sm">
            <a href="#" className="hover:text-gray-400">
              Privacy
            </a>
            <a href="#" className="hover:text-gray-400">
              Terms
            </a>
            <a href="#" className="hover:text-gray-400">
              Docs
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
