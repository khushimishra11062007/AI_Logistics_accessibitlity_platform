from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd

from app.ml.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN

OUTPUT_PATH = Path(__file__).resolve().parents[2] / "data" / "training" / "landslide_demo_dataset.csv"


def create_demo_dataset(output_path: str | Path = OUTPUT_PATH, rows: int = 2000, seed: int = 42) -> pd.DataFrame:
    """Create a synthetic demo dataset for landslide risk classification.

    This dataset is intentionally synthetic and should be replaced with a real landslide dataset
    when available. It is designed to mimic the environmental feature set used by NER-SAFE.
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    data = {
        "latitude": np_rng.uniform(22.5, 29.5, size=rows),
        "longitude": np_rng.uniform(89.5, 97.5, size=rows),
        "rainfall_1h": np_rng.uniform(0, 120, size=rows),
        "rainfall_6h": np_rng.uniform(0, 260, size=rows),
        "rainfall_24h": np_rng.uniform(0, 450, size=rows),
        "soil_moisture": np_rng.uniform(10, 95, size=rows),
        "slope": np_rng.uniform(5, 75, size=rows),
        "elevation": np_rng.uniform(200, 2600, size=rows),
        "historical_landslides": np_rng.integers(0, 15, size=rows),
    }

    df = pd.DataFrame(data)
    slope_factor = (df["slope"] / 70) * 0.7
    rainfall_factor = (df["rainfall_24h"] / 450) * 1.2
    soil_factor = (df["soil_moisture"] / 100) * 0.8
    historical_factor = (df["historical_landslides"] / 14) * 0.9
    hazard_score = 0.35 + rainfall_factor + slope_factor + soil_factor + historical_factor
    probability = np.clip(hazard_score / 4.0, 0.02, 0.95)

    df[TARGET_COLUMN] = (np_rng.random(rows) < probability).astype(int)

    # Add a few extreme examples to make the class structure more realistic.
    for _ in range(60):
        idx = rng.randrange(len(df))
        df.at[idx, "rainfall_24h"] = rng.uniform(250, 450)
        df.at[idx, "soil_moisture"] = rng.uniform(70, 96)
        df.at[idx, "slope"] = rng.uniform(35, 75)
        df.at[idx, "historical_landslides"] = rng.randint(4, 12)
        df.at[idx, TARGET_COLUMN] = 1

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    return df


if __name__ == "__main__":
    create_demo_dataset()
    print(f"Synthetic dataset created at: {OUTPUT_PATH}")
