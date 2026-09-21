import type {
  ActivityItem,
  AnalysisSummary,
  ChartPoint,
  DashboardMetrics,
  DashboardSnapshot,
  InsightItem,
  MonthlyPoint,
  TransactionRecord,
  UploadedDataset,
} from "@/utils/types";

export const mockTransactions: TransactionRecord[] = [
  {
    id: "TXN-90813",
    reference: "REF-90813",
    date: "2026-07-12T09:20:00.000Z",
    account: "ACC-44102",
    merchant: "North Axis Payments",
    category: "Wire Transfer",
    channel: "Online Banking",
    region: "New York",
    amount: 19400,
    riskScore: 93,
    confidence: 0.94,
    status: "Fraud",
    riskLevel: "Critical",
    explanation:
      "Large-value transfer deviates sharply from historical frequency and merchant pattern.",
    affectedFeatures: ["amount_spike", "night_window", "new_beneficiary"],
    flags: ["New beneficiary", "Velocity spike", "Out-of-pattern amount"],
  },
  {
    id: "TXN-90814",
    reference: "REF-90814",
    date: "2026-07-12T10:35:00.000Z",
    account: "ACC-12844",
    merchant: "Cityline Retail",
    category: "Card Payment",
    channel: "POS",
    region: "Chicago",
    amount: 420,
    riskScore: 18,
    confidence: 0.82,
    status: "Safe",
    riskLevel: "Low",
    explanation: "Transaction aligns with user history, amount profile, and usual merchant category.",
    affectedFeatures: ["stable_frequency", "trusted_device"],
    flags: ["Trusted device"],
  },
  {
    id: "TXN-90815",
    reference: "REF-90815",
    date: "2026-07-11T19:05:00.000Z",
    account: "ACC-66789",
    merchant: "Rapid Cargo Global",
    category: "Invoice Payment",
    channel: "Corporate Portal",
    region: "Dallas",
    amount: 8300,
    riskScore: 74,
    confidence: 0.88,
    status: "Review",
    riskLevel: "High",
    explanation:
      "Invoice amount is elevated and destination region is uncommon, but entity is previously seen.",
    affectedFeatures: ["regional_shift", "amount_percentile"],
    flags: ["Uncommon region", "Amount anomaly"],
  },
  {
    id: "TXN-90816",
    reference: "REF-90816",
    date: "2026-07-10T05:55:00.000Z",
    account: "ACC-83402",
    merchant: "Vantage Health Systems",
    category: "ACH Transfer",
    channel: "API",
    region: "San Jose",
    amount: 12150,
    riskScore: 89,
    confidence: 0.91,
    status: "Fraud",
    riskLevel: "Critical",
    explanation:
      "Abnormal execution window plus repeated transfer attempts triggered elevated fraud confidence.",
    affectedFeatures: ["retry_pattern", "execution_time", "counterparty_novelty"],
    flags: ["Odd-hour execution", "Repeated attempts"],
  },
  {
    id: "TXN-90817",
    reference: "REF-90817",
    date: "2026-07-09T14:15:00.000Z",
    account: "ACC-55220",
    merchant: "BluePeak Telecom",
    category: "Subscription",
    channel: "Card on File",
    region: "Boston",
    amount: 96,
    riskScore: 12,
    confidence: 0.79,
    status: "Safe",
    riskLevel: "Low",
    explanation: "Recurring payment with consistent cadence and existing merchant fingerprint.",
    affectedFeatures: ["recurring_pattern", "merchant_stability"],
    flags: ["Recurring payment"],
  },
  {
    id: "TXN-90818",
    reference: "REF-90818",
    date: "2026-07-09T16:40:00.000Z",
    account: "ACC-41028",
    merchant: "Helix Trade Supply",
    category: "Vendor Settlement",
    channel: "Online Banking",
    region: "Seattle",
    amount: 6750,
    riskScore: 67,
    confidence: 0.85,
    status: "Review",
    riskLevel: "Medium",
    explanation: "Transfer is within range but beneficiary behavior changed over the past 30 days.",
    affectedFeatures: ["beneficiary_shift", "sequence_gap"],
    flags: ["Behavior drift"],
  },
  {
    id: "TXN-90819",
    reference: "REF-90819",
    date: "2026-07-08T11:10:00.000Z",
    account: "ACC-99510",
    merchant: "Nimbus Travel",
    category: "Expense Claim",
    channel: "Internal Portal",
    region: "Austin",
    amount: 2280,
    riskScore: 84,
    confidence: 0.9,
    status: "Fraud",
    riskLevel: "High",
    explanation:
      "Expense category and timing conflict with policy rules and prior employee activity window.",
    affectedFeatures: ["policy_conflict", "timing_violation"],
    flags: ["Policy mismatch", "Atypical cadence"],
  },
  {
    id: "TXN-90820",
    reference: "REF-90820",
    date: "2026-07-08T17:25:00.000Z",
    account: "ACC-66218",
    merchant: "Riverstone Office",
    category: "Office Spend",
    channel: "Card on File",
    region: "Atlanta",
    amount: 315,
    riskScore: 26,
    confidence: 0.76,
    status: "Safe",
    riskLevel: "Low",
    explanation: "Vendor and amount fall within normal office procurement range.",
    affectedFeatures: ["merchant_history", "amount_baseline"],
    flags: ["Stable merchant"],
  },
  {
    id: "TXN-90821",
    reference: "REF-90821",
    date: "2026-07-07T21:15:00.000Z",
    account: "ACC-15542",
    merchant: "Quantum Brokerage",
    category: "Securities Transfer",
    channel: "Corporate Portal",
    region: "New York",
    amount: 14750,
    riskScore: 78,
    confidence: 0.89,
    status: "Review",
    riskLevel: "High",
    explanation:
      "Beneficiary is known, but transfer pattern differs from the portfolio team baseline.",
    affectedFeatures: ["portfolio_drift", "volume_change"],
    flags: ["Behavior anomaly"],
  },
  {
    id: "TXN-90822",
    reference: "REF-90822",
    date: "2026-07-07T08:40:00.000Z",
    account: "ACC-30287",
    merchant: "Apex Cloud Works",
    category: "Software Billing",
    channel: "API",
    region: "San Francisco",
    amount: 5600,
    riskScore: 22,
    confidence: 0.81,
    status: "Safe",
    riskLevel: "Low",
    explanation: "Billing matches contract schedule and expected procurement controls.",
    affectedFeatures: ["contract_alignment", "scheduled_billing"],
    flags: ["Scheduled vendor"],
  },
  {
    id: "TXN-90823",
    reference: "REF-90823",
    date: "2026-07-06T13:50:00.000Z",
    account: "ACC-42876",
    merchant: "Metro Claims Hub",
    category: "Insurance Payout",
    channel: "Internal Portal",
    region: "Miami",
    amount: 9720,
    riskScore: 87,
    confidence: 0.92,
    status: "Fraud",
    riskLevel: "Critical",
    explanation:
      "Claim amount and beneficiary timeline diverge from policy maturity and prior claim graph.",
    affectedFeatures: ["claim_graph_shift", "policy_maturity_gap"],
    flags: ["Claim anomaly", "Beneficiary mismatch"],
  },
  {
    id: "TXN-90824",
    reference: "REF-90824",
    date: "2026-07-05T15:35:00.000Z",
    account: "ACC-76312",
    merchant: "Terra Freight Lines",
    category: "Logistics Payment",
    channel: "Online Banking",
    region: "Denver",
    amount: 4920,
    riskScore: 34,
    confidence: 0.77,
    status: "Safe",
    riskLevel: "Low",
    explanation: "Freight settlement aligns with historic vendor volume and expected invoice window.",
    affectedFeatures: ["invoice_match", "vendor_consistency"],
    flags: ["Invoice matched"],
  },
];

