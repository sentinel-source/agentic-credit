from __future__ import annotations

from pydantic import BaseModel


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
