"""Bounded asymmetric trust dynamics."""

from __future__ import annotations

import math


def logit(value: float) -> float:
    clipped = min(max(value, 1e-6), 1 - 1e-6)
    return math.log(clipped / (1 - clipped))


def update_trust(
    trust: float,
    ai_was_correct: bool,
    intervention_occurred: bool,
    accepted: bool,
    positive_rate: float = 0.18,
    failure_rate: float = 0.42,
) -> float:
    """Failures decrease trust more strongly than successes increase it."""
    if not intervention_occurred:
        return trust
    delta = positive_rate if ai_was_correct else -failure_rate
    if not accepted:
        delta *= 0.35
    return float(1 / (1 + math.exp(-(logit(trust) + delta))))
