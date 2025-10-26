"""
Integration test examples for Configuration CRUD operations.

This module demonstrates how to test the configuration CRUD endpoints
with realistic data and scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Configuration, ToolConfiguration, ToolParameter
from app.routers.configuration import get_configuration_service


@pytest.fixture
def sample_ai_configuration():
    """Create a sample AI assistant configuration."""
    return Configuration(
        id="ai-assistant-config",
        name="AI Assistant Configuration",
        content="Configuration for a multi-purpose AI assistant with image and text processing capabilities",
        default=True,
        tools=[
            ToolConfiguration(
                name="generate_image",
                description="Generate images based on text descriptions",
                parameters=[
                    ToolParameter(
                        name="prompt",
                        type="string",
                        description="Text description of the image to generate",
                        required=True,
                    ),
                    ToolParameter(
                        name="style",
                        type="string",
                        description="Art style for the image",
                        required=False,
                    ),
                    ToolParameter(
                        name="width",
                        type="integer",
                        description="Image width in pixels",
                        required=False,
                    ),
                    ToolParameter(
                        name="height",
                        type="integer",
                        description="Image height in pixels",
                        required=False,
                    ),
                ],
            ),
            ToolConfiguration(
                name="analyze_sentiment",
                description="Analyze the sentiment of given text",
                parameters=[
                    ToolParameter(
                        name="text",
                        type="string",
                        description="Text to analyze for sentiment",
                        required=True,
                    ),
                    ToolParameter(
                        name="detailed",
                        type="boolean",
                        description="Return detailed sentiment analysis",
                        required=False,
                    ),
                ],
            ),
            ToolConfiguration(
                name="search_web",
                description="Search the web for information",
                parameters=[
                    ToolParameter(
                        name="query",
                        type="string",
                        description="Search query",
                        required=True,
                    ),
                    ToolParameter(
                        name="max_results",
                        type="integer",
                        description="Maximum number of results to return",
                        required=False,
                    ),
                    ToolParameter(
                        name="safe_search",
                        type="boolean",
                        description="Enable safe search filtering",
                        required=False,
                    ),
                ],
            ),
        ],
    )


@pytest.fixture
def mock_cosmos_service_with_data():
    """Create a mock CosmosService with some predefined data."""
    from unittest.mock import AsyncMock

    mock_service = AsyncMock()
    mock_service.create_container_if_not_exists = AsyncMock()
    mock_service.upsert_item = AsyncMock()
    mock_service.get_item = AsyncMock()
    mock_service.get_items = AsyncMock()
    mock_service.query_items = AsyncMock()
    mock_service.update_items = AsyncMock()

    # Simulated data store
    configurations = {}

    def mock_upsert(config):
        configurations[config.id] = config
        return config

    def mock_get(config_id):
        return configurations.get(config_id)

    def mock_get_all():
        return list(configurations.values())

    def mock_query(query):
        if "default = true" in query:
            return [config for config in configurations.values() if config.default]
        return []

    def mock_update_defaults(mapper_func):
        # Update all configurations to set default=False
        for config_id, config in configurations.items():
            updated_dict = mapper_func(config.model_dump())
            configurations[config_id] = Configuration.model_validate(updated_dict)

    mock_service.upsert_item.side_effect = mock_upsert
    mock_service.get_item.side_effect = mock_get
    mock_service.get_items.side_effect = mock_get_all
    mock_service.query_items.side_effect = mock_query
    mock_service.update_items.side_effect = mock_update_defaults

    return mock_service


class TestConfigurationIntegration:
    """Integration tests with realistic configuration data."""

    def test_complete_configuration_workflow(
        self, sample_ai_configuration, mock_cosmos_service_with_data
    ):
        """Test a complete workflow of creating, updating, and managing configurations."""

        # Setup dependency override
        def override_get_configuration_service():
            return mock_cosmos_service_with_data

        app.dependency_overrides[get_configuration_service] = (
            override_get_configuration_service
        )
        client = TestClient(app)

        try:
            # 1. Create the AI configuration
            response = client.post(
                "/configurations/", json=sample_ai_configuration.model_dump()
            )
            assert response.status_code == 200
            created_config = response.json()

            # Verify the configuration was created with all tools
            assert created_config["id"] == sample_ai_configuration.id
            assert created_config["name"] == sample_ai_configuration.name
            assert len(created_config["tools"]) == 3
            assert created_config["default"] is True

            # Verify tool details
            generate_tool = next(
                tool
                for tool in created_config["tools"]
                if tool["name"] == "generate_image"
            )
            assert len(generate_tool["parameters"]) == 4
            assert generate_tool["parameters"][0]["name"] == "prompt"
            assert generate_tool["parameters"][0]["required"] is True

            # 2. Get the configuration by ID
            response = client.get(f"/configurations/{sample_ai_configuration.id}")
            assert response.status_code == 200
            retrieved_config = response.json()
            assert retrieved_config["id"] == sample_ai_configuration.id

            # 3. List all configurations
            response = client.get("/configurations/")
            assert response.status_code == 200
            all_configs = response.json()
            assert len(all_configs) == 1
            assert all_configs[0]["id"] == sample_ai_configuration.id

            # 4. Get the default configuration
            response = client.get("/configurations/default/active")
            assert response.status_code == 200
            default_config = response.json()
            assert default_config["id"] == sample_ai_configuration.id
            assert default_config["default"] is True

            # 5. Create a second configuration
            coding_config = Configuration(
                id="coding-assistant-config",
                name="Coding Assistant",
                content="Configuration for coding assistance",
                default=False,
                tools=[
                    ToolConfiguration(
                        name="format_code",
                        description="Format code in various languages",
                        parameters=[
                            ToolParameter(
                                name="code",
                                type="string",
                                description="Code to format",
                                required=True,
                            ),
                            ToolParameter(
                                name="language",
                                type="string",
                                description="Programming language",
                                required=True,
                            ),
                        ],
                    )
                ],
            )

            response = client.post("/configurations/", json=coding_config.model_dump())
            assert response.status_code == 200

            # 6. Now list should have 2 configurations
            response = client.get("/configurations/")
            assert response.status_code == 200
            all_configs = response.json()
            assert len(all_configs) == 2

            # 7. Set the coding config as default
            response = client.patch(f"/configurations/{coding_config.id}/set-default")
            assert response.status_code == 200
            updated_config = response.json()
            assert updated_config["default"] is True

            # 8. Verify the new default
            response = client.get("/configurations/default/active")
            assert response.status_code == 200
            default_config = response.json()
            assert default_config["id"] == coding_config.id

            # 9. Update the AI configuration
            updated_ai_config = sample_ai_configuration.model_copy()
            updated_ai_config.content = (
                "Updated AI assistant configuration with enhanced capabilities"
            )
            updated_ai_config.tools.append(
                ToolConfiguration(
                    name="translate_text",
                    description="Translate text between languages",
                    parameters=[
                        ToolParameter(
                            name="text",
                            type="string",
                            description="Text to translate",
                            required=True,
                        ),
                        ToolParameter(
                            name="target_language",
                            type="string",
                            description="Target language",
                            required=True,
                        ),
                        ToolParameter(
                            name="source_language",
                            type="string",
                            description="Source language",
                            required=False,
                        ),
                    ],
                )
            )

            response = client.put(
                f"/configurations/{sample_ai_configuration.id}",
                json=updated_ai_config.model_dump(),
            )
            assert response.status_code == 200
            updated_config = response.json()
            assert len(updated_config["tools"]) == 4  # Original 3 + 1 new tool
            assert "enhanced capabilities" in updated_config["content"]

        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    def test_tool_parameter_conversion(
        self, sample_ai_configuration, mock_cosmos_service_with_data
    ):
        """Test that tool configurations can be converted to function parameters."""

        # Setup dependency override
        def override_get_configuration_service():
            return mock_cosmos_service_with_data

        app.dependency_overrides[get_configuration_service] = (
            override_get_configuration_service
        )
        client = TestClient(app)

        try:
            # Create configuration
            response = client.post(
                "/configurations/", json=sample_ai_configuration.model_dump()
            )
            assert response.status_code == 200
            created_config = response.json()

            # Manually test the function parameter conversion
            config_obj = Configuration.model_validate(created_config)
            for tool in config_obj.tools:
                function_params = tool.convert_function_params()

                # Verify the structure matches OpenAI function calling format
                assert function_params["type"] == "object"
                assert "properties" in function_params
                assert "required" in function_params

                # Check that required parameters are properly identified
                required_params = function_params["required"]
                for param in tool.parameters:
                    if param.required:
                        assert param.name in required_params
                    else:
                        assert param.name not in required_params

                # Check parameter definitions
                for param in tool.parameters:
                    assert param.name in function_params["properties"]
                    param_def = function_params["properties"][param.name]
                    assert param_def["type"] == param.type
                    if param.description:
                        assert param_def["description"] == param.description
                    else:
                        assert param_def["description"] == "No Description"

        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    def test_error_handling_scenarios(self, mock_cosmos_service_with_data):
        """Test various error scenarios."""

        # Setup dependency override
        def override_get_configuration_service():
            return mock_cosmos_service_with_data

        app.dependency_overrides[get_configuration_service] = (
            override_get_configuration_service
        )
        client = TestClient(app)

        try:
            # Test getting non-existent configuration
            response = client.get("/configurations/non-existent-id")
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

            # Test updating non-existent configuration
            dummy_config = Configuration(id="dummy", name="Dummy", content="Test")
            response = client.put(
                "/configurations/non-existent-id", json=dummy_config.model_dump()
            )
            assert response.status_code == 404

            # Test setting non-existent configuration as default
            response = client.patch("/configurations/non-existent-id/set-default")
            assert response.status_code == 404

            # Test getting default when none exists
            response = client.get("/configurations/default/active")
            assert response.status_code == 404
            assert "no default configuration found" in response.json()["detail"].lower()

            # Test creating configuration with invalid data
            invalid_config = {
                "id": "",  # Empty ID
                "tools": [
                    {"parameters": [{"required": "not_a_boolean"}]}  # Invalid boolean
                ],
            }
            response = client.post("/configurations/", json=invalid_config)
            assert response.status_code == 422

        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()


