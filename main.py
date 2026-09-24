from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient, Choice, Score, Noul


load_dotenv()

client = TypeSafeClient(model="jev-1.13.0")   # Jev version

ticket_text = "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP."

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


print(response.answers["category"].choice)  
print(response.answers["bug_severity"].score)
print(response.answers["refund_requested"].noul)
print(response.answers["frustration"].score)

print(response.answers)