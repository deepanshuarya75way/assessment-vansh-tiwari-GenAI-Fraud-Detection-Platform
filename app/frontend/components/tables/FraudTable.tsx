import { useMemo, useState } from "react";
import { ArrowDownUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { currencyFormatter, formatDate } from "@/utils/formatters";
import type { SortDirection, TransactionRecord } from "@/utils/types";

interface FraudTableProps {
  data: TransactionRecord[];
}

type SortField = "reference" | "date" | "amount" | "riskScore" | "status";

const pageSize = 6;

export function FraudTable({ data }: FraudTableProps) {
  const [sortField, setSortField] = useState<SortField>("riskScore");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");
  const [page, setPage] = useState(1);

  const sortedData = useMemo(() => {
    return [...data].sort((left, right) => {
      const leftValue = left[sortField];
      const rightValue = right[sortField];

      if (leftValue === rightValue) return 0;
      if (sortDirection === "asc") {
        return leftValue > rightValue ? 1 : -1;
      }
      return leftValue < rightValue ? 1 : -1;
    });
  }, [data, sortDirection, sortField]);

  const paginatedData = sortedData.slice((page - 1) * pageSize, page * pageSize);
  const totalPages = Math.max(1, Math.ceil(sortedData.length / pageSize));

  function updateSort(field: SortField) {
    setPage(1);
    if (field === sortField) {
      setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
      return;
    }
    setSortField(field);
    setSortDirection("desc");
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Fraud Details</CardTitle>
        <CardDescription>
          Sortable transaction review table with risk level, status, and explainable AI summary.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="overflow-x-auto rounded-2xl border border-border/70">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-secondary/60">
              <tr>
                {[
                  ["reference", "Reference"],
                  ["date", "Date"],
                  ["amount", "Amount"],
                  ["riskScore", "Risk Score"],
                  ["status", "Status"],
                ].map(([field, label]) => (
                  <th key={field} className="px-4 py-3 font-medium">
                    <button
                      type="button"
                      onClick={() => updateSort(field as SortField)}
                      className="inline-flex items-center gap-2"
                    >
                      {label}
                      <ArrowDownUp className="h-3.5 w-3.5 text-muted-foreground" />
                    </button>
                  </th>
                ))}
                <th className="px-4 py-3 font-medium">Category</th>
                <th className="px-4 py-3 font-medium">AI Explanation</th>
              </tr>
            </thead>
            <tbody>
              {paginatedData.map((transaction) => (
                <tr key={transaction.id} className="border-t border-border/70 align-top">
                  <td className="px-4 py-4 font-medium">{transaction.reference}</td>
                  <td className="px-4 py-4 text-muted-foreground">{formatDate(transaction.date)}</td>
                  <td className="px-4 py-4">{currencyFormatter.format(transaction.amount)}</td>
                  <td className="px-4 py-4">{transaction.riskScore}/100</td>
                  <td className="px-4 py-4">
                    <Badge
                      tone={
                        transaction.status === "Fraud"
                          ? "danger"
                          : transaction.status === "Review"
                            ? "warning"
                            : "success"
                      }
                    >
                      {transaction.status}
                    </Badge>
                  </td>
                  <td className="px-4 py-4 text-muted-foreground">{transaction.category}</td>
                  <td className="px-4 py-4 text-muted-foreground">{transaction.explanation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, sortedData.length)} of{" "}
            {sortedData.length} records
          </p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => setPage((current) => Math.max(1, current - 1))}>
              Previous
            </Button>
            <Button variant="outline" size="sm" onClick={() => setPage((current) => Math.min(totalPages, current + 1))}>
              Next
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
