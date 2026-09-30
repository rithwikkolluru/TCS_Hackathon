import React from "react";
import { Layers } from "lucide-react";
import { SERVICE_CATEGORIES } from "../../utils/constants";

export const ServiceFilter = ({
  selectedCategory,
  onSelectCategory,
  includeAll = true,
  className = ""
}) => {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Layers className="w-4 h-4 text-cyan-400 flex-shrink-0" />
      <select
        value={selectedCategory || ""}
        onChange={(e) => onSelectCategory(e.target.value)}
        className="select-field text-xs py-1.5 px-3 bg-slate-900 border-slate-700 text-slate-200 cursor-pointer font-medium"
      >
        {includeAll && <option value="">All 14 Banking Services</option>}
        {SERVICE_CATEGORIES.map((cat) => (
          <option key={cat} value={cat}>
            {cat}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ServiceFilter;
