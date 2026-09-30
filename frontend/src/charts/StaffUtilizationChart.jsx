import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from "recharts";

export const StaffUtilizationChart = ({ data = [], height = 280 }) => {
  const defaultData = [
    { category: "Withdrawal", available: 3, required: 4, gap: 1 },
    { category: "Deposit", available: 2, required: 2, gap: 0 },
    { category: "Loans", available: 1, required: 3, gap: 2 },
    { category: "KYC", available: 1, required: 2, gap: 1 },
    { category: "Account Open", available: 2, required: 2, gap: 0 },
    { category: "Cards", available: 1, required: 1, gap: 0 },
    { category: "Transfers", available: 1, required: 2, gap: 1 },
  ];

  const chartData = data && data.length > 0 ? data : defaultData;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-slate-900 border border-slate-700 p-2.5 rounded-lg shadow-xl text-xs space-y-1">
          <p className="font-bold text-slate-200">{label}</p>
          <p className="text-emerald-400">Available Staff: <span className="font-mono font-bold">{item.available}</span></p>
          <p className="text-cyan-400">Required Staff: <span className="font-mono font-bold">{item.required}</span></p>
          {item.gap > 0 ? (
            <p className="text-rose-400 font-semibold">Shortage: -{item.gap} employee(s)</p>
          ) : (
            <p className="text-emerald-400 font-semibold">Adequately Staffed</p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis dataKey="category" stroke="#64748b" fontSize={11} tickLine={false} />
          <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            height={32}
            iconType="circle"
            wrapperStyle={{ fontSize: "11px", color: "#94a3b8" }}
          />
          <Bar dataKey="available" name="Available Staff" fill="#10b981" radius={[3, 3, 0, 0]} />
          <Bar dataKey="required" name="AI Required Staff" fill="#06b6d4" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StaffUtilizationChart;
