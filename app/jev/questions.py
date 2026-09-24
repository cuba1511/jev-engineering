from typesafe_sdk import Choice, Noul, Score


TRIAGE_QUESTIONS = {
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
}
