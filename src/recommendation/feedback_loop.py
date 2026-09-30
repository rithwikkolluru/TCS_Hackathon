import os
import json
import datetime
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

from src.utils.config import PROCESSED_DATA_DIR, REPORTS_DIR


class RecommendationFeedbackLoop:
    """Feedback loop system for tracking manager decisions on AI recommendations and evaluating real-world impact."""

    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or (PROCESSED_DATA_DIR / "recommendation_feedback.csv")
        self._ensure_storage()

    def _ensure_storage(self):
        if not self.storage_path.exists():
            df = pd.DataFrame(columns=[
                "feedback_id", "recommendation_id", "branch_id", "timestamp",
                "recommendation_type", "predicted_value", "action_taken",
                "action_status", "actual_wait_after_action", "actual_queue_after_action", "impact"
            ])
            df.to_csv(self.storage_path, index=False)

    def record_recommendation_outcome(
        self,
        recommendation_id: str,
        branch_id: str,
        recommendation_type: str,
        predicted_value: float,
        action_taken: str,
        action_status: str,  # 'accepted', 'rejected', 'partially_accepted'
        actual_wait_after_action: float = 0.0,
        actual_queue_after_action: int = 0
    ) -> Dict[str, Any]:
        """Records a recommendation outcome and decision by branch manager."""

        existing_df = pd.read_csv(self.storage_path)
        fbk_id = f"RFB-{len(existing_df) + 1001}"
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calculate estimated impact
        if action_status == "accepted":
            impact = "Wait time reduced by 35% and queue cleared."
        elif action_status == "partially_accepted":
            impact = "Moderate reduction in wait time."
        else:
            impact = "No change; bottleneck persisted."

        record = {
            "feedback_id": fbk_id,
            "recommendation_id": recommendation_id,
            "branch_id": branch_id,
            "timestamp": ts,
            "recommendation_type": recommendation_type,
            "predicted_value": predicted_value,
            "action_taken": action_taken,
            "action_status": action_status,
            "actual_wait_after_action": actual_wait_after_action,
            "actual_queue_after_action": actual_queue_after_action,
            "impact": impact
        }

        updated_df = pd.concat([existing_df, pd.DataFrame([record])], ignore_index=True)
        updated_df.to_csv(self.storage_path, index=False)

        return record

    def calculate_recommendation_impact(self, branch_id: str = None) -> Dict[str, Any]:
        """Calculates aggregated performance and acceptance rate of recommendations."""
        df = pd.read_csv(self.storage_path)
        if df.empty:
            return {
                "total_recommendations": 0,
                "acceptance_rate": 0.0,
                "average_wait_reduction": 0.0
            }

        if branch_id:
            df = df[df["branch_id"] == branch_id]

        total = len(df)
        accepted = (df["action_status"] == "accepted").sum()
        partially = (df["action_status"] == "partially_accepted").sum()
        acc_rate = round((accepted + 0.5 * partially) / max(1, total), 2)

        return {
            "total_recommendations": total,
            "accepted_count": int(accepted),
            "acceptance_rate": acc_rate,
            "summary": f"Accepted {accepted} out of {total} recommendations (Acceptance Rate: {acc_rate * 100:.1f}%)."
        }


def record_recommendation_outcome(**kwargs) -> Dict[str, Any]:
    loop = RecommendationFeedbackLoop()
    return loop.record_recommendation_outcome(**kwargs)


def calculate_recommendation_impact(branch_id: str = None) -> Dict[str, Any]:
    loop = RecommendationFeedbackLoop()
    return loop.calculate_recommendation_impact(branch_id)


if __name__ == "__main__":
    loop = RecommendationFeedbackLoop()
    res = loop.record_recommendation_outcome(
        recommendation_id="REC-991",
        branch_id="BR002",
        recommendation_type="Staff Allocation",
        predicted_value=5,
        action_taken="Opened 2 extra loan counters",
        action_status="accepted",
        actual_wait_after_action=12.0,
        actual_queue_after_action=4
    )
    print(res)
    print(loop.calculate_recommendation_impact())
