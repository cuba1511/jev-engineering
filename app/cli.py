import argparse
import asyncio

from app.jev import Jev


DEFAULT_TICKET = "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP."


async def run(ticket_text: str) -> None:
    async with Jev() as jev:
        result = await jev.triage(ticket_text)

    cost = result.usage.cost_usd
    print(result.triage.model_dump_json(indent=2))
    print(f"Model: {result.model}")
    print(f"Input tokens: {result.usage.input_tokens}")
    print(f"Output tokens: {result.usage.output_tokens}")
    print(f"Execution latency: {result.usage.latency_seconds:.2f} seconds")
    print(f"Input price: ${jev.input_price_per_1m:.3f} per 1M tokens")
    print(f"Output price: ${jev.output_price_per_1m:.3f} per 1M tokens")
    print(f"Token cost: {f'${cost:.6f}' if cost is not None else 'not calculated; token usage was not reported'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Triage a support ticket with Jev")
    parser.add_argument("ticket_text", nargs="?", default=DEFAULT_TICKET)
    asyncio.run(run(parser.parse_args().ticket_text))


if __name__ == "__main__":
    main()
