"""
Generates ~10,000 realistic employees + salary history so the app can be
exercised at real-world scale. Safe to re-run - if the employees table
already has rows, the script skips instead of adding duplicates.

Usage (from backend/):
    python -m scripts.seed
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from faker import Faker

from app.constants import currency_for_country
from app.database import SessionLocal
from app.models import Employee, SalaryRecord

random.seed(42)
Faker.seed(42)
fake = Faker()

TOTAL_EMPLOYEES = 10000
BATCH_SIZE = 500

COUNTRY_WEIGHTS = {
    "India": 30,
    "United States": 20,
    "United Kingdom": 10,
    "Germany": 8,
    "Canada": 8,
    "Australia": 6,
    "Singapore": 6,
    "Japan": 5,
    "Brazil": 4,
    "United Arab Emirates": 3,
}

DEPARTMENT_ROLES = {
    "Engineering": [
        "Software Engineer I", "Software Engineer II", "Senior Software Engineer",
        "Staff Engineer", "Engineering Manager",
    ],
    "Sales": [
        "Sales Associate", "Account Executive", "Senior Account Executive",
        "Sales Team Lead", "Sales Director",
    ],
    "Marketing": [
        "Marketing Associate", "Marketing Specialist", "Senior Marketing Specialist",
        "Marketing Manager", "Marketing Director",
    ],
    "Product": [
        "Associate Product Manager", "Product Manager", "Senior Product Manager",
        "Group Product Manager", "Director of Product",
    ],
    "Customer Support": [
        "Support Associate", "Support Specialist", "Senior Support Specialist",
        "Support Team Lead", "Support Manager",
    ],
    "Operations": [
        "Operations Associate", "Operations Analyst", "Senior Operations Analyst",
        "Operations Manager", "Operations Director",
    ],
    "Finance": [
        "Financial Analyst", "Senior Financial Analyst", "Finance Manager",
        "Finance Controller", "Finance Director",
    ],
    "HR": [
        "HR Associate", "HR Generalist", "Senior HR Generalist",
        "HR Manager", "HR Director",
    ],
}

DEPARTMENT_WEIGHTS = {
    "Engineering": 30,
    "Sales": 15,
    "Marketing": 10,
    "Product": 10,
    "Customer Support": 15,
    "Operations": 8,
    "Finance": 7,
    "HR": 5,
}

# role index (0-4, junior to senior) -> annual salary band in USD, before
# the country adjustment below
LEVEL_USD_BAND = {
    0: (35000, 50000),
    1: (50000, 70000),
    2: (70000, 95000),
    3: (95000, 130000),
    4: (130000, 180000),
}
LEVEL_WEIGHTS = {0: 35, 1: 30, 2: 20, 3: 10, 4: 5}

# Approximate local-currency scale, used only to make seed salaries look
# realistic in each currency. This is NOT a live FX conversion feature -
# docs/requirements.md explicitly leaves that out of the app itself.
USD_TO_LOCAL = {
    "INR": 83, "USD": 1, "GBP": 0.79, "EUR": 0.92, "CAD": 1.36,
    "AUD": 1.52, "SGD": 1.34, "JPY": 149, "BRL": 5.4, "AED": 3.67,
}


def weighted_choice(weights_dict):
    options = list(weights_dict.keys())
    weights = list(weights_dict.values())
    return random.choices(options, weights=weights, k=1)[0]


def random_salary_for_level(level, country):
    low_usd, high_usd = LEVEL_USD_BAND[level]
    usd_amount = random.uniform(low_usd, high_usd)
    currency = currency_for_country(country)
    local_amount = usd_amount * USD_TO_LOCAL[currency]
    rounding_unit = 100 if local_amount < 10000 else 1000
    return Decimal(round(local_amount / rounding_unit) * rounding_unit)


def random_join_date():
    start = date(2016, 1, 1)
    end = date.today() - timedelta(days=30)
    days_between = (end - start).days
    return start + timedelta(days=random.randint(0, days_between))


def build_employee(index):
    country = weighted_choice(COUNTRY_WEIGHTS)
    department = weighted_choice(DEPARTMENT_WEIGHTS)
    level = weighted_choice(LEVEL_WEIGHTS)
    role = DEPARTMENT_ROLES[department][level]
    is_active = random.random() > 0.03  # ~3% deactivated, to exercise soft-delete at scale

    employee = Employee(
        employee_code=f"EMP{index:05d}",
        name=fake.name(),
        department=department,
        role=role,
        country=country,
        join_date=random_join_date(),
        is_active=is_active,
    )
    return employee, level


def build_salary_history(employee, level):
    """Hire record on the join date, plus 0-2 raises for employees who've
    been around long enough - gives the salary history view something
    real to show."""
    currency = currency_for_country(employee.country)
    hire_amount = random_salary_for_level(level, employee.country)
    records = [
        SalaryRecord(
            employee_id=employee.id,
            amount=hire_amount,
            currency=currency,
            effective_date=employee.join_date,
            reason="Hire",
        )
    ]

    years_since_join = (date.today() - employee.join_date).days / 365
    num_raises = random.choice([0, 1, 1, 2]) if years_since_join > 1 else 0

    current_amount = hire_amount
    raise_date = employee.join_date
    for _ in range(num_raises):
        raise_date = raise_date + timedelta(days=random.randint(365, 540))
        if raise_date >= date.today():
            break
        increase_factor = Decimal(str(round(random.uniform(1.05, 1.20), 2)))
        current_amount = (current_amount * increase_factor).quantize(Decimal("1"))
        records.append(SalaryRecord(
            employee_id=employee.id,
            amount=current_amount,
            currency=currency,
            effective_date=raise_date,
            reason=random.choice(["Annual raise", "Promotion", "Performance adjustment"]),
        ))

    return records


def seed():
    db = SessionLocal()
    try:
        existing_count = db.query(Employee).count()
        if existing_count > 0:
            print(f"employees table already has {existing_count} rows - skipping seed.")
            return

        for batch_start in range(0, TOTAL_EMPLOYEES, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, TOTAL_EMPLOYEES)

            batch_employees = []
            batch_levels = []
            for i in range(batch_start, batch_end):
                employee, level = build_employee(i + 1)
                batch_employees.append(employee)
                batch_levels.append(level)

            db.add_all(batch_employees)
            db.flush()  # assigns each employee's id, needed for salary_records below

            batch_salary_records = []
            for employee, level in zip(batch_employees, batch_levels):
                batch_salary_records.extend(build_salary_history(employee, level))

            db.add_all(batch_salary_records)
            db.commit()

            print(f"Seeded {batch_end}/{TOTAL_EMPLOYEES} employees")

        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
