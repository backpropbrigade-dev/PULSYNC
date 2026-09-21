import os
import json
import uuid
import datetime
from typing import List, Optional, Any, Dict

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.config import settings
from backend.database import engine, get_db
from backend.models import (
    Base, UserProfile, Session as DBSession, Event, Match, Recommendation, Outcome, SessionPrediction
)
from backend.schemas import (
    AgeVerificationRequest, AgeVerificationResponse,
    SelfExclusionRequest, SelfExclusionResponse,
    KYCDemoRequest, KYCDemoResponse,
    BettingEligibilityRequest, BettingEligibilityResponse,
    ComplianceStatusResponse,
    UserCreate, UserResponse,
    SessionCreate, SessionResponse,
    EventCreate, SessionIntelligenceResponse, SessionScoreResponse,
    RecommendationListResponse, RecommendationItem, RecommendationFeedbackRequest,
    OutcomeCreate, OutcomeResponse,
    MatchResponse,
    DashboardMetricsResponse, DashboardSegmentsResponse,
    DashboardRecommendationsResponse, DashboardQualityResponse, DashboardImpactResponse,
    DemoStartRequest, ROISimulationRequest
)
from backend.services.user_profiling import UserProfilingService
from backend.services.session_intelligence import SessionIntelligenceService
from backend.services.dashboard_service import DashboardAnalyticsService
from backend.services.demo_service import DemoSimulationService
from backend.services.impact_service import ImpactAnalyticsService

# Initialize database schema if not already present
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="PULSYNC: AI-Powered Session Intelligence & Contextual Guidance Platform"
)

# CORS Configuration allowing Vue and Next Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================================================
# Root & Health Endpoints
# ==================================================
@app.get("/", tags=["System"])
def read_root():
    return {"message": "Welcome to PULSYNC API"}

@app.get("/api/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint validating API and database connectivity."""
    try:
        user_count = db.query(UserProfile).count()
        return {
            "status": "healthy",
            "service": "PULSYNC API",
            "version": settings.VERSION,
            "database": "connected",
            "users_in_db": user_count,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}"
        )

# ==================================================
# Compliance MVP (Machine 2 Implementation)
# ==================================================
@app.post("/api/compliance/age-verification", response_model=AgeVerificationResponse, tags=["Compliance"])
def verify_age(payload: AgeVerificationRequest, db: Session = Depends(get_db)):
    """Conceptual 18+ age verification endpoint."""
    uid = payload.user_id or payload.anonymous_user_id or "usr_demo"
    user = db.query(UserProfile).filter(
        (UserProfile.id == uid) | (UserProfile.anonymous_id == uid)
    ).first()
    
    if not user:
        user = UserProfile(id=uid, anonymous_id=uid, segment="Casual Explorer")
        db.add(user)
        
    is_underage = (payload.age is not None and payload.age < 18)
    if payload.birth_date:
        try:
            dob = datetime.datetime.strptime(payload.birth_date, "%Y-%m-%d")
            today = datetime.datetime.utcnow()
            age_calculated = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age_calculated < 18:
                is_underage = True
        except ValueError:
            pass

    if is_underage:
        user.age_verified = False
        user.eligibility_status = "AGE_RESTRICTED"
        db.commit()
        return AgeVerificationResponse(
            user_id=user.id,
            is_verified=False,
            verified=False,
            minimum_age=18,
            status="AGE_RESTRICTED",
            provider="Simulated 18+ Attribute Verification"
        )
        
    user.age_verified = True
    user.age_verified_at = datetime.datetime.utcnow()
    user.verification_method = payload.verification_method or "DEMO_ATTRIBUTE"
    if user.kyc_verified and not user.self_excluded:
        user.eligibility_status = "ELIGIBLE"
    elif not user.kyc_verified:
        user.eligibility_status = "KYC_REQUIRED"
    db.commit()
    
    return AgeVerificationResponse(
        user_id=user.id,
        is_verified=True,
        verified=True,
        minimum_age=18,
        status="VERIFIED_AGE_OVER_18",
        provider="Simulated 18+ Attribute Verification"
    )

@app.post("/api/compliance/kyc-demo", response_model=KYCDemoResponse, tags=["Compliance"])
def submit_kyc_demo(payload: KYCDemoRequest, db: Session = Depends(get_db)):
    """Conceptual synthetic KYC verification step using dummy document types."""
    uid = payload.user_id or payload.anonymous_user_id or "usr_demo"
    user = db.query(UserProfile).filter(
        (UserProfile.id == uid) | (UserProfile.anonymous_id == uid)
    ).first()
    
    if not user:
        user = UserProfile(id=uid, anonymous_id=uid, age_verified=True)
        db.add(user)
        
    user.kyc_verified = True
    user.kyc_document_type = payload.document_type or "National ID"
    if user.age_verified and not user.self_excluded:
        user.eligibility_status = "ELIGIBLE"
    db.commit()
    
    return KYCDemoResponse(
        user_id=user.id,
        kyc_verified=True,
        document_type=user.kyc_document_type,
        status="VERIFIED",
        demo=True,
        notice="Demo verification — no real identity data processed."
    )

@app.post("/api/compliance/self-exclusion-check", response_model=SelfExclusionResponse, tags=["Compliance"])
def check_self_exclusion(payload: SelfExclusionRequest, db: Session = Depends(get_db)):
    """Deterministic mock register check for excluded players."""
    uid = payload.user_id or payload.anonymous_user_id or payload.demo_profile_id or "usr_demo"
    user = db.query(UserProfile).filter(
        (UserProfile.id == uid) | (UserProfile.anonymous_id == uid)
    ).first()

    # Keep the existing UI persona deterministic without adding a production rule.
    if uid == "usr_excluded_demo":
        user = user or UserProfilingService.get_or_create_user(db, user_id=uid)
        user.self_excluded = True
        user.eligibility_status = "SELF_EXCLUDED"
        db.commit()

    is_excluded = user.self_excluded if user else False
    status_str = "EXCLUDED" if is_excluded else "ACTIVE_NOT_EXCLUDED"
    
    return SelfExclusionResponse(
        user_id=uid,
        checked=True,
        excluded=is_excluded,
        self_excluded=is_excluded,
        eligible=not is_excluded,
        source="DEMO_REGISTER",
        status=status_str
    )

