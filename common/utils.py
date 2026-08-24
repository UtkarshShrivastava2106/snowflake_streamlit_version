"""General reusable utility functions."""

from typing import Any


def is_empty(value: Any) -> bool:
    """Return True when a value is None or empty."""

    if value is None:
        return True

    if isinstance(value, str):
        return not value.strip()

    return False


def normalize_string(value: str | None) -> str:
    """Normalize a string value."""

    if value is None:
        return ""

    return value.strip()