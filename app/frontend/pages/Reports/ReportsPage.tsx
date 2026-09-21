import { ReportViewer } from "@/components/reports/ReportViewer";
import { PageHeading } from "@/components/common/PageHeading";

export function ReportsPage() {
  return (
    <div className="space-y-8">
      <PageHeading
        eyebrow="AI Report"
        title="Executive and analyst-ready reporting from the current analysis state"
        description="Summaries, dataset metrics, fraud findings, recommendations, and export actions are consolidated into a single report screen."
      />

      <ReportViewer />
    </div>
  );
}
