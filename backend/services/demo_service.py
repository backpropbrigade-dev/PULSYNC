import uuid
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.models import (
    Session as DBSession, Event, UserProfile, Match, Outcome
)
from backend.services.session_intelligence import SessionIntelligenceService

class DemoSimulationService:
    """
    Simulates a deterministic, high-friction interactive user session for live presentations.
    Demonstrates the full reactive lifecycle of PULSYNC:
    Exploration -> Hesitation & Navigation Friction -> Elevated Abandonment Risk -> Contextual Guidance -> Outcome.
    """
    
    @classmethod
    def run_demo_simulation(
        cls, 
        db: Session, 
        user_id: str = "demo_fan_01",
        match_id: str = "match_el_clasico"
    ) -> Dict[str, Any]:
        
        session_id = f"demo_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        
        # 1. Ensure Demo Match Exists
        demo_match = db.query(Match).filter(Match.id == match_id).first()
        if not demo_match:
            demo_match = Match(
                id=match_id,
                sport="Football",
                team_home="Real Madrid",
                team_away="FC Barcelona",
                start_time=now + timedelta(hours=2),
                status="UPCOMING"
            )
            db.add(demo_match)
            db.commit()
            
        # 2. Ensure Demo User Exists
        user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not user:
            user = UserProfile(
                id=user_id,
                anonymous_id=f"anon_{user_id}",
                segment="Football Explorer",
                age_verified=True,
                self_excluded=False
            )
            db.add(user)
            db.commit()
            
        # 3. Create Demo Session
        demo_session = DBSession(
            id=session_id,
            user_id=user_id,
            started_at=now,
            is_synthetic=False,
            status="ACTIVE"
        )
        db.add(demo_session)
        db.commit()
        
        # 4. Synthesize Deterministic Event Sequence
        # Sequence: Match View -> Statistics -> H2H -> Back -> Statistics (Loop)
        events_timeline = [
            {
                "event_type": "session_start",
                "page": "home",
                "action": "open_app",
                "offset_sec": 0
            },
            {
                "event_type": "match_view",
                "page": "match_detail",
                "action": "view_match_card",
                "offset_sec": 4
            },
            {
                "event_type": "statistics_view",
                "page": "statistics",
                "action": "expand_possession_stats",
                "offset_sec": 12
            },
            {
                "event_type": "h2h_view",
                "page": "h2h",
                "action": "view_last_encounters",
                "offset_sec": 22
            },
            {
                "event_type": "back",
                "page": "match_detail",
                "action": "back_to_overview",
                "offset_sec": 28
            },
            {
                "event_type": "statistics_view",
                "page": "statistics",
                "action": "reopen_statistics", # Oscillation loop: statistics -> h2h -> match_detail -> statistics!
                "offset_sec": 34
            },
            {
                "event_type": "back",
                "page": "match_detail",
                "action": "back_again", # Second rapid back navigation!
                "offset_sec": 40
            }
        ]
        
        created_events = []
        last_intel = None
        
        for ev_def in events_timeline:
            ev = Event(
                session_id=session_id,
                user_id=user_id,
                timestamp=now + timedelta(seconds=ev_def["offset_sec"]),
                event_type=ev_def["event_type"],
                page=ev_def["page"],
                action=ev_def["action"],
                sport="Football",
                match_id=match_id
            )
            db.add(ev)
            db.commit()
            db.refresh(ev)
            created_events.append({
                "timestamp": ev.timestamp.isoformat(),
                "event_type": ev.event_type,
                "page": ev.page,
                "action": ev.action
            })
            
            # Update Intelligence
            last_intel = SessionIntelligenceService.process_event(db, session_id, ev)
            
        # Record an initial positive outcome (e.g. user saw the intervention)
        outcome = Outcome(
            session_id=session_id,
            recommendation_id=None,
            decision="VIEW_CONTENT",
            content_viewed=True,
            session_continued=True,
            created_at=now + timedelta(seconds=45)
        )
        db.add(outcome)
        db.commit()
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "events_triggered": created_events,
            "final_intelligence": last_intel,
            "provenance": "Demo Simulation (Deterministic behavioral simulation for MVP presentation)"
        }
