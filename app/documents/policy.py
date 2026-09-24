"""Turns raw judgments into checks and a verdict. Model-agnostic, so Jev and any baseline share it."""

from dataclasses import dataclass

from app.documents.questions import REQUIRED_FIELDS
from app.schemas import CheckResult, CheckStatus


# Starting points, not universal rules: tune them on your own labeled documents.
PASS_THRESHOLD = 0.8
FAIL_THRESHOLD = 0.2
TYPE_CONFIDENCE_THRESHOLD = 0.8


@dataclass(frozen=True)
class Judgments:
    detected_type: str
    detected_type_confidence: float
    expected_type_probability: float
    belongs_to_holder: float
    fields_present: dict[str, float]
    has_contradictions: float


def _status_from_probability(probability: float) -> CheckStatus:
    if probability >= PASS_THRESHOLD:
        return "pass"
    if probability <= FAIL_THRESHOLD:
        return "fail"
    return "uncertain"


def evaluate(judgments: Judgments, expected_type: str, holder_name: str) -> tuple[str, list[CheckResult]]:
    if judgments.detected_type_confidence < TYPE_CONFIDENCE_THRESHOLD:
        type_status: CheckStatus = "uncertain"
    elif judgments.detected_type == expected_type:
        type_status = "pass"
    else:
        type_status = "fail"

    checks = [
        CheckResult(
            name="document_type",
            status=type_status,
            probability=judgments.expected_type_probability,
            detail=f"expected {expected_type}, detected {judgments.detected_type}",
        ),
        CheckResult(
            name="belongs_to_holder",
            status=_status_from_probability(judgments.belongs_to_holder),
            probability=judgments.belongs_to_holder,
            detail=f"holder should be {holder_name}",
        ),
    ]

    # Field presence only makes sense if the document is the type we asked for.
    if type_status != "fail":
        for field in REQUIRED_FIELDS[expected_type]:
            present = judgments.fields_present[field["name"]]
            checks.append(
                CheckResult(
                    name=f"field:{field['name']}",
                    status=_status_from_probability(present),
                    probability=present,
                    detail=field["description"],
                )
            )

    coherent = 1 - judgments.has_contradictions
    checks.append(
        CheckResult(
            name="coherent",
            status=_status_from_probability(coherent),
            probability=coherent,
            detail="no contradictory names, IDs, dates or amounts",
        )
    )

    statuses = {check.status for check in checks}
    if "fail" in statuses:
        status = "rejected"
    elif "uncertain" in statuses:
        status = "needs_review"
    else:
        status = "approved"
    return status, checks
