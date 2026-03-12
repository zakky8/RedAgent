"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import useSWR from "swr";
import { Card, CardContent, CardHeader } from "@/components/Card";
import StatsGrid from "@/components/StatsGrid";
import RiskGauge from "@/components/RiskGauge";
import Badge from "@/components/Badge";
import Button from "@/components/Button";
import LoadingSpinner from "@/components/LoadingSpinner";
import Skeleton from "@/components/Skeleton";
import { api } from "@/lib/api";
import { formatDate, formatDateTime } from "@/lib/utils";
import type { Scan, DashboardStats } from "@/types";

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useSWR<DashboardStats>(
    "/api/v1/dashboard/stats",
    (url) => api.get(url),
    { revalidateOnFocus: false, dedupingInterval: 30000 }
  );

  const { data: scans, isLoading: scansLoading } = useSWR<Scan[]>(
    "/api/v1/scans?limit=10&offset=0",
    (url) => api.get(url),
    { revalidateOnFocus: false, dedupingInterval: 30000 }
  );

  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const statCards = [
    {
      label: "Total Scans",
      value: stats?.total_scans || 0,
      icon: "⚡",
      trend: stats ? `${Math.round(stats.total_scans * 0.1)}% this month` : undefined,
      trendDirection: "up" as const,
    },
    {
      label: "Avg Risk Score",
      value: stats?.avg_risk_score ? `${stats.avg_risk_score.toFixed(1)}` : "0",
      icon: "📊",
      trend: stats ? (stats.avg_risk_score > 50 ? "Needs attention" : "Good") : undefined,
      trendDirection: stats && stats.avg_risk_score > 50 ? ("down" as const) : ("up" as const),
    },
    {
      label: "Open Findings",
      value: stats?.open_findings || 0,
      icon: "🔍",
      trend: stats ? `${stats.critical_findings} critical` : undefined,
      trendDirection: "down" as const,
    },
    {
      label: "Compliance Score",
      value: stats?.compliance_score ? `${stats.compliance_score.toFixed(0)}%` : "0%",
      icon: "✓",
      trend: stats ? "Avg across frameworks" : undefined,
      trendDirection: "up" as const,
    },
  ];

  if (!mounted) return null;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-gray-400">
          Real-time overview of your AI security posture
        </p>
      </div>

      {/* Stats Grid */}
      <StatsGrid stats={statCards} isLoading={statsLoading} />

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Score Gauge */}
        <div className="lg:col-span-1">
          <RiskGauge score={stats?.avg_risk_score} isLoading={statsLoading} />
        </div>

        {/* Trend Chart */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-white">Risk Trend (30 days)</h3>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <div className="h-64 flex items-center justify-center">
                  <LoadingSpinner />
                </div>
              ) : (
                <div className="h-64 flex items-end justify-around gap-1">
                  {stats?.trends?.slice(0, 30).map((trend, index) => (
                    <div
                      key={index}
                      className="flex-1 flex flex-col items-center"
                      title={`${trend.date}: ${trend.risk_score.toFixed(1)}`}
                    >
                      <div
                        className="w-full bg-gradient-to-t from-red-600 to-red-500 rounded-t opacity-80 hover:opacity-100 transition-opacity"
                        style={{
                          height: `${Math.max(10, (trend.risk_score / 100) * 100)}px`,
                        }}
                      />
                      <p className="text-xs text-gray-500 mt-2 rotate-0 -rotate-45 text-center">
                        {trend.date.split("-")[2]}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Recent Scans */}
      <Card>
        <CardHeader className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Recent Scans</h3>
          <Link href="/scans">
            <Button variant="outline" size="sm">
              View All
            </Button>
          </Link>
        </CardHeader>
        <CardContent>
          {scansLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : scans && scans.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-800">
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Name
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Status
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Risk Score
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {scans.map((scan) => (
                    <tr
                      key={scan.id}
                      className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors"
                    >
                      <td className="py-3 px-4">
                        <Link href={`/scans/${scan.id}`}>
                          <a className="text-red-400 hover:text-red-300">
                            Scan {scan.id.slice(0, 8)}
                          </a>
                        </Link>
                      </td>
                      <td className="py-3 px-4">
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
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-white font-medium">
                          {scan.risk_score !== null
                            ? `${scan.risk_score.toFixed(1)}`
                            : "—"}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-400">
                        {formatDate(scan.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-400 mb-4">No scans yet</p>
              <Link href="/scans/new">
                <Button variant="primary" size="sm">
                  Start Your First Scan
                </Button>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Compliance Frameworks */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">
          Compliance Frameworks
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { name: "EU AI Act", score: stats?.framework_scores?.["eu_ai_act"] || 0 },
            { name: "NIST AI RMF", score: stats?.framework_scores?.["nist_ai_rmf"] || 0 },
            { name: "OWASP LLM", score: stats?.framework_scores?.["owasp_llm"] || 0 },
            { name: "ISO 42001", score: stats?.framework_scores?.["iso_42001"] || 0 },
            { name: "SOC2 AI", score: stats?.framework_scores?.["soc2_ai"] || 0 },
            {
              name: "OWASP Agentic",
              score: stats?.framework_scores?.["owasp_agentic"] || 0,
            },
          ].map((framework) => (
            <Card key={framework.name}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-white">{framework.name}</h4>
                  <Badge variant="info">
                    {framework.score.toFixed(0)}%
                  </Badge>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-green-600 to-green-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(100, framework.score)}%` }}
                  />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-white">Quick Actions</h3>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Link href="/scans/new">
            <Button variant="primary">
              Start New Scan
            </Button>
          </Link>
          <Link href="/targets">
            <Button variant="secondary">
              Add Target
            </Button>
          </Link>
          <Link href="/reports">
            <Button variant="secondary">
              Generate Report
            </Button>
          </Link>
          <Link href="/compliance">
            <Button variant="secondary">
              View Compliance
            </Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
