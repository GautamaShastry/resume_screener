import io
import math
import re
import zipfile
from dataclasses import dataclass, field
from typing import Literal

import docx
import pymupdf as fitz

MARGIN = 0.05


@dataclass
class TextBlock:
    page: int
    x0: float
    y0: float
    x1: float
    y1: float
    text: str


@dataclass
class ExtractedDoc:
    file_type: str
    body_text: str
    header_footer_text: str
    pages: int
    blocks: list[TextBlock] = field(default_factory=list)
    page_sizes: list[tuple[float, float]] = field(default_factory=list)
    image_count: int = 0
    table_count: int = 0

    @property
    def full_text(self) -> str:
        return "\n".join(t for t in (self.header_footer_text, self.body_text) if t)


def sniff_type(data: bytes) -> Literal["pdf", "docx"] | None:
    if data[:5] == b"%PDF-":
        return "pdf"
    if data[:4] == b"PK\x03\x04":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                if "word/document.xml" in z.namelist():
                    return "docx"
        except zipfile.BadZipFile:
            return None
    return None


def _extract_pdf(data: bytes) -> ExtractedDoc:
    doc = fitz.open(stream=data, filetype="pdf")
    body: list[TextBlock] = []
    margin_texts: list[str] = []
    sizes: list[tuple[float, float]] = []
    images = tables = 0
    for pno, page in enumerate(doc):
        w, h = page.rect.width, page.rect.height
        sizes.append((w, h))
        for x0, y0, x1, y1, text, _no, btype in page.get_text("blocks"):
            if btype != 0 or not text.strip():
                continue
            if y1 < h * MARGIN or y0 > h * (1 - MARGIN):
                margin_texts.append(text.strip())
                continue
            body.append(TextBlock(pno, x0, y0, x1, y1, text.strip()))
        images += len(page.get_images(full=True))
        try:
            tables += len(page.find_tables().tables)
        except Exception:  # noqa: BLE001  (table detection is best effort)
            pass
    body.sort(key=lambda b: (b.page, round(b.y0), b.x0))
    return ExtractedDoc(
        file_type="pdf",
        body_text="\n".join(b.text for b in body),
        header_footer_text="\n".join(margin_texts),
        pages=len(sizes),
        blocks=body,
        page_sizes=sizes,
        image_count=images,
        table_count=tables,
    )


def _docx_pages(data: bytes, text: str) -> int:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if "docProps/app.xml" in z.namelist():
            m = re.search(rb"<Pages>(\d+)</Pages>", z.read("docProps/app.xml"))
            if m:
                return max(1, int(m.group(1)))
    return max(1, math.ceil(len(text) / 3000))


def _extract_docx(data: bytes) -> ExtractedDoc:
    d = docx.Document(io.BytesIO(data))
    parts = [p.text for p in d.paragraphs if p.text.strip()]
    seen: set[int] = set()
    for table in d.tables:
        for row in table.rows:
            for cell in row.cells:
                if id(cell._tc) in seen or not cell.text.strip():
                    continue
                seen.add(id(cell._tc))
                parts.append(cell.text)
    hf: list[str] = []
    for section in d.sections:
        for part in (section.header, section.footer):
            hf.extend(p.text for p in part.paragraphs if p.text.strip())
    body = "\n".join(parts)
    return ExtractedDoc(
        file_type="docx",
        body_text=body,
        header_footer_text="\n".join(hf),
        pages=_docx_pages(data, body),
        image_count=len(d.inline_shapes),
        table_count=len(d.tables),
    )


def extract(data: bytes, file_type: str) -> ExtractedDoc:
    return _extract_pdf(data) if file_type == "pdf" else _extract_docx(data)
