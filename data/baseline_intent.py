import pandas as pd

# Load the hand-labelled golden dataset
df = pd.read_csv("golden_set.csv")

print("Golden set loaded successfully!")
print("Total examples:", len(df))

print("\nIntent distribution:")
print(df["intent"].value_counts())

print("\nAction distribution:")
print(df["expected_action"].value_counts())

# =====================================================
# BASELINE 1: MAJORITY CLASS
# =====================================================

# Find the most common intent
majority_intent = df["intent"].value_counts().idxmax()

print("\n--- BASELINE 1: MAJORITY CLASS ---")
print("Most common intent:", majority_intent)

# Predict the same intent for every example
df["baseline_prediction"] = majority_intent

# Calculate accuracy
accuracy = (
    df["baseline_prediction"] == df["intent"]
).mean()

print("Baseline accuracy:", round(accuracy, 3))
print("Baseline accuracy %:", round(accuracy * 100, 2))


# =====================================================
# BASELINE 2: KEYWORD-BASED CLASSIFIER
# =====================================================

def keyword_classifier(text):

    text = str(text).lower()

    # Account access
    if any(word in text for word in [
        "login", "log in", "password", "hacked",
        "account access", "sign in", "username"
    ]):
        return "ACCOUNT_ACCESS"

    # Billing / subscription
    elif any(word in text for word in [
        "premium", "payment", "charged", "charge",
        "refund", "subscription", "student",
        "family plan", "trial", "billing", "cancel"
    ]):
        return "BILLING_SUBSCRIPTION"

    # Download / offline
    elif any(word in text for word in [
        "download", "downloaded", "offline"
    ]):
        return "DOWNLOAD_OFFLINE"

    # Content availability
    elif any(word in text for word in [
        "not available", "missing song", "missing album",
        "album unavailable", "song unavailable",
        "available in my country"
    ]):
        return "CONTENT_AVAILABILITY"

    # Feature request
    elif any(word in text for word in [
        "feature", "apple watch", "roku", "lyrics",
        "mini player", "hifi", "wish", "please add"
    ]):
        return "FEATURE_REQUEST"

    # Playback / technical
    elif any(word in text for word in [
        "play", "playing", "crash", "buffer",
        "shuffle", "skip", "glitch", "not working",
        "doesn't work", "does not work"
    ]):
        return "PLAYBACK_TECHNICAL"

    # Anything else
    else:
        return "OTHER"


df["keyword_prediction"] = df["customer_message"].apply(
    keyword_classifier
)

keyword_accuracy = (
    df["keyword_prediction"] == df["intent"]
).mean()

print("\n--- BASELINE 2: KEYWORD CLASSIFIER ---")
print("Keyword baseline accuracy:", round(keyword_accuracy, 3))
print("Keyword baseline accuracy %:", round(keyword_accuracy * 100, 2))