export const recentAnalyses: AnalysisSummary[] = [
  {
    id: "analysis-q2",
    name: "Q2 Card Settlement Review",
    createdAt: "2026-07-12T08:00:00.000Z",
    totalRecords: 184920,
    fraudRate: 0.064,
    riskScore: 71,
    files: 3,
  },
  {
    id: "analysis-claims",
    name: "Insurance Claims Audit",
    createdAt: "2026-07-10T13:20:00.000Z",
    totalRecords: 98214,
    fraudRate: 0.041,
    riskScore: 64,
    files: 2,
  },
  {
    id: "analysis-wire",
    name: "Cross-Border Wire Scan",
    createdAt: "2026-07-06T16:10:00.000Z",
    totalRecords: 76402,
    fraudRate: 0.089,
    riskScore: 78,
    files: 1,
  },
];

function groupCount<T extends string>(items: T[]) {
  return items.reduce<Record<string, number>>((acc, item) => {
    acc[item] = (acc[item] ?? 0) + 1;
    return acc;
  }, {});
}

function toChartPoints(record: Record<string, number>): ChartPoint[] {
  return Object.entries(record).map(([label, value]) => ({ label, value }));
}

function buildMonthlyAnalysis(transactions: TransactionRecord[]): MonthlyPoint[] {
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"];
  return months.map((month, index) => {
    const fraud = 12 + index * 3;
    const safe = 54 + index * 4;
    const review = 16 + index * 2;
    return { month, fraud, safe, review };
  });
}

