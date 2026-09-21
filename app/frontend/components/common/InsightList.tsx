import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { InsightItem } from "@/utils/types";

interface InsightListProps {
  items: InsightItem[];
}

export function InsightList({ items }: InsightListProps) {
  const toneMap = {
    informational: "info",
    elevated: "warning",
    critical: "danger",
  } as const;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Fraud Patterns</CardTitle>
        <CardDescription>
          Explainable AI findings surfaced from the uploaded dataset and analysis workflow.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {items.map((item) => (
          <div key={item.id} className="rounded-2xl border border-border/60 bg-background/40 p-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-medium">{item.title}</p>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.summary}</p>
              </div>
              <Badge tone={toneMap[item.severity]}>{item.severity}</Badge>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
