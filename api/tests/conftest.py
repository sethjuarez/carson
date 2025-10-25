"""
Pytest configuration and fixtures for the Carson API test suite.

This module provides shared fixtures and configuration for all tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.services import StorageService
from app.models import Settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI application."""
    async with AsyncClient(base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings for testing."""
    return Settings(
        storage_connection="https://teststorage.blob.core.windows.net",
        storage_container="test-container",
        database_connection="test-database-connection",
        client_id="test-client-id",
    )


@pytest.fixture
def mock_azure_credential():
    """Mock Azure credential for testing."""
    mock_credential = AsyncMock()
    mock_credential.close = AsyncMock()
    return mock_credential


@pytest.fixture
def mock_blob_service_client():
    """Mock Azure Blob Service Client for testing."""
    mock_client = AsyncMock()
    mock_client.close = AsyncMock()

    # Mock container client
    mock_container_client = AsyncMock()
    mock_container_client.exists = AsyncMock(return_value=True)
    mock_container_client.create_container = AsyncMock()
    mock_container_client.upload_blob = AsyncMock()

    mock_client.get_container_client.return_value = mock_container_client
    return mock_client


@pytest.fixture
def mock_storage_service(
    mock_settings, mock_blob_service_client, mock_azure_credential
):
    """Create a mock storage service for testing."""
    service = StorageService(
        client_id=mock_settings.client_id,
        storage=mock_settings.storage_connection,
        container=mock_settings.storage_container,
    )


    return service


@pytest.fixture
def sample_base64_image() -> str:
    """Sample base64-encoded image data for testing."""
    # This is a minimal 1x1 pixel PNG image
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="


@pytest.fixture
def sample_invalid_base64() -> str:
    """Invalid base64 data for testing error cases."""
    return "invalid-base64-data!"


@pytest.fixture
def sample_image_list() -> list[str]:
    """List of sample base64-encoded images for batch testing."""
    base_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    return [base_image, base_image, base_image]


# Async test marker configuration
pytest_plugins = ["pytest_asyncio"]
