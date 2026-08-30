from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from app.ml.create_demo_dataset import create_demo_dataset
from app.ml.model import MODEL_PATH, SCALER_PATH
from app.ml.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN, build_preprocessor, prepare_dataset, save_preprocessor, train_test_split_data, validate_dataset_columns

DATASET_PATH = Path(__file__).resolve().parents[2] / "data" / "training" / "landslide_demo_dataset.csv"


def _find_or_create_dataset() -> Path:
    if DATASET_PATH.exists():
        return DATASET_PATH
    create_demo_dataset(DATASET_PATH)
    return DATASET_PATH


def train_model(dataset_path: str | Path | None = None):
    dataset_path = Path(dataset_path) if dataset_path is not None else _find_or_create_dataset()
    df = pd.read_csv(dataset_path)
    validate_dataset_columns(df)
    cleaned = prepare_dataset(df)

    X_train, X_test, y_train, y_test = train_test_split_data(cleaned, test_size=0.2, random_state=42)

    preprocessor = build_preprocessor()
    X_train_scaled = preprocessor.fit_transform(X_train)
    X_test_scaled = preprocessor.transform(X_test)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.unlink(missing_ok=True)
    SCALER_PATH.unlink(missing_ok=True)

    import joblib

    joblib.dump(model, MODEL_PATH)
    save_preprocessor(preprocessor, SCALER_PATH)

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print("Confusion Matrix:")
    print(cm)

    importances = model.feature_importances_
    print("Feature Importance:")
    for feature, importance in zip(FEATURE_COLUMNS, importances):
        print(f"- {feature}: {importance:.4f}")

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": cm.tolist(),
        "feature_importance": {feature: float(importance) for feature, importance in zip(FEATURE_COLUMNS, importances)},
    }


if __name__ == "__main__":
    train_model()
