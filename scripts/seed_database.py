import os
import sys
import datetime
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import engine
from backend.models import Base, Match, UserProfile

def seed():
    print("========================================")
    print("PULSYNC: DATABASE SEEDING")
    print("========================================")
    
    # 1. Initialize Tables
    print("Recreating database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    sessions_path = "data/processed/SB_Player_session_features.csv"
    events_path = "data/processed/SB_Player_processed_events.csv"
    
    if not os.path.exists(sessions_path) or not os.path.exists(events_path):
        print("ERROR: Processed data not found. Please run scripts/preprocess_dataset.py first.")
        return
        
    print("Loading processed data...")
    sessions_df = pd.read_csv(sessions_path)
    
    # 2. Seed Users
    print("Seeding Users...")
    unique_users = sessions_df['user_id'].dropna().unique()
    users_df = pd.DataFrame({
        'id': unique_users,
        'anonymous_id': [f"anon_{i:06d}" for i in range(len(unique_users))],
        'segment': 'Casual Explorer',
        'age_verified': False,
        'self_excluded': False,
        'created_at': datetime.datetime.utcnow()
    })
    users_df.to_sql("users", con=engine, if_exists="append", index=False)
    print(f"   -> Seeded {len(users_df):,} users.")
    
    # 3. Seed Reconstructed Sessions
    print("Seeding Sessions...")
    db_sessions = sessions_df.rename(columns={
        'session_id': 'id',
        'session_duration': 'duration_seconds'
    })
    db_sessions['is_synthetic'] = True
    db_sessions['intent'] = 'EXPLORE'
    db_sessions['intent_confidence'] = 0.60
    db_sessions['abandonment_probability'] = 0.15
    db_sessions['friction_score'] = 10.0
    db_sessions['friction_level'] = 'LOW'
    db_sessions['session_quality_score'] = 82.0
    db_sessions['status'] = 'ENDED'
    
    session_cols = [
        'id', 'user_id', 'started_at', 'ended_at', 'intent', 'intent_confidence',
        'abandonment_probability', 'friction_score', 'friction_level',
        'session_quality_score', 'status', 'is_synthetic', 'duration_seconds',
        'total_events', 'total_actions', 'unique_sports'
    ]
    db_sessions[session_cols].to_sql("sessions", con=engine, if_exists="append", index=False)
    print(f"   -> Seeded {len(db_sessions):,} reconstructed sessions.")
    
    # 4. Seed Events (Sample / Chunk)
    print("Seeding Sample Events (Chunked)...")
    # For rapid seeding and responsive MVP, seed first 150,000 events into DB
    events_chunk = pd.read_csv(events_path, nrows=150000)
    events_chunk['metadata_json'] = "{}"
    event_cols = [
        'session_id', 'user_id', 'timestamp', 'event_type', 'action',
        'page', 'sport', 'match_id', 'metadata_json'
    ]
    events_chunk[event_cols].to_sql("events", con=engine, if_exists="append", index=False)
    print(f"   -> Seeded {len(events_chunk):,} events.")
    
    # 5. Seed Catalog Matches
    print("Seeding Match Fixtures Catalog...")
    now = datetime.datetime.utcnow()
    sample_matches = pd.DataFrame([
        {
            "id": "match_el_clasico",
            "sport": "Football",
            "team_home": "Real Madrid",
            "team_away": "FC Barcelona",
            "start_time": now + datetime.timedelta(hours=2),
            "status": "UPCOMING"
        },
        {
            "id": "match_mci_ars",
            "sport": "Football",
            "team_home": "Manchester City",
            "team_away": "Arsenal",
            "start_time": now + datetime.timedelta(hours=5),
            "status": "UPCOMING"
        },
        {
            "id": "match_lal_gsw",
            "sport": "Basketball",
            "team_home": "LA Lakers",
            "team_away": "Golden State Warriors",
            "start_time": now + datetime.timedelta(hours=8),
            "status": "UPCOMING"
        },
        {
            "id": "match_alcaraz_sinner",
            "sport": "Tennis",
            "team_home": "Carlos Alcaraz",
            "team_away": "Jannik Sinner",
            "start_time": now + datetime.timedelta(hours=1),
            "status": "LIVE"
        }
    ])
    sample_matches.to_sql("matches", con=engine, if_exists="append", index=False)
    print(f"   -> Seeded {len(sample_matches)} matches.")
    
    print("========================================")
    print("DATABASE SEEDING FINISHED SUCCESSFULLY!")
    print("========================================")

if __name__ == "__main__":
    seed()
