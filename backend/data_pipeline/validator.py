import pandas as pd
from typing import Dict, Any

class DataValidator:
    """Performs quality checks on the standardized DataFrame."""
    
    def validate(self, std_df: pd.DataFrame) -> Dict[str, Any]:
        report = {}
        
        # Missing values check
        report["missing_session_ids"] = int(std_df["session_id"].isnull().sum())
        report["missing_timestamps"] = int(std_df["timestamp"].isnull().sum())
        report["missing_user_ids"] = int(std_df["user_id"].isnull().sum())
        
        # Duplicates check (on all standardized columns)
        report["duplicate_events"] = int(std_df.duplicated().sum())
        
        # Timestamp validation
        if not std_df["timestamp"].isnull().all():
            try:
                # Try to convert to datetime
                timestamps = pd.to_datetime(std_df["timestamp"], errors='coerce')
                report["invalid_timestamps"] = int(timestamps.isnull().sum()) - report["missing_timestamps"]
                valid_ts = timestamps.dropna()
                if not valid_ts.empty:
                    report["timestamp_range"] = {
                        "min": valid_ts.min().isoformat(),
                        "max": valid_ts.max().isoformat()
                    }
                else:
                    report["timestamp_range"] = None
            except Exception:
                report["invalid_timestamps"] = len(std_df)
                report["timestamp_range"] = None
        else:
            report["invalid_timestamps"] = len(std_df)
            report["timestamp_range"] = None
            
        # Basic quality score calculation
        total_rows = len(std_df)
        if total_rows == 0:
            report["quality_score"] = 0
            return report
            
        deductions = 0
        
        # Deduct points for missing critical fields
        missing_user_pct = report["missing_user_ids"] / total_rows
        missing_session_pct = report["missing_session_ids"] / total_rows
        missing_ts_pct = report["missing_timestamps"] / total_rows
        invalid_ts_pct = report["invalid_timestamps"] / total_rows
        
        deductions += (missing_user_pct * 30)  # User ID is very important
        deductions += (missing_session_pct * 30)  # Session ID is very important
        deductions += ((missing_ts_pct + invalid_ts_pct) * 20)
        
        score = max(0, min(100, 100 - int(deductions)))
        report["quality_score"] = score
        
        return report
