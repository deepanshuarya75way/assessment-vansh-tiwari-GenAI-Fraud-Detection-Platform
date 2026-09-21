import { FileScan, TableProperties, Layers3 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { formatFileSize, numberFormatter } from "@/utils/formatters";
import type { UploadedDataset } from "@/utils/types";

interface DatasetSummaryCardProps {
  dataset: UploadedDataset;
}

export function DatasetSummaryCard({ dataset }: DatasetSummaryCardProps) {
  const items = [
    { label: "Rows", value: numberFormatter.format(dataset.rows), icon: TableProperties },
    { label: "Columns", value: numberFormatter.format(dataset.columns.length), icon: Layers3 },
    { label: "File Size", value: formatFileSize(dataset.size), icon: FileScan },
  ];

  return (
    <Card>
      <CardContent className="grid gap-4 sm:grid-cols-3">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.label} className="rounded-2xl border border-border/60 bg-background/40 p-4">
              <div className="flex items-center gap-3">
                <div className="rounded-2xl bg-primary/8 p-3 text-primary">
                  <Icon className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{item.label}</p>
                  <p className="mt-1 text-lg font-semibold">{item.value}</p>
                </div>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
