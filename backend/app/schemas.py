"""
Pydantic request/response models. Plain classes, one per shape we send or
receive over the API - no shared generic base, so each schema is readable
on its own.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EmployeeCreate(BaseModel):
    employee_code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=100)
    department: str = Field(min_length=1, max_length=50)
    role: str = Field(min_length=1, max_length=50)
    country: str = Field(min_length=1, max_length=50)
    join_date: date


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    country: Optional[str] = None
    join_date: Optional[date] = None


class EmployeeOut(BaseModel):
    id: int
    employee_code: str
    name: str
    department: str
    role: str
    country: str
    join_date: date
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EmployeeListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[EmployeeOut]


class SalaryRecordCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    effective_date: date
    reason: Optional[str] = Field(default=None, max_length=200)

    @field_validator("effective_date")
    @classmethod
    def effective_date_not_in_future(cls, value):
        if value > date.today():
            raise ValueError("effective_date cannot be in the future")
        return value


class SalaryRecordOut(BaseModel):
    id: int
    amount: Decimal
    currency: str
    effective_date: date
    reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EmployeeDetailOut(EmployeeOut):
    current_salary: Optional[SalaryRecordOut] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SalarySummaryItem(BaseModel):
    group: str
    currency: str
    headcount: int
    average_salary: float
    median_salary: float
    min_salary: float
    max_salary: float


class PayBand(BaseModel):
    range_label: str
    range_min: float
    range_max: float
    headcount: int


class DistributionGroup(BaseModel):
    currency: str
    bands: list[PayBand]


class ExtremeEmployee(BaseModel):
    employee_id: int
    employee_code: str
    name: str
    department: str
    role: str
    country: str
    amount: float
    currency: str


class ExtremesGroup(BaseModel):
    currency: str
    highest: list[ExtremeEmployee]
    lowest: list[ExtremeEmployee]


class HeadcountPayrollItem(BaseModel):
    country: str
    currency: str
    headcount: int
    total_payroll: float
