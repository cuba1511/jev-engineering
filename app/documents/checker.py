from app.documents.questions import REQUIRED_FIELDS, build_questions
from app.jev import Jev
from app.schemas import CheckResult, CheckStatus, DocumentType, DocumentVerification


# Starting points, not universal rules: tune them on your own labeled documents.
PASS_THRESHOLD = 0.8
FAIL_THRESHOLD = 0.2
TYPE_CONFIDENCE_THRESHOLD = 0.8


def _status_from_probability(probability: float) -> CheckStatus:
    if probability >= PASS_THRESHOLD:
        return "pass"
    if probability <= FAIL_THRESHOLD:
        return "fail"
    return "uncertain"


class DocumentChecker:
    """Checks that an uploaded document is what we expected: right type, right person, complete and coherent."""

    def __init__(self, jev: Jev) -> None:
        self.jev = jev

    async def verify(
        self, document_text: str, expected_type: DocumentType, holder_name: str
    ) -> DocumentVerification:
        state = {
            "expected": {"document_type": expected_type, "holder_name": holder_name},
            "document": document_text,
        }
        response, usage = await self.jev.ask(state, build_questions(expected_type))
        answers = response.answers

        detected = answers["document_type"]
        if detected.confidence < TYPE_CONFIDENCE_THRESHOLD:
            type_status: CheckStatus = "uncertain"
        elif detected.choice == expected_type:
            type_status = "pass"
        else:
            type_status = "fail"

        checks = [
            CheckResult(
                name="document_type",
                status=type_status,
                probability=detected.probabilities.get(expected_type, 0.0),
                detail=f"expected {expected_type}, detected {detected.choice}",
            ),
            CheckResult(
                name="belongs_to_holder",
                status=_status_from_probability(answers["belongs_to_holder"].noul),
                probability=answers["belongs_to_holder"].noul,
                detail=f"holder should be {holder_name}",
            ),
        ]

        # Field presence only makes sense if the document is the type we asked for.
        if type_status != "fail":
            for field in REQUIRED_FIELDS[expected_type]:
                present = answers[f"field_{field['name']}"].noul
                checks.append(
                    CheckResult(
                        name=f"field:{field['name']}",
                        status=_status_from_probability(present),
                        probability=present,
                        detail=field["description"],
                    )
                )

        coherent = 1 - answers["has_contradictions"].noul
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

        return DocumentVerification(
            model=response.model,
            status=status,
            detected_type=detected.choice,
            detected_type_confidence=detected.confidence,
            checks=checks,
            usage=usage,
        )
