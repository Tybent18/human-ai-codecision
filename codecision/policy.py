"""Transparent intervention policies and decisions."""

from __future__ import annotations

from dataclasses import dataclass

from .agents import AIResponse, HumanResponse
from .config import ExperimentConfig, InterventionMode, PolicyName
from .tasks import ThreatEvent
from .uncertainty import UncertaintyEstimate


@dataclass(slots=True)
class Intervention:
    mode: InterventionMode
    final_decision: int
    authority_ai: float
    explanation: str
    contestable: bool
    threshold_trace: dict[str, float | bool]


def choose_intervention(
    policy: PolicyName,
    human: HumanResponse,
    ai: AIResponse,
    uncertainty: UncertaintyEstimate,
    event: ThreatEvent,
    trust: float,
    config: ExperimentConfig,
) -> Intervention:
    risk = max(ai.probability, 1 - ai.probability) * (0.55 + 0.45 * event.complexity)
    disagreement = human.decision != ai.decision
    trace: dict[str, float | bool] = {
        "human_uncertainty": uncertainty.score,
        "ai_confidence": ai.confidence,
        "predicted_risk": risk,
        "trust": trust,
        "disagreement": disagreement,
        "uncertainty_threshold": config.uncertainty_threshold,
        "confidence_threshold": config.ai_confidence_threshold,
        "critical_risk_threshold": config.critical_risk_threshold,
    }
    if policy == PolicyName.HUMAN_ONLY:
        return Intervention(
            InterventionMode.DEFER,
            human.decision,
            0.0,
            "Human-only control condition.",
            False,
            trace,
        )
    if policy == PolicyName.STATIC:
        accepts = disagreement and ai.confidence > 0.38 and human.confidence < 0.62
        final = ai.decision if accepts else human.decision
        return Intervention(
            InterventionMode.RECOMMEND,
            final,
            0.35 if accepts else 0.2,
            f"Uniform recommendation shown without behavioral adaptation. {ai.explanation}",
            True,
            trace,
        )
    if policy == PolicyName.AGGRESSIVE:
        return Intervention(
            InterventionMode.OVERRIDE,
            ai.decision,
            1.0,
            f"Automatic decision. {ai.explanation}",
            config.contestability,
            trace,
        )

    override_ready = (
        disagreement
        and uncertainty.score >= config.uncertainty_threshold
        and ai.confidence >= config.ai_confidence_threshold
        and risk >= config.critical_risk_threshold
        and ai.confidence - human.confidence >= config.override_margin
        and trust >= 0.32
    )
    if override_ready:
        why = (
            "Override threshold met: disagreement, high human uncertainty, "
            "high AI confidence, and critical predicted risk."
        )
        return Intervention(
            InterventionMode.OVERRIDE,
            ai.decision,
            0.9,
            f"{why} {ai.explanation}",
            config.contestability,
            trace,
        )
    if uncertainty.score >= config.uncertainty_threshold and ai.confidence >= 0.08:
        final = (
            ai.decision
            if disagreement and ai.confidence > human.confidence + 0.12
            else human.decision
        )
        why = "Assistance escalated because inferred uncertainty crossed the assistance threshold."
        return Intervention(
            InterventionMode.ASSIST, final, 0.55, f"{why} {ai.explanation}", True, trace
        )
    return Intervention(
        InterventionMode.RECOMMEND,
        human.decision,
        0.2,
        f"Recommendation only; override conditions were not met. {ai.explanation}",
        True,
        trace,
    )
