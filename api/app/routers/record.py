import uuid
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..services.cosmos import CosmosService
from ..dependencies import get_settings

from ..models import Record, Settings


def get_record_service(
    container: str,
    type: str,
    settings: Settings,
) -> CosmosService:
    """Get a RecordService instance for records."""
    return CosmosService(
        connection_string=settings.database_connection,
        database_name=settings.database_name,
        container_name=container,
        type=type,
    )


async def create_record(record: Record, service: CosmosService) -> Record:
    """Create a new record."""
    try:
        # Ensure container exists
        await service.create_container_if_not_exists(partition_key_path="/id")

        if not record.id:
            # Generate a new ID if not provided
            record.id = f"{record.name.lower().replace(' ', '-')}-{str(uuid.uuid4()).replace('-', '')[:8]}"

        # Upsert the record
        record.type = service.type
        result = await service.upsert_item(record)
        return Record.model_validate(result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create record: {str(e)}"
        )


async def get_record(record_id: str, service: CosmosService) -> Record:
    """Get a record by ID."""
    try:
        result = await service.get_item(record_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return Record.model_validate(result.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get record: {str(e)}")


async def list_records(service: CosmosService) -> List[Record]:
    """List all records."""
    try:
        results = await service.get_items()
        return [Record.model_validate(item.model_dump()) for item in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list records: {str(e)}")


async def update_record(
    record_id: str,
    record: Record,
    service: CosmosService,
) -> Record:
    """Update a record by ID."""
    try:
        # Check if record exists
        existing = await service.get_item(record_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Record not found")

        # Update the record ID to match the path parameter
        record.id = record_id

        # Upsert the updated record
        result = await service.upsert_item(record)
        return Record.model_validate(result.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update record: {str(e)}"
        )


async def delete_record(
    record_id: str,
    service: CosmosService,
) -> dict:
    """Delete a record by ID."""
    try:
        # Check if record exists
        existing = await service.get_item(record_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Record not found")

        # Delete the record
        async with service.get_cosmos_client() as container:
            await container.delete_item(item=record_id, partition_key=record_id)

        return {"message": f"Record {record_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete record: {str(e)}"
        )


async def get_default_record(
    service: CosmosService,
) -> Record:
    """Get the default record."""
    try:
        query = "SELECT * FROM c WHERE c.default = true"
        results = await service.query_items(query)

        if not results:
            raise HTTPException(status_code=404, detail="No default record found")

        # Return the first default record found
        return Record.model_validate(results[0].model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get default record: {str(e)}"
        )


async def set_default_record(
    record_id: str,
    service: CosmosService,
) -> Record:
    """Set a record as the default one."""
    try:
        # Check if record exists
        existing = await service.get_item(record_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Record not found")

        # First, unset all default flags
        await service.update_items(lambda item: {**item, "default": False})

        # Then set this record as default
        record_dict = existing.model_dump()
        record_dict["default"] = True
        updated_record = Record.model_validate(record_dict)

        result = await service.upsert_item(updated_record)
        return Record.model_validate(result.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to set default record: {str(e)}"
        )


def create_router(database: str, type: str) -> APIRouter:

    router = APIRouter(prefix=f"/{type}", tags=[type])

    def get_api_service(
        settings=Depends(get_settings),
    ) -> CosmosService:
        return get_record_service(
            container=database,
            settings=settings,
            type=type,
        )

    @router.post(
        "/",
        response_model=Record,
        tags=[type],
        summary=f"Create a new {type}",
        description=f"Create a new {type}.",
    )
    async def create_api(
        record: Record,
        service: CosmosService = Depends(get_api_service),
    ) -> Record:
        f"""Create a new {type}."""
        return await create_record(record, service)

    @router.get(
        "/{id}/",
        response_model=Record,
        tags=[type],
        summary=f"Get a {type} by ID",
        description=f"Get a {type} by its ID.",
    )
    async def get_api(
        id: str,
        service: CosmosService = Depends(get_api_service),
    ) -> Record:
        f"""Get a {type} by ID."""
        return await get_record(id, service)

    @router.get(
        "/",
        response_model=list[Record],
        tags=[type],
        summary=f"List all {type}s",
        description=f"List all {type}s.",
    )
    async def list_api(
        service: CosmosService = Depends(get_api_service),
    ) -> list[Record]:
        f"""List all {type}s."""
        return await list_records(service)

    @router.put(
        "/{id}/",
        response_model=Record,
        tags=[type],
        summary=f"Update a {type} by ID",
        description=f"Update a {type} by its ID.",
    )
    async def update_api(
        id: str,
        design: Record,
        service: CosmosService = Depends(get_api_service),
    ) -> Record:
        f"""Update a {type} by ID."""
        return await update_record(id, design, service)

    @router.delete(
        "/{id}/",
        response_model=dict,
        tags=[type],
        summary=f"Delete a {type} by ID",
        description=f"Delete a {type} by its ID.",
    )
    async def delete_api(
        id: str,
        service: CosmosService = Depends(get_api_service),
    ) -> dict:
        f"""Delete a {type} by ID."""
        await delete_record(id, service)
        return {"message": f"{type} {id} deleted successfully"}

    @router.get(
        "/default/",
        response_model=Record,
        tags=[type],
        summary=f"Get the default {type}",
        description=f"Get the default {type}.",
    )
    async def get_default_api(
        service: CosmosService = Depends(get_api_service),
    ) -> Record:
        f"""Get the default {type}."""
        return await get_default_record(service)

    @router.patch(
        "/{id}/default/",
        response_model=Record,
        tags=[type],
        summary=f"Set a {type} as the default",
        description=f"Set a {type} as the default.",
    )
    async def set_default_api(
        id: str,
        service: CosmosService = Depends(get_api_service),
    ) -> Record:
        f"""Set a {type} as the default {type}."""
        return await set_default_record(id, service)

    return router
