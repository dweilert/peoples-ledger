from __future__ import annotations

from typing import Any


HOUSEHOLD_FINANCIAL_KEYS = {
    "adjusted_gross_income",
    "agi",
    "bank_account",
    "household_income",
    "income",
    "net_worth",
    "payroll",
    "ssn",
    "taxpayer_id",
    "w2",
}


class HouseholdFinancialDataError(ValueError):
    """Raised when private household financial data is about to be stored or sent."""


def assert_no_household_financial_data(payload: Any) -> None:
    offending = sorted(_find_offending_keys(payload))
    if offending:
        raise HouseholdFinancialDataError(
            "household financial data is not permitted in this POC: " + ", ".join(offending)
        )


def _find_offending_keys(payload: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(payload, dict):
        for key, value in payload.items():
            normalized = key.lower().replace("-", "_")
            if normalized in HOUSEHOLD_FINANCIAL_KEYS:
                found.add(key)
            found.update(_find_offending_keys(value))
    elif isinstance(payload, list):
        for item in payload:
            found.update(_find_offending_keys(item))
    return found
