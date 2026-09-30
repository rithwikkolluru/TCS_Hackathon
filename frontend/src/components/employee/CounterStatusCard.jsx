import React, { useState } from "react";
import { UserCheck, Coffee, Power, Clock, CheckCircle2 } from "lucide-react";
import StatusBadge from "../common/StatusBadge";

export const CounterStatusCard = ({ staffInfo = null, branchName = "Hyderabad Central" }) => {
  const [counterStatus, setCounterStatus] = useState("AVAILABLE");
  const [currentTicket, setCurrentTicket] = useState("W-142");

  const nextCustomer = () => {
    const num = Math.floor(Math.random() * 800) + 100;
    setCurrentTicket(`W-${num}`);
  };

  return (
    <div className="glass-card p-5 border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="text-xs font-semibold text-slate-400 block uppercase">Assigned Station</span>
          <h3 className="font-bold text-base text-slate-100">Counter #02 (Cash & Transfers)</h3>
        </div>
        <StatusBadge status={counterStatus} />
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 mb-4 text-center">
        <div>
          <span className="text-[10px] text-slate-400 uppercase font-medium">Serving Token</span>
          <span className="font-mono font-extrabold text-base text-cyan-400 block mt-0.5">
            {currentTicket}
          </span>
        </div>
        <div>
          <span className="text-[10px] text-slate-400 uppercase font-medium">Avg Handling</span>
          <span className="font-mono font-extrabold text-base text-emerald-400 block mt-0.5">
            4.8 mins
          </span>
        </div>
        <div>
          <span className="text-[10px] text-slate-400 uppercase font-medium">Served Today</span>
          <span className="font-mono font-extrabold text-base text-slate-100 block mt-0.5">
            38 Cust
          </span>
        </div>
        <div>
          <span className="text-[10px] text-slate-400 uppercase font-medium">Shift Remaining</span>
          <span className="font-mono font-extrabold text-base text-amber-400 block mt-0.5">
            3h 20m
          </span>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/80">
        <button
          onClick={nextCustomer}
          className="btn-primary flex-1 text-xs py-2"
        >
          <CheckCircle2 className="w-4 h-4" />
          Call Next Ticket
        </button>

        <button
          onClick={() => setCounterStatus(counterStatus === "AVAILABLE" ? "SHORTAGE" : "AVAILABLE")}
          className="btn-secondary text-xs py-2 px-3"
        >
          <Coffee className="w-3.5 h-3.5" />
          {counterStatus === "AVAILABLE" ? "Take Break" : "Resume Counter"}
        </button>
      </div>
    </div>
  );
};

export default CounterStatusCard;
