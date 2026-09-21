import { Download, FileSpreadsheet, FileText, Printer } from "lucide-react";
import { useAnalysis } from "@/hooks/use-analysis";
import { exportReportAsWord, exportTransactionsToCsv, printReport } from "@/services/exportService";
import { currencyFormatter, numberFormatter, percentFormatter } from "@/utils/formatters";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export function ReportViewer() {
  const { snapshot, transactions } = useAnalysis();

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">AI Report</p>
          <h2 className="mt-2 text-2xl font-semibold">Executive Fraud Analysis Report</h2>
        </div>
        <div className="flex flex-wrap gap-3 print:hidden">
          <Button variant="outline" onClick={printReport}>
            <Printer className="mr-2 h-4 w-4" />
            PDF
          </Button>
          <Button variant="outline" onClick={() => exportReportAsWord(snapshot)}>
            <FileText className="mr-2 h-4 w-4" />
            Word
          </Button>
          <Button onClick={() => exportTransactionsToCsv(transactions)}>
            <FileSpreadsheet className="mr-2 h-4 w-4" />
            Excel
          </Button>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
        <Card>
          <CardHeader>
            <CardTitle>Executive Summary</CardTitle>
            <CardDescription>High-level fraud posture for the uploaded dataset, tailored for leadership review.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <p className="text-sm leading-7 text-muted-foreground">
              The active session {snapshot.sessionMetadata.sessionId} contains {numberFormatter.format(snapshot.metrics.totalRecords)} records across {snapshot.metrics.totalFiles} files, with {numberFormatter.format(snapshot.metrics.fraudRecords)} suspicious transactions identified. Overall exposure is assessed at {snapshot.metrics.riskScore}/100 with the strongest pressure coming from {snapshot.fraudAnalysis.fraudByMerchant[0]?.label ?? "the current transaction mix"} and related risk clusters.
            </p>
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Fraud Rate</p>
                <p className="mt-2 text-2xl font-semibold">{percentFormatter.format(snapshot.metrics.fraudRate)}</p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Average Risk</p>
                <p className="mt-2 text-2xl font-semibold">{snapshot.metrics.riskScore}/100</p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Estimated Exposure</p>
                <p className="mt-2 text-2xl font-semibold">
                  {currencyFormatter.format(transactions.filter((item) => item.status === "Fraud").reduce((sum, item) => sum + item.amount, 0))}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recommendations</CardTitle>
            <CardDescription>Immediate actions to tighten controls after analysis.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {snapshot.recommendations.map((recommendation) => (
              <div key={recommendation.id} className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium">{recommendation.title}</p>
                  <Badge tone={recommendation.priority === "high" ? "danger" : recommendation.priority === "medium" ? "warning" : "info"}>{recommendation.priority}</Badge>
                </div>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{recommendation.detail}</p>
              </div>
            ))}
            <Button variant="ghost" className="w-full justify-between">
              Export detailed recommendations pack
              <Download className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Dataset Summary</CardTitle>
            <CardDescription>Rows, columns, and quality indicators from the active upload.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <p>Rows: {snapshot.datasetSummary.rows}</p>
            <p>Columns: {snapshot.datasetSummary.columns}</p>
            <p>Missing values: {snapshot.datasetSummary.missingValues}</p>
            <p>Duplicate records: {snapshot.datasetSummary.duplicateRecords}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Session metadata</CardTitle>
            <CardDescription>Versioning, timing, and model information for the current report.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <p>Session ID: {snapshot.sessionMetadata.sessionId}</p>
            <p>Dataset name: {snapshot.sessionMetadata.datasetName}</p>
            <p>Processing time: {snapshot.sessionMetadata.processingTime}</p>
            <p>Model version: {snapshot.sessionMetadata.modelVersion}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
