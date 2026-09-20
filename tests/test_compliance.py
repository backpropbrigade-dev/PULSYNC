import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.database import get_db, engine
from backend.models import Base, UserProfile

client = TestClient(app)

from backend.database import SessionLocal

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.query(UserProfile).delete()
    db.commit()
    db.close()
    yield

def test_registration_and_user_creation():
    response = client.post("/api/users", json={
        "id": "test_user_reg_01",
        "anonymous_id": "test_anon_reg_01",
        "display_name": "Demo Player",
        "email": "player@demo.com",
        "segment": "Sportsbook Fan"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "test_user_reg_01"
    assert data["age_verified"] == False
    assert data["kyc_verified"] == False
    assert data["self_excluded"] == False

def test_age_verification_valid_18_plus():
    response = client.post("/api/compliance/age-verification", json={
        "user_id": "test_user_reg_01",
        "age": 22,
        "birth_date": "2002-05-15",
        "verification_method": "DEMO_ATTRIBUTE"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] == True
    assert data["status"] == "VERIFIED_AGE_OVER_18"

def test_age_verification_underage_blocked():
    response = client.post("/api/compliance/age-verification", json={
        "user_id": "test_underage_01",
        "age": 16,
        "birth_date": "2010-01-01"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] == False
    assert data["status"] == "AGE_RESTRICTED"

def test_conceptual_kyc_demo():
    response = client.post("/api/compliance/kyc-demo", json={
        "user_id": "test_user_reg_01",
        "document_type": "National ID"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["kyc_verified"] == True
    assert data["document_type"] == "National ID"
    assert data["status"] == "VERIFIED"
    assert "Demo verification" in data["notice"]

def test_self_exclusion_check_active():
    response = client.post("/api/compliance/self-exclusion-check", json={
        "user_id": "test_user_reg_01"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["checked"] == True
    assert data["excluded"] == False
    assert data["eligible"] == True

def test_betting_eligibility_decision_eligible():
    response = client.post("/api/compliance/betting-eligibility", json={
        "user_id": "test_user_reg_01"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] == True
    assert data["status"] == "ELIGIBLE"
    assert data["reason"] == "ELIGIBLE"

def test_betting_eligibility_decision_underage():
    response = client.post("/api/compliance/betting-eligibility", json={
        "user_id": "test_underage_01"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["eligible"] == False
    assert data["status"] == "AGE_RESTRICTED"
    assert "18+ age verification" in data["reason"]

def test_backend_gate_enforcement_on_place_bet_blocked():
    # Attempting to place bet for under-18 user directly via API MUST be blocked by backend
    response = client.post("/api/bets", json={
        "user_id": "test_underage_01",
        "stake": 10
    })
    assert response.status_code == 403
    detail = response.json()["detail"]
    assert detail["eligible"] == False
    assert detail["status"] == "AGE_RESTRICTED"

def test_backend_gate_enforcement_on_place_bet_accepted():
    # Attempting to place bet for fully verified user MUST succeed
    response = client.post("/api/bets", json={
        "user_id": "test_user_reg_01",
        "stake": 10
    })
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    assert data["eligible"] == True
    assert data["status"] == "ACCEPTED"

def test_compliance_status_endpoint():
    response = client.get("/api/compliance/status/test_user_reg_01")
    assert response.status_code == 200
    data = response.json()
    assert data["betting_eligible"] == True
    assert data["age_verified"] == True
    assert data["kyc_verified"] == True
    assert data["self_excluded"] == False
    assert data["status"] == "ELIGIBLE"
