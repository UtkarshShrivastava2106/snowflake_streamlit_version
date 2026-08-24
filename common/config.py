import os
from dataclasses import dataclass

from common.constants import ENV_NON_PROD, ENV_PROD
from common.exceptions import ConfigurationError


@dataclass(frozen=True)
class SnowflakeConfig:
    environment: str
    database: str
    schema: str


ENVIRONMENT_DATABASES = {
    ENV_NON_PROD: "DB_G_GIT_UAT",
    ENV_PROD: "DB_G_PROD",
}


def get_environment() -> str:

    environment = os.getenv(
        "STREAMLIT_ENV",
        ENV_NON_PROD,
    ).upper()

    if environment not in ENVIRONMENT_DATABASES:
        raise ConfigurationError(
            f"Unsupported environment: {environment}"
        )

    return environment


def get_snowflake_config() -> SnowflakeConfig:

    environment = get_environment()

    return SnowflakeConfig(
        environment=environment,
        database=ENVIRONMENT_DATABASES[environment],
        schema=os.getenv(
            "SNOWFLAKE_SCHEMA",
            "FINANCE",
        ),
    )