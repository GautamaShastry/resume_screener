import socket

import pytest

from app.core.errors import NotFound
from app.core.settings import Settings
from app.storage.blob import AzureBlobStore, LocalBlobStore

AZURITE = (
    "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
    "QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;"
)


def _azurite_up() -> bool:
    try:
        socket.create_connection(("127.0.0.1", 10000), timeout=0.5).close()
        return True
    except OSError:
        return False


async def _roundtrip(store) -> None:
    await store.put("u1/a.pdf", b"hello", "application/pdf")
    await store.put("u1/b.pdf", b"world", "application/pdf")
    await store.put("u2/c.pdf", b"other", "application/pdf")
    assert await store.get("u1/a.pdf") == b"hello"
    await store.delete("u1/a.pdf")
    await store.delete("u1/a.pdf")  # idempotent
    with pytest.raises(NotFound):
        await store.get("u1/a.pdf")
    await store.delete_prefix("u1/")
    with pytest.raises(NotFound):
        await store.get("u1/b.pdf")
    assert await store.get("u2/c.pdf") == b"other"


async def test_local_roundtrip(tmp_path):
    await _roundtrip(LocalBlobStore(str(tmp_path)))


async def test_local_rejects_path_escape(tmp_path):
    store = LocalBlobStore(str(tmp_path / "root"))
    with pytest.raises(ValueError):
        await store.put("../escape.txt", b"x", "text/plain")


@pytest.mark.azure
@pytest.mark.skipif(not _azurite_up(), reason="Azurite not running")
async def test_azure_roundtrip_against_azurite():
    settings = Settings(
        env="test",
        storage_mode="azure",
        azure_storage_connection_string=AZURITE,
        blob_container="test-blobs",
    )
    store = AzureBlobStore.from_settings(settings)
    await store.ensure()
    try:
        await _roundtrip(store)
    finally:
        await store.delete_prefix("u2/")
        await store.aclose()
