import pytest


@pytest.fixture
def sample_vocabulary():
    return {
        "fact_types": [
            {
                "name": "gross_annual_income",
                "description": "Total annual income before tax.",
                "value_type": "monetary",
                "typical_operators": ["eq", "approx"],
                "examples": ["I earn £35,000 a year"],
            },
        ],
        "attribute_types": [
            {
                "name": "full_name",
                "description": "Full legal name.",
                "value_structure": "string",
                "examples": ["John Smith"],
            },
        ],
        "goal_types": [
            {
                "name": "debt_consolidation",
                "description": "Combine multiple debts into one loan.",
                "typical_desired_changes": ["reduce total repayments"],
                "examples": ["I want to consolidate my debts"],
            },
        ],
    }
