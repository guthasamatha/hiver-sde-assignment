def generate_reply(message, intent, action, evidence):
    """
    Generate a safe draft reply using the predicted intent,
    escalation decision, and retrieved historical support evidence.
    """

    # If human investigation is required
    if action == "ESCALATE":

        if intent == "BILLING_SUBSCRIPTION":
            return (
                "Sorry about the billing issue. We'd like to look into "
                "your account and payment details. Please contact support "
                "through a private channel so the team can investigate "
                "the charge securely."
            )

        elif intent == "ACCOUNT_ACCESS":
            return (
                "Sorry you're having trouble accessing your account. "
                "For security, this needs account-specific assistance. "
                "Please contact support through a private channel so the "
                "team can verify your account and help restore access."
            )

        else:
            return (
                "Sorry you're experiencing this issue. This appears to "
                "require account-specific investigation, so we're "
                "escalating it to a human support agent."
            )

    # Safe automatic replies for common intents
    if intent == "DOWNLOAD_OFFLINE":
        return (
            "It sounds like you have a question about downloads or "
            "offline listening. Check that you're signed into the correct "
            "account and that your device is online periodically so your "
            "downloads remain available."
        )

    elif intent == "CONTENT_AVAILABILITY":
        return (
            "Thanks for flagging this. Music availability can vary based "
            "on licensing and region. The catalog may change when content "
            "becomes available or unavailable."
        )

    elif intent == "FEATURE_REQUEST":
        return (
            "Thanks for the suggestion! We appreciate the feedback and "
            "will treat this as a feature request."
        )

    elif intent == "PLAYBACK_TECHNICAL":
        return (
            "Sorry you're having trouble with playback. Please restart "
            "the app, check your connection, and make sure you're using "
            "the latest version. If the problem continues, further "
            "troubleshooting may be needed."
        )

    elif intent == "BILLING_SUBSCRIPTION":
        return (
            "Thanks for reaching out. For general Premium or subscription "
            "questions, please check your current plan and payment details "
            "in your account settings."
        )

    elif intent == "ACCOUNT_ACCESS":
        return (
            "Please check your login details and try the account recovery "
            "options. If you still cannot access the account, a support "
            "agent may need to investigate."
        )

    else:
        # Use evidence only as a signal that historical support exists.
        # We deliberately avoid copying historical replies verbatim.
        if evidence:
            return (
                "Thanks for reaching out. We found similar historical "
                "support cases, but there isn't enough confidence to give "
                "a specific automated resolution. Please provide more "
                "details about the issue."
            )

        return (
            "Thanks for reaching out. Please provide a little more "
            "information about the issue so we can help."
        )


# -------------------------------------------------
# Simple test
# -------------------------------------------------

if __name__ == "__main__":

    test_message = "I was charged twice for Spotify Premium"
    test_intent = "BILLING_SUBSCRIPTION"
    test_action = "ESCALATE"
    test_evidence = []

    reply = generate_reply(
        test_message,
        test_intent,
        test_action,
        test_evidence
    )

    print("Customer:", test_message)
    print("Intent:", test_intent)
    print("Action:", test_action)
    print("Draft reply:", reply)