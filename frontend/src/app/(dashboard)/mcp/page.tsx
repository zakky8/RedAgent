"use client";
import { useState } from "react";

const MCP_RISK_CATEGORIES = [
  "Tool Poisoning",
  "Rug Pull",
  "SSE Injection",
  "Excessive Permissions",
  "Unvalidated Input",
  "Secret Exposure",
  "Confused Deputy",
  "Resource Exhaustion",
  "Cross-Context Leak",
  "Auth Bypass",
  "Schema Confusion",
  "Indirect Injection",
  "Callback Hijack",
  "Version Downgrade",
];

interface ScanResult {
  serverUrl: string;
  riskScore: number;
  findings: Array<{
    category: string;
    severity: "critical" | "high" | "medium" | "low";
    description: string;
    recommendation: string;
  }>;
}

export default function MCPScannerPage() {
  const [serverUrl, setServerUrl] = useState("");
  const [transport, setTransport] = useState("sse");
  const [scanning, setScanning] = useState(false);
  const [results, setResults] = useState<ScanResult | null>(null);
  const [checkedCategories, setCheckedCategories] = useState<string[]>([]);
  const [error, setError] = useState("");

  async function startScan() {
    if (!serverUrl) {
      setError("Please enter a server URL");
      return;
    }

    setError("");
    setScanning(true);
    setCheckedCategories([]);
    setResults(null);

    try {
      // Simulate scanning through categories
      for (let i = 0; i < MCP_RISK_CATEGORIES.length; i++) {
        await new Promise((resolve) => setTimeout(resolve, 200));
        setCheckedCategories((prev) => [...prev, MCP_RISK_CATEGORIES[i]]);
      }

      // Call actual API
      const token = localStorage.getItem("access_token");
      const res = await fetch("/api/v1/mcp/scan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          server_url: serverUrl,
          transport: transport,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setResults(data);
      } else {
        setError("Scan failed. Please check the URL and try again.");
      }
    } catch (err) {
      setError(
        "Error connecting to MCP server. " +
          (err instanceof Error ? err.message : "Unknown error")
      );
    } finally {
      setScanning(false);
    }
  }

  const riskColor = (score: number) => {
    if (score >= 80) return "text-red-500";
    if (score >= 60) return "text-orange-500";
    if (score >= 40) return "text-yellow-500";
    return "text-green-500";
  };

  const severityBadge = (severity: string) => {
    const colors = {
      critical: "bg-red-900/30 text-red-400 border border-red-800",
      high: "bg-orange-900/30 text-orange-400 border border-orange-800",
      medium: "bg-yellow-900/30 text-yellow-400 border border-yellow-800",
      low: "bg-blue-900/30 text-blue-400 border border-blue-800",
    };
    return colors[severity as keyof typeof colors] || colors.low;
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">MCP Deep Scanner</h1>
        <p className="text-gray-400">Scan MCP servers for security vulnerabilities across 14 risk categories</p>
      </div>

      {/* Configuration Section */}
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">Scan Configuration</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="text-gray-400 text-sm mb-2 block font-medium">
              MCP Server URL
            </label>
            <input
              type="url"
              value={serverUrl}
              onChange={(e) => {
                setServerUrl(e.target.value);
                setError("");
              }}
              placeholder="https://mcp-server.example.com or stdio://path/to/binary"
              disabled={scanning}
              className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-red-500 disabled:opacity-50"
            />
          </div>
          <div>
            <label className="text-gray-400 text-sm mb-2 block font-medium">
              Transport Protocol
            </label>
            <select
              value={transport}
              onChange={(e) => setTransport(e.target.value)}
              disabled={scanning}
              className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-red-500 disabled:opacity-50"
            >
              <option value="sse">SSE (HTTP)</option>
              <option value="stdio">stdio</option>
              <option value="http">HTTP</option>
            </select>
          </div>
        </div>

        {error && <p className="text-red-400 text-sm mt-3">{error}</p>}

        <button
          onClick={startScan}
          disabled={!serverUrl || scanning}
          className="mt-4 w-full md:w-auto bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white px-8 py-3 rounded-lg font-medium transition-colors"
        >
          {scanning ? "Scanning..." : "Start Deep Scan"}
        </button>
      </div>

      {/* Risk Categories Checklist */}
      {(scanning || checkedCategories.length > 0) && (
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-8">
          <h3 className="text-lg font-semibold text-white mb-4">Scanning Progress</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {MCP_RISK_CATEGORIES.map((cat, i) => (
              <div
                key={i}
                className={`flex items-center gap-2 text-sm p-3 rounded-lg border transition-all ${
                  checkedCategories.includes(cat)
                    ? "bg-green-900/20 border-green-600/30 text-green-400"
                    : scanning && i < checkedCategories.length
                      ? "bg-green-900/20 border-green-600/30 text-green-400"
                      : "bg-gray-900/50 border-gray-600/30 text-gray-400"
                }`}
              >
                <span className="font-bold text-lg">
                  {checkedCategories.includes(cat) ? "✓" : "○"}
                </span>
                <span className="font-medium">{cat}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Results Section */}
      {results && (
        <div className="space-y-6">
          {/* Risk Score Card */}
          <div className="bg-gray-800 rounded-xl p-8 border border-gray-700">
            <h3 className="text-gray-400 text-sm font-medium mb-4">Overall Risk Score</h3>
            <div className="flex items-end gap-6">
              <div>
                <div className={`text-6xl font-bold ${riskColor(results.riskScore)}`}>
                  {results.riskScore}
                </div>
                <p className="text-gray-400 text-sm mt-2">out of 100</p>
              </div>
              <div className="flex-1">
                <div className="w-full bg-gray-900 rounded-full h-4 overflow-hidden border border-gray-700">
                  <div
                    className={`h-full transition-all ${
                      results.riskScore >= 80
                        ? "bg-red-600"
                        : results.riskScore >= 60
                          ? "bg-orange-600"
                          : results.riskScore >= 40
                            ? "bg-yellow-600"
                            : "bg-green-600"
                    }`}
                    style={{ width: `${results.riskScore}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Findings Table */}
          {results.findings.length > 0 && (
            <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
              <div className="p-6 border-b border-gray-700">
                <h3 className="text-xl font-semibold text-white">
                  Findings ({results.findings.length})
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-700 bg-gray-900/50">
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">
                        Category
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">
                        Severity
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">
                        Description
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">
                        Recommendation
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.findings.map((finding, idx) => (
                      <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700/30">
                        <td className="px-6 py-4 text-white font-medium text-sm">
                          {finding.category}
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${severityBadge(finding.severity)}`}
                          >
                            {finding.severity.charAt(0).toUpperCase() + finding.severity.slice(1)}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-gray-300 text-sm max-w-xs">
                          {finding.description}
                        </td>
                        <td className="px-6 py-4 text-gray-300 text-sm max-w-sm">
                          {finding.recommendation}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {results.findings.length === 0 && (
            <div className="bg-green-900/20 border border-green-600/30 rounded-xl p-6 text-center">
              <p className="text-green-400 font-medium">
                ✓ No critical issues found. This MCP server appears to be secure.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
