# Experimental data catalog

Committed evidence uses immutable dated run directories:

```text
data/<experiment_id>/runs/YYYY-MM-DD_<condition>-vN/
```

| UTC date | Run ID | Experiment | Participants | Status | Evidence |
|---|---|---|---:|---|---|
| 2026-09-15 | `2026-09-15_synthetic-codecision-v1` | Synthetic authority-policy baseline | 0 | Frozen computational baseline | [Open run](synthetic_baseline/runs/2026-09-15_synthetic-codecision-v1/) |

Synthetic-agent and human-participant evidence must always use separate experiment families and run directories. Dates come from generated manifests. Usability pilots, incomplete sessions, and smoke runs remain outside the committed evidence catalog.
