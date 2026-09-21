from datetime import datetime, timedelta
from backend.models import Event, UserProfile, Session as DBSession
from backend.services.intent_detector import IntentDetector
from backend.services.friction_engine import FrictionEngine
from backend.services.abandonment_engine import AbandonmentEngine
from backend.services.recommendation_engine import RecommendationEngine
from backend.services.session_quality import SessionQualityEngine

def test_intent_detection():
    now = datetime.utcnow()
    # Test COMPARE intent
    events = [
        Event(session_id="s1", event_type="match_view", page="match_detail", timestamp=now),
        Event(session_id="s1", event_type="h2h_view", page="h2h", timestamp=now + timedelta(seconds=5)),
        Event(session_id="s1", event_type="comparison", page="comparison", timestamp=now + timedelta(seconds=10)),
    ]
    intent, conf, reason = IntentDetector.detect_intent(events)
    assert intent == "COMPARE"
    assert conf > 0.70
    assert "comparing" in reason.lower()

def test_friction_detection_loop():
    now = datetime.utcnow()
    # Test oscillation loop: page A -> B -> A
    events = [
        Event(session_id="s1", event_type="page_view", page="statistics", action="open", timestamp=now),
        Event(session_id="s1", event_type="page_view", page="h2h", action="open", timestamp=now + timedelta(seconds=4)),
        Event(session_id="s1", event_type="back", page="statistics", action="back", timestamp=now + timedelta(seconds=8)),
    ]
    score, level, reason = FrictionEngine.calculate_friction(events)
    assert score >= 30.0
    assert "loop" in reason.lower() or "back" in reason.lower()

def test_abandonment_engine():
    now = datetime.utcnow()
    events = [
        Event(session_id="s1", event_type="page_view", page="home", timestamp=now - timedelta(seconds=200)),
    ]
    # Long idle + high friction
    prob, risk, reason = AbandonmentEngine.calculate_risk(events, session_duration_sec=200.0, friction_score=75.0)
    assert prob >= 0.70
    assert risk == "HIGH"
    assert "behavioral proxy" in reason.lower()

def test_recommendation_scoring_non_gambling():
    now = datetime.utcnow()
    session = DBSession(id="s1", user_id="u1")
    user = UserProfile(id="u1", segment="Football Explorer")
    events = [
        Event(session_id="s1", event_type="match_view", page="match_detail", timestamp=now),
        Event(session_id="s1", event_type="statistics_view", page="statistics", timestamp=now + timedelta(seconds=5)),
    ]
    recs = RecommendationEngine.generate_recommendations(
        session=session,
        user=user,
        events=events,
        current_intent="UNDERSTAND",
        friction_level="LOW",
        abandonment_probability=0.20,
        previous_recommendations=[]
    )
    assert len(recs) > 0
    # Verify non-gambling: no bet, no wager, no stake
    for r in recs:
        assert "bet" not in r["title"].lower()
        assert "wager" not in r["title"].lower()
        assert "odds" not in r["title"].lower()
        assert 0.0 <= r["score"] <= 100.0
        assert r["rank"] >= 1

def test_session_quality_scoring():
    now = datetime.utcnow()
    events = [
        Event(session_id="s1", event_type="match_view", page="match_detail", action="view_card", timestamp=now),
        Event(session_id="s1", event_type="statistics_view", page="statistics", action="inspect_shots", timestamp=now + timedelta(seconds=10)),
        Event(session_id="s1", event_type="save", page="match_detail", action="save_match", timestamp=now + timedelta(seconds=20)),
    ]
    # Smooth session with low friction & low abandonment
    final_quality, explanation_text = SessionQualityEngine.evaluate_quality(events, 10.0, 0.15)
    assert final_quality >= 80.0
    assert "engagement" in explanation_text.lower() or "active" in explanation_text.lower()

def test_dataset_validation_pipeline():
    import os
    from scripts.validate_dataset import validate
    if os.path.exists("assets/SB_Player.csv"):
        report = validate("assets/SB_Player.csv")
        assert report is not None
        assert "dataset_summary" in report
        assert "quality_report" in report
        assert report["quality_report"]["quality_score"] > 0
