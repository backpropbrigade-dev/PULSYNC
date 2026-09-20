import os
import sys
import json
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.data_pipeline.schema import SchemaMapper
from backend.data_pipeline.cleaner import DataCleaner

def preprocess(target_path: str = "assets/SB_Player.csv"):
    if not os.path.exists(target_path):
        print(f"ERROR: Could not find raw dataset at {target_path}")
        return
        
    print("========================================")
    print("PULSYNC DATASET PREPROCESSING")
    print("========================================")
    
    # 1. Load Raw
    print("1. Loading raw events...")
    raw_df = pd.read_csv(target_path)
    
    # 2. Schema mapping
    print("2. Mapping columns to standardized schema...")
    mapper = SchemaMapper()
    col_mapping = mapper.guess_mapping(raw_df.columns.tolist())
    std_df = mapper.apply_mapping(raw_df, col_mapping)
    
    # 3. Timestamp normalization
    print("3. Normalizing timestamps...")
    std_df['timestamp'] = pd.to_datetime(std_df['timestamp'], errors='coerce')
    
    cleaner = DataCleaner(session_gap_minutes=30)
    
    # 4. Filter missing PlayerID
    print("4. Separating unattributed events from user-attributed events...")
    attributed_df, unattributed_df, attr_report = cleaner.split_attributed(std_df)
    
    os.makedirs("data/processed", exist_ok=True)
    unattributed_df.to_csv("data/processed/SB_Player_unattributed.csv", index=False)
    print(f"   -> Saved {len(unattributed_df):,} unattributed events to data/processed/SB_Player_unattributed.csv")
    
    # 5. Remove exact duplicates
    print("5. Removing exact duplicate events from attributed dataset...")
    cleaned_df, dup_report = cleaner.process_duplicates(attributed_df)
    print(f"   -> Retained {len(cleaned_df):,} events after dropping {dup_report['rows_removed']:,} duplicates.")
    
    # 6. Reconstruct synthetic sessions
    print("6. Reconstructing synthetic sessions (30-minute inactivity threshold)...")
    reconstructed_df = cleaner.reconstruct_sessions(cleaned_df)
    
    # 7. Generate session-level features
    print("7. Generating session-level behavioral features...")
    session_features = cleaner.generate_session_features(reconstructed_df)
    
    # 8. Save Processed Artifacts
    print("8. Saving processed datasets...")
    reconstructed_df.to_csv("data/processed/SB_Player_processed_events.csv", index=False)
    session_features.to_csv("data/processed/SB_Player_session_features.csv", index=False)
    
    # Dataset Provenance Metadata
    provenance = {
        "source": target_path,
        "processed_at": datetime.utcnow().isoformat() + "Z",
        "session_type": "synthetic_reconstructed",
        "session_gap_minutes": 30,
        "native_session_id_available": False,
        "page_telemetry_available": False,
        "metadata_available": False,
        "note": "Reconstructed historical sessions represent behavioral proxies based on daily transaction timestamps."
    }
    with open("data/processed/dataset_provenance.json", "w") as f:
        json.dump(provenance, f, indent=4)
        
    print("\n========================================")
    print("PREPROCESSING COMPLETED")
    print("========================================")
    print(f"Raw rows: {len(raw_df):,}")
    print(f"Cleaned event rows: {len(cleaned_df):,}")
    print(f"Reconstructed sessions: {len(session_features):,}")
    print(f"Unique users: {session_features['user_id'].nunique():,}")
    print(f"Average events / session: {session_features['total_events'].mean():.2f}")
    print(f"Median events / session: {session_features['total_events'].median():.2f}")
    print("Artifacts generated in data/processed/")
    print("========================================\n")

if __name__ == "__main__":
    preprocess()
