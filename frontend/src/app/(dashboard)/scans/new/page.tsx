"use client";

import React, { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import useSWR from "swr";
import { Card, CardContent, CardHeader } from "@/components/Card";
import Input from "@/components/Input";
import Button from "@/components/Button";
import Badge from "@/components/Badge";
import LoadingSpinner from "@/components/LoadingSpinner";
import { api } from "@/lib/api";
import type { Target } from "@/types";

const scanSchema = z.object({
  target_id: z.string().min(1, "Target is required"),
  scan_mode: z.enum(["quick", "standard", "deep", "custom"]),
  target_name: z.string().optional(),
  endpoint_url: z.string().url().optional(),
  model_type: z.string().optional(),
});

type ScanFormData = z.infer<typeof scanSchema>;

const modes = [
  { value: "quick", label: "Quick Scan", attacks: "50", time: "~5 min" },
  { value: "standard", label: "Standard Scan", attacks: "200", time: "~20 min" },
  { value: "deep", label: "Deep Scan", attacks: "456", time: "~2 hours" },
  { value: "custom", label: "Custom", attacks: "Select", time: "Varies" },
];

export default function NewScanPage() {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [isCreatingNewTarget, setIsCreatingNewTarget] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: targets, isLoading: targetsLoading } = useSWR<Target[]>(
    "/api/v1/targets?limit=100",
    (url) => api.get(url)
  );

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ScanFormData>({
    resolver: zodResolver(scanSchema),
    defaultValues: { scan_mode: "standard" },
  });

  const targetId = watch("target_id");
  const scanMode = watch("scan_mode");

  const selectedTarget = useMemo(() => {
    return targets?.find((t) => t.id === targetId);
  }, [targets, targetId]);

  const onSubmit = async (data: ScanFormData) => {
    setIsSubmitting(true);

    try {
      let finalTargetId = data.target_id;

      // Create new target if needed
      if (isCreatingNewTarget && !finalTargetId) {
        const newTarget = await api.post<Target>("/api/v1/targets", {
          name: data.target_name,
          endpoint_url: data.endpoint_url,
          model_type: data.model_type,
          provider: "custom",
        });
        finalTargetId = newTarget.id;
      }

      // Create scan
      const scan = await api.post("/api/v1/scans", {
        target_id: finalTargetId,
        scan_mode: data.scan_mode,
      });

      router.push(`/scans/${scan.id}`);
    } catch (error) {
      console.error("Error creating scan:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const progressSteps = [
    { num: 1, label: "Target" },
    { num: 2, label: "Mode" },
    { num: 3, label: "Options" },
    { num: 4, label: "Review" },
  ];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">New Scan</h1>
        <p className="text-gray-400">
          Configure and start a new security scan
        </p>
      </div>

      {/* Progress Indicator */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            {progressSteps.map((s, idx) => (
              <div key={s.num} className="flex items-center flex-1">
                <div
                  className={`flex items-center justify-center w-10 h-10 rounded-full font-bold transition-colors ${
                    step >= s.num
                      ? "bg-red-600 text-white"
                      : "bg-gray-800 text-gray-400"
                  }`}
                >
                  {s.num}
                </div>
                <p
                  className={`ml-2 text-sm font-medium ${
                    step >= s.num ? "text-white" : "text-gray-400"
                  }`}
                >
                  {s.label}
                </p>
                {idx < progressSteps.length - 1 && (
                  <div
                    className={`flex-1 h-1 mx-4 rounded-full ${
                      step > s.num
                        ? "bg-red-600"
                        : "bg-gray-800"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <form onSubmit={handleSubmit(onSubmit)}>
        {/* Step 1: Target Selection */}
        {step === 1 && (
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold text-white">
                Select Target
              </h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-200 mb-3">
                  Target Type
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setIsCreatingNewTarget(false)}
                    className={`p-4 rounded-lg border transition-all ${
                      !isCreatingNewTarget
                        ? "border-red-600 bg-red-600/10"
                        : "border-gray-700 hover:border-gray-600"
                    }`}
                  >
                    <p className="text-white font-medium">Existing Target</p>
                    <p className="text-xs text-gray-400">Use saved endpoint</p>
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsCreatingNewTarget(true)}
                    className={`p-4 rounded-lg border transition-all ${
                      isCreatingNewTarget
                        ? "border-red-600 bg-red-600/10"
                        : "border-gray-700 hover:border-gray-600"
                    }`}
                  >
                    <p className="text-white font-medium">New Target</p>
                    <p className="text-xs text-gray-400">Add new endpoint</p>
                  </button>
                </div>
              </div>

              {!isCreatingNewTarget ? (
                <div>
                  <label className="block text-sm font-medium text-gray-200 mb-2">
                    Choose Target
                  </label>
                  {targetsLoading ? (
                    <LoadingSpinner size="sm" />
                  ) : targets && targets.length > 0 ? (
                    <select
                      {...register("target_id")}
                      className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white transition-colors focus:outline-none focus:border-red-600"
                    >
                      <option value="">Select a target...</option>
                      {targets.map((t) => (
                        <option key={t.id} value={t.id}>
                          {t.name} ({t.model_type})
                        </option>
                      ))}
                    </select>
                  ) : (
                    <div className="p-4 bg-gray-800/50 rounded-lg text-gray-400">
                      No targets yet. Create one first or use New Target option.
                    </div>
                  )}
                  {errors.target_id && (
                    <p className="mt-1 text-sm text-red-500">
                      {errors.target_id.message}
                    </p>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  <Input
                    label="Target Name"
                    {...register("target_name")}
                    placeholder="e.g., ChatGPT API Production"
                  />
                  <Input
                    label="API Endpoint"
                    type="url"
                    {...register("endpoint_url")}
                    placeholder="https://api.openai.com/v1/chat/completions"
                  />
                  <div>
                    <label className="block text-sm font-medium text-gray-200 mb-2">
                      Model Type
                    </label>
                    <select
                      {...register("model_type")}
                      className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white transition-colors focus:outline-none focus:border-red-600"
                    >
                      <option value="">Select model...</option>
                      <option value="gpt-4">GPT-4</option>
                      <option value="gpt-3.5">GPT-3.5</option>
                      <option value="claude">Claude</option>
                      <option value="mistral">Mistral</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Step 2: Scan Mode */}
        {step === 2 && (
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold text-white">
                Choose Scan Mode
              </h2>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {modes.map((mode) => (
                  <button
                    key={mode.value}
                    type="button"
                    onClick={() => {}}
                    className={`p-6 rounded-lg border-2 transition-all text-left ${
                      scanMode === mode.value
                        ? "border-red-600 bg-red-600/10"
                        : "border-gray-700 hover:border-gray-600"
                    }`}
                  >
                    <input
                      type="radio"
                      {...register("scan_mode")}
                      value={mode.value}
                      className="hidden"
                    />
                    <p className="text-white font-medium mb-2">{mode.label}</p>
                    <div className="space-y-1 text-sm text-gray-400">
                      <p>Attacks: {mode.attacks}</p>
                      <p>Est. time: {mode.time}</p>
                    </div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Advanced Options */}
        {step === 3 && (
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold text-white">
                Advanced Options
              </h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-200 mb-2">
                  Concurrency (parallel attacks)
                </label>
                <input
                  type="number"
                  defaultValue={5}
                  min={1}
                  max={20}
                  className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-200 mb-3">
                  Attack Categories
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {["Prompt Injection", "Jailbreak", "Data Extraction", "Model Reversal", "Bias", "Evasion"].map((cat) => (
                    <label
                      key={cat}
                      className="flex items-center gap-2 p-2 rounded hover:bg-gray-800/50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        defaultChecked
                        className="rounded"
                      />
                      <span className="text-sm text-gray-300">{cat}</span>
                    </label>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 4: Review */}
        {step === 4 && (
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold text-white">
                Review & Start
              </h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-gray-800/30 rounded-lg space-y-3">
                <div>
                  <p className="text-xs text-gray-400">Target</p>
                  <p className="text-white font-medium">
                    {selectedTarget?.name || "New Target"}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Scan Mode</p>
                  <Badge variant="info">
                    {scanMode.charAt(0).toUpperCase() + scanMode.slice(1)}
                  </Badge>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Status</p>
                  <p className="text-white">Ready to start</p>
                </div>
              </div>
              <p className="text-sm text-gray-400">
                Clicking "Start Scan" will begin attacking your AI system.
                Monitor the progress in real-time on the next page.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Navigation Buttons */}
        <div className="flex gap-4 justify-between">
          <Button
            type="button"
            variant="outline"
            onClick={() => setStep((s) => Math.max(1, s - 1) as any)}
            disabled={step === 1}
          >
            Back
          </Button>

          {step < 4 ? (
            <Button
              type="button"
              variant="primary"
              onClick={() => setStep((s) => Math.min(4, s + 1) as any)}
            >
              Continue
            </Button>
          ) : (
            <Button
              type="submit"
              variant="primary"
              isLoading={isSubmitting}
            >
              Start Scan
            </Button>
          )}
        </div>
      </form>
    </div>
  );
}
