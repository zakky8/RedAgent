"use client";
import { useState } from "react";
import { Download } from "lucide-react";

interface RiskSummary {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

interface Vulnerability {
  package: string;
  version: string;
  cve: string;
  severity: "critical" | "high" | "medium" | "low";
  description: string;
}

interface SBOMResult {
  risk_summary: RiskSummary;
  vulnerabilities: Vulnerability[];
  sbom_id: string;
  timestamp: string;
}

export default function SBOMPage() {
  const [systemName, setSystemName] = useState("");
  const [version, setVersion] = useState("1.0.0");
  const [requirements, setRequirements] = useState("");
  const [sbomResult, setSbomResult] = useState<SBOMResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerate() {
    if (!systemName || !requirements) {
      setError("Please fill in all required fields");
      return;
    }

    setError("");
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch("/api/v1/sbom/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          system_name: systemName,
          version: version,
          requirements_content: requirements,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setSbomResult(data);
      } else {
        setError("Failed to generate SBOM. Please check your input and try again.");
      }
    } catch (err) {
      setError(
        "Error generating SBOM. " + (err instanceof Error ? err.message : "Unknown error")
      );
    } finally {
      setLoading(false);
    }
  }

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
        <h1 className="text-3xl font-bold text-white mb-2">SBOM Generator</h1>
        <p className="text-gray-400">Generate Software Bill of Materials and analyze supply chain risks</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h2 className="text-xl font-semibold text-white mb-6">AI System Details</h2>
          <div className="space-y-4">
            <div>
              <label className="text-gray-400 text-sm block mb-2 font-medium">
                System Name *
              </label>
              <input
                type="text"
                value={systemName}
                onChange={(e) => setSystemName(e.target.value)}
                placeholder="e.g., MyAIAgent, LangChain App"
                className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-red-500"
              />
            </div>

            <div>
              <label className="text-gray-400 text-sm block mb-2 font-medium">
                Version
              </label>
              <input
                type="text"
                value={version}
                onChange={(e) => setVersion(e.target.value)}
                placeholder="1.0.0"
                className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-red-500"
              />
            </div>

            <div>
              <label className="text-gray-400 text-sm block mb-2 font-medium">
                requirements.txt Content *
              </label>
              <textarea
                rows={10}
                value={requirements}
                onChange={(e) => setRequirements(e.target.value)}
                placeholder={`openai==1.30.0
langchain==0.2.0
anthropic==0.28.0
pydantic==2.0.0
requests==2.31.0`}
                className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-3 text-white font-mono text-sm placeholder-gray-500 focus:outline-none focus:border-red-500"
              />
            </div>

            {error && <p className="text-red-400 text-sm">{error}</p>}

            <button
              onClick={handleGenerate}
              disabled={!systemName || !requirements || loading}
              className="w-full bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white py-3 rounded-lg font-medium transition-colors"
            >
              {loading ? "Generating SBOM..." : "Generate SBOM"}
            </button>
          </div>
        </div>

        {/* Results Section */}
        {sbomResult && (
          <div className="space-y-4">
            {/* Risk Summary Card */}
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">Risk Summary</h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-900 rounded-lg p-4 border border-red-800/30">
                  <div className="text-3xl font-bold text-red-500">
                    {sbomResult.risk_summary.critical}
                  </div>
                  <div className="text-gray-400 text-xs mt-1 font-medium">Critical</div>
                </div>
                <div className="bg-gray-900 rounded-lg p-4 border border-orange-800/30">
                  <div className="text-3xl font-bold text-orange-500">
                    {sbomResult.risk_summary.high}
                  </div>
                  <div className="text-gray-400 text-xs mt-1 font-medium">High</div>
                </div>
                <div className="bg-gray-900 rounded-lg p-4 border border-yellow-800/30">
                  <div className="text-3xl font-bold text-yellow-500">
                    {sbomResult.risk_summary.medium}
                  </div>
                  <div className="text-gray-400 text-xs mt-1 font-medium">Medium</div>
                </div>
                <div className="bg-gray-900 rounded-lg p-4 border border-blue-800/30">
                  <div className="text-3xl font-bold text-blue-400">
                    {sbomResult.risk_summary.low}
                  </div>
                  <div className="text-gray-400 text-xs mt-1 font-medium">Low</div>
                </div>
              </div>
            </div>

            {/* Export Options */}
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">Export SBOM</h3>
              <div className="space-y-2">
                <a
                  href={`/api/v1/sbom/${sbomResult.sbom_id}/export?format=cyclonedx`}
                  className="flex items-center justify-between w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  <span className="font-medium">CycloneDX (JSON)</span>
                  <Download size={18} />
                </a>
                <a
                  href={`/api/v1/sbom/${sbomResult.sbom_id}/export?format=spdx`}
                  className="flex items-center justify-between w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                >
                  <span className="font-medium">SPDX (JSON)</span>
                  <Download size={18} />
                </a>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Vulnerabilities Table */}
      {sbomResult && sbomResult.vulnerabilities.length > 0 && (
        <div className="mt-8 bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="p-6 border-b border-gray-700">
            <h3 className="text-xl font-semibold text-white">
              Detected Vulnerabilities ({sbomResult.vulnerabilities.length})
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700 bg-gray-900/50">
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">
                    Package
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">
                    Version
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">
                    CVE
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">
                    Severity
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">
                    Description
                  </th>
                </tr>
              </thead>
              <tbody>
                {sbomResult.vulnerabilities.map((vuln, idx) => (
                  <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700/30">
                    <td className="px-6 py-4 text-white font-medium text-sm">{vuln.package}</td>
                    <td className="px-6 py-4 text-gray-400 text-sm font-mono">
                      {vuln.version}
                    </td>
                    <td className="px-6 py-4 text-gray-400 text-sm font-mono">{vuln.cve}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${severityBadge(vuln.severity)}`}
                      >
                        {vuln.severity.charAt(0).toUpperCase() + vuln.severity.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-300 text-sm max-w-sm">
                      {vuln.description}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {sbomResult && sbomResult.vulnerabilities.length === 0 && (
        <div className="mt-8 bg-green-900/20 border border-green-600/30 rounded-xl p-6 text-center">
          <p className="text-green-400 font-medium">
            ✓ No known vulnerabilities detected in the dependencies.
          </p>
        </div>
      )}
    </div>
  );
}
