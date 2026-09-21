from typing import List, Tuple
from backend.models import Event
from backend.ml.model_registry import ModelRegistry

class IntentDetector:
    """Detects current user session intent, transaction intent, information interest, and engagement state."""
    
    INTENTS = ["EXPLORE", "COMPARE", "UNDERSTAND", "REVIEW", "ACT"]
    
    @classmethod
    def detect_intent(cls, events: List[Event]) -> Tuple[str, float, str]:
        """
        Analyzes the last few events in the session to deduce the user's immediate intent.
        Returns: (intent, confidence, reason)
        """
        if not events:
            return "EXPLORE", 0.50, "New session started with exploratory posture."
            
        registry = ModelRegistry()
        if registry.is_loaded():
            try:
                # Extract features for ML
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
                
                _, _, ml_intent, ml_conf, _ = registry.predict(features)
                
                # Use ML if confidence is above threshold
                if ml_conf >= 0.40:
                    reason_by_intent = {
                        "COMPARE": "User is comparing team attributes, head-to-head records, and relative match forms.",
                        "UNDERSTAND": "User is inspecting detailed match statistics and rules to understand context.",
                        "ACT": "User is taking decisive action in the session.",
                        "REVIEW": "User is navigating back and reviewing previously considered match information.",
                        "EXPLORE": "User is actively exploring the fixture catalog across leagues and sports.",
                    }
                    reason = reason_by_intent.get(
                        ml_intent,
                        "User intent estimated from historical session behavior."
                    )
                    return ml_intent, ml_conf, f"ML Prediction ({registry.get_version()}): {reason}"
            except Exception as e:
                print(f"ML intent prediction failed: {e}. Falling back to heuristic.")
                
        # Heuristic fallback
            
        recent = events[-8:] # Analyze last 8 interactions
        event_types = [e.event_type.lower() if e.event_type else "" for e in recent]
        pages = [e.page.lower() if e.page else "" for e in recent]
        actions = [e.action.lower() if e.action else "" for e in recent]
        
        all_text = " ".join(event_types + pages + actions)
        
        # 1. ACT intent: betslip interactions, placing bets, or saving match content
        if any(term in all_text for term in ["betslip", "place_bet", "click_place_bet", "save", "content_click", "share", "select", "pin"]):
            return (
                "ACT",
                0.88,
                "User is taking decisive action in the session (viewing betslip, placing bet, or saving content)."
            )
            
        # 2. COMPARE intent: user viewing H2H, team comparison, switching between teams/matches
        if any(term in all_text for term in ["compare", "comparison", "h2h", "versus", "vs", "head_to_head"]):
            return (
                "COMPARE",
                0.85,
                "User is comparing team attributes, head-to-head records, and relative match forms."
            )
            
        # 3. UNDERSTAND intent: user diving deep into statistics, rules, team forms, metrics
        if any(term in all_text for term in ["stat", "statistics", "rule", "info", "form", "detail"]):
            return (
                "UNDERSTAND",
                0.80,
                "User is inspecting detailed match statistics and rules to understand context."
            )
            
        # 4. REVIEW intent: user going back, returning to previously opened matches or overview
        if any(term in all_text for term in ["back", "overview", "history", "summary"]) or "back" in event_types:
            return (
                "REVIEW",
                0.75,
                "User is navigating back and reviewing previously considered match information."
            )
            
        # 5. EXPLORE: default browsing sports and matches
        match_views = sum(1 for et in event_types if "match" in et or "search" in et or "navigation" in et or "sport" in et)
        if match_views >= 2:
            return (
                "EXPLORE",
                0.78,
                "User is actively exploring the fixture catalog across leagues and sports."
            )
            
        return (
            "EXPLORE",
            0.60,
            "General browsing behavior observed across sports event categories."
        )

    @classmethod
    def calculate_transaction_intent(cls, events: List[Event]) -> str:
        """
        Evaluates observed transaction / betting intent in the current session.
        Returns: "HIGH", "MEDIUM", or "LOW"
        """
        if not events:
            return "LOW"
            
        recent = events[-8:]
        all_text = " ".join([
            f"{e.event_type or ''} {e.page or ''} {e.action or ''}".lower()
            for e in recent
        ])
        
        # High transaction signals: betslip, place bet, selections, multiple market views
        high_signals = ["betslip", "place_bet", "click_place_bet", "add_selection", "remove_selection", "odds_click"]
        if any(sig in all_text for sig in high_signals):
            return "HIGH"
            
        market_views = sum(1 for e in recent if any(m in f"{e.event_type or ''} {e.page or ''} {e.action or ''}".lower() for m in ["market", "view_market", "odds"]))
        if market_views >= 2:
            return "HIGH"
        elif market_views == 1:
            return "MEDIUM"
            
        return "LOW"

    @classmethod
    def calculate_information_interest(cls, events: List[Event], abandonment_prob: float = 0.0) -> str:
        """
        Evaluates observed informational interest in the current session.
        Returns: "HIGH", "MEDIUM", or "LOW"
        """
        if not events:
            return "HIGH"
            
        recent = events[-8:]
        all_text = " ".join([
            f"{e.event_type or ''} {e.page or ''} {e.action or ''}".lower()
            for e in recent
        ])
        
        # Check explicit exit signal
        if any(term in all_text for term in ["explicit_exit", "exit", "dismiss_all"]):
            return "LOW"
            
        if abandonment_prob > 0.85:
            return "LOW"
            
        # High information signals: match view, team view, statistics, comparison, H2H, form, insights, save
        info_signals = ["match", "team", "stat", "statistics", "compare", "comparison", "h2h", "form", "insights", "save"]
        info_count = sum(1 for e in recent if any(sig in f"{e.event_type or ''} {e.page or ''} {e.action or ''}".lower() for sig in info_signals))
        
        if info_count >= 2:
            return "HIGH"
        elif info_count == 1:
            return "MEDIUM"
            
        return "MEDIUM" if len(events) <= 3 else "LOW"

    @classmethod
    def evaluate_engagement_state(cls, transaction_intent: str, information_interest: str, explicit_exit: bool = False) -> Tuple[str, str]:
        """
        Calculates engagement_state and recommendation_mode based on decision matrix.
        Returns: (engagement_state, recommendation_mode)
        """
        if explicit_exit:
            return "RESPECT_EXIT", "RESPECT_EXIT"
            
        if transaction_intent == "LOW" and information_interest == "HIGH":
            return "VALUE_SEEKING", "VALUE_SEEKING"
        elif transaction_intent == "LOW" and information_interest == "MEDIUM":
            return "LOW_PRESSURE", "LOW_PRESSURE"
        elif transaction_intent == "LOW" and information_interest == "LOW":
            return "RESPECT_EXIT", "RESPECT_EXIT"
        else:
            return "NORMAL", "NORMAL"
