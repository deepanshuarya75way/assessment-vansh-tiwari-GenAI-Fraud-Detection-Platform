import type { FraudFilters, TransactionRecord } from "@/utils/types";

export function filterTransactions(transactions: TransactionRecord[], filters: FraudFilters) {
  const latestDate = transactions
    .map((item) => new Date(item.date).getTime())
    .reduce((max, value) => Math.max(max, value), 0);

  return transactions.filter((transaction) => {
    const matchesSearch =
      !filters.search ||
      [transaction.reference, transaction.merchant, transaction.account, transaction.category]
        .join(" ")
        .toLowerCase()
        .includes(filters.search.toLowerCase());

    const matchesCategory =
      filters.category === "All" || transaction.category === filters.category;
    const matchesStatus = filters.status === "All" || transaction.status === filters.status;
    const matchesRisk = filters.risk === "All" || transaction.riskLevel === filters.risk;
    const matchesAmount =
      transaction.amount >= filters.minAmount && transaction.amount <= filters.maxAmount;

    const withinSelectedRange =
      filters.dateRange === "All"
        ? true
        : latestDate - new Date(transaction.date).getTime() <= Number(filters.dateRange) * 86400000;

    return (
      matchesSearch &&
      matchesCategory &&
      matchesStatus &&
      matchesRisk &&
      matchesAmount &&
      withinSelectedRange
    );
  });
}
