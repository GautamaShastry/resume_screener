import re
from datetime import date

MONTHS = {
    m: i
    for i, m in enumerate(
        ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1
    )
}
PRESENT = {"present", "current", "now", "today"}


def parse_month(value: str, *, is_end: bool, today: date) -> date | None:
    s = (value or "").strip().lower()
    if not s:
        return today if is_end else None
    if s in PRESENT:
        return today
    m = re.fullmatch(r"([a-z]{3})[a-z]*\.?\s+(\d{4})", s)
    if m and m.group(1) in MONTHS:
        return date(int(m.group(2)), MONTHS[m.group(1)], 1)
    m = re.fullmatch(r"(\d{1,2})/(\d{4})", s)
    if m and 1 <= int(m.group(1)) <= 12:
        return date(int(m.group(2)), int(m.group(1)), 1)
    m = re.fullmatch(r"(\d{4})-(\d{1,2})", s)
    if m and 1 <= int(m.group(2)) <= 12:
        return date(int(m.group(1)), int(m.group(2)), 1)
    if re.fullmatch(r"\d{4}", s):
        return date(int(s), 12 if is_end else 1, 1)
    return None


def _index(d: date) -> int:
    return d.year * 12 + d.month - 1


def years_of_experience(structured: dict | None, today: date) -> float:
    if not structured:
        return 0.0
    intervals: list[tuple[int, int]] = []
    for section in structured.get("sections", []):
        if section.get("kind") != "experience":
            continue
        for entry in section.get("entries", []):
            start = parse_month(entry.get("start", ""), is_end=False, today=today)
            end = parse_month(entry.get("end", ""), is_end=True, today=today)
            if start is None or end is None or end < start:
                continue
            intervals.append((_index(start), _index(end) + 1))
    total = 0
    current: tuple[int, int] | None = None
    for lo, hi in sorted(intervals):
        if current is None or lo > current[1]:
            if current is not None:
                total += current[1] - current[0]
            current = (lo, hi)
        else:
            current = (current[0], max(current[1], hi))
    if current is not None:
        total += current[1] - current[0]
    return round(total / 12, 1)
