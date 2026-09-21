from typing import Dict, Any, Optional

class ContextualGuidanceService:
    """
    Decides when and how to proactively offer non-intrusive contextual assistance to users
    experiencing friction or elevated abandonment risk.
    """
    
    @classmethod
    def evaluate_intervention(
        cls,
        intent: str,
        friction_level: str,
        abandonment_probability: float,
        top_recommendation: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Intervention triggered strictly under high friction/abandonment conditions to aid comprehension.
        Never manipulative; user remains in complete control.
        """
        should_intervene = False
        message = None
        action = None
        content_id = None
        
        if top_recommendation:
            content_id = top_recommendation.get("content_id")
            content_title = top_recommendation.get("title", "Match Overview")
            
        # Trigger Condition 1: High friction and high abandonment risk
        if abandonment_probability >= 0.70 and friction_level == "HIGH":
            should_intervene = True
            if intent == "COMPARE":
                message = "Looks like you're comparing both teams. Would you like a unified side-by-side comparison?"
                action = "Open Team Comparison"
            elif intent == "UNDERSTAND":
                message = "Lots of stats to take in! Here's a clean summary of the most decisive match numbers."
                action = "View Key Statistics"
            else:
                message = f"Here is a quick digest to help you navigate: {content_title}."
                action = f"View {content_title}"
                
        # Trigger Condition 2: Moderate friction but high repeated back-navigation
        elif friction_level == "HIGH" and abandonment_probability >= 0.50:
            should_intervene = True
            message = "Need a quick shortcut? We've prepared a concise Head-to-Head & Form overview."
            action = "View Head-to-Head Overview"
            
        return {
            "should_intervene": should_intervene,
            "guidance_message": message,
            "recommended_action": action,
            "content_id": content_id
        }
