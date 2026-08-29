"""Tests for salary history: recording changes, currency assignment,
validation, and 'current salary' resolution."""
from datetime import date, timedelta


def create_employee(client, employee_code="E100", country="India"):
    payload = {
        "employee_code": employee_code,
        "name": "Salary Test Employee",
        "department": "Engineering",
        "role": "Engineer",
        "country": country,
        "join_date": "2022-01-01",
    }
    return client.post("/api/v1/employees", json=payload).json()


def test_add_salary_record_sets_currency_from_country(client):
    employee = create_employee(client, country="Germany")

    response = client.post(
        f"/api/v1/employees/{employee['id']}/salary",
        json={"amount": "50000", "effective_date": "2022-01-01", "reason": "Hire"},
    )
    assert response.status_code == 201
    assert response.json()["currency"] == "EUR"


def test_add_salary_for_unknown_country_defaults_to_usd(client):
    employee = create_employee(client, country="Atlantis")

    response = client.post(
        f"/api/v1/employees/{employee['id']}/salary",
        json={"amount": "50000", "effective_date": "2022-01-01"},
    )
    assert response.json()["currency"] == "USD"


def test_add_salary_negative_amount_rejected(client):
    employee = create_employee(client)

    response = client.post(
        f"/api/v1/employees/{employee['id']}/salary",
        json={"amount": "-100", "effective_date": "2022-01-01"},
    )
    assert response.status_code == 422


def test_add_salary_future_date_rejected(client):
    employee = create_employee(client)
    future_date = (date.today() + timedelta(days=30)).isoformat()

    response = client.post(
        f"/api/v1/employees/{employee['id']}/salary",
        json={"amount": "50000", "effective_date": future_date},
    )
    assert response.status_code == 422


def test_add_salary_for_nonexistent_employee_returns_404(client):
    response = client.post(
        "/api/v1/employees/9999/salary",
        json={"amount": "50000", "effective_date": "2022-01-01"},
    )
    assert response.status_code == 404


def test_salary_history_lists_all_records_latest_first(client):
    employee = create_employee(client)
    client.post(
        f"/api/v1/employees/{employee['id']}/salary",
        json={"amount": "40000", "effective_date": "2022-01-01", "reason": "Hire"},
    )
    client.post(
        f"/api/v1/employees/{employee['id']}/salary",
        json={"amount": "45000", "effective_date": "2023-01-01", "reason": "Raise"},
    )

    response = client.get(f"/api/v1/employees/{employee['id']}/salary-history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 2
    assert history[0]["effective_date"] == "2023-01-01"
    assert history[1]["effective_date"] == "2022-01-01"


def test_current_salary_resolves_by_effective_date_not_insert_order(client):
    employee = create_employee(client)

    # Insert the later raise first, then backfill an earlier record - the
    # employee's "current" salary must still be the one with the latest
    # effective_date, not whichever row was inserted last.
    client.post(
        f"/api/v1/employees/{employee['id']}/salary",
        json={"amount": "60000", "effective_date": "2023-06-01", "reason": "Raise"},
    )
    client.post(
        f"/api/v1/employees/{employee['id']}/salary",
        json={"amount": "40000", "effective_date": "2022-01-01", "reason": "Hire"},
    )

    detail = client.get(f"/api/v1/employees/{employee['id']}").json()
    assert detail["current_salary"]["amount"] == "60000.00"
    assert detail["current_salary"]["effective_date"] == "2023-06-01"


def test_employee_detail_current_salary_is_null_with_no_records(client):
    employee = create_employee(client)

    detail = client.get(f"/api/v1/employees/{employee['id']}").json()
    assert detail["current_salary"] is None
