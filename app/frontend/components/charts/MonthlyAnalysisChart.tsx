import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { MonthlyPoint } from "@/utils/types";

interface MonthlyAnalysisChartProps {
  data: MonthlyPoint[];
}

export function MonthlyAnalysisChart({ data }: MonthlyAnalysisChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Monthly Analysis</CardTitle>
        <CardDescription>Fraud, safe, and review volume trend over recent reporting cycles.</CardDescription>
      </CardHeader>
      <CardContent className="h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="fraudGradient" x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor="#0f172a" stopOpacity={0.9} />
                <stop offset="95%" stopColor="#0f172a" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="safeGradient" x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor="#64748b" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#64748b" stopOpacity={0.08} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.18)" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="safe" stroke="#64748b" fill="url(#safeGradient)" strokeWidth={2.2} />
            <Area type="monotone" dataKey="fraud" stroke="#0f172a" fill="url(#fraudGradient)" strokeWidth={2.2} />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
