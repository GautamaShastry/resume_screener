import asyncio
import ipaddress
import socket

import httpx

from app.core.errors import AppError

USER_AGENT = "HireReadyBot/2.0"


class FetchError(AppError):
    status_code = 422
    code = "FETCH_FAILED"
    retryable = False


async def _resolve(host: str) -> list[str]:
    infos = await asyncio.get_running_loop().getaddrinfo(host, None)
    return [info[4][0] for info in infos]


async def _check_host(host: str) -> None:
    try:
        addresses = await _resolve(host)
    except socket.gaierror as exc:
        raise FetchError("We couldn't find that website.") from exc
    if not addresses:
        raise FetchError("We couldn't find that website.")
    for address in addresses:
        if not ipaddress.ip_address(address.split("%")[0]).is_global:
            raise FetchError("That address isn't allowed.")


async def safe_get(
    client: httpx.AsyncClient, url: str, *, max_bytes: int = 2_000_000, max_redirects: int = 3
) -> tuple[str, bytes, str]:
    current = url
    for _ in range(max_redirects + 1):
        parsed = httpx.URL(current)
        if parsed.scheme not in ("http", "https") or not parsed.host:
            raise FetchError("Only http and https links are supported.")
        await _check_host(parsed.host)
        try:
            async with client.stream(
                "GET",
                parsed,
                headers={"User-Agent": USER_AGENT},
                follow_redirects=False,
                timeout=10,
            ) as response:
                if response.is_redirect and "location" in response.headers:
                    current = str(parsed.join(response.headers["location"]))
                    continue
                if response.status_code >= 400:
                    raise FetchError(f"The page returned HTTP {response.status_code}.")
                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body += chunk
                    if len(body) > max_bytes:
                        raise FetchError("The page is too large to import.")
                return str(parsed), bytes(body), response.headers.get("content-type", "")
        except httpx.HTTPError as exc:
            raise FetchError("We couldn't load that page.") from exc
    raise FetchError("The link has too many redirects.")
