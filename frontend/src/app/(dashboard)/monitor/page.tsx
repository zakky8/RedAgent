"use client";

import React, { useState } from "react";
import useSWR from "swr";
import { Card, CardContent, CardHeader } from "@/components/Card";
import Badge from "@/components/Badge";
import Button from "@/components/Button";
import Skeleton from "@/components/Skeleton";
import { api } from "@/lib/api";
import { formatDateTime } from "@/lib/utils";
import type { MonitoringSession, MonitoringAlert } from "@/types";

export default function MonitorPage() {
  const { data: sessions, isLoading } = useSWR<MonitoringSession[]>(
    "/api/v1/monitoring/sessions?limit=50",
    (url) => api.get(url),
    { revalidateOnFocus: false, dedupingInterval: 10000 }
  );

  const [selectedSession, setSelectedSession] = useState<MonitoringSession | null>(null);
  const [filterStatus, setFilterStatus] = useState<"all" | "active" | "paused" | "completed">("all");

  const filteredSessions = sessions?.filter((s) => {
    if (filterStatus === "all") return true;
    return s.status === filterStatus;
  }) || [];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "text-red-500 bg-red-500/10";
      case "high":
        return "text-orange-500 bg-orange-500/10";
      case "medium":
        return "text-yellow-500 bg-yellow-500/10";
      case "low":
        return "text-blue-500 bg-blue-500/10";
      default:
        return "text-gray-500 bg-gray-500/10";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Monitoring</h1>
        <p className="text-gray-400">Real-time monitoring of AI system security</p>
      </div>

      {/* Active Sessions Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          {
            label: "Active Sessions",
            value: sessions?.filter((s) => s.status === "active").length || 0,
            icon: "🟢",
          },
          {
            label: "Critical Alerts",
            value: sessions?.reduce((acc, s) => acc + (s.alerts?.filter((a) => a.severity === "critical").length || 0), 0) || 0,
            icon: "🔴",
          },
          {
            label: "Total Requests",
            value: sessions?.reduce((acc, s) => acc + (Object.keys(s.metrics || {}).length || 0), 0) || 0,
            icon: "📊",
          },
          {
            label: "Threat Score",
            value: "4.2/10",
            icon: "⚠️",
          },
        ].map((stat, idx) => (
          <Card key={idx}>
            <CardContent className="pt-6">
              <p className="text-gray-400 text-sm mb-2">{stat.label}</p>
              <p className="text-3xl font-bold text-white">{stat.value}</p>
              <p className="text-2xl mt-2">{stat.icon}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filter */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2">
            <p className="text-sm text-gray-400">Filter:</p>
            <div className="flex gap-2">
              {["all", "active", "paused", "completed"].map((status) => (
                <button
                  key={status}
                  onClick={() => setFilterStatus(status as any)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    filterStatus === status
                      ? "bg-red-600 text-white"
                      : "bg-gray-800 text-gray-300 hover:bg-gray-700"
                  }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sessions List */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      ) : filteredSessions.length > 0 ? (
        <div className="space-y-3">
          {filteredSessions.map((session) => (
            <Card
              key={session.id}
              className="cursor-pointer hover:border-red-600/30 transition-all"
              onClick={() => setSelectedSession(session)}
            >
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-2">
                      {session.name}
                    </h3>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-400">Agent</p>
                        <p className="text-gray-300">{session.agent_id.slice(0, 12)}...</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Started</p>
                        <p className="text-gray-300">{formatDateTime(session.start_time)}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Alerts</p>
                        <p className="text-white font-medium">
                          {session.alerts?.length || 0}
                        </p>
                      </div>
                    </div>
                  </div>
                  <Badge
                    variant={
                      session.status === "active"
                        ? "info"
                        : session.status === "paused"
                        ? "warning"
                        : "secondary"
                    }
                  >
                    {session.status}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-gray-400 mb-4">No monitoring sessions yet</p>
            <Button variant="primary">Start Monitoring</Button>
          </CardContent>
        </Card>
      )}

      {/* Session Detail */}
      {selectedSession && (
        <Card>
          <CardHeader className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">
              Session: {selectedSession.name}
            </h3>
            <button
              onClick={() => setSelectedSession(null)}
              className="text-gray-400 hover:text-gray-300"
            >
              ✕
            </button>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Alerts */}
            <div>
              <h4 className="text-white font-medium mb-3">Alerts</h4>
              {selectedSession.alerts && selectedSession.alerts.length > 0 ? (
                <div className="space-y-2">
                  {selectedSession.alerts.map((alert) => (
                    <div
                      key={alert.id}
                      className={`p-3 rounded-lg border border-gray-700 ${getSeverityColor(alert.severity)}`}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium">{alert.message}</p>
                          <p className="text-xs opacity-75 mt-1">
                            {formatDateTime(alert.timestamp)}
                          </p>
                        </div>
                        <Badge
                          variant={
                            alert.severity === "critical"
                              ? "destructive"
                              : alert.severity === "high"
                              ? "warning"
                              : alert.severity === "medium"
                              ? "warning"
                              : "info"
                          }
                        >
                          {alert.severity}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 text-sm">No alerts</p>
              )}
            </div>

            {/* Metrics */}
            <div>
              <h4 className="text-white font-medium mb-3">Metrics</h4>
              <div className="grid grid-cols-2 gap-4">
                {selectedSession.metrics &&
                  Object.entries(selectedSession.metrics).map(([key, value]) => (
                    <div
                      key={key}
                      className="p-3 rounded-lg bg-gray-800/30 border border-gray-700"
                    >
                      <p className="text-xs text-gray-400 mb-1">{key}</p>
                      <p className="text-white font-medium">
                        {typeof value === "number"
                          ? value.toFixed(2)
                          : String(value)}
                      </p>
                    </div>
                  ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
