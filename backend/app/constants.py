"""
Country -> currency lookup. Salary is always stored in the employee's local
currency (see docs/requirements.md - no FX conversion in scope), so the
currency is derived from the employee's country instead of being sent by
the client.
"""

COUNTRY_CURRENCY = {
    "India": "INR",
    "United States": "USD",
    "United Kingdom": "GBP",
    "Germany": "EUR",
    "Canada": "CAD",
    "Australia": "AUD",
    "Singapore": "SGD",
    "Japan": "JPY",
    "Brazil": "BRL",
    "United Arab Emirates": "AED",
}


def currency_for_country(country):
    return COUNTRY_CURRENCY.get(country, "USD")
