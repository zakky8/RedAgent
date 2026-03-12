"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import Input from "@/components/Input";
import Button from "@/components/Button";
import { login } from "@/lib/auth";

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [generalError, setGeneralError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    setGeneralError(null);

    try {
      await login(data.email, data.password);
      router.push("/dashboard");
    } catch (error) {
      setGeneralError(
        error instanceof Error ? error.message : "Login failed. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-2">Welcome back</h2>
      <p className="text-gray-400 mb-6">
        Sign in to your AgentRed account to continue
      </p>

      {generalError && (
        <div className="mb-6 p-4 bg-red-900/30 border border-red-800 rounded-lg text-red-400 text-sm">
          {generalError}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Email Address"
          type="email"
          placeholder="you@company.com"
          {...register("email")}
          error={errors.email?.message}
        />

        <Input
          label="Password"
          type="password"
          placeholder="••••••••"
          {...register("password")}
          error={errors.password?.message}
        />

        <Button
          type="submit"
          variant="primary"
          size="md"
          className="w-full mt-6"
          isLoading={isLoading}
        >
          Sign In
        </Button>
      </form>

      <div className="mt-6 border-t border-gray-800 pt-6">
        <p className="text-gray-400 text-center mb-4">Don't have an account?</p>
        <Link href="/register">
          <Button
            variant="outline"
            size="md"
            className="w-full"
          >
            Create Account
          </Button>
        </Link>
      </div>

      <div className="mt-6 p-4 bg-gray-800/30 rounded-lg border border-gray-700/50">
        <p className="text-xs text-gray-500 text-center">
          Demo credentials: <br />
          Email: <code className="text-gray-400">demo@agentred.ai</code>
          <br />
          Password: <code className="text-gray-400">password123</code>
        </p>
      </div>
    </div>
  );
}
