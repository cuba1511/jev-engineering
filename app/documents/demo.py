"""Run every sample document through the checker: python -m app.documents.demo"""

import asyncio

from app.documents import DocumentChecker
from app.documents.samples import SAMPLES
from app.jev import Jev


STATUS_ICONS = {"pass": "✅", "fail": "❌", "uncertain": "⚠️ ", "approved": "✅", "rejected": "❌", "needs_review": "⚠️ "}


async def main() -> None:
    async with Jev() as jev:
        checker = DocumentChecker(jev)
        results = await asyncio.gather(
            *(checker.verify(s.document_text, s.expected_type, s.holder_name) for s in SAMPLES)
        )

    total_cost = 0.0
    hits = 0
    for sample, result in zip(SAMPLES, results):
        hits += result.status == sample.expected_status
        total_cost += result.usage.cost_usd or 0.0
        print(f"\n{STATUS_ICONS[result.status]} {sample.title}")
        print(f"   expected {sample.expected_type} for {sample.holder_name} → {result.status.upper()} "
              f"(detected {result.detected_type}, {result.detected_type_confidence:.0%})")
        for check in result.checks:
            print(f"   {STATUS_ICONS[check.status]} {check.name:<22} {check.probability:>5.0%}  {check.detail}")
        print(f"   {result.usage.input_tokens} in / {result.usage.output_tokens} out tokens · "
              f"{result.usage.latency_seconds:.2f}s")

    print(f"\n{hits}/{len(SAMPLES)} documents got the expected verdict · total cost ${total_cost:.6f}")


if __name__ == "__main__":
    asyncio.run(main())
