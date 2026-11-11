import httpx
import pytest

from app.core.errors import UnsupportedSource
from app.postings import fetch
from app.postings.fetch import FetchError
from app.postings.sources import SourceRef, detect_source, fetch_posting
from tests.postings.fixtures import (
    ASHBY_BOARD,
    GREENHOUSE_JOB,
    JSONLD_PAGE,
    LEVER_JOB,
    PLAIN_PAGE,
    mock_client,
    public_resolver,
)


@pytest.fixture(autouse=True)
def _public_dns(monkeypatch):
    monkeypatch.setattr(fetch, "_resolve", public_resolver)


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://boards.greenhouse.io/acme/jobs/123", SourceRef("greenhouse", "acme", "123")),
        (
            "https://job-boards.greenhouse.io/acme/jobs/123?gh_src=x",
            SourceRef("greenhouse", "acme", "123"),
        ),
        (
            "https://boards.greenhouse.io/embed/job_app?for=acme&token=123",
            SourceRef("greenhouse", "acme", "123"),
        ),
        ("https://jobs.lever.co/acme/abc-def", SourceRef("lever", "acme", "abc-def")),
        ("https://jobs.ashbyhq.com/acme/abc-123", SourceRef("ashby", "acme", "abc-123")),
        ("https://careers.globex.com/jobs/1", SourceRef("html")),
    ],
)
def test_detect_source(url, expected):
    assert detect_source(url) == expected


@pytest.mark.parametrize(
    "url", ["https://www.linkedin.com/jobs/view/1", "https://www.indeed.com/viewjob?jk=1"]
)
def test_unsupported_sources(url):
    with pytest.raises(UnsupportedSource):
        detect_source(url)


async def test_greenhouse():
    client = mock_client(
        {
            "https://boards-api.greenhouse.io/v1/boards/acme/jobs/123": httpx.Response(
                200, json=GREENHOUSE_JOB
            )
        }
    )
    p = await fetch_posting(client, "https://boards.greenhouse.io/acme/jobs/123")
    assert (p.source, p.title, p.company, p.location) == (
        "greenhouse",
        "Backend Engineer",
        "Acme",
        "Remote - US",
    )
    assert "5+ years of professional Python experience" in p.description_text
    assert "<li>" not in p.description_text


async def test_lever():
    client = mock_client(
        {"https://api.lever.co/v0/postings/acme/abc": httpx.Response(200, json=LEVER_JOB)}
    )
    p = await fetch_posting(client, "https://jobs.lever.co/acme/abc")
    assert p.source == "lever" and p.title == "Backend Engineer"
    assert "Requirements" in p.description_text and "Kubernetes" in p.description_text


async def test_ashby_selects_job_and_404s_when_missing():
    client = mock_client(
        {
            "https://api.ashbyhq.com/posting-api/job-board/acme": httpx.Response(
                200, json=ASHBY_BOARD
            )
        }
    )
    p = await fetch_posting(client, "https://jobs.ashbyhq.com/acme/abc-123")
    assert p.title == "Backend Engineer" and p.location == "Remote"
    with pytest.raises(FetchError):
        await fetch_posting(client, "https://jobs.ashbyhq.com/acme/missing")


async def test_html_prefers_jsonld():
    client = mock_client(
        {
            "https://careers.globex.com/": httpx.Response(
                200, text=JSONLD_PAGE, headers={"content-type": "text/html"}
            )
        }
    )
    p = await fetch_posting(client, "https://careers.globex.com/")
    assert (p.source, p.title, p.company, p.location) == (
        "html",
        "Platform Engineer",
        "Globex",
        "Austin",
    )
    assert "PostgreSQL" in p.description_text


async def test_html_main_text_fallback_and_short_page_error():
    client = mock_client(
        {
            "https://initech.example/job": httpx.Response(
                200, text=PLAIN_PAGE, headers={"content-type": "text/html"}
            ),
            "https://empty.example/": httpx.Response(
                200, text="<html><body>Hi</body></html>", headers={"content-type": "text/html"}
            ),
        }
    )
    p = await fetch_posting(client, "https://initech.example/job")
    assert p.title.startswith("Data Engineer")
    assert "PostgreSQL" in p.description_text
    with pytest.raises(FetchError, match="Paste"):
        await fetch_posting(client, "https://empty.example/")


async def test_ashby_large_board_is_allowed():
    padding = [
        {"id": f"pad-{i}", "title": "Other", "descriptionPlain": "x" * 100_000} for i in range(30)
    ]
    board = {"jobs": padding + ASHBY_BOARD["jobs"]}
    client = mock_client(
        {"https://api.ashbyhq.com/posting-api/job-board/acme": httpx.Response(200, json=board)}
    )
    p = await fetch_posting(client, "https://jobs.ashbyhq.com/acme/abc-123")
    assert p.title == "Backend Engineer"