@app.post("/api/compliance/betting-eligibility", response_model=BettingEligibilityResponse, tags=["Compliance"])
def evaluate_betting_eligibility(payload: BettingEligibilityRequest, db: Session = Depends(get_db)):
    """
    Core Machine 2 Gate: Returns single eligibility decision for betting access.
    Checks age_verified == True AND kyc_verified == True AND self_excluded == False.
    """
    uid = payload.user_id or payload.anonymous_user_id
    if not uid and payload.session_id:
        sess = db.query(DBSession).filter(DBSession.id == payload.session_id).first()
        if sess:
            uid = sess.user_id
            
    uid = uid or "usr_demo"
    user = db.query(UserProfile).filter(
        (UserProfile.id == uid) | (UserProfile.anonymous_id == uid)
    ).first()
    
    if not user:
        return BettingEligibilityResponse(
            user_id=uid,
            eligible=False,
            age_verified=False,
            kyc_verified=False,
            self_excluded=False,
            reason="PENDING_VERIFICATION",
            status="PENDING_VERIFICATION",
            demo=True
        )
        
    if user.self_excluded:
        return BettingEligibilityResponse(
            user_id=user.id,
            eligible=False,
            age_verified=user.age_verified,
            kyc_verified=user.kyc_verified,
            self_excluded=True,
            reason="Betting access is unavailable for this account due to self-exclusion.",
            status="SELF_EXCLUDED",
            demo=True
        )

    if not user.age_verified:
        return BettingEligibilityResponse(
            user_id=user.id,
            eligible=False,
            age_verified=False,
            kyc_verified=user.kyc_verified,
            self_excluded=False,
            reason="Betting is available only after 18+ age verification.",
            status="AGE_RESTRICTED",
            demo=True
        )

    if not user.kyc_verified:
        return BettingEligibilityResponse(
            user_id=user.id,
            eligible=False,
            age_verified=True,
            kyc_verified=False,
            self_excluded=False,
            reason="Identity verification (KYC demo) is required before placing bets.",
            status="KYC_REQUIRED",
            demo=True
        )

    user.eligibility_status = "ELIGIBLE"
    db.commit()

    return BettingEligibilityResponse(
        user_id=user.id,
        eligible=True,
        age_verified=True,
        kyc_verified=True,
        self_excluded=False,
        reason="ELIGIBLE",
        status="ELIGIBLE",
        demo=True
    )

@app.get("/api/compliance/status/{user_id}", response_model=ComplianceStatusResponse, tags=["Compliance"])
def get_compliance_status(user_id: str, db: Session = Depends(get_db)):
    """Exposes compliance status for Machine 3 & UI consumption."""
    user = db.query(UserProfile).filter(
        (UserProfile.id == user_id) | (UserProfile.anonymous_id == user_id)
    ).first()
    
    if not user:
        return ComplianceStatusResponse(
            user_id=user_id,
            betting_eligible=False,
            age_verified=False,
            kyc_verified=False,
            self_excluded=False,
            status="PENDING_VERIFICATION"
        )
        
    is_eligible = user.age_verified and user.kyc_verified and not user.self_excluded
    status_str = "ELIGIBLE" if is_eligible else (
        "SELF_EXCLUDED" if user.self_excluded else (
            "AGE_RESTRICTED" if not user.age_verified else "KYC_REQUIRED"
        )
    )
    
    return ComplianceStatusResponse(
        user_id=user.id,
        anonymous_id=user.anonymous_id,
        betting_eligible=is_eligible,
        age_verified=user.age_verified,
        kyc_verified=user.kyc_verified,
        self_excluded=user.self_excluded,
        status=status_str,
        verification_method=user.verification_method or "DEMO_ATTRIBUTE"
    )

