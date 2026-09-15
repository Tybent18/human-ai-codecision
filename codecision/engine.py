"""Auditable sequential codecision engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .agents import AIResponse, HumanResponse
from .config import ExperimentConfig, InterventionMode, PolicyName
from .policy import Intervention, choose_intervention
from .tasks import ThreatEvent
from .trust import update_trust
from .uncertainty import UncertaintyEstimate, estimate_uncertainty


@dataclass(slots=True)
class DecisionRecord:
    event_id: str
    policy: str
    seed: int
    trial: int
    complexity: float
    ground_truth: int
    human_decision: int
    human_confidence: float
    ai_decision: int
    ai_probability: float
    ai_confidence: float
    uncertainty: float
    intervention_mode: str
    authority_ai: float
    final_decision: int
    correct: int
    human_correct: int
    ai_correct: int
    latency_seconds: float
    hesitation: float
    revisions: int
    workload: float
    trust_before: float
    trust_after: float
    accepted: int
    contested: int
    unnecessary_override: int
    explanation: str
    synthetic: int = 1

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class CodecisionEngine:
    def __init__(self, config: ExperimentConfig, policy: PolicyName, seed: int) -> None:
        self.config = config
        self.policy = policy
        self.seed = seed
        self.trust = 0.55
        self.rng = np.random.default_rng(seed + 9000)

    def process(
        self,
        event: ThreatEvent,
        human_response: HumanResponse,
        ai_response: AIResponse,
        recent_error_rate: float,
        trial: int,
        simulate_contest: bool = True,
    ) -> tuple[DecisionRecord, Intervention, UncertaintyEstimate]:
        uncertainty = estimate_uncertainty(human_response, recent_error_rate)
        intervention = choose_intervention(
            self.policy,
            human_response,
            ai_response,
            uncertainty,
            event,
            self.trust,
            self.config,
        )
        contested = False
        accepted = True
        final_decision = intervention.final_decision
        if (
            simulate_contest
            and intervention.mode == InterventionMode.OVERRIDE
            and intervention.contestable
        ):
            contest_probability = np.clip(
                0.12 + 0.52 * human_response.confidence - 0.28 * self.trust, 0.02, 0.72
            )
            contested = bool(self.rng.random() < contest_probability)
            if contested:
                accepted = False
                final_decision = human_response.decision
        trust_before = self.trust
        intervention_occurred = intervention.mode in {
            InterventionMode.ASSIST,
            InterventionMode.OVERRIDE,
        }
        self.trust = update_trust(
            self.trust,
            ai_response.decision == event.ground_truth,
            intervention_occurred,
            accepted,
        )
        unnecessary = int(
            intervention.mode == InterventionMode.OVERRIDE
            and human_response.decision == event.ground_truth
            and ai_response.decision != event.ground_truth
        )
        record = DecisionRecord(
            event_id=event.event_id,
            policy=self.policy.value,
            seed=self.seed,
            trial=trial,
            complexity=event.complexity,
            ground_truth=event.ground_truth,
            human_decision=human_response.decision,
            human_confidence=human_response.confidence,
            ai_decision=ai_response.decision,
            ai_probability=ai_response.probability,
            ai_confidence=ai_response.confidence,
            uncertainty=uncertainty.score,
            intervention_mode=intervention.mode.value,
            authority_ai=intervention.authority_ai,
            final_decision=final_decision,
            correct=int(final_decision == event.ground_truth),
            human_correct=int(human_response.decision == event.ground_truth),
            ai_correct=int(ai_response.decision == event.ground_truth),
            latency_seconds=human_response.latency_seconds,
            hesitation=human_response.hesitation,
            revisions=human_response.revisions,
            workload=human_response.workload,
            trust_before=trust_before,
            trust_after=self.trust,
            accepted=int(accepted),
            contested=int(contested),
            unnecessary_override=unnecessary,
            explanation=intervention.explanation,
        )
        return record, intervention, uncertainty
