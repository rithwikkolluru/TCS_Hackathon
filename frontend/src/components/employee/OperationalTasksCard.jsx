import React, { useState } from "react";
import { CheckCircle, Clock, AlertTriangle, ArrowUpRight, ShieldCheck } from "lucide-react";
import RiskBadge from "../common/RiskBadge";

export const OperationalTasksCard = ({ tasks = [], onTaskStatusChange = null }) => {
  const defaultTasks = [
    {
      id: "TSK-01",
      title: "Deploy to Counter 3 (Withdrawal Queue Spillover)",
      description: "Withdrawal queue has exceeded 15 customers. Open secondary teller counter immediately.",
      priority: "HIGH",
      service: "Withdrawal",
      estimatedTime: "25 mins",
      status: "IN_PROGRESS"
    },
    {
      id: "TSK-02",
      title: "Prepare KYC Fast-Track Documentation Kits",
      description: "Surge expected between 11:00 AM - 1:00 PM. Pre-verify biometric scanner connections.",
      priority: "MEDIUM",
      service: "KYC Related",
      estimatedTime: "15 mins",
      status: "PENDING"
    },
    {
      id: "TSK-03",
      title: "Assist Senior Citizen Account Opening Desk",
      description: "Two senior citizens in queue waiting > 18 mins. Guide through priority assistance booth.",
      priority: "LOW",
      service: "Account Opening",
      estimatedTime: "20 mins",
      status: "PENDING"
    }
  ];

  const [taskList, setTaskList] = useState(tasks.length > 0 ? tasks : defaultTasks);

  const toggleTask = (id) => {
    setTaskList((prev) =>
      prev.map((t) =>
        t.id === id
          ? { ...t, status: t.status === "COMPLETED" ? "IN_PROGRESS" : "COMPLETED" }
          : t
      )
    );
    if (onTaskStatusChange) {
      onTaskStatusChange(id);
    }
  };

  return (
    <div className="glass-card p-5 border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-cyan-400" />
          <h3 className="font-bold text-sm text-slate-100">My Operational Tasks</h3>
        </div>
        <span className="text-xs font-semibold text-cyan-400 bg-cyan-500/10 px-2.5 py-0.5 rounded-full border border-cyan-500/20">
          {taskList.filter((t) => t.status !== "COMPLETED").length} Active
        </span>
      </div>

      <div className="space-y-3">
        {taskList.map((task) => {
          const isDone = task.status === "COMPLETED";

          return (
            <div
              key={task.id}
              className={`p-3.5 rounded-xl border transition-all ${
                isDone
                  ? "bg-slate-950/40 border-slate-800/80 opacity-60"
                  : task.priority === "HIGH"
                  ? "bg-orange-950/20 border-orange-500/30 text-slate-100"
                  : "bg-slate-900 border-slate-700/80 text-slate-100"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-2.5 flex-1 min-w-0">
                  <button
                    onClick={() => toggleTask(task.id)}
                    className={`mt-0.5 w-4 h-4 rounded border flex items-center justify-center transition-colors ${
                      isDone
                        ? "bg-emerald-500 border-emerald-500 text-white"
                        : "border-slate-600 hover:border-cyan-400"
                    }`}
                  >
                    {isDone && <CheckCircle className="w-3.5 h-3.5" />}
                  </button>
                  <div className="flex-1 min-w-0">
                    <h4
                      className={`text-xs font-bold ${
                        isDone ? "line-through text-slate-400" : "text-slate-100"
                      }`}
                    >
                      {task.title}
                    </h4>
                    <p className="text-[11px] text-slate-400 mt-1 leading-snug">
                      {task.description}
                    </p>
                    <div className="flex items-center gap-3 mt-2 text-[10px] text-slate-400">
                      <span className="text-cyan-400 font-semibold">{task.service}</span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-400" />
                        {task.estimatedTime}
                      </span>
                    </div>
                  </div>
                </div>
                <RiskBadge risk={task.priority} size="sm" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default OperationalTasksCard;
