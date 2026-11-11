import math

from app.core.errors import AppError

WEIGHTS = {"must": 3, "nice": 1}
VALUES = {"met": 1.0, "partial": 0.5, "missing": 0.0}
EXPECTED_YEARS: dict[str, tuple[float, float | None]] = {
    "intern": (0.0, 2.0),
    "junior": (0.0, 2.0),
    "mid": (2.0, 5.0),
    "senior": (5.0, 9.0),
    "staff+": (8.0, None),
}
MUST_MISSING_CAP = 75


class NoRequirements(AppError):
    status_code = 422
    code = "NO_REQUIREMENTS"


def round_half_up(x: float) -> int:
    return math.floor(x + 0.5)


def seniority_fit(years: float, seniority: str) -> int:
    if seniority not in EXPECTED_YEARS:
        return 100
    lo, hi = EXPECTED_YEARS[seniority]
    if years >= lo and (hi is None or years <= hi):
        return 100
    distance = lo - years if years < lo else years - (hi if hi is not None else years)
    return 50 if distance <= 1 else 0


def compute_score(requirements: list[dict], evidence: list[dict], fit: int) -> tuple[int, dict]:
    if not requirements:
        raise NoRequirements("We couldn't find any requirements in this job description.")
    status = {e["requirement_id"]: e["status"] for e in evidence}
    numerator = denominator = 0.0
    must_missing = 0
    for req in requirements:
        weight = WEIGHTS[req["kind"]]
        value = status.get(req["id"], "missing")
        numerator += weight * VALUES[value]
        denominator += weight
        if req["kind"] == "must" and value == "missing":
            must_missing += 1
    coverage = numerator / denominator
    score = round_half_up(85 * coverage + 15 * fit / 100)
    capped = must_missing > 0 and score > MUST_MISSING_CAP
    if must_missing:
        score = min(score, MUST_MISSING_CAP)
    return score, {
        "coverage": round(coverage, 4),
        "seniority_fit": fit,
        "must_missing_count": must_missing,
        "capped": capped,
        "weights": dict(WEIGHTS),
    }
