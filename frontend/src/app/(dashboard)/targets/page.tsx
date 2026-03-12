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
import type { Target } from "@/types";

export default function TargetsPage() {
  const { data: targets, isLoading } = useSWR<Target[]>(
    "/api/v1/targets?limit=100",
    (url) => api.get(url),
    { revalidateOnFocus: false, dedupingInterval: 30000 }
  );

  const [isCreating, setIsCreating] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    endpoint_url: "",
    model_type: "",
    provider: "custom",
  });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/api/v1/targets", formData);
      setFormData({ name: "", endpoint_url: "", model_type: "", provider: "custom" });
      setIsCreating(false);
    } catch (error) {
      console.error("Error creating target:", error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Targets</h1>
          <p className="text-gray-400">Manage AI endpoints to test</p>
        </div>
        <Button
          variant="primary"
          onClick={() => setIsCreating(!isCreating)}
        >
          {isCreating ? "Cancel" : "Add Target"}
        </Button>
      </div>

      {/* Create Form */}
      {isCreating && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-white">Add New Target</h3>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="space-y-4">
              <Input
                label="Target Name"
                placeholder="e.g., Production ChatGPT"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
              />
              <Input
                label="API Endpoint"
                type="url"
                placeholder="https://api.openai.com/v1/chat/completions"
                value={formData.endpoint_url}
                onChange={(e) =>
                  setFormData({ ...formData, endpoint_url: e.target.value })
                }
                required
              />
              <div>
                <label className="block text-sm font-medium text-gray-200 mb-2">
                  Model Type
                </label>
                <select
                  value={formData.model_type}
                  onChange={(e) =>
                    setFormData({ ...formData, model_type: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white"
                  required
                >
                  <option value="">Select model...</option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-3.5">GPT-3.5</option>
                  <option value="claude">Claude</option>
                  <option value="mistral">Mistral</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <Button type="submit" variant="primary" className="w-full">
                Create Target
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Targets Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-40" />
          ))}
        </div>
      ) : targets && targets.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {targets.map((target) => (
            <Card key={target.id}>
              <CardContent className="pt-6">
                <h3 className="text-lg font-semibold text-white mb-2">
                  {target.name}
                </h3>
                <div className="space-y-2 text-sm mb-4">
                  <div>
                    <p className="text-gray-400">Model Type</p>
                    <p className="text-gray-300">{target.model_type}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Endpoint</p>
                    <code className="text-xs text-gray-400 break-all">
                      {target.endpoint_url}
                    </code>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Status:</span>
                    <Badge variant={target.is_active ? "success" : "secondary"}>
                      {target.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    Test
                  </Button>
                  <Button variant="ghost" size="sm" className="flex-1">
                    Edit
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-gray-400 mb-4">No targets yet</p>
            <Button variant="primary" onClick={() => setIsCreating(true)}>
              Add First Target
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