# ==================================================
# Users Endpoints
# ==================================================
@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Register or initialize a user profile."""
    uid = payload.id or f"usr_{uuid.uuid4().hex[:8]}"
    existing = db.query(UserProfile).filter(UserProfile.id == uid).first()
    if existing:
        return UserProfilingService.get_user_summary(db, existing.id)
        
    user = UserProfile(
        id=uid,
        anonymous_id=payload.anonymous_id or f"anon_{uuid.uuid4().hex[:10]}",
        segment=payload.segment or "Casual Explorer"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserProfilingService.get_user_summary(db, user.id)

@app.get("/api/users/{id}", response_model=UserResponse, tags=["Users"])
def get_user(id: str, db: Session = Depends(get_db)):
    """Fetch user profile and behavioral segmentation."""
    user = db.query(UserProfile).filter(UserProfile.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfilingService.get_user_summary(db, user.id)

@app.get("/api/users/{id}/profile", tags=["Users"])
def get_user_compact_profile(id: str, db: Session = Depends(get_db)):
    """Fetch compact FEG historical behavioral profile for user."""
    return UserProfilingService.get_historical_player_profile(db, id)

@app.get("/api/users/{id}/recommendation-profile", tags=["Users"])
def get_user_recommendation_profile(id: str, db: Session = Depends(get_db)):
    """Returns compact recommendation profile prior for PULSYNC recommendation engine (< 10 KB)."""
    rec_profiles = load_processed_json("recommendation_profiles.json", {})
    if id in rec_profiles:
        return rec_profiles[id]
    if "demo_profile" in rec_profiles:
        return rec_profiles["demo_profile"]
    return {
        "profile_id": id,
        "sport_affinity": {"Football": 0.75, "Tennis": 0.15},
        "event_affinity": {},
        "content_affinity": {"Team Comparison": 0.90, "Key Statistics": 0.85},
        "activity_level": "HIGH"
    }

# ==================================================
# Sessions Endpoints
# ==================================================
@app.post("/api/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED, tags=["Sessions"])
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    """Initialize a new user session."""
    sid = getattr(payload, "id", None) or getattr(payload, "session_id", None) or f"sess_{uuid.uuid4().hex[:10]}"
    anon_id = getattr(payload, "anonymous_user_id", None) or getattr(payload, "anonymous_id", None) or getattr(payload, "user_id", None)
    uid = getattr(payload, "user_id", None) or anon_id
    
    existing = db.query(DBSession).filter(DBSession.id == sid).first()
    if existing:
        existing.session_id = existing.id
        return existing
        
    user = UserProfilingService.get_or_create_user(db, user_id=uid, anonymous_id=anon_id)
    session_user_id = user.id if user else uid
    session = DBSession(
        id=sid,
        user_id=session_user_id,
        started_at=datetime.datetime.utcnow(),
        is_synthetic=payload.is_synthetic,
        status="ACTIVE"
    )
    try:
        db.add(session)
        db.commit()
        db.refresh(session)
    except IntegrityError:
        db.rollback()
        existing = db.query(DBSession).filter(DBSession.id == sid).first()
        if existing:
            existing.session_id = existing.id
            return existing
        raise

    session.session_id = session.id
    return session

@app.get("/api/sessions/{id}", response_model=SessionResponse, tags=["Sessions"])
def get_session(id: str, db: Session = Depends(get_db)):
    """Retrieve session state and metrics."""
    session = db.query(DBSession).filter(DBSession.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.session_id = session.id
    return session

# ==================================================
# Events & Realtime Intelligence
# ==================================================
@app.post("/api/sessions/{id}/events", response_model=SessionIntelligenceResponse, tags=["Events & Intelligence"])
def ingest_event(id: str, payload: EventCreate, db: Session = Depends(get_db)):
    """
    Ingests live frontend telemetry event and immediately triggers the unified Session Intelligence pipeline.
    """
    session = db.query(DBSession).filter(DBSession.id == id).first()
    if not session:
        session = DBSession(
            id=id,
            user_id=payload.user_id,
            started_at=payload.timestamp or datetime.datetime.utcnow(),
            is_synthetic=False,
            status="ACTIVE"
        )
        db.add(session)
        db.commit()
        
    user_id = payload.user_id or session.user_id
    if user_id:
        UserProfilingService.get_or_create_user(db, user_id)
        
    event = Event(
        session_id=id,
        user_id=user_id,
        timestamp=payload.timestamp or datetime.datetime.utcnow(),
        event_type=payload.event_type,
        page=payload.page,
        action=payload.action,
        sport=payload.sport,
        match_id=payload.match_id
    )
    if payload.metadata:
        event.set_metadata(payload.metadata)
        
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # Process through unified intelligence pipeline
    intel = SessionIntelligenceService.process_event(db, id, event)
    
    # Expose nested intelligence format expected by frontend client
    intel["intelligence"] = {
        "intent": {
            "label": intel["intent"],
            "confidence": intel["intent_confidence"],
            "reason": intel["intent_reason"]
        },
        "abandonment": {
            "probability": intel["abandonment_probability"],
            "risk": intel["abandonment_risk_level"],
            "reason": intel["abandonment_reason"]
        },
        "friction": {
            "score": intel["friction_score"],
            "level": intel["friction_level"],
            "reason": intel["friction_reason"]
        },
        "recommendations": intel["recommendations"],
        "guidance": {
            "show": intel["guidance"]["should_intervene"],
            "message": intel["guidance"]["guidance_message"],
            "action": intel["guidance"]["recommended_action"],
            "content_id": intel["guidance"]["content_id"]
        },
        "session_quality": {
            "score": intel["session_quality_score"],
            "explanation": intel["session_quality_explanation"]
        }
    }
    return intel

@app.get("/api/sessions/{id}/intelligence", response_model=SessionIntelligenceResponse, tags=["Events & Intelligence"])
def get_session_intelligence(id: str, db: Session = Depends(get_db)):
    """Get current session intelligence (intent, friction, abandonment, guidance)."""
    intel = SessionIntelligenceService.get_intelligence(db, id)
    if not intel:
        raise HTTPException(status_code=404, detail="Session not found or has no activity.")
    return intel

@app.get("/api/sessions/{id}/score", response_model=SessionScoreResponse, tags=["Sessions"])
def get_session_score(id: str, db: Session = Depends(get_db)):
    """Authoritative Session Quality Score breakdown with trend and factor impacts."""
    intel = SessionIntelligenceService.get_intelligence(db, id)
    if not intel:
        raise HTTPException(status_code=404, detail="Session not found or has no activity.")
        
    preds = db.query(SessionPrediction).filter(SessionPrediction.session_id == id).order_by(SessionPrediction.created_at.asc()).all()
    delta = 0.0
    trend = "STABLE"
    if len(preds) >= 2:
        delta = round(preds[-1].quality_score - preds[0].quality_score, 1)
        if delta > 2.0:
            trend = "IMPROVING"
        elif delta < -2.0:
            trend = "DECLINING"
            
    factors = intel.get("score_factors", [])
    return SessionScoreResponse(
        session_id=id,
        session_quality_score=intel["session_quality_score"],
        session_quality=intel["session_quality"],
        explanation=intel["session_quality_explanation"],
        factors=factors,
        score_factors=factors,
        trend=trend,
        delta=delta,
        abandonment_probability=intel["abandonment_probability"],
        friction_score=intel["friction_score"]
    )

# ==================================================
# Matches
# ==================================================
@app.get("/api/matches", response_model=List[MatchResponse], tags=["Matches"])
def list_matches(sport: Optional[str] = None, db: Session = Depends(get_db)):
    """List available matches with optional sport filter."""
    query = db.query(Match)
    if sport:
        query = query.filter(Match.sport.ilike(f"%{sport}%"))
    matches = query.limit(20).all()
    if not matches:
        now = datetime.datetime.utcnow()
        sample_matches = [
            Match(id="match_el_clasico", sport="Football", team_home="Real Madrid", team_away="FC Barcelona", start_time=now + datetime.timedelta(hours=3), status="UPCOMING"),
            Match(id="match_mci_ars", sport="Football", team_home="Manchester City", team_away="Arsenal", start_time=now + datetime.timedelta(hours=5), status="UPCOMING"),
            Match(id="match_lal_gsw", sport="Basketball", team_home="LA Lakers", team_away="Golden State Warriors", start_time=now + datetime.timedelta(hours=7), status="UPCOMING"),
            Match(id="match_alcaraz_sinner", sport="Tennis", team_home="Carlos Alcaraz", team_away="Jannik Sinner", start_time=now + datetime.timedelta(hours=1), status="LIVE")
        ]
        db.add_all(sample_matches)
        db.commit()
        matches = sample_matches
    return matches

@app.get("/api/matches/{id}", response_model=MatchResponse, tags=["Matches"])
def get_match(id: str, db: Session = Depends(get_db)):
    """Get match details."""
    match = db.query(Match).filter(Match.id == id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

# ==================================================
# Recommendations & Feedback
# ==================================================
@app.get("/api/recommendations/{session_id}", response_model=RecommendationListResponse, tags=["Recommendations"])
def get_recommendations(session_id: str, db: Session = Depends(get_db)):
    """
    Returns ranked, explainable next-best informational content recommendations.
    STRICTLY NON-GAMBLING: Recommends insights, comparisons, form, rules, and statistics.
    """
    intel = SessionIntelligenceService.get_intelligence(db, session_id)
    if not intel:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    user = db.query(UserProfile).filter(UserProfile.id == session.user_id).first() if session.user_id else None
    events = db.query(Event).filter(Event.session_id == session_id).order_by(Event.timestamp.asc()).all()
    previous_recs = db.query(Recommendation).filter(Recommendation.session_id == session_id).all()
    
    from backend.services.recommendation_engine import RecommendationEngine
    recs = RecommendationEngine.generate_recommendations(
        session=session,
        user=user,
        events=events,
        current_intent=intel["intent"],
        friction_level=intel["friction_level"],
        abandonment_probability=intel["abandonment_probability"],
        previous_recommendations=previous_recs
    )
    
    return RecommendationListResponse(
        session_id=session_id,
        intent=intel["intent"],
        friction_level=intel["friction_level"],
        recommendations=[RecommendationItem(**r) for r in recs]
    )

@app.post("/api/recommendations/{session_id}/feedback", tags=["Recommendations"])
def submit_recommendation_feedback(
    session_id: str, 
    payload: RecommendationFeedbackRequest, 
    db: Session = Depends(get_db)
):
    """
    Records user feedback (clicked, dismissed, ignored) to adapt recommendation scoring.
    Supports both payload.feedback_type and payload.action.
    """
    fb_type = payload.feedback_type or payload.action or "clicked"
    rec = None
    if payload.recommendation_id:
        try:
            rec_id_int = int(payload.recommendation_id)
            rec = db.query(Recommendation).filter(Recommendation.id == rec_id_int).first()
        except (ValueError, TypeError):
            rec = db.query(Recommendation).filter(
                Recommendation.session_id == session_id,
                Recommendation.content_id == str(payload.recommendation_id)
            ).order_by(Recommendation.id.desc()).first()
            
    if not rec and payload.content_id:
        rec = db.query(Recommendation).filter(
            Recommendation.session_id == session_id,
            Recommendation.content_id == payload.content_id
        ).order_by(Recommendation.id.desc()).first()
        
    content_id = payload.content_id or (rec.content_id if rec else "content_unknown")
    if not rec:
        rec = Recommendation(
            session_id=session_id,
            content_id=content_id,
            content_type="Content",
            reason="User interaction logged",
            shown_at=datetime.datetime.utcnow()
        )
        db.add(rec)
        
    if fb_type == "clicked":
        rec.clicked = True
    elif fb_type == "dismissed":
        rec.dismissed = True
        
    db.commit()
    return {"status": "success", "content_id": content_id, "feedback": fb_type}

# ==================================================
# Outcomes
# ==================================================
@app.post("/api/outcomes", response_model=OutcomeResponse, status_code=status.HTTP_201_CREATED, tags=["Outcomes"])
def record_outcome(payload: OutcomeCreate, db: Session = Depends(get_db)):
    """Record session outcome and decision point."""
    outcome = Outcome(
        session_id=payload.session_id,
        recommendation_id=payload.recommendation_id,
        decision=payload.decision,
        content_viewed=payload.content_viewed,
        session_continued=payload.session_continued,
        created_at=datetime.datetime.utcnow()
    )
    db.add(outcome)
    db.commit()
    db.refresh(outcome)
    return outcome

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROCESSED_DATA_DIR = os.path.join(REPO_ROOT, "data", "processed")


def load_processed_json(filename: str, fallback: Optional[Any] = None):
    candidates = [
        os.path.join(PROCESSED_DATA_DIR, filename),
        os.path.join("data", "processed", filename),
    ]
    for filepath in candidates:
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                continue
    return fallback if fallback is not None else {}


# ==================================================
# Dashboard Analytics
# ==================================================
@app.get("/api/dashboard/dataset-summary", tags=["Dashboard"])
def get_dataset_summary():
    """Returns FEG dataset summary metrics (< 10 KB)."""
    return load_processed_json("dataset_summary.json", {
        "dataset_name": "SB_Player",
        "total_records": 3005499,
        "date_range": {"from": "2026-08-16", "to": "2026-08-31"},
        "unique_players": 15738,
        "unique_sports": 38,
        "unique_events": 5731,
        "data_quality": {"duplicate_rows": 0, "missing_player_id": 0, "data_quality_score": 98.5}
    })

@app.get("/api/dashboard/sports", tags=["Dashboard"])
def get_dashboard_sports():
    """Returns top 10 sports summary (< 10 KB)."""
    return load_processed_json("sports_summary.json", [])

@app.get("/api/dashboard/events", tags=["Dashboard"])
def get_dashboard_events():
    """Returns top 50 events summary (< 100 KB)."""
    return load_processed_json("events_summary.json", [])

@app.get("/api/dashboard/metrics", response_model=DashboardMetricsResponse, tags=["Dashboard"])
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Aggregate KPIs across sessions, users, quality, and engagement."""
    return DashboardAnalyticsService.get_metrics(db)

