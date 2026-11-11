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
        url = str(request.url)
        for prefix, response in routes.items():
            if url.startswith(prefix):
                return response
        return httpx.Response(404, text="not found")

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def public_resolver(host: str) -> list[str]:
    return ["93.184.216.34"]
