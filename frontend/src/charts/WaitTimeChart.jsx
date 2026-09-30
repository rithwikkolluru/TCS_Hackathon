import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ReferenceLine
} from "recharts";
import { getRiskColor } from "../utils/formatters";

export const WaitTimeChart = ({ data = [], height = 300, benchmark = 20 }) => {
  const defaultData = [
    { service: "Loans", wait: 38.5, queue: 24, risk: "CRITICAL" },
    { service: "KYC", wait: 28.0, queue: 16, risk: "HIGH" },
    { service: "Account Opening", wait: 22.0, queue: 12, risk: "MEDIUM" },
    { service: "Deposit", wait: 14.5, queue: 8, risk: "LOW" },
    { service: "Withdrawal", wait: 12.0, queue: 7, risk: "LOW" },
    { service: "Cheque", wait: 9.0, queue: 4, risk: "LOW" },
    { service: "Cards", wait: 8.5, queue: 3, risk: "LOW" }
  ];

  const chartData = data && data.length > 0 ? data : defaultData;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl text-xs">
          <p className="font-bold text-slate-200">{item.service || label}</p>
          <div className="space-y-1 mt-1.5">
            <p className="text-cyan-400">
              Predicted Wait: <span className="font-mono font-bold">{item.wait?.toFixed(1)} mins</span>
            </p>
            <p className="text-slate-400">
              Current Queue: <span className="font-mono font-bold text-slate-200">{item.queue}</span>
            </p>
            <p className="text-slate-400">
              Risk Level: <span className="font-bold text-amber-400">{item.risk}</span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} layout="vertical" margin={{ top: 10, right: 30, left: 40, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
          <XAxis type="number" stroke="#64748b" fontSize={11} unit="m" tickLine={false} />
          <YAxis
            type="category"
            dataKey="service"
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            width={90}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            x={benchmark}
            stroke="#f43f5e"
            strokeDasharray="3 3"
            label={{ value: `SLA Limit (${benchmark}m)`, fill: "#f43f5e", fontSize: 10, position: "top" }}
          />
          <Bar dataKey="wait" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getRiskColor(entry.risk)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default WaitTimeChart;
