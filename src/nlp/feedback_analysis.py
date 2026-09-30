import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR


class FeedbackAnalyzer:
    """NLP analysis module for Customer Feedback: Sentiment Analysis and Topic Extraction with robust fallbacks."""

    TOPIC_KEYWORDS = {
        "waiting_time": ["wait", "waited", "waiting", "time", "hour", "hours", "minute", "minutes", "slow", "delay"],
        "staff_behavior": ["staff", "executive", "officer", "polite", "helpful", "rude", "behaviour", "behavior", "attitude", "manager"],
        "service_delay": ["delay", "slow", "forever", "took too long", "sluggish", "holding"],
        "loan": ["loan", "sanction", "mortgage", "emi", "interest"],
        "account_opening": ["account", "open", "opening", "savings", "current"],
        "KYC": ["kyc", "documents", "verification", "update", "aadhaar", "pan"],
        "digital_banking": ["online", "app", "mobile", "portal", "website", "netbanking", "digital"],
        "queue": ["queue", "counter", "line", "token", "crowd", "crowded", "standing"],
        "documentation": ["form", "paperwork", "document", "copy", "signature"],
        "general_service": ["service", "branch", "experience", "bank", "facility"]
    }

    POSITIVE_WORDS = {
        "good", "great", "excellent", "fast", "smooth", "helpful", "polite", "quick",
        "awesome", "satisfied", "efficient", "immediately", "smoothly", "prompt", "easy"
    }

    NEGATIVE_WORDS = {
        "bad", "worst", "terrible", "slow", "delay", "horrible", "messy", "unmanaged",
        "absurd", "forever", "unhelpful", "rude", "disappointed", "frustrated", "standing", "crowded"
    }

    def __init__(self):
        pass

    def analyze_comment(self, comment: str, rating: int = 3) -> Dict[str, Any]:
        """Extracts sentiment, score, and primary topic from a comment string."""
        comment_lower = str(comment).lower()

        # 1. Sentiment Score calculation (rule-based hybrid with rating weight)
        pos_count = sum(1 for w in self.POSITIVE_WORDS if w in comment_lower)
        neg_count = sum(1 for w in self.NEGATIVE_WORDS if w in comment_lower)

        word_score = pos_count - neg_count
        rating_score = (rating - 3) / 2.0  # maps 1..5 to -1.0 .. +1.0

        combined_score = round(float(np.clip(0.6 * rating_score + 0.4 * word_score, -1.0, 1.0)), 2)

        if combined_score > 0.15 or rating >= 4:
            sentiment = "Positive"
        elif combined_score < -0.15 or rating <= 2:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        # 2. Topic Extraction
        matched_topics = []
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            if any(re.search(rf"\b{kw}\b", comment_lower) for kw in keywords):
                matched_topics.append(topic)

        primary_topic = matched_topics[0] if matched_topics else "general_service"

        return {
            "sentiment": sentiment,
            "sentiment_score": combined_score,
            "topic": primary_topic,
            "all_topics": ",".join(matched_topics)
        }

    def analyze_dataset(self, df_feedback: pd.DataFrame) -> pd.DataFrame:
        """Analyzes full feedback dataset and produces reports."""
        df = df_feedback.copy()

        results = []
        for _, row in df.iterrows():
            res = self.analyze_comment(row["comment"], int(row.get("rating", 3)))
            results.append(res)

        res_df = pd.DataFrame(results)
        analyzed_df = pd.concat([df.reset_index(drop=True), res_df], axis=1)

        # Save to reports
        output_path = REPORTS_DIR / "feedback_analysis.csv"
        analyzed_df.to_csv(output_path, index=False)
        print(f"Feedback analysis saved to {output_path}")

        # Summary statistics
        print("\n--- Feedback Summary Statistics ---")
        print(f"Total Feedback Comments: {len(analyzed_df)}")
        print(f"Sentiment Breakdown: {analyzed_df['sentiment'].value_counts().to_dict()}")
        print(f"Top Topics: {analyzed_df['topic'].value_counts().head(5).to_dict()}")

        return analyzed_df


def run_feedback_analysis() -> pd.DataFrame:
    input_path = PROCESSED_DATA_DIR / "processed_feedback.csv"
    if not input_path.exists():
        input_path = RAW_DATA_DIR / "customer_feedback.csv"
    if not input_path.exists():
        raise FileNotFoundError("Feedback dataset not found. Run generate_data.py first.")

    df_feedback = pd.read_csv(input_path)
    analyzer = FeedbackAnalyzer()
    return analyzer.analyze_dataset(df_feedback)


if __name__ == "__main__":
    run_feedback_analysis()
