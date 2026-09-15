from codecision.agents import AIResponse, HumanResponse
from codecision.config import ExperimentConfig, InterventionMode, PolicyName
from codecision.policy import choose_intervention
from codecision.tasks import ThreatEvent
from codecision.uncertainty import UncertaintyEstimate


def fixtures():
    human = HumanResponse(0, 0.2, 9, 0.9, 2, 0.8)
    ai = AIResponse(1, 0.99, 0.92, 0.08, "High-risk evidence.")
    event = ThreatEvent("x", 1, 1, 1, 1, 1, 1, 1, 1, 0.99)
    uncertainty = UncertaintyEstimate(0.9, 0.8, 0.9, 1, 0.7, 0.8)
    return human, ai, event, uncertainty


def test_adaptive_override_requires_complete_safety_gate() -> None:
    human, ai, event, uncertainty = fixtures()
    result = choose_intervention(
        PolicyName.ADAPTIVE, human, ai, uncertainty, event, 0.7, ExperimentConfig()
    )
    assert result.mode == InterventionMode.OVERRIDE
    assert result.contestable


def test_low_trust_blocks_adaptive_override() -> None:
    human, ai, event, uncertainty = fixtures()
    result = choose_intervention(
        PolicyName.ADAPTIVE, human, ai, uncertainty, event, 0.1, ExperimentConfig()
    )
    assert result.mode != InterventionMode.OVERRIDE


def test_human_only_never_transfers_authority() -> None:
    human, ai, event, uncertainty = fixtures()
    result = choose_intervention(
        PolicyName.HUMAN_ONLY, human, ai, uncertainty, event, 0.7, ExperimentConfig()
    )
    assert result.final_decision == human.decision
    assert result.authority_ai == 0