function buildActivities(transactions: TransactionRecord[]): ActivityItem[] {
  return transactions.slice(0, 5).map((transaction, index) => ({
    id: transaction.id,
    title:
      transaction.status === "Fraud"
        ? `Fraud escalation created for ${transaction.reference}`
        : `Transaction ${transaction.reference} reviewed`,
    description: `${transaction.category} from ${transaction.merchant} in ${transaction.region}`,
    time: transaction.date,
    tone:
      transaction.status === "Fraud"
        ? "danger"
        : transaction.status === "Review"
          ? "warning"
          : index === 0
            ? "success"
            : "neutral",
  }));
}

function buildInsights(transactions: TransactionRecord[]): InsightItem[] {
  return [
    {
      id: "insight-1",
      title: "Wire transfer category carries the highest weighted risk density",
      summary:
        "High-value transfer patterns and new beneficiary relationships are driving the sharpest fraud concentration.",
      severity: "critical",
    },
    {
      id: "insight-2",
      title: "Odd-hour transactions show elevated review-to-fraud conversion",
      summary:
        "Transactions executed outside standard processing windows are overrepresented in critical risk records.",
      severity: "elevated",
    },
    {
      id: "insight-3",
      title: "Known vendors continue to dominate safe transaction volume",
      summary:
        "Recurring software, office spend, and logistics payments remain stable with low anomaly pressure.",
      severity: "informational",
    },
  ];
}

