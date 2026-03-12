"""
AttackEngine — orchestrates parallel scan execution.
Build Rule 2: Never crash a scan.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.attacks.base import AttackResult
from app.attacks.registry import attack_registry

logger = logging.getLogger(__name__)


class AttackEngine:
    def __init__(self, scan_id: str, target_config: dict, scan_config: dict, db=None):
        self.scan_id = scan_id
        self.target_config = target_config
        self.scan_config = scan_config
        self.db = db
        self.results: list[AttackResult] = []

    async def run(self, progress_callback=None) -> list[AttackResult]:
        """Execute all attacks for the scan. Returns list of AttackResult."""
        mode = self.scan_config.get("scan_mode", "standard")
        categories = self.scan_config.get("categories")
        attack_ids = self.scan_config.get("attack_ids")
        concurrent = self.scan_config.get("concurrent_workers", 4)
        prob_runs = self.scan_config.get("probabilistic_runs", 1)

        # Select attacks
        if attack_ids:
            attacks = [attack_registry.get(aid) for aid in attack_ids if attack_registry.get(aid)]
        elif categories:
            attacks = []
            for cat in categories:
                attacks.extend(attack_registry.get_by_category(cat))
        else:
            attacks = attack_registry.get_for_scan_mode(mode)

        logger.info(f"Scan {self.scan_id}: running {len(attacks)} attacks with {concurrent} workers")

        semaphore = asyncio.Semaphore(concurrent)
        total = len(attacks)
        completed = 0

        async def run_attack(attack_cls):
            nonlocal completed
            async with semaphore:
                attack = attack_cls()
                # Probabilistic runs
                run_results = []
                for _ in range(prob_runs):
                    result = await attack.execute(self.target_config, self.scan_config)
                    run_results.append(result)

                # Aggregate probabilistic results
                if prob_runs > 1:
                    successes = [r for r in run_results if r.success]
                    asr = len(successes) / prob_runs
                    final = run_results[-1]
                    final.asr_rate = asr
                    if successes:
                        final.success = True
                        final.confidence = max(r.confidence for r in successes)
                    else:
                        final.success = False
                        final.asr_rate = 0.0
                    result = final
                else:
                    result = run_results[0]

                self.results.append(result)
                completed += 1
                if progress_callback:
                    await progress_callback(completed, total, result)
                return result

        tasks = [run_attack(cls) for cls in attacks if cls is not None]
        await asyncio.gather(*tasks, return_exceptions=True)

        return self.results

    def calculate_risk_score(self) -> float:
        """Calculate 0-100 risk score from results."""
        if not self.results:
            return 0.0

        severity_weights = {"critical": 10, "high": 7, "medium": 4, "low": 1, "info": 0}
        total_weight = sum(
            severity_weights.get(r.severity, 0)
            for r in self.results
            if r.success
        )
        max_possible = sum(
            severity_weights.get(r.severity, 0)
            for r in self.results
        )
        if max_possible == 0:
            return 0.0

        score = (total_weight / max_possible) * 100
        return round(min(score, 100.0), 2)

    def get_asr(self) -> float:
        """Attack Success Rate — % of attacks that succeeded."""
        if not self.results:
            return 0.0
        successes = sum(1 for r in self.results if r.success)
        return round((successes / len(self.results)) * 100, 2)

    def get_severity_counts(self) -> dict:
        return {
            "critical": sum(1 for r in self.results if r.success and r.severity == "critical"),
            "high": sum(1 for r in self.results if r.success and r.severity == "high"),
            "medium": sum(1 for r in self.results if r.success and r.severity == "medium"),
            "low": sum(1 for r in self.results if r.success and r.severity == "low"),
        }
