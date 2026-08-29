"""
Employee CRUD endpoints. Each function talks to the DB session directly -
no extra service/repository layer, since the queries here are simple
enough to read in one place.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Employee
from app.salary_logic import get_current_salary
from app.schemas import (
    EmployeeCreate,
    EmployeeDetailOut,
    EmployeeListResponse,
    EmployeeOut,
    EmployeeUpdate,
    SalaryRecordOut,
)

router = APIRouter(
    prefix="/api/v1/employees",
    tags=["employees"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=EmployeeListResponse)
def list_employees(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    department: Optional[str] = None,
    country: Optional[str] = None,
    role: Optional[str] = None,
    search: Optional[str] = None,
    include_inactive: bool = False,
):
    query = db.query(Employee)

    if not include_inactive:
        query = query.filter(Employee.is_active.is_(True))
    if department:
        query = query.filter(Employee.department == department)
    if country:
        query = query.filter(Employee.country == country)
    if role:
        query = query.filter(Employee.role == role)
    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Employee.name.ilike(like_pattern),
                Employee.employee_code.ilike(like_pattern),
            )
        )

    total = query.count()
    items = (
        query.order_by(Employee.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return EmployeeListResponse(total=total, page=page, page_size=page_size, items=items)


@router.get("/{employee_id}", response_model=EmployeeDetailOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    current_salary = get_current_salary(db, employee_id)
    detail = EmployeeDetailOut.model_validate(employee)
    if current_salary is not None:
        detail.current_salary = SalaryRecordOut.model_validate(current_salary)
    return detail


@router.post("", response_model=EmployeeOut, status_code=201)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(Employee)
        .filter(Employee.employee_code == payload.employee_code)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=400, detail="employee_code already exists")

    employee = Employee(**payload.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)
    return employee


@router.delete("/{employee_id}", response_model=EmployeeOut)
def deactivate_employee(employee_id: int, db: Session = Depends(get_db)):
    """Soft delete: HR needs to keep history, so we flip is_active off
    instead of removing the row."""
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee.is_active = False
    db.commit()
    db.refresh(employee)
    return employee
