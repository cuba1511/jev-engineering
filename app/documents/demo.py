"""Run every sample document through the checker: python -m app.documents.demo

If OPENAI_API_KEY is set, the same documents also run through an OpenAI baseline for comparison.
"""

import asyncio
from time import perf_counter

from app.config import settings
from app.documents import DocumentChecker
from app.documents.samples import SAMPLES
from app.jev import Jev
from app.schemas import DocumentVerification


STATUS_ICONS = {"pass": "✅", "fail": "❌", "uncertain": "⚠️ ", "approved": "✅", "rejected": "❌", "needs_review": "⚠️ "}


async def run_all(checker) -> tuple[list[DocumentVerification], float]:
    started_at = perf_counter()
    results = await asyncio.gather(
        *(checker.verify(s.document_text, s.expected_type, s.holder_name) for s in SAMPLES)
    )
    return results, perf_counter() - started_at


def summarize(results: list[DocumentVerification], wall_seconds: float) -> dict:
    costs = [r.usage.cost_usd for r in results]
    latencies = [r.usage.latency_seconds for r in results]
    return {
        "model": results[0].model,
        "hits": sum(r.status == s.expected_status for s, r in zip(SAMPLES, results)),
        "total_cost": None if None in costs else sum(costs),
        "wall_seconds": wall_seconds,
        "avg_latency": sum(latencies) / len(latencies),
        "input_tokens": sum(r.usage.input_tokens or 0 for r in results),
        "output_tokens": sum(r.usage.output_tokens or 0 for r in results),
    }


def print_details(results: list[DocumentVerification]) -> None:
    for sample, result in zip(SAMPLES, results):
        print(f"\n{STATUS_ICONS[result.status]} {sample.title}")
        print(f"   expected {sample.expected_type} for {sample.holder_name} → {result.status.upper()} "
              f"(detected {result.detected_type}, {result.detected_type_confidence:.0%})")
        for check in result.checks:
            print(f"   {STATUS_ICONS[check.status]} {check.name:<22} {check.probability:>5.0%}  {check.detail}")
        print(f"   {result.usage.input_tokens} in / {result.usage.output_tokens} out tokens · "
              f"{result.usage.latency_seconds:.2f}s")


def print_summary(rows: list[dict]) -> None:
    print(f"\n{'Model':<22} {'Correct':>8} {'Total time':>11} {'Avg/doc':>8} {'Tokens in/out':>15} {'Total cost':>12}")
    for row in rows:
        cost = f"${row['total_cost']:.6f}" if row["total_cost"] is not None else "set prices"
        print(f"{row['model']:<22} {row['hits']:>6}/{len(SAMPLES)} {row['wall_seconds']:>10.2f}s "
              f"{row['avg_latency']:>7.2f}s {row['input_tokens']:>7}/{row['output_tokens']:<7} {cost:>12}")

    if len(rows) == 2:
        jev, other = rows
        print(f"\nJev is {other['avg_latency'] / jev['avg_latency']:.1f}x faster per document than {other['model']}", end="")
        if jev["total_cost"] and other["total_cost"]:
            print(f" and {other['total_cost'] / jev['total_cost']:.0f}x cheaper", end="")
        print(".")


async def main() -> None:
    async with Jev() as jev:
        jev_results, jev_wall = await run_all(DocumentChecker(jev))
    print_details(jev_results)
    rows = [summarize(jev_results, jev_wall)]

    if settings.openai_api_key:
        from app.documents.openai_baseline import OpenAIDocumentChecker

        baseline = OpenAIDocumentChecker()
        try:
            openai_results, openai_wall = await run_all(baseline)
        finally:
            await baseline.close()
        rows.append(summarize(openai_results, openai_wall))
    else:
        print("\n(Set OPENAI_API_KEY in .env to compare against OpenAI.)")

    print_summary(rows)


if __name__ == "__main__":
    asyncio.run(main())
