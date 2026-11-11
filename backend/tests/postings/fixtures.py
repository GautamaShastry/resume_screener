import httpx

GREENHOUSE_JOB = {
    "id": 123,
    "title": "Backend Engineer",
    "location": {"name": "Remote - US"},
    "company_name": "Acme",
    "absolute_url": "https://boards.greenhouse.io/acme/jobs/123",
    "content": "&lt;p&gt;Requirements:&lt;/p&gt;&lt;ul&gt;&lt;li&gt;5+ years of professional "
    "Python experience&lt;/li&gt;&lt;li&gt;Strong PostgreSQL skills&lt;/li&gt;&lt;/ul&gt;",
}
LEVER_JOB = {
    "text": "Backend Engineer",
    "categories": {"location": "Remote"},
    "descriptionPlain": "We build APIs.",
    "lists": [
        {"text": "Requirements", "content": "<li>5+ years of professional Python experience</li>"}
    ],
    "additionalPlain": "Kubernetes experience is a plus.",
    "hostedUrl": "https://jobs.lever.co/acme/abc",
}
ASHBY_BOARD = {
    "jobs": [
        {"id": "other", "title": "Designer", "location": "NYC", "descriptionPlain": "Design."},
        {
            "id": "abc-123",
            "title": " Backend Engineer ",
            "location": "Remote",
            "descriptionPlain": "Requirements: 5+ years of professional Python experience.",
            "jobUrl": "https://jobs.ashbyhq.com/acme/abc-123",
        },
    ]
}
LONG_TEXT = " ".join(["We need 5+ years of professional Python experience and PostgreSQL."] * 10)
JSONLD_PAGE = f"""<html><head><title>Careers</title>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"JobPosting",
"title":"Platform Engineer","hiringOrganization":{{"@type":"Organization","name":"Globex"}},
"jobLocation":{{"@type":"Place","address":{{"addressLocality":"Austin"}}}},
"description":"<p>{LONG_TEXT}</p>"}}</script></head><body>Apply now</body></html>"""
PLAIN_PAGE = f"""<html><head><title>Data Engineer - Initech</title></head><body>
<nav>Home About</nav><article><h1>Data Engineer</h1><p>{LONG_TEXT}</p><p>{LONG_TEXT}</p></article>
<footer>© Initech</footer></body></html>"""


def mock_client(routes: dict[str, httpx.Response]) -> httpx.AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        # safe_get connects to the validated IP; route on the original host from the Host header.
        host = request.headers.get("host", request.url.host).split(":")[0]
        url = str(request.url.copy_with(host=host))
        for prefix, response in routes.items():
            if url.startswith(prefix):
                return response
        return httpx.Response(404, text="not found")

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def public_resolver(host: str) -> list[str]:
    return ["93.184.216.34"]


POSTING_TEXT = """Senior Backend Engineer
Acme Corp - Remote
Requirements:
- 5+ years of professional Python experience
- Experience building REST APIs with FastAPI or Django
- Strong PostgreSQL skills
Nice to have:
- Kubernetes experience is a plus
"""


def posting_llm_response(extra: dict | None = None) -> dict:
    reqs = [
        {
            "text": "5+ years of professional Python experience",
            "kind": "must",
            "category": "experience",
            "source_phrase": "5+ years of professional Python experience",
        },
        {
            "text": "Experience building REST APIs with FastAPI or Django",
            "kind": "must",
            "category": "skill",
            "source_phrase": "Experience building REST APIs with FastAPI or Django",
        },
        {
            "text": "Strong PostgreSQL skills",
            "kind": "must",
            "category": "skill",
            "source_phrase": "Strong PostgreSQL skills",
        },
        {
            "text": "Kubernetes experience",
            "kind": "nice",
            "category": "skill",
            "source_phrase": "Kubernetes experience is a plus",
        },
    ]
    if extra:
        reqs.append(extra)
    return {
        "title": "Senior Backend Engineer",
        "company": "Acme Corp",
        "location": "Remote",
        "seniority": "senior",
        "requirements": reqs,
    }