@app.get("/api/dashboard/segments", response_model=DashboardSegmentsResponse, tags=["Dashboard"])
def get_dashboard_segments(db: Session = Depends(get_db)):
    """User segment distribution across the platform."""
    return {"segments": DashboardAnalyticsService.get_segments(db)}

@app.get("/api/dashboard/recommendations", response_model=DashboardRecommendationsResponse, tags=["Dashboard"])
def get_dashboard_recommendations(db: Session = Depends(get_db)):
    """Performance metrics (impressions, clicks, CTR) per informational content type."""
    return {"performance": DashboardAnalyticsService.get_recommendations_performance(db)}

@app.get("/api/dashboard/quality", response_model=DashboardQualityResponse, tags=["Dashboard"])
def get_dashboard_quality(db: Session = Depends(get_db)):
    """Session quality and abandonment metrics by user segment."""
    data = DashboardAnalyticsService.get_quality_and_abandonment_by_segment(db)
    return DashboardQualityResponse(**data)

@app.get("/api/dashboard/impact", response_model=DashboardImpactResponse, tags=["Dashboard"])
def get_dashboard_impact(db: Session = Depends(get_db)):
    """Prototype Impact Simulation metrics."""
    data = DashboardAnalyticsService.get_impact_simulation(db)
    return DashboardImpactResponse(**data)

