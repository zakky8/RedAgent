"use client";

import React, { useState, useMemo } from "react";
import Link from "next/link";
import useSWR from "swr";
import { Card, CardContent, CardHeader } from "@/components/Card";
import Badge from "@/components/Badge";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Skeleton from "@/components/Skeleton";
import { api } from "@/lib/api";
import { formatDate, getStatusColor } from "@/lib/utils";
import type { Scan } from "@/types";

type FilterStatus = "all" | "pending" | "running" | "completed" | "failed";

export default function ScansPage() {
  const { data: scans, isLoading } = useSWR<Scan[]>(
    "/api/v1/scans?limit=100&offset=0",
    (url) => api.get(url),
    { revalidateOnFocus: false, dedupingInterval: 30000 }
  );

  const [statusFilter, setStatusFilter] = useState<FilterStatus>("all");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredScans = useMemo(() => {
    if (!scans) return [];

    return scans.filter((scan) => {
      const matchesStatus = statusFilter === "all" || scan.status === statusFilter;
      const matchesSearch =
        scan.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        scan.target_id?.toLowerCase().includes(searchQuery.toLowerCase());

      return matchesStatus && matchesSearch;
    });
  }, [scans, statusFilter, searchQuery]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Scans</h1>
          <p className="text-gray-400">
            Manage and monitor your AI security scans
          </p>
        </div>
        <Link href="/scans/new">
          <Button variant="primary" size="lg">
            New Scan
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="Search"
              type="text"
              placeholder="Search by scan ID or target..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />

            <div>
              <label className="block text-sm font-medium text-gray-200 mb-2">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as FilterStatus)}
                className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white transition-colors focus:outline-none focus:border-red-600"
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="running">Running</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </select>
            </div>

            <div className="flex items-end">
              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  setStatusFilter("all");
                  setSearchQuery("");
                }}
              >
                Clear Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Scans Table */}
      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : filteredScans.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-800">
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Scan ID
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Target
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Mode
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Status
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Progress
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Risk Score
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Date
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredScans.map((scan) => (
                    <tr
                      key={scan.id}
                      className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors"
                    >
                      <td className="py-3 px-4">
                        <code className="text-xs text-gray-400">
                          {scan.id.slice(0, 12)}...
                        </code>
                      </td>
                      <td className="py-3 px-4 text-gray-300">
                        {scan.target?.name || "Unknown"}
                      </td>
                      <td className="py-3 px-4">
                        <span className="capitalize text-gray-300">
                          {scan.scan_mode}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={scan.status === "completed" ? "success" : scan.status === "running" ? "info" : scan.status === "failed" ? "destructive" : "secondary"}>
                          {scan.status.charAt(0).toUpperCase() + scan.status.slice(1)}
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-24 bg-gray-800 rounded-full h-2">
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
                          <span className="text-xs text-gray-400">
                            {scan.completed_count}/{scan.attack_count}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        {scan.risk_score !== null ? (
                          <span className="font-medium text-white">
                            {scan.risk_score.toFixed(1)}
                          </span>
                        ) : (
                          <span className="text-gray-500">—</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-gray-400">
                        {formatDate(scan.created_at)}
                      </td>
                      <td className="py-3 px-4">
                        <Link href={`/scans/${scan.id}`}>
                          <Button variant="ghost" size="sm">
                            View
                          </Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-400 mb-4">No scans found</p>
              <Link href="/scans/new">
                <Button variant="primary">Start First Scan</Button>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
