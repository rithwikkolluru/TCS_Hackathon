import React, { useState } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from "recharts";

export const TrafficChart = ({ data = [], height = 300 }) => {
  const [timeframe, setTimeframe] = useState("TODAY"); // 'TODAY' | 'TOMORROW' | 'NEXT_7_DAYS'

  // Default synthetic curve if data is empty
  const defaultTodayData = [
    { time: "08:00", actual: 15, predicted: 18, baseline: 12 },
    { time: "09:00", actual: 42, predicted: 45, baseline: 30 },
    { time: "10:00", actual: 78, predicted: 85, baseline: 55 },
    { time: "11:00", actual: 110, predicted: 135, baseline: 70 },
    { time: "12:00", actual: 95, predicted: 120, baseline: 65 },
    { time: "13:00", actual: 60, predicted: 75, baseline: 45 },
    { time: "14:00", actual: 55, predicted: 68, baseline: 40 },
    { time: "15:00", actual: 70, predicted: 88, baseline: 50 },
    { time: "16:00", actual: 65, predicted: 72, baseline: 45 },
    { time: "17:00", actual: 30, predicted: 35, baseline: 25 },
  ];

  const defaultTomorrowData = [
    { time: "08:00", predicted: 20, baseline: 12 },
    { time: "09:00", predicted: 50, baseline: 30 },
    { time: "10:00", predicted: 95, baseline: 55 },
    { time: "11:00", predicted: 145, baseline: 70 },
    { time: "12:00", predicted: 130, baseline: 65 },
    { time: "13:00", predicted: 80, baseline: 45 },
    { time: "14:00", predicted: 75, baseline: 40 },
    { time: "15:00", predicted: 95, baseline: 50 },
    { time: "16:00", predicted: 80, baseline: 45 },
    { time: "17:00", predicted: 40, baseline: 25 },
  ];

  const default7DaysData = [
    { time: "Mon", actual: 420, predicted: 430, baseline: 350 },
    { time: "Tue", actual: 480, predicted: 490, baseline: 350 },
    { time: "Wed", actual: 510, predicted: 530, baseline: 350 },
    { time: "Thu", actual: 390, predicted: 410, baseline: 350 },
    { time: "Fri", actual: 580, predicted: 620, baseline: 350 },
    { time: "Sat", actual: 650, predicted: 710, baseline: 380 },
    { time: "Sun", actual: 0, predicted: 0, baseline: 0 },
  ];

  const activeData =
    data && data.length > 0
      ? data
      : timeframe === "TODAY"
      ? defaultTodayData
      : timeframe === "TOMORROW"
      ? defaultTomorrowData
      : default7DaysData;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900/95 border border-slate-700 p-3 rounded-xl shadow-xl backdrop-blur-md text-xs">
          <p className="font-bold text-slate-200 mb-1.5 border-b border-slate-800 pb-1">{label}</p>
          {payload.map((entry, index) => (
            <div key={`item-${index}`} className="flex items-center justify-between gap-4 py-0.5">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                <span className="text-slate-400 capitalize">{entry.name}:</span>
              </span>
              <span className="font-mono font-bold text-slate-100">{entry.value} customers</span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full flex flex-col">
      {/* Timeframe Controls */}
      <div className="flex items-center justify-end gap-1 mb-4">
        {["TODAY", "TOMORROW", "NEXT_7_DAYS"].map((tf) => (
          <button
            key={tf}
            onClick={() => setTimeframe(tf)}
            className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
              timeframe === tf
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
            }`}
          >
            {tf === "TODAY" ? "Today" : tf === "TOMORROW" ? "Tomorrow" : "Next 7 Days"}
          </button>
        ))}
      </div>

      <div style={{ width: "100%", height }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={activeData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} />
            <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="top"
              align="left"
              height={36}
              iconType="circle"
              wrapperStyle={{ fontSize: "11px", color: "#94a3b8" }}
            />
            {timeframe === "TODAY" && (
              <Area
                type="monotone"
                dataKey="actual"
                name="Historical / Actual"
                stroke="#10b981"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorActual)"
              />
            )}
            <Area
              type="monotone"
              dataKey="predicted"
              name="AI Predicted Footfall"
              stroke="#06b6d4"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#colorPredicted)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default TrafficChart;
