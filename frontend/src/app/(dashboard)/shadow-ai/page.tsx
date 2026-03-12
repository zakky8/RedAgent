"use client";
import { useState } from "react";

const SCAN_MODES = [
  {
    id: "requirements",
    label: "requirements.txt",
    icon: "📦",
    placeholder: "Paste requirements.txt content...",
  },
  {
    id: "env_vars",
    label: "Environment Variables",
    icon: "🔑",
    placeholder: "KEY=value pairs, one per line...",
  },
  {
    id: "network_logs",
    label: "Network Logs",
    icon: "🌐",
    placeholder: "Paste network access logs...",
  },
  {
    id: "code",
    label: "Source Code",
    icon: "💻",
    placeholder: "Paste Python/JS/TS code...",
  },
];

const KNOWN_SERVICES = [
  {
    name: "OpenAI API",
    host: "api.openai.com",
    risk: "critical",
    category: "LLM Provider",
  },
  {
    name: "Anthropic Claude",
    host: "api.anthropic.com",
    risk: "critical",
    category: "LLM Provider",
  },
  {
    name: "Google Vertex AI",
    host: "vertexai.googleapis.com",
    risk: "critical",
    category: "LLM Provider",
  },
  {
    name: "AWS Bedrock",
    host: "bedrock.*.amazonaws.com",
    risk: "critical",
    category: "LLM Provider",
  },
  {
    name: "Cohere API",
    host: "api.cohere.ai",
    risk: "critical",
    category: "LLM Provider",
  },
  {
    name: "Hugging Face Inference",
    host: "api-inference.huggingface.co",
    risk: "high",
    category: "ML Service",
  },
  {
    name: "LangChain Tracing",
    host: "api.smith.langchain.com",
    risk: "medium",
    category: "Observability",
  },
];

interface Finding {
  service: string;
  host: string;
  risk: "critical" | "high" | "medium" | "low";
  category: string;
  evidence: string;
  authorized: boolean;
}

