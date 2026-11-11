import re

from app.resumes.extract import ExtractedDoc

HEADINGS: dict[str, list[str]] = {
    "summary": ["summary", "professional summary", "profile", "objective", "about", "about me"],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "work history",
    ],
    "education": ["education", "academic background", "education and training"],
    "skills": ["skills", "technical skills", "core competencies", "technologies", "tech stack"],
    "projects": ["projects", "personal projects", "selected projects"],
    "certifications": ["certifications", "licenses", "certificates", "licenses & certifications"],
    "awards": ["awards", "honors", "achievements"],
    "publications": ["publications"],
    "volunteer": ["volunteer", "volunteering", "volunteer experience"],
}
SYNONYMS = {syn: kind for kind, syns in HEADINGS.items() for syn in syns}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
MONTHS = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?"
DATE_PATTERNS = {
    "month_name": re.compile(rf"\b{MONTHS}\s+\d{{4}}\b"),
    "mm/yyyy": re.compile(r"\b(?:0?[1-9]|1[0-2])/\d{4}\b"),
    "yyyy-mm": re.compile(r"\b\d{4}-(?:0[1-9]|1[0-2])\b"),
}


def find_phone(text: str) -> str | None:
    for m in PHONE_RE.finditer(text):
        if sum(ch.isdigit() for ch in m.group(0)) >= 10:
            return m.group(0).strip()
    return None


def _norm_heading(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip().rstrip(":")).lower()


def _check(check: str, severity: str, message: str, how_to_fix: str) -> dict:
    return {"check": check, "severity": severity, "message": message, "how_to_fix": how_to_fix}


def _is_multi_column(doc: ExtractedDoc) -> bool:
    for pno, (w, _h) in enumerate(doc.page_sizes):
        blocks = [b for b in doc.blocks if b.page == pno and (b.x1 - b.x0) < 0.45 * w]
        left = [b for b in blocks if b.x1 <= 0.55 * w]
        right = [b for b in blocks if b.x0 >= 0.45 * w]
        for lb in left:
            for rb in right:
                if min(lb.y1, rb.y1) - max(lb.y0, rb.y0) > 0:
                    return True
    return False


def build_ats_report(doc: ExtractedDoc) -> dict:
    checks: list[dict] = []
    body, hf = doc.body_text, doc.header_footer_text
    lines = [line.strip() for line in doc.full_text.splitlines() if line.strip()]

    if len(doc.full_text.strip()) / max(doc.pages, 1) < 200:
        checks.append(
            _check(
                "no_text",
                "error",
                "We couldn't read text from this file.",
                "Export your résumé from Word or Google Docs as a text-based PDF or DOCX, "
                "not a scan.",
            )
        )
    if doc.file_type == "pdf" and _is_multi_column(doc):
        checks.append(
            _check(
                "multi_column",
                "warning",
                "This résumé uses a multi-column layout.",
                "Use a single column so parsers read sections in the right order.",
            )
        )
    if doc.table_count:
        checks.append(
            _check(
                "tables",
                "warning",
                f"Found {doc.table_count} table(s).",
                "Replace tables with plain text lines; many parsers skip or scramble table cells.",
            )
        )

    email_body, email_hf = EMAIL_RE.search(body), EMAIL_RE.search(hf)
    phone_body, phone_hf = find_phone(body), find_phone(hf)
    if (email_hf and not email_body) or (phone_hf and not phone_body):
        checks.append(
            _check(
                "header_footer_content",
                "warning",
                "Your contact details are only in the page header or footer.",
                "Move your email and phone number into the main body at the top of the page.",
            )
        )
    found = (("email", email_body or email_hf), ("phone", phone_body or phone_hf))
    missing = [name for name, ok in found if not ok]
    if missing:
        checks.append(
            _check(
                "missing_contact",
                "error",
                f"No {' or '.join(missing)} found.",
                "Add your email address and phone number near the top.",
            )
        )
    if doc.image_count:
        checks.append(
            _check(
                "images",
                "info",
                f"Found {doc.image_count} image(s) or icon(s).",
                "Parsers ignore images; make sure no information exists only inside an image.",
            )
        )

    found_kinds: list[str] = []
    for line in lines:
        kind = SYNONYMS.get(_norm_heading(line))
        if kind and kind not in found_kinds:
            found_kinds.append(kind)
    if "experience" not in found_kinds or "education" not in found_kinds or len(found_kinds) < 2:
        candidates = [
            ln
            for ln in lines
            if ln.isupper() and len(ln.split()) <= 4 and _norm_heading(ln) not in SYNONYMS
        ][:5]
        detail = f" Unrecognized headings: {', '.join(candidates)}." if candidates else ""
        checks.append(
            _check(
                "nonstandard_headings",
                "warning",
                "Couldn't find standard section headings like Experience and Education." + detail,
                "Use common headings: Summary, Experience, Education, Skills, Projects.",
            )
        )
    if doc.pages > 2:
        checks.append(
            _check(
                "length",
                "info",
                f"This résumé is {doc.pages} pages long.",
                "Most roles expect one or two pages.",
            )
        )
    formats = [name for name, rx in DATE_PATTERNS.items() if rx.search(doc.full_text)]
    if len(formats) > 1:
        checks.append(
            _check(
                "date_format",
                "info",
                "Dates use more than one format.",
                "Pick one format (for example 'Jan 2020') and use it everywhere.",
            )
        )

    name = next(
        (
            ln
            for ln in lines
            if "@" not in ln and not any(c.isdigit() for c in ln) and len(ln.split()) <= 5
        ),
        None,
    )
    email = email_body or email_hf
    return {
        "checks": checks,
        "parsed_view": {
            "text": body,
            "fields": {
                "name": name,
                "email": email.group(0) if email else None,
                "phone": phone_body or phone_hf,
                "sections": found_kinds,
            },
        },
    }
