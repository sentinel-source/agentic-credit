from fastapi import FastAPI

from mock_broker.journey.engine import JourneyEngine
from mock_broker.routes import cases, vocabulary
from mock_broker.state.case_store import CaseStore


def create_app() -> FastAPI:
    app = FastAPI(
        title="Mock Credit Broker",
        description=(
            "A mock Credit Broker implementing the Agentic Credit Broking Protocol. "
            "Simulates a consumer credit (personal loan) broking journey for "
            "User Agent development and testing."
        ),
        version="0.1.0",
    )
    app.state.store = CaseStore()
    app.state.engine = JourneyEngine()
    app.include_router(cases.router, prefix="/cases", tags=["cases"])
    app.include_router(vocabulary.router, prefix="/vocabulary", tags=["vocabulary"])
    return app
