import os
import json
import joblib
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, average_precision_score

from backend.ml.feature_engineering import generate_features_and_labels_from_chunk

def train_and_evaluate():
    print("Loading preprocessed dataset...")
    data_path = 'data/processed/SB_Player_processed_events.csv'
    
    # Read a chunk (200k rows) to prevent OOM and allow fast iteration
    # Ensure we don't cut a session in half by finding the last full session in the chunk
    df = pd.read_csv(data_path, nrows=200000)
    last_session = df.iloc[-1]["session_id"]
    df = df[df["session_id"] != last_session]
    
    print(f"Loaded {len(df)} events. Generating features...")
    features_df = generate_features_and_labels_from_chunk(df)
    
    # Temporal Split (earliest -> latest based on chronological rows)
    n_samples = len(features_df)
    train_end = int(n_samples * 0.70)
    val_end = int(n_samples * 0.85)
    
    train_df = features_df.iloc[:train_end]
    val_df = features_df.iloc[train_end:val_end]
    test_df = features_df.iloc[val_end:]
    
    print(f"Split: Train {len(train_df)}, Val {len(val_df)}, Test {len(test_df)}")
    
    feature_cols = [
        "unique_sports_so_far", "unique_matches_so_far", 
        "is_prematch", "is_live", "is_lottery"
    ]
    
    X_train = train_df[feature_cols]
    X_test = test_df[feature_cols]
    
    metrics = {}
    os.makedirs('backend/ml/artifacts', exist_ok=True)
    
    # 1. Abandonment Model
    print("Training Abandonment Model...")
    y_train_ab = train_df["target_abandonment"]
    y_test_ab = test_df["target_abandonment"]
    
    clf_ab = LogisticRegression(random_state=42, max_iter=1000)
    clf_ab.fit(X_train, y_train_ab)
    
    y_pred_ab = clf_ab.predict(X_test)
    y_prob_ab = clf_ab.predict_proba(X_test)[:, 1]
    
    metrics["abandonment_model"] = {
        "test_samples": len(y_test_ab),
        "roc_auc": float(roc_auc_score(y_test_ab, y_prob_ab)),
        "pr_auc": float(average_precision_score(y_test_ab, y_prob_ab)),
        "precision": float(precision_score(y_test_ab, y_pred_ab)),
        "recall": float(recall_score(y_test_ab, y_pred_ab)),
        "f1": float(f1_score(y_test_ab, y_pred_ab))
    }
    joblib.dump(clf_ab, 'backend/ml/artifacts/abandonment_model.joblib')
    
    # 2. Continuation Model
    # Continuation is the exact inverse of abandonment for training, 
    # but we train it as requested to have a dedicated artifact.
    print("Training Continuation Model...")
    y_train_cont = train_df["target_continuation"]
    y_test_cont = test_df["target_continuation"]
    
    clf_cont = LogisticRegression(random_state=42, max_iter=1000)
    clf_cont.fit(X_train, y_train_cont)
    
    y_prob_cont = clf_cont.predict_proba(X_test)[:, 1]
    
    metrics["continuation_model"] = {
        "test_samples": len(y_test_cont),
        "roc_auc": float(roc_auc_score(y_test_cont, y_prob_cont)),
        "pr_auc": float(average_precision_score(y_test_cont, y_prob_cont))
    }
    joblib.dump(clf_cont, 'backend/ml/artifacts/continuation_model.joblib')
    
    # 3. Next Intent Model
    print("Training Next Intent Model...")
    # Filter to only examples where the session continued (target != UNKNOWN)
    train_intent_df = train_df[train_df["target_intent"] != "UNKNOWN"]
    test_intent_df = test_df[test_df["target_intent"] != "UNKNOWN"]
    
    X_train_intent = train_intent_df[feature_cols]
    y_train_intent = train_intent_df["target_intent"]
    X_test_intent = test_intent_df[feature_cols]
    y_test_intent = test_intent_df["target_intent"]
    
    clf_intent = HistGradientBoostingClassifier(random_state=42)
    clf_intent.fit(X_train_intent, y_train_intent)
    
    y_pred_intent = clf_intent.predict(X_test_intent)
    
    metrics["intent_model"] = {
        "test_samples": len(y_test_intent),
        "accuracy": float(accuracy_score(y_test_intent, y_pred_intent)),
        "macro_f1": float(f1_score(y_test_intent, y_pred_intent, average="macro")),
        "precision": float(precision_score(y_test_intent, y_pred_intent, average="macro", zero_division=0)),
        "recall": float(recall_score(y_test_intent, y_pred_intent, average="macro", zero_division=0))
    }
    joblib.dump(clf_intent, 'backend/ml/artifacts/intent_model.joblib')
    
    # Save metrics and metadata
    with open('backend/ml/artifacts/model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
        
    metadata = {
        "version": "v1",
        "training_timestamp": datetime.utcnow().isoformat(),
        "feature_list": feature_cols,
        "dataset_date_range": "historical",
        "training_samples": len(X_train),
        "validation_samples": len(val_df),
        "test_samples": len(X_test)
    }
    with open('backend/ml/artifacts/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
        
    print("Training complete! Artifacts saved to backend/ml/artifacts/")
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    train_and_evaluate()
