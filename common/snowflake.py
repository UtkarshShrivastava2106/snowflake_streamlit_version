"""
Centralized Snowflake session management.

Dashboard applications should use this module instead of
creating their own Snowpark session implementation.
"""

from snowflake.snowpark import Session

from common.config import get_snowflake_config
from common.exceptions import SnowflakeConnectionError


def create_snowflake_session() -> Session:
    """
    Create a Snowpark session using centralized configuration.
    """

    try:
        config = get_snowflake_config()

        connection_parameters = {
            "account": config.account,
            "role": config.role,
            "warehouse": config.warehouse,
            "database": config.database,
            "schema": config.schema,
        }

        if config.user:
            connection_parameters["user"] = config.user

        return Session.builder.configs(
            connection_parameters
        ).create()

    except Exception as exc:
        raise SnowflakeConnectionError(
            "Unable to create Snowflake session."
        ) from exc