"""
Dedicated Eligibility Assessment Endpoints.
Allows standalone, direct testing of schemes against user profiles with criterion-level explanations.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.repositories.scheme_repo import SchemeRepository
from backend.schemas.user_profile import UserProfile
from backend.schemas.eligibility import SchemeEligibilityResult
from backend.eligibility.engine import EligibilityEngine

router = APIRouter(prefix="/eligibility", tags=["Eligibility"])


class StandaloneEligibilityRequest(BaseModel):
    profile: UserProfile
    scheme_ids: Optional[List[str]] = Field(
        default=None, description="Optional subset of scheme IDs to check. If omitted, checks all active schemes."
    )


@router.post("/check", response_model=List[SchemeEligibilityResult])
def check_eligibility(
    request: StandaloneEligibilityRequest,
    db: Session = Depends(get_db),
):
    repo = SchemeRepository(db)
    if request.scheme_ids:
        schemes = [repo.get_by_id(sid) for sid in request.scheme_ids if repo.get_by_id(sid)]
    else:
        schemes = repo.get_all(active_only=True)

    if not schemes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching schemes found for evaluation.",
        )

    results = []
    for s in schemes:
        res = EligibilityEngine.evaluate_scheme(s, request.profile)
        results.append(res)

    return results
