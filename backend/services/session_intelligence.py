from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import (
    Session as DBSession, Event, UserProfile, Recommendation, SessionPrediction
)
from backend.services.user_profiling import UserProfilingService
from backend.services.intent_detector import IntentDetector
from backend.services.friction_engine import FrictionEngine
from backend.services.abandonment_engine import AbandonmentEngine
from backend.services.recommendation_engine import RecommendationEngine
from backend.services.contextual_guidance import ContextualGuidanceService
from backend.services.session_quality import SessionQualityEngine


def _check_explicit_exit(events) -> bool:
    for e in events:
        combined = "{} {} {}".format(e.event_type or '', e.page or '', e.action or '').lower()
        if "explicit_exit" in combined:
            return True
    return False


def _get_compliance(user) -> Dict[str, Any]:
    if not user:
        return {"betting_eligible": False, "self_excluded": False, "age_verified": False, "kyc_verified": False}
    return {
        "betting_eligible": getattr(user, "eligibility_status", "PENDING_VERIFICATION") == "ELIGIBLE",
        "self_excluded": getattr(user, "self_excluded", False),
        "age_verified": getattr(user, "age_verified", False),
        "kyc_verified": getattr(user, "kyc_verified", False),
    }


class SessionIntelligenceService:
    """Machine 3 — PULSYNC Session Intelligence Pipeline.
    PULSYNC does NOT simply optimize for another bet.
    It determines what the user is trying to accomplish in the current session.
    """

    @classmethod
    def process_event(cls, db: Session, session_id: str, event: Event) -> Dict[str, Any]:
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if not session:
            session = DBSession(
                id=session_id, user_id=event.user_id,
                started_at=event.timestamp or datetime.utcnow(),
                is_synthetic=False, status="ACTIVE"
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        all_events = db.query(Event).filter(Event.session_id == session_id).order_by(Event.timestamp.asc()).all()
        session.total_events = len(all_events)
        session.total_actions = sum(1 for e in all_events if e.action)
        session.unique_sports = len(set(e.sport for e in all_events if e.sport))

        if all_events:
            session.duration_seconds = max(0.0, (all_events[-1].timestamp - all_events[0].timestamp).total_seconds())
            session.ended_at = all_events[-1].timestamp

        user = UserProfilingService.update_profile(db, session.user_id) if session.user_id else None
        compliance = _get_compliance(user)

        intent, intent_conf, intent_reason = IntentDetector.detect_intent(all_events)
        session.intent = intent
        session.intent_confidence = intent_conf

        friction_score, friction_level, friction_reason = FrictionEngine.calculate_friction(all_events)
        session.friction_score = friction_score
        session.friction_level = friction_level

        abandonment_prob, risk_level, abandonment_reason, abandonment_model_source = AbandonmentEngine.calculate_risk_detailed(
            all_events, session.duration_seconds, friction_score)
        session.abandonment_probability = abandonment_prob

        quality_score, quality_reason, score_factors = SessionQualityEngine.evaluate_quality_detailed(
            all_events, friction_score, abandonment_prob
        )
        session.session_quality_score = quality_score
        
        # Calculate Continuation explicitly via registry
        from backend.ml.model_registry import ModelRegistry
        registry = ModelRegistry()
        ml_continuation_prob = round(1.0 - abandonment_prob, 2)
        intent_probs = {}
        if registry.is_loaded() and all_events:
            try:
                features = {
                    "unique_sports_so_far": len(set(e.sport for e in all_events if e.sport)),
                    "unique_matches_so_far": len(set(e.match_id for e in all_events if e.match_id)),
                    "is_prematch": 1 if all_events[-1].event_type == "PREMATCH" else 0,
                    "is_live": 1 if all_events[-1].event_type == "LIVE" else 0,
                    "is_lottery": 1 if all_events[-1].event_type == "WORLD_LOTTERY" else 0
                }
                _, prob_cont, _, _, probs_dict = registry.predict(features)
                ml_continuation_prob = round(prob_cont, 2)
                intent_probs = probs_dict
            except:
                pass

        # Action and conversion metrics
        action_events = [
            e for e in all_events
            if e.action and e.action.lower() not in ("page_view", "browse", "session_start")
        ]
        actions_count = len(action_events)
        time_to_first_action = None
        if action_events and all_events and all_events[0].timestamp and action_events[0].timestamp:
            delta = (action_events[0].timestamp - all_events[0].timestamp).total_seconds()
            time_to_first_action = round(max(0.0, delta), 2)
            
        last_action = action_events[-1].action if action_events else (all_events[-1].action if all_events and all_events[-1].action else None)
        final_step_conversion = any(
            (e.action and e.action.lower() in ("bet_confirmed", "bet_placed", "action_completed", "saved_to_betslip"))
            for e in all_events
        )

        transaction_intent = IntentDetector.calculate_transaction_intent(all_events)
        explicit_exit = _check_explicit_exit(all_events)
        information_interest = IntentDetector.calculate_information_interest(all_events, abandonment_prob)
        engagement_state, recommendation_mode = IntentDetector.evaluate_engagement_state(
            transaction_intent, information_interest, explicit_exit)

        if compliance["self_excluded"] or not compliance["betting_eligible"]:
            if engagement_state == "NORMAL" and transaction_intent in ("HIGH", "MEDIUM"):
                engagement_state = "VALUE_SEEKING"
                recommendation_mode = "VALUE_SEEKING"

        hist_profile = UserProfilingService.get_historical_player_profile(db, session.user_id) if session.user_id else None

        previous_recs = db.query(Recommendation).filter(Recommendation.session_id == session_id).all()
        recommendations = RecommendationEngine.generate_recommendations(
            session=session, user=user, events=all_events, current_intent=intent,
            friction_level=friction_level, abandonment_probability=abandonment_prob,
            previous_recommendations=previous_recs, transaction_intent=transaction_intent,
            information_interest=information_interest, engagement_state=engagement_state,
            recommendation_mode=recommendation_mode, compliance=compliance,
        )

        top_rec = recommendations[0] if recommendations else None
        if top_rec:
            existing = db.query(Recommendation).filter(
                Recommendation.session_id == session_id,
                Recommendation.content_id == top_rec["content_id"]
            ).first()
            if not existing:
                db.add(Recommendation(
                    session_id=session_id, content_id=top_rec["content_id"],
                    content_type=top_rec["content_type"], title=top_rec["title"],
                    reason=top_rec["reason"], rank=top_rec["rank"],
                    score=top_rec["score"], shown_at=datetime.utcnow()
                ))

        guidance = ContextualGuidanceService.evaluate_intervention(
            intent=intent, friction_level=friction_level,
            abandonment_probability=abandonment_prob, top_recommendation=top_rec)

        db.add(SessionPrediction(
            session_id=session_id, intent=intent, intent_confidence=intent_conf,
            abandonment_probability=abandonment_prob, friction_score=friction_score,
            quality_score=quality_score, created_at=datetime.utcnow()
        ))
        db.commit()
        db.refresh(session)

        return cls._build_response(
            session_id=session_id, session=session,
            intent=intent, intent_conf=intent_conf, intent_reason=intent_reason,
            transaction_intent=transaction_intent, information_interest=information_interest,
            engagement_state=engagement_state, recommendation_mode=recommendation_mode,
            explicit_exit=explicit_exit, abandonment_prob=abandonment_prob,
            risk_level=risk_level, abandonment_reason=abandonment_reason,
            friction_score=friction_score, friction_level=friction_level, friction_reason=friction_reason,
            quality_score=quality_score, quality_reason=quality_reason, score_factors=score_factors,
            actions_count=actions_count, time_to_first_action=time_to_first_action,
            last_action=last_action, final_step_conversion=final_step_conversion,
            guidance=guidance, top_rec=top_rec, recommendations=recommendations,
            hist_profile=hist_profile, compliance=compliance,
        )

    @classmethod
    def get_intelligence(cls, db: Session, session_id: str) -> Dict[str, Any]:
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if not session:
            return None

        all_events = db.query(Event).filter(Event.session_id == session_id).order_by(Event.timestamp.asc()).all()
        user = db.query(UserProfile).filter(UserProfile.id == session.user_id).first() if session.user_id else None
        compliance = _get_compliance(user)

        intent, intent_conf, intent_reason = IntentDetector.detect_intent(all_events)
        friction_score, friction_level, friction_reason = FrictionEngine.calculate_friction(all_events)
        abandonment_prob, risk_level, abandonment_reason, abandonment_model_source = AbandonmentEngine.calculate_risk_detailed(
            all_events, session.duration_seconds, friction_score)
        quality_score, quality_reason, score_factors = SessionQualityEngine.evaluate_quality_detailed(
            all_events, friction_score, abandonment_prob
        )

        action_events = [
            e for e in all_events
            if e.action and e.action.lower() not in ("page_view", "browse", "session_start")
        ]
        actions_count = len(action_events)
        time_to_first_action = None
        if action_events and all_events and all_events[0].timestamp and action_events[0].timestamp:
            delta = (action_events[0].timestamp - all_events[0].timestamp).total_seconds()
            time_to_first_action = round(max(0.0, delta), 2)
            
        last_action = action_events[-1].action if action_events else (all_events[-1].action if all_events and all_events[-1].action else None)
        final_step_conversion = any(
            (e.action and e.action.lower() in ("bet_confirmed", "bet_placed", "action_completed", "saved_to_betslip"))
            for e in all_events
        )

        transaction_intent = IntentDetector.calculate_transaction_intent(all_events)
        explicit_exit = _check_explicit_exit(all_events)
        information_interest = IntentDetector.calculate_information_interest(all_events, abandonment_prob)
        engagement_state, recommendation_mode = IntentDetector.evaluate_engagement_state(
            transaction_intent, information_interest, explicit_exit)

        if compliance["self_excluded"] or not compliance["betting_eligible"]:
            if engagement_state == "NORMAL" and transaction_intent in ("HIGH", "MEDIUM"):
                engagement_state = "VALUE_SEEKING"
                recommendation_mode = "VALUE_SEEKING"

        hist_profile = UserProfilingService.get_historical_player_profile(db, session.user_id) if session.user_id else None

        previous_recs = db.query(Recommendation).filter(Recommendation.session_id == session_id).all()
        recommendations = RecommendationEngine.generate_recommendations(
            session=session, user=user, events=all_events, current_intent=intent,
            friction_level=friction_level, abandonment_probability=abandonment_prob,
            previous_recommendations=previous_recs, transaction_intent=transaction_intent,
            information_interest=information_interest, engagement_state=engagement_state,
            recommendation_mode=recommendation_mode, compliance=compliance,
        )
        top_rec = recommendations[0] if recommendations else None

        guidance = ContextualGuidanceService.evaluate_intervention(
            intent=intent, friction_level=friction_level,
            abandonment_probability=abandonment_prob, top_recommendation=top_rec)

        return cls._build_response(
            session_id=session_id, session=session,
            intent=intent, intent_conf=intent_conf, intent_reason=intent_reason,
            transaction_intent=transaction_intent, information_interest=information_interest,
            engagement_state=engagement_state, recommendation_mode=recommendation_mode,
            explicit_exit=explicit_exit, abandonment_prob=abandonment_prob,
            risk_level=risk_level, abandonment_reason=abandonment_reason,
            friction_score=friction_score, friction_level=friction_level, friction_reason=friction_reason,
            quality_score=quality_score, quality_reason=quality_reason, score_factors=score_factors,
            actions_count=actions_count, time_to_first_action=time_to_first_action,
            last_action=last_action, final_step_conversion=final_step_conversion,
            guidance=guidance, top_rec=top_rec, recommendations=recommendations,
            hist_profile=hist_profile, compliance=compliance,
        )

    @classmethod
    def _build_response(cls, *, session_id, session, intent, intent_conf, intent_reason,
                        transaction_intent, information_interest, engagement_state, recommendation_mode,
                        explicit_exit, abandonment_prob, risk_level, abandonment_reason,
                        friction_score, friction_level, friction_reason, quality_score, quality_reason,
                        score_factors=None, actions_count=0, time_to_first_action=None,
                        last_action=None, final_step_conversion=False,
                        guidance, top_rec, recommendations, hist_profile, compliance,
                        ml_continuation_prob=None, intent_probs=None, abandonment_model_source=None) -> Dict[str, Any]:
        engagement_message = None
        if engagement_state == "VALUE_SEEKING":
            engagement_message = "No problem. Still interested in the match?"
        elif engagement_state == "NORMAL" and transaction_intent in ("HIGH", "MEDIUM"):
            engagement_message = "You're exploring this match. Here's some useful context."
        elif engagement_state == "LOW_PRESSURE":
            engagement_message = "Take your time. Here's more information about this fixture."

        from backend.ml.model_registry import ModelRegistry
        registry = ModelRegistry()
        
        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "intent": intent,
            "intent_confidence": round(intent_conf, 2),
            "intent_reason": intent_reason,
            "intent_probabilities": intent_probs or {},
            "transaction_intent": transaction_intent,
            "information_interest": information_interest,
            "engagement_state": engagement_state,
            "recommendation_mode": recommendation_mode,
            "friction_score": friction_score,
            "friction_level": friction_level,
            "friction_reason": friction_reason,
            "abandonment_probability": abandonment_prob,
            "abandonment_risk": risk_level,
            "abandonment_reason": abandonment_reason,
            "continuation_probability": ml_continuation_prob if ml_continuation_prob is not None else round(1.0 - abandonment_prob, 2),
            "session_quality_score": quality_score,
            "session_quality_reason": quality_reason,
            "model_source": abandonment_model_source or "heuristic_fallback",
            "model_versions": {
                "intent": registry.get_version(),
                "abandonment": registry.get_version(),
                "continuation": registry.get_version()
            } if registry.is_loaded() else None,
            "explicit_exit": explicit_exit,
            "engagement_message": engagement_message,
            "abandonment_risk_level": risk_level,
            "session_quality": round(quality_score, 1),
            "session_quality_explanation": quality_reason,
            "score_factors": score_factors or [],
            "actions_count": actions_count,
            "time_to_first_action_seconds": time_to_first_action,
            "last_action": last_action,
            "final_step_conversion": final_step_conversion,
            "betting_eligible": compliance.get("betting_eligible", False) if compliance else False,
            "age_verified": compliance.get("age_verified", False) if compliance else False,
            "kyc_verified": compliance.get("kyc_verified", False) if compliance else False,
            "self_excluded": compliance.get("self_excluded", False) if compliance else False,
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "top_recommendation": top_rec,
            "recommendations": recommendations[:5],
            "guidance": guidance,
            "historical_profile": hist_profile,
            "compliance": compliance,
        }
