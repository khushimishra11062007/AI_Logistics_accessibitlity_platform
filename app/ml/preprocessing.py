from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "latitude",
    "longitude",
    "rainfall_1h",
    "rainfall_6h",
    "rainfall_24h",
    "soil_moisture",
    "slope",
    "elevation",
    "historical_landslides",
]
TARGET_COLUMN = "landslide_occurred"


def validate_dataset_columns(df: pd.DataFrame) -> None:
    required = FEATURE_COLUMNS + [TARGET_COLUMN]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")


def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        raise ValueError("Dataset is empty.")

    cleaned = df.copy()
    for column in FEATURE_COLUMNS + [TARGET_COLUMN]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned = cleaned.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN]).reset_index(drop=True)
    if cleaned.empty:
        raise ValueError("Dataset contains no valid rows after cleaning.")

    return cleaned


def build_preprocessor() -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )


def train_test_split_data(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]
    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )


def save_preprocessor(preprocessor: Pipeline, path: str | Path) -> None:
    import joblib

    joblib.dump(preprocessor, path)


def load_preprocessor(path: str | Path):
    import joblib

    return joblib.load(path)
