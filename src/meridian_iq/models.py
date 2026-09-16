"""Shared domain models used by every demo pattern."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceFact:
    iq: str
    fact: str
    value: Any
    citation: str
    confidence: str = "high"

    def as_dict(self) -> dict[str, Any]:
        return {
            "iq": self.iq,
            "fact": self.fact,
            "value": self.value,
            "citation": self.citation,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class AgentTrace:
    actor: str
    action: str
    sources: tuple[str, ...]


@dataclass
class DemoResult:
    question: str
    answer: str
    facts: list[SourceFact]
    trace: list[AgentTrace] = field(default_factory=list)
