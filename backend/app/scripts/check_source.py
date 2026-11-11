"""Usage: python -m app.scripts.check_source <job-url>  — fetches a real posting and prints it."""

import asyncio
import sys

import httpx

from app.postings.sources import fetch_posting


async def main(url: str) -> None:
    async with httpx.AsyncClient() as client:
        p = await fetch_posting(client, url)
    print(f"source={p.source}\ntitle={p.title}\ncompany={p.company}\nlocation={p.location}")
    print(f"description ({len(p.description_text)} chars):\n{p.description_text[:300]}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