# ==================================================
# Demo Mode Endpoint
# ==================================================
@app.post("/api/demo/start", tags=["Demo Mode"])
def start_demo_session(payload: Optional[DemoStartRequest] = None, db: Session = Depends(get_db)):
    """
    Executes a complete, deterministic demonstration session illustrating high friction,
    abandonment surge, reactive contextual guidance, and outcome resolution.
    """
    uid = payload.user_id if payload else "demo_fan_01"
    mid = payload.match_id if payload else "match_el_clasico"
    return DemoSimulationService.run_demo_simulation(db, user_id=uid, match_id=mid)


# ==================================================
# Frontend Compatibility Endpoints (Sports, Events, Auth, Wallet, Promotions)
# ==================================================
@app.get("/api/auth/me", tags=["Auth"])
def get_auth_me():
    return {
        "user": {
            "id": "usr_demo",
            "email": "fan@pulsync.ai",
            "displayName": "Sports Enthusiast",
            "roles": ["customer", "bettor"],
            "status": "active",
            "city": "London"
        },
        "permissions": ["view_events", "place_bets", "view_intelligence"],
        "portal": "customer",
        "wallet": {
            "available": 1000.0,
            "bonus": 50.0,
            "currency": "EUR"
        }
    }


@app.post("/api/auth/login", tags=["Auth"])
def auth_login(payload: Optional[Dict[str, Any]] = None, db: Session = Depends(get_db)):
    sid = payload.get("session_id") if payload else None
    if sid:
        sess = db.query(DBSession).filter(DBSession.id == sid).first()
        if sess:
            UserProfilingService.get_or_create_user(db, user_id="usr_demo")
            sess.user_id = "usr_demo"
            events = db.query(Event).filter(Event.session_id == sid).all()
            for ev in events:
                ev.user_id = "usr_demo"
            db.commit()
    return {
        "ok": True,
        "token": "demo_jwt_token",
        "user": {
            "id": "usr_demo",
            "email": "fan@pulsync.ai",
            "displayName": "Sports Enthusiast",
            "roles": ["customer"]
        }
    }


@app.post("/api/auth/logout", tags=["Auth"])
def auth_logout():
    return {"ok": True}


def get_sport_slug(name: str) -> str:
    return name.lower().replace(" ", "_")


@app.get("/api/sports", tags=["Sports & Events"])
def list_sports_rail(db: Session = Depends(get_db)):
    """
    Returns list of sports aggregated from real dataset in pulsync.db.
    """
    rows = (
        db.query(Event.sport, func.count(func.distinct(Event.match_id)), func.count(Event.id))
        .filter(Event.sport.isnot(None), Event.sport != "")
        .group_by(Event.sport)
        .order_by(func.count(Event.id).desc())
        .all()
    )
    
    sports = []
    for sport_name, match_cnt, evt_cnt in rows:
        if sport_name in ["World Lotteries", "TOP OFFER"]:
            continue
        slug = get_sport_slug(sport_name)
        sports.append({
            "id": slug,
            "slug": slug,
            "name": sport_name,
            "eventCount": match_cnt if match_cnt > 0 else evt_cnt,
            "liveCount": 1 if sport_name in ["Football", "Tennis", "Basketball"] else 0
        })

    if not sports:
        summary = load_processed_json("sports_summary.json", [])
        for item in summary:
            sport_name = item.get("sport") if isinstance(item, dict) else None
            if not sport_name or sport_name in ["World Lotteries", "TOP OFFER"]:
                continue
            slug = get_sport_slug(sport_name)
            sports.append({
                "id": slug,
                "slug": slug,
                "name": sport_name,
                "eventCount": item.get("activity_count", 0),
                "liveCount": 1 if sport_name in ["Football", "Tennis", "Basketball"] else 0
            })

    return {"sports": sports}


