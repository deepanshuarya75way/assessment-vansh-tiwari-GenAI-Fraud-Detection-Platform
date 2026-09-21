import type { LucideIcon } from "lucide-react";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/utils/cn";

interface StatCardProps {
  label: string;
  value: string;
  delta: string;
  tone?: "neutral" | "positive" | "negative";
  icon: LucideIcon;
}

export function StatCard({
  label,
  value,
  delta,
  tone = "neutral",
  icon: Icon,
}: StatCardProps) {
  const isPositive = tone === "positive";
  const isNegative = tone === "negative";

  return (
    <Card className="overflow-hidden">
      <CardContent className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="mt-3 text-3xl font-semibold tracking-tight">{value}</p>
          <div
            className={cn(
              "mt-4 inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium",
              isPositive && "bg-emerald-500/12 text-emerald-700 dark:text-emerald-300",
              isNegative && "bg-rose-500/12 text-rose-700 dark:text-rose-200",
              tone === "neutral" && "bg-secondary text-secondary-foreground",
            )}
          >
            {isNegative ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
            {delta}
          </div>
        </div>

        <div className="rounded-2xl bg-primary/8 p-3 text-primary">
          <Icon className="h-5 w-5" />
        </div>
      </CardContent>
    </Card>
  );
}
