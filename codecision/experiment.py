"""Multi-condition synthetic validation and immutable evidence exports."""

from __future__ import annotations

import csv
import json
import platform
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from .agents import SimulatedAI, SimulatedHuman
from .config import ExperimentConfig, PolicyName
from .engine import CodecisionEngine
from .metrics import aggregate, summarize
from .tasks import generate_events

Progress = Callable[[str, float], None]


def run_condition(
    config: ExperimentConfig, policy: PolicyName, seed: int
) -> tuple[list[dict[str, object]], dict[str, object]]:
    human = SimulatedHuman(config.human_expertise, config.human_fatigue, seed + 100)
    ai = SimulatedAI(config.ai_skill, seed + 200)
    engine = CodecisionEngine(config, policy, seed)
    events = generate_events(config.trials_per_condition, seed)
    records = []
    for index, event in enumerate(events, 1):
        human_response = human.decide(event)
        ai_response = ai.decide(event, shifted=index > int(len(events) * 0.75))
        record, _, _ = engine.process(
            event, human_response, ai_response, human.recent_error_rate, index
        )
        records.append(record.to_dict())
        human.observe(bool(record.correct))
    return records, summarize(records)


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_suite(
    config: ExperimentConfig, callback: Progress | None = None
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    started = time.perf_counter()
    config.output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    conditions = list(PolicyName)
    total = len(conditions) * len(config.seeds)
    complete = 0
    for policy in conditions:
        for seed in config.seeds:
            condition_records, summary = run_condition(config, policy, seed)
            records.extend(condition_records)
            summaries.append(summary)
            complete += 1
            if callback:
                callback(f"completed {policy.value}, seed {seed}", complete / total)
    aggregates = aggregate(summaries)
    _write_csv(config.output_dir / "trial_telemetry.csv", records)
    _write_csv(config.output_dir / "condition_summary.csv", summaries)
    _write_csv(config.output_dir / "aggregate_summary.csv", aggregates)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "study_type": "synthetic computational validation",
        "human_participants": 0,
        "policies": [policy.value for policy in conditions],
        "seeds": list(config.seeds),
        "trials_per_condition": config.trials_per_condition,
        "distribution_shift_start": "final 25% of trials",
        "config": config.to_dict(),
        "runtime_seconds": time.perf_counter() - started,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "claim_boundary": (
            "Synthetic-agent results validate system behavior only; they do not measure human "
            "trust, satisfaction, cognition, or real-world safety."
        ),
    }
    (config.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return records, summaries, aggregates