@app.get("/api/promotions", tags=["Promotions"])
def get_promotions():
    banners = [
        {"id": "p1", "title": "PULSYNC Live Intelligence", "subtitle": "AI-powered real-time sports analytics", "theme": "sports"},
        {"id": "p2", "title": "Contextual Guidance Active", "subtitle": "Right Information at the Right Time", "theme": "live"},
        {"id": "p3", "title": "Session Quality Tracking", "subtitle": "Friction-free exploration experience", "theme": "casino"}
    ]
    promotions = [
        {"id": "p1", "title": "PULSYNC Live Intelligence", "subtitle": "AI-powered real-time sports analytics", "theme": "sports", "status": "PUBLISHED", "description": "Explore real-time telemetry and contextual guidance."},
        {"id": "p2", "title": "Contextual Guidance Active", "subtitle": "Right Information at the Right Time", "theme": "live", "status": "PUBLISHED", "description": "Automated insights and head-to-head comparison tools."},
        {"id": "p3", "title": "Session Quality Tracking", "subtitle": "Friction-free exploration experience", "theme": "sports", "status": "PUBLISHED", "description": "Continuous telemetry monitoring with personalized suggestions."}
    ]
    return {"banners": banners, "promotions": promotions}


@app.get("/api/events", tags=["Sports & Events"])
def list_events_feed(
    sport: Optional[str] = "all",
    day: Optional[str] = "all",
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = (
        db.query(
            Event.match_id,
            Event.sport,
            func.count(Event.id).label("event_count")
        )
        .filter(
            Event.match_id.isnot(None), 
            Event.match_id != "",
            Event.sport.notin_(["World Lotteries", "TOP OFFER"])
        )
    )
    
    if sport and sport.lower() != "all":
        query = query.filter(
            func.lower(func.replace(Event.sport, " ", "_")) == sport.lower()
        )
        
    rows = (
        query.group_by(Event.match_id, Event.sport)
        .order_by(func.count(Event.id).desc())
        .all()
    )

    if not rows:
        summary = load_processed_json("events_summary.json", [])
        compact_rows = []
        for item in summary:
            if not isinstance(item, dict):
                continue
            sport_name = item.get("sport") or ""
            match_id = item.get("event_name") or ""
            if not match_id or sport_name in ["World Lotteries", "TOP OFFER"]:
                continue
            if sport and sport.lower() != "all" and get_sport_slug(sport_name) != sport.lower():
                continue
            compact_rows.append((match_id, sport_name, item.get("activity_count", 0)))
        rows = compact_rows

    if status and status.lower() == "live":
        # Historical events do not carry a live status. Keep the existing
        # demo-live surface to one representative fixture rather than
        # presenting the historical dataset as live.
        rows = rows[:1]
    elif sport and sport.lower() == "all":
        # Keep the compact feed responsive while ensuring All is not
        # dominated by the highest-volume sport.
        rows_by_sport = {}
        for row in rows:
            rows_by_sport.setdefault(row[1], []).append(row)
        balanced_rows = []
        row_index = 0
        while len(balanced_rows) < 60:
            added = False
            for sport_rows in rows_by_sport.values():
                if row_index < len(sport_rows):
                    balanced_rows.append(sport_rows[row_index])
                    added = True
                    if len(balanced_rows) == 60:
                        break
            if not added:
                break
            row_index += 1
        rows = balanced_rows
    else:
        rows = rows[:60]
    
    now = datetime.datetime.utcnow()
    events_data = []
    
    for idx, (match_id, sport_name, cnt) in enumerate(rows):
        if " - " in match_id:
            home, away = match_id.split(" - ", 1)
        else:
            home, away = match_id, "Opponent"
            
        h_val = abs(hash(match_id))
        is_live = bool(status and status.lower() == "live")
        event_status = "LIVE" if is_live else "UPCOMING"
        
        odds_home = round(1.4 + (h_val % 25) / 10.0, 2)
        odds_draw = round(3.1 + ((h_val >> 2) % 15) / 10.0, 2)
        odds_away = round(2.1 + ((h_val >> 4) % 30) / 10.0, 2)
        
        slug = get_sport_slug(sport_name or "Football")
        
        selections = [
            {"id": f"sel_{idx}_1", "name": home, "odds": odds_home},
        ]
        if sport_name != "Tennis":
            selections.append({"id": f"sel_{idx}_2", "name": "Draw", "odds": odds_draw})
        selections.append({"id": f"sel_{idx}_3", "name": away, "odds": odds_away})
        
        comp_name = f"{sport_name} League" if sport_name else "Major League"
        if "Real Madrid" in match_id or "Barcelona" in match_id or "Elche" in match_id or "Espanyol" in match_id:
            comp_name = "La Liga"
        elif "Man." in match_id or "Arsenal" in match_id or "Chelsea" in match_id or "Newcastle" in match_id or "Brighton" in match_id or "Liverpool" in match_id:
            comp_name = "Premier League"
        elif "Dinamo Zagreb" in match_id or "Hajduk" in match_id or "Istra" in match_id or "Rijeka" in match_id:
            comp_name = "HNL League"
        elif "Milano" in match_id or "Torino" in match_id or "Napoli" in match_id or "Genoa" in match_id or "Cagliari" in match_id:
            comp_name = "Serie A"
        elif "Paris SG" in match_id or "Rennes" in match_id or "Lens" in match_id or "Lille" in match_id:
            comp_name = "Ligue 1"
        elif sport_name == "Tennis":
            comp_name = "ATP Tour"
        elif sport_name == "Basketball":
            comp_name = "FIBA World Tour"
        elif sport_name == "Baseball":
            comp_name = "MLB"

        start_offset = (idx % 8 + 1) if (day and day.lower() == "today") else ((idx % 8 + 24) if (day and day.lower() == "tomorrow") else (idx % 12 + 1))
        events_data.append({
            "id": f"match_{idx}_{slug}",
            "match_id": match_id,
            "home": home,
            "away": away,
            "startsAt": (now + datetime.timedelta(hours=start_offset)).isoformat() + "Z",
            "status": event_status,
            "homeScore": (h_val % 3) if is_live else 0,
            "awayScore": ((h_val >> 3) % 3) if is_live else 0,
            "clockSeconds": (h_val % 4000) if is_live else 0,
            "sport": {"name": sport_name or "Football", "slug": slug},
            "competition": {"name": comp_name},
            "marketCount": 12 + (h_val % 15),
            "primaryMarket": {"id": f"m_{idx}", "name": "Match Winner" if sport_name == "Tennis" else "Match Result", "status": "OPEN"},
            "primarySelections": selections
        })

    if status and status.lower() == "live":
        events_data = [e for e in events_data if e["status"] == "LIVE"]

    return {"events": events_data, "total": len(events_data)}


@app.get("/api/events/{id}", tags=["Sports & Events"])
def get_event_detail(id: str, db: Session = Depends(get_db)):
    now = datetime.datetime.utcnow()
    event_row = db.query(Event).filter(
        (Event.match_id == id) | (Event.match_id.ilike(f"%{id.replace('match_', '')}%"))
    ).first()
    
    match_id = event_row.match_id if (event_row and event_row.match_id) else "Elche - Barcelona"
    sport_name = event_row.sport if (event_row and event_row.sport) else "Football"
    
    if " - " in match_id:
        home, away = match_id.split(" - ", 1)
    else:
        home, away = match_id, "Opponent"
        
    h_val = abs(hash(match_id))
    
    selections = [
        {"id": f"sel_{id}_1", "name": home, "odds": round(1.4 + (h_val % 25) / 10.0, 2), "status": "ACTIVE"},
        {"id": f"sel_{id}_2", "name": "Draw", "odds": round(3.1 + ((h_val >> 2) % 15) / 10.0, 2), "status": "ACTIVE"} if sport_name != "Tennis" else None,
        {"id": f"sel_{id}_3", "name": away, "odds": round(2.1 + ((h_val >> 4) % 30) / 10.0, 2), "status": "ACTIVE"}
    ]
    selections = [s for s in selections if s is not None]
    
    return {
        "event": {
            "id": id,
            "match_id": match_id,
            "home": home,
            "away": away,
            "startsAt": (now + datetime.timedelta(hours=2)).isoformat() + "Z",
            "status": "UPCOMING",
            "homeScore": 0,
            "awayScore": 0,
            "clockSeconds": 0,
            "competition": {"name": f"{sport_name} Championship"},
            "sport": {"name": sport_name, "slug": get_sport_slug(sport_name)},
            "markets": [
                {
                    "id": "m_result",
                    "name": "Match Result (1X2)" if sport_name != "Tennis" else "Match Winner",
                    "status": "OPEN",
                    "selections": selections
                },
                {
                    "id": "m_overunder",
                    "name": "Total Goals (Over/Under 2.5)",
                    "status": "OPEN",
                    "selections": [
                        {"id": "sel_ou_1", "name": "Over 2.5", "odds": 1.70, "status": "ACTIVE"},
                        {"id": "sel_ou_2", "name": "Under 2.5", "odds": 2.15, "status": "ACTIVE"}
                    ]
                }
            ]
        }
    }


@app.get("/api/wallet", tags=["Wallet"])
def get_wallet():
    return {
        "wallet": {
            "available": 1000.0,
            "bonus": 50.0,
            "currency": "EUR"
        },
        "transactions": [
            {"id": "tx_1", "type": "DEPOSIT", "amount": 100.0, "status": "COMPLETED", "created_at": datetime.datetime.utcnow().isoformat() + "Z"}
        ]
    }


@app.get("/api/bets", tags=["Bets"])
def list_bets(filter: Optional[str] = "open"):
    return {"bets": []}


@app.post("/api/bets", tags=["Bets"])
def place_bet(payload: Optional[Dict[str, Any]] = None, db: Session = Depends(get_db)):
    """
    Enforces Machine 2 Gate on Bet Placement.
    Backend evaluates age_verified, kyc_verified, self_excluded.
    Rejects ineligible users with HTTP 403.
    Tracks bet_confirmed and bet_cancelled events when session_id is provided.
    """
    sid = payload.get("session_id") if payload else None
    uid = (payload.get("user_id") or payload.get("anonymous_user_id")) if payload else None
    if not uid and sid:
        sess = db.query(DBSession).filter(DBSession.id == sid).first()
        if sess:
            uid = sess.user_id
    uid = uid or "usr_demo"
    
    user = db.query(UserProfile).filter(
        (UserProfile.id == uid) | (UserProfile.anonymous_id == uid)
    ).first()
    
    is_eligible = (user is not None) and user.age_verified and user.kyc_verified and not user.self_excluded
    
    if not is_eligible:
        status_str = "SELF_EXCLUDED" if (user and user.self_excluded) else (
            "AGE_RESTRICTED" if (user and not user.age_verified) else "KYC_REQUIRED"
        )
        reason_str = "Betting access is unavailable due to self-exclusion." if (user and user.self_excluded) else (
            "18+ Age verification required before placing bets." if (user and not user.age_verified) else "Identity verification (KYC demo) required."
        )
        if sid:
            blocked_event = Event(
                session_id=sid,
                user_id=uid,
                timestamp=datetime.datetime.utcnow(),
                event_type="action",
                page="betslip",
                action="bet_cancelled"
            )
            blocked_event.set_metadata({"reason": reason_str, "status": status_str})
            db.add(blocked_event)
            db.commit()
            
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "eligible": False,
                "status": status_str,
                "reason": reason_str,
                "message": f"Betting blocked by PULSYNC Compliance Gate: {reason_str}"
            }
        )

    bet_id = f"bet_{uuid.uuid4().hex[:8]}"
    if sid:
        confirm_event = Event(
            session_id=sid,
            user_id=uid,
            timestamp=datetime.datetime.utcnow(),
            event_type="action",
            page="betslip",
            action="bet_confirmed"
        )
        confirm_event.set_metadata({
            "bet_id": bet_id,
            "amount": payload.get("amount", 10.0),
            "selections": payload.get("selections", [])
        })
        db.add(confirm_event)
        
        sess = db.query(DBSession).filter(DBSession.id == sid).first()
        if sess:
            sess.user_id = uid
            sess.total_actions = (sess.total_actions or 0) + 1
            sess.total_events = (sess.total_events or 0) + 1
        db.commit()

    return {
        "ok": True,
        "eligible": True,
        "betId": bet_id,
        "status": "ACCEPTED",
        "demo": True
    }


@app.get("/api/casino", tags=["Casino"])
def list_casino_games(category: Optional[str] = "all"):
    return {"games": [], "categories": ["slots", "table", "live"]}


@app.get("/api/notifications", tags=["System"])
def get_notifications():
    return {"notifications": [], "unread": 0}


@app.get("/api/analytics", tags=["Dashboard"])
def get_frontend_analytics(db: Session = Depends(get_db)):
    metrics = DashboardAnalyticsService.get_metrics(db)
    sports_data = load_processed_json("sports_summary.json", [])
    bets_by_sport = [{"name": s["sport"], "value": s["activity_count"]} for s in sports_data[:6]]
    if not bets_by_sport:
        bets_by_sport = [
            {"name": "Football", "value": 2765432},
            {"name": "Tennis", "value": 124530},
            {"name": "Basketball", "value": 52140},
            {"name": "Baseball", "value": 32100},
            {"name": "Ice Hockey", "value": 20120}
        ]
    by_day = [
        {"day": "Mon", "bets": 120, "turnover": 4500},
        {"day": "Tue", "bets": 180, "turnover": 6200},
        {"day": "Wed", "bets": 210, "turnover": 7800},
        {"day": "Thu", "bets": 190, "turnover": 6900},
        {"day": "Fri", "bets": 310, "turnover": 11200},
        {"day": "Sat", "bets": 450, "turnover": 18500},
        {"day": "Sun", "bets": 380, "turnover": 15400}
    ]
    kpis = {
        "turnover": metrics.get("turnover", 70500.0),
        "totalBets": metrics.get("total_sessions", 15738),
        "activeCustomers": metrics.get("active_users", 15738),
        "liveEvents": 60
    }
    return {
        "kpis": kpis,
        "byDay": by_day,
        "betsBySport": bets_by_sport
    }


