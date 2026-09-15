"""Command-line experiment runner."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

from .config import ExperimentConfig
from .experiment import run_suite
from .visualization import create_charts


def main() -> int:
    parser = argparse.ArgumentParser(description="Run synthetic codecision experiments")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--seeds", default="7,21,42,84,101")
    parser.add_argument("--trials", type=int, default=180)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output = args.output or Path("results/runs") / stamp
    seeds = (7, 42) if args.quick else tuple(int(value) for value in args.seeds.split(","))
    trials = min(args.trials, 36) if args.quick else args.trials
    config = ExperimentConfig(trials_per_condition=trials, seeds=seeds, output_dir=output)
    records, _, aggregates = run_suite(config, report)
    create_charts(records, aggregates, output)
    print(f"\nSynthetic evidence bundle written to {output}")
    return 0


def report(message: str, progress: float) -> None:
    print(f"[{progress:6.1%}] {message}")


if __name__ == "__main__":
    raise SystemExit(main())
