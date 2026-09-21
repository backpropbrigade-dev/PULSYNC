import datetime
import json
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    anonymous_id = Column(String, unique=True, index=True, nullable=True)
    display_name = Column(String, nullable=True, default="Sports Enthusiast")
    email = Column(String, nullable=True, default="fan@pulsync.ai")
    segment = Column(String, default="Casual Explorer") # Football Explorer, Multi-Sport Explorer, etc.
    age_verified = Column(Boolean, default=False)
    kyc_verified = Column(Boolean, default=False)
    kyc_document_type = Column(String, nullable=True) # National ID, Passport, Driving Licence
    self_excluded = Column(Boolean, default=False)
    age_verified_at = Column(DateTime, nullable=True)
    verification_method = Column(String, default="DEMO_ATTRIBUTE")
    eligibility_status = Column(String, default="PENDING_VERIFICATION") # PENDING_VERIFICATION, AGE_RESTRICTED, KYC_REQUIRED, SELF_EXCLUDED, ELIGIBLE, VERIFICATION_FAILED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=True)
    
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    intent = Column(String, default="EXPLORE") # EXPLORE, COMPARE, UNDERSTAND, REVIEW, ACT
    intent_confidence = Column(Float, default=0.5)
    abandonment_probability = Column(Float, default=0.0) # 0.0 - 1.0
    friction_score = Column(Float, default=0.0) # 0.0 - 100.0
    friction_level = Column(String, default="LOW") # LOW, MEDIUM, HIGH
    session_quality_score = Column(Float, default=100.0) # 0.0 - 100.0
    status = Column(String, default="ACTIVE") # ACTIVE, ENDED, ABANDONED
    
    is_synthetic = Column(Boolean, default=False)
    duration_seconds = Column(Float, default=0.0)
    total_events = Column(Integer, default=0)
    total_actions = Column(Integer, default=0)
    unique_sports = Column(Integer, default=0)
    
    # Relationships
    user = relationship("UserProfile", back_populates="sessions")
    events = relationship("Event", back_populates="session", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="session", cascade="all, delete-orphan")
    outcomes = relationship("Outcome", back_populates="session", cascade="all, delete-orphan")
    predictions = relationship("SessionPrediction", back_populates="session", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    event_type = Column(String, index=True) # page_view, match_view, statistics_view, h2h_view, team_form_view, comparison, search, back, save, content_click, navigation, session_start, session_end
    page = Column(String, nullable=True) # e.g., "match_detail", "statistics", "comparison", "home"
    action = Column(String, nullable=True) # e.g., "click_h2h", "open_stats", "filter_odds"
    sport = Column(String, nullable=True)
    match_id = Column(String, nullable=True)
    metadata_json = Column(Text, default="{}") # Flexible JSON metadata
    
    session = relationship("Session", back_populates="events")

    def get_metadata(self):
        try:
            return json.loads(self.metadata_json) if self.metadata_json else {}
        except Exception:
            return {}

    def set_metadata(self, value):
        self.metadata_json = json.dumps(value) if value is not None else "{}"


class Match(Base):
    __tablename__ = "matches"
    
    id = Column(String, primary_key=True, index=True)
    sport = Column(String, index=True)
    team_home = Column(String)
    team_away = Column(String)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="UPCOMING") # UPCOMING, LIVE, FINISHED


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), index=True)
    content_id = Column(String, index=True)
    content_type = Column(String) # Match Insights, Team Comparison, Team Form, Head-to-Head, Key Statistics, etc.
    title = Column(String, nullable=True)
    reason = Column(String)
    rank = Column(Integer, default=1)
    score = Column(Float, default=0.0) # 0.0 - 100.0
    shown_at = Column(DateTime, default=datetime.datetime.utcnow)
    clicked = Column(Boolean, default=False)
    dismissed = Column(Boolean, default=False)
    
    session = relationship("Session", back_populates="recommendations")


class Outcome(Base):
    __tablename__ = "outcomes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=True)
    decision = Column(String) # VIEW_CONTENT, SAVE_CONTENT, DISMISS, CONTINUE_BROWSING, ABANDON
    content_viewed = Column(Boolean, default=False)
    session_continued = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("Session", back_populates="outcomes")


class SessionPrediction(Base):
    __tablename__ = "session_predictions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), index=True)
    intent = Column(String)
    intent_confidence = Column(Float)
    abandonment_probability = Column(Float)
    friction_score = Column(Float)
    quality_score = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("Session", back_populates="predictions")


class PlayerProfile(Base):
    __tablename__ = "player_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    anonymous_user_id = Column(String, unique=True, index=True)
    preferred_sport = Column(String, default="Football")
    activity_level = Column(String, default="MEDIUM") # HIGH, MEDIUM, LOW
    total_activity = Column(Integer, default=0)
    sport_distribution_json = Column(Text, default="{}")
    preferred_product = Column(String, default="Sportsbook")
    historical_activity_score = Column(Float, default=50.0)
    profile_source = Column(String, default="FEG historical behavioral profile")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def get_sport_distribution(self):
        try:
            return json.loads(self.sport_distribution_json) if self.sport_distribution_json else {}
        except Exception:
            return {}

    def set_sport_distribution(self, value):
        self.sport_distribution_json = json.dumps(value) if value is not None else "{}"

# Indexes
Index("idx_events_session_time", Event.session_id, Event.timestamp)
Index("idx_recommendations_session_rank", Recommendation.session_id, Recommendation.rank)
Index("idx_outcomes_session_created", Outcome.session_id, Outcome.created_at)
Index("idx_player_profiles_anon_id", PlayerProfile.anonymous_user_id)
Index("idx_events_sport_match", Event.sport, Event.match_id)
