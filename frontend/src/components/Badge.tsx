import React from "react";
import { cn } from "@/lib/utils";

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline" | "success" | "warning" | "info";
  children: React.ReactNode;
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = "default", children, ...props }, ref) => {
    const variants = {
      default: "bg-red-600/20 text-red-400 border border-red-600/30",
      secondary: "bg-gray-700/50 text-gray-300 border border-gray-600",
      destructive: "bg-red-500/20 text-red-300 border border-red-600",
      outline: "border border-gray-600 text-gray-300",
      success: "bg-green-500/20 text-green-400 border border-green-600",
      warning: "bg-yellow-500/20 text-yellow-400 border border-yellow-600",
      info: "bg-blue-500/20 text-blue-400 border border-blue-600",
    };

    return (
      <div
        ref={ref}
        className={cn(
          "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors",
          variants[variant],
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Badge.displayName = "Badge";

export default Badge;
