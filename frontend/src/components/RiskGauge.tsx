"use client";

import React from "react";
import { Card, CardContent, CardHeader } from "@/components/Card";
import { getRiskColor, getRiskLabel } from "@/lib/utils";

interface RiskGaugeProps {
  score: number | null | undefined;
  isLoading?: boolean;
}

export default function RiskGauge({ score = 0, isLoading = false }: RiskGaugeProps) {
  const numScore = Number(score) || 0;
  const riskColor = getRiskColor(numScore);
  const riskLabel = getRiskLabel(numScore);

  const colorMap = {
    critical: { bg: "from-red-600 to-red-500", text: "text-red-500" },
    high: { bg: "from-orange-600 to-orange-500", text: "text-orange-500" },
    medium: { bg: "from-yellow-600 to-yellow-500", text: "text-yellow-500" },
    low: { bg: "from-green-600 to-green-500", text: "text-green-500" },
  };

  const colors = colorMap[riskColor];

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-white">Risk Score</h3>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center justify-center py-8">
          {isLoading ? (
            <div className="animate-pulse w-32 h-32 rounded-full bg-gray-700" />
          ) : (
            <>
              {/* SVG Arc Gauge */}
              <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 120 120">
                {/* Background arc */}
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  fill="none"
                  stroke="#374151"
                  strokeWidth="8"
                  strokeDasharray={`${(numScore / 100) * 314} 314`}
                />
                {/* Colored arc */}
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  fill="none"
                  stroke={colors.text}
                  strokeWidth="8"
                  strokeDasharray={`${(numScore / 100) * 314} 314`}
                  className={`transition-all duration-500`}
                />
              </svg>

              {/* Score Display */}
              <div className="text-center mt-4">
                <p className={`text-5xl font-bold mb-2 ${colors.text}`}>
                  {numScore.toFixed(0)}
                </p>
                <p className="text-gray-400 text-sm">out of 100</p>
              </div>

              {/* Risk Label */}
              <div className={`mt-4 px-4 py-2 rounded-lg bg-gray-800 border border-gray-700`}>
                <p className={`text-sm font-medium ${colors.text}`}>
                  {riskLabel} Risk
                </p>
              </div>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
