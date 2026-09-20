import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_impact_summary(client):
    res = client.get("/api/impact/summary")
    assert res.status_code == 200
    data = res.json()
    assert "dataset" in data
    assert "kpi_cards" in data
    assert data["dataset"]["players"] == 15738
    assert data["dataset"]["sessions"] == 99504
    assert data["kpi_cards"]["value_seeking_sessions"]["value"] == 3220
    assert data["evidence"]["causal_claim"] is False

def test_impact_session_health(client):
    res = client.get("/api/impact/session-health")
    assert res.status_code == 200
    data = res.json()
    assert "funnel" in data
    assert len(data["funnel"]) == 6
    assert data["funnel"][0]["stage"] == "1. Session Start"
    assert data["funnel"][0]["rate_pct"] == 100.0
    assert "daily_trends" in data
    assert len(data["daily_trends"]) == 16

def test_impact_matrix(client):
    res = client.get("/api/impact/matrix")
    assert res.status_code == 200
    matrix = res.json()
    assert len(matrix) == 9
    total_matrix_sessions = sum(cell["sessions"] for cell in matrix)
    assert total_matrix_sessions == 99504
    # Check PULSYNC Opportunity cell
    opp = [c for c in matrix if c["is_pulsync_opportunity"]]
    assert len(opp) == 1
    assert opp[0]["transaction_intent"] == "LOW"
    assert opp[0]["information_interest"] == "HIGH"
    assert opp[0]["sessions"] == 3220

def test_impact_segments(client):
    res = client.get("/api/impact/segments")
    assert res.status_code == 200
    segments = res.json()
    expected_segments = ["VALUE_SEEKING", "TRANSACTION_FOCUSED", "INFORMATION_FOCUSED", "RESPECT_EXIT", "LOW_ENGAGEMENT", "MIXED_UNCERTAIN"]
    for seg in expected_segments:
        assert seg in segments
    # Value seeking metrics check
    vs = segments["VALUE_SEEKING"]
    assert vs["sessions"] == 3220
    assert vs["return_7d_rate"] > 70.0

def test_impact_replay(client):
    res = client.get("/api/impact/replay")
    assert res.status_code == 200
    replay = res.json()
    assert replay["value_seeking"]["sessions"] == 3220
    assert replay["comparison_cohort"]["sessions"] == 2594
    assert replay["observed_difference_pp"] == 9.9
    assert replay["confidence_interval_95"][0] < replay["observed_difference_pp"] < replay["confidence_interval_95"][1]
    assert replay["statistically_significant"] is True
    assert "Observed Correlation" in replay["evidence_type"]

def test_impact_opportunity(client):
    res = client.get("/api/impact/opportunity")
    assert res.status_code == 200
    opp = res.json()
    assert opp["target_segment"] == "VALUE_SEEKING"
    assert opp["sessions"] == 3220
    assert opp["observed_gap_pp"] == 9.9

def test_impact_roi_simulation(client):
    # Base scenario
    res = client.post("/api/impact/roi/simulate", json={"scenario": "base", "scenario_realization_pct": 50})
    assert res.status_code == 200
    base = res.json()
    assert base["outputs"]["roi_percent"] > 0
    assert base["outputs"]["annual_net_value_eur"] > 0
    assert base["outputs"]["payback_months"] is not None

    # Conservative scenario
    res_cons = client.post("/api/impact/roi/simulate", json={"scenario": "conservative", "scenario_realization_pct": 25})
    assert res_cons.status_code == 200
    cons = res_cons.json()
    assert cons["outputs"]["roi_percent"] < base["outputs"]["roi_percent"]

    # Optimistic scenario
    res_opt = client.post("/api/impact/roi/simulate", json={"scenario": "optimistic", "scenario_realization_pct": 75})
    assert res_opt.status_code == 200
    opt = res_opt.json()
    assert opt["outputs"]["roi_percent"] > base["outputs"]["roi_percent"]

    # Negative net value test (extremely high costs)
    res_neg = client.post("/api/impact/roi/simulate", json={
        "scenario_realization_pct": 5,
        "hosting_cost_monthly": 50000.0,
        "storage_cost_monthly": 10000.0
    })
    assert res_neg.status_code == 200
    neg = res_neg.json()
    assert neg["outputs"]["payback_months"] is None
    assert "No positive payback" in neg["outputs"]["payback_status"]

def test_impact_case_generation(client):
    res = client.get("/api/impact/impact-case?scenario=base")
    assert res.status_code == 200
    case = res.json()
    assert "title" in case
    assert len(case["sections"]) == 9
    titles = [s["title"] for s in case["sections"]]
    assert any("Business Problem" in t for t in titles)
    assert any("Compliance" in t for t in titles)
    assert any("Limitations" in t for t in titles)

def test_impact_methodology(client):
    res = client.get("/api/impact/methodology")
    assert res.status_code == 200
    meth = res.json()
    assert "inactivity threshold" in meth["session_definition"].lower()
    assert meth["causal_claim"] is False
    assert "dual-arm A/B" in meth["causal_disclaimer"]

def test_impact_metrics_chain(client):
    res = client.get("/api/impact/metrics-chain")
    assert res.status_code == 200
    chain = res.json()
    assert len(chain["levels"]) == 4
    assert chain["levels"][0]["name"] == "Session Health"
    assert chain["levels"][3]["name"] == "Business Outcome"
    assert "signals" in chain
    assert len(chain["signals"]["compliance_guardrails"]) == 4
