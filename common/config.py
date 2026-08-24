"""
Central Snowflake environment configuration.

The application determines the current environment from the
Snowflake account and resolves logical database names to the
correct physical database.

Example:

    Logical database: G

    UAT:
        G -> DB_G_GIT_UAT

    PROD:
        G -> DB_G_PROD

Example:

    Logical database: S

    UAT:
        S -> DB_S_GIT_UAT

    PROD:
        S -> DB_S_PROD

Schema names are NOT environment mapped because they are expected
to remain the same across environments.
"""

from dataclasses import dataclass


# ============================================================
# ACCOUNT / ENVIRONMENT CONFIGURATION
# ============================================================

ACCOUNT_CONFIG = {

    # ========================================================
    # UAT
    # ========================================================

    "LG41978": {
        "environment": "UAT",

        "databases": {
            "G": "DB_G_GIT_UAT",
            "S": "DB_S_GIT_UAT",
        },
    },

    # ========================================================
    # PROD
    # ========================================================

    # Replace YOUR_PROD_ACCOUNT with the actual PROD
    # CURRENT_ACCOUNT() value.

    "YQ30334": {
        "environment": "PROD",

        "databases": {
            "G": "DB_G_PROD",
            "S": "DB_S_PROD",
        },
    },
}


# ============================================================
# CONFIGURATION OBJECT
# ============================================================

@dataclass(frozen=True)
class SnowflakeConfig:

    account: str
    environment: str


# ============================================================
# GET CURRENT ACCOUNT
# ============================================================

def get_current_account(session) -> str:
    """
    Get the Snowflake account in which the Streamlit
    application is currently running.
    """

    result = session.sql(
        """
        SELECT CURRENT_ACCOUNT()
        """
    ).collect()

    if not result:
        raise RuntimeError(
            "Unable to determine Snowflake account."
        )

    account = result[0][0]

    if not account:
        raise RuntimeError(
            "CURRENT_ACCOUNT() returned an empty value."
        )

    return str(account).strip().upper()


# ============================================================
# GET ENVIRONMENT CONFIGURATION
# ============================================================

def get_snowflake_config(session) -> SnowflakeConfig:
    """
    Resolve the environment using CURRENT_ACCOUNT().
    """

    account = get_current_account(session)

    account_config = ACCOUNT_CONFIG.get(account)

    if account_config is None:

        raise RuntimeError(
            f"Snowflake account '{account}' is not configured "
            "in ACCOUNT_CONFIG."
        )

    return SnowflakeConfig(
        account=account,
        environment=account_config["environment"],
    )


# ============================================================
# GET DATABASE
# ============================================================

def get_database(
    config: SnowflakeConfig,
    database_key: str,
) -> str:
    """
    Resolve a logical database key to the physical database.

    Example:

        get_database(config, "G")

    UAT:
        DB_G_GIT_UAT

    PROD:
        DB_G_PROD
    """

    account_config = ACCOUNT_CONFIG.get(
        config.account
    )

    if account_config is None:
        raise RuntimeError(
            f"No configuration found for account "
            f"'{config.account}'."
        )

    databases = account_config.get(
        "databases",
        {}
    )

    database = databases.get(
        database_key.upper()
    )

    if database is None:

        raise RuntimeError(
            f"Database key '{database_key}' is not configured "
            f"for environment '{config.environment}'."
        )

    return database


# ============================================================
# BUILD FULL OBJECT NAME
# ============================================================

def get_object_name(
    config: SnowflakeConfig,
    database_key: str,
    schema: str,
    object_name: str,
) -> str:
    """
    Build a fully qualified Snowflake object name.

    Example:

        get_object_name(
            config,
            "G",
            "FINANCE",
            "ORDERS"
        )

    UAT:

        DB_G_GIT_UAT.FINANCE.ORDERS

    PROD:

        DB_G_PROD.FINANCE.ORDERS
    """

    if not schema:
        raise ValueError(
            "Schema cannot be empty."
        )

    if not object_name:
        raise ValueError(
            "Object name cannot be empty."
        )

    database = get_database(
        config,
        database_key,
    )

    return (
        f"{database}."
        f"{schema}."
        f"{object_name}"
    )


# ============================================================
# VALIDATE CONFIGURATION
# ============================================================

def validate_config(
    config: SnowflakeConfig,
) -> None:
    """
    Validate the current Snowflake environment.
    """

    if not config.account:
        raise RuntimeError(
            "Snowflake account is missing."
        )

    if not config.environment:
        raise RuntimeError(
            "Snowflake environment is missing."
        )

    if config.account not in ACCOUNT_CONFIG:
        raise RuntimeError(
            f"Snowflake account '{config.account}' "
            "is not configured."
        )


# ============================================================
# CONFIGURATION SUMMARY
# ============================================================

def get_config_summary(
    config: SnowflakeConfig,
) -> dict:
    """
    Return a configuration summary useful for logging
    and displaying the current environment.
    """

    account_config = ACCOUNT_CONFIG[
        config.account
    ]

    return {
        "account": config.account,
        "environment": config.environment,
        "databases": account_config["databases"],
    }