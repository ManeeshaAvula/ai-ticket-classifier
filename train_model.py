"""Train the ticket classifier and save it to models/ticket_classifier.joblib.

Reads data/tickets.csv, trains a TF-IDF + LogisticRegression pipeline,
evaluates it on a held-out test split, prints the results, saves the model
with joblib, and writes the measured metrics to models/metrics.json.

Usage:
    python train_model.py
"""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "tickets.csv"
MODEL_PATH = BASE_DIR / "models" / "ticket_classifier.joblib"
METRICS_PATH = BASE_DIR / "models" / "metrics.json"
TEST_SIZE = 0.2
RANDOM_STATE = 42


def build_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )


def train(data_path: Path = DATA_PATH) -> dict:
    """Train the model and return a dict of measured evaluation metrics."""
    df = pd.read_csv(data_path)
    if not {"text", "label"}.issubset(df.columns):
        raise ValueError("Dataset must have 'text' and 'label' columns")

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["label"],
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=df["label"],
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, output_dict=True)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    metrics = {
        "accuracy": round(float(accuracy), 4),
        "dataset_rows": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "labels": sorted(df["label"].unique().tolist()),
        "per_label": {
            label: {
                "precision": round(report[label]["precision"], 4),
                "recall": round(report[label]["recall"], 4),
                "f1-score": round(report[label]["f1-score"], 4),
                "support": int(report[label]["support"]),
            }
            for label in sorted(df["label"].unique())
        },
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))

    print(f"Dataset: {len(df)} tickets ({len(X_train)} train / {len(X_test)} test)")
    print(f"Test accuracy: {accuracy:.4f}")
    print()
    print(classification_report(y_test, predictions))
    print(f"Model saved to {MODEL_PATH}")
    print(f"Metrics saved to {METRICS_PATH}")
    return metrics


if __name__ == "__main__":
    train()
