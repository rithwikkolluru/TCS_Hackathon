import React from "react";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend
} from "recharts";

export const RiskDistributionChart = ({
  low = 8,
  medium = 3,
  high = 2,
  critical = 1,
  height = 220
}) => {
  const data = [
    { name: "Low Risk", value: low, color: "#10b981" },
    { name: "Medium Risk", value: medium, color: "#f59e0b" },
    { name: "High Risk", value: high, color: "#fb923c" },
    { name: "Critical Risk", value: critical, color: "#f43f5e" }
  ].filter((item) => item.value > 0);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0];
      return (
        <div className="bg-slate-900 border border-slate-700 p-2 rounded shadow text-xs">
          <span style={{ color: item.payload.color }} className="font-bold">
            {item.name}: {item.value} service(s)
          </span>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            height={32}
            iconType="circle"
            wrapperStyle={{ fontSize: "11px", color: "#94a3b8" }}
          />
          <Pie
            data={data}
            cx="50%"
            cy="45%"
            innerRadius={45}
            outerRadius={70}
            paddingAngle={4}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} stroke="#0f172a" strokeWidth={2} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RiskDistributionChart;
