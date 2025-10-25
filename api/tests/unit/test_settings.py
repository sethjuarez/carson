"""
Unit tests for the Settings model.

Tests the Pydantic settings configuration and validation.
"""

import pytest
import os
from unittest.mock import patch

# Import the settings model
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.models.settings import Settings


def test_settings_creation_with_all_fields():
    """Test creating settings with all required fields."""
    settings = Settings(
        storage_connection="https://test.blob.core.windows.net",
        storage_container="test-container",
        database_connection="test-db-connection",
        client_id="test-client",
    )

    assert settings.storage_connection == "https://test.blob.core.windows.net"
    assert settings.storage_container == "test-container"
    assert settings.database_connection == "test-db-connection"
    assert settings.client_id == "test-client"


def test_settings_default_client_id():
    """Test that client_id defaults to 'LOCAL'."""
    settings = Settings(
        storage_connection="https://test.blob.core.windows.net",
        storage_container="test-container",
        database_connection="test-db-connection",
    )

    assert settings.client_id == "LOCAL"


@patch.dict(
    os.environ,
    {
        "APP_STORAGE_CONNECTION": "https://env.blob.core.windows.net",
        "APP_STORAGE_CONTAINER": "env-container",
        "APP_DATABASE_CONNECTION": "env-db-connection",
        "APP_CLIENT_ID": "env-client",
    },
)
def test_settings_from_environment_variables():
    """Test loading settings from environment variables with APP_ prefix."""
    settings = Settings()

    assert settings.storage_connection == "https://env.blob.core.windows.net"
    assert settings.storage_container == "env-container"
    assert settings.database_connection == "env-db-connection"
    assert settings.client_id == "env-client"


@patch.dict(
    os.environ,
    {
        "APP_STORAGE_CONNECTION": "https://env.blob.core.windows.net",
        "APP_STORAGE_CONTAINER": "env-container",
        "APP_DATABASE_CONNECTION": "env-db-connection",
        # No APP_CLIENT_ID set
    },
)
def test_settings_env_with_default_client_id():
    """Test that default client_id is used when not set in environment."""
    settings = Settings()

    assert settings.client_id == "LOCAL"


def test_settings_override_with_explicit_values():
    """Test that explicit values override environment variables."""
    with patch.dict(
        os.environ,
        {
            "APP_STORAGE_CONNECTION": "https://env.blob.core.windows.net",
            "APP_STORAGE_CONTAINER": "env-container",
            "APP_DATABASE_CONNECTION": "env-db-connection",
            "APP_CLIENT_ID": "env-client",
        },
    ):
        settings = Settings(
            storage_connection="https://override.blob.core.windows.net",
            storage_container="override-container",
            database_connection="override-db-connection",
            client_id="override-client",
        )

        assert settings.storage_connection == "https://override.blob.core.windows.net"
        assert settings.storage_container == "override-container"
        assert settings.database_connection == "override-db-connection"
        assert settings.client_id == "override-client"


def test_settings_string_types():
    """Test that all settings fields are strings."""
    settings = Settings(
        storage_connection="https://test.blob.core.windows.net",
        storage_container="test-container",
        database_connection="test-db-connection",
        client_id="test-client",
    )

    assert isinstance(settings.storage_connection, str)
    assert isinstance(settings.storage_container, str)
    assert isinstance(settings.database_connection, str)
    assert isinstance(settings.client_id, str)


def test_settings_empty_strings_validation():
    """Test behavior with empty strings (should be valid)."""
    settings = Settings(
        storage_connection="",
        storage_container="",
        database_connection="",
        client_id="",
    )

    assert settings.storage_connection == ""
    assert settings.storage_container == ""
    assert settings.database_connection == ""
    assert settings.client_id == ""


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__])
