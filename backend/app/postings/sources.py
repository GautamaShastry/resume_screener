import html
import json
import re
from dataclasses import dataclass
from typing import Literal
from urllib.parse import parse_qs, urlparse

import httpx
import trafilatura
from bs4 import BeautifulSoup

from app.core.errors import UnsupportedSource
from app.postings.fetch import FetchError, safe_get

UNSUPPORTED_HOSTS = ("linkedin.com", "indeed.com")
GREENHOUSE_HOSTS = ("boards.greenhouse.io", "job-boards.greenhouse.io")
MIN_DESCRIPTION = 200
BOARD_API_MAX_BYTES = 20_000_000  # whole-board APIs we construct ourselves (Ashby ~3 MB)


@dataclass(frozen=True)
class SourceRef:
    kind: Literal["greenhouse", "lever", "ashby", "html"]
    token: str = ""
    job_id: str = ""


@dataclass
class FetchedPosting:
    source: str
    url: str
    title: str
    company: str
    location: str
    description_text: str


def html_to_text(markup: str) -> str:
    text = BeautifulSoup(markup, "html.parser").get_text("\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def detect_source(url: str) -> SourceRef:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    parts = [p for p in parsed.path.split("/") if p]
    if any(host == h or host.endswith("." + h) for h in UNSUPPORTED_HOSTS):
        raise UnsupportedSource(
            "We can't import from this site. Paste the job description instead."
        )
    if host in GREENHOUSE_HOSTS:
        if parts[:2] == ["embed", "job_app"]:
            q = parse_qs(parsed.query)
            if q.get("for") and q.get("token"):
                return SourceRef("greenhouse", q["for"][0], q["token"][0])
        if len(parts) >= 3 and parts[1] == "jobs":
            return SourceRef("greenhouse", parts[0], parts[2])
    if host == "jobs.lever.co" and len(parts) >= 2:
        return SourceRef("lever", parts[0], parts[1])
    if host == "jobs.ashbyhq.com" and len(parts) >= 2:
        return SourceRef("ashby", parts[0], parts[1])
    return SourceRef("html")


async def _get_json(client: httpx.AsyncClient, url: str, max_bytes: int = 2_000_000) -> dict:
    _, body, _ = await safe_get(client, url, max_bytes=max_bytes)
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise FetchError("The job board returned an unexpected response.") from exc


def _slug_name(token: str) -> str:
    return token.replace("-", " ").title()


async def _greenhouse(client: httpx.AsyncClient, ref: SourceRef, url: str) -> FetchedPosting:
    data = await _get_json(
        client, f"https://boards-api.greenhouse.io/v1/boards/{ref.token}/jobs/{ref.job_id}"
    )
    return FetchedPosting(
        source="greenhouse",
        url=data.get("absolute_url") or url,
        title=data.get("title", "").strip(),
        company=data.get("company_name") or _slug_name(ref.token),
        location=(data.get("location") or {}).get("name", ""),
        description_text=html_to_text(html.unescape(data.get("content", ""))),
    )


async def _lever(client: httpx.AsyncClient, ref: SourceRef, url: str) -> FetchedPosting:
    data = await _get_json(client, f"https://api.lever.co/v0/postings/{ref.token}/{ref.job_id}")
    parts = [data.get("descriptionPlain", "")]
    for item in data.get("lists", []):
        parts.append(item.get("text", ""))
        parts.append(html_to_text(item.get("content", "")))
    parts.append(data.get("additionalPlain", ""))
    return FetchedPosting(
        source="lever",
        url=data.get("hostedUrl") or url,
        title=data.get("text", "").strip(),
        company=_slug_name(ref.token),
        location=(data.get("categories") or {}).get("location", ""),
        description_text="\n".join(p for p in parts if p).strip(),
    )


async def _ashby(client: httpx.AsyncClient, ref: SourceRef, url: str) -> FetchedPosting:
    data = await _get_json(
        client,
        f"https://api.ashbyhq.com/posting-api/job-board/{ref.token}",
        max_bytes=BOARD_API_MAX_BYTES,
    )
    job = next((j for j in data.get("jobs", []) if str(j.get("id")) == ref.job_id), None)
    if job is None:
        raise FetchError("That job is no longer listed.")
    description = job.get("descriptionPlain") or html_to_text(job.get("descriptionHtml", ""))
    return FetchedPosting(
        source="ashby",
        url=job.get("jobUrl") or url,
        title=job.get("title", "").strip(),
        company=_slug_name(ref.token),
        location=job.get("location", "") or "",
        description_text=description,
    )


def _find_jobposting(node) -> dict | None:  # noqa: ANN001
    if isinstance(node, list):
        for item in node:
            found = _find_jobposting(item)
            if found:
                return found
    elif isinstance(node, dict):
        types = node.get("@type")
        if types == "JobPosting" or (isinstance(types, list) and "JobPosting" in types):
            return node
        if "@graph" in node:
            return _find_jobposting(node["@graph"])
    return None


def _jsonld_location(job: dict) -> str:
    loc = job.get("jobLocation")
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    address = (loc or {}).get("address", {}) if isinstance(loc, dict) else {}
    return address.get("addressLocality", "") if isinstance(address, dict) else ""


async def _html(client: httpx.AsyncClient, url: str) -> FetchedPosting:
    final_url, body, _ = await safe_get(client, url)
    page = body.decode("utf-8", errors="replace")
    soup = BeautifulSoup(page, "html.parser")
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            job = _find_jobposting(json.loads(script.string or ""))
        except json.JSONDecodeError:
            continue
        if job:
            org = job.get("hiringOrganization") or {}
            description = html_to_text(html.unescape(job.get("description", "")))
            if len(description) >= MIN_DESCRIPTION:
                return FetchedPosting(
                    source="html",
                    url=final_url,
                    title=job.get("title", "").strip(),
                    company=org.get("name", "") if isinstance(org, dict) else "",
                    location=_jsonld_location(job),
                    description_text=description,
                )
    text = trafilatura.extract(page) or ""
    if len(text) < MIN_DESCRIPTION:
        raise FetchError("We couldn't find a job description on that page. Paste it instead.")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    return FetchedPosting(
        source="html", url=final_url, title=title, company="", location="", description_text=text
    )


async def fetch_posting(client: httpx.AsyncClient, url: str) -> FetchedPosting:
    ref = detect_source(url)
    if ref.kind == "greenhouse":
        return await _greenhouse(client, ref, url)
    if ref.kind == "lever":
        return await _lever(client, ref, url)
    if ref.kind == "ashby":
        return await _ashby(client, ref, url)
    return await _html(client, url)
