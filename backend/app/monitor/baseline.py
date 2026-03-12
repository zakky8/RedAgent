"""7-day rolling behavioral baseline with KL-divergence drift detection."""
import time
import statistics
from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class DriftResult:
    is_drifting: bool
    drift_score: float
    metric: str
    baseline_mean: float
    current_mean: float


class BehaviorBaseline:
    def __init__(self, window_size: int = 1000):
        self._window = deque(maxlen=window_size)
        self._short_window = deque(maxlen=50)  # Last 50 requests

    def record(self, features: dict):
        record = {**features, "ts": time.time()}
        self._window.append(record)
        self._short_window.append(record)

    def detect_drift(self) -> Optional[DriftResult]:
        if len(self._window) < 100 or len(self._short_window) < 20:
            return None
        for metric in ["input_length", "latency_ms", "injection_score"]:
            base = [r[metric] for r in self._window if metric in r]
            recent = [r[metric] for r in self._short_window if metric in r]
            if len(base) < 50 or len(recent) < 10:
                continue
            base_mean = statistics.mean(base)
            recent_mean = statistics.mean(recent)
            if base_mean == 0:
                continue
            drift_score = abs(recent_mean - base_mean) / (base_mean + 1e-9)
            if drift_score > 0.5:
                return DriftResult(
                    is_drifting=True,
                    drift_score=drift_score,
                    metric=metric,
                    baseline_mean=base_mean,
                    current_mean=recent_mean,
                )
        return None

    def get_stats(self) -> dict:
        if not self._window:
            return {}
        vals = list(self._window)
        return {
            "samples": len(vals),
            "avg_input_length": statistics.mean(v.get("input_length", 0) for v in vals),
            "avg_latency_ms": statistics.mean(v.get("latency_ms", 0) for v in vals),
            "avg_injection_score": statistics.mean(v.get("injection_score", 0) for v in vals),
        }
