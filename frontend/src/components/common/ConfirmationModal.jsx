import React, { useState } from "react";
import { AlertCircle, CheckCircle, XCircle } from "lucide-react";

export const ConfirmationModal = ({
  isOpen,
  title,
  message,
  recommendation = null,
  actionType = "ACCEPT", // 'ACCEPT' | 'REJECT' | 'MODIFY'
  onConfirm,
  onCancel,
  loading = false
}) => {
  const [reason, setReason] = useState("");

  if (!isOpen) return null;

  const isAccept = actionType === "ACCEPT";

  const handleConfirm = () => {
    onConfirm({ reason: reason || (isAccept ? "Approved by Manager" : "Declined by Manager") });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="glass-card max-w-lg w-full p-6 border-slate-700 bg-slate-900 shadow-2xl relative">
        <div className="flex items-start gap-4 mb-4">
          <div
            className={`p-3 rounded-full flex-shrink-0 ${
              isAccept ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
            }`}
          >
            {isAccept ? <CheckCircle className="w-6 h-6" /> : <XCircle className="w-6 h-6" />}
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">{title}</h3>
            <p className="text-sm text-slate-400 mt-1">{message}</p>
          </div>
        </div>

        {recommendation && (
          <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800 text-xs mb-4 space-y-1.5">
            <div className="flex justify-between">
              <span className="text-slate-400">Service:</span>
              <span className="font-semibold text-slate-200">{recommendation.service_category}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Action:</span>
              <span className="font-semibold text-cyan-400">{recommendation.recommendation_text}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Risk Level:</span>
              <span className="font-semibold text-amber-400">{recommendation.risk_level}</span>
            </div>
          </div>
        )}

        <div className="mb-5">
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">
            Manager Operational Notes / Justification:
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder={
              isAccept
                ? "e.g. Reassigned 2 counter staff from general duties to handle peak surge."
                : "e.g. Staff currently occupied in scheduled branch audit."
            }
            rows={3}
            className="input-field text-xs resize-none"
          />
        </div>

        <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="btn-secondary text-xs"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            disabled={loading}
            className={`${
              isAccept
                ? "bg-emerald-600 hover:bg-emerald-500 text-white"
                : "bg-rose-600 hover:bg-rose-500 text-white"
            } px-4 py-2 rounded-lg text-xs font-bold transition-all shadow-md flex items-center gap-2`}
          >
            {loading ? "Processing..." : isAccept ? "Confirm Approval" : "Confirm Rejection"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
