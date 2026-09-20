import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import engine
from backend.models import Base

def seed_database():
    print("========================================")
    print("PULSYNC: DATABASE SEEDING")
    print("========================================")
    
    # 1. Create tables
    print("Creating tables in SQLite...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # 2. Load Processed datasets
    sessions_path = "data/processed/SB_Player_session_features.csv"
    events_path = "data/processed/SB_Player_processed_events.csv"
    
    if not os.path.exists(sessions_path) or not os.path.exists(events_path):
        print("ERROR: Processed datasets missing. Run validate_dataset.py first.")
        return
        
    print("Loading datasets into memory...")
    sessions_df = pd.read_csv(sessions_path)
    events_df = pd.read_csv(events_path)
    
    # 3. Users Table Seeding
    print("Seeding Users...")
    users_df = pd.DataFrame({'id': sessions_df['user_id'].unique()})
    users_df.to_sql("users", con=engine, if_exists="append", index=False)
    print(f"-> Inserted {len(users_df)} users.")
    
    # 4. Sessions Table Seeding
    print("Seeding Reconstructed Sessions...")
    # Map pandas columns to SQLAlchemy Session model
    db_sessions = sessions_df.rename(columns={
        'session_id': 'id',
        'started_at': 'started_at',
        'ended_at': 'ended_at',
        'session_duration': 'duration_seconds'
    })
    db_sessions['is_synthetic'] = True
    db_sessions['friction_score'] = None
    
    # Select columns matching the table
    session_cols = [
        'id', 'user_id', 'is_synthetic', 'started_at', 'ended_at', 
        'duration_seconds', 'total_events', 'total_actions', 'unique_sports',
        'friction_score'
    ]
    db_sessions[session_cols].to_sql("sessions", con=engine, if_exists="append", index=False)
    print(f"-> Inserted {len(db_sessions)} synthetic sessions.")
    
    # 5. Events Table Seeding (Chunked to prevent out-of-memory)
    print("Seeding Historical Events (Chunked)...")
    db_events = events_df.rename(columns={
        'timestamp': 'timestamp',
        'event_type': 'event_type',
        'action': 'action',
        'sport': 'sport',
        'match_id': 'match_id'
    })
    # 'id' will auto-increment. 'page' is None for historical data.
    db_events['page'] = None
    
    event_cols = [
        'session_id', 'user_id', 'timestamp', 'event_type', 'action', 
        'page', 'sport', 'match_id'
    ]
    
    db_events[event_cols].to_sql("events", con=engine, if_exists="append", index=False, chunksize=100000)
    print(f"-> Inserted {len(db_events)} historical events.")
    print("========================================")
    print("DATABASE SEEDING COMPLETE!")
    print("========================================")

if __name__ == "__main__":
    seed_database()
