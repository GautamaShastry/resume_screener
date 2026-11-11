import io

import docx
import pymupdf as fitz

STANDARD_RESUME = """Jane Doe
jane@example.com | +1 555 123 4567
SUMMARY
Backend engineer focused on reliable APIs.
EXPERIENCE
Senior Engineer, Acme Corp, Jan 2020 - Present
Built a Python FastAPI service handling 2 million requests per day.
Led migration of PostgreSQL databases to managed cloud instances.
Software Engineer, Beta Inc, Jun 2016 - Dec 2019
Developed React dashboards used by 300 internal analysts.
EDUCATION
BSc Computer Science, State University, 2016
SKILLS
Python, FastAPI, PostgreSQL, React, Docker
"""

BULLETS = [
    "Built a Python FastAPI service handling 2 million requests per day.",
    "Led migration of PostgreSQL databases to managed cloud instances.",
    "Developed React dashboards used by 300 internal analysts.",
]


def make_pdf(text: str = STANDARD_RESUME, pages: int = 1) -> bytes:
    doc = fitz.open()
    for _ in range(pages):
        page = doc.new_page()
        page.insert_textbox(fitz.Rect(72, 72, 540, 760), text, fontsize=10)
    return doc.tobytes()


def make_two_column_pdf() -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((40, 60), "Jane Doe  jane@example.com  +1 555 123 4567", fontsize=10)
    left = "EXPERIENCE\n" + "Built systems in Python for many customers.\n" * 8
    right = "SKILLS\n" + "Python\nDocker\nKubernetes\n" * 4 + "EDUCATION\nBSc Computer Science\n"
    page.insert_textbox(fitz.Rect(40, 100, 270, 700), left, fontsize=10)
    page.insert_textbox(fitz.Rect(330, 100, 570, 700), right, fontsize=10)
    return doc.tobytes()


def make_image_only_pdf() -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 50, 50), False)
    pix.clear_with(200)
    page.insert_image(fitz.Rect(72, 72, 300, 300), pixmap=pix)
    return doc.tobytes()


def make_header_contact_pdf() -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 25), "jane@example.com  +1 555 123 4567", fontsize=9)
    body = "\n".join(line for line in STANDARD_RESUME.splitlines() if "@" not in line)
    page.insert_textbox(fitz.Rect(72, 72, 540, 760), body, fontsize=10)
    return doc.tobytes()


def make_docx(
    text: str = STANDARD_RESUME, table: bool = False, header_contact: bool = False
) -> bytes:
    d = docx.Document()
    lines = text.splitlines()
    if header_contact:
        d.sections[0].header.paragraphs[0].text = lines[1]
        lines = [lines[0]] + lines[2:]
    for line in lines:
        d.add_paragraph(line)
    if table:
        t = d.add_table(rows=1, cols=2)
        t.cell(0, 0).text = "Python"
        t.cell(0, 1).text = "Docker"
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()
