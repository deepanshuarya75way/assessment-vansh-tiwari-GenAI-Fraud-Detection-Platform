export type ThemeMode = "light" | "dark";

export type UploadStatus = "valid" | "warning" | "processing";
export type FraudStatus = "Fraud" | "Safe" | "Review";
export type RiskLevel = "Critical" | "High" | "Medium" | "Low";
export type SortDirection = "asc" | "desc";

export interface UploadedDataset {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: string;
  rows: number;
  columns: string[];
  preview: string[][];
  validation: {
    status: UploadStatus;
    message: string;
  };
}

export interface TransactionRecord {
  id: string;
  reference: string;
  date: string;
  account: string;
  merchant: string;
  category: string;
  channel: string;
  region: string;
  amount: number;
  riskScore: number;
  confidence: number;
  status: FraudStatus;
  riskLevel: RiskLevel;
  explanation: string;
  affectedFeatures: string[];
  flags: string[];
}

export interface ActivityItem {
  id: string;
  title: string;
  description: string;
  time: string;
  tone: "neutral" | "success" | "warning" | "danger";
}

export interface InsightItem {
  id: string;
  title: string;
  summary: string;
  severity: "informational" | "elevated" | "critical";
}

export interface ChartPoint {
  label: string;
  value: number;
}

export interface MonthlyPoint {
  month: string;
  fraud: number;
  safe: number;
  review: number;
}

export interface AnalysisSummary {
  id: string;
  name: string;
  createdAt: string;
  totalRecords: number;
  fraudRate: number;
  riskScore: number;
  files: number;
}

export interface ProcessingStep {
  id: string;
  title: string;
  detail: string;
}

export interface DashboardMetrics {
  totalFiles: number;
  totalRecords: number;
  fraudRecords: number;
  safeRecords: number;
  fraudRate: number;
  riskScore: number;
  highRisk: number;
  mediumRisk: number;
  lowRisk: number;
  dataQuality: number;
}

export interface OverviewSection {
  datasetName: string;
  sessionId: string;
  uploadTime: string;
  records: number;
  columns: number;
  processingStatus: string;
  dataQualityScore: number;
}

export interface DatasetSummarySection {
  rows: number;
  columns: number;
  missingValues: number;
  duplicateRecords: number;
  categoricalColumns: string[];
  numericColumns: string[];
  dataSize: number;
}

export interface FraudAnalysisSection {
  fraudCount: number;
  fraudPercentage: number;
  fraudByCategory: ChartPoint[];
  fraudByMerchant: ChartPoint[];
  fraudByLocation: ChartPoint[];
  fraudByTime: ChartPoint[];
  fraudByAmount: ChartPoint[];
  topFraudTransactions: Array<{
    id: string;
    reference: string;
    merchant: string;
    amount: number;
    riskScore: number;
    confidence: number;
    explanation: string;
  }>;
}

export interface RiskAnalysisSection {
  overallRiskScore: number;
  riskDistribution: ChartPoint[];
  highRiskAreas: ChartPoint[];
  highRiskMerchants: ChartPoint[];
  highRiskTime: ChartPoint[];
  highRiskCategories: ChartPoint[];
}

export interface TrendAnalysisSection {
  hourlyTrend: ChartPoint[];
  dailyTrend: MonthlyPoint[];
  weeklyTrend: ChartPoint[];
  monthlyTrend: MonthlyPoint[];
  yearlyTrend: ChartPoint[];
  trendSummary: string;
}

export interface RecommendationItem {
  id: string;
  title: string;
  detail: string;
  priority: "high" | "medium" | "low";
}

export interface ExplainabilityItem {
  id: string;
  transactionId: string;
  reason: string;
  confidence: number;
  importantFeatures: string[];
  riskFactors: string[];
  businessExplanation: string;
}

export interface DashboardSnapshot {
  metrics: DashboardMetrics;
  fraudDistribution: ChartPoint[];
  riskDistribution: ChartPoint[];
  monthlyAnalysis: MonthlyPoint[];
  categoryAnalysis: ChartPoint[];
  amountDistribution: ChartPoint[];
  recentActivities: ActivityItem[];
  topPatterns: InsightItem[];
  overview: OverviewSection;
  datasetSummary: DatasetSummarySection;
  fraudAnalysis: FraudAnalysisSection;
  riskAnalysis: RiskAnalysisSection;
  trendAnalysis: TrendAnalysisSection;
  businessInsights: InsightItem[];
  filters: FraudFilters;
  fraudTable: Array<{
    transactionId: string;
    amount: number;
    merchant: string;
    category: string;
    location: string;
    riskScore: number;
    fraudStatus: FraudStatus;
    confidenceScore: number;
    aiExplanation: string;
  }>;
  aiExplainability: ExplainabilityItem[];
  recommendations: RecommendationItem[];
  sessionMetadata: {
    sessionId: string;
    datasetName: string;
    uploadTime: string;
    processingTime: string;
    modelVersion: string;
    analysisVersion: string;
  };
  charts: {
    fraudDistribution: ChartPoint[];
    riskDistribution: ChartPoint[];
    categoryDistribution: ChartPoint[];
    amountDistribution: ChartPoint[];
    monthlyAnalysis: MonthlyPoint[];
  };
}

export interface FraudFilters {
  search: string;
  category: string;
  status: string;
  risk: string;
  dateRange: string;
  minAmount: number;
  maxAmount: number;
}

export interface ChatMessage {
  id: string;
  role: "assistant" | "user";
  content: string;
  createdAt: string;
}
