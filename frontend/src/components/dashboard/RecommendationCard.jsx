import React, { useState } from "react";
import RiskBadge from "../common/RiskBadge";
import StatusBadge from "../common/StatusBadge";
import ConfirmationModal from "../common/ConfirmationModal";
import { formatDateTime } from "../../utils/formatters";
import { Check, X, Sparkles, Clock, AlertTriangle, Cpu } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export const RecommendationCard = ({
  recommendation,
  onAccept,
  onReject,
  loading = false
}) => {
  const { role } = useAuth();
  const isManager = role === "manager";
  const [modalAction, setModalAction] = useState(null); // 'ACCEPT' | 'REJECT' | null

  if (!recommendation) return null;

  const isPending = recommendation.status === "PENDING";

  const handleOpenModal = (action) => {
    setModalAction(action);
  };

  const handleModalConfirm = (payload) => {
    if (modalAction === "ACCEPT" && onAccept) {
      onAccept(recommendation.id, payload);
    } else if (modalAction === "REJECT" && onReject) {
      onReject(recommendation.id, payload);
    }
    setModalAction(null);
  };

  return (
    <>
      <div className="glass-card p-5 border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between">
        <div>
          {/* Header */}
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] font-bold text-cyan-400 uppercase tracking-wider block">
                  {recommendation.recommendation_type?.replace(/_/g, " ")}
                </span>
                <h4 className="font-bold text-sm text-slate-100">
                  {recommendation.service_category || "Branch Wide"}
                </h4>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <RiskBadge risk={recommendation.risk_level} size="sm" />
              <StatusBadge status={recommendation.status} />
            </div>
          </div>

          {/* Action Proposition */}
          <div className="bg-slate-950/70 p-3 rounded-lg border border-slate-800/80 my-3">
            <p className="text-sm font-semibold text-cyan-300">
              {recommendation.recommendation_text}
            </p>
          </div>

          {/* AI Explanation Details */}
          <div className="space-y-1.5 text-xs text-slate-300 border-t border-slate-800/80 pt-3">
            <div className="flex items-start gap-1.5">
              <span className="font-semibold text-cyan-400 flex-shrink-0">Reason:</span>
              <p className="text-slate-400 leading-relaxed">
                {recommendation.explanation}
              </p>
            </div>
          </div>
        </div>

        {/* Footer info and Accept/Reject buttons */}
        <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>{formatDateTime(recommendation.created_at)}</span>
            <span className="text-slate-400">•</span>
            <span className="font-mono text-slate-400">#{recommendation.id}</span>
          </div>

          {isPending && isManager && (
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleOpenModal("REJECT")}
                disabled={loading}
                className="btn-danger"
              >
                <X className="w-3.5 h-3.5" />
                Reject
              </button>
              <button
                onClick={() => handleOpenModal("ACCEPT")}
                disabled={loading}
                className="btn-success"
              >
                <Check className="w-3.5 h-3.5" />
                Accept
              </button>
            </div>
          )}
        </div>
      </div>

      <ConfirmationModal
        isOpen={!!modalAction}
        title={modalAction === "ACCEPT" ? "Accept AI Recommendation" : "Reject AI Recommendation"}
        message={
          modalAction === "ACCEPT"
            ? "Approving this recommendation will enact the operational changes and log the decision to continuous feedback."
            : "Declining this recommendation requires managerial justification for audit and machine learning calibration."
        }
        recommendation={recommendation}
        actionType={modalAction || "ACCEPT"}
        onConfirm={handleModalConfirm}
        onCancel={() => setModalAction(null)}
        loading={loading}
      />
    </>
  );
};

export default RecommendationCard;
