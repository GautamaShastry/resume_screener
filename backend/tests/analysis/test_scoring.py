import pytest

from app.analysis.scoring import NoRequirements, compute_score, seniority_fit


def _req(i, kind):
    return {"id": f"r{i}", "text": f"req {i}", "kind": kind}


def _ev(i, status):
    return {"requirement_id": f"r{i}", "status": status, "quotes": [], "note": ""}


@pytest.mark.parametrize(
    "years,level,fit",
    [
        (6, "senior", 100),
        (4.2, "senior", 50),
        (2, "senior", 0),
        (10, "senior", 50),
        (20, "staff+", 100),
        (7.5, "staff+", 50),
        (1, "unknown", 100),
        (0, "intern", 100),
    ],
)
def test_seniority_fit(years, level, fit):
    assert seniority_fit(years, level) == fit


def test_all_met_full_fit_is_100():
    reqs = [_req(1, "must"), _req(2, "nice")]
    score, breakdown = compute_score(reqs, [_ev(1, "met"), _ev(2, "met")], 100)
    assert score == 100
    assert breakdown == {
        "coverage": 1.0,
        "seniority_fit": 100,
        "must_missing_count": 0,
        "capped": False,
        "weights": {"must": 3, "nice": 1},
    }


def test_missing_must_caps_at_75():
    reqs = [_req(i, "must") for i in range(1, 11)]
    evidence = [_ev(i, "met") for i in range(1, 10)] + [_ev(10, "missing")]
    score, breakdown = compute_score(reqs, evidence, 100)
    assert score == 75
    assert breakdown["capped"] is True and breakdown["must_missing_count"] == 1


def test_low_score_with_missing_must_is_not_marked_capped():
    reqs = [_req(1, "must"), _req(2, "must"), _req(3, "nice")]
    evidence = [_ev(1, "met"), _ev(2, "missing"), _ev(3, "met")]
    score, breakdown = compute_score(reqs, evidence, 100)
    assert score == 64  # 85 * 4/7 + 15 = 63.57
    assert breakdown["capped"] is False and breakdown["must_missing_count"] == 1


def test_partial_counts_half_and_rounds_half_up():
    score, _ = compute_score([_req(1, "must")], [_ev(1, "partial")], 0)
    assert score == 43  # 85 * 0.5 = 42.5


def test_requirement_without_evidence_counts_as_missing():
    score, breakdown = compute_score([_req(1, "nice"), _req(2, "nice")], [_ev(1, "met")], 100)
    assert breakdown["coverage"] == 0.5
    assert score == 58  # 42.5 + 15 = 57.5


def test_no_requirements_raises():
    with pytest.raises(NoRequirements):
        compute_score([], [], 100)
