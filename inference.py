import joblib
import pandas as pd
import os
from config import MODEL_PATH

class RiskModel:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
            print("Model loaded successfully.")
        else:
            print("Model file not found. Risk scores will be default.")

    def predict(self, transaction_data):
        if not self.model:
            return 0.5 # Default risk if no model

        # Convert dict to DataFrame
        df = pd.DataFrame([transaction_data])
        
        # Ensure columns match training
        required_cols = ['amount', 'channel', 'geo', 'device_type']
        for col in required_cols:
            if col not in df.columns:
                df[col] = None # Handle missing cols

        try:
            # Predict probability of class 1 (Failure/Risk)
            prob = self.model.predict_proba(df[required_cols])[0][1]
            return prob
        except Exception as e:
            print(f"Prediction error: {e}")
            return 0.5
