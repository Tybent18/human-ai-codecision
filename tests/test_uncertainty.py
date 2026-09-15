from codecision.agents import HumanResponse
from codecision.uncertainty import estimate_uncertainty


def test_uncertainty_increases_with_behavioral_signals() -> None:
    certain = HumanResponse(0, 0.95, 1.2, 0.02, 0, 0.1)
    uncertain = HumanResponse(0, 0.25, 9.0, 0.9, 2, 0.9)
    assert estimate_uncertainty(uncertain, 0.7).score > estimate_uncertainty(certain, 0.0).score


def test_uncertainty_is_bounded() -> None:
    response = HumanResponse(1, 0.0, 999, 99, 99, 1)
    assert 0 <= estimate_uncertainty(response, 99).score <= 1
