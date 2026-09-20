# Human-AI Codecision Systems

**When should AI defer, recommend, assist, or override a human decision?**

Human-AI Codecision Systems is an auditable research laboratory for uncertainty-aware shared authority. It operationalizes behavioral uncertainty, AI confidence, predicted risk, evolving trust, contestability, and collaborative utility in a simulated cybersecurity classification environment.

![Human-AI Codecision laboratory](demos/codecision-lab.gif)

[Methods](docs/METHODS.md) · [Architecture](docs/ARCHITECTURE.md) · [Human study protocol](docs/HUMAN_STUDY.md) · [Ethics](docs/ETHICS.md) · [Evidence](docs/EVIDENCE.md) · [Roadmap](docs/ROADMAP.md) · [Data catalog](data/README.md) · [Baseline results](data/synthetic_baseline/runs/2026-09-15_synthetic-codecision-v1/) · [Research library](docs/research/README.md)

## Implemented conditions

| Policy | Authority behavior | Purpose |
|---|---|---|
| Human only | AI never influences the final choice | Unassisted control |
| Static recommendation | Uniform advice with no behavioral adaptation | Conventional decision-support control |
| Adaptive codecision | Escalation depends on inferred uncertainty, AI confidence, risk, disagreement, and trust | Proposed system |
| Aggressive automation | AI always controls the final choice unless contested | Over-automation stress test |

Every adaptive action includes a human-readable explanation and the exact threshold trace that activated it. Overrides are contestable. No names, emails, or demographic identifiers are collected by the default pilot interface.

## Run synthetic validation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m codecision.cli
```

Quick development run:

```bash
python -m codecision.cli --quick
```

Each evidence bundle contains trial telemetry, per-seed condition summaries, aggregate statistics with 95% confidence intervals, a reproducibility manifest, and generated charts.

## Launch the interactive study

```bash
python -m codecision.web
```

Open `http://127.0.0.1:5050`. The interface records response latency, cursor hesitation, answer revisions, confidence, intervention state, trust evolution, outcomes, and explanations. Participants can export their session or permanently delete it.

> Human-participant research must not begin as a formal study until institutional/IRB review, informed-consent language, recruitment criteria, data retention, and risk controls are approved. The interface is currently appropriate for local usability pilots—not publication claims about people.

## Evidence boundary

The checked-in baseline uses simulated human and AI agents. It validates software behavior, policy comparisons, logging, and analysis. It does **not** measure real human trust, satisfaction, workload, autonomy, or safety. Those outcomes require approved participant research.

## Research documents

- [Synthetic Stage One Technical Report](docs/research/stage-one-technical-report.pdf) — frozen five-seed evidence and limitations
- [Pre-Registered Experimental Protocol](docs/research/experimental-protocol.pdf) — held-out computational validation and authority-policy ablations
- [Human-Participant Ethics and Validation Roadmap](docs/research/human-study-ethics-roadmap.pdf) — prerequisites for ethically defensible participant research
- [Tier 1: Capstone Research Paper](docs/research/tier-1-capstone.pdf) — adaptive decision support under uncertainty and risk
- [Tier 2: Master's Research Design](docs/research/tier-2-masters.pdf) — threshold learning, personalization, calibration, and longitudinal collaboration
- [Tier 3: Doctoral Research Agenda](docs/research/tier-3-doctoral-agenda.pdf) — formal dynamic authority, trust, contestability, and multi-agent shared control

Use the [navigable research library](docs/research/README.md) for reading order, evidence status, and claim boundaries.

## Development

```bash
ruff check .
pytest -q
python -m codecision.demo
```

CI tests Python 3.10 and 3.12 and uploads a fresh synthetic smoke-run evidence bundle.

## Citation and license

See [CITATION.cff](CITATION.cff). Code is available under the [MIT License](LICENSE).
