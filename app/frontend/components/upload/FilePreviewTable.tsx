import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatFileSize } from "@/utils/formatters";
import type { UploadedDataset } from "@/utils/types";

interface FilePreviewTableProps {
  dataset: UploadedDataset;
}

export function FilePreviewTable({ dataset }: FilePreviewTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{dataset.name}</CardTitle>
        <CardDescription>
          {dataset.rows} rows · {dataset.columns.length} columns · {formatFileSize(dataset.size)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <Badge tone={dataset.validation.status === "valid" ? "success" : "warning"}>
            {dataset.validation.status}
          </Badge>
          <p className="text-sm text-muted-foreground">{dataset.validation.message}</p>
        </div>

        <div className="overflow-hidden rounded-2xl border border-border/70">
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-secondary/60">
                <tr>
                  {dataset.columns.map((column) => (
                    <th key={column} className="px-4 py-3 font-medium">
                      {column}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {dataset.preview.map((row, rowIndex) => (
                  <tr key={`${dataset.id}-${rowIndex}`} className="border-t border-border/70">
                    {dataset.columns.map((column, cellIndex) => (
                      <td key={`${column}-${cellIndex}`} className="px-4 py-3 text-muted-foreground">
                        {row[cellIndex] ?? "—"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
