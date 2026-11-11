import httpx
import pytest

from app.postings import fetch
from app.postings.fetch import FetchError, safe_get
from tests.postings.fixtures import mock_client, public_resolver


@pytest.fixture(autouse=True)
def _public_dns(monkeypatch):
    monkeypatch.setattr(fetch, "_resolve", public_resolver)


@pytest.mark.parametrize("ip", ["127.0.0.1", "10.0.0.5", "169.254.169.254", "192.168.1.1", "::1"])
async def test_blocks_non_global_addresses(monkeypatch, ip):
    async def resolver(host):
        return [ip]

    monkeypatch.setattr(fetch, "_resolve", resolver)
    with pytest.raises(FetchError):
        await safe_get(mock_client({}), "http://internal.example/")


async def test_rejects_non_http_scheme():
    with pytest.raises(FetchError):
        await safe_get(mock_client({}), "file:///etc/passwd")


async def test_redirect_to_private_address_is_blocked(monkeypatch):
    async def resolver(host):
        return ["127.0.0.1"] if host == "evil.internal" else ["93.184.216.34"]

    monkeypatch.setattr(fetch, "_resolve", resolver)
    client = mock_client(
        {
            "https://jobs.example.com/": httpx.Response(
                302, headers={"location": "http://evil.internal/"}
            )
        }
    )
    with pytest.raises(FetchError):
        await safe_get(client, "https://jobs.example.com/")


async def test_too_many_redirects():
    client = mock_client(
        {"https://a.example/": httpx.Response(302, headers={"location": "https://a.example/"})}
    )
    with pytest.raises(FetchError, match="redirects"):
        await safe_get(client, "https://a.example/")


async def test_size_cap_and_http_errors():
    client = mock_client(
        {
            "https://big.example/": httpx.Response(200, content=b"x" * 50),
            "https://gone.example/": httpx.Response(404),
        }
    )
    with pytest.raises(FetchError, match="too large"):
        await safe_get(client, "https://big.example/", max_bytes=10)
    with pytest.raises(FetchError, match="404"):
        await safe_get(client, "https://gone.example/")


async def test_success_sends_user_agent():
    seen = {}

    def handler(request):
        seen["ua"] = request.headers["user-agent"]
        return httpx.Response(200, text="ok", headers={"content-type": "text/plain"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    url, body, ctype = await safe_get(client, "https://ok.example/")
    assert body == b"ok" and ctype == "text/plain" and seen["ua"] == "HireReadyBot/2.0"
