import pandas as pd
from typing import Dict, List, Optional

class SchemaMapper:
    """Maps arbitrary datasets to PULSYNC standard event schema."""
    
    STANDARD_COLUMNS = [
        "session_id",
        "user_id",
        "timestamp",
        "event_type",
        "page",
        "action",
        "sport",
        "match_id",
        "metadata"
    ]
    
    def __init__(self):
        # We can implement basic heuristic mapping rules here
        self.heuristic_map = {
            "user_id": ["playerid", "user_id", "userid", "user", "clientid"],
            "timestamp": ["placed_date", "start_datetime_utc", "timestamp", "time", "date"],
            "sport": ["sport_name", "sport_name_english", "sport"],
            "match_id": ["fixture_name_english", "match_name", "match", "event_name_english"],
            "session_id": ["session_id", "session"],
            "event_type": ["event_type", "type", "betslip_product", "market_name_english"],
            "action": ["action", "selection_name_english"],
            "page": ["page", "screen"],
        }
        
    def guess_mapping(self, columns: List[str]) -> Dict[str, Optional[str]]:
        """Guess the mapping from dataset columns to standard columns."""
        mapping = {col: None for col in self.STANDARD_COLUMNS}
        
        lower_cols = {c.lower(): c for c in columns}
        
        for std_col, guesses in self.heuristic_map.items():
            for guess in guesses:
                if guess in lower_cols:
                    mapping[std_col] = lower_cols[guess]
                    break
                    
        return mapping
        
    def apply_mapping(self, df: pd.DataFrame, mapping: Dict[str, Optional[str]]) -> pd.DataFrame:
        """Apply mapping to create a standardized DataFrame. Missing mapped columns will be created as NaN/None."""
        standard_df = pd.DataFrame()
        
        for std_col, orig_col in mapping.items():
            if orig_col and orig_col in df.columns:
                standard_df[std_col] = df[orig_col]
            else:
                standard_df[std_col] = pd.NA
                
        return standard_df
