"""KL-divergence drift detector — distinguishes benign from adversarial drift."""
import math
import statistics
from dataclasses import dataclass
from collections import deque
from typing import List, Optional


@dataclass
class KLDriftResult:
    is_drifting: bool
    kl_divergence: float
    drift_type: str  # "benign" | "adversarial" | "unknown"
    affected_features: List[str]
    confidence: float


def kl_divergence(p: List[float], q: List[float], bins: int = 20) -> float:
    """KL(P || Q) — measure how P diverges from baseline Q."""
    if not p or not q:
        return 0.0
    min_v = min(min(p), min(q))
    max_v = max(max(p), max(q)) + 1e-9

    def histogram(data):
        counts = [0] * bins
        for x in data:
            idx = min(int((x - min_v) / (max_v - min_v) * bins), bins - 1)
            counts[idx] += 1
        total = sum(counts) + 1e-9
        return [c / total + 1e-10 for c in counts]

    ph = histogram(p)
    qh = histogram(q)
    return sum(pi * math.log(pi / qi) for pi, qi in zip(ph, qh))


class DriftDetector:
    def __init__(self, threshold: float = 0.3, window: int = 200):
        self._baseline: deque = deque(maxlen=window * 5)
        self._recent: deque = deque(maxlen=window)
        self._threshold = threshold
        self._features = [
            "input_length",
            "response_length",
            "injection_score",
            "output_sensitivity",
            "latency_ms",
        ]

    def update(self, features: dict):
        self._baseline.append(features)
        self._recent.append(features)

    def check(self) -> Optional[KLDriftResult]:
        if len(self._baseline) < 100 or len(self._recent) < 20:
            return None

        drifted = []
        kl_scores = []
        for feat in self._features:
            base = [r.get(feat, 0) for r in self._baseline]
            recent = [r.get(feat, 0) for r in self._recent]
            kl = kl_divergence(recent, base)
            kl_scores.append(kl)
            if kl > self._threshold:
                drifted.append(feat)

        max_kl = max(kl_scores) if kl_scores else 0.0

        if not drifted:
            return None

        # Adversarial drift: injection_score or output_sensitivity spiking
        drift_type = "adversarial" if any(
            f in drifted for f in ["injection_score", "output_sensitivity"]
        ) else "benign"

        return KLDriftResult(
            is_drifting=True,
            kl_divergence=max_kl,
            drift_type=drift_type,
            affected_features=drifted,
            confidence=min(1.0, max_kl / (self._threshold * 2)),
        )
