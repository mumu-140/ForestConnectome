from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(slots=True)
class IsotonicConfidenceCalibrator:
    """Post-hoc probability calibration using scikit-learn's IsotonicRegression.

    Raw LLM self-confidence is kept as an input signal only. The fitted output is
    a calibrated empirical probability on a held-out, human-labelled benchmark.
    """

    out_of_bounds: str = "clip"
    _model: object | None = field(default=None, init=False, repr=False)

    def fit(self, raw_scores: Iterable[float], labels: Iterable[int]) -> "IsotonicConfidenceCalibrator":
        try:
            from sklearn.isotonic import IsotonicRegression
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Install forestconnectome[calibration] to calibrate confidence") from exc

        x = list(raw_scores)
        y = list(labels)
        if len(x) != len(y) or len(x) < 2:
            raise ValueError("raw_scores and labels must have equal length >= 2")
        if any(label not in {0, 1} for label in y):
            raise ValueError("labels must be binary 0/1")
        self._model = IsotonicRegression(out_of_bounds=self.out_of_bounds).fit(x, y)
        return self

    def predict(self, raw_scores: Iterable[float]) -> list[float]:
        if self._model is None:
            raise RuntimeError("calibrator has not been fitted")
        return [float(value) for value in self._model.predict(list(raw_scores))]
