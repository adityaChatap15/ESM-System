"""Unit/API tests for employee CRUD - each test is independent and uses
the fresh in-memory DB from conftest.py."""


def make_employee_payload(employee_code, name="Test Employee", department="Engineering",
                           role="Engineer", country="India", join_date="2023-01-01"):
    return {
        "employee_code": employee_code,
        "name": name,
        "department": department,
        "role": role,
        "country": country,
        "join_date": join_date,
    }


def test_create_employee(client):
    response = client.post("/api/v1/employees", json=make_employee_payload("E001"))
    assert response.status_code == 201
    body = response.json()
    assert body["employee_code"] == "E001"
    assert body["is_active"] is True


def test_create_employee_duplicate_code_rejected(client):
    payload = make_employee_payload("E002")
    first = client.post("/api/v1/employees", json=payload)
    assert first.status_code == 201

    second = client.post("/api/v1/employees", json=payload)
    assert second.status_code == 400


def test_get_employee_not_found(client):
    response = client.get("/api/v1/employees/9999")
    assert response.status_code == 404


def test_list_employees_filters_by_department(client):
    client.post("/api/v1/employees", json=make_employee_payload("E010", department="Engineering"))
    client.post("/api/v1/employees", json=make_employee_payload("E011", department="Sales"))

    response = client.get("/api/v1/employees", params={"department": "Engineering"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["employee_code"] == "E010"


def test_list_employees_search_by_name(client):
    client.post("/api/v1/employees", json=make_employee_payload("E020", name="Priya Sharma"))

    response = client.get("/api/v1/employees", params={"search": "priya"})
    assert response.json()["total"] == 1


def test_list_employees_pagination(client):
    for i in range(5):
        client.post("/api/v1/employees", json=make_employee_payload(f"E10{i}"))

    response = client.get("/api/v1/employees", params={"page": 1, "page_size": 2})
    body = response.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2


def test_update_employee(client):
    created = client.post("/api/v1/employees", json=make_employee_payload("E030", name="Old Name")).json()

    response = client.put(f"/api/v1/employees/{created['id']}", json={"name": "New Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    # fields not sent in the update stay unchanged
    assert response.json()["department"] == "Engineering"


def test_employee_filters_returns_distinct_sorted_values(client):
    client.post("/api/v1/employees", json=make_employee_payload("H001", department="Sales", country="India", role="Executive"))
    client.post("/api/v1/employees", json=make_employee_payload("H002", department="Engineering", country="Germany", role="Engineer"))
    client.post("/api/v1/employees", json=make_employee_payload("H003", department="Sales", country="India", role="Executive"))

    response = client.get("/api/v1/employees/filters")
    assert response.status_code == 200
    body = response.json()
    assert body["departments"] == ["Engineering", "Sales"]
    assert body["countries"] == ["Germany", "India"]
    assert body["roles"] == ["Engineer", "Executive"]


def test_deactivate_employee_excluded_from_default_listing(client):
    created = client.post("/api/v1/employees", json=make_employee_payload("E040")).json()

    delete_response = client.delete(f"/api/v1/employees/{created['id']}")
    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    listing = client.get("/api/v1/employees")
    codes = [item["employee_code"] for item in listing.json()["items"]]
    assert "E040" not in codes

    listing_with_inactive = client.get("/api/v1/employees", params={"include_inactive": True})
    codes_with_inactive = [item["employee_code"] for item in listing_with_inactive.json()["items"]]
    assert "E040" in codes_with_inactive
