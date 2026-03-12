"use client";
import { useState, useEffect } from "react";
import { X, Eye, EyeOff, Trash2, Check } from "lucide-react";

const INTEGRATION_TYPES = [
  {
    id: "splunk",
    name: "Splunk",
    icon: "🔴",
    description: "Send findings to Splunk SIEM",
    fields: [
      { key: "hec_url", label: "HEC URL", type: "url", required: true },
      { key: "token", label: "HEC Token", type: "password", required: true },
      { key: "index", label: "Index Name", type: "text", required: true },
    ],
  },
  {
    id: "jira",
    name: "Jira",
    icon: "🔵",
    description: "Create Jira tickets for critical findings",
    fields: [
      { key: "base_url", label: "Base URL", type: "url", required: true },
      { key: "email", label: "Email", type: "email", required: true },
      { key: "api_token", label: "API Token", type: "password", required: true },
      { key: "project_key", label: "Project Key", type: "text", required: true },
    ],
  },
  {
    id: "github",
    name: "GitHub",
    icon: "⚫",
    description: "Create GitHub Issues / Security Advisories",
    fields: [
      { key: "token", label: "Personal Access Token", type: "password", required: true },
      { key: "repo_owner", label: "Repository Owner", type: "text", required: true },
      { key: "repo_name", label: "Repository Name", type: "text", required: true },
    ],
  },
  {
    id: "elastic",
    name: "Elastic",
    icon: "🟡",
    description: "Index findings in Elasticsearch",
    fields: [
      { key: "host", label: "Elasticsearch Host", type: "url", required: true },
      { key: "api_key", label: "API Key", type: "password", required: true },
      { key: "index", label: "Index Name", type: "text", required: true },
    ],
  },
  {
    id: "sentinel",
    name: "Microsoft Sentinel",
    icon: "🔷",
    description: "Send to Azure Sentinel Log Analytics",
    fields: [
      { key: "workspace_id", label: "Workspace ID", type: "text", required: true },
      { key: "shared_key", label: "Shared Key", type: "password", required: true },
    ],
  },
  {
    id: "webhook",
    name: "Webhook",
    icon: "🔗",
    description: "Generic webhook for any system",
    fields: [
      { key: "url", label: "Webhook URL", type: "url", required: true },
      { key: "secret", label: "Secret (optional)", type: "password", required: false },
    ],
  },
];

