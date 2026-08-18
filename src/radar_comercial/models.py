from __future__ import annotations

from dataclasses import dataclass, field


REQUIRED_FIELDS = ("company", "objective", "pain_points", "signals", "risks")


@dataclass(frozen=True)
class CommercialCase:
    company: str
    objective: str
    pain_points: list[str]
    signals: list[str]
    risks: list[str]
    case_type: str = "generic"

    @classmethod
    def from_dict(cls, data: dict) -> "CommercialCase":
        missing = [field for field in REQUIRED_FIELDS if field not in data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return cls(
            company=data["company"],
            objective=data["objective"],
            pain_points=list(data["pain_points"]),
            signals=list(data["signals"]),
            risks=list(data["risks"]),
            case_type=data.get("case_type", "generic"),
        )


@dataclass(frozen=True)
class RadarReport:
    summary: str
    priority: str
    confidence: str = "media"
    score_total: int = 0
    score_breakdown: list[str] = field(default_factory=list)
    rationale: str = ""
    signals_positive: list[str] = field(default_factory=list)
    signals_risk: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    case_type: str = "generic"

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "priority": self.priority,
            "confidence": self.confidence,
            "score_total": self.score_total,
            "score_breakdown": list(self.score_breakdown),
            "rationale": self.rationale,
            "signals_positive": list(self.signals_positive),
            "signals_risk": list(self.signals_risk),
            "next_steps": list(self.next_steps),
            "case_type": self.case_type,
        }
