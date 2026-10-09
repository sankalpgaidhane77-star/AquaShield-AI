"""
AquaShield AI - Machine Learning Model Training Script
Trains a Random Forest classifier to classify water quality into Safe, Moderate, or Dangerous.
Evaluates model performance and saves the trained model bundle to joblib.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

def generate_water_quality_dataset(n_samples=4500):
    """
    Generate realistic water quality dataset based on WHO/EPA standards.
    Parameters:
      - pH: 0 to 14
      - Turbidity: NTU (0 to 50+)
      - TDS: Total Dissolved Solids ppm (0 to 2500+)
      - Temperature: Celsius (5 to 45+)
    Target Classes:
      - Safe (0)
      - Moderate (1)
      - Dangerous (2)
    """
    samples_per_class = n_samples // 3
    data = []

    # 1. SAFE WATER: Meets WHO potable drinking water standards
    for _ in range(samples_per_class):
        ph = np.random.normal(loc=7.3, scale=0.35)
        ph = np.clip(ph, 6.6, 8.3)

        turbidity = np.random.exponential(scale=1.1) + 0.2
        turbidity = np.clip(turbidity, 0.1, 3.8)

        tds = np.random.normal(loc=190, scale=75)
        tds = np.clip(tds, 60.0, 440.0)

        temp = np.random.normal(loc=18.5, scale=3.5)
        temp = np.clip(temp, 10.0, 24.0)

        data.append({
            "ph": round(float(ph), 2),
            "turbidity": round(float(turbidity), 2),
            "tds": round(float(tds), 1),
            "temperature": round(float(temp), 1),
            "label": "Safe"
        })

    # 2. MODERATE WATER: Sub-optimal; requires boiling/filtration/treatment
    for _ in range(samples_per_class):
        sub_type = np.random.choice(["marginal_ph", "elevated_turbidity", "elevated_tds", "elevated_temp", "mixed"])
        if sub_type == "marginal_ph":
            # pH slightly off (6.0-6.5 or 8.4-8.9)
            ph = np.random.choice([
                np.random.uniform(6.0, 6.5),
                np.random.uniform(8.4, 8.9)
            ])
            turbidity = np.random.uniform(1.0, 4.0)
            tds = np.random.uniform(150.0, 500.0)
            temp = np.random.uniform(14.0, 26.0)
        elif sub_type == "elevated_turbidity":
            # Suspended particles needing filtration
            ph = np.random.uniform(6.6, 8.2)
            turbidity = np.random.uniform(4.1, 9.8)
            tds = np.random.uniform(150.0, 500.0)
            temp = np.random.uniform(14.0, 26.0)
        elif sub_type == "elevated_tds":
            # High mineral / brackish
            ph = np.random.uniform(6.6, 8.2)
            turbidity = np.random.uniform(1.0, 4.5)
            tds = np.random.uniform(500.0, 950.0)
            temp = np.random.uniform(14.0, 26.0)
        elif sub_type == "elevated_temp":
            # Warm water with higher bacterial activity risk
            ph = np.random.uniform(6.6, 8.2)
            turbidity = np.random.uniform(1.5, 4.5)
            tds = np.random.uniform(150.0, 480.0)
            temp = np.random.uniform(25.0, 34.0)
        else: # mixed
            ph = np.random.uniform(6.3, 8.6)
            turbidity = np.random.uniform(3.5, 8.0)
            tds = np.random.uniform(450.0, 800.0)
            temp = np.random.uniform(23.0, 32.0)

        data.append({
            "ph": round(float(ph), 2),
            "turbidity": round(float(turbidity), 2),
            "tds": round(float(tds), 1),
            "temperature": round(float(temp), 1),
            "label": "Moderate"
        })

    # 3. DANGEROUS WATER: Hazardous for consumption, industrial runoff, severe contamination
    for _ in range(samples_per_class):
        danger_type = np.random.choice([
            "acidic_runoff", "chemical_alkaline", "high_turbidity_sewage",
            "toxic_high_tds", "extreme_thermal", "multi_hazard"
        ])

        if danger_type == "acidic_runoff":
            # Highly acidic (e.g. mine drainage or acid rain)
            ph = np.random.uniform(2.5, 5.8)
            turbidity = np.random.uniform(2.0, 28.0)
            tds = np.random.uniform(300.0, 1600.0)
            temp = np.random.uniform(14.0, 32.0)
        elif danger_type == "chemical_alkaline":
            # Alkaline spill / caustic chemical contamination
            ph = np.random.uniform(9.2, 13.0)
            turbidity = np.random.uniform(2.0, 25.0)
            tds = np.random.uniform(400.0, 1800.0)
            temp = np.random.uniform(15.0, 34.0)
        elif danger_type == "high_turbidity_sewage":
            # Severe sewage / industrial suspension
            ph = np.random.uniform(5.5, 8.8)
            turbidity = np.random.uniform(10.5, 45.0)
            tds = np.random.uniform(400.0, 1500.0)
            temp = np.random.uniform(18.0, 33.0)
        elif danger_type == "toxic_high_tds":
            # Toxic mineral salt or heavy saline contamination
            ph = np.random.uniform(5.8, 9.0)
            turbidity = np.random.uniform(1.0, 18.0)
            tds = np.random.uniform(1050.0, 2400.0)
            temp = np.random.uniform(16.0, 32.0)
        elif danger_type == "extreme_thermal":
            # Severe thermal pollution
            ph = np.random.uniform(6.0, 9.0)
            turbidity = np.random.uniform(3.0, 15.0)
            tds = np.random.uniform(300.0, 1200.0)
            temp = np.random.uniform(36.0, 48.0)
        else: # multi_hazard
            ph = np.random.choice([np.random.uniform(3.0, 5.5), np.random.uniform(9.5, 12.5)])
            turbidity = np.random.uniform(11.0, 35.0)
            tds = np.random.uniform(1100.0, 2200.0)
            temp = np.random.uniform(28.0, 42.0)

        data.append({
            "ph": round(float(ph), 2),
            "turbidity": round(float(turbidity), 2),
            "tds": round(float(tds), 1),
            "temperature": round(float(temp), 1),
            "label": "Dangerous"
        })

    df = pd.DataFrame(data)
    df = df.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)
    return df

def train_and_evaluate():
    print("=" * 60)
    print("AquaShield AI - Random Forest Model Training")
    print("=" * 60)

    # 1. Generate / load dataset
    df = generate_water_quality_dataset(n_samples=4500)
    print(f"Generated dataset with {len(df)} samples.")
    print("Class distribution:\n", df['label'].value_counts())

    # Create directories
    os.makedirs("ml", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    dataset_path_ml = os.path.join("ml", "dataset.csv")
    dataset_path_data = os.path.join("data", "water_quality_training_data.csv")
    df.to_csv(dataset_path_ml, index=False)
    df.to_csv(dataset_path_data, index=False)
    print(f"Saved dataset to {dataset_path_ml} and {dataset_path_data}")

    # 2. Strict featurization ordering (split BEFORE fitting)
    feature_cols = ["ph", "turbidity", "tds", "temperature"]
    X = df[feature_cols]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_SEED, stratify=y
    )
    print(f"\nTraining set size: {X_train.shape[0]}, Test set size: {X_test.shape[0]}")

    # 3. Model Training
    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=3,
        min_samples_leaf=1,
        random_state=RANDOM_SEED,
        n_jobs=-1
    )

    # 5-fold cross-validation on train set
    cv_scores = cross_val_score(clf, X_train, y_train, cv=5, scoring="accuracy")
    print(f"5-Fold Cross-Validation Accuracy on Train set: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    clf.fit(X_train, y_train)

    # 4. Evaluation on Held-Out Test Set
    y_pred = clf.predict(X_test)
    test_acc = accuracy_score(y_test, y_pred)
    print(f"\nFinal Test Set Accuracy: {test_acc * 100:.2f}%")

    if test_acc >= 0.90:
        print("SUCCESS: Target accuracy >= 90% achieved!")
    else:
        print("WARNING: Target accuracy not reached.")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, digits=4))

    cm = confusion_matrix(y_test, y_pred, labels=["Safe", "Moderate", "Dangerous"])
    print("Confusion Matrix (Safe, Moderate, Dangerous):")
    print(cm)

    # Feature Importances
    importances = dict(zip(feature_cols, clf.feature_importances_))
    print("\nFeature Importances:")
    for feat, imp in sorted(importances.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {feat:12s}: {imp:.4f}")

    # 5. Save model bundle with metadata
    model_bundle = {
        "model": clf,
        "feature_names": feature_cols,
        "classes": list(clf.classes_),
        "metrics": {
            "test_accuracy": float(test_acc),
            "cv_accuracy_mean": float(cv_scores.mean()),
            "cv_accuracy_std": float(cv_scores.std()),
            "feature_importances": importances
        }
    }

    model_path = os.path.join("ml", "model.joblib")
    joblib.dump(model_bundle, model_path)
    print(f"\nSaved model bundle to {model_path}")

    # 6. Sanity Test with typical scenarios
    print("\n" + "=" * 60)
    print("Sanity Test Predictions:")
    test_cases = [
        {"name": "Clean Spring Water", "ph": 7.4, "turbidity": 0.8, "tds": 150.0, "temperature": 18.0},
        {"name": "High Turbidity Runoff", "ph": 7.1, "turbidity": 8.5, "tds": 320.0, "temperature": 21.0},
        {"name": "Industrial Acid Spill", "ph": 4.1, "turbidity": 14.0, "tds": 1250.0, "temperature": 29.0},
        {"name": "High TDS Brackish Well", "ph": 7.9, "turbidity": 2.1, "tds": 780.0, "temperature": 23.0},
        {"name": "Severe Alkaline Bleach", "ph": 11.2, "turbidity": 5.0, "tds": 1100.0, "temperature": 22.0},
    ]

    for tc in test_cases:
        feat_vals = pd.DataFrame([[tc["ph"], tc["turbidity"], tc["tds"], tc["temperature"]]], columns=feature_cols)
        pred_label = clf.predict(feat_vals)[0]
        probs = clf.predict_proba(feat_vals)[0]
        class_idx = list(clf.classes_).index(pred_label)
        confidence = probs[class_idx] * 100
        print(f"[{tc['name']}] -> {pred_label} ({confidence:.1f}% confidence)")

    print("=" * 60)
    return model_bundle

if __name__ == "__main__":
    train_and_evaluate()
