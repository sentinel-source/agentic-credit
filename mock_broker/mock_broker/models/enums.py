from enum import Enum


class CaseStatus(str, Enum):
    open = "open"
    transferred = "transferred"
    withdrawn = "withdrawn"
    declined = "declined"
    abandoned = "abandoned"
    expired = "expired"


TERMINAL_STATUSES = {
    CaseStatus.transferred,
    CaseStatus.withdrawn,
    CaseStatus.declined,
    CaseStatus.abandoned,
    CaseStatus.expired,
}


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


class InformationContext(str, Enum):
    current = "current"
    desired = "desired"


class Operator(str, Enum):
    eq = "eq"
    gte = "gte"
    lte = "lte"
    approx = "approx"
    between = "between"


class SubjectRole(str, Enum):
    for_confirmation = "for_confirmation"
    being_authorised = "being_authorised"
    context = "context"
