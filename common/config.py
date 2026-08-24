"""
Central configuration for the Streamlit platform.

Environment-specific values should come from Streamlit secrets,
environment variables, or the deployment environment.
"""

import os
from dataclasses import dataclass

from common.constants import ENV_NON_PROD, ENV_PROD
from common.exceptions import ConfigurationError


@dataclass(frozen=True)
class SnowflakeConfig:
    account: str
    user: str | None
    role: str
    warehouse: str
    database: str
    schema: str


def get_environment() -> str:
    environment = os.getenv("STREAMLIT_ENV", ENV_NON_PROD).upper()

    if environment not in {ENV_NON_PROD, ENV_PROD}:
        raise ConfigurationError(
            f"Unsupported STREAMLIT_ENV: {environment}"
        )

    return environment


def get_snowflake_config() -> SnowflakeConfig:
    required_values = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE", "DB_STREAMLIT"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    }

    missing = [
        key for key, value in required_values.items()
        if not value
    ]

    if missing:
        raise ConfigurationError(
            f"Missing Snowflake configuration: {', '.join(missing)}"
        )

    return SnowflakeConfig(
        account=required_values["account"],
        user=os.getenv("SNOWFLAKE_USER"),
        role=required_values["role"],
        warehouse=required_values["warehouse"],
        database=required_values["database"],
        schema=required_values["schema"],
    )