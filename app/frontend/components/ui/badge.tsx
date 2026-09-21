import type { HTMLAttributes } from "react";
import { cn } from "@/utils/cn";

const toneStyles = {
  neutral: "bg-secondary text-secondary-foreground",
  success: "bg-emerald-500/12 text-emerald-700 dark:text-emerald-300",
  warning: "bg-amber-500/12 text-amber-700 dark:text-amber-200",
  danger: "bg-rose-500/12 text-rose-700 dark:text-rose-200",
  info: "bg-sky-500/12 text-sky-700 dark:text-sky-200",
};

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: keyof typeof toneStyles;
}

export function Badge({ className, tone = "neutral", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium",
        toneStyles[tone],
        className,
      )}
      {...props}
    />
  );
}
