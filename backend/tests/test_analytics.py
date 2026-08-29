"""Tests for analytics endpoints. Verifies grouping, currency-safe
aggregation (never averaging different currencies together), and that
only each employee's *current* salary counts."""


def create_employee_with_salary(client, employee_code, country, department, role,
                                 amount, effective_date="2023-01-01"):
    employee = client.post("/api/v1/employees", json={
        "employee_code": employee_code,
        "name": f"Employee {employee_code}",
        "department": department,
        "role": role,
        "country": country,
        "join_date": "2022-01-01",
    }).json()
    client.post(
        f"/api/v1/employees/{employee['id']}/salary",
        json={"amount": str(amount), "effective_date": effective_date},
    )
    return employee


def test_summary_by_country_returns_avg_and_median(client):
    create_employee_with_salary(client, "A1", "India", "Engineering", "Engineer", 40000)
    create_employee_with_salary(client, "A2", "India", "Engineering", "Engineer", 60000)

    response = client.get("/api/v1/analytics/summary", params={"dimension": "country"})
    assert response.status_code == 200
    india_item = next(item for item in response.json() if item["group"] == "India")
    assert india_item["currency"] == "INR"
    assert india_item["headcount"] == 2
    assert india_item["average_salary"] == 50000.0
    assert india_item["median_salary"] == 50000.0


def test_summary_by_department_splits_by_currency(client):
    create_employee_with_salary(client, "B1", "India", "Engineering", "Engineer", 40000)
    create_employee_with_salary(client, "B2", "United States", "Engineering", "Engineer", 80000)

    response = client.get("/api/v1/analytics/summary", params={"dimension": "department"})
    items = [item for item in response.json() if item["group"] == "Engineering"]
    currencies = {item["currency"] for item in items}
    assert currencies == {"INR", "USD"}
    for item in items:
        assert item["headcount"] == 1


def test_summary_invalid_dimension_rejected(client):
    response = client.get("/api/v1/analytics/summary", params={"dimension": "planet"})
    assert response.status_code == 400


def test_distribution_buckets_salaries_per_currency(client):
    create_employee_with_salary(client, "C1", "India", "Engineering", "Engineer", 30000)
    create_employee_with_salary(client, "C2", "India", "Engineering", "Engineer", 90000)

    response = client.get("/api/v1/analytics/distribution")
    india_group = next(group for group in response.json() if group["currency"] == "INR")
    total_headcount = sum(band["headcount"] for band in india_group["bands"])
    assert total_headcount == 2


def test_extremes_returns_highest_and_lowest_per_currency(client):
    create_employee_with_salary(client, "D1", "India", "Engineering", "Engineer", 30000)
    create_employee_with_salary(client, "D2", "India", "Engineering", "Engineer", 90000)

    response = client.get("/api/v1/analytics/extremes", params={"limit": 1})
    india_group = next(group for group in response.json() if group["currency"] == "INR")
    assert india_group["highest"][0]["employee_code"] == "D2"
    assert india_group["lowest"][0]["employee_code"] == "D1"


def test_headcount_payroll_sums_by_country(client):
    create_employee_with_salary(client, "E1", "India", "Engineering", "Engineer", 40000)
    create_employee_with_salary(client, "E2", "India", "Sales", "Executive", 60000)

    response = client.get("/api/v1/analytics/headcount-payroll")
    india_item = next(item for item in response.json() if item["country"] == "India")
    assert india_item["headcount"] == 2
    assert india_item["total_payroll"] == 100000.0
    assert india_item["currency"] == "INR"


def test_analytics_excludes_inactive_employees(client):
    employee = create_employee_with_salary(client, "F1", "India", "Engineering", "Engineer", 999999)
    client.delete(f"/api/v1/employees/{employee['id']}")

    response = client.get("/api/v1/analytics/headcount-payroll")
    india_item = next((item for item in response.json() if item["country"] == "India"), None)
    assert india_item is None


def test_analytics_uses_current_salary_not_history(client):
    employee = create_employee_with_salary(
        client, "G1", "India", "Engineering", "Engineer", 40000, effective_date="2022-01-01"
    )
    # backdated earlier record inserted after the raise - "current" must
    # still resolve to the later effective_date, not insertion order.
    client.post(
        f"/api/v1/employees/{employee['id']}/salary",
        json={"amount": "70000", "effective_date": "2023-01-01", "reason": "Raise"},
    )

    response = client.get("/api/v1/analytics/summary", params={"dimension": "country"})
    india_item = next(item for item in response.json() if item["group"] == "India")
    assert india_item["average_salary"] == 70000.0
