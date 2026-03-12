"use client";

import React, { useState } from "react";
import useSWR from "swr";
import { Card, CardContent, CardHeader } from "@/components/Card";
import Badge from "@/components/Badge";
import Button from "@/components/Button";
import Skeleton from "@/components/Skeleton";
import { api } from "@/lib/api";
import type { ComplianceFramework, ComplianceControl } from "@/types";

export default function CompliancePage() {
  const { data: frameworks, isLoading } = useSWR<ComplianceFramework[]>(
    "/api/v1/compliance/frameworks",
    (url) => api.get(url),
    { revalidateOnFocus: false, dedupingInterval: 30000 }
  );

  const [selectedFramework, setSelectedFramework] = useState<ComplianceFramework | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "compliant":
        return "success";
      case "partial":
        return "warning";
      case "non_compliant":
        return "destructive";
      default:
        return "secondary";
    }
  };

  const getControlColor = (status: string) => {
    switch (status) {
      case "pass":
        return "success";
      case "partial":
        return "warning";
      case "fail":
        return "destructive";
      default:
        return "secondary";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Compliance</h1>
        <p className="text-gray-400">
          Track compliance against 6 AI security frameworks
        </p>
      </div>

      {/* Frameworks Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      ) : frameworks && frameworks.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {frameworks.map((framework) => (
            <Card
              key={framework.id}
              className="cursor-pointer hover:border-red-600/50 transition-all"
              onClick={() => setSelectedFramework(framework)}
            >
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">
                    {framework.name}
                  </h3>
                  <Badge variant={getStatusColor(framework.status)}>
                    {framework.score.toFixed(0)}%
                  </Badge>
                </div>

                <p className="text-sm text-gray-400 mb-4">
                  {framework.description}
                </p>

                {/* Progress Bar */}
                <div className="w-full bg-gray-800 rounded-full h-2 mb-3">
                  <div
                    className="bg-gradient-to-r from-green-600 to-green-500 h-2 rounded-full transition-all"
                    style={{ width: `${Math.min(100, framework.score)}%` }}
                  />
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-2 text-center text-xs mb-4">
                  <div>
                    <p className="text-green-400 font-bold">
                      {framework.passed_controls}
                    </p>
                    <p className="text-gray-400">Passed</p>
                  </div>
                  <div>
                    <p className="text-yellow-400 font-bold">
                      {framework.control_count - framework.passed_controls - (framework.control_count - framework.passed_controls - framework.failed_controls)}
                    </p>
                    <p className="text-gray-400">Partial</p>
                  </div>
                  <div>
                    <p className="text-red-400 font-bold">
                      {framework.failed_controls}
                    </p>
                    <p className="text-gray-400">Failed</p>
                  </div>
                </div>

                <Button variant="outline" size="sm" className="w-full">
                  View Details
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-gray-400">No compliance data yet</p>
          </CardContent>
        </Card>
      )}

      {/* Framework Detail */}
      {selectedFramework && (
        <div className="fixed inset-0 z-40 flex bg-black/30">
          <div className="w-full max-w-2xl mx-auto bg-gray-900 rounded-lg border border-gray-800 max-h-96 overflow-y-auto">
            <div className="p-6 sticky top-0 bg-gray-900 border-b border-gray-800 flex items-start justify-between">
              <div>
                <h3 className="text-2xl font-bold text-white">
                  {selectedFramework.name}
                </h3>
                <p className="text-gray-400 mt-1">
                  {selectedFramework.description}
                </p>
              </div>
              <button
                onClick={() => setSelectedFramework(null)}
                className="text-gray-400 hover:text-gray-300 text-2xl"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-4">
              {selectedFramework.controls?.map((control) => (
                <div
                  key={control.id}
                  className="p-4 rounded-lg border border-gray-800 bg-gray-900/50"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="text-white font-medium">{control.name}</h4>
                    <Badge variant={getControlColor(control.status)}>
                      {control.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-400 mb-3">
                    {control.description}
                  </p>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Requirement:</p>
                    <p className="text-sm text-gray-300">
                      {control.requirement}
                    </p>
                  </div>
                  {control.remediation && (
                    <div className="mt-3 p-3 bg-red-900/20 rounded border border-red-800/30">
                      <p className="text-xs text-red-400 mb-1">
                        Remediation:
                      </p>
                      <p className="text-sm text-red-300">
                        {control.remediation}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Summary */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-white">
            Compliance Summary
          </h3>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <p className="text-gray-400 text-sm">
              Your AI system is currently being assessed against 6 major compliance frameworks:
            </p>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <span className="text-gray-400">•</span>
                <span className="text-gray-300">EU AI Act</span>
                <span className="text-gray-500">- Risk-based regulation for AI systems</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-gray-400">•</span>
                <span className="text-gray-300">NIST AI RMF</span>
                <span className="text-gray-500">- AI risk management framework</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-gray-400">•</span>
                <span className="text-gray-300">OWASP LLM Top 10</span>
                <span className="text-gray-500">- Critical vulnerabilities for LLMs</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-gray-400">•</span>
                <span className="text-gray-300">ISO 42001</span>
                <span className="text-gray-500">- AI management system standard</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-gray-400">•</span>
                <span className="text-gray-300">SOC2 Type II</span>
                <span className="text-gray-500">- AI-specific security controls</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-gray-400">•</span>
                <span className="text-gray-300">OWASP Agentic AI</span>
                <span className="text-gray-500">- AI agents security guidelines</span>
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
