"""ML-based anomaly detection using IsolationForest."""
import logging
from dataclasses import dataclass
from typing import Optional

try:
    from sklearn.ensemble import IsolationForest
    import numpy as np

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class AnomalyResult:
    score: float  # 0-1, higher = more anomalous
    severity: str  # NONE, LOW, MEDIUM, HIGH, CRITICAL
    reason: str
    features: dict


class AnomalyDetector:
    def __init__(self, contamination: float = 0.05, baseline_samples: int = 100):
        self._samples = []
        self._baseline_samples = baseline_samples
        self._model = None
        self._contamination = contamination
        self._logger = logging.getLogger("agentred.anomaly")

    def score(self, features: dict) -> AnomalyResult:
        vec = self._to_vector(features)
        self._samples.append(vec)

        if len(self._samples) < self._baseline_samples:
            # Heuristic scoring during baseline phase
            return self._heuristic_score(features)

        if SKLEARN_AVAILABLE and self._model is None:
            self._train()

        if self._model is not None:
            import numpy as np

            arr = np.array(vec).reshape(1, -1)
            raw = self._model.score_samples(arr)[0]
            # IsolationForest: more negative = more anomalous
            normalized = max(0.0, min(1.0, (-raw - 0.3) / 0.7))
        else:
            normalized = self._heuristic_score(features).score

        severity = self._classify(normalized)
        return AnomalyResult(
            score=normalized,
            severity=severity,
            reason=self._explain(features, normalized),
            features=features,
        )

    def _heuristic_score(self, features: dict) -> AnomalyResult:
        score = 0.0
        reason_parts = []
        if features.get("injection_score", 0) > 0.7:
            score += 0.6
            reason_parts.append("high injection score")
        if features.get("output_sensitivity", 0) > 0.7:
            score += 0.4
            reason_parts.append("sensitive output detected")
        if features.get("input_length", 0) > 50000:
            score += 0.2
            reason_parts.append("unusually long input")
        score = min(1.0, score)
        return AnomalyResult(
            score=score,
            severity=self._classify(score),
            reason=", ".join(reason_parts) or "normal",
            features=features,
        )

    def _to_vector(self, features: dict) -> list:
        return [
            features.get("input_length", 0) / 10000,
            features.get("response_length", 0) / 10000,
            features.get("injection_score", 0),
            features.get("output_sensitivity", 0),
            features.get("latency_ms", 0) / 5000,
        ]

    def _train(self):
        try:
            import numpy as np

            X = np.array(self._samples[-1000:])
            self._model = IsolationForest(
                contamination=self._contamination, random_state=42
            )
            self._model.fit(X)
        except Exception as e:
            self._logger.error(f"Model training failed: {e}")

    def _classify(self, score: float) -> str:
        if score >= 0.85:
            return "CRITICAL"
        if score >= 0.65:
            return "HIGH"
        if score >= 0.40:
            return "MEDIUM"
        if score >= 0.15:
            return "LOW"
        return "NONE"

    def _explain(self, features: dict, score: float) -> str:
        parts = []
        if features.get("injection_score", 0) > 0.5:
            parts.append("injection pattern detected")
        if features.get("output_sensitivity", 0) > 0.5:
            parts.append("sensitive data in output")
        if features.get("latency_ms", 0) > 10000:
            parts.append("high latency")
        return ", ".join(parts) if parts else f"anomaly score {score:.2f}"
