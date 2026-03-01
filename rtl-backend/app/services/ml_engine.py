import joblib
import numpy as np
import os

# Get correct path to model file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "classical_model.pkl")

# Load trained model
model = joblib.load(MODEL_PATH)


def predict_risk(features: dict):
    """
    Takes extracted RTL features and returns:
    - risk_level
    - confidence score
    """

    feature_order = [
        "num_modules",
        "num_always_blocks",
        "num_if",
        "num_case",
        "num_loops",
        "num_assignments",
        "code_length",
    ]

    X = np.array([[features[f] for f in feature_order]])

    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]

    confidence = float(np.max(probabilities))

    return prediction, confidence
