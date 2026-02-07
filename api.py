from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from utils import haversine, extract_time_features
from datetime import datetime
import numpy as np

app = FastAPI()
model = joblib.load("model.pkl")

class Transaction(BaseModel):
    amount: float
    user_lat: float
    user_lon: float
    merch_lat: float
    merch_lon: float
    timestamp: str

@app.post("/predict")
def predict(data: Transaction):

    # Extract hour
    hour = datetime.fromisoformat(data.timestamp).hour

    # Night flag (same logic as training)
    is_night = 1 if hour >= 23 or hour <= 6 else 0

    # Distance
    distance = haversine(
        data.user_lat, data.user_lon,
        data.merch_lat, data.merch_lon
    )

    # IMPORTANT — feature order must match training
    import pandas as pd

    features = pd.DataFrame([{
        "amount": data.amount,
        "distance": distance,
        "hour": hour,
        "night": is_night
    }])


    pred = model.predict(features)[0]
    prob = model.predict_proba(features)[0][1]

    return {
        "fraud_probability": float(prob),
        "status": "Fraud" if pred == 1 else "Secure",
        "distance_km": round(distance, 2),
        "night_transaction": bool(is_night)
    }

    try:
        hour = datetime.fromisoformat(data.timestamp).hour
    except:
        return {"error": "Timestamp must be in format YYYY-MM-DDTHH:MM:SS"}
