"""Collaborative performance and calibration metrics."""

from __future__ import annotations

from collections import defaultdict

import numpy as np


def summarize(records: list[dict[str, object]]) -> dict[str, float | int | str]:
    if not records:
        raise ValueError("cannot summarize an empty record set")
    intervention = [r for r in records if r["intervention_mode"] in {"assist", "override"}]
    overrides = [r for r in records if r["intervention_mode"] == "override"]
    reliance = [r for r in records if int(r["ai_decision"]) != int(r["human_decision"])]
    correct_reliance = [r for r in reliance if int(r["ai_correct"]) and int(r["accepted"])]
    trust_error = [abs(float(r["trust_after"]) - float(r["ai_correct"])) for r in records]
    accuracy = float(np.mean([int(r["correct"]) for r in records]))
    latency = float(np.mean([float(r["latency_seconds"]) for r in records]))
    autonomy = 1 - float(np.mean([float(r["authority_ai"]) for r in records]))
    trust_calibration = 1 - float(np.mean(trust_error))
    efficiency = 1 / (1 + latency / 5)
    unnecessary_rate = float(np.mean([int(r["unnecessary_override"]) for r in records]))
    utility = (
        0.42 * accuracy
        + 0.22 * trust_calibration
        + 0.18 * efficiency
        + 0.18 * autonomy
        - 0.25 * unnecessary_rate
    )
    return {
        "policy": str(records[0]["policy"]),
        "seed": int(records[0]["seed"]),
        "trials": len(records),
        "accuracy": accuracy,
        "human_accuracy": float(np.mean([int(r["human_correct"]) for r in records])),
        "ai_accuracy": float(np.mean([int(r["ai_correct"]) for r in records])),
        "mean_latency_seconds": latency,
        "intervention_rate": len(intervention) / len(records),
        "override_rate": len(overrides) / len(records),
        "unnecessary_override_rate": unnecessary_rate,
        "contest_rate": sum(int(r["contested"]) for r in overrides) / max(1, len(overrides)),
        "appropriate_reliance": len(correct_reliance) / max(1, len(reliance)),
        "final_trust": float(records[-1]["trust_after"]),
        "trust_calibration": trust_calibration,
        "autonomy_preservation": autonomy,
        "collaborative_utility": utility,
    }


def aggregate(summaries: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in summaries:
        grouped[str(row["policy"])].append(row)
    metrics = [
        "accuracy",
        "mean_latency_seconds",
        "intervention_rate",
        "override_rate",
        "unnecessary_override_rate",
        "appropriate_reliance",
        "final_trust",
        "trust_calibration",
        "autonomy_preservation",
        "collaborative_utility",
    ]
    output = []
    for policy, rows in grouped.items():
        item: dict[str, object] = {"policy": policy, "seeds": len(rows)}
        for metric in metrics:
            values = np.array([float(row[metric]) for row in rows])
            item[f"{metric}_mean"] = float(values.mean())
            item[f"{metric}_sd"] = float(values.std(ddof=1)) if len(values) > 1 else 0.0
            item[f"{metric}_ci95"] = (
                float(1.96 * values.std(ddof=1) / np.sqrt(len(values))) if len(values) > 1 else 0.0
            )
        output.append(item)
    return output
