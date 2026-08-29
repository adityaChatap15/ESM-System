"""
Shared salary lookup logic. Kept separate from the routers because both
the employee detail endpoint and the salary endpoints need "what is this
employee's current salary right now" answered the same way.
"""
from app.models import SalaryRecord


def get_current_salary(db, employee_id):
    """The 'current' salary is the record with the latest effective_date,
    not the most recently inserted row - an HR manager can backdate or
    log a raise after the fact, and the newest effective_date should
    always win regardless of insertion order."""
    return (
        db.query(SalaryRecord)
        .filter(SalaryRecord.employee_id == employee_id)
        .order_by(SalaryRecord.effective_date.desc(), SalaryRecord.id.desc())
        .first()
    )
