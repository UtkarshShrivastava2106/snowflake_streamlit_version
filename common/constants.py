"""
Platform-wide constants.

Do not place secrets or environment-specific credentials here.
"""

PLATFORM_NAME = "Snowflake Streamlit Platform"

ENV_NON_PROD = "GXHRUQB-LG41978" ##Utkarsh2001
ENV_PROD = "DQSHFQQ-YQ30334"

SUPPORTED_ENVIRONMENTS = {
    ENV_NON_PROD,
    ENV_PROD,
}

DEFAULT_DATABASE = "DB_STREAMLIT_APPS"

DASHBOARD_FUNCTIONS = {
    "finance",
    "sales",
    "hr",
    "operations",
}