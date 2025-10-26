from collections.abc import Callable
import contextlib
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from pydantic import BaseModel


class CosmosService:
    def __init__(self, connection_string: str, database_name: str, container_name: str):
        self.connection_string = connection_string
        self.database_name = database_name
        self.container_name = container_name

    @contextlib.asynccontextmanager
    async def get_cosmos_client(self):
        # Create a Cosmos DB client
        client = CosmosClient.from_connection_string(self.connection_string)
        try:
            database = client.get_database_client(self.database_name)
            container = database.get_container_client(self.container_name)
            yield container
        finally:
            await client.close()

    async def create_container_if_not_exists(
        self, partition_key_path: str = "/id"
    ) -> None:
        client = CosmosClient.from_connection_string(self.connection_string)
        try:
            database = client.get_database_client(self.database_name)
            try:
                await database.read()
            except CosmosResourceNotFoundError:
                await client.create_database(self.database_name)

            container = database.get_container_client(self.container_name)
            try:
                await container.read()
            except CosmosResourceNotFoundError:
                await database.create_container(
                    id=self.container_name,
                    partition_key=PartitionKey(path=partition_key_path),
                )
        finally:
            await client.close()

    async def upsert_item(self, item: BaseModel) -> BaseModel:
        async with self.get_cosmos_client() as container:
            response = await container.upsert_item(item.model_dump())
            return BaseModel.model_validate(response)

    async def get_item(self, item_id: str) -> BaseModel | None:
        async with self.get_cosmos_client() as container:
            try:
                item = await container.read_item(item=item_id, partition_key=item_id)
                return BaseModel.model_validate(item)
            except CosmosResourceNotFoundError:
                return None

    async def get_items(self) -> list[BaseModel]:
        async with self.get_cosmos_client() as container:
            items = container.read_all_items()
            results = []
            async for item in items:
                results.append(BaseModel.model_validate(item))
            return results

    async def update_items(
        self,
        mapper: Callable[[dict], dict],
    ) -> None:
        async with self.get_cosmos_client() as container:
            async for item in container.read_all_items():
                updated_item = mapper(item)
                await container.upsert_item(updated_item)

    async def query_items(
        self, query: str, parameters: list[dict] | None = None
    ) -> list[BaseModel]:
        async with self.get_cosmos_client() as container:
            items = container.query_items(
                query=query,
                parameters=parameters or [],
                enable_cross_partition_query=True,
            )
            results = []
            async for item in items:
                results.append(BaseModel.model_validate(item))
            return results


class ConfigurationService(CosmosService):
    def __init__(self, connection_string: str, database_name: str):
        super().__init__(
            connection_string=connection_string,
            database_name=database_name,
            container_name="configurations",
        )
