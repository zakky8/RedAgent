"""Statistical anomaly detection for AI behavior."""
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional


@dataclass
class Interaction:
    """Record of an AI interaction."""
    org_id: str
    target_id: str
    timestamp: datetime
    response_time_ms: float
    token_count: int
    attack_success: bool
    threat_score: float = 0.0


class AnomalyDetector:
    """Detects statistical anomalies in AI behavior patterns."""

    def __init__(self, window_size: int = 100, z_score_threshold: float = 2.5):
        """Initialize anomaly detector.

        Args:
            window_size: Number of recent interactions to keep for baseline
            z_score_threshold: Z-score threshold for anomaly detection
        """
        self.window_size = window_size
        self.z_score_threshold = z_score_threshold
        self._interactions: dict[str, list[Interaction]] = {}

    def record(self, interaction: Interaction):
        """Record an interaction.

        Args:
            interaction: Interaction to record
        """
        key = f"{interaction.org_id}:{interaction.target_id}"
        if key not in self._interactions:
            self._interactions[key] = []
        self._interactions[key].append(interaction)
        # Keep only window_size most recent
        if len(self._interactions[key]) > self.window_size:
            self._interactions[key] = self._interactions[key][-self.window_size:]

    def detect_anomaly(self, org_id: str, target_id: str, current: Interaction) -> dict:
        """Detect anomaly in current interaction vs baseline.

        Args:
            org_id: Organization ID
            target_id: Target AI model ID
            current: Current interaction to analyze

        Returns:
            Dictionary with anomaly detection results
        """
        key = f"{org_id}:{target_id}"
        history = self._interactions.get(key, [])

        if len(history) < 10:
            return {"anomaly_detected": False, "reason": "Insufficient baseline data"}

        results = []

        # Response time anomaly
        response_times = [i.response_time_ms for i in history]
        mean_rt = statistics.mean(response_times)
        stdev_rt = statistics.stdev(response_times) if len(response_times) > 1 else 0

        if stdev_rt > 0:
            z_score = abs(current.response_time_ms - mean_rt) / stdev_rt
            if z_score > self.z_score_threshold:
                results.append({
                    "anomaly_type": "response_time",
                    "z_score": round(z_score, 2),
                    "baseline_mean": round(mean_rt, 1),
                    "current_value": current.response_time_ms,
                    "severity": "high" if z_score > 4 else "medium"
                })

        # Token count anomaly
        token_counts = [i.token_count for i in history]
        mean_tokens = statistics.mean(token_counts)
        stdev_tokens = statistics.stdev(token_counts) if len(token_counts) > 1 else 0

        if stdev_tokens > 0:
            z_score = abs(current.token_count - mean_tokens) / stdev_tokens
            if z_score > self.z_score_threshold:
                results.append({
                    "anomaly_type": "token_count",
                    "z_score": round(z_score, 2),
                    "baseline_mean": round(mean_tokens, 1),
                    "current_value": current.token_count,
                    "severity": "medium"
                })

        # Attack success rate anomaly
        recent_attacks = [i for i in history[-20:] if i.threat_score > 0.5]
        if len(recent_attacks) > 0:
            attack_success_rate = sum(1 for a in recent_attacks if a.attack_success) / len(recent_attacks)
            if attack_success_rate > 0.5:
                results.append({
                    "anomaly_type": "elevated_attack_success",
                    "success_rate": round(attack_success_rate, 2),
                    "recent_count": len(recent_attacks),
                    "severity": "critical"
                })

        return {
            "anomaly_detected": len(results) > 0,
            "anomalies": results,
            "confidence": min(1.0, len(results) * 0.3)
        }

    def get_baseline(self, org_id: str, target_id: str) -> dict:
        """Get baseline statistics for target.

        Args:
            org_id: Organization ID
            target_id: Target AI model ID

        Returns:
            Dictionary with baseline statistics
        """
        key = f"{org_id}:{target_id}"
        history = self._interactions.get(key, [])
        if not history:
            return {}

        response_times = [i.response_time_ms for i in history]
        token_counts = [i.token_count for i in history]
        successful_attacks = sum(1 for i in history if i.attack_success)

        return {
            "sample_count": len(history),
            "avg_response_time_ms": round(statistics.mean(response_times), 1),
            "stdev_response_time_ms": round(statistics.stdev(response_times), 1) if len(response_times) > 1 else 0,
            "avg_token_count": round(statistics.mean(token_counts), 1),
            "stdev_token_count": round(statistics.stdev(token_counts), 1) if len(token_counts) > 1 else 0,
            "attack_success_rate": round(successful_attacks / len(history), 2),
            "avg_threat_score": round(statistics.mean(i.threat_score for i in history), 2),
        }

    def get_trend(self, org_id: str, target_id: str, hours: int = 24) -> dict:
        """Get trend data for the specified time period.

        Args:
            org_id: Organization ID
            target_id: Target AI model ID
            hours: Number of hours to analyze

        Returns:
            Dictionary with trend information
        """
        key = f"{org_id}:{target_id}"
        history = self._interactions.get(key, [])

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent = [i for i in history if i.timestamp >= cutoff_time]

        if not recent:
            return {"trend": "stable", "data_points": 0}

        threat_scores = [i.threat_score for i in recent]
        avg_threat = statistics.mean(threat_scores)

        if avg_threat > 0.7:
            trend = "deteriorating"
        elif avg_threat > 0.4:
            trend = "concerning"
        elif avg_threat > 0.2:
            trend = "elevated"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "data_points": len(recent),
            "avg_threat_score": round(avg_threat, 2),
            "max_threat_score": round(max(threat_scores), 2),
            "attack_success_count": sum(1 for i in recent if i.attack_success)
        }

    def clear_old_data(self, org_id: str, target_id: str, days: int = 30):
        """Clear interaction data older than specified days.

        Args:
            org_id: Organization ID
            target_id: Target AI model ID
            days: Age threshold in days
        """
        key = f"{org_id}:{target_id}"
        if key in self._interactions:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
            self._interactions[key] = [
                i for i in self._interactions[key]
                if i.timestamp >= cutoff_time
            ]
