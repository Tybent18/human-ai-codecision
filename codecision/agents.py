"""Synthetic human and AI collaborators used for computational validation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .tasks import ThreatEvent, sigmoid


@dataclass(slots=True)
class HumanResponse:
    decision: int
    confidence: float
    latency_seconds: float
    hesitation: float
    revisions: int
    workload: float


@dataclass(slots=True)
class AIResponse:
    decision: int
    probability: float
    confidence: float
    entropy: float
    explanation: str


class SimulatedHuman:
    def __init__(self, expertise: float, fatigue: float, seed: int) -> None:
        self.expertise = expertise
        self.fatigue = fatigue
        self.rng = np.random.default_rng(seed)
        self.recent_errors: list[int] = []

    def decide(self, event: ThreatEvent) -> HumanResponse:
        signal = event.latent_risk
        noise_scale = 0.68 - 0.42 * self.expertise + 0.3 * self.fatigue + 0.24 * event.complexity
        perceived = float(np.clip(signal + self.rng.normal(0, noise_scale), 0, 1))
        decision = int(perceived >= 0.5)
        margin = abs(perceived - 0.5) * 2
        confidence = float(np.clip(0.38 + 0.58 * margin - 0.25 * event.complexity, 0.05, 0.98))
        hesitation = float(
            np.clip(event.complexity * (1 - confidence) + self.rng.normal(0.08, 0.05), 0, 1)
        )
        latency = float(
            np.clip(
                1.2 + 5.2 * event.complexity + 3.1 * hesitation + self.rng.normal(0, 0.5), 0.4, 15
            )
        )
        revisions = int(self.rng.random() < hesitation * 0.5) + int(
            self.rng.random() < hesitation * 0.18
        )
        workload = float(
            np.clip(0.55 * event.complexity + 0.3 * hesitation + 0.15 * self.fatigue, 0, 1)
        )
        return HumanResponse(decision, confidence, latency, hesitation, revisions, workload)

    def observe(self, correct: bool) -> None:
        self.recent_errors.append(int(not correct))
        self.recent_errors = self.recent_errors[-12:]

    @property
    def recent_error_rate(self) -> float:
        return float(np.mean(self.recent_errors)) if self.recent_errors else 0.25


class SimulatedAI:
    def __init__(self, skill: float, seed: int) -> None:
        self.skill = skill
        self.rng = np.random.default_rng(seed)

    def decide(self, event: ThreatEvent, shifted: bool = False) -> AIResponse:
        shift_penalty = 0.24 if shifted else 0.0
        noise = self.rng.normal(0, 0.38 + (1 - self.skill) * 0.85 + shift_penalty)
        score = float(event.features() @ np.array([0.7, 0.25, 0.62, 0.95, 1.2, 1.05]) - 2.2 + noise)
        probability = sigmoid(score)
        decision = int(probability >= 0.5)
        entropy = 0.0
        for p in (probability, 1 - probability):
            entropy -= p * np.log(max(p, 1e-12))
        confidence = float(1 - entropy / np.log(2))
        strongest = int(np.argmax(event.features()))
        labels = [
            "failed logins",
            "unusual access time",
            "geographic velocity",
            "privilege change",
            "exfiltration signal",
            "signature match",
        ]
        explanation = (
            f"Prediction driven most strongly by {labels[strongest]}; "
            f"calibrated confidence {confidence:.0%}."
        )
        return AIResponse(decision, probability, confidence, float(entropy), explanation)
