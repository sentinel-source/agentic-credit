from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from mock_broker.models.actions import BrokerAction
from mock_broker.models.entities import (
    FinancialGoal,
    FinancialPlan,
    FinancialProfile,
    ProductOffer,
)
from mock_broker.models.enums import CaseStatus
from mock_broker.models.events import Event


@dataclass
class EvidenceEntry:
    """A single entry in the case evidence log, recording an operation and its context."""

    timestamp: datetime
    operation: str
    data: dict[str, Any] = field(default_factory=dict)
    transcript: str | None = None


@dataclass
class Case:
    case_id: str
    status: CaseStatus = CaseStatus.open
    stage: int = 0
    profile: FinancialProfile = field(default_factory=FinancialProfile)
    goals: list[FinancialGoal] = field(default_factory=list)
    plans: list[FinancialPlan] = field(default_factory=list)
    offers: list[ProductOffer] = field(default_factory=list)
    pending_action: BrokerAction | None = None
    event_log: list[Event] = field(default_factory=list)
    evidence_log: list[EvidenceEntry] = field(default_factory=list)

    def record_evidence(
        self,
        operation: str,
        data: dict[str, Any] | None = None,
        transcript: str | None = None,
    ) -> None:
        self.evidence_log.append(
            EvidenceEntry(
                timestamp=datetime.now(timezone.utc),
                operation=operation,
                data=data or {},
                transcript=transcript,
            )
        )
