"""
Security and authorization helpers.

Actual Snowflake privileges remain controlled in Snowflake.
This module provides application-level checks where required.
"""

from common.exceptions import AuthorizationError


def require_role(
    current_role: str | None,
    allowed_roles: set[str],
) -> None:
    """
    Validate that the current role is authorized.
    """

    if not current_role:
        raise AuthorizationError(
            "Unable to determine the current Snowflake role."
        )

    if current_role.upper() not in {
        role.upper() for role in allowed_roles
    }:
        raise AuthorizationError(
            f"Role '{current_role}' is not authorized."
        )