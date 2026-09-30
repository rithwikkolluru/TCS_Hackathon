import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple

from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.utils.config import FEATURES_DATA_DIR, MODELS_DIR, REPORTS_DIR


class FootfallModel:
    """Footfall prediction model for predicting expected customer count for time slots."""

    CAT_FEATURES = ["branch_id", "service_category", "day_of_week"]
    NUM_FEATURES = [
        "hour", "day_num", "day_of_month", "is_weekend", "is_month_end", "is_salary_day",
        "appointment_count", "employees_available", "employees_absent", "historical_arrivals",
        "previous_slot_arrivals", "previous_day_arrivals", "rolling_15min_arrivals",
        "rolling_30min_arrivals", "rolling_60min_arrivals", "rolling_wait_time", "queue_per_employee"
    ]
    TARGET = "predicted_customer_count"

    def __init__(self, model_path: Path = None):
        self.model_path = model_path or (MODELS_DIR / "footfall_model.pkl")
        self.pipeline = None

    def _build_pipeline(self) -> Pipeline:
        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), self.CAT_FEATURES),
                ("num", StandardScaler(), self.NUM_FEATURES)
            ]
        )

        model = HistGradientBoostingRegressor(
            max_iter=150,
            learning_rate=0.08,
            max_depth=8,
            random_state=42
        )

        return Pipeline([
            ("preprocessor", preprocessor),
            ("model", model)
        ])

    def train(self, df_features: pd.DataFrame) -> Dict[str, float]:
        """Trains the footfall prediction pipeline on input features."""
        X = df_features[self.CAT_FEATURES + self.NUM_FEATURES]
        y = df_features[self.TARGET]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.pipeline = self._build_pipeline()
        self.pipeline.fit(X_train, y_train)

        y_pred = self.pipeline.predict(X_test)
        metrics = self.evaluate(y_test, y_pred)

        # Save model
        joblib.dump(self.pipeline, self.model_path)

        # Save metrics
        metrics_path = REPORTS_DIR / "footfall_metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=4)

        print(f"Footfall model trained successfully. Saved to {self.model_path}")
        print(f"Metrics: MAE={metrics['MAE']:.3f}, RMSE={metrics['RMSE']:.3f}, R2={metrics['R2']:.3f}")
        return metrics

    def predict(self, input_df: pd.DataFrame) -> np.ndarray:
        """Predicts customer footfall given feature input dataframe."""
        if self.pipeline is None:
            if self.model_path.exists():
                self.pipeline = joblib.load(self.model_path)
            else:
                raise FileNotFoundError(f"Model file not found at {self.model_path}. Train the model first.")

        # Handle missing columns with default fill
        input_data = input_df.copy()
        for col in self.CAT_FEATURES:
            if col not in input_data.columns:
                input_data[col] = "Unknown" if col != "service_category" else "Other"
        for col in self.NUM_FEATURES:
            if col not in input_data.columns:
                input_data[col] = 0

        X = input_data[self.CAT_FEATURES + self.NUM_FEATURES]
        preds = self.pipeline.predict(X)
        return np.clip(preds, 0, None)  # Footfall cannot be negative

    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        mae = float(mean_absolute_error(y_true, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        r2 = float(r2_score(y_true, y_pred))
        return {"MAE": mae, "RMSE": rmse, "R2": r2}


def train_footfall_model() -> Dict[str, float]:
    features_path = FEATURES_DATA_DIR / "features_footfall.parquet"
    if not features_path.exists():
        raise FileNotFoundError("Footfall feature dataset not found. Run build_features.py first.")
    df_features = pd.read_parquet(features_path)
    model = FootfallModel()
    return model.train(df_features)


def predict_footfall(input_df: pd.DataFrame) -> np.ndarray:
    model = FootfallModel()
    return model.predict(input_df)


def evaluate_footfall_model(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    model = FootfallModel()
    return model.evaluate(y_true, y_pred)


if __name__ == "__main__":
    train_footfall_model()
