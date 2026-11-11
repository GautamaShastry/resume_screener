import io
import zipfile

from app.resumes.ats import build_ats_report
from app.resumes.extract import extract, sniff_type
from tests.resumes.factories import (
    STANDARD_RESUME,
    make_docx,
    make_header_contact_pdf,
    make_image_only_pdf,
    make_pdf,
    make_two_column_pdf,
)


def _checks(report: dict) -> dict[str, str]:
    return {c["check"]: c["severity"] for c in report["checks"]}


def test_sniff_type():
    assert sniff_type(make_pdf()) == "pdf"
    assert sniff_type(make_docx()) == "docx"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("hello.txt", "x")
    assert sniff_type(buf.getvalue()) is None
    assert sniff_type(b"plain text") is None


def test_clean_single_column_pdf_has_no_warnings():
    report = build_ats_report(extract(make_pdf(), "pdf"))
    severities = set(_checks(report).values())
    assert "error" not in severities and "warning" not in severities
    fields = report["parsed_view"]["fields"]
    assert fields["name"] == "Jane Doe"
    assert fields["email"] == "jane@example.com"
    assert fields["phone"] == "+1 555 123 4567"
    assert {"summary", "experience", "education", "skills"} <= set(fields["sections"])
    assert "Built a Python FastAPI service" in report["parsed_view"]["text"]


def test_two_column_pdf_warns():
    report = build_ats_report(extract(make_two_column_pdf(), "pdf"))
    assert _checks(report)["multi_column"] == "warning"


def test_image_only_pdf_is_no_text_error():
    checks = _checks(build_ats_report(extract(make_image_only_pdf(), "pdf")))
    assert checks["no_text"] == "error"
    assert checks["images"] == "info"
    assert checks["missing_contact"] == "error"


def test_contact_only_in_pdf_header_warns():
    checks = _checks(build_ats_report(extract(make_header_contact_pdf(), "pdf")))
    assert checks["header_footer_content"] == "warning"
    assert "missing_contact" not in checks


def test_docx_table_and_header_contact():
    doc = extract(make_docx(table=True, header_contact=True), "docx")
    checks = _checks(build_ats_report(doc))
    assert checks["tables"] == "warning"
    assert checks["header_footer_content"] == "warning"


def test_nonstandard_headings_warn_and_name_candidates():
    text = STANDARD_RESUME.replace("EXPERIENCE", "WHERE I'VE WORKED").replace(
        "EDUCATION", "SCHOOLING"
    )
    report = build_ats_report(extract(make_pdf(text), "pdf"))
    check = next(c for c in report["checks"] if c["check"] == "nonstandard_headings")
    assert check["severity"] == "warning"
    assert "WHERE I'VE WORKED" in check["message"]


def test_length_and_mixed_dates_are_info():
    text = STANDARD_RESUME.replace("Jun 2016", "06/2016")
    checks = _checks(build_ats_report(extract(make_pdf(text, pages=3), "pdf")))
    assert checks["length"] == "info"
    assert checks["date_format"] == "info"


def test_year_ranges_are_not_phone_numbers():
    text = STANDARD_RESUME.replace("+1 555 123 4567", "").replace(
        "Jun 2016 - Dec 2019", "2016 - 2019"
    )
    report = build_ats_report(extract(make_pdf(text), "pdf"))
    assert report["parsed_view"]["fields"]["phone"] is None
