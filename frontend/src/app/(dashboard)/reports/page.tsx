"use client";

import React, { useState } from "react";
import useSWR from "swr";
import { Card, CardContent, CardHeader } from "@/components/Card";
import Badge from "@/components/Badge";
import Button from "@/components/Button";
import Skeleton from "@/components/Skeleton";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { Report } from "@/types";

export default function ReportsPage() {
  const { data: reports, isLoading } = useSWR<Report[]>(
    "/api/v1/reports?limit=100",
    (url) => api.get(url),
    { revalidateOnFocus: false, dedupingInterval: 30000 }
  );

  const [isGenerating, setIsGenerating] = useState(false);
  const [reportType, setReportType] = useState<"executive" | "detailed" | "compliance">("detailed");

  const handleGenerateReport = async () => {
    setIsGenerating(true);
    try {
      await api.post("/api/v1/reports", {
        report_type: reportType,
        include_recommendations: true,
      });
    } catch (error) {
      console.error("Error generating report:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const reportTypeLabels = {
    executive: "Executive Summary",
    detailed: "Detailed Technical",
    compliance: "Compliance Focused",
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Reports</h1>
          <p className="text-gray-400">Generate and manage security reports</p>
        </div>
      </div>

      {/* Generate Report */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-white">Generate Report</h3>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-200 mb-3">
              Report Type
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {(["executive", "detailed", "compliance"] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => setReportType(type)}
                  className={`p-4 rounded-lg border transition-all text-left ${
                    reportType === type
                      ? "border-red-600 bg-red-600/10"
                      : "border-gray-700 hover:border-gray-600"
                  }`}
                >
                  <p className="text-white font-medium">
                    {reportTypeLabels[type]}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    {type === "executive"
                      ? "C-suite friendly overview"
                      : type === "detailed"
                      ? "In-depth technical analysis"
                      : "Framework compliance mapped"}
                  </p>
                </button>
              ))}
            </div>
          </div>
          <Button
            variant="primary"
            onClick={handleGenerateReport}
            isLoading={isGenerating}
            className="w-full"
          >
            Generate Report
          </Button>
        </CardContent>
      </Card>

      {/* Reports List */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-16" />
          ))}
        </div>
      ) : reports && reports.length > 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-3">
              {reports.map((report) => (
                <div
                  key={report.id}
                  className="p-4 rounded-lg border border-gray-800 hover:border-red-600/30 transition-all flex items-center justify-between"
                >
                  <div>
                    <h4 className="text-white font-medium">{report.name}</h4>
                    <div className="flex items-center gap-3 mt-2">
                      <Badge variant="secondary">
                        {reportTypeLabels[report.report_type as keyof typeof reportTypeLabels] || report.report_type}
                      </Badge>
                      <span className="text-xs text-gray-400">
                        {formatDate(report.created_at)}
                      </span>
                      <span className="text-xs text-gray-400">
                        Created by {report.created_by}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      View
                    </Button>
                    <Button variant="secondary" size="sm">
                      Download
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-gray-400 mb-4">No reports yet</p>
            <Button variant="primary" onClick={handleGenerateReport}>
              Generate First Report
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Report Templates */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-white">Report Templates</h3>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              {
                title: "Risk Assessment",
                description: "Comprehensive risk analysis and scoring",
              },
              {
                title: "Vulnerability Report",
                description: "Detailed technical vulnerability findings",
              },
              {
                title: "Remediation Plan",
                description: "Step-by-step fixing guide for all issues",
              },
            ].map((template) => (
              <div
                key={template.title}
                className="p-4 rounded-lg border border-gray-800 hover:border-red-600/30 cursor-pointer transition-all"
              >
                <h4 className="text-white font-medium">{template.title}</h4>
                <p className="text-sm text-gray-400 mt-1">
                  {template.description}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
