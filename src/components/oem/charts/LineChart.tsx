"use client";

import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface LineChartProps {
  data: Record<string, string | number>[];
  lines: { dataKey: string; color: string; name: string }[];
  xDataKey: string;
  height?: number;
  yAxisFormatter?: (value: number) => string;
}

export default function LineChart({
  data,
  lines,
  xDataKey,
  height = 300,
  yAxisFormatter,
}: LineChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsLineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xDataKey} tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} tickFormatter={yAxisFormatter} />
        <Tooltip
          formatter={(value) => {
            const num = Number(value);
            return yAxisFormatter ? yAxisFormatter(num) : num.toLocaleString();
          }}
        />
        <Legend />
        {lines.map((line) => (
          <Line
            key={line.dataKey}
            type="monotone"
            dataKey={line.dataKey}
            stroke={line.color}
            name={line.name}
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        ))}
      </RechartsLineChart>
    </ResponsiveContainer>
  );
}
