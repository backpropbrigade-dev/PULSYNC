import pandas as pd
import hashlib
from typing import Dict, Tuple

class DataCleaner:
    """Handles data cleaning, session reconstruction, and feature generation."""
    
    def __init__(self, session_gap_minutes: int = 30):
        self.session_gap_minutes = session_gap_minutes
        
    def process_duplicates(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
        raw_rows = len(df)
        exact_duplicate_rows = df.duplicated().sum()
        df_cleaned = df.drop_duplicates()
        rows_removed = raw_rows - len(df_cleaned)
        rows_retained = len(df_cleaned)
        
        report = {
            "raw_rows": int(raw_rows),
            "exact_duplicate_rows": int(exact_duplicate_rows),
            "rows_removed": int(rows_removed),
            "rows_retained": int(rows_retained)
        }
        return df_cleaned, report
        
    def split_attributed(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, int]]:
        unattributed = df[df['user_id'].isnull()]
        attributed = df[df['user_id'].notnull()].copy()
        report = {
            "unattributed_rows": len(unattributed),
            "attributed_rows": len(attributed)
        }
        return attributed, unattributed, report
        
    def reconstruct_sessions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Uses PlayerID and chronological timestamps to synthesize sessions."""
        if df.empty:
            return df
            
        # Ensure timestamp is datetime and sort
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])
        df = df.sort_values(['user_id', 'timestamp']).copy()
        
        # Calculate time diff
        df['time_diff'] = df.groupby('user_id')['timestamp'].diff()
        
        # Identify session boundaries
        threshold = pd.Timedelta(minutes=self.session_gap_minutes)
        df['new_session_flag'] = (df['time_diff'] > threshold) | df['time_diff'].isna()
        
        # Cumulative sum gives sequential session integer per user
        df['session_seq'] = df.groupby('user_id')['new_session_flag'].cumsum()
        
        # Generate deterministic IDs (vectorized for speed)
        session_strs = df['user_id'].astype(str) + "_" + df['session_seq'].astype(str)
        session_ids = ["sess_" + hashlib.md5(s.encode()).hexdigest()[:12] for s in session_strs]
        df['session_id'] = session_ids
        
        # Clean up temporaries
        df = df.drop(columns=['time_diff', 'new_session_flag', 'session_seq'])
        return df
        
    def generate_session_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates features per reconstructed session."""
        if df.empty:
            return pd.DataFrame()
            
        grouped = df.groupby('session_id')
        
        stats = grouped.agg(
            user_id=('user_id', 'first'),
            started_at=('timestamp', 'min'),
            ended_at=('timestamp', 'max'),
            total_events=('timestamp', 'count'),
            total_actions=('action', lambda x: x.notnull().sum()),
            unique_sports=('sport', 'nunique'),
            unique_matches=('match_id', 'nunique'),
            unique_events=('event_type', 'nunique'),
            last_event_type=('event_type', 'last'),
            last_sport=('sport', 'last'),
            last_match=('match_id', 'last')
        ).reset_index()
        
        stats['session_duration'] = (stats['ended_at'] - stats['started_at']).dt.total_seconds()
        stats['average_time_between_events'] = stats.apply(
            lambda x: x['session_duration'] / (x['total_events'] - 1) if x['total_events'] > 1 else 0, 
            axis=1
        )
        # Using 0 as MVP since we have no distinct page-view vs action differentiation in historical
        stats['time_to_first_action'] = 0 
        
        return stats
