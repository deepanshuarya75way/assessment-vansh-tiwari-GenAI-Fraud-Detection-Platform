import type {
  ActivityItem,
  ChartPoint,
  DashboardMetrics,
  DashboardSnapshot,
  ExplainabilityItem,
  FraudFilters,
  InsightItem,
  MonthlyPoint,
  RecommendationItem,
  TransactionRecord,
  UploadedDataset,
} from "@/utils/types";

function normalizeString(value: unknown): string {
  if (value === null || value === undefined) return "";
  return String(value).trim();
}

function parseNumber(value: unknown): number {
  if (value === null || value === undefined) return 0;
  const parsed = Number(String(value).replace(/[^0-9.-]/g, ""));
  return Number.isFinite(parsed) ? parsed : 0;
}

function inferStatus(statusValue: unknown, riskScore: number): TransactionRecord["status"] {
  const normalized = normalizeString(statusValue).toLowerCase();
  if (normalized.includes("fraud") || normalized.includes("suspicious") || normalized.includes("anom")) {
    return "Fraud";
  }
  if (normalized.includes("review") || normalized.includes("hold") || riskScore >= 65) {
    return "Review";
  }
  return "Safe";
}

function inferRiskLevel(riskScore: number): TransactionRecord["riskLevel"] {
  if (riskScore >= 80) return "Critical";
  if (riskScore >= 60) return "High";
  if (riskScore >= 35) return "Medium";
  return "Low";
}

function buildReference(row: unknown[], aliases: string[], index: number): string {
  const direct = aliases
    .map((alias) => row[alias.length - 1])
    .find((value) => normalizeString(value));
  return normalizeString(direct) || `TXN-${index + 1}`;
}

function getFieldValue(row: (string | number | null)[], columns: string[], aliases: string[]) {
  const index = columns.findIndex((column) => aliases.includes(column.toLowerCase()));
  if (index >= 0) return row[index];
  return undefined;
}

function groupCounts<T extends string>(items: T[]) {
  return items.reduce<Record<string, number>>((acc, item) => {
    acc[item] = (acc[item] ?? 0) + 1;
    return acc;
  }, {});
}

function toChartPoints(record: Record<string, number>): ChartPoint[] {
  return Object.entries(record).map(([label, value]) => ({ label, value }));
}

function toMonthlyTrend(transactions: TransactionRecord[]): MonthlyPoint[] {
  const buckets = new Map<string, { fraud: number; safe: number; review: number }>();
  transactions.forEach((transaction) => {
    const timestamp = new Date(transaction.date);
    const month = timestamp.toLocaleString("en", { month: "short" });
    const entry = buckets.get(month) ?? { fraud: 0, safe: 0, review: 0 };
    if (transaction.status === "Fraud") entry.fraud += 1;
    else if (transaction.status === "Review") entry.review += 1;
    else entry.safe += 1;
    buckets.set(month, entry);
  });

  return ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    .filter((month) => buckets.has(month))
    .map((month) => ({ month, ...buckets.get(month)! }));
}

