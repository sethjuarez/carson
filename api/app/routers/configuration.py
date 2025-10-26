import uuid
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..models import Settings, Configuration
from ..services import ConfigurationService
from ..dependencies import get_settings

router = APIRouter(prefix="/configuration", tags=["configuration"])


def get_configuration_service(
    settings: Settings = Depends(get_settings),
) -> ConfigurationService:
    """Get a ConfigurationService instance for configurations."""
    return ConfigurationService(
        connection_string=settings.database_connection,
        database_name=settings.database_name,
    )


@router.post(
    "/",
    response_model=Configuration,
    tags=["configuration"],
)
async def create_configuration(
    configuration: Configuration,
    service: ConfigurationService = Depends(get_configuration_service),
) -> Configuration:
    """Create a new configuration."""
    try:
        # Ensure container exists
        await service.create_container_if_not_exists(partition_key_path="/id")

        if not configuration.id:
            # Generate a new ID if not provided
            configuration.id = f"{configuration.name.lower().replace(' ', '-')}-{str(uuid.uuid4()).replace('-', '')[:8]}"

        # Upsert the configuration
        result = await service.upsert_item(configuration)
        return Configuration.model_validate(result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create configuration: {str(e)}"
        )


@router.get(
    "/{configuration_id}/",
    response_model=Configuration,
)
async def get_configuration(
    configuration_id: str,
    service: ConfigurationService = Depends(get_configuration_service),
) -> Configuration:
    """Get a configuration by ID."""
    try:
        result = await service.get_item(configuration_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return Configuration.model_validate(result.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get configuration: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[Configuration],
)
async def list_configurations(
    service: ConfigurationService = Depends(get_configuration_service),
) -> List[Configuration]:
    """List all configurations."""
    try:
        results = await service.get_items()
        return [Configuration.model_validate(item.model_dump()) for item in results]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list configurations: {str(e)}"
        )


@router.put(
    "/{configuration_id}/",
    response_model=Configuration,
)
async def update_configuration(
    configuration_id: str,
    configuration: Configuration,
    service: ConfigurationService = Depends(get_configuration_service),
) -> Configuration:
    """Update a configuration by ID."""
    try:
        # Check if configuration exists
        existing = await service.get_item(configuration_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Configuration not found")

        # Update the configuration ID to match the path parameter
        configuration.id = configuration_id

        # Upsert the updated configuration
        result = await service.upsert_item(configuration)
        return Configuration.model_validate(result.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update configuration: {str(e)}"
        )


@router.delete(
    "/{configuration_id}/",
)
async def delete_configuration(
    configuration_id: str,
    service: ConfigurationService = Depends(get_configuration_service),
) -> dict:
    """Delete a configuration by ID."""
    try:
        # Check if configuration exists
        existing = await service.get_item(configuration_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Configuration not found")

        # Delete the configuration
        async with service.get_cosmos_client() as container:
            await container.delete_item(
                item=configuration_id, partition_key=configuration_id
            )

        return {"message": f"Configuration {configuration_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete configuration: {str(e)}"
        )


@router.get(
    "/default/",
    response_model=Configuration,
)
async def get_default_configuration(
    service: ConfigurationService = Depends(get_configuration_service),
) -> Configuration:
    """Get the default configuration."""
    try:
        query = "SELECT * FROM c WHERE c.default = true"
        results = await service.query_items(query)

        if not results:
            raise HTTPException(
                status_code=404, detail="No default configuration found"
            )

        # Return the first default configuration found
        return Configuration.model_validate(results[0].model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get default configuration: {str(e)}"
        )


@router.patch(
    "/{configuration_id}/default/",
    response_model=Configuration,
)
async def set_default_configuration(
    configuration_id: str,
    service: ConfigurationService = Depends(get_configuration_service),
) -> Configuration:
    """Set a configuration as the default one."""
    try:
        # Check if configuration exists
        existing = await service.get_item(configuration_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Configuration not found")

        # First, unset all default flags
        await service.update_items(lambda item: {**item, "default": False})

        # Then set this configuration as default
        config_dict = existing.model_dump()
        config_dict["default"] = True
        updated_config = Configuration.model_validate(config_dict)

        result = await service.upsert_item(updated_config)
        return Configuration.model_validate(result.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to set default configuration: {str(e)}"
        )