export default function ShadowAIPage() {
  const [mode, setMode] = useState("requirements");
  const [input, setInput] = useState("");
  const [findings, setFindings] = useState<Finding[]>([]);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState("");
  const [overallRisk, setOverallRisk] = useState<string | null>(null);

  async function handleScan() {
    if (!input.trim()) {
      setError("Please enter content to scan");
      return;
    }

    setError("");
    setScanning(true);
    setFindings([]);

    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch("/api/v1/shadow-ai/scan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          mode: mode,
          content: input,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setFindings(data.findings || []);
        setOverallRisk(data.overall_risk || "low");
      } else {
        setError("Scan failed. Please try again.");
      }
    } catch (err) {
      setError(
        "Error scanning content. " + (err instanceof Error ? err.message : "Unknown error")
      );
    } finally {
      setScanning(false);
    }
  }

  const riskBadge = (risk: string) => {
    const colors = {
      critical: "bg-red-900/30 text-red-400 border border-red-800",
      high: "bg-orange-900/30 text-orange-400 border border-orange-800",
      medium: "bg-yellow-900/30 text-yellow-400 border border-yellow-800",
      low: "bg-blue-900/30 text-blue-400 border border-blue-800",
    };
    return colors[risk as keyof typeof colors] || colors.low;
  };

  const authorizedFindings = findings.filter((f) => f.authorized).length;
  const unauthorizedFindings = findings.filter((f) => !f.authorized).length;

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Shadow AI Detection</h1>
        <p className="text-gray-400">
          Detect unauthorized AI service usage in your infrastructure
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Scan Input */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h2 className="text-lg font-semibold text-white mb-4">Scan Input</h2>

            {/* Mode Tabs */}
            <div className="flex gap-2 mb-4 flex-wrap">
              {SCAN_MODES.map((m) => (
                <button
                  key={m.id}
                  onClick={() => {
                    setMode(m.id);
                    setInput("");
                    setFindings([]);
                    setError("");
                  }}
                  disabled={scanning}
                  className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                    mode === m.id
                      ? "bg-red-600 text-white"
                      : "bg-gray-900 hover:bg-gray-700 text-gray-400"
                  }`}
                >
                  <span className="mr-2">{m.icon}</span>
                  {m.label}
                </button>
              ))}
            </div>

            {/* Text Input */}
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={SCAN_MODES.find((m) => m.id === mode)?.placeholder}
              disabled={scanning}
              rows={10}
              className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-3 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-red-500 disabled:opacity-50"
            />

            {error && <p className="text-red-400 text-sm mt-3">{error}</p>}

            <button
              onClick={handleScan}
              disabled={!input.trim() || scanning}
              className="mt-4 w-full bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white py-3 rounded-lg font-medium transition-colors"
            >
              {scanning ? "Scanning..." : "Scan for Shadow AI"}
            </button>
          </div>

          {/* Known Services Reference */}
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Known AI Services Database</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {KNOWN_SERVICES.map((service, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg border border-gray-600/30 text-sm"
                >
                  <div>
                    <p className="text-white font-medium">{service.name}</p>
                    <p className="text-gray-400 text-xs mt-1 font-mono">{service.host}</p>
                  </div>
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      service.risk === "critical"
                        ? "bg-red-900/30 text-red-400"
                        : service.risk === "high"
                          ? "bg-orange-900/30 text-orange-400"
                          : "bg-yellow-900/30 text-yellow-400"
                    }`}
                  >
                    {service.risk}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Summary Panel */}
        {findings.length > 0 && (
          <div className="space-y-4">
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">Overall Risk</h3>
              <div
                className={`text-4xl font-bold mb-4 ${
                  overallRisk === "critical"
                    ? "text-red-500"
                    : overallRisk === "high"
                      ? "text-orange-500"
                      : overallRisk === "medium"
                        ? "text-yellow-500"
                        : "text-blue-500"
                }`}
              >
                {overallRisk?.charAt(0).toUpperCase() + overallRisk?.slice(1)}
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Services Detected:</span>
                  <span className="text-white font-medium">{findings.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Unauthorized:</span>
                  <span className="text-red-400 font-medium">{unauthorizedFindings}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Authorized:</span>
                  <span className="text-green-400 font-medium">{authorizedFindings}</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3">Summary Stats</h3>
              <div className="space-y-3">
                {findings
                  .reduce((acc: Record<string, number>, f) => {
                    acc[f.risk] = (acc[f.risk] || 0) + 1;
                    return acc;
                  }, {})
                  .toString()
                  .split(",")
                  .map((item, idx) => {
                    const [risk, count] = item.split(":");
                    return (
                      <div key={idx} className="flex justify-between text-sm">
                        <span className="capitalize text-gray-400">{risk}</span>
                        <span
                          className={
                            risk === "critical"
                              ? "text-red-400"
                              : risk === "high"
                                ? "text-orange-400"
                                : risk === "medium"
                                  ? "text-yellow-400"
                                  : "text-blue-400"
                          }
                        >
                          {count}
                        </span>
                      </div>
                    );
                  })}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Findings Table */}
      {findings.length > 0 && (
        <div className="mt-8 bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="p-6 border-b border-gray-700">
            <h3 className="text-xl font-semibold text-white">Detected Services</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700 bg-gray-900/50">
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">
                    Service
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">
                    Risk
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">
                    Evidence
                  </th>
                  <th className="px-6 py-3 text-center text-sm font-semibold text-gray-300">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {findings.map((finding, idx) => (
                  <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700/30">
                    <td className="px-6 py-4 text-white font-medium">{finding.service}</td>
                    <td className="px-6 py-4 text-gray-400 text-sm">{finding.category}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${riskBadge(finding.risk)}`}
                      >
                        {finding.risk.charAt(0).toUpperCase() + finding.risk.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-300 text-sm max-w-sm truncate">
                      {finding.evidence}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <button
                        className={`px-3 py-1 rounded-lg text-xs font-medium ${
                          finding.authorized
                            ? "bg-green-900/30 text-green-400 border border-green-800"
                            : "bg-blue-900/30 text-blue-400 border border-blue-800 hover:bg-blue-900/50"
                        }`}
                      >
                        {finding.authorized ? "✓ Authorized" : "Mark Authorized"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {findings.length === 0 && !scanning && input && (
        <div className="mt-8 bg-gray-800 rounded-xl p-6 border border-gray-700 text-center">
          <p className="text-gray-400">No unauthorized AI services detected in the input.</p>
        </div>
      )}
    </div>
  );
}
