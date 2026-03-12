"use client";

import React from "react";
import { Card, CardContent } from "@/components/Card";
import Skeleton from "@/components/Skeleton";

interface StatCard {
  label: string;
  value: number | string;
  icon: string;
  trend?: string;
  trendDirection?: "up" | "down";
}

interface StatsGridProps {
  stats: StatCard[];
  isLoading?: boolean;
}

export default function StatsGrid({ stats, isLoading = false }: StatsGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardContent className="pt-6">
              <Skeleton className="h-8 w-16 mb-2" />
              <Skeleton className="h-4 w-24" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <Card key={index}>
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium mb-2">
                  {stat.label}
                </p>
                <p className="text-3xl font-bold text-white">
                  {stat.value}
                </p>
                {stat.trend && (
                  <p
                    className={`text-xs mt-2 ${
                      stat.trendDirection === "up"
                        ? "text-green-400"
                        : "text-red-400"
                    }`}
                  >
                    {stat.trendDirection === "up" ? "↑" : "↓"} {stat.trend}
                  </p>
                )}
              </div>
              <div className="text-4xl">{stat.icon}</div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
