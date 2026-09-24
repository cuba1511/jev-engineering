import os
from time import perf_counter

from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient, Choice, Score, Noul


load_dotenv()

client = TypeSafeClient(model="jev-1.13.0")   # Jev version

ticket_text = "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP."

started_at = perf_counter()
response = client.system_one(
    state=ticket_text,
    questions={
        "category": Choice(
            instructions="Determine the broad category of this support ticket",
            criteria={
                "bug_report": "Something is broken or producing errors",
                "billing": "Charges, invoices, refunds, subscriptions",
                "feature_request": "The user is requesting new functionality",
                "account": "Login, permissions, profile, security",
            },
        ),
        "bug_severity": Score(
            instructions="How severe is the reported issue",
            criteria=[
                "Cosmetic, no impact to functionality",
                "Broken or degraded feature, workaround exists",
                "Blocking issue, no workaround",
            ],
        ),
        "refund_requested": Noul(
            instructions="The user is explicitly asking for a refund or credit",
        ),
        "frustration": Score(
            instructions="How frustrated the user appears",
            criteria=["Calm", "Frustrated but civil", "Very angry"],
        ),
    },
)
latency_seconds = perf_counter() - started_at

input_tokens = response.usage.input_tokens
output_tokens = response.usage.output_tokens
input_price = float(os.getenv("INPUT_PRICE_PER_1M_TOKENS", "0.042")) ## Source: https://typesafe.ai/
output_price = float(os.getenv("OUTPUT_PRICE_PER_1M_TOKENS", "0"))

if input_tokens is not None and output_tokens is not None:
    token_cost = (
        input_tokens * float(input_price) + output_tokens * float(output_price)
    ) / 1_000_000
    token_cost_text = f"${token_cost:.6f}"
else:
    token_cost_text = "not calculated; token usage was not reported"


print(response.answers["category"].choice)  
print(response.answers["bug_severity"].score)
print(response.answers["refund_requested"].noul)
print(response.answers["frustration"].score)

print(response.answers)
print(f"Model: {response.model}")
print(f"Input tokens: {input_tokens}")
print(f"Output tokens: {output_tokens}")
print(f"Execution latency: {latency_seconds:.2f} seconds")
print(f"Input price: ${input_price:.3f} per 1M tokens")
print(f"Output price: ${output_price:.3f} per 1M tokens (free)")
print(f"Token cost: {token_cost_text}")