export function deriveTransactionsFromUploads(uploads: UploadedDataset[]): TransactionRecord[] {
  return uploads.flatMap((upload, uploadIndex) => {
    const columns = upload.columns.map((column) => column.toLowerCase());
    const rows = upload.preview ?? [];

    return rows.map((row, rowIndex) => {
      const amountValue = getFieldValue(row, upload.columns, ["amount", "amount_usd", "transaction_amount", "value"]);
      const merchantValue = getFieldValue(row, upload.columns, ["merchant", "merchant_name", "counterparty"]);
      const categoryValue = getFieldValue(row, upload.columns, ["category", "transaction_category", "type"]);
      const locationValue = getFieldValue(row, upload.columns, ["location", "region", "country", "city"]);
      const dateValue = getFieldValue(row, upload.columns, ["date", "timestamp", "created_at", "transaction_date"]);
      const riskValue = getFieldValue(row, upload.columns, ["risk_score", "risk", "score"]);
      const confidenceValue = getFieldValue(row, upload.columns, ["confidence", "confidence_score"]);
      const statusValue = getFieldValue(row, upload.columns, ["status", "label", "predicted_label", "fraud_status"]);
      const transactionIdValue = getFieldValue(row, upload.columns, ["transaction_id", "id", "reference", "txn_id"]);
      const amount = parseNumber(amountValue);
      const riskScore = Math.max(5, Math.min(95, Math.round(parseNumber(riskValue) || Math.max(12, Math.min(92, amount / 200)))));
      const status = inferStatus(statusValue, riskScore);
      const date = normalizeString(dateValue) || new Date(Date.now() - uploadIndex * 86400000 - rowIndex * 3600000).toISOString();

      return {
        id: normalizeString(transactionIdValue) || `txn-${uploadIndex + 1}-${rowIndex + 1}`,
        reference: normalizeString(transactionIdValue) || `REF-${uploadIndex + 1}${rowIndex + 1}`,
        date,
        account: `ACC-${uploadIndex + 1}${rowIndex + 1}`,
        merchant: normalizeString(merchantValue) || `Merchant ${uploadIndex + 1}`,
        category: normalizeString(categoryValue) || "General",
        channel: "Uploaded Dataset",
        region: normalizeString(locationValue) || "Unknown",
        amount: Number.isFinite(amount) ? amount : 0,
        riskScore,
        confidence: Math.max(0.6, Math.min(0.99, parseNumber(confidenceValue) / 100 || 0.82)),
        status,
        riskLevel: inferRiskLevel(riskScore),
        explanation: `Pattern derived from ${upload.name} for ${normalizeString(categoryValue) || "this transaction"}.`,
        affectedFeatures: ["amount_profile", "behavioral_shift", "merchant_context"],
        flags: status === "Fraud" ? ["Elevated anomaly score"] : ["Baseline review"],
      } satisfies TransactionRecord;
    });
  });
}

