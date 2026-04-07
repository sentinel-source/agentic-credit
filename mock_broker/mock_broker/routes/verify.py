from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from mock_broker.security import verify_redirect

router = APIRouter()


class VerifyRequest(BaseModel):
    token: str
    case_id: str
    offer_id: str
    destination_url: str


class VerifyResponse(BaseModel):
    valid: bool
    reason: str


@router.post("", response_model=VerifyResponse)
def verify_redirect_token(body: VerifyRequest):
    valid, reason = verify_redirect(
        token=body.token,
        case_id=body.case_id,
        offer_id=body.offer_id,
        destination_url=body.destination_url,
    )
    return VerifyResponse(valid=valid, reason=reason)
