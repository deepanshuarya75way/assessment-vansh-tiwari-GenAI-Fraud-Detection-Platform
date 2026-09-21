import type { DashboardSnapshot, TransactionRecord } from "@/utils/types";
import { currencyFormatter, percentFormatter } from "@/utils/formatters";

export function answerQuestion(
  question: string,
  snapshot: DashboardSnapshot,
  transactions: TransactionRecord[],
) {
  const normalized = question.toLowerCase();
  const highestRisk = [...transactions].sort((a, b) => b.riskScore - a.riskScore).slice(0, 3);
  const topCategory = [...snapshot.categoryAnalysis].sort((a, b) => b.value - a.value)[0];

  if (normalized.includes("total fraud")) {
    return `The current dataset contains ${snapshot.metrics.fraudRecords} fraud-marked records, representing ${percentFormatter.format(snapshot.metrics.fraudRate)} of the analyzed sample.`;
  }

  if (normalized.includes("highest risk")) {
    return `The highest-risk transactions are ${highestRisk
      .map(
        (item) =>
          `${item.reference} (${item.riskScore}/100, ${currencyFormatter.format(item.amount)})`,
      )
      .join(", ")}.`;
  }

  if (normalized.includes("category") && normalized.includes("fraud")) {
    return `The highest-volume category in the current analysis is ${topCategory.label}, and it is one of the most important segments to review alongside its concentration of flagged activity.`;
  }

  if (normalized.includes("dashboard")) {
    return `The dashboard summarizes uploaded files, record volume, fraud share, and average risk score, then breaks the analysis down by status, risk level, month, category, and transaction amount to help investigators move from detection to explanation.`;
  }

  return `For this uploaded dataset, the leading signals are a ${snapshot.metrics.riskScore}/100 portfolio risk score, ${snapshot.metrics.fraudRecords} fraud records, and elevated concentration in ${topCategory.label}. Ask about risk segments, categories, transactions, or insights and I can summarize them.`;
}