export function createDashboardSnapshot(
  uploads: UploadedDataset[],
  transactions: TransactionRecord[] = [],
  sessionName?: string,
): DashboardSnapshot {
  const derivedTransactions = transactions.length > 0 ? transactions : deriveTransactionsFromUploads(uploads);
  const totalRows = uploads.reduce((sum, upload) => sum + upload.rows, 0) || derivedTransactions.length;
  const totalFiles = uploads.length;
  const fraudTransactions = derivedTransactions.filter((item) => item.status === "Fraud");
  const reviewTransactions = derivedTransactions.filter((item) => item.status === "Review");
  const safeTransactions = derivedTransactions.filter((item) => item.status === "Safe");
  const fraudRate = derivedTransactions.length > 0 ? fraudTransactions.length / derivedTransactions.length : 0;
  const averageRisk = derivedTransactions.length > 0
    ? derivedTransactions.reduce((sum, item) => sum + item.riskScore, 0) / derivedTransactions.length
    : 0;
  const highRisk = derivedTransactions.filter((item) => item.riskLevel === "High" || item.riskLevel === "Critical").length;
  const mediumRisk = derivedTransactions.filter((item) => item.riskLevel === "Medium").length;
  const lowRisk = derivedTransactions.filter((item) => item.riskLevel === "Low").length;

  const columns = uploads.flatMap((upload) => upload.columns);
  const uniqueColumns = Array.from(new Set(columns));
  const missingValues = uploads.reduce((sum, upload) => {
    const previewRows = upload.preview ?? [];
    return sum + previewRows.reduce((innerSum, row) => innerSum + row.filter((cell) => normalizeString(cell) === "").length, 0);
  }, 0);
  const duplicateRecords = Math.max(0, derivedTransactions.length - new Set(derivedTransactions.map((item) => item.reference)).size);
  const categoricalColumns = uniqueColumns.filter((column) => !/amount|risk|score|confidence|id|date|timestamp/i.test(column));
  const numericColumns = uniqueColumns.filter((column) => /amount|risk|score|confidence|count|value/i.test(column));
  const dataSize = uploads.reduce((sum, upload) => sum + upload.size, 0);

  const fraudByCategory = toChartPoints(groupCounts(fraudTransactions.map((item) => item.category)));
  const fraudByMerchant = toChartPoints(groupCounts(fraudTransactions.map((item) => item.merchant).slice(0, 6)));
  const fraudByLocation = toChartPoints(groupCounts(fraudTransactions.map((item) => item.region)));
  const fraudByTime = toChartPoints(groupCounts(fraudTransactions.map((item) => item.date.slice(11, 13))));
  const fraudByAmount = [
    { label: "Under 1K", value: fraudTransactions.filter((item) => item.amount < 1000).length },
    { label: "1K-5K", value: fraudTransactions.filter((item) => item.amount >= 1000 && item.amount < 5000).length },
    { label: "5K-10K", value: fraudTransactions.filter((item) => item.amount >= 5000 && item.amount < 10000).length },
    { label: "10K+", value: fraudTransactions.filter((item) => item.amount >= 10000).length },
  ];

  const riskDistribution = toChartPoints(groupCounts(derivedTransactions.map((item) => item.riskLevel)));
  const categoryDistribution = toChartPoints(groupCounts(derivedTransactions.map((item) => item.category)));
  const amountDistribution = [
    { label: "0-1K", value: derivedTransactions.filter((item) => item.amount < 1000).length },
    { label: "1K-5K", value: derivedTransactions.filter((item) => item.amount >= 1000 && item.amount < 5000).length },
    { label: "5K-10K", value: derivedTransactions.filter((item) => item.amount >= 5000 && item.amount < 10000).length },
    { label: "10K+", value: derivedTransactions.filter((item) => item.amount >= 10000).length },
  ];

  const topMerchant = fraudTransactions[0]?.merchant ?? "No high-risk merchant detected";
  const topLocation = fraudTransactions[0]?.region ?? "No high-risk region detected";
  const topCategory = fraudTransactions[0]?.category ?? "No high-risk category detected";

  const metrics: DashboardMetrics = {
    totalFiles,
    totalRecords: totalRows,
    fraudRecords: fraudTransactions.length,
    safeRecords: safeTransactions.length,
    fraudRate,
    riskScore: Math.round(averageRisk),
    highRisk,
    mediumRisk,
    lowRisk,
    dataQuality: Math.max(0, 100 - Math.round(missingValues / Math.max(1, totalRows) * 100)),
  };

  const overview = {
    datasetName: uploads[0]?.name ?? sessionName ?? "Uploaded dataset",
    sessionId: sessionName ?? "active-session",
    uploadTime: uploads[0]?.uploadedAt ?? new Date().toISOString(),
    records: totalRows,
    columns: uniqueColumns.length,
    processingStatus: fraudTransactions.length > 0 ? "Completed" : "Waiting for processing",
    dataQualityScore: metrics.dataQuality,
  };

  const datasetSummary = {
    rows: totalRows,
    columns: uniqueColumns.length,
    missingValues: missingValues,
    duplicateRecords,
    categoricalColumns: categoricalColumns.slice(0, 8),
    numericColumns: numericColumns.slice(0, 8),
    dataSize,
  };

  const fraudAnalysis = {
    fraudCount: fraudTransactions.length,
    fraudPercentage: fraudRate,
    fraudByCategory,
    fraudByMerchant,
    fraudByLocation,
    fraudByTime,
    fraudByAmount,
    topFraudTransactions: fraudTransactions.slice(0, 8).map((transaction) => ({
      id: transaction.id,
      reference: transaction.reference,
      merchant: transaction.merchant,
      amount: transaction.amount,
      riskScore: transaction.riskScore,
      confidence: transaction.confidence,
      explanation: transaction.explanation,
    })),
  };

  const riskAnalysis = {
    overallRiskScore: metrics.riskScore,
    riskDistribution,
    highRiskAreas: fraudByLocation.slice(0, 4),
    highRiskMerchants: fraudByMerchant.slice(0, 4),
    highRiskTime: fraudByTime.slice(0, 4),
    highRiskCategories: fraudByCategory.slice(0, 4),
  };

  const trendAnalysis = {
    hourlyTrend: fraudTransactions.slice(0, 6).map((transaction) => ({ label: transaction.date.slice(11, 13), value: transaction.riskScore })),
    dailyTrend: toMonthlyTrend(derivedTransactions).slice(0, 5),
    weeklyTrend: fraudByCategory.slice(0, 4),
    monthlyTrend: toMonthlyTrend(derivedTransactions),
    yearlyTrend: fraudByCategory.slice(0, 4),
    trendSummary: `${fraudTransactions.length} suspicious patterns detected across ${Math.max(1, derivedTransactions.length)} transactions.`,
  };

  const businessInsights: InsightItem[] = [
    {
      id: "insight-merchant",
      title: `Most suspicious merchant: ${topMerchant}`,
      summary: `High-risk behavior is clustering around ${topMerchant} with elevated fraud confidence.`,
      severity: "critical",
    },
    {
      id: "insight-location",
      title: `Most risky location: ${topLocation}`,
      summary: `The highest concentration of anomalous activity appears in ${topLocation}.`,
      severity: "elevated",
    },
    {
      id: "insight-pattern",
      title: `Most common fraud pattern: ${topCategory}`,
      summary: `Review queues are concentrated around ${topCategory} transactions with above-baseline risk.`,
      severity: "informational",
    },
  ];

  const recommendations: RecommendationItem[] = [
    {
      id: "recommendation-1",
      title: "Increase monitoring for high-risk merchants",
      detail: "Route these transactions to manual review and tighten thresholding for repeat anomalies.",
      priority: "high",
    },
    {
      id: "recommendation-2",
      title: "Review risky regions during business hours",
      detail: "Focus attention on location clusters before they become repeated financial losses.",
      priority: "medium",
    },
  ];

  const aiExplainability: ExplainabilityItem[] = fraudTransactions.slice(0, 6).map((transaction) => ({
    id: transaction.id,
    transactionId: transaction.reference,
    reason: transaction.explanation,
    confidence: transaction.confidence,
    importantFeatures: transaction.affectedFeatures,
    riskFactors: transaction.flags,
    businessExplanation: `${transaction.merchant} shows ${transaction.status.toLowerCase()} characteristics that warrant investigation.`,
  }));

  const filters: FraudFilters = {
    search: "",
    category: "All",
    status: "All",
    risk: "All",
    dateRange: "All",
    minAmount: 0,
    maxAmount: Math.max(...derivedTransactions.map((item) => item.amount), 100000),
  };

  const fraudTable = derivedTransactions.slice(0, 12).map((transaction) => ({
    transactionId: transaction.reference,
    amount: transaction.amount,
    merchant: transaction.merchant,
    category: transaction.category,
    location: transaction.region,
    riskScore: transaction.riskScore,
    fraudStatus: transaction.status,
    confidenceScore: transaction.confidence,
    aiExplanation: transaction.explanation,
  }));

  const charts = {
    fraudDistribution: fraudByCategory,
    riskDistribution,
    categoryDistribution,
    amountDistribution,
    monthlyAnalysis: toMonthlyTrend(derivedTransactions),
  };

  const sessionMetadata = {
    sessionId: sessionName ?? "active-session",
    datasetName: uploads[0]?.name ?? "Uploaded dataset",
    uploadTime: uploads[0]?.uploadedAt ?? new Date().toISOString(),
    processingTime: `${Math.max(1, derivedTransactions.length)} sec`,
    modelVersion: "fraud-ensemble-v1",
    analysisVersion: "dashboard-v2",
  };

  return {
    metrics,
    fraudDistribution: charts.fraudDistribution,
    riskDistribution: charts.riskDistribution,
    monthlyAnalysis: charts.monthlyAnalysis,
    categoryAnalysis: charts.categoryDistribution,
    amountDistribution: charts.amountDistribution,
    recentActivities: derivedTransactions.slice(0, 5).map((transaction) => ({
      id: transaction.id,
      title: transaction.status === "Fraud" ? `Fraud escalation for ${transaction.reference}` : `Review completed for ${transaction.reference}`,
      description: `${transaction.category} • ${transaction.merchant}`,
      time: transaction.date,
      tone: transaction.status === "Fraud" ? "danger" : transaction.status === "Review" ? "warning" : "success",
    })),
    topPatterns: businessInsights,
    overview,
    datasetSummary,
    fraudAnalysis,
    riskAnalysis,
    trendAnalysis,
    businessInsights,
    filters,
    fraudTable,
    aiExplainability,
    recommendations,
    sessionMetadata,
    charts,
  } as DashboardSnapshot;
}

export const mockTransactions: TransactionRecord[] = [];
export const recentAnalyses = [];
