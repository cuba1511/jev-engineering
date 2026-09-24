"""Same documents, same questions, same verdict policy, answered by an OpenAI chat model.

OpenAI answers with booleans instead of probabilities, so each yes/no becomes 1.0 or 0.0
and the type confidence is 1.0. Everything else goes through `policy.evaluate` unchanged.
"""

import json
from time import perf_counter

from openai import AsyncOpenAI

from app.config import settings
from app.documents.policy import Judgments, evaluate
from app.documents.questions import build_questions
from app.schemas import DocumentVerification, Usage


SYSTEM_PROMPT = (
    "You verify documents. Answer every question about `document` using the question definitions "
    "provided, and return only JSON matching the schema."
)


def _response_schema(questions: dict) -> dict:
    properties = {
        name: {"type": "string", "enum": list(question.criteria.keys())}
        if name == "document_type"
        else {"type": "boolean"}
        for name, question in questions.items()
    }
    return {
        "name": "document_verification",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": properties,
            "required": list(properties),
            "additionalProperties": False,
        },
    }


class OpenAIDocumentChecker:
    def __init__(self, model: str = settings.openai_model, client: AsyncOpenAI | None = None) -> None:
        self.model = model
        self._client = client or AsyncOpenAI(api_key=settings.openai_api_key)

    async def close(self) -> None:
        await self._client.close()

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float | None:
        if settings.openai_input_price_per_1m is None or settings.openai_output_price_per_1m is None:
            return None
        return (
            input_tokens * settings.openai_input_price_per_1m + output_tokens * settings.openai_output_price_per_1m
        ) / 1_000_000

    async def verify(self, document_text: str, expected_type: str, holder_name: str) -> DocumentVerification:
        questions = build_questions(expected_type)
        state = {
            "expected": {"document_type": expected_type, "holder_name": holder_name},
            "document": document_text,
        }
        question_definitions = {
            name: question.model_dump(exclude_none=True) for name, question in questions.items()
        }

        started_at = perf_counter()
        completion = await self._client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_schema", "json_schema": _response_schema(questions)},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {"state": state, "questions": question_definitions}, ensure_ascii=False
                    ),
                },
            ],
        )
        latency_seconds = perf_counter() - started_at
        answers = json.loads(completion.choices[0].message.content)

        detected_type = answers["document_type"]
        judgments = Judgments(
            detected_type=detected_type,
            detected_type_confidence=1.0,
            expected_type_probability=float(detected_type == expected_type),
            belongs_to_holder=float(answers["belongs_to_holder"]),
            fields_present={
                name.removeprefix("field_"): float(value)
                for name, value in answers.items()
                if name.startswith("field_")
            },
            has_contradictions=float(answers["has_contradictions"]),
        )
        status, checks = evaluate(judgments, expected_type, holder_name)

        input_tokens = completion.usage.prompt_tokens
        output_tokens = completion.usage.completion_tokens
        return DocumentVerification(
            model=completion.model,
            status=status,
            detected_type=detected_type,
            detected_type_confidence=1.0,
            checks=checks,
            usage=Usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=self.estimate_cost(input_tokens, output_tokens),
                latency_seconds=latency_seconds,
            ),
        )
