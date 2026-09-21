import type { DashboardSnapshot, TransactionRecord } from "@/utils/types";

function downloadBlob(filename: string, blob: Blob) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function exportTransactionsToCsv(transactions: TransactionRecord[]) {
  const header = [
    "Reference",
    "Date",
    "Account",
    "Merchant",
    "Category",
    "Amount",
    "Risk Score",
    "Status",
    "Risk Level",
  ];

  const rows = transactions.map((item) => [
    item.reference,
    item.date,
    item.account,
    item.merchant,
    item.category,
    item.amount,
    item.riskScore,
    item.status,
    item.riskLevel,
  ]);

  const csv = [header, ...rows]
    .map((row) => row.map((cell) => `"${String(cell).split('"').join('""')}"`).join(","))
    .join("\n");

  downloadBlob("fraud-analysis-transactions.csv", new Blob([csv], { type: "text/csv" }));
}

export function exportReportAsWord(snapshot: DashboardSnapshot) {
  const content = `
    <html>
      <body>
        <h1>GenAI Fraud Analysis Report</h1>
        <p>Total Records: ${snapshot.metrics.totalRecords}</p>
        <p>Fraud Records: ${snapshot.metrics.fraudRecords}</p>
        <p>Risk Score: ${snapshot.metrics.riskScore}</p>
        <h2>Top Insights</h2>
        <ul>
          ${snapshot.topPatterns.map((item) => `<li><strong>${item.title}</strong>: ${item.summary}</li>`).join("")}
        </ul>
      </body>
    </html>
  `;

  downloadBlob("fraud-analysis-report.doc", new Blob([content], { type: "application/msword" }));
}

export function printReport() {
  window.print();
}
