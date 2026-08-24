"""Custom exceptions used across the Streamlit platform."""


class StreamlitPlatformError(Exception):
    """Base exception for the Streamlit platform."""


class ConfigurationError(StreamlitPlatformError):
    """Raised when platform configuration is invalid."""


class SnowflakeConnectionError(StreamlitPlatformError):
    """Raised when a Snowflake connection cannot be established."""


class AuthorizationError(StreamlitPlatformError):
    """Raised when the current user lacks required authorization."""