@app.get("/api/admin/audit", tags=["Admin"])
def get_admin_audit(q: Optional[str] = ""):
    return {"logs": [], "total": 0}


@app.get("/api/admin/flags", tags=["Admin"])
def get_admin_flags():
    return {"flags": [], "settings": []}


@app.get("/api/ops/events", tags=["Admin"])
def get_ops_events(status: Optional[str] = "all"):
    return {"events": []}


@app.get("/api/risk", tags=["Admin"])
def get_risk_alerts(status: Optional[str] = "all"):
    return {"alerts": []}


@app.get("/api/ledger", tags=["Admin"])
def get_ledger(q: Optional[str] = ""):
    return {"entries": []}


@app.get("/api/support", tags=["Support"])
def get_support_tickets():
    return {"tickets": []}


# ==================================================
# PULSYNC Session & ROI Intelligence API (Machine 4)
# ==================================================
@app.get("/api/impact/summary", tags=["Impact Intelligence"])
def get_impact_summary():
    """Returns top KPI summary, dataset facts, target segment metrics, and replay preview."""
    return ImpactAnalyticsService.get_summary()


@app.get("/api/impact/session-health", tags=["Impact Intelligence"])
def get_impact_session_health():
    """Returns session health funnel, durations, friction, quality, and daily trends."""
    return ImpactAnalyticsService.get_session_health()


@app.get("/api/impact/matrix", tags=["Impact Intelligence"])
def get_impact_matrix():
    """Returns 3x3 Transaction Intent vs Information Interest matrix."""
    return ImpactAnalyticsService.get_matrix()


@app.get("/api/impact/segments", tags=["Impact Intelligence"])
def get_impact_segments():
    """Returns 5 behavioral segments with metrics and shares."""
    return ImpactAnalyticsService.get_segments()


@app.get("/api/impact/replay", tags=["Impact Intelligence"])
def get_impact_replay():
    """Returns historical replay comparison between VALUE_SEEKING and RESPECT_EXIT cohorts with statistical test results."""
    return ImpactAnalyticsService.get_replay()


@app.get("/api/impact/opportunity", tags=["Impact Intelligence"])
def get_impact_opportunity():
    """Returns segment opportunity sizing for VALUE_SEEKING."""
    return ImpactAnalyticsService.get_opportunity()


@app.post("/api/impact/roi/simulate", tags=["Impact Intelligence"])
def simulate_roi(payload: Optional[ROISimulationRequest] = None):
    """Interactive ROI simulator supporting Conservative, Base, Optimistic scenarios and custom assumptions."""
    assumptions = payload.model_dump() if payload else {}
    return ImpactAnalyticsService.calculate_roi(assumptions)


@app.get("/api/impact/impact-case", tags=["Impact Intelligence"])
def get_impact_case(scenario: Optional[str] = "base"):
    """Auto-generates the one-page executive Impact Case."""
    return ImpactAnalyticsService.get_impact_case(scenario or "base")


@app.get("/api/impact/methodology", tags=["Impact Intelligence"])
def get_impact_methodology():
    """Returns data methodology, definitions, and causal limitation disclaimers."""
    data = ImpactAnalyticsService.get_raw_data()
    return data.get("methodology", {})


@app.get("/api/impact/metrics-chain", tags=["Impact Intelligence"])
def get_impact_metrics_chain():
    """Returns 4-level business metrics to follow and management signals."""
    return ImpactAnalyticsService.get_metrics_chain()
