"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import useSWR from "swr";
import { Card, CardContent, CardHeader } from "@/components/Card";
import Badge from "@/components/Badge";
import Button from "@/components/Button";
import LoadingSpinner from "@/components/LoadingSpinner";
import Skeleton from "@/components/Skeleton";
import { api } from "@/lib/api";
import { formatDateTime, formatDuration } from "@/lib/utils";
import type { Scan, AttackResult } from "@/types";

export default function ScanDetailPage() {
  const params = useParams();
  const scanId = params.id as string;

  const { data: scan, isLoading: scanLoading } = useSWR<Scan>(
    `/api/v1/scans/${scanId}`,
    (url) => api.get(url),
    { revalidateOnFocus: false, dedupingInterval: 5000 }
  );

  const { data: results, isLoading: resultsLoading } = useSWR<AttackResult[]>(
    scan?.status === "completed" ? `/api/v1/scans/${scanId}/results` : null,
    (url) => api.get(url),
    { revalidateOnFocus: false, dedupingInterval: 10000 }
  );

  const [selectedResult, setSelectedResult] = useState<AttackResult | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<"all" | "critical" | "high" | "medium" | "low">("all");

  const filteredResults = results?.filter((r) => {
    if (filterSeverity === "all") return true;
    return r.severity === filterSeverity;
  }) || [];

  const duration = scan
    ? new Date(scan.completed_at || new Date()).getTime() -
      new Date(scan.started_at || new Date()).getTime()
    : 0;

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return "🔴";
      case "high":
        return "🟠";
      case "medium":
        return "🟡";
      case "low":
        return "🔵";
      default:
        return "⚪";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Scan Details</h1>
        <p className="text-gray-400">
          {scanId.slice(0, 12)}...
        </p>
      </div>

      {/* Scan Overview */}
      {scanLoading ? (
        <Skeleton className="h-32" />
      ) : scan ? (
        <Card>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div>
                <p className="text-gray-400 text-sm mb-2">Status</p>
                <Badge
                  variant={
                    scan.status === "completed"
                      ? "success"
                      : scan.status === "running"
                      ? "info"
                      : scan.status === "failed"
                      ? "destructive"
                      : "secondary"
                  }
                >
                  {scan.status.charAt(0).toUpperCase() + scan.status.slice(1)}
                </Badge>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-2">Progress</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-800 rounded-full h-2">
                    <div
                      className="bg-red-600 h-2 rounded-full transition-all"
                      style={{
                        width: `${
                          scan.attack_count > 0
                            ? (scan.completed_count / scan.attack_count) * 100
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                  <span className="text-sm text-white font-medium">
                    {scan.completed_count}/{scan.attack_count}
                  </span>
                </div>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-2">Risk Score</p>
                <p className="text-2xl font-bold text-white">
                  {scan.risk_score !== null ? scan.risk_score.toFixed(1) : "—"}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-2">Duration</p>
                <p className="text-white font-medium">
                  {duration > 0 ? formatDuration(duration) : "In progress"}
                </p>
              </div>
            </div>

            {/* Findings Summary */}
            <div className="mt-6 pt-6 border-t border-gray-800 grid grid-cols-5 gap-4">
              {[
                {
                  label: "Critical",
                  value: scan.critical_count,
                  color: "text-red-500",
                },
                {
                  label: "High",
                  value: scan.high_count,
                  color: "text-orange-500",
                },
                {
                  label: "Medium",
                  value: scan.medium_count,
                  color: "text-yellow-500",
                },
                { label: "Low", value: scan.low_count, color: "text-blue-500" },
                {
                  label: "Total",
                  value: scan.critical_count +
                    scan.high_count +
                    scan.medium_count +
                    scan.low_count,
                  color: "text-white",
                },
              ].map((item) => (
                <div key={item.label} className="text-center">
                  <p className={`text-2xl font-bold ${item.color}`}>
                    {item.value}
                  </p>
                  <p className="text-xs text-gray-400">{item.label}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}

      {/* Live Feed / Results */}
      {scan?.status === "running" ? (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-white">
              Live Attack Feed
            </h3>
          </CardHeader>
          <CardContent className="h-64 flex items-center justify-center">
            <div className="text-center">
              <LoadingSpinner size="lg" />
              <p className="text-gray-400 mt-4">
                Scan in progress... Attacks completing
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Filter */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2">
                <p className="text-sm text-gray-400">Filter by severity:</p>
                <div className="flex gap-2">
                  {[
                    { label: "All", value: "all" },
                    { label: "Critical", value: "critical" },
                    { label: "High", value: "high" },
                    { label: "Medium", value: "medium" },
                    { label: "Low", value: "low" },
                  ].map((f) => (
                    <button
                      key={f.value}
                      onClick={() =>
                        setFilterSeverity(f.value as any)
                      }
                      className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                        filterSeverity === f.value
                          ? "bg-red-600 text-white"
                          : "bg-gray-800 text-gray-300 hover:bg-gray-700"
                      }`}
                    >
                      {f.label}
                    </button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Results Table */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-white">
                Attack Results ({filteredResults.length})
              </h3>
            </CardHeader>
            <CardContent>
              {resultsLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : filteredResults.length > 0 ? (
                <div className="space-y-3">
                  {filteredResults.map((result) => (
                    <div
                      key={result.id}
                      onClick={() => setSelectedResult(result)}
                      className="p-4 rounded-lg border border-gray-800 hover:border-red-600/50 hover:bg-gray-900/50 cursor-pointer transition-all"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-2xl">
                              {getSeverityIcon(result.severity)}
                            </span>
                            <div>
                              <h4 className="text-white font-medium">
                                {result.attack_name}
                              </h4>
                              <p className="text-xs text-gray-400">
                                {result.category}
                              </p>
                            </div>
                          </div>
                        </div>
                        <Badge
                          variant={
                            result.severity === "critical"
                              ? "destructive"
                              : result.severity === "high"
                              ? "warning"
                              : result.severity === "medium"
                              ? "warning"
                              : "info"
                          }
                        >
                          {result.severity}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-400 mt-2">
                        {result.evidence}
                      </p>
                      <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                        <span>Confidence: {(result.confidence * 100).toFixed(0)}%</span>
                        <span>
                          {result.success ? "✓ Successful" : "Failed"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-400 py-8">
                  No results found
                </p>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Result Detail Drawer */}
      {selectedResult && (
        <div className="fixed inset-0 z-40 flex">
          {/* Overlay */}
          <div
            className="flex-1 bg-black/30"
            onClick={() => setSelectedResult(null)}
          />

          {/* Drawer */}
          <div className="w-96 bg-gray-900 border-l border-gray-800 overflow-y-auto">
            <div className="p-6 space-y-6">
              <div className="flex items-start justify-between">
                <h3 className="text-lg font-semibold text-white">
                  Result Details
                </h3>
                <button
                  onClick={() => setSelectedResult(null)}
                  className="text-gray-400 hover:text-gray-300"
                >
                  ✕
                </button>
              </div>

              {/* Attack Info */}
              <div>
                <p className="text-xs text-gray-400 mb-1">Attack</p>
                <p className="text-white font-medium">
                  {selectedResult.attack_name}
                </p>
              </div>

              {/* Severity */}
              <div>
                <p className="text-xs text-gray-400 mb-1">Severity</p>
                <Badge variant="destructive">
                  {selectedResult.severity}
                </Badge>
              </div>

              {/* Payload */}
              <div>
                <p className="text-xs text-gray-400 mb-2">Payload</p>
                <pre className="bg-gray-800/50 p-3 rounded text-xs text-gray-300 overflow-x-auto">
                  {selectedResult.payload}
                </pre>
              </div>

              {/* Response */}
              <div>
                <p className="text-xs text-gray-400 mb-2">Response</p>
                <pre className="bg-gray-800/50 p-3 rounded text-xs text-gray-300 overflow-x-auto">
                  {selectedResult.response_snippet}
                </pre>
              </div>

              {/* Remediation */}
              <div>
                <p className="text-xs text-gray-400 mb-1">Remediation</p>
                <p className="text-sm text-gray-300">
                  {selectedResult.remediation}
                </p>
              </div>

              {/* Framework Mappings */}
              <div>
                <p className="text-xs text-gray-400 mb-2">Framework Mappings</p>
                <div className="space-y-2">
                  {Object.entries(selectedResult.framework_mapping).map(
                    ([key, value]) => (
                      <div key={key} className="text-xs">
                        <span className="text-gray-400">{key}:</span>
                        <span className="text-gray-300 ml-2">{value}</span>
                      </div>
                    )
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
