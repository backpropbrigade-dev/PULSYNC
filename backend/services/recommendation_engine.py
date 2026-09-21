from typing import List, Dict, Any, Optional
from backend.models import Event, Recommendation, UserProfile, Session as DBSession
from backend.config import settings

class RecommendationEngine:
    """
    Core Intelligence Recommendation Engine for PULSYNC.
    Ranks next-best informational and context content for sports fans.
    STRICTLY NON-GAMBLING: Recommends insights, comparisons, form, rules, and statistics.
    """
    
    CANDIDATES = [
        {
            "id": "rec_team_comp",
            "type": "Team Comparison",
            "title": "Comprehensive Team Comparison",
            "description": "Side-by-side metric comparison of attacking and defensive attributes.",
            "base_info_value": 0.85,
            "best_intents": ["COMPARE", "REVIEW"],
            "relevant_pages": ["match_detail", "comparison", "statistics"]
        },
        {
            "id": "rec_h2h",
            "type": "Head-to-Head",
            "title": "Head-to-Head Historical Encounters",
            "description": "Historical record, scorelines, and match pacing from the past 5 encounters.",
            "base_info_value": 0.80,
            "best_intents": ["COMPARE", "UNDERSTAND"],
            "relevant_pages": ["match_detail", "h2h", "home"]
        },
        {
            "id": "rec_team_form",
            "type": "Team Form",
            "title": "Recent Team Form & Momentum Index",
            "description": "Trend breakdown over the past 6 matches with home/away splits.",
            "base_info_value": 0.75,
            "best_intents": ["UNDERSTAND", "REVIEW"],
            "relevant_pages": ["match_detail", "team_form", "statistics"]
        },
        {
            "id": "rec_key_stats",
            "type": "Key Statistics",
            "title": "Key Match Statistics & Expected Metrics",
            "description": "Deep-dive into possession, shots on target, conversion rates, and momentum.",
            "base_info_value": 0.90,
            "best_intents": ["UNDERSTAND", "COMPARE"],
            "relevant_pages": ["statistics", "match_detail"]
        },
        {
            "id": "rec_match_insights",
            "type": "Match Insights",
            "title": "Tactical Match Insights & Pre-Match Analysis",
            "description": "Tactical preview highlighting tactical matchups, key absences, and storylines.",
            "base_info_value": 0.85,
            "best_intents": ["EXPLORE", "UNDERSTAND"],
            "relevant_pages": ["match_detail", "home", "insights"]
        },
        {
            "id": "rec_similar_matches",
            "type": "Similar Matches",
            "title": "Similar Matches in This Tournament",
            "description": "Contextual fixtures featuring similar tactical setups and league stakes.",
            "base_info_value": 0.70,
            "best_intents": ["EXPLORE"],
            "relevant_pages": ["home", "fixtures", "search"]
        },
        {
            "id": "rec_related_events",
            "type": "Related Events",
            "title": "Related Live Fixtures & Standings Impact",
            "description": "How this fixture's outcome directly shifts league table rankings.",
            "base_info_value": 0.65,
            "best_intents": ["EXPLORE", "ACT"],
            "relevant_pages": ["home", "fixtures"]
        },
        {
            "id": "rec_rules_info",
            "type": "Rules / Information",
            "title": "Tournament Format, Rules & Overtime Clarifications",
            "description": "Official tournament tiebreakers, extra-time regulations, and scheduling details.",
            "base_info_value": 0.60,
            "best_intents": ["UNDERSTAND", "REVIEW"],
            "relevant_pages": ["rules", "info", "match_detail"]
        },
        {
            "id": "rec_save_later",
            "type": "Save for Later",
            "title": "Save Match to Personal Digest",
            "description": "Pin this fixture to your saved matches for instant access and post-game recaps.",
            "base_info_value": 0.70,
            "best_intents": ["ACT", "REVIEW"],
            "relevant_pages": ["match_detail", "comparison", "statistics"]
        }
    ]
    
    @classmethod
    def generate_recommendations(
        cls,
        session: DBSession,
        user: Optional[UserProfile],
        events: List[Event],
        current_intent: str,
        friction_level: str,
        abandonment_probability: float,
        previous_recommendations: List[Recommendation],
        transaction_intent: str = "LOW",
        information_interest: str = "HIGH",
        engagement_state: str = "VALUE_SEEKING",
        recommendation_mode: str = "VALUE_SEEKING",
        compliance: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:

        # 0. RESPECT_EXIT: return nothing — honour user's choice
        if recommendation_mode == "RESPECT_EXIT" or engagement_state == "RESPECT_EXIT":
            return []

        current_page = events[-1].page.lower() if events and events[-1].page else "match_detail"
        recent_event_types = [e.event_type.lower() for e in events[-5:] if e.event_type]

        # History tracking for penalties
        viewed_content = {r.content_id for r in previous_recommendations if r.clicked}
        dismissed_content = {r.content_id for r in previous_recommendations if r.dismissed}
        recently_shown = {r.content_id for r in previous_recommendations[-3:]}

        user_segment = user.segment if user else "Casual Explorer"

        # Allowed candidate types based on recommendation_mode
        allowed_types = None
        if recommendation_mode in ("VALUE_SEEKING", "LOW_PRESSURE") or (transaction_intent == "LOW" and information_interest in ("HIGH", "MEDIUM")):
            # Filter to strictly informational content only
            allowed_types = {
                "Team Comparison", "Head-to-Head", "Team Form",
                "Key Statistics", "Match Insights", "Save for Later"
            }
        elif recommendation_mode == "NORMAL" and transaction_intent in ("HIGH", "MEDIUM"):
            # High betting intent: provide informational context to help informed decision
            # NEVER recommend stake increases, bet more, or loss recovery
            allowed_types = {
                "Key Statistics", "Team Form", "Head-to-Head",
                "Team Comparison", "Match Insights", "Save for Later"
            }


        scored_candidates = []
        
        for cand in cls.CANDIDATES:
            cand_id = cand["id"]
            cand_type = cand["type"]
            
            if allowed_types and cand_type not in allowed_types:
                continue
            
            # 1. Intent Relevance (0 - 1.0)
            if current_intent in cand["best_intents"]:
                intent_rel = 1.0
            elif "EXPLORE" in cand["best_intents"]:
                intent_rel = 0.5
            else:
                intent_rel = 0.2
                
            # 2. Page Relevance (0 - 1.0)
            if any(p in current_page for p in cand["relevant_pages"]):
                page_rel = 1.0
            else:
                page_rel = 0.3
                
            # 3. User Interest Match (0 - 1.0)
            user_interest = 0.5
            if user_segment == "Statistics Focused" and cand_type in ["Key Statistics", "Team Form", "Team Comparison"]:
                user_interest = 1.0
            elif user_segment == "Match Information Seeker" and cand_type in ["Match Insights", "Head-to-Head"]:
                user_interest = 1.0
            elif user_segment == "Football Explorer" and cand_type in ["Team Comparison", "Team Form", "Match Insights"]:
                user_interest = 0.9
            elif user_segment == "Multi-Sport Explorer" and cand_type in ["Related Events", "Similar Matches"]:
                user_interest = 0.9
                
            # 4. Recent Behavior Match (0 - 1.0)
            recent_match = 0.4
            if any("stat" in et for et in recent_event_types) and cand_type in ["Key Statistics", "Team Comparison"]:
                recent_match = 1.0
            elif any("h2h" in et or "compare" in et for et in recent_event_types) and cand_type in ["Team Comparison", "Head-to-Head"]:
                recent_match = 1.0
            elif any("back" in et for et in recent_event_types) and cand_type in ["Team Comparison", "Match Insights"]:
                recent_match = 0.85
                
            # 5. Information Value (0 - 1.0)
            info_val = cand["base_info_value"]
            
            # Combine via formula
            raw_score = (
                settings.W_INTENT * intent_rel
                + settings.W_PAGE * page_rel
                + settings.W_USER * user_interest
                + settings.W_RECENT * recent_match
                + settings.W_INFO * info_val
            ) * 100.0
            
            # High friction bonus: If user is struggling/looping, Team Comparison and Insights give immediate clarity
            if friction_level == "HIGH" and cand_type in ["Team Comparison", "Head-to-Head", "Match Insights"]:
                raw_score += 10.0
                
            # Abandonment risk bonus: Suggest digestible summary or save for later
            if abandonment_probability > 0.60 and cand_type in ["Team Comparison", "Save for Later", "Key Statistics"]:
                raw_score += 8.0
                
            # Deductions & Penalties
            reasons = []
            if cand_id in dismissed_content:
                raw_score -= 40.0
                reasons.append("Penalized (previously dismissed)")
            if cand_id in viewed_content:
                raw_score -= 25.0
                reasons.append("Adjusted (already viewed)")
            if cand_id in recently_shown:
                raw_score -= 20.0
                reasons.append("De-prioritized (recently presented)")
                
            final_score = round(max(5.0, min(100.0, raw_score)), 1)
            
            # Construct human-readable explainable reason
            if current_intent == "COMPARE":
                reason = f"User is actively comparing match perspectives; {cand_type} directly satisfies this intent."
            elif current_intent == "UNDERSTAND":
                reason = f"User is inspecting statistical depth; {cand_type} provides instant contextual clarity."
            elif current_intent == "REVIEW":
                reason = f"User is reviewing options after navigation; {cand_type} highlights summarized differences."
            elif current_intent == "ACT":
                reason = f"User ready to digest structured match insight; {cand_type} offers direct utility."
            else:
                reason = f"Exploratory guidance matching {user_segment} profile and current {current_page} context."
                
            if reasons:
                reason += f" [{', '.join(reasons)}]"
                
            scored_candidates.append({
                "content_id": cand_id,
                "content_type": cand_type,
                "title": cand["title"],
                "score": final_score,
                "reason": reason
            })
            
        # Rank descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        for idx, item in enumerate(scored_candidates):
            item["rank"] = idx + 1
            
        return scored_candidates
