import React from "react";
import { Calendar } from "lucide-react";

export const DateSelector = ({ selectedDate, onSelectDate, className = "" }) => {
  const todayStr = new Date().toISOString().split("T")[0];

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Calendar className="w-4 h-4 text-cyan-400 flex-shrink-0" />
      <input
        type="date"
        value={selectedDate || todayStr}
        onChange={(e) => onSelectDate(e.target.value)}
        className="input-field text-xs py-1.5 px-2.5 bg-slate-900 border-slate-700 text-slate-200 cursor-pointer font-medium"
      />
    </div>
  );
};

export default DateSelector;
