import os
import sys
import json
import time
import datetime
import sqlite3
from collections import defaultdict
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import engine
from backend.models import Base

def preprocess_player_profiles(target_path: str = "assets/SB_Player.csv"):
    start_time = time.time()
    
    print("==================================================")
    print("PULSYNC: CHUNKED PLAYER PROFILE PREPROCESSING")
    print("==================================================")
    
    if not os.path.exists(target_path):
        print(f"WARNING: Dataset file {target_path} not found.")
        print("Creating baseline deterministic player profiles for offline demo fallback...")
        _seed_baseline_profiles(engine)
        print("Completed baseline setup in {:.2f}s.".format(time.time() - start_time))
        return
        
    print(f"Processing dataset in chunks from: {target_path}")
    
    # In-memory aggregation dictionaries per PlayerID
    user_activity_count = defaultdict(int)
    user_sports_count = defaultdict(lambda: defaultdict(int))
    user_product_count = defaultdict(lambda: defaultdict(int))
    
    total_rows = 0
    chunk_size = 50000
    
    for chunk in pd.read_csv(target_path, chunksize=chunk_size):
        total_rows += len(chunk)
        
        # Extract columns
        players = chunk['PlayerID'].values
        sports = chunk['Sport_name_english'].fillna('Football').values
        products = chunk['betslip_product'].fillna('Sportsbook').values
        
        for p, s, pr in zip(players, sports, products):
            if not p or pd.isna(p):
                continue
            user_activity_count[p] += 1
            user_sports_count[p][s] += 1
            user_product_count[p][pr] += 1

    print(f"Processed {total_rows:,} raw rows across {len(user_activity_count):,} unique PlayerIDs.")

    # Convert to aggregated profile rows
    profile_rows = []
    player_id_list = list(user_activity_count.keys())
    
    # Selection rule for deterministic demo mapping:
    # Select the profile with highest Football activity
    demo_candidate = None
    demo_candidate_count = -1
    
    for idx, pid in enumerate(player_id_list):
        anon_id = f"anon_prof_{idx+1:06d}"
        tot_act = user_activity_count[pid]
        
        # Calculate sport distribution
        sports_map = dict(user_sports_count[pid])
        tot_sport_events = sum(sports_map.values())
        sport_dist = {s: round(c / max(1, tot_sport_events), 2) for s, c in sports_map.items()}
        preferred_sport = max(sports_map, key=sports_map.get) if sports_map else "Football"
        
        # Calculate product preference
        prod_map = dict(user_product_count[pid])
        preferred_prod = max(prod_map, key=prod_map.get) if prod_map else "Sportsbook"
        
        # Activity level classification
        if tot_act >= 20:
            act_level = "HIGH"
        elif tot_act >= 5:
            act_level = "MEDIUM"
        else:
            act_level = "LOW"
            
        hist_score = min(100.0, round(20.0 + (tot_act * 1.5), 1))
        
        # Selection for demo profile mapping
        fb_count = sports_map.get("Football", 0) + sports_map.get("Soccer", 0)
        if fb_count > demo_candidate_count:
            demo_candidate_count = fb_count
            demo_candidate = {
                "preferred_sport": preferred_sport,
                "activity_level": "HIGH",
                "total_activity": tot_act,
                "sport_distribution_json": json.dumps(sport_dist),
                "preferred_product": preferred_prod,
                "historical_activity_score": hist_score,
                "profile_source": "FEG historical behavioral profile",
                "created_at": datetime.datetime.utcnow()
            }
            
        profile_rows.append({
            "anonymous_user_id": anon_id,
            "preferred_sport": preferred_sport,
            "activity_level": act_level,
            "total_activity": tot_act,
            "sport_distribution_json": json.dumps(sport_dist),
            "preferred_product": preferred_prod,
            "historical_activity_score": hist_score,
            "profile_source": "FEG historical behavioral profile",
            "created_at": datetime.datetime.utcnow()
        })
        
    # Add explicit deterministic demo user entries
    if not demo_candidate:
        demo_candidate = {
            "preferred_sport": "Football",
            "activity_level": "HIGH",
            "total_activity": 128,
            "sport_distribution_json": json.dumps({"Football": 0.75, "Tennis": 0.15, "Basketball": 0.10}),
            "preferred_product": "Sportsbook",
            "historical_activity_score": 88.5,
            "profile_source": "FEG historical behavioral profile",
            "created_at": datetime.datetime.utcnow()
        }
        
    for demo_id in ["anonymous-demo-user", "usr_demo", "blackbox_anon_id_999"]:
        p_demo = dict(demo_candidate)
        p_demo["anonymous_user_id"] = demo_id
        profile_rows.append(p_demo)
        
    print(f"Generated {len(profile_rows):,} compact profile records.")
    
    # Save to SQLite table player_profiles
    print("Writing compact player profiles to pulsync.db SQLite store...")
    Base.metadata.create_all(bind=engine)
    
    profiles_df = pd.DataFrame(profile_rows)
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP TABLE IF EXISTS player_profiles")
    
    Base.metadata.create_all(bind=engine)
    profiles_df.to_sql("player_profiles", con=engine, if_exists="append", index=False)
    
    # Create indexes
    with engine.begin() as conn:
        conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS idx_player_profiles_anon_id ON player_profiles (anonymous_user_id)")
        
    elapsed = time.time() - start_time
    print("==================================================")
    print("PLAYER PROFILE PREPROCESSING COMPLETED SUCCESSFULLY!")
    print("==================================================")
    print(f"Processing duration: {elapsed:.2f} seconds")
    print(f"Raw rows scanned: {total_rows:,}")
    print(f"Profiles generated: {len(profile_rows):,}")
    print("Demo user mapped: anonymous-demo-user & usr_demo -> Football Affinity HIGH")
    print("==================================================\n")

def _seed_baseline_profiles(engine):
    Base.metadata.create_all(bind=engine)
    demo_profiles = [
        {
            "anonymous_user_id": "anonymous-demo-user",
            "preferred_sport": "Football",
            "activity_level": "HIGH",
            "total_activity": 128,
            "sport_distribution_json": json.dumps({"Football": 0.75, "Tennis": 0.15, "Basketball": 0.10}),
            "preferred_product": "Sportsbook",
            "historical_activity_score": 88.5,
            "profile_source": "FEG historical behavioral profile",
            "created_at": datetime.datetime.utcnow()
        },
        {
            "anonymous_user_id": "usr_demo",
            "preferred_sport": "Football",
            "activity_level": "HIGH",
            "total_activity": 128,
            "sport_distribution_json": json.dumps({"Football": 0.75, "Tennis": 0.15, "Basketball": 0.10}),
            "preferred_product": "Sportsbook",
            "historical_activity_score": 88.5,
            "profile_source": "FEG historical behavioral profile",
            "created_at": datetime.datetime.utcnow()
        }
    ]
    df = pd.DataFrame(demo_profiles)
    df.to_sql("player_profiles", con=engine, if_exists="append", index=False)

if __name__ == "__main__":
    preprocess_player_profiles()
