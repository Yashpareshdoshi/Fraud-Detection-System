import pandas as pd
import random
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from utils import haversine

# -----------------------------
# 1️⃣ Generate Synthetic Data
# -----------------------------
data = []

for _ in range(7000):
    user_lat, user_lon = 19.0760, 72.8777  # Mumbai home
    merch_lat = random.uniform(-90, 90)
    merch_lon = random.uniform(-180, 180)
    amount = random.randint(100, 100000)
    hour = random.randint(0, 23)

    distance = haversine(user_lat, user_lon, merch_lat, merch_lon)
    is_night = 1 if hour >= 23 or hour <= 6 else 0

    # Fraud logic (for training labels)
    fraud = 1 if distance > 4000 or is_night or amount > 80000 else 0

    data.append([amount, distance, hour, is_night, fraud])

# -----------------------------
# 2️⃣ Create DataFrame
# -----------------------------
columns = ["amount", "distance", "hour", "night", "fraud"]
df = pd.DataFrame(data, columns=columns)

# -----------------------------
# 3️⃣ Feature Selection
# -----------------------------
feature_cols = ["amount", "distance", "hour", "night"]
X = df[feature_cols]
y = df["fraud"]

# -----------------------------
# 4️⃣ Handle Imbalanced Data
# -----------------------------
sm = SMOTE(random_state=42)
X_res, y_res = sm.fit_resample(X, y)

# -----------------------------
# 5️⃣ Train/Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X_res, y_res, test_size=0.2, random_state=42
)

# -----------------------------
# 6️⃣ Train Model
# -----------------------------
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# -----------------------------
# 7️⃣ Evaluation
# -----------------------------
preds = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, preds))

# -----------------------------
# 8️⃣ Save Model
# -----------------------------
joblib.dump(model, "model.pkl")

print("✅ Model saved as model.pkl")

