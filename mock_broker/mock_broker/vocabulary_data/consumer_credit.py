from mock_broker.models.vocabulary import (
    AttributeTypeDefinition,
    FactTypeDefinition,
    GoalTypeDefinition,
)

FACT_TYPES: list[FactTypeDefinition] = [
    FactTypeDefinition(
        name="gross_annual_income",
        description="Total annual income before tax and deductions from all employment sources.",
        value_type="monetary",
        typical_operators=["eq", "approx"],
        examples=[
            "I earn £35,000 a year",
            "My salary is about forty-five thousand",
        ],
    ),
    FactTypeDefinition(
        name="net_monthly_income",
        description="Monthly income after tax and all deductions, including take-home pay from all sources.",
        value_type="monetary",
        typical_operators=["eq", "approx"],
        examples=[
            "I take home £2,400 a month",
            "My monthly pay after tax is around two thousand",
        ],
    ),
    FactTypeDefinition(
        name="monthly_expenditure",
        description="Total regular monthly outgoings excluding rent or mortgage payments. Includes bills, subscriptions, food, transport, and other recurring costs.",
        value_type="monetary",
        typical_operators=["eq", "approx"],
        examples=[
            "My bills and living costs are about £1,200 a month",
            "I spend roughly fifteen hundred on everything each month",
        ],
    ),
    FactTypeDefinition(
        name="monthly_rent_or_mortgage",
        description="Monthly housing cost, whether rent or mortgage payment.",
        value_type="monetary",
        typical_operators=["eq"],
        examples=[
            "My rent is £850 a month",
            "I pay £1,100 on my mortgage each month",
        ],
    ),
    FactTypeDefinition(
        name="existing_credit_card_balance",
        description="Total outstanding balance across all credit cards.",
        value_type="monetary",
        typical_operators=["eq", "approx"],
        examples=[
            "I owe about £3,000 on credit cards",
            "My credit card balance is £1,500",
        ],
    ),
    FactTypeDefinition(
        name="existing_loan_balance",
        description="Total outstanding balance on existing personal loans, car finance, or hire purchase agreements.",
        value_type="monetary",
        typical_operators=["eq", "approx"],
        examples=[
            "I have £5,000 left on a car loan",
            "I still owe about eight thousand on a personal loan",
        ],
    ),
    FactTypeDefinition(
        name="employment_status",
        description="Current employment status: employed, self-employed, part-time, unemployed, retired, student, or carer.",
        value_type="text",
        typical_operators=["eq"],
        examples=[
            "I work full-time",
            "I'm self-employed",
            "I've been unemployed for three months",
        ],
    ),
    FactTypeDefinition(
        name="years_in_current_employment",
        description="Duration in current job or self-employment, in years.",
        value_type="integer",
        typical_operators=["eq", "gte"],
        examples=[
            "I've been in my job for four years",
            "I started here about two years ago",
        ],
    ),
    FactTypeDefinition(
        name="number_of_dependants",
        description="Number of financial dependants the applicant supports.",
        value_type="integer",
        typical_operators=["eq"],
        examples=[
            "I have two children",
            "No dependants",
        ],
    ),
    FactTypeDefinition(
        name="residential_status",
        description="Whether the applicant is a homeowner, tenant, living with family, or other arrangement.",
        value_type="text",
        typical_operators=["eq"],
        examples=[
            "I rent my flat",
            "I own my home with a mortgage",
            "I live with my parents",
        ],
    ),
    FactTypeDefinition(
        name="monthly_loan_repayment_budget",
        description="The maximum monthly repayment amount the applicant is comfortable with for a new loan.",
        value_type="monetary",
        typical_operators=["eq", "lte"],
        examples=[
            "I can afford up to £300 a month",
            "I'd like to keep repayments under two hundred",
        ],
    ),
]

ATTRIBUTE_TYPES: list[AttributeTypeDefinition] = [
    AttributeTypeDefinition(
        name="full_name",
        description="Applicant's full legal name as it appears on official documents.",
        value_structure="string",
        examples=["John Smith", "Sarah Jane Connor"],
    ),
    AttributeTypeDefinition(
        name="date_of_birth",
        description="Applicant's date of birth in ISO 8601 format (YYYY-MM-DD).",
        value_structure="date (YYYY-MM-DD)",
        examples=["1990-05-15", "1985-11-23"],
    ),
    AttributeTypeDefinition(
        name="current_address",
        description="Applicant's current residential address including postcode.",
        value_structure="string (full address with postcode)",
        examples=["14 Elm Street, Manchester, M1 2AB"],
    ),
    AttributeTypeDefinition(
        name="email",
        description="Applicant's email address for correspondence.",
        value_structure="string (email)",
        examples=["john.smith@example.com"],
    ),
    AttributeTypeDefinition(
        name="phone",
        description="Applicant's primary contact telephone number.",
        value_structure="string (phone number)",
        examples=["07700 900123", "+44 7700 900123"],
    ),
    AttributeTypeDefinition(
        name="nationality",
        description="Applicant's nationality or nationalities.",
        value_structure="string",
        examples=["British", "Irish"],
    ),
]

GOAL_TYPES: list[GoalTypeDefinition] = [
    GoalTypeDefinition(
        name="debt_consolidation",
        description="Combine multiple existing debts into a single personal loan, typically to reduce overall interest or simplify repayments.",
        typical_desired_changes=[
            "existing_credit_card_balance reduced to zero",
            "existing_loan_balance reduced to zero",
            "single monthly repayment amount",
        ],
        examples=[
            "I want to consolidate my credit card debts into one loan",
            "I'd like to roll my debts together to get a lower rate",
        ],
    ),
    GoalTypeDefinition(
        name="major_purchase",
        description="Finance a significant one-off purchase such as a car, home improvements, wedding, or other large expense.",
        typical_desired_changes=[
            "loan_amount to cover purchase cost",
            "loan_term matching budget",
        ],
        examples=[
            "I need a loan for a new car",
            "I want to borrow £10,000 for home renovations",
            "I'm looking for finance for my wedding",
        ],
    ),
    GoalTypeDefinition(
        name="emergency_funds",
        description="Borrow to cover an unexpected expense such as a repair, medical bill, or urgent financial need.",
        typical_desired_changes=[
            "loan_amount to cover shortfall",
            "fast disbursement",
        ],
        examples=[
            "I need money quickly for an emergency repair",
            "I have an unexpected bill I need to cover",
        ],
    ),
    GoalTypeDefinition(
        name="credit_building",
        description="Take out a manageable loan or credit product primarily to build or improve credit history.",
        typical_desired_changes=[
            "small loan amount",
            "regular repayments over fixed term",
        ],
        examples=[
            "I want to improve my credit score",
            "I'm looking for a credit builder loan",
        ],
    ),
]
