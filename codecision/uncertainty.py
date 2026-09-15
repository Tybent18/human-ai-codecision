"""Behavioral human-uncertainty estimation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .agents import HumanResponse


@dataclass(slots=True)
class UncertaintyEstimate:
    score: float
    latency_component: float
    hesitation_component: float
    revision_component: float
    error_component: float
    self_report_component: float


def estimate_uncertainty(response: HumanResponse, recent_error_rate: float) -> UncertaintyEstimate:
    latency = float(np.clip((response.latency_seconds - 1) / 10, 0, 1))
    hesitation = float(np.clip(response.hesitation, 0, 1))
    revisions = float(np.clip(response.revisions / 2, 0, 1))
    errors = float(np.clip(recent_error_rate, 0, 1))
    self_report = 1 - response.confidence
    values = np.array([latency, hesitation, revisions, errors, self_report])
    weights = np.array([0.20, 0.22, 0.13, 0.18, 0.27])
    score = float(np.clip(values @ weights, 0, 1))
    return UncertaintyEstimate(score, latency, hesitation, revisions, errors, self_report)
