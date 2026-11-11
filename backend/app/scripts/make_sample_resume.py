"""Usage: python -m app.scripts.make_sample_resume <out.pdf> — writes a one-page résumé PDF."""

import sys

import pymupdf as fitz

TEXT = """Jane Doe
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


def main(path: str) -> None:
    doc = fitz.open()
    doc.new_page().insert_textbox(fitz.Rect(72, 72, 540, 760), TEXT, fontsize=10)
    doc.save(path)


if __name__ == "__main__":
    main(sys.argv[1])
