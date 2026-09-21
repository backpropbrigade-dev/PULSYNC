from typing import List, Tuple, Dict, Any
from backend.models import Event

class SessionQualityEngine:
    """
    Computes an authoritative, explainable session quality score (0 - 100).
    Measures meaningful fan comprehension, engagement, and navigational ease.
    
    Formula:
        session_quality =
            base_score (50.0)
            + positive_engagement (up to +20)
            + information_value (up to +20)
            + action_progression (up to +15)
            + recommendation_engagement (up to +15)
            - friction_penalty (down to -25)
            - abandonment_penalty (down to -25)
            - repetition_penalty (down to -10)
            
    Clamped strictly: 0 <= session_quality <= 100.
    """
    
    @classmethod
    def evaluate_quality(
        cls,
        events: List[Event],
        friction_score: float,
        abandonment_prob: float
    ) -> Tuple[float, str]:
        score, explanation, _ = cls.evaluate_quality_detailed(events, friction_score, abandonment_prob)
        return score, explanation

    @classmethod
    def evaluate_quality_detailed(
        cls,
        events: List[Event],
        friction_score: float,
        abandonment_prob: float
    ) -> Tuple[float, str, List[Dict[str, Any]]]:
        """
        Returns: (quality_score: 0-100, explanation_str, score_factors: List[Dict])
        """
        if not events:
            return 75.0, "Session started; initial quality baseline established.", [
                {"factor": "baseline", "impact": 75, "reason": "Initial session initiation baseline established."}
            ]
            
        base_score = 50.0
        factors: List[Dict[str, Any]] = [
            {"factor": "session_baseline", "impact": 50, "reason": "Baseline platform interaction."}
        ]
        explanations = []
        
        from backend.ml.model_registry import ModelRegistry
        registry = ModelRegistry()
        ml_continuation_prob = None
        
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
                _, prob_continuation, _, _, _ = registry.predict(features)
                ml_continuation_prob = prob_continuation
                
                # ML Contribution: up to +15 for high continuation likelihood
                ml_impact = (ml_continuation_prob - 0.5) * 30 # Range -15 to +15
                base_score += ml_impact
                factors.append({"factor": "ml_continuation", "impact": round(ml_impact, 1), "reason": f"ML continuation probability: {ml_continuation_prob:.0%}"})
                explanations.append(f"ML Continuation likelihood {ml_continuation_prob:.0%}")
            except Exception as e:
                print(f"ML continuation failed: {e}")
        
        all_actions = [e.action.lower() if e.action else "" for e in events]
        all_types = [e.event_type.lower() if e.event_type else "" for e in events]
        all_pages = [e.page.lower() if e.page else "" for e in events]
        combined = " ".join(all_actions + all_types + all_pages)
        
        # 1. Positive engagement
        meaningful_actions = sum(1 for a in all_actions if a and a not in ("page_view", "browse", "session_start"))
        if meaningful_actions >= 4:
            base_score += 20.0
            factors.append({"factor": "positive_engagement", "impact": 20, "reason": f"Sustained interaction across {meaningful_actions} user actions."})
            explanations.append(f"High engagement ({meaningful_actions} content interactions)")
        elif meaningful_actions >= 1:
            impact = 5.0 * meaningful_actions
            base_score += impact
            factors.append({"factor": "positive_engagement", "impact": int(impact), "reason": f"Active participation with {meaningful_actions} user actions."})
            explanations.append("Active interaction with match details")
            
        # 2. Information value (H2H, statistics, team comparison, team form, match insights)
        info_terms = ["stat", "compare", "comparison", "h2h", "form", "insights", "save"]
        info_count = sum(1 for e in events if any(t in f"{e.event_type or ''} {e.page or ''} {e.action or ''}".lower() for t in info_terms))
        if info_count >= 2:
            base_score += 20.0
            factors.append({"factor": "information_value", "impact": 20, "reason": "Deep exploration of head-to-head analytics and team stats."})
            explanations.append("Deep information engagement across comparative stats")
        elif info_count == 1:
            base_score += 10.0
            factors.append({"factor": "information_value", "impact": 10, "reason": "Inspected team statistics and fixture context."})
            explanations.append("Inspected team statistics")
            
        # 3. Action progression (e.g. progressing to market, betslip, or completed demo action)
        if any(term in combined for term in ["betslip", "market", "bet_confirmed", "select"]):
            base_score += 15.0
            factors.append({"factor": "action_progression", "impact": 15, "reason": "User progressed purposefully toward market/selection resolution."})
            explanations.append("Clear progression toward action resolution")
            
        # 4. Recommendation engagement
        rec_clicks = sum(1 for a in all_actions if "recommendation_click" in a or "guidance" in a)
        if rec_clicks >= 1:
            base_score += 10.0
            factors.append({"factor": "recommendation_engagement", "impact": 10, "reason": "User accepted contextual guidance and interacted with recommended content."})
            explanations.append("Contextual recommendation interaction")
            
        # 5. Friction penalty
        if friction_score >= 70:
            base_score -= 25.0
            factors.append({"factor": "friction_penalty", "impact": -25, "reason": f"Severe navigation loops or back navigation friction ({friction_score} pts)."})
            explanations.append(f"Significant quality loss from friction ({friction_score} pts)")
        elif friction_score >= 30:
            base_score -= 10.0
            factors.append({"factor": "friction_penalty", "impact": -10, "reason": f"Minor navigational hesitation detected ({friction_score} pts)."})
            explanations.append("Minor deduction due to navigation hesitation")
            
        # 6. Abandonment penalty
        if abandonment_prob >= 0.70:
            base_score -= 20.0
            factors.append({"factor": "abandonment_penalty", "impact": -20, "reason": f"Elevated early abandonment probability ({int(abandonment_prob * 100)}%)."})
            explanations.append(f"Elevated abandonment risk ({int(abandonment_prob * 100)}%)")
        elif abandonment_prob >= 0.40:
            base_score -= 8.0
            factors.append({"factor": "abandonment_penalty", "impact": -8, "reason": "Moderate abandonment risk."})
            
        # 7. Repetition penalty
        if any("cta_hesitation" in a for a in all_actions):
            base_score -= 5.0
            factors.append({"factor": "repetition_penalty", "impact": -5, "reason": "User exhibited CTA hesitation before deciding."})
            explanations.append("Hesitation recorded on key CTA")
            
        final_quality = round(max(0.0, min(100.0, base_score)), 1)
        explanation_text = "; ".join(explanations) if explanations else "Standard exploratory session."
        
        return final_quality, explanation_text, factors

