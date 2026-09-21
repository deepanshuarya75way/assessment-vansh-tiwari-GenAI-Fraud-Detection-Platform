import { ResponsiveContainer, Tooltip, FunnelChart, Funnel, LabelList } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { ChartPoint } from "@/utils/types";

interface AmountDistributionChartProps {
  data: ChartPoint[];
}

export function AmountDistributionChart({ data }: AmountDistributionChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Amount Distribution</CardTitle>
        <CardDescription>
          Transaction spread across amount bands for quick exposure analysis.
        </CardDescription>
      </CardHeader>
      <CardContent className="h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <FunnelChart>
            <Tooltip />
            <Funnel dataKey="value" data={data} isAnimationActive fill="#0f172a">
              <LabelList position="right" fill="currentColor" stroke="none" dataKey="label" />
            </Funnel>
          </FunnelChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
