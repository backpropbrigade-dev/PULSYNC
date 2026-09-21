from typing import List, Tuple
from datetime import datetime
from backend.models import Event
from backend.ml.model_registry import ModelRegistry

class AbandonmentEngine:
    """
    Computes session abandonment risk. Uses ML model backed by heuristic safety fallback.
    """
    
    @classmethod
    def calculate_risk(
        cls, 
        events: List[Event], 
        session_duration_sec: float,
        friction_score: float
    ) -> Tuple[float, str, str]:
        probability, risk_level, reason, _ = cls.calculate_risk_detailed(
            events, session_duration_sec, friction_score
        )
        return probability, risk_level, reason

    @classmethod
    def calculate_risk_detailed(
        cls,
        events: List[Event],
        session_duration_sec: float,
        friction_score: float
    ) -> Tuple[float, str, str, str]:
        """
        Returns: (probability, risk_level, reason, model_source).
        """
        if not events:
            return 0.10, "LOW", "Session just initiated; baseline low abandonment risk.", "heuristic_fallback"
            
        registry = ModelRegistry()
        ml_prob = None
        if registry.is_loaded():
            try:
                unique_sports = len(set(e.sport for e in events if e.sport))
                unique_matches = len(set(e.match_id for e in events if e.match_id))
                last_event = events[-1]
                features = {
                    "unique_sports_so_far": unique_sports,
                    "unique_matches_so_far": unique_matches,
                    "is_prematch": 1 if last_event.event_type == "PREMATCH" else 0,
                    "is_live": 1 if last_event.event_type == "LIVE" else 0,
                    "is_lottery": 1 if last_event.event_type == "WORLD_LOTTERY" else 0
                }
                
                prob_abandonment, _, _, _, _ = registry.predict(features)
                ml_prob = round(prob_abandonment, 2)
            except Exception as e:
                print(f"ML abandonment failed: {e}")

            
        now = datetime.utcnow()
        last_event_time = events[-1].timestamp or now
        inactivity_sec = (now - last_event_time).total_seconds() if now > last_event_time else 0
        
        event_count = len(events)
        actions_count = sum(1 for e in events if e.action)
        back_events = sum(1 for e in events if e.event_type == "back" or e.action == "back")
        
        score = 0.10 # baseline
        reasons = []
        
        # Inactivity component
        if inactivity_sec > 180: # > 3 minutes idle
            score += 0.40
            reasons.append(f"Extended user idle period ({int(inactivity_sec)}s)")
        elif inactivity_sec > 60: # > 1 minute idle
            score += 0.20
            reasons.append(f"Moderate inactivity ({int(inactivity_sec)}s)")
            
        # Friction penalty
        if friction_score >= 70:
            score += 0.35
            reasons.append("High navigation friction and page looping detected")
        elif friction_score >= 40:
            score += 0.20
            reasons.append("Moderate navigation hesitation observed")
            
        # Rapid back events (frustration signal)
        if back_events >= 2:
            score += 0.20
            reasons.append(f"Multiple rapid back navigations ({back_events})")
            
        # Single-event / low-engagement early sessions
        if event_count <= 2 and session_duration_sec > 45:
            score += 0.25
            reasons.append("Slow pacing without meaningful content interaction")
            
        # Mitigating factor: high action engagement
        if actions_count >= 3:
            score = max(0.05, score - 0.20)
            reasons.append("Active interaction with content cards mitigates abandonment risk")
            
        heuristic_probability = round(min(0.95, max(0.05, score)), 2)
        probability = heuristic_probability
        model_source = "heuristic_fallback"
        reason_text = "Behavioral proxy: " + ("; ".join(reasons) if reasons else "Normal session pacing observed.")
        
        if ml_prob is not None:
            # Preserve deterministic behavioral safety signals when the model
            # underestimates an obviously stalled, high-friction session.
            probability = max(ml_prob, heuristic_probability)
            model_source = "ml"
            reason_text = (
                f"ML Prediction ({registry.get_version()}): Estimated abandonment risk "
                f"based on {len(events)} events; behavioral proxy safety signals retained."
            )
        
        if probability < 0.30:
            risk_level = "LOW"
        elif probability < 0.70:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
            
        return probability, risk_level, reason_text, model_source
