from common.constants import (
    DEFAULT_DATABASE,
    ENV_NON_PROD,
    ENV_PROD,
    SUPPORTED_ENVIRONMENTS,
)
from common.utils import is_empty, normalize_string


def test_default_database():
    assert DEFAULT_DATABASE == "DB_STREAMLIT_APPS"


def test_supported_environments():
    assert ENV_NON_PROD in SUPPORTED_ENVIRONMENTS
    assert ENV_PROD in SUPPORTED_ENVIRONMENTS


def test_is_empty():
    assert is_empty(None)
    assert is_empty("")
    assert is_empty("   ")
    assert not is_empty("value")


def test_normalize_string():
    assert normalize_string("  hello  ") == "hello"
    assert normalize_string(None) == ""
