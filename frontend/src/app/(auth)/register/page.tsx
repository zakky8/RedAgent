"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import Input from "@/components/Input";
import Button from "@/components/Button";
import { register as registerUser } from "@/lib/auth";

const registerSchema = z
  .object({
    full_name: z.string().min(2, "Name must be at least 2 characters"),
    email: z.string().email("Invalid email address"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirm_password: z.string(),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords don't match",
    path: ["confirm_password"],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [generalError, setGeneralError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    setGeneralError(null);

    try {
      await registerUser(data.email, data.full_name, data.password);
      router.push("/dashboard");
    } catch (error) {
      setGeneralError(
        error instanceof Error ? error.message : "Registration failed. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-2">Create your account</h2>
      <p className="text-gray-400 mb-6">
        Join AgentRed and start securing your AI systems
      </p>

      {generalError && (
        <div className="mb-6 p-4 bg-red-900/30 border border-red-800 rounded-lg text-red-400 text-sm">
          {generalError}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Full Name"
          type="text"
          placeholder="John Doe"
          {...register("full_name")}
          error={errors.full_name?.message}
        />

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
          helperText="Must be at least 8 characters"
          {...register("password")}
          error={errors.password?.message}
        />

        <Input
          label="Confirm Password"
          type="password"
          placeholder="••••••••"
          {...register("confirm_password")}
          error={errors.confirm_password?.message}
        />

        <div className="flex items-center gap-2 text-xs text-gray-400">
          <input
            type="checkbox"
            id="terms"
            className="rounded border-gray-700"
            required
          />
          <label htmlFor="terms">
            I agree to the Terms of Service and Privacy Policy
          </label>
        </div>

        <Button
          type="submit"
          variant="primary"
          size="md"
          className="w-full mt-6"
          isLoading={isLoading}
        >
          Create Account
        </Button>
      </form>

      <div className="mt-6 border-t border-gray-800 pt-6">
        <p className="text-gray-400 text-center mb-4">Already have an account?</p>
        <Link href="/login">
          <Button
            variant="outline"
            size="md"
            className="w-full"
          >
            Sign In
          </Button>
        </Link>
      </div>
    </div>
  );
}
