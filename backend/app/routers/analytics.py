"""
Analytics endpoints - answers the "how does the org pay people" questions
from docs/requirements.md. All filters (department/country/role) are
optional and combine with each other.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.analytics_logic import (
    DIMENSION_GETTERS,
    build_distribution,
    build_extremes,
    build_headcount_payroll,
    build_summary,
    get_current_salaries,
)
from app.auth import get_current_user
from app.database import get_db
from app.schemas import (
    DistributionGroup,
    ExtremesGroup,
    HeadcountPayrollItem,
    SalarySummaryItem,
)

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/summary", response_model=list[SalarySummaryItem])
def salary_summary(
    dimension: str = Query(..., description="One of: country, department, role"),
    department: Optional[str] = None,
    country: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if dimension not in DIMENSION_GETTERS:
        valid_options = sorted(DIMENSION_GETTERS.keys())
        raise HTTPException(status_code=400, detail=f"dimension must be one of {valid_options}")

    pairs = get_current_salaries(db, department=department, country=country, role=role)
    return build_summary(pairs, dimension)


@router.get("/distribution", response_model=list[DistributionGroup])
def salary_distribution(
    department: Optional[str] = None,
    country: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
):
    pairs = get_current_salaries(db, department=department, country=country, role=role)
    return build_distribution(pairs)


@router.get("/extremes", response_model=list[ExtremesGroup])
def salary_extremes(
    department: Optional[str] = None,
    country: Optional[str] = None,
    role: Optional[str] = None,
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
):
    pairs = get_current_salaries(db, department=department, country=country, role=role)
    return build_extremes(pairs, limit=limit)


@router.get("/headcount-payroll", response_model=list[HeadcountPayrollItem])
def headcount_payroll(
    department: Optional[str] = None,
    country: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
):
    pairs = get_current_salaries(db, department=department, country=country, role=role)
    return build_headcount_payroll(pairs)
