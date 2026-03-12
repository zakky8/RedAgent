"use client";

import React, { useState } from "react";
import useSWR from "swr";
import { Card, CardContent, CardHeader } from "@/components/Card";
import Badge from "@/components/Badge";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Skeleton from "@/components/Skeleton";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { Agent } from "@/types";

export default function AgentsPage() {
  const { data: agents, isLoading } = useSWR<Agent[]>(
    "/api/v1/agents?limit=100",
    (url) => api.get(url),
    { revalidateOnFocus: false, dedupingInterval: 30000 }
  );

  const [isCreating, setIsCreating] = useState(false);
  const [showApiKey, setShowApiKey] = useState<Record<string, boolean>>({});
  const [formData, setFormData] = useState({ name: "", role: "monitor" });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/api/v1/agents", formData);
      setFormData({ name: "", role: "monitor" });
      setIsCreating(false);
    } catch (error) {
      console.error("Error creating agent:", error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Agents</h1>
          <p className="text-gray-400">Manage monitoring and scanning agents</p>
        </div>
        <Button
          variant="primary"
          onClick={() => setIsCreating(!isCreating)}
        >
          {isCreating ? "Cancel" : "Create Agent"}
        </Button>
      </div>

      {/* Create Form */}
      {isCreating && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-white">Create New Agent</h3>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="space-y-4">
              <Input
                label="Agent Name"
                placeholder="e.g., Production Monitor"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
              />
              <div>
                <label className="block text-sm font-medium text-gray-200 mb-2">
                  Role
                </label>
                <select
                  value={formData.role}
                  onChange={(e) =>
                    setFormData({ ...formData, role: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white"
                  required
                >
                  <option value="monitor">Monitor</option>
                  <option value="scanner">Scanner</option>
                  <option value="both">Monitor & Scanner</option>
                </select>
              </div>
              <Button type="submit" variant="primary" className="w-full">
                Create Agent
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Agents List */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : agents && agents.length > 0 ? (
        <div className="space-y-4">
          {agents.map((agent) => (
            <Card key={agent.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      {agent.name}
                    </h3>
                    <p className="text-sm text-gray-400 mt-1">
                      {agent.id}
                    </p>
                  </div>
                  <Badge variant={agent.status === "active" ? "success" : "secondary"}>
                    {agent.status}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-xs text-gray-400 mb-1">Role</p>
                    <p className="text-white font-medium">
                      {agent.role.charAt(0).toUpperCase() + agent.role.slice(1)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400 mb-1">Last Seen</p>
                    <p className="text-white font-medium">
                      {agent.last_seen_at ? formatDate(agent.last_seen_at) : "Never"}
                    </p>
                  </div>
                </div>

                {/* API Key */}
                <div className="mb-4 p-3 bg-gray-800/30 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xs text-gray-400">API Key</p>
                    <button
                      onClick={() =>
                        setShowApiKey({
                          ...showApiKey,
                          [agent.id]: !showApiKey[agent.id],
                        })
                      }
                      className="text-xs text-red-400 hover:text-red-300"
                    >
                      {showApiKey[agent.id] ? "Hide" : "Show"}
                    </button>
                  </div>
                  <code className="text-xs text-gray-400 break-all">
                    {showApiKey[agent.id]
                      ? agent.api_key
                      : agent.api_key.slice(0, 20) + "..."}
                  </code>
                </div>

                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    Configure
                  </Button>
                  <Button variant="ghost" size="sm" className="flex-1">
                    View Logs
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-gray-400 mb-4">No agents yet</p>
            <Button variant="primary" onClick={() => setIsCreating(true)}>
              Create First Agent
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Integration Guide */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-white">Integration Guide</h3>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm text-gray-300 mb-2">Install the SDK:</p>
            <pre className="bg-gray-800/50 p-3 rounded text-xs text-gray-300 overflow-x-auto">
              pip install agentred-sdk
            </pre>
          </div>
          <div>
            <p className="text-sm text-gray-300 mb-2">Initialize monitoring:</p>
            <pre className="bg-gray-800/50 p-3 rounded text-xs text-gray-300 overflow-x-auto">
{`from agentred import Monitor

monitor = Monitor(api_key="your_api_key")
monitor.track_request(prompt, response)`}
            </pre>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
