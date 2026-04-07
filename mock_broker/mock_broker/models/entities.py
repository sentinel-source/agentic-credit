from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from .enums import InformationContext, Operator


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
