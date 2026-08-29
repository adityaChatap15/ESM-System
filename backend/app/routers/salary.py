"""
Salary history endpoints. Every salary change is an insert, never an
update - that's what gives us history for free (see app/models.py).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.constants import currency_for_country
from app.database import get_db
from app.models import Employee, SalaryRecord
from app.schemas import SalaryRecordCreate, SalaryRecordOut

router = APIRouter(prefix="/api/v1/employees", tags=["salary"])


@router.get("/{employee_id}/salary-history", response_model=list[SalaryRecordOut])
def get_salary_history(employee_id: int, db: Session = Depends(get_db)):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return (
        db.query(SalaryRecord)
        .filter(SalaryRecord.employee_id == employee_id)
        .order_by(SalaryRecord.effective_date.desc(), SalaryRecord.id.desc())
        .all()
    )


@router.post("/{employee_id}/salary", response_model=SalaryRecordOut, status_code=201)
def add_salary_record(employee_id: int, payload: SalaryRecordCreate, db: Session = Depends(get_db)):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    record = SalaryRecord(
        employee_id=employee_id,
        amount=payload.amount,
        currency=currency_for_country(employee.country),
        effective_date=payload.effective_date,
        reason=payload.reason,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
