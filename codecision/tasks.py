"""Synthetic cybersecurity event generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np


@dataclass(slots=True)
class ThreatEvent:
    event_id: str
    failed_logins: float
    unusual_hour: float
    geo_velocity: float
    privilege_change: float
    exfiltration_signal: float
    signature_match: float
    complexity: float
    ground_truth: int
    latent_risk: float

    def features(self) -> np.ndarray:
        return np.array(
            [
                self.failed_logins,
                self.unusual_hour,
                self.geo_velocity,
                self.privilege_change,
                self.exfiltration_signal,
                self.signature_match,
            ]
        )

    def public_view(self) -> dict[str, object]:
        values = asdict(self)
        values.pop("ground_truth")
        values.pop("latent_risk")
        return values


WEIGHTS = np.array([0.75, 0.35, 0.7, 1.05, 1.35, 1.15])


def sigmoid(value: float) -> float:
    return float(1 / (1 + np.exp(-value)))


def generate_events(count: int, seed: int, shift: float = 0.0) -> list[ThreatEvent]:
    """Create reproducible ambiguous binary threat-classification trials."""
    rng = np.random.default_rng(seed)
    events = []
    for index in range(count):
        complexity = float(rng.uniform(0.05, 1.0))
        features = rng.beta(1.6 + shift, 2.4, 6)
        noise = rng.normal(0, 0.5 + complexity * 0.55)
        logit = float(features @ WEIGHTS - 2.45 + noise)
        risk = sigmoid(logit)
        truth = int(rng.random() < risk)
        events.append(
            ThreatEvent(
                event_id=f"EVT-{seed}-{index:04d}",
                failed_logins=float(features[0]),
                unusual_hour=float(features[1]),
                geo_velocity=float(features[2]),
                privilege_change=float(features[3]),
                exfiltration_signal=float(features[4]),
                signature_match=float(features[5]),
                complexity=complexity,
                ground_truth=truth,
                latent_risk=risk,
            )
        )
    return events
