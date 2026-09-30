import pytest
from src.nlp.feedback_analysis import FeedbackAnalyzer


def test_feedback_sentiment_analysis():
    analyzer = FeedbackAnalyzer()

    # Positive feedback
    res_pos = analyzer.analyze_comment("Quick service and polite counter staff!", rating=5)
    assert res_pos["sentiment"] == "Positive"
    assert res_pos["sentiment_score"] > 0

    # Negative feedback
    res_neg = analyzer.analyze_comment("Waited for 45 minutes, horrible queue management!", rating=1)
    assert res_neg["sentiment"] == "Negative"
    assert res_neg["sentiment_score"] < 0
    assert res_neg["topic"] in ["waiting_time", "queue", "service_delay"]
