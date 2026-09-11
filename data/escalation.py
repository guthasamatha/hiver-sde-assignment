def decide_escalation(message, intent):
    """
    Decide whether a customer request can be handled automatically
    or should be escalated to a human agent.

    Returns:
        action: AUTO_HANDLE or ESCALATE
        reason: explanation for the decision
    """

    text = str(message).lower()

    # Account access/security issues
    account_risk_words = [
        "hacked",
        "can't login",
        "cannot login",
        "can't log in",
        "cannot log in",
        "password reset",
        "account stolen",
        "someone using my account"
    ]

    if intent == "ACCOUNT_ACCESS":
        if any(word in text for word in account_risk_words):
            return (
                "ESCALATE",
                "Account access or security issue requires account-specific investigation."
            )

    # Billing/refund/charge issues
    billing_risk_words = [
        "charged twice",
        "double charged",
        "duplicate charge",
        "refund",
        "wrong charge",
        "unauthorized charge",
        "charged me",
        "money back"
    ]

    if intent == "BILLING_SUBSCRIPTION":
        if any(word in text for word in billing_risk_words):
            return (
                "ESCALATE",
                "Billing or refund issue may require access to account-specific payment information."
            )

    # Explicit request for human assistance
    human_request_words = [
        "human agent",
        "real person",
        "speak to someone",
        "talk to someone"
    ]

    if any(word in text for word in human_request_words):
        return (
            "ESCALATE",
            "Customer explicitly requested human assistance."
        )

    # Everything else can initially be handled automatically
    return (
        "AUTO_HANDLE",
        "Request can be answered using known support information and historical resolutions."
    )


# -------------------------------------------------
# Simple tests
# -------------------------------------------------

if __name__ == "__main__":

    examples = [
        (
            "I was charged twice for Spotify Premium",
            "BILLING_SUBSCRIPTION"
        ),
        (
            "How many devices can download music?",
            "DOWNLOAD_OFFLINE"
        ),
        (
            "I forgot my password and cannot login",
            "ACCOUNT_ACCESS"
        ),
        (
            "Please add Spotify support for my device",
            "FEATURE_REQUEST"
        )
    ]

    for message, intent in examples:

        action, reason = decide_escalation(message, intent)

        print("\nCustomer:", message)
        print("Intent:", intent)
        print("Decision:", action)
        print("Reason:", reason)