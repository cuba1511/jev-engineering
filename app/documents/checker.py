from app.documents.policy import Judgments, evaluate
from app.documents.questions import REQUIRED_FIELDS, build_questions
from app.jev import Jev
from app.schemas import DocumentType, DocumentVerification


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

        judgments = Judgments(
            detected_type=detected.choice,
            detected_type_confidence=detected.confidence,
            expected_type_probability=detected.probabilities.get(expected_type, 0.0),
            belongs_to_holder=answers["belongs_to_holder"].noul,
            fields_present={
                field["name"]: answers[f"field_{field['name']}"].noul
                for field in REQUIRED_FIELDS[expected_type]
            },
            has_contradictions=answers["has_contradictions"].noul,
        )
        status, checks = evaluate(judgments, expected_type, holder_name)

        return DocumentVerification(
            model=response.model,
            status=status,
            detected_type=detected.choice,
            detected_type_confidence=detected.confidence,
            checks=checks,
            usage=usage,
        )
