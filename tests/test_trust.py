from codecision.trust import update_trust


def test_ai_failure_hurts_more_than_success_helps() -> None:
    initial = 0.5
    gain = update_trust(initial, True, True, True) - initial
    loss = initial - update_trust(initial, False, True, True)
    assert loss > gain


def test_non_intervention_does_not_change_trust() -> None:
    assert update_trust(0.61, False, False, True) == 0.61
