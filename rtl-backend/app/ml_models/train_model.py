import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

# Generate synthetic dataset
np.random.seed(42)

data_size = 1000

data = {
    "num_modules": np.random.randint(1, 5, data_size),
    "num_always_blocks": np.random.randint(0, 10, data_size),
    "num_if": np.random.randint(0, 15, data_size),
    "num_case": np.random.randint(0, 8, data_size),
    "num_loops": np.random.randint(0, 5, data_size),
    "num_assignments": np.random.randint(1, 30, data_size),
    "code_length": np.random.randint(10, 500, data_size),
}

df = pd.DataFrame(data)

# Define synthetic risk logic for labeling
def label_risk(row):
    complexity = row["num_if"] + row["num_case"] + row["num_loops"]
    if complexity < 5:
        return "Low"
    elif complexity < 12:
        return "Medium"
    else:
        return "High"

df["risk"] = df.apply(label_risk, axis=1)

# Split features and target
X = df.drop("risk", axis=1)
y = df["risk"]

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# Save model
joblib.dump(model, "classical_model.pkl")

print("Model trained and saved as classical_model.pkl")
