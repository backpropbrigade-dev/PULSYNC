import pandas as pd
import numpy as np

def generate_features_and_labels_from_chunk(chunk_df):
    """
    Process a chunk of event data (which must be grouped by session)
    to generate prefix-level features and targets for Next Intent and Abandonment/Continuation.
    """
    features = []
    labels_abandonment = []
    labels_continuation = []
    labels_intent = []
    
    # Sort by session and timestamp (assuming row order is roughly chronological)
    # The dataset timestamps are dates, so we rely on natural row order for sequence within a day.
    
    for session_id, group in chunk_df.groupby("session_id", sort=False):
        events = group.to_dict('records')
        n_events = len(events)
        
        unique_sports = set()
        unique_matches = set()
        
        for k in range(n_events):
            e = events[k]
            unique_sports.add(e.get("sport", "Unknown"))
            unique_matches.add(e.get("match_id", "Unknown"))
            
            # Features at step k
            feat = {
                "session_id": session_id,
                "event_index": k + 1,
                "events_so_far": k + 1,
                "unique_sports_so_far": len(unique_sports),
                "unique_matches_so_far": len(unique_matches),
                "is_prematch": 1 if e.get("event_type") == "PREMATCH" else 0,
                "is_live": 1 if e.get("event_type") == "LIVE" else 0,
                "is_lottery": 1 if e.get("event_type") == "WORLD_LOTTERY" else 0,
            }
            
            # Target generation
            is_abandoned = 1 if k == n_events - 1 else 0
            is_continued = 1 if k < n_events - 1 else 0
            
            intent = "UNKNOWN"
            if is_continued:
                next_e = events[k+1]
                # Next intent logic
                if next_e.get("match_id") != e.get("match_id"):
                    intent = "COMPARE"
                else:
                    action = str(next_e.get("action", ""))
                    if action.isdigit():
                        intent = "EXPLORE"
                    elif "/" in action or "-" in action:
                        intent = "UNDERSTAND"
                    elif next_e.get("event_type") == "LIVE" and e.get("event_type") == "PREMATCH":
                        intent = "REVIEW"
                    else:
                        intent = "ACT"
            
            features.append(feat)
            labels_abandonment.append(is_abandoned)
            labels_continuation.append(is_continued)
            labels_intent.append(intent)
            
    df_feat = pd.DataFrame(features)
    df_feat["target_abandonment"] = labels_abandonment
    df_feat["target_continuation"] = labels_continuation
    df_feat["target_intent"] = labels_intent
    
    return df_feat
