import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCompactDateTime } from "@/utils/formatters";
import type { ActivityItem } from "@/utils/types";

interface ActivityListProps {
  items: ActivityItem[];
}

export function ActivityList({ items }: ActivityListProps) {
  const toneMap = {
    neutral: "neutral",
    success: "success",
    warning: "warning",
    danger: "danger",
  } as const;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>Latest actions produced during the current analysis cycle.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {items.map((item) => (
          <div key={item.id} className="flex items-start justify-between gap-4 rounded-2xl border border-border/60 bg-background/40 p-4">
            <div>
              <p className="font-medium">{item.title}</p>
              <p className="mt-1 text-sm text-muted-foreground">{item.description}</p>
              <p className="mt-2 text-xs uppercase tracking-[0.2em] text-muted-foreground">
                {formatCompactDateTime(item.time)}
              </p>
            </div>
            <Badge tone={toneMap[item.tone]}>{item.tone}</Badge>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
