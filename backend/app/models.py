"""
Database models. Kept as plain SQLAlchemy classes - no mixins or generic
base classes, so every table's columns are easy to read top to bottom.

Salary history is a first-class table (SalaryRecord), not a single column
on Employee: every salary change inserts a new row instead of overwriting
the old value. The employee's "current" salary is just the row with the
latest effective_date for that employee - see app/salary_logic.py (added
in a later phase) for that lookup.
"""
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    employee_code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    join_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    salary_records = relationship("SalaryRecord", back_populates="employee")

    __table_args__ = (
        Index("ix_employees_department", "department"),
        Index("ix_employees_country", "country"),
        Index("ix_employees_role", "role"),
        Index("ix_employees_name", "name"),
    )


class SalaryRecord(Base):
    __tablename__ = "salary_records"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    effective_date = Column(Date, nullable=False)
    reason = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="salary_records")

    __table_args__ = (
        Index("ix_salary_records_employee_effective", "employee_id", "effective_date"),
    )
