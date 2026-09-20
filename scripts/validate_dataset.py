import os
import sys
import json
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.data_pipeline.inspect import DatasetInspector
from backend.data_pipeline.schema import SchemaMapper
from backend.data_pipeline.validator import DataValidator

def validate(target_path: str = "assets/SB_Player.csv"):
    if not os.path.exists(target_path):
        print(f"ERROR: Could not find dataset at {target_path}")
        return None
        
    print("========================================")
    print("PULSYNC DATASET VALIDATION PIPELINE")
    print("========================================")
    print(f"Inspecting file: {target_path}")
    
    inspector = DatasetInspector(target_path)
    raw_df = inspector.load_data()
    inspect_report = inspector.inspect(raw_df)
    
    mapper = SchemaMapper()
    col_mapping = mapper.guess_mapping(raw_df.columns.tolist())
    std_df = mapper.apply_mapping(raw_df, col_mapping)
    
    validator = DataValidator()
    quality_report = validator.validate(std_df)
    
    print("\n========================================")
    print("VALIDATION SUMMARY")
    print("========================================")
    print(f"File Name: {inspect_report['file_name']}")
    print(f"Format: {inspect_report['file_format']}")
    print(f"Total Rows: {inspect_report['row_count']:,}")
    print(f"Total Columns: {inspect_report['column_count']}")
    print(f"Columns Discovered: {', '.join(inspect_report['column_names'])}")
    print(f"Exact Duplicate Rows: {inspect_report['duplicate_rows']:,}")
    print(f"Missing PlayerID: {quality_report['missing_user_ids']:,}")
    print(f"Missing Actions: {int(std_df['action'].isnull().sum()):,}")
    print(f"Timestamp Range: {quality_report.get('timestamp_range', 'Unavailable')}")
    print(f"Dataset Quality Score: {quality_report['quality_score']}/100")
    print("========================================\n")
    
    full_report = {
        "dataset_summary": inspect_report,
        "schema_mapping": col_mapping,
        "quality_report": quality_report,
        "validated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    with open("data_validation_report.json", "w") as f:
        json.dump(full_report, f, indent=4)
        
    summary_df = pd.DataFrame([{
        "File": inspect_report['file_name'],
        "Rows": inspect_report['row_count'],
        "Columns": inspect_report['column_count'],
        "Duplicates": inspect_report['duplicate_rows'],
        "Missing_Users": quality_report['missing_user_ids'],
        "Quality_Score": quality_report['quality_score']
    }])
    summary_df.to_csv("data_validation_report.csv", index=False)
    print("Saved 'data_validation_report.json' and 'data_validation_report.csv'.")
    return full_report

if __name__ == "__main__":
    validate()
