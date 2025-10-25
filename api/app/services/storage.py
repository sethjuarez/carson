import uuid
import base64
import contextlib
from typing import AsyncGenerator
from aiohttp.streams import StreamReader
from azure.storage.blob.aio import BlobServiceClient
from azure.identity.aio import DefaultAzureCredential, ManagedIdentityCredential


class StorageService:
    def __init__(self, client_id: str, storage: str, container: str):
        self.client_id = client_id
        self.storage = storage
        self.container = container

    @contextlib.asynccontextmanager
    async def get_storage_client(self):
        # Create credential and blob service client
        credential: ManagedIdentityCredential | DefaultAzureCredential
        if self.client_id == "LOCAL":
            credential = DefaultAzureCredential()
        else:
            credential = ManagedIdentityCredential(client_id=self.client_id)

        blob_service_client = BlobServiceClient(
            account_url=self.storage, credential=credential
        )
        try:
            # Create the container if it doesn't exist
            container_client = blob_service_client.get_container_client(self.container)

            yield container_client
        finally:
            await credential.close()
            await blob_service_client.close()

    async def create_container(self) -> None:
        async with self.get_storage_client() as container_client:
            if not await container_client.exists():
                await container_client.create_container()

    async def save_image_blobs(
        self,
        images: list[str],
        path: str | None = None,
    ) -> AsyncGenerator[str, None]:
        async with self.get_storage_client() as container_client:
            for image in images:
                image_bytes = base64.b64decode(image)
                blob_name = (
                    f"images/{str(uuid.uuid4())}.png"
                    if path is None
                    else f"images/{path}/{str(uuid.uuid4())}.png"
                )
                await container_client.upload_blob(
                    name=blob_name, data=image_bytes, overwrite=True
                )
                yield blob_name

    async def save_image_blob(self, image: str, path: str | None = None) -> str:
        async with self.get_storage_client() as container_client:
            image_bytes = base64.b64decode(image)
            blob_name = (
                f"images/{str(uuid.uuid4())}.png"
                if path is None
                else f"images/{path}/{str(uuid.uuid4())}.png"
            )
            await container_client.upload_blob(
                name=blob_name, data=image_bytes, overwrite=True
            )
            return blob_name

    async def save_video_blob(
        self,
        stream_reader: StreamReader,
        path: str | None = None,
    ) -> str:
        async with self.get_storage_client() as container_client:
            blob_name = (
                f"videos/{str(uuid.uuid4())}.mp4"
                if path is None
                else f"videos/{path}/{str(uuid.uuid4())}.mp4"
            )
            content = await stream_reader.read()
            await container_client.upload_blob(
                name=blob_name, data=content, overwrite=True
            )
            return blob_name
