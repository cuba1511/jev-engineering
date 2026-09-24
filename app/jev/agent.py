from collections.abc import Mapping
from time import perf_counter

from typesafe_sdk import AsyncTypeSafeClient, JSONContent, Question, SystemOneResponse

from app.config import settings
from app.jev.questions import TRIAGE_QUESTIONS
from app.schemas import TicketTriage, TriageResult, Usage


class Jev:
    """Support-ticket triage agent backed by the Jev System One model."""

    def __init__(
        self,
        model: str = settings.model,
        input_price_per_1m: float = settings.input_price_per_1m,
        output_price_per_1m: float = settings.output_price_per_1m,
        client: AsyncTypeSafeClient | None = None,
    ) -> None:
        self.model = model
        self.input_price_per_1m = input_price_per_1m
        self.output_price_per_1m = output_price_per_1m
        self._client = client or AsyncTypeSafeClient(model=model)

    def __repr__(self) -> str:
        return f"Jev(model={self.model!r})"

    async def __aenter__(self) -> "Jev":
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    def estimate_cost(self, input_tokens: int | None, output_tokens: int | None) -> float | None:
        if input_tokens is None or output_tokens is None:
            return None
        return (
            input_tokens * self.input_price_per_1m + output_tokens * self.output_price_per_1m
        ) / 1_000_000

    async def ask(
        self, state: JSONContent, questions: Mapping[str, Question]
    ) -> tuple[SystemOneResponse, Usage]:
        """Run any set of questions over a state and measure usage, cost and latency."""
        started_at = perf_counter()
        response = await self._client.system_one(state=state, questions=questions)
        latency_seconds = perf_counter() - started_at

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        usage = Usage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=self.estimate_cost(input_tokens, output_tokens),
            latency_seconds=latency_seconds,
        )
        return response, usage

    async def triage(self, ticket_text: str) -> TriageResult:
        response, usage = await self.ask(ticket_text, TRIAGE_QUESTIONS)
        answers = response.answers

        return TriageResult(
            model=response.model,
            triage=TicketTriage(
                category=answers["category"].choice,
                category_confidence=answers["category"].confidence,
                bug_severity=answers["bug_severity"].score,
                refund_requested=answers["refund_requested"].noul,
                frustration=answers["frustration"].score,
            ),
            usage=usage,
        )
