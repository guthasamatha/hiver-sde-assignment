from reply_retrieval import retrieve_similar
from escalation import decide_escalation
from reply_generator import generate_reply


def simple_intent_classifier(message):
    """
    Simple intent classifier used for the end-to-end demo.
    """

    text = str(message).lower()

    if any(word in text for word in [
        "login", "log in", "password", "hacked",
        "account access", "sign in", "username"
    ]):
        return "ACCOUNT_ACCESS"

    elif any(word in text for word in [
        "premium", "payment", "charged", "charge",
        "refund", "subscription", "student",
        "family plan", "trial", "billing", "cancel"
    ]):
        return "BILLING_SUBSCRIPTION"

    elif any(word in text for word in [
        "download", "downloaded", "offline"
    ]):
        return "DOWNLOAD_OFFLINE"

    elif any(word in text for word in [
        "not available", "missing song", "missing album",
        "album unavailable", "song unavailable",
        "available in my country"
    ]):
        return "CONTENT_AVAILABILITY"

    elif any(word in text for word in [
        "feature", "apple watch", "roku", "lyrics",
        "mini player", "hifi", "wish", "please add"
    ]):
        return "FEATURE_REQUEST"

    elif any(word in text for word in [
        "play", "playing", "crash", "buffer",
        "shuffle", "skip", "glitch", "not working",
        "doesn't work", "does not work"
    ]):
        return "PLAYBACK_TECHNICAL"

    else:
        return "OTHER"


def run_agent(message):

    # 1. Predict intent
    intent = simple_intent_classifier(message)

    # 2. Decide whether to escalate
    action, reason = decide_escalation(message, intent)

    # 3. Retrieve historical Spotify resolutions
    evidence = retrieve_similar(message, top_k=3)

    # 4. Generate draft reply
    draft_reply = generate_reply(
        message,
        intent,
        action,
        evidence
    )

    print("\n========================================")
    print("AI CUSTOMER SUPPORT AGENT")
    print("========================================")

    print("\nCustomer message:")
    print(message)

    print("\nPredicted intent:")
    print(intent)

    print("\nAction:")
    print(action)

    print("\nReason:")
    print(reason)

    print("\nDraft reply:")
    print(draft_reply)

    print("\nHistorical support evidence:")

    for number, item in enumerate(evidence, start=1):
        print(f"\n--- Evidence {number} ---")
        print("Similarity:", item["similarity"])
        print("Historical customer:", item["customer_message"])
        print("Spotify reply:", item["brand_reply"])


if __name__ == "__main__":

    customer_message = input("\nEnter customer message: ")

    run_agent(customer_message)