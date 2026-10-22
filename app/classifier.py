"""Loads the trained scikit-learn pipeline and runs predictions.

Train the model first with:

    python train_model.py

The model path can be overridden with the MODEL_PATH environment variable.
"""

import os
from pathlib import Path

import joblib

DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parent.parent / "models" / "ticket_classifier.joblib"
)


class ClassifierNotReadyError(RuntimeError):
    """Raised when a prediction is requested before the model is loaded."""


class TicketClassifier:
    def __init__(self, model_path: str | Path | None = None) -> None:
        self.model_path = Path(model_path or os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH))
        self._model = None
        if self.model_path.exists():
            self.load()

    def load(self) -> None:
        self._model = joblib.load(self.model_path)

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def labels(self) -> list[str]:
        if self._model is None:
            return []
        return list(self._model.classes_)

    def predict(self, text: str) -> tuple[str, float]:
        """Return (label, confidence) for a single ticket text."""
        if self._model is None:
            raise ClassifierNotReadyError(
                f"Model not found at {self.model_path}. Run `python train_model.py` first."
            )
        label = str(self._model.predict([text])[0])
        confidence = self._confidence(text, label)
        return label, confidence

    def predict_batch(self, texts: list[str]) -> list[tuple[str, float]]:
        if self._model is None:
            raise ClassifierNotReadyError(
                f"Model not found at {self.model_path}. Run `python train_model.py` first."
            )
        labels = [str(label) for label in self._model.predict(texts)]
        if not hasattr(self._model, "predict_proba"):
            return [(label, 1.0) for label in labels]
        classes = list(self._model.classes_)
        probabilities = self._model.predict_proba(texts)
        return [
            (label, round(float(probabilities[i][classes.index(label)]), 4))
            for i, label in enumerate(labels)
        ]

    def _confidence(self, text: str, label: str) -> float:
        """Probability of the predicted class, if the model provides it."""
        if hasattr(self._model, "predict_proba"):
            probabilities = self._model.predict_proba([text])[0]
            classes = list(self._model.classes_)
            return round(float(probabilities[classes.index(label)]), 4)
        # Models without probability estimates report full confidence.
        return 1.0


# Shared instance used by the API; loaded once at import/startup time.
classifier = TicketClassifier()
