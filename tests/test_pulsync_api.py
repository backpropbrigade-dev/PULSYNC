import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "users_in_db" in data

def test_compliance_mock_endpoints():
    # 1. Age verification
    res_age = client.post("/api/compliance/age-verification", json={"user_id": "test_fan_01"})
    assert res_age.status_code == 200
    assert res_age.json()["is_verified"] is True
    
    # 2. Self exclusion check
    res_excl = client.post("/api/compliance/self-exclusion-check", json={"user_id": "test_fan_01"})
    assert res_excl.status_code == 200
    assert res_excl.json()["self_excluded"] is False

def test_user_and_session_lifecycle():
    # Create user
    res_user = client.post("/api/users", json={"id": "usr_test_99", "segment": "Football Explorer"})
    assert res_user.status_code == 201
    assert res_user.json()["id"] == "usr_test_99"
    
    # Create session
    res_sess = client.post("/api/sessions", json={"id": "sess_test_99", "user_id": "usr_test_99"})
    assert res_sess.status_code == 201
    assert res_sess.json()["id"] == "sess_test_99"

def test_event_ingestion_and_intelligence():
    session_id = "sess_test_intel_01"
    user_id = "usr_test_intel_01"
    
    # Event 1: Open match
    e1 = {
        "user_id": user_id,
        "event_type": "match_view",
        "page": "match_detail",
        "action": "open_fixture",
        "sport": "Football",
        "match_id": "match_el_clasico"
    }
    r1 = client.post(f"/api/sessions/{session_id}/events", json=e1)
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["session_id"] == session_id
    assert d1["intent"] in ["EXPLORE", "UNDERSTAND", "ACT", "COMPARE", "REVIEW"]
    
    # Event 2: Statistics view
    e2 = {
        "user_id": user_id,
        "event_type": "statistics_view",
        "page": "statistics",
        "action": "view_stats",
        "sport": "Football",
        "match_id": "match_el_clasico"
    }
    r2 = client.post(f"/api/sessions/{session_id}/events", json=e2)
    assert r2.status_code == 200
    
    # Fetch intelligence
    res_intel = client.get(f"/api/sessions/{session_id}/intelligence")
    assert res_intel.status_code == 200
    intel = res_intel.json()
    assert "intent" in intel
    assert "friction_level" in intel
    assert "abandonment_probability" in intel
    assert "session_quality_score" in intel
    assert "guidance" in intel
    # Machine 3: new fields
    assert "score_factors" in intel
    assert "actions_count" in intel
    assert "betting_eligible" in intel
    assert "updated_at" in intel

def test_session_score_endpoint():
    session_id = "sess_test_score_01"
    # Seed a couple of events
    client.post(f"/api/sessions/{session_id}/events", json={
        "event_type": "match_view", "page": "match_detail",
        "action": "open_fixture", "sport": "Football"
    })
    client.post(f"/api/sessions/{session_id}/events", json={
        "event_type": "statistics_view", "page": "statistics",
        "action": "view_h2h", "sport": "Football"
    })
    # Fetch score
    res = client.get(f"/api/sessions/{session_id}/score")
    assert res.status_code == 200
    data = res.json()
    assert data["session_id"] == session_id
    assert 0.0 <= data["session_quality_score"] <= 100.0
    assert data["trend"] in ("IMPROVING", "STABLE", "DECLINING")
    assert isinstance(data["score_factors"], list)
    assert len(data["score_factors"]) >= 1

def test_recommendations_and_feedback():
    session_id = "sess_test_rec_01"
    # Seed event
    client.post(f"/api/sessions/{session_id}/events", json={
        "event_type": "comparison",
        "page": "comparison",
        "action": "compare_teams",
        "sport": "Football",
        "match_id": "match_el_clasico"
    })
    
    # Get recommendations
    res_recs = client.get(f"/api/recommendations/{session_id}")
    assert res_recs.status_code == 200
    recs = res_recs.json()["recommendations"]
    assert len(recs) > 0
    assert recs[0]["content_type"] in [
        "Team Comparison", "Head-to-Head", "Key Statistics", 
        "Team Form", "Match Insights", "Save for Later", "Related Events", "Similar Matches", "Rules / Information"
    ]
    
    # Submit feedback (clicked)
    feedback_payload = {
        "content_id": recs[0]["content_id"],
        "feedback_type": "clicked"
    }
    res_fb = client.post(f"/api/recommendations/{session_id}/feedback", json=feedback_payload)
    assert res_fb.status_code == 200
    assert res_fb.json()["status"] == "success"

def test_outcomes():
    outcome_payload = {
        "session_id": "sess_test_out_01",
        "decision": "VIEW_CONTENT",
        "content_viewed": True,
        "session_continued": True
    }
    res = client.post("/api/outcomes", json=outcome_payload)
    assert res.status_code == 201
    assert res.json()["decision"] == "VIEW_CONTENT"

def test_dashboard_endpoints():
    # 1. Metrics
    res_m = client.get("/api/dashboard/metrics")
    assert res_m.status_code == 200
    data_m = res_m.json()
    assert "total_sessions" in data_m
    assert "average_session_quality" in data_m
    
    # 2. Segments
    res_s = client.get("/api/dashboard/segments")
    assert res_s.status_code == 200
    assert "segments" in res_s.json()
    
    # 3. Recommendations
    res_r = client.get("/api/dashboard/recommendations")
    assert res_r.status_code == 200
    assert "performance" in res_r.json()
    
    # 4. Quality & Abandonment
    res_q = client.get("/api/dashboard/quality")
    assert res_q.status_code == 200
    assert "quality_by_segment" in res_q.json()
    
    # 5. Impact Simulation
    res_i = client.get("/api/dashboard/impact")
    assert res_i.status_code == 200
    assert "metric_improvements" in res_i.json()

def test_demo_mode_endpoint():
    res_demo = client.post("/api/demo/start", json={"user_id": "demo_test_fan", "match_id": "match_el_clasico"})
    assert res_demo.status_code == 200
    demo_data = res_demo.json()
    assert "session_id" in demo_data
    assert len(demo_data["events_triggered"]) > 0
    assert "final_intelligence" in demo_data
    assert demo_data["final_intelligence"]["friction_level"] in ["MEDIUM", "HIGH"]
