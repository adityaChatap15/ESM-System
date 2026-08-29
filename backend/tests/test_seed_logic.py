"""Tests for the pure-logic parts of the seed script. The full 10k-row
run itself is exercised manually against a real database (see README) -
these tests check the building blocks are individually correct."""
from datetime import date

from scripts.seed import (
    DEPARTMENT_ROLES,
    LEVEL_USD_BAND,
    build_employee,
    build_salary_history,
    random_join_date,
    random_salary_for_level,
    weighted_choice,
)


def test_weighted_choice_only_returns_known_options():
    weights = {"a": 10, "b": 1}
    results = {weighted_choice(weights) for _ in range(50)}
    assert results <= {"a", "b"}


def test_random_join_date_is_in_the_past():
    for _ in range(20):
        assert random_join_date() < date.today()


def test_random_salary_for_level_is_positive_for_every_level():
    for level in LEVEL_USD_BAND:
        assert random_salary_for_level(level, "India") > 0


def test_build_employee_role_matches_its_department():
    employee, level = build_employee(1)
    assert employee.role in DEPARTMENT_ROLES[employee.department]
    assert 0 <= level <= 4


def test_build_salary_history_starts_with_hire_record_on_join_date():
    employee, level = build_employee(2)
    history = build_salary_history(employee, level)
    assert history[0].effective_date == employee.join_date
    assert history[0].reason == "Hire"


def test_build_salary_history_records_are_chronological():
    employee, level = build_employee(3)
    history = build_salary_history(employee, level)
    dates = [record.effective_date for record in history]
    assert dates == sorted(dates)


def test_build_salary_history_never_dated_in_the_future():
    employee, level = build_employee(4)
    history = build_salary_history(employee, level)
    for record in history:
        assert record.effective_date < date.today()