export function createDashboardSnapshot(
  uploads: UploadedDataset[],
  transactions: TransactionRecord[] = mockTransactions,
): DashboardSnapshot {
  const sample = transactions.length > 0 ? transactions : mockTransactions;
  const fraudRecords = transactions.filter((item) => item.status === "Fraud").length;
  const safeRecords = transactions.filter((item) => item.status === "Safe").length;
  const totalRecords = transactions.length;
  const averageRisk = sample.reduce((total, item) => total + item.riskScore, 0) / sample.length;

  const metrics: DashboardMetrics = {
    totalFiles: uploads.length || 3,
    totalRecords: uploads.reduce((total, file) => total + file.rows, 0) || totalRecords * 1243,
    fraudRecords,
    safeRecords,
    fraudRate: totalRecords > 0 ? fraudRecords / totalRecords : 0,
    riskScore: Math.round(averageRisk),
    highRisk: transactions.filter((item) => item.riskLevel === "High" || item.riskLevel === "Critical").length,
    mediumRisk: transactions.filter((item) => item.riskLevel === "Medium").length,
    lowRisk: transactions.filter((item) => item.riskLevel === "Low").length,
    dataQuality: 92,
  };

  const fraudDistribution = toChartPoints(groupCount(transactions.map((item) => item.status)));
  const riskDistribution = toChartPoints(groupCount(transactions.map((item) => item.riskLevel)));
  const categoryAnalysis = toChartPoints(groupCount(transactions.map((item) => item.category)));
  const amountDistribution: ChartPoint[] = [
    { label: "0-1K", value: transactions.filter((item) => item.amount < 1000).length },
    {
      label: "1K-5K",
      value: transactions.filter((item) => item.amount >= 1000 && item.amount < 5000).length,
    },
    {
      label: "5K-10K",
      value: transactions.filter((item) => item.amount >= 5000 && item.amount < 10000).length,
    },
    {
      label: "10K+",
      value: transactions.filter((item) => item.amount >= 10000).length,
    },
  ];

  return {
    metrics,
    fraudDistribution,
    riskDistribution,
    monthlyAnalysis: buildMonthlyAnalysis(transactions),
    categoryAnalysis,
    amountDistribution,
    recentActivities: buildActivities(transactions),
    topPatterns: buildInsights(transactions),
    overview: {
      datasetName: uploads[0]?.name ?? "Uploaded dataset",
      sessionId: "mock-session",
      uploadTime: uploads[0]?.uploadedAt ?? new Date().toISOString(),
      records: totalRecords,
      columns: uploads.flatMap((item) => item.columns).length,
      processingStatus: "Completed",
      dataQualityScore: 92,
    },
    datasetSummary: {
      rows: totalRecords,
      columns: uploads.flatMap((item) => item.columns).length,
      missingValues: 0,
      duplicateRecords: 0,
      categoricalColumns: ["category", "merchant", "region"],
      numericColumns: ["amount", "riskScore"],
      dataSize: uploads.reduce((sum, item) => sum + item.size, 0),
    },
    fraudAnalysis: {
      fraudCount: fraudRecords,
      fraudPercentage: totalRecords > 0 ? fraudRecords / totalRecords : 0,
      fraudByCategory: [],
      fraudByMerchant: [],
      fraudByLocation: [],
      fraudByTime: [],
      fraudByAmount: [],
      topFraudTransactions: [],
    },
    riskAnalysis: {
      overallRiskScore: Math.round(averageRisk),
      riskDistribution: [],
      highRiskAreas: [],
      highRiskMerchants: [],
      highRiskTime: [],
      highRiskCategories: [],
    },
    trendAnalysis: {
      hourlyTrend: [],
      dailyTrend: [],
      weeklyTrend: [],
      monthlyTrend: [],
      yearlyTrend: [],
      trendSummary: "Mock snapshot",
    },
    businessInsights: buildInsights(transactions),
    filters: {
      search: "",
      category: "All",
      status: "All",
      risk: "All",
      dateRange: "All",
      minAmount: 0,
      maxAmount: 25000,
    },
    fraudTable: [],
    aiExplainability: [],
    recommendations: [],
    sessionMetadata: {
      sessionId: "mock-session",
      datasetName: uploads[0]?.name ?? "Uploaded dataset",
      uploadTime: uploads[0]?.uploadedAt ?? new Date().toISOString(),
      processingTime: "0 sec",
      modelVersion: "mock",
      analysisVersion: "mock",
    },
    charts: {
      fraudDistribution,
      riskDistribution,
      categoryDistribution: [],
      amountDistribution,
      monthlyAnalysis: buildMonthlyAnalysis(transactions),
    },
  };
}
