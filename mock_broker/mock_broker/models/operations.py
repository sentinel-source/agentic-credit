from __future__ import annotations

from pydantic import BaseModel

from .actions import BrokerAction
from .entities import (
    FinancialFact,
    FinancialGoal,
    FinancialPlan,
    FinancialProfile,
    PartyAttribute,
    ProductOffer,
)
from .enums import CaseStatus, ResolutionType
from .evidence import EvidenceEntryResponse
from .events import Event


class OperationResponse(BaseModel):
    events: list[Event] = []
    pending_action: BrokerAction | None = None


class OpenCaseRequest(BaseModel):
    user_id: str
    facts: list[FinancialFact] = []
    attributes: list[PartyAttribute] = []
    goals: list[FinancialGoal] = []


class OpenCaseResponse(BaseModel):
    case_id: str
    events: list[Event] = []
    pending_action: BrokerAction | None = None


class ProvideRequest(BaseModel):
    facts: list[FinancialFact] = []
    attributes: list[PartyAttribute] = []
    goals: list[FinancialGoal] = []
    transcript: str | None = None


class SelectRequest(BaseModel):
    entity_type: str
    entity_id: str
    transcript: str | None = None


class ResolveActionRequest(BaseModel):
    action_id: str
    resolution: ResolutionType
    transcript: str | None = None


class CaseState(BaseModel):
    case_id: str
    status: CaseStatus
    profile: FinancialProfile
    goals: list[FinancialGoal] = []
    plans: list[FinancialPlan] = []
    offers: list[ProductOffer] = []
    pending_action: BrokerAction | None = None
    evidence: list[EvidenceEntryResponse] = []
