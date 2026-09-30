import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell
} from "recharts";

export const HourlyTrafficChart = ({ data = [], height = 260 }) => {
  const defaultHourly = [
    { hour: "08:00", customers: 18, risk: "LOW" },
    { hour: "09:00", customers: 45, risk: "LOW" },
    { hour: "10:00", customers: 85, risk: "MEDIUM" },
    { hour: "11:00", customers: 135, risk: "CRITICAL" },
    { hour: "12:00", customers: 120, risk: "HIGH" },
    { hour: "13:00", customers: 75, risk: "MEDIUM" },
    { hour: "14:00", customers: 68, risk: "MEDIUM" },
    { hour: "15:00", customers: 88, risk: "HIGH" },
    { hour: "16:00", customers: 72, risk: "MEDIUM" },
    { hour: "17:00", customers: 35, risk: "LOW" }
  ];

  const chartData = data && data.length > 0 ? data : defaultHourly;

  const getBarColor = (risk) => {
    switch (String(risk).toUpperCase()) {
      case "CRITICAL":
        return "#f43f5e";
      case "HIGH":
        return "#fb923c";
      case "MEDIUM":
        return "#f59e0b";
      case "LOW":
      default:
        return "#06b6d4";
    }
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-slate-900 border border-slate-700 p-2.5 rounded-lg shadow-xl text-xs">
          <p className="font-bold text-slate-200">{label}</p>
          <p className="text-cyan-400 font-mono font-bold mt-1">
            {item.customers} Expected Customers
          </p>
          <p className="text-slate-400 text-[11px] mt-0.5">
            Risk Tier: <span className="font-semibold text-slate-200">{item.risk}</span>
          </p>
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
          <XAxis dataKey="hour" stroke="#64748b" fontSize={11} tickLine={false} />
          <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="customers" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry.risk)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default HourlyTrafficChart;
