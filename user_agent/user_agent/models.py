"""Pydantic models matching the broker's wire format.

Independently defined — no imports from mock_broker.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


# --- Enums ---

class CaseStatus(str, Enum):
    open = "open"
    transferred = "transferred"
    withdrawn = "withdrawn"
    declined = "declined"
    abandoned = "abandoned"
    expired = "expired"


class EventType(str, Enum):
    profile_updated = "profile_updated"
    goals_updated = "goals_updated"
    plans_ready = "plans_ready"
    plans_revised = "plans_revised"
    offers_ready = "offers_ready"
    offers_revised = "offers_revised"
    case_status_changed = "case_status_changed"


class ActionType(str, Enum):
    information_request = "information_request"
    disclosure = "disclosure"
    consent = "consent"
    declaration = "declaration"
    instruction = "instruction"
    case_outcome = "case_outcome"


class ResponseExpectation(str, Enum):
    provide = "provide"
    acknowledge = "acknowledge"
    grant_or_refuse = "grant_or_refuse"
    affirm_or_deny = "affirm_or_deny"
    authorise = "authorise"
    none = "none"


class ResolutionType(str, Enum):
    acknowledged = "acknowledged"
    granted = "granted"
    refused = "refused"
    affirmed = "affirmed"
    denied = "denied"
    authorised = "authorised"


class Operator(str, Enum):
    eq = "eq"
    gte = "gte"
    lte = "lte"
    approx = "approx"
    between = "between"


class InformationContext(str, Enum):
    current = "current"
    desired = "desired"


class SubjectRole(str, Enum):
    for_confirmation = "for_confirmation"
    being_authorised = "being_authorised"
    context = "context"


TERMINAL_STATUSES = {
    CaseStatus.transferred,
    CaseStatus.withdrawn,
    CaseStatus.declined,
    CaseStatus.abandoned,
    CaseStatus.expired,
}


# --- Domain entities ---

class ValueExpression(BaseModel):
    operator: Operator = Operator.eq
    value: Any
    upper: Any | None = None


class FinancialFact(BaseModel):
    id: str
    fact_type: str
    value: ValueExpression
    information_context: InformationContext = InformationContext.current
    qualifier: str | None = None
    provenance: str | None = None


class PartyAttribute(BaseModel):
    id: str
    attribute_type: str
    value: Any


class FinancialGoal(BaseModel):
    id: str
    goal_type: str
    statement: str | None = None
    desired_changes: list[FinancialFact] = []
    timeframe: str | None = None


class FinancialProfile(BaseModel):
    facts: list[FinancialFact] = []
    attributes: list[PartyAttribute] = []


class ProductFeature(BaseModel):
    name: str
    value: Any
    description: str | None = None


class SuitabilityAssessment(BaseModel):
    id: str
    suitable: bool
    reasoning: str
    factors: list[str] = []


class Recommendation(BaseModel):
    id: str
    recommended: bool
    rationale: str


class FinancialPlan(BaseModel):
    id: str
    name: str
    description: str
    steps: list[str] = []
    required_product: dict[str, Any] | None = None
    suitability_assessment: SuitabilityAssessment | None = None
    recommendation: Recommendation | None = None


class ProductOffer(BaseModel):
    id: str
    plan_id: str
    lender: str
    product_name: str
    features: list[ProductFeature] = []
    rates: dict[str, Any] = {}
    conditions: list[str] = []
    apply_url: str | None = None


# --- Broker actions ---

class ActionSubject(BaseModel):
    entity_type: str
    entity_id: str
    role: SubjectRole


class BrokerAction(BaseModel):
    id: str
    action_type: ActionType
    regulated: bool
    content: str | None = None
    response_expectation: ResponseExpectation
    subjects: list[ActionSubject] = []
    information_scope: dict[str, list[str]] | None = None
    challenge_token: str | None = None


# --- Events ---

class Event(BaseModel):
    event_type: EventType
    timestamp: datetime | None = None
    data: dict[str, Any] = {}


# --- Operation responses ---

class OpenCaseResponse(BaseModel):
    case_id: str
    events: list[Event] = []
    pending_action: BrokerAction | None = None


class OperationResponse(BaseModel):
    events: list[Event] = []
    pending_action: BrokerAction | None = None


class EvidenceEntry(BaseModel):
    timestamp: datetime | None = None
    operation: str
    data: dict[str, Any] = {}
    transcript: str | None = None
    transcript_hash: str | None = None
    challenge_token_verified: bool | None = None
    ua_version: str | None = None
    ua_version_mismatch: bool = False


class CaseState(BaseModel):
    case_id: str
    status: CaseStatus
    profile: FinancialProfile
    goals: list[FinancialGoal] = []
    plans: list[FinancialPlan] = []
    offers: list[ProductOffer] = []
    pending_action: BrokerAction | None = None
    evidence: list[EvidenceEntry] = []


# --- Vocabulary ---

class FactTypeDefinition(BaseModel):
    name: str
    description: str
    value_type: str
    typical_operators: list[str]
    examples: list[str]


class AttributeTypeDefinition(BaseModel):
    name: str
    description: str
    value_structure: str
    examples: list[str]


class GoalTypeDefinition(BaseModel):
    name: str
    description: str
    typical_desired_changes: list[str]
    examples: list[str]
