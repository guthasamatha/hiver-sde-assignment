import pandas as pd

from support_agent import simple_intent_classifier
from escalation import decide_escalation
from reply_retrieval import retrieve_similar
from reply_generator import generate_reply


# -------------------------------------------------
# 1. Load the 30-example human evaluation set
# -------------------------------------------------

df = pd.read_csv("human_eval_30.csv")

print("Evaluation examples loaded:", len(df))


# -------------------------------------------------
# 2. Generate agent outputs
# -------------------------------------------------

predicted_intents = []
predicted_actions = []
decision_reasons = []
draft_replies = []


for number, row in df.iterrows():

    message = str(row["customer_message"])

    # Predict intent
    intent = simple_intent_classifier(message)

    # Decide escalation
    action, reason = decide_escalation(
        message,
        intent
    )

    # Retrieve historical support evidence
    evidence = retrieve_similar(
        message,
        top_k=3
    )

    # Generate draft reply
    draft_reply = generate_reply(
        message,
        intent,
        action,
        evidence
    )

    predicted_intents.append(intent)
    predicted_actions.append(action)
    decision_reasons.append(reason)
    draft_replies.append(draft_reply)

    print(
        f"Processed {number + 1}/{len(df)}"
    )


# -------------------------------------------------
# 3. Add outputs to evaluation file
# -------------------------------------------------

df["predicted_intent"] = predicted_intents
df["predicted_action"] = predicted_actions
df["decision_reason"] = decision_reasons
df["draft_reply"] = draft_replies


# -------------------------------------------------
# 4. Save
# -------------------------------------------------

df.to_csv(
    "human_eval_30_with_replies.csv",
    index=False
)

print("\nDone!")
print("Created: human_eval_30_with_replies.csv")
print("Total evaluated examples:", len(df))