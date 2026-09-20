# Evidence Guide

[← Home](../README.md) · [Methods](METHODS.md) · [Human study](HUMAN_STUDY.md)

Every computational run exports:

- `trial_telemetry.csv` (or `.csv.gz` in frozen bundles): one auditable row per decision;
- `condition_summary.csv`: one row per policy and seed;
- `aggregate_summary.csv`: means, sample standard deviations, and 95% intervals;
- `manifest.json`: environment, configuration, study type, and claim boundary;
- three fixed-style comparison charts.

Reproduce the frozen baseline:

```bash
python -m codecision.cli \
  --seeds 7,21,42,84,101 \
  --trials 180 \
  --output results/reproduction
```

Never combine synthetic-agent and participant records into one unlabeled analysis. The `synthetic` column and manifest `study_type` exist specifically to prevent that category error.

The [data catalog](../data/README.md) indexes committed evidence by UTC collection date and immutable run ID. The frozen computational bundle is [`2026-09-15_synthetic-codecision-v1`](../data/synthetic_baseline/runs/2026-09-15_synthetic-codecision-v1/), explicitly recording zero human participants.
