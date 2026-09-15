"""Consistent, publication-ready synthetic evidence charts."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

COLORS = {
    "human_only": "#93a9b8",
    "static_recommendation": "#54a6ff",
    "adaptive_codecision": "#51e0ad",
    "aggressive_automation": "#ff7d8d",
}
LABELS = {
    "human_only": "Human only",
    "static_recommendation": "Static recommendation",
    "adaptive_codecision": "Adaptive codecision",
    "aggressive_automation": "Aggressive automation",
}


def _theme(ax: plt.Axes) -> None:
    ax.set_facecolor("#0d1a29")
    ax.grid(axis="y", alpha=0.12)
    ax.spines[["top", "right"]].set_visible(False)


def create_charts(
    records: list[dict[str, object]], aggregates: list[dict[str, object]], output: Path
) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    plt.style.use("dark_background")
    policies = list(COLORS)

    fig, ax = plt.subplots(figsize=(11, 5.8), facecolor="#07111d")
    _theme(ax)
    metrics = ["accuracy", "trust_calibration", "autonomy_preservation", "collaborative_utility"]
    labels = ["Accuracy", "Trust calibration*", "Autonomy", "Utility"]
    x = np.arange(len(metrics))
    width = 0.19
    by_policy = {str(row["policy"]): row for row in aggregates}
    for index, policy in enumerate(policies):
        values = [float(by_policy[policy][f"{metric}_mean"]) for metric in metrics]
        ax.bar(x + (index - 1.5) * width, values, width, label=LABELS[policy], color=COLORS[policy])
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Normalized score")
    ax.set_title("Synthetic Policy Comparison")
    ax.legend(frameon=False, ncol=2)
    ax.text(
        0.99,
        0.02,
        "*Synthetic trust state, not participant-reported trust",
        transform=ax.transAxes,
        ha="right",
        color="#b7c7d1",
        fontsize=8,
    )
    fig.tight_layout()
    comparison = output / "policy_comparison.png"
    fig.savefig(comparison, dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor="#07111d")
    _theme(ax)
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in records:
        grouped[str(row["policy"])].append(row)
    for policy in policies:
        rows = grouped[policy]
        bins = np.array_split(rows, 12)
        accuracy = [np.mean([int(row["correct"]) for row in part]) for part in bins]
        ax.plot(range(1, 13), accuracy, lw=2.2, color=COLORS[policy], label=LABELS[policy])
    ax.axvline(9, color="#ffca6a", ls="--", alpha=0.65, label="AI shift begins")
    ax.set(
        title="Accuracy Under Late Distribution Shift",
        xlabel="Trial block",
        ylabel="Accuracy",
        ylim=(0.35, 1),
    )
    ax.legend(frameon=False, ncol=2)
    fig.tight_layout()
    shift = output / "distribution_shift.png"
    fig.savefig(shift, dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor="#07111d")
    _theme(ax)
    modes = ["defer", "recommend", "assist", "override"]
    bottom = np.zeros(len(policies))
    for mode, color in zip(modes, ["#506273", "#54a6ff", "#51e0ad", "#ff7d8d"], strict=True):
        values = []
        for policy in policies:
            rows = grouped[policy]
            values.append(np.mean([row["intervention_mode"] == mode for row in rows]))
        ax.bar(
            [LABELS[p] for p in policies], values, bottom=bottom, label=mode.title(), color=color
        )
        bottom += values
    ax.set(title="Authority Allocation by Policy", ylabel="Share of trials", ylim=(0, 1))
    ax.tick_params(axis="x", rotation=12)
    ax.legend(frameon=False, ncol=4)
    fig.tight_layout()
    authority = output / "authority_allocation.png"
    fig.savefig(authority, dpi=180)
    plt.close(fig)
    return [comparison, shift, authority]
