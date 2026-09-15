"""Experiment configuration and enumerated study conditions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path


class StringEnum(str, Enum):
    """Python 3.10-compatible equivalent of :class:`enum.StrEnum`."""

    def __str__(self) -> str:
        return self.value


class PolicyName(StringEnum):
    HUMAN_ONLY = "human_only"
    STATIC = "static_recommendation"
    ADAPTIVE = "adaptive_codecision"
    AGGRESSIVE = "aggressive_automation"


class InterventionMode(StringEnum):
    DEFER = "defer"
    RECOMMEND = "recommend"
    ASSIST = "assist"
    OVERRIDE = "override"


@dataclass(slots=True)
class ExperimentConfig:
    trials_per_condition: int = 180
    seeds: tuple[int, ...] = (7, 21, 42, 84, 101)
    human_expertise: float = 0.68
    human_fatigue: float = 0.18
    ai_skill: float = 0.82
    uncertainty_threshold: float = 0.42
    ai_confidence_threshold: float = 0.25
    critical_risk_threshold: float = 0.55
    override_margin: float = 0.05
    contestability: bool = True
    output_dir: Path = Path("results/runs/latest")

    def __post_init__(self) -> None:
        for name in (
            "human_expertise",
            "human_fatigue",
            "ai_skill",
            "uncertainty_threshold",
            "ai_confidence_threshold",
            "critical_risk_threshold",
            "override_margin",
        ):
            value = getattr(self, name)
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be in [0, 1]")
        if self.trials_per_condition < 1:
            raise ValueError("trials_per_condition must be positive")
        self.output_dir = Path(self.output_dir)

    def to_dict(self) -> dict[str, object]:
        values = asdict(self)
        values["output_dir"] = str(self.output_dir)
        values["seeds"] = list(self.seeds)
        return values
