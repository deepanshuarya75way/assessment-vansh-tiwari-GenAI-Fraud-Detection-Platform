import {
  AlertTriangle,
  BrainCircuit,
  DatabaseZap,
  FileCheck2,
  FileStack,
  Gauge,
  ShieldCheck,
  ShieldX,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import { Link } from "react-router-dom";
import { useAnalysis } from "@/hooks/use-analysis";
import { filterTransactions } from "@/services/analysisService";
import { PageHeading } from "@/components/common/PageHeading";
import { SearchInput } from "@/components/common/SearchInput";
import { StatCard } from "@/components/common/StatCard";
import { ActivityList } from "@/components/common/ActivityList";
import { InsightList } from "@/components/common/InsightList";
import { MonthlyAnalysisChart } from "@/components/charts/MonthlyAnalysisChart";
import { StatusDonutChart } from "@/components/charts/StatusDonutChart";
import { CategoryBarChart } from "@/components/charts/CategoryBarChart";
import { AmountDistributionChart } from "@/components/charts/AmountDistributionChart";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { numberFormatter, percentFormatter } from "@/utils/formatters";

export function DashboardPage() {
  const { transactions, uploads, filters, setFilters, snapshot } = useAnalysis();
  const filteredTransactions = filterTransactions(transactions, filters);
  const filteredSnapshot = {
    ...snapshot,
    metrics: {
      ...snapshot.metrics,
      totalRecords: filteredTransactions.length,
      fraudRecords: filteredTransactions.filter((item) => item.status === "Fraud").length,
      safeRecords: filteredTransactions.filter((item) => item.status === "Safe").length,
      fraudRate: filteredTransactions.length > 0 ? filteredTransactions.filter((item) => item.status === "Fraud").length / filteredTransactions.length : 0,
    },
    recentActivities: snapshot.recentActivities.filter((activity) => activity.title.toLowerCase().includes("fraud") || activity.title.toLowerCase().includes("review")),
  };
  const categories = ["All", ...new Set(transactions.map((item) => item.category))];

  return (
    <div className="space-y-8">
      <PageHeading
        eyebrow="Dashboard"
        title="Fraud analytics built from the uploaded dataset"
        description="Track file volume, fraud density, risk posture, category concentration, amount spread, and recent activities with a focused enterprise dashboard."
        actions={
          <Link to="/reports">
            <Button>Open AI Report</Button>
          </Link>
        }
      />

      <Card>
        <CardContent className="grid gap-4 p-6 md:grid-cols-2 xl:grid-cols-6">
          <SearchInput
            value={filters.search}
            onChange={(value) => setFilters({ search: value })}
            placeholder="Search transaction, merchant, account, or category"
          />
          <Select value={filters.category} onChange={(event) => setFilters({ category: event.target.value })}>
            {categories.map((category) => (
              <option key={category}>{category}</option>
            ))}
          </Select>
          <Select value={filters.status} onChange={(event) => setFilters({ status: event.target.value })}>
            {["All", "Fraud", "Review", "Safe"].map((status) => (
              <option key={status}>{status}</option>
            ))}
          </Select>
          <Select value={filters.risk} onChange={(event) => setFilters({ risk: event.target.value })}>
            {["All", "Critical", "High", "Medium", "Low"].map((risk) => (
              <option key={risk}>{risk}</option>
            ))}
          </Select>
          <Select value={filters.dateRange} onChange={(event) => setFilters({ dateRange: event.target.value })}>
            {[
              { value: "7", label: "Last 7 days" },
              { value: "30", label: "Last 30 days" },
              { value: "90", label: "Last 90 days" },
              { value: "All", label: "All dates" },
            ].map((range) => (
              <option key={range.value} value={range.value}>
                {range.label}
              </option>
            ))}
          </Select>
          <div className="flex items-center gap-3">
            <Input
              type="number"
              value={filters.minAmount}
              onChange={(event) => setFilters({ minAmount: Number(event.target.value || 0) })}
              placeholder="Min amount"
            />
            <Input
              type="number"
              value={filters.maxAmount}
              onChange={(event) => setFilters({ maxAmount: Number(event.target.value || 0) })}
              placeholder="Max amount"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="grid gap-6 p-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-4">
            <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Session overview</p>
            <h2 className="text-2xl font-semibold">{filteredSnapshot.overview.datasetName}</h2>
            <p className="text-sm leading-7 text-muted-foreground">
              Active session {filteredSnapshot.overview.sessionId} is driving this dashboard from the uploaded dataset. Metrics, fraud analysis, and explanations are rebuilt whenever a new upload is processed.
            </p>
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Records</p>
                <p className="mt-2 text-xl font-semibold">{numberFormatter.format(filteredSnapshot.overview.records)}</p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Columns</p>
                <p className="mt-2 text-xl font-semibold">{filteredSnapshot.overview.columns}</p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Quality</p>
                <p className="mt-2 text-xl font-semibold">{filteredSnapshot.overview.dataQualityScore}%</p>
              </div>
            </div>
          </div>
          <div className="rounded-3xl border border-border/70 bg-background/40 p-5">
            <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Session metadata</p>
            <dl className="mt-4 space-y-3 text-sm text-muted-foreground">
              <div className="flex items-center justify-between gap-3">
                <dt>Session ID</dt>
                <dd className="font-medium text-foreground">{filteredSnapshot.sessionMetadata.sessionId}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt>Upload time</dt>
                <dd className="font-medium text-foreground">{new Date(filteredSnapshot.overview.uploadTime).toLocaleString()}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt>Processing status</dt>
                <dd className="font-medium text-foreground">{filteredSnapshot.overview.processingStatus}</dd>
              </div>
            </dl>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <StatCard label="Total Files" value={String(filteredSnapshot.metrics.totalFiles)} delta="Uploaded scope" icon={FileStack} />
        <StatCard label="Total Records" value={numberFormatter.format(filteredSnapshot.metrics.totalRecords)} delta={`${filteredTransactions.length} visible records`} icon={DatabaseZap} />
        <StatCard label="Fraud Records" value={numberFormatter.format(filteredSnapshot.metrics.fraudRecords)} delta="Needs investigator review" tone="negative" icon={ShieldX} />
        <StatCard label="Safe Records" value={numberFormatter.format(filteredSnapshot.metrics.safeRecords)} delta="Low-risk profile" tone="positive" icon={ShieldCheck} />
        <StatCard label="Fraud Rate" value={percentFormatter.format(filteredSnapshot.metrics.fraudRate)} delta="Share of filtered sample" tone="negative" icon={AlertTriangle} />
        <StatCard label="Risk Score" value={`${filteredSnapshot.metrics.riskScore}/100`} delta="Dataset risk posture" icon={TrendingUp} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardHeader>
            <CardTitle>Dataset summary</CardTitle>
            <CardDescription>Structural overview of the active dataset and the quality profile used for this session.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Rows</p>
              <p className="mt-2 text-2xl font-semibold">{numberFormatter.format(filteredSnapshot.datasetSummary.rows)}</p>
            </div>
            <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Columns</p>
              <p className="mt-2 text-2xl font-semibold">{filteredSnapshot.datasetSummary.columns}</p>
            </div>
            <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Missing values</p>
              <p className="mt-2 text-2xl font-semibold">{filteredSnapshot.datasetSummary.missingValues}</p>
            </div>
            <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Duplicate records</p>
              <p className="mt-2 text-2xl font-semibold">{filteredSnapshot.datasetSummary.duplicateRecords}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Fraud posture</CardTitle>
            <CardDescription>Current risk segmentation and business-critical signals derived from the active dataset.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">High risk</p>
                <p className="mt-2 text-xl font-semibold">{filteredSnapshot.metrics.highRisk}</p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Medium risk</p>
                <p className="mt-2 text-xl font-semibold">{filteredSnapshot.metrics.mediumRisk}</p>
              </div>
              <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Low risk</p>
                <p className="mt-2 text-xl font-semibold">{filteredSnapshot.metrics.lowRisk}</p>
              </div>
            </div>
            <div className="rounded-2xl border border-border/70 bg-background/40 p-4 text-sm leading-7 text-muted-foreground">
              <p className="font-medium text-foreground">{filteredSnapshot.fraudAnalysis.fraudCount} fraud cases identified</p>
              <p>{percentFormatter.format(filteredSnapshot.fraudAnalysis.fraudPercentage)} of the current view is flagged as suspicious or needs manual review.</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <StatusDonutChart title="Fraud Distribution" description="Breakdown of filtered transactions by fraud status." data={filteredSnapshot.fraudDistribution} />
        <StatusDonutChart title="Risk Distribution" description="Spread of records across risk tiers after the current filters are applied." data={filteredSnapshot.riskDistribution} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <MonthlyAnalysisChart data={filteredSnapshot.monthlyAnalysis} />
        <CategoryBarChart title="Category Analysis" description="Volume by category to spot concentrations quickly." data={filteredSnapshot.categoryAnalysis} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <AmountDistributionChart data={filteredSnapshot.amountDistribution} />
        <Card>
          <CardHeader>
            <CardTitle>AI insights</CardTitle>
            <CardDescription>Key patterns and recommendations generated from the active upload.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                <Sparkles className="h-4 w-4 text-primary" />
                {filteredSnapshot.businessInsights[0]?.title}
              </div>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">{filteredSnapshot.businessInsights[0]?.summary}</p>
            </div>
            <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                <BrainCircuit className="h-4 w-4 text-primary" />
                {filteredSnapshot.businessInsights[1]?.title}
              </div>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">{filteredSnapshot.businessInsights[1]?.summary}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <ActivityList items={filteredSnapshot.recentActivities} />
        <InsightList items={filteredSnapshot.topPatterns} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top fraud transactions</CardTitle>
            <CardDescription>Highest-risk transactions surfaced from the active upload.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {filteredSnapshot.fraudAnalysis.topFraudTransactions.map((item) => (
              <div key={item.id} className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium">{item.reference}</p>
                    <p className="text-sm text-muted-foreground">{item.merchant}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{numberFormatter.format(item.amount)}</p>
                    <p className="text-sm text-muted-foreground">{item.riskScore}/100</p>
                  </div>
                </div>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.explanation}</p>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Explainability and review guidance</CardTitle>
            <CardDescription>Business-facing reasoning for the most suspicious transactions.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {filteredSnapshot.aiExplainability.map((item) => (
              <div key={item.id} className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium">{item.transactionId}</p>
                  <p className="text-sm text-muted-foreground">{Math.round(item.confidence * 100)}% confidence</p>
                </div>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.businessExplanation}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
