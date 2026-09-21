from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

# ==================================================
# Compliance Schemas (Machine 2)
# ==================================================
class AgeVerificationRequest(BaseModel):
    user_id: Optional[str] = None
    anonymous_user_id: Optional[str] = None
    age: Optional[int] = None
    birth_date: Optional[str] = None
    verification_method: str = "DEMO_ATTRIBUTE"

class AgeVerificationResponse(BaseModel):
    user_id: Optional[str] = None
    is_verified: bool = True
    verified: bool = True
    minimum_age: int = 18
    status: str = "VERIFIED_AGE_OVER_18"
    provider: str = "Simulated Mock Age Verification (MVP)"
    timestamp: datetime = Field(default_factory=utc_now)

class SelfExclusionRequest(BaseModel):
    user_id: Optional[str] = None
    anonymous_user_id: Optional[str] = None
    demo_profile_id: Optional[str] = None

class SelfExclusionResponse(BaseModel):
    user_id: Optional[str] = None
    checked: bool = True
    excluded: bool = False
    self_excluded: bool = False
    eligible: bool = True
    source: str = "DEMO_REGISTER"
    status: str = "ACTIVE_NOT_EXCLUDED"
    timestamp: datetime = Field(default_factory=utc_now)

class KYCDemoRequest(BaseModel):
    user_id: Optional[str] = None
    anonymous_user_id: Optional[str] = None
    document_type: str = "National ID" # National ID, Passport, Driving Licence

class KYCDemoResponse(BaseModel):
    user_id: Optional[str] = None
    kyc_verified: bool = True
    document_type: str = "National ID"
    status: str = "VERIFIED"
    demo: bool = True
    notice: str = "Demo verification — no real identity data processed."
    timestamp: datetime = Field(default_factory=utc_now)

