import os
import joblib
import pandas as pd
from typing import Dict, Any, Tuple

class ModelRegistry:
    _instance = None
    _models = {}
    _metadata = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance._load_models()
        return cls._instance
        
    def _load_models(self):
        base_dir = os.path.join(os.path.dirname(__file__), 'artifacts')
        
        try:
            self._models['abandonment'] = joblib.load(os.path.join(base_dir, 'abandonment_model.joblib'))
            self._models['continuation'] = joblib.load(os.path.join(base_dir, 'continuation_model.joblib'))
            self._models['intent'] = joblib.load(os.path.join(base_dir, 'intent_model.joblib'))
            
            import json
            with open(os.path.join(base_dir, 'model_metadata.json'), 'r') as f:
                self._metadata = json.load(f)
                
            self.version = self._metadata.get('version', 'v1')
            self.feature_cols = self._metadata.get('feature_list', [])
        except Exception as e:
            print(f"Warning: ML models failed to load. Using heuristic fallbacks. Error: {e}")
            self._models = {}
            self.version = "heuristic_fallback"
            
    def get_version(self) -> str:
        return self.version
        
    def is_loaded(self) -> bool:
        return len(self._models) == 3
        
    def predict(self, features: Dict[str, Any]) -> Tuple[float, float, str, float, Dict[str, float]]:
        if not self.is_loaded():
            raise ValueError("Models not loaded")
            
        # Prepare dataframe in the exact format used during training
        df = pd.DataFrame([features])
        X = df[self.feature_cols]
        
        # Abandonment & Continuation
        prob_abandonment = float(self._models['abandonment'].predict_proba(X)[0][1])
        prob_continuation = float(self._models['continuation'].predict_proba(X)[0][1])
        
        # Intent
        intent_probs = self._models['intent'].predict_proba(X)[0]
        classes = self._models['intent'].classes_
        
        probs_dict = {str(classes[i]): float(intent_probs[i]) for i in range(len(classes))}
        
        best_intent = str(classes[intent_probs.argmax()])
        best_conf = float(intent_probs.max())
        
        return prob_abandonment, prob_continuation, best_intent, best_conf, probs_dict
