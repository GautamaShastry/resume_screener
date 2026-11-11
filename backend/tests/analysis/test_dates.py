from datetime import date

import pytest

from app.analysis.dates import parse_month, years_of_experience

TODAY = date(2026, 1, 1)


@pytest.mark.parametrize(
    "value,is_end,expected",
    [
        ("Jan 2020", False, date(2020, 1, 1)),
        ("September 2019", False, date(2019, 9, 1)),
        ("Sept. 2019", False, date(2019, 9, 1)),
        ("06/2016", False, date(2016, 6, 1)),
        ("2016-06", False, date(2016, 6, 1)),
        ("2016", False, date(2016, 1, 1)),
        ("2016", True, date(2016, 12, 1)),
        ("Present", True, TODAY),
        ("", True, TODAY),
        ("", False, None),
        ("13/2020", False, None),
        ("sometime", False, None),
    ],
)
def test_parse_month(value, is_end, expected):
    assert parse_month(value, is_end=is_end, today=TODAY) == expected


def _structured(*ranges):
    entries = [{"start": s, "end": e, "bullets": []} for s, e in ranges]
    return {
        "sections": [
            {"kind": "experience", "entries": entries},
            {"kind": "education", "entries": [{"start": "2000", "end": "2004", "bullets": []}]},
        ]
    }


def test_years_sum_and_merge_overlaps():
    overlapping = _structured(("Jan 2020", "Dec 2021"), ("Jun 2021", "Dec 2022"))
    assert years_of_experience(overlapping, TODAY) == 3.0
    two_jobs = _structured(("Jan 2020", "Present"), ("Jun 2016", "Dec 2019"))
    assert years_of_experience(two_jobs, TODAY) == 9.7
    assert years_of_experience(_structured(("Dec 2022", "Jan 2020")), TODAY) == 0.0
    assert years_of_experience(None, TODAY) == 0.0
