import asyncio
import pathlib
import shutil
from typing import Protocol

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import BlobServiceClient

from app.core.errors import NotFound
from app.core.settings import Settings


class BlobStore(Protocol):
    async def put(self, path: str, data: bytes, content_type: str) -> None: ...
    async def get(self, path: str) -> bytes: ...
    async def delete(self, path: str) -> None: ...
    async def delete_prefix(self, prefix: str) -> None: ...
    async def ensure(self) -> None: ...
    async def aclose(self) -> None: ...


class LocalBlobStore:
    def __init__(self, root: str):
        self._root = pathlib.Path(root).resolve()

    def _resolve(self, path: str) -> pathlib.Path:
        target = (self._root / path).resolve()
        if self._root not in target.parents and target != self._root:
            raise ValueError("Path escapes storage root")
        return target

    async def put(self, path: str, data: bytes, content_type: str) -> None:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(target.write_bytes, data)

    async def get(self, path: str) -> bytes:
        target = self._resolve(path)
        if not target.is_file():
            raise NotFound("File not found")
        return await asyncio.to_thread(target.read_bytes)

    async def delete(self, path: str) -> None:
        self._resolve(path).unlink(missing_ok=True)

    async def delete_prefix(self, prefix: str) -> None:
        target = self._resolve(prefix)
        if target.is_dir():
            await asyncio.to_thread(shutil.rmtree, target)
        else:
            target.unlink(missing_ok=True)

    async def ensure(self) -> None:
        self._root.mkdir(parents=True, exist_ok=True)

    async def aclose(self) -> None:
        return None


class AzureBlobStore:
    def __init__(self, service: BlobServiceClient, container: str):
        self._service = service
        self._container = service.get_container_client(container)

    @classmethod
    def from_settings(cls, settings: Settings) -> "AzureBlobStore":
        if settings.azure_storage_connection_string:
            service = BlobServiceClient.from_connection_string(
                settings.azure_storage_connection_string
            )
        else:
            from azure.identity.aio import DefaultAzureCredential

            service = BlobServiceClient(
                settings.azure_storage_account_url, credential=DefaultAzureCredential()
            )
        return cls(service, settings.blob_container)

    async def put(self, path: str, data: bytes, content_type: str) -> None:
        await self._container.upload_blob(
            path, data, overwrite=True, content_settings=ContentSettings(content_type=content_type)
        )

    async def get(self, path: str) -> bytes:
        try:
            stream = await self._container.download_blob(path)
        except ResourceNotFoundError as exc:
            raise NotFound("File not found") from exc
        return await stream.readall()

    async def delete(self, path: str) -> None:
        try:
            await self._container.delete_blob(path)
        except ResourceNotFoundError:
            pass

    async def delete_prefix(self, prefix: str) -> None:
        async for blob in self._container.list_blobs(name_starts_with=prefix):
            await self.delete(blob.name)

    async def ensure(self) -> None:
        try:
            await self._container.create_container()
        except ResourceExistsError:
            pass

    async def aclose(self) -> None:
        await self._service.close()


def build_blob_store(settings: Settings) -> BlobStore:
    if settings.storage_mode == "azure":
        return AzureBlobStore.from_settings(settings)
    return LocalBlobStore(settings.local_storage_dir)
