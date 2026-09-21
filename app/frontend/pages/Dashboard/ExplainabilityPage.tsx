import { BarChart3, ShieldAlert } from "lucide-react";
import { useAnalysis } from "@/hooks/use-analysis";
import { filterTransactions } from "@/services/analysisService";
import { currencyFormatter, formatDate } from "@/utils/formatters";
import { PageHeading } from "@/components/common/PageHeading";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export function ExplainabilityPage() {
  const { transactions, filters } = useAnalysis();
  const explainableRecords = filterTransactions(transactions, filters)
    .filter((item) => item.status !== "Safe")
    .sort((left, right) => right.riskScore - left.riskScore);

  return (
    <div className="space-y-8">
      <PageHeading
        eyebrow="AI Explainability"
        title="Understand why each suspicious transaction was detected"
        description="Every flagged or review-worthy record includes risk level, confidence, affected features, and a plain-language AI explanation."
      />

      <div className="grid gap-6 xl:grid-cols-2">
        {explainableRecords.map((record) => (
          <Card key={record.id}>
            <CardHeader>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <CardTitle>{record.reference}</CardTitle>
                  <CardDescription>
                    {record.category} · {record.merchant} · {formatDate(record.date)}
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Badge tone={record.status === "Fraud" ? "danger" : "warning"}>{record.status}</Badge>
                  <Badge tone={record.riskLevel === "Critical" || record.riskLevel === "High" ? "danger" : "warning"}>
                    {record.riskLevel}
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="grid gap-4 sm:grid-cols-3">
                <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Amount</p>
                  <p className="mt-2 text-lg font-semibold">{currencyFormatter.format(record.amount)}</p>
                </div>
                <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Risk Score</p>
                  <p className="mt-2 text-lg font-semibold">{record.riskScore}/100</p>
                </div>
                <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Confidence</p>
                  <p className="mt-2 text-lg font-semibold">{Math.round(record.confidence * 100)}%</p>
                </div>
              </div>

              <div>
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-sm font-medium">Model confidence</p>
                  <p className="text-sm text-muted-foreground">{Math.round(record.confidence * 100)}%</p>
                </div>
                <Progress value={record.confidence * 100} />
              </div>

              <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="h-4 w-4 text-primary" />
                  <p className="font-medium">Why was it detected?</p>
                </div>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">{record.explanation}</p>
              </div>

              <div>
                <div className="mb-3 flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-primary" />
                  <p className="font-medium">Affected features and risk factors</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {record.affectedFeatures.map((feature) => (
                    <Badge key={feature} tone="info">
                      {feature}
                    </Badge>
                  ))}
                  {record.flags.map((flag) => (
                    <Badge key={flag} tone="warning">
                      {flag}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