class BettingEligibilityRequest(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    anonymous_user_id: Optional[str] = None

class BettingEligibilityResponse(BaseModel):
    user_id: Optional[str] = None
    eligible: bool = True
    age_verified: bool = True
    kyc_verified: bool = True
    self_excluded: bool = False
    reason: str = "ELIGIBLE"
    status: str = "ELIGIBLE" # PENDING_VERIFICATION, AGE_RESTRICTED, KYC_REQUIRED, SELF_EXCLUDED, ELIGIBLE, VERIFICATION_FAILED
    demo: bool = True
    timestamp: datetime = Field(default_factory=utc_now)

class ComplianceStatusResponse(BaseModel):
    user_id: str
    anonymous_id: Optional[str] = None
    betting_eligible: bool = True
    age_verified: bool = True
    kyc_verified: bool = True
    self_excluded: bool = False
    status: str = "ELIGIBLE"
    verification_method: str = "DEMO_ATTRIBUTE"

# ==================================================
# User Schemas
# ==================================================
class UserCreate(BaseModel):
    id: Optional[str] = None
    anonymous_id: Optional[str] = None
    display_name: Optional[str] = "Sports Enthusiast"
    email: Optional[str] = "fan@pulsync.ai"
    segment: Optional[str] = "Casual Explorer"
    age: Optional[int] = 21

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    anonymous_id: Optional[str] = None
    display_name: Optional[str] = "Sports Enthusiast"
    email: Optional[str] = "fan@pulsync.ai"
    segment: str
    age_verified: bool
    kyc_verified: bool = False
    self_excluded: bool
    eligibility_status: str = "PENDING_VERIFICATION"
    created_at: datetime
    sessions_count: Optional[int] = 0
    preferred_sport: Optional[str] = None
    frequently_viewed_content: Optional[List[str]] = []

# ==================================================
# Session Schemas
# ==================================================
class SessionCreate(BaseModel):
    id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    anonymous_user_id: Optional[str] = None
    is_synthetic: bool = False

class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    intent: str
    intent_confidence: float
    abandonment_probability: float
    friction_score: float
    friction_level: str
    session_quality_score: float
    status: str
    is_synthetic: bool

# ==================================================
# Event Schemas
# ==================================================
class EventCreate(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    event_type: str # page_view, match_view, statistics_view, h2h_view, team_form_view, comparison, search, back, save, content_click, navigation, session_start, session_end
    page: Optional[str] = None
    action: Optional[str] = None
    sport: Optional[str] = None
    match_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: str
    user_id: Optional[str] = None
    timestamp: datetime
    event_type: str
    page: Optional[str] = None
    action: Optional[str] = None
    sport: Optional[str] = None
    match_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

# ==================================================
# Intelligence & Contextual Guidance Schemas
# ==================================================
class GuidanceResponse(BaseModel):
    should_intervene: bool
    guidance_message: Optional[str] = None
    recommended_action: Optional[str] = None
    content_id: Optional[str] = None

class SessionIntelligenceResponse(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    intent: str
    intent_confidence: float
    intent_reason: str
    # Machine 3: transaction intent, information interest, engagement
    transaction_intent: Optional[str] = "LOW"
    information_interest: Optional[str] = "HIGH"
    engagement_state: Optional[str] = "NORMAL"
    recommendation_mode: Optional[str] = "NORMAL"
    engagement_message: Optional[str] = None
    explicit_exit: Optional[bool] = False
    # Behavioural scores
    abandonment_probability: float
    abandonment_risk_level: str
    abandonment_reason: str
    friction_score: float
    friction_level: str
    friction_reason: str
    session_quality: Optional[float] = None
    session_quality_score: float
    session_quality_explanation: str
    
    # ML Outputs
    continuation_probability: Optional[float] = None
    intent_probabilities: Optional[Dict[str, float]] = None
    model_source: Optional[str] = None
    model_versions: Optional[Dict[str, str]] = None
    
    # Detailed scoring breakdown and action metrics (Machine 3)
    score_factors: Optional[List[Dict[str, Any]]] = []
    actions_count: Optional[int] = 0
    time_to_first_action_seconds: Optional[float] = None
    last_action: Optional[str] = None
    final_step_conversion: Optional[bool] = False
    # Top-level compliance status
    betting_eligible: Optional[bool] = False
    age_verified: Optional[bool] = False
    kyc_verified: Optional[bool] = False
    self_excluded: Optional[bool] = False
    updated_at: Optional[str] = None
    # Guidance & recommendations
    guidance: GuidanceResponse
    top_recommendation: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Dict[str, Any]]] = []
    intelligence: Optional[Dict[str, Any]] = None
    # Compliance (from Machine 2 — read-only here)
    compliance: Optional[Dict[str, Any]] = None

class SessionScoreResponse(BaseModel):
    session_id: str
    session_quality_score: float
    session_quality: float
    explanation: str
    factors: List[Dict[str, Any]] = []
    score_factors: List[Dict[str, Any]] = []
    trend: str = "STABLE" # IMPROVING, STABLE, DECLINING
    delta: float = 0.0
    abandonment_probability: float = 0.0
    friction_score: float = 0.0

# ==================================================
# Recommendation Schemas
# ==================================================
class RecommendationItem(BaseModel):
    content_id: str
    content_type: str
    title: str
    score: float
    rank: int
    reason: str
    context: Optional[str] = None

class RecommendationListResponse(BaseModel):
    session_id: str
    intent: str
    friction_level: str
    recommendations: List[RecommendationItem]

class RecommendationFeedbackRequest(BaseModel):
    recommendation_id: Optional[Any] = None
    content_id: Optional[str] = None
    feedback_type: Optional[str] = None
    action: Optional[str] = None

# ==================================================
# Outcome Schemas
# ==================================================
class OutcomeCreate(BaseModel):
    session_id: str
    recommendation_id: Optional[int] = None
    decision: str # VIEW_CONTENT, SAVE_CONTENT, DISMISS, CONTINUE_BROWSING, ABANDON
    content_viewed: bool = False
    session_continued: bool = True

class OutcomeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: str
    decision: str
    content_viewed: bool
    session_continued: bool
    created_at: datetime

# ==================================================
# Match Schemas
# ==================================================
class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    sport: str
    team_home: str
    team_away: str
    start_time: datetime
    status: str

# ==================================================
# Dashboard Schemas
# ==================================================
class DashboardMetricsResponse(BaseModel):
    total_sessions: int
    live_sessions: int
    reconstructed_sessions: int
    actions_per_session: float
    sessions_per_user: float
    time_to_first_action_sec: float
    early_abandonment_rate: float
    average_session_quality: float
    recommendation_ctr: float
    recommendation_continuation_rate: float

class DashboardSegmentsResponse(BaseModel):
    segments: List[Dict[str, Any]]

class DashboardRecommendationsResponse(BaseModel):
    performance: List[Dict[str, Any]]

class DashboardQualityResponse(BaseModel):
    quality_by_segment: List[Dict[str, Any]]
    abandonment_by_segment: List[Dict[str, Any]]

class DashboardImpactResponse(BaseModel):
    status: str = "Prototype Impact Simulation"
    methodology: str = "Behavioral proxy replay comparing high-friction sessions with vs without contextual guidance intervention"
    metric_improvements: Dict[str, Any]

# ==================================================
# Demo Mode Schemas
# ==================================================
class DemoStartRequest(BaseModel):
    user_id: Optional[str] = "demo_user_001"
    sport: Optional[str] = "Football"
    match_id: Optional[str] = "match_rma_bar"

class DemoStartResponse(BaseModel):
    session_id: str
    user_id: str
    events_triggered: List[Dict[str, Any]]
    final_intelligence: SessionIntelligenceResponse
    message: str = "Demo session successfully executed through full behavioral cycle."

# ==================================================
# Impact & ROI Intelligence Schemas (Machine 4)
# ==================================================
class ROISimulationRequest(BaseModel):
    scenario: Optional[str] = "base"
    scenario_realization_pct: Optional[float] = 50.0
    inference_cost_per_call: Optional[float] = 0.005
    api_cost_per_call: Optional[float] = 0.002
    hosting_cost_monthly: Optional[float] = 500.0
    storage_cost_monthly: Optional[float] = 200.0
    engineering_cost: Optional[float] = 25000.0
    monthly_sessions: Optional[int] = 100000

