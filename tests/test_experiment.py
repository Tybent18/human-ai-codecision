import csv
import json

from codecision.config import ExperimentConfig, PolicyName
from codecision.experiment import run_condition, run_suite


def test_condition_is_deterministic() -> None:
    config = ExperimentConfig(trials_per_condition=12, seeds=(7,))
    first, _ = run_condition(config, PolicyName.ADAPTIVE, 7)
    second, _ = run_condition(config, PolicyName.ADAPTIVE, 7)
    assert first == second


def test_suite_exports_labeled_synthetic_evidence(tmp_path) -> None:
    config = ExperimentConfig(trials_per_condition=8, seeds=(7,), output_dir=tmp_path)
    records, summaries, aggregates = run_suite(config)
    assert len(records) == 32
    assert len(summaries) == len(PolicyName)
    assert len(aggregates) == len(PolicyName)
    assert all(int(row["synthetic"]) == 1 for row in records)
    assert len(list(csv.DictReader((tmp_path / "trial_telemetry.csv").open()))) == 32
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["human_participants"] == 0
