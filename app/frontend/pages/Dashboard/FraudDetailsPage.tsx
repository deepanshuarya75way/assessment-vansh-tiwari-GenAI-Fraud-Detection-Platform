import { useAnalysis } from "@/hooks/use-analysis";
import { filterTransactions } from "@/services/analysisService";
import { PageHeading } from "@/components/common/PageHeading";
import { SearchInput } from "@/components/common/SearchInput";
import { FraudTable } from "@/components/tables/FraudTable";
import { Card, CardContent } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

export function FraudDetailsPage() {
  const { transactions, filters, setFilters } = useAnalysis();
  const filteredTransactions = filterTransactions(transactions, filters);
  const categories = ["All", ...new Set(transactions.map((item) => item.category))];

  return (
    <div className="space-y-8">
      <PageHeading
        eyebrow="Fraud Details"
        title="Investigate suspicious transactions with filters, sorting, and pagination"
        description="This table is focused on record review, helping investigators isolate the transactions that need action first."
      />

      <Card>
        <CardContent className="grid gap-4 p-6 md:grid-cols-2 xl:grid-cols-4">
          <SearchInput
            value={filters.search}
            onChange={(value) => setFilters({ search: value })}
            placeholder="Search by transaction, merchant, account"
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
        </CardContent>
      </Card>

      <div className="flex flex-wrap gap-3">
        <Badge tone="danger">
          Fraud: {filteredTransactions.filter((item) => item.status === "Fraud").length}
        </Badge>
        <Badge tone="warning">
          Review: {filteredTransactions.filter((item) => item.status === "Review").length}
        </Badge>
        <Badge tone="success">
          Safe: {filteredTransactions.filter((item) => item.status === "Safe").length}
        </Badge>
      </div>

      <FraudTable data={filteredTransactions} />
    </div>
  );
}
