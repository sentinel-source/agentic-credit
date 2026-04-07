from __future__ import annotations

from fastapi import APIRouter

from mock_broker.models.vocabulary import (
    AttributeTypeDefinition,
    FactTypeDefinition,
    GoalTypeDefinition,
)
from mock_broker.vocabulary_data.consumer_credit import (
    ATTRIBUTE_TYPES,
    FACT_TYPES,
    GOAL_TYPES,
)

router = APIRouter()


@router.get("/fact-types", response_model=list[FactTypeDefinition])
def get_fact_types():
    return FACT_TYPES


@router.get("/attribute-types", response_model=list[AttributeTypeDefinition])
def get_attribute_types():
    return ATTRIBUTE_TYPES


@router.get("/goal-types", response_model=list[GoalTypeDefinition])
def get_goal_types():
    return GOAL_TYPES
