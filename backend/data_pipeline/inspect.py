import pandas as pd
import os
from typing import Dict, Any

class DatasetInspector:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.format = self.file_name.split('.')[-1].lower() if '.' in self.file_name else 'unknown'
        
    def load_data(self) -> pd.DataFrame:
        if self.format == 'csv':
            return pd.read_csv(self.file_path)
        elif self.format == 'json':
            return pd.read_json(self.file_path)
        elif self.format == 'parquet':
            return pd.read_parquet(self.file_path)
        else:
            raise ValueError(f"Unsupported format: {self.format}")
            
    def inspect(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate a basic inspection report from a raw dataframe."""
        report = {
            "file_name": self.file_name,
            "file_format": self.format,
            "row_count": len(df),
            "column_count": len(df.columns),
            "column_names": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": df.isnull().sum().to_dict(),
            "duplicate_rows": int(df.duplicated().sum()),
        }
        
        # Categorical distributions for string/object columns (limit to top 10 per column)
        categorical_distributions = {}
        for col in df.columns:
            if df[col].dtype == 'object' or str(df[col].dtype) == 'category':
                val_counts = df[col].value_counts()
                # Store top 10 distributions to not blow up the report
                categorical_distributions[col] = val_counts.head(10).to_dict()
                
        report["categorical_distributions"] = categorical_distributions
        
        return report
