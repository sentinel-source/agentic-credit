"""Scripted personal loan broking journey.

Each step is a function that takes a Case and an operation request, and returns
a StepResult describing what events to emit, what pending action to set, and
what stage to advance to.

Journey stages:
  0  open_case   → InformationRequest (income, debts, loan purpose)
  1  provide     → Disclosure (broker identity)
  2  resolve(ack)→ Consent (soft credit search)
  3  resolve(grant)→ PlansReady (no gate)
  4  select(plan)→ OffersReady + Disclosure (regulated product info)
  5  resolve(ack)→ (no gate, user can select offer)
  6  select(offer)→ Declaration (info is true)
  7  resolve(affirm)→ Instruction (proceed to lender)
  8  resolve(authorise)→ CaseOutcome (transferred)
  9  terminal
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from mock_broker.models.actions import ActionSubject, BrokerAction
from mock_broker.models.entities import (
    FinancialPlan,
    ProductFeature,
    ProductOffer,
    Recommendation,
    SuitabilityAssessment,
)
from mock_broker.models.enums import (
    ActionType,
    CaseStatus,
    EventType,
    ResponseExpectation,
    SubjectRole,
)
from mock_broker.models.events import Event
from mock_broker.state.case import Case


@dataclass
class StepResult:
    events: list[Event] = field(default_factory=list)
    pending_action: BrokerAction | None = None
    advance_to: int = 0
    status: CaseStatus | None = None


def _event(event_type: EventType, data: dict[str, Any] | None = None) -> Event:
    return Event(
        event_type=event_type,
        timestamp=datetime.now(timezone.utc),
        data=data or {},
    )


# --- Stage 0: Open Case ---

def step_open_case(case: Case, request: Any) -> StepResult:
    events = []
    if request.facts:
        events.append(_event(EventType.profile_updated, {"facts": [f.model_dump() for f in request.facts]}))
    if request.goals:
        events.append(_event(EventType.goals_updated, {"goals": [g.model_dump() for g in request.goals]}))

    return StepResult(
        events=events,
        pending_action=BrokerAction(
            id="action-info-request-01",
            action_type=ActionType.information_request,
            regulated=False,
            content=(
                "To find suitable loan options, we need some information about your "
                "financial circumstances. Please provide your income, employment status, "
                "existing debts, and what you intend to use the loan for."
            ),
            response_expectation=ResponseExpectation.provide,
            information_scope={
                "required_facts": [
                    "gross_annual_income",
                    "employment_status",
                    "existing_credit_card_balance",
                    "existing_loan_balance",
                ],
                "optional_facts": [
                    "net_monthly_income",
                    "monthly_expenditure",
                    "monthly_rent_or_mortgage",
                    "number_of_dependants",
                    "monthly_loan_repayment_budget",
                ],
                "required_goals": ["loan purpose and amount"],
            },
        ),
        advance_to=1,
    )


# --- Stage 1: Provide (resolves information request) ---

def step_provide(case: Case, request: Any) -> StepResult:
    events = [
        _event(EventType.profile_updated, {
            "facts": [f.model_dump() for f in request.facts],
            "attributes": [a.model_dump() for a in request.attributes],
        }),
    ]
    if request.goals:
        events.append(_event(EventType.goals_updated, {"goals": [g.model_dump() for g in request.goals]}))

    return StepResult(
        events=events,
        pending_action=BrokerAction(
            id="action-disclosure-01",
            action_type=ActionType.disclosure,
            regulated=True,
            content=(
                "ClearCredit Solutions Ltd is authorised and regulated by the Financial "
                "Conduct Authority (FRN 789012). We act as a credit broker, not a lender. "
                "We offer products from a panel of lenders. We may receive a commission "
                "from the lender if you take out a product through us. This does not "
                "affect the amount you pay. You are under no obligation to proceed with "
                "any product we present to you."
            ),
            response_expectation=ResponseExpectation.acknowledge,
        ),
        advance_to=2,
    )


# --- Stage 2: Resolve (acknowledge disclosure) → Consent ---

def step_resolve_disclosure(case: Case, request: Any) -> StepResult:
    return StepResult(
        pending_action=BrokerAction(
            id="action-consent-01",
            action_type=ActionType.consent,
            regulated=True,
            content=(
                "We would like to perform a soft credit search to assess your "
                "eligibility for personal loan products. A soft search will not "
                "appear on your credit file and will not affect your credit score. "
                "Do you consent to this search being carried out?"
            ),
            response_expectation=ResponseExpectation.grant_or_refuse,
        ),
        advance_to=3,
    )


# --- Stage 3: Resolve (grant consent) → PlansReady ---

def _build_plans() -> list[FinancialPlan]:
    return [
        FinancialPlan(
            id="plan-01",
            name="Debt Consolidation Loan",
            description=(
                "Consolidate existing credit card and loan balances into a single "
                "fixed-rate personal loan with one monthly repayment."
            ),
            steps=[
                "Confirm total debt to consolidate",
                "Source loan offers covering total balance",
                "Select preferred offer and apply",
                "Use loan funds to clear existing debts",
            ],
            required_product={"type": "personal_loan", "purpose": "debt_consolidation"},
            suitability_assessment=SuitabilityAssessment(
                id="assess-01",
                suitable=True,
                reasoning=(
                    "Based on your income and existing debt levels, consolidating into "
                    "a single loan would reduce your total monthly repayments and provide "
                    "a clear repayment timeline. The projected interest rate is lower than "
                    "your current weighted average across existing debts."
                ),
                factors=[
                    "Debt-to-income ratio within acceptable range",
                    "Stable employment history",
                    "Projected monthly saving on repayments",
                    "Fixed end date for debt clearance",
                ],
            ),
            recommendation=Recommendation(
                id="rec-01",
                recommended=True,
                rationale=(
                    "We recommend this plan as it simplifies your finances, reduces your "
                    "monthly outgoings, and provides a fixed date by which your debt will "
                    "be fully repaid."
                ),
            ),
        ),
        FinancialPlan(
            id="plan-02",
            name="Flexible Personal Loan",
            description=(
                "A general-purpose personal loan with flexible repayment terms, "
                "suitable for a range of borrowing needs."
            ),
            steps=[
                "Confirm loan amount and preferred term",
                "Source loan offers from panel",
                "Select preferred offer and apply",
            ],
            required_product={"type": "personal_loan", "purpose": "general"},
            suitability_assessment=SuitabilityAssessment(
                id="assess-02",
                suitable=True,
                reasoning=(
                    "Your financial profile supports a personal loan of the requested "
                    "amount. Monthly repayments would be within your stated budget, "
                    "leaving sufficient disposable income."
                ),
                factors=[
                    "Affordable monthly repayments",
                    "Sufficient disposable income after repayment",
                    "Loan term within standard range",
                ],
            ),
            recommendation=Recommendation(
                id="rec-02",
                recommended=True,
                rationale=(
                    "This plan provides flexibility in how you use the funds while "
                    "maintaining affordable repayments."
                ),
            ),
        ),
    ]


def step_resolve_consent(case: Case, request: Any) -> StepResult:
    plans = _build_plans()
    case.plans = plans
    return StepResult(
        events=[
            _event(EventType.plans_ready, {
                "plans": [p.model_dump() for p in plans],
            }),
        ],
        advance_to=4,
    )


# --- Stage 4: Select (plan) → OffersReady + Disclosure ---

def _build_offers(plan_id: str) -> list[ProductOffer]:
    return [
        ProductOffer(
            id="offer-01",
            plan_id=plan_id,
            lender="Horizon Bank",
            product_name="Horizon Fixed Personal Loan",
            features=[
                ProductFeature(name="Loan amount", value="£7,500", description="Total borrowing"),
                ProductFeature(name="Term", value="48 months", description="Repayment period"),
                ProductFeature(name="Monthly repayment", value="£178.42", description="Fixed monthly amount"),
                ProductFeature(name="Early repayment", value="Allowed", description="No early repayment charges after 12 months"),
            ],
            rates={"apr": "6.9%", "annual_rate": "6.7%", "total_repayable": "£8,564.16"},
            conditions=[
                "Subject to full credit check at application",
                "Must be UK resident aged 18 or over",
                "Minimum income requirement: £15,000 per annum",
            ],
            apply_url="https://example.com/horizon/apply",
        ),
        ProductOffer(
            id="offer-02",
            plan_id=plan_id,
            lender="Sterling Finance",
            product_name="Sterling Flex Loan",
            features=[
                ProductFeature(name="Loan amount", value="£7,500", description="Total borrowing"),
                ProductFeature(name="Term", value="36 months", description="Repayment period"),
                ProductFeature(name="Monthly repayment", value="£231.89", description="Fixed monthly amount"),
                ProductFeature(name="Early repayment", value="Allowed", description="No early repayment charges"),
            ],
            rates={"apr": "7.4%", "annual_rate": "7.2%", "total_repayable": "£8,348.04"},
            conditions=[
                "Subject to full credit check at application",
                "Must be UK resident aged 18 or over",
                "Minimum income requirement: £12,000 per annum",
            ],
            apply_url="https://example.com/sterling/apply",
        ),
        ProductOffer(
            id="offer-03",
            plan_id=plan_id,
            lender="Maple Credit",
            product_name="Maple Essential Loan",
            features=[
                ProductFeature(name="Loan amount", value="£7,500", description="Total borrowing"),
                ProductFeature(name="Term", value="60 months", description="Repayment period"),
                ProductFeature(name="Monthly repayment", value="£149.25", description="Fixed monthly amount"),
                ProductFeature(name="Early repayment", value="Allowed", description="28-day early settlement charge applies"),
            ],
            rates={"apr": "8.9%", "annual_rate": "8.6%", "total_repayable": "£8,955.00"},
            conditions=[
                "Subject to full credit check at application",
                "Must be UK resident aged 18 or over",
            ],
            apply_url="https://example.com/maple/apply",
        ),
    ]


def step_select_plan(case: Case, request: Any) -> StepResult:
    offers = _build_offers(request.entity_id)
    case.offers = offers

    offer_subjects = [
        ActionSubject(
            entity_type="product_offer",
            entity_id=o.id,
            role=SubjectRole.context,
        )
        for o in offers
    ]

    return StepResult(
        events=[
            _event(EventType.offers_ready, {
                "offers": [o.model_dump() for o in offers],
            }),
        ],
        pending_action=BrokerAction(
            id="action-disclosure-02",
            action_type=ActionType.disclosure,
            regulated=True,
            content=(
                "Important information about these loan offers:\n\n"
                "Representative example: If you borrow £7,500 over 48 months at a "
                "fixed annual rate of 6.7%, you would pay 48 monthly instalments of "
                "£178.42. Total amount repayable: £8,564.16. Representative APR: 6.9%.\n\n"
                "The APR shown is representative. The rate you are offered may differ "
                "based on your individual circumstances and credit history. All offers "
                "are subject to a full credit check at the point of application, which "
                "will be recorded on your credit file.\n\n"
                "You are under no obligation to proceed with any of these offers."
            ),
            response_expectation=ResponseExpectation.acknowledge,
            subjects=offer_subjects,
        ),
        advance_to=5,
    )


# --- Stage 5: Resolve (acknowledge offer disclosure) ---

def step_resolve_offer_disclosure(case: Case, request: Any) -> StepResult:
    return StepResult(advance_to=6)


# --- Stage 6: Select (offer) → Declaration ---

def step_select_offer(case: Case, request: Any) -> StepResult:
    selected_offer = next((o for o in case.offers if o.id == request.entity_id), None)
    offer_name = selected_offer.product_name if selected_offer else "the selected product"

    return StepResult(
        pending_action=BrokerAction(
            id="action-declaration-01",
            action_type=ActionType.declaration,
            regulated=True,
            content=(
                f"Before we submit your application for {offer_name}, please confirm "
                "the following declaration:\n\n"
                "I declare that the information I have provided is true, complete, "
                "and accurate to the best of my knowledge. I understand that providing "
                "false or misleading information may result in my application being "
                "declined, any agreement being cancelled, or legal action being taken."
            ),
            response_expectation=ResponseExpectation.affirm_or_deny,
            subjects=[
                ActionSubject(
                    entity_type="product_offer",
                    entity_id=request.entity_id,
                    role=SubjectRole.for_confirmation,
                ),
            ],
        ),
        advance_to=7,
    )


# --- Stage 7: Resolve (affirm declaration) → Instruction ---

def step_resolve_declaration(case: Case, request: Any) -> StepResult:
    # Find the selected offer from the declaration's subjects
    selected_offer = None
    if case.offers:
        # Use the last pending action's subjects to find the offer
        selected_offer = case.offers[0]  # Default to first
        for o in case.offers:
            # The offer referenced in the declaration
            if any(
                s.entity_id == o.id
                for s in (case.event_log[-1].data.get("subjects", []) if case.event_log else [])
            ):
                selected_offer = o
                break

    apply_url = selected_offer.apply_url if selected_offer else "https://example.com/apply"
    lender_name = selected_offer.lender if selected_offer else "the lender"

    return StepResult(
        pending_action=BrokerAction(
            id="action-instruction-01",
            action_type=ActionType.instruction,
            regulated=True,
            content=(
                f"Your application is ready to be submitted to {lender_name}. "
                "By proceeding, you will be directed to the lender's website to "
                "complete your application. The lender will perform a full credit "
                "check, which will be recorded on your credit file.\n\n"
                f"Click the link to proceed: {apply_url}"
            ),
            response_expectation=ResponseExpectation.authorise,
            subjects=[
                ActionSubject(
                    entity_type="product_offer",
                    entity_id=selected_offer.id if selected_offer else "unknown",
                    role=SubjectRole.being_authorised,
                ),
            ],
        ),
        advance_to=8,
    )


# --- Stage 8: Resolve (authorise instruction) → CaseOutcome ---

def step_resolve_instruction(case: Case, request: Any) -> StepResult:
    return StepResult(
        events=[
            _event(EventType.case_status_changed, {
                "previous_status": CaseStatus.open.value,
                "new_status": CaseStatus.transferred.value,
                "reason": "Application submitted to lender",
            }),
        ],
        pending_action=BrokerAction(
            id="action-case-outcome-01",
            action_type=ActionType.case_outcome,
            regulated=False,
            content=(
                "Your case has been transferred to the lender. Your application "
                "reference will be provided by the lender directly. If you have "
                "any questions about the broking process, please contact "
                "ClearCredit Solutions Ltd."
            ),
            response_expectation=ResponseExpectation.none,
        ),
        advance_to=9,
        status=CaseStatus.transferred,
    )


# --- Withdraw (any stage) ---

def step_withdraw(case: Case, request: Any) -> StepResult:
    return StepResult(
        events=[
            _event(EventType.case_status_changed, {
                "previous_status": case.status.value,
                "new_status": CaseStatus.withdrawn.value,
                "reason": "User withdrew from the process",
            }),
        ],
        pending_action=BrokerAction(
            id="action-case-outcome-withdraw",
            action_type=ActionType.case_outcome,
            regulated=False,
            content=(
                "You have withdrawn from the credit broking process. No application "
                "has been submitted. Your data will be retained in accordance with "
                "our privacy policy. You are welcome to start a new enquiry at any time."
            ),
            response_expectation=ResponseExpectation.none,
        ),
        advance_to=9,
        status=CaseStatus.withdrawn,
    )


# Step registry: (operation, stage) → handler function
# stage=None means the step applies at any stage (used for withdraw)
JOURNEY_STEPS: dict[tuple[str, int | None], Callable] = {
    ("open", 0): step_open_case,
    ("provide", 1): step_provide,
    ("resolve", 2): step_resolve_disclosure,
    ("resolve", 3): step_resolve_consent,
    ("select", 4): step_select_plan,
    ("resolve", 5): step_resolve_offer_disclosure,
    ("select", 6): step_select_offer,
    ("resolve", 7): step_resolve_declaration,
    ("resolve", 8): step_resolve_instruction,
    ("withdraw", None): step_withdraw,
}
