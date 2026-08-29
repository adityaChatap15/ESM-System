"""
Analytics logic. Everything here works on each active employee's *current*
salary (latest effective_date), never the full history table.

Important rule followed throughout this file: salaries are never averaged,
summed, or compared across different currencies (docs/requirements.md
explicitly leaves out FX conversion). Every aggregation below groups by
currency first - "average salary by department" actually means "average
salary by department, per currency", since a department can span
countries that don't share a currency.

Aggregation (avg/median/bands) is done in plain Python with the
`statistics` module instead of database-specific SQL (e.g. Postgres'
percentile_cont), on purpose: at ~10,000 employees the numbers comfortably
fit in memory, and this keeps the logic readable and testable against
the same in-memory SQLite the rest of the test suite uses.
"""
import statistics

from app.models import Employee, SalaryRecord

DIMENSION_GETTERS = {
    "country": lambda employee: employee.country,
    "department": lambda employee: employee.department,
    "role": lambda employee: employee.role,
}


def get_current_salaries(db, department=None, country=None, role=None):
    """Returns one (employee, salary_record) pair per active employee -
    their current salary - honoring the same filters as the employee
    list endpoint."""
    query = (
        db.query(Employee, SalaryRecord)
        .join(SalaryRecord, SalaryRecord.employee_id == Employee.id)
        .filter(Employee.is_active.is_(True))
    )
    if department:
        query = query.filter(Employee.department == department)
    if country:
        query = query.filter(Employee.country == country)
    if role:
        query = query.filter(Employee.role == role)

    query = query.order_by(Employee.id, SalaryRecord.effective_date.desc(), SalaryRecord.id.desc())

    current_by_employee = {}
    for employee, salary in query.all():
        if employee.id not in current_by_employee:
            current_by_employee[employee.id] = (employee, salary)

    return list(current_by_employee.values())


def build_summary(pairs, dimension):
    get_dimension_value = DIMENSION_GETTERS[dimension]

    groups = {}
    for employee, salary in pairs:
        key = (get_dimension_value(employee), salary.currency)
        groups.setdefault(key, []).append(float(salary.amount))

    items = []
    for (group_value, currency), amounts in groups.items():
        items.append({
            "group": group_value,
            "currency": currency,
            "headcount": len(amounts),
            "average_salary": round(statistics.mean(amounts), 2),
            "median_salary": round(statistics.median(amounts), 2),
            "min_salary": round(min(amounts), 2),
            "max_salary": round(max(amounts), 2),
        })

    items.sort(key=lambda item: (item["group"], item["currency"]))
    return items


def build_distribution(pairs, num_bands=5):
    amounts_by_currency = {}
    for employee, salary in pairs:
        amounts_by_currency.setdefault(salary.currency, []).append(float(salary.amount))

    result = []
    for currency, amounts in sorted(amounts_by_currency.items()):
        low = min(amounts)
        high = max(amounts)
        band_width = (high - low) / num_bands if high > low else 1.0

        bands = []
        for i in range(num_bands):
            band_min = low + i * band_width
            band_max = low + (i + 1) * band_width
            is_last_band = i == num_bands - 1
            count = sum(
                1 for amount in amounts
                if band_min <= amount < band_max or (is_last_band and amount == high)
            )
            bands.append({
                "range_label": f"{band_min:.0f}-{band_max:.0f}",
                "range_min": round(band_min, 2),
                "range_max": round(band_max, 2),
                "headcount": count,
            })

        result.append({"currency": currency, "bands": bands})

    return result


def build_extremes(pairs, limit=5):
    pairs_by_currency = {}
    for employee, salary in pairs:
        pairs_by_currency.setdefault(salary.currency, []).append((employee, salary))

    def to_extreme(pair):
        employee, salary = pair
        return {
            "employee_id": employee.id,
            "employee_code": employee.employee_code,
            "name": employee.name,
            "department": employee.department,
            "role": employee.role,
            "country": employee.country,
            "amount": float(salary.amount),
            "currency": salary.currency,
        }

    result = []
    for currency, group in sorted(pairs_by_currency.items()):
        sorted_group = sorted(group, key=lambda pair: pair[1].amount)
        lowest = sorted_group[:limit]
        highest = list(reversed(sorted_group[-limit:]))

        result.append({
            "currency": currency,
            "highest": [to_extreme(pair) for pair in highest],
            "lowest": [to_extreme(pair) for pair in lowest],
        })

    return result


def build_headcount_payroll(pairs):
    amounts_by_country = {}
    for employee, salary in pairs:
        key = (employee.country, salary.currency)
        amounts_by_country.setdefault(key, []).append(float(salary.amount))

    items = []
    for (country, currency), amounts in amounts_by_country.items():
        items.append({
            "country": country,
            "currency": currency,
            "headcount": len(amounts),
            "total_payroll": round(sum(amounts), 2),
        })

    items.sort(key=lambda item: item["country"])
    return items