interface Integration {
  id: string;
  type: string;
  name: string;
  connected: boolean;
  lastTest?: string;
  fields: Record<string, string>;
}

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [selectedType, setSelectedType] = useState<(typeof INTEGRATION_TYPES)[0] | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>({});
  const [testing, setTesting] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchIntegrations();
  }, []);

  async function fetchIntegrations() {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch("/api/v1/integrations", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setIntegrations(data.integrations || []);
    } catch (error) {
      console.error("Failed to fetch integrations:", error);
    }
  }

  function openConfigModal(type: typeof INTEGRATION_TYPES[0]) {
    setSelectedType(type);
    const existing = integrations.find((i) => i.type === type.id);
    setFormData(existing ? existing.fields : {});
    setShowModal(true);
  }

  async function saveIntegration() {
    if (!selectedType) return;
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch("/api/v1/integrations", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          type: selectedType.id,
          config: formData,
        }),
      });
      if (res.ok) {
        await fetchIntegrations();
        setShowModal(false);
        setFormData({});
      }
    } catch (error) {
      console.error("Failed to save integration:", error);
    } finally {
      setLoading(false);
    }
  }

  async function testIntegration(id: string) {
    setTesting(id);
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`/api/v1/integrations/${id}/test`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        alert("Test failed");
      }
    } catch (error) {
      console.error("Test failed:", error);
      alert("Test failed");
    } finally {
      setTesting(null);
    }
  }

  async function deleteIntegration(id: string) {
    if (!confirm("Delete this integration?")) return;
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`/api/v1/integrations/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        await fetchIntegrations();
      }
    } catch (error) {
      console.error("Failed to delete:", error);
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Integrations</h1>
        <p className="text-gray-400">Connect AgentRed with your security tools and platforms</p>
      </div>

      {/* Integration Types Grid */}
      <div className="mb-12">
        <h2 className="text-xl font-semibold text-white mb-4">Available Integrations</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {INTEGRATION_TYPES.map((type) => {
            const isConnected = integrations.some((i) => i.type === type.id);
            return (
              <div
                key={type.id}
                className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-gray-600 transition-colors"
              >
                <div className="text-4xl mb-3">{type.icon}</div>
                <h3 className="text-white font-semibold text-lg">{type.name}</h3>
                <p className="text-gray-400 text-sm mt-2 mb-4 min-h-10">{type.description}</p>
                <button
                  onClick={() => openConfigModal(type)}
                  className={`w-full py-2 rounded-lg font-medium text-sm transition-colors ${
                    isConnected
                      ? "bg-green-600 hover:bg-green-700 text-white"
                      : "bg-red-600 hover:bg-red-700 text-white"
                  }`}
                >
                  {isConnected ? "✓ Configured" : "Configure"}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Connected Integrations Table */}
      {integrations.length > 0 && (
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-xl font-semibold text-white">Connected Integrations</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700 bg-gray-900/50">
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">Name</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">Type</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">Status</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-300">Last Test</th>
                  <th className="px-6 py-3 text-right text-sm font-semibold text-gray-300">Actions</th>
                </tr>
              </thead>
              <tbody>
                {integrations.map((integration) => (
                  <tr key={integration.id} className="border-b border-gray-700 hover:bg-gray-700/30">
                    <td className="px-6 py-4 text-white font-medium">{integration.name}</td>
                    <td className="px-6 py-4 text-gray-400">
                      {INTEGRATION_TYPES.find((t) => t.id === integration.type)?.name}
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-block px-3 py-1 bg-green-900/30 text-green-400 rounded-full text-xs font-medium">
                        Connected
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-400 text-sm">
                      {integration.lastTest || "Never"}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => testIntegration(integration.id)}
                        disabled={testing === integration.id}
                        className="px-3 py-1 text-sm bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg mr-2"
                      >
                        {testing === integration.id ? "Testing..." : "Test"}
                      </button>
                      <button
                        onClick={() => deleteIntegration(integration.id)}
                        className="px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded-lg"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Configuration Modal */}
      {showModal && selectedType && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-xl border border-gray-700 max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-700 sticky top-0 bg-gray-800">
              <h3 className="text-xl font-bold text-white">Configure {selectedType.name}</h3>
              <button
                onClick={() => {
                  setShowModal(false);
                  setFormData({});
                }}
                className="text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>

            <div className="p-6 space-y-4">
              {selectedType.fields.map((field) => (
                <div key={field.key}>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    {field.label}
                    {field.required && <span className="text-red-500">*</span>}
                  </label>
                  <div className="relative">
                    <input
                      type={
                        field.type === "password"
                          ? showPasswords[field.key]
                            ? "text"
                            : "password"
                          : field.type
                      }
                      value={formData[field.key] || ""}
                      onChange={(e) =>
                        setFormData({ ...formData, [field.key]: e.target.value })
                      }
                      className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-red-500"
                    />
                    {field.type === "password" && (
                      <button
                        type="button"
                        onClick={() =>
                          setShowPasswords({
                            ...showPasswords,
                            [field.key]: !showPasswords[field.key],
                          })
                        }
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-300"
                      >
                        {showPasswords[field.key] ? <EyeOff size={18} /> : <Eye size={18} />}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="p-6 border-t border-gray-700 flex gap-3">
              <button
                onClick={() => {
                  setShowModal(false);
                  setFormData({});
                }}
                className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={saveIntegration}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white rounded-lg font-medium"
              >
                {loading ? "Saving..." : "Save"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
