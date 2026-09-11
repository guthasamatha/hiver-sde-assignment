import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, classification_report
from support_agent import simple_intent_classifier
from escalation import decide_escalation


# -------------------------------------------------
# 1. Load golden evaluation set
# -------------------------------------------------

df = pd.read_csv("golden_set.csv")

print("Golden evaluation set loaded:", len(df))


# -------------------------------------------------
# 2. Evaluate intent classification
# -------------------------------------------------

df["predicted_intent"] = df["customer_message"].apply(
    simple_intent_classifier
)

intent_accuracy = accuracy_score(
    df["intent"],
    df["predicted_intent"]
)

intent_macro_f1 = f1_score(
    df["intent"],
    df["predicted_intent"],
    average="macro"
)

print("\n========================================")
print("INTENT EVALUATION")
print("========================================")

print("Intent Accuracy:", round(intent_accuracy, 3))
print("Intent Accuracy %:", round(intent_accuracy * 100, 1))
print("Intent Macro F1:", round(intent_macro_f1, 3))

print("\nClassification Report:")
print(
    classification_report(
        df["intent"],
        df["predicted_intent"],
        zero_division=0
    )
)


# -------------------------------------------------
# 3. Evaluate escalation decisions
# -------------------------------------------------

predicted_actions = []
decision_reasons = []

for _, row in df.iterrows():

    action, reason = decide_escalation(
        row["customer_message"],
        row["predicted_intent"]
    )

    predicted_actions.append(action)
    decision_reasons.append(reason)

df["predicted_action"] = predicted_actions
df["decision_reason"] = decision_reasons


action_accuracy = accuracy_score(
    df["expected_action"],
    df["predicted_action"]
)

action_macro_f1 = f1_score(
    df["expected_action"],
    df["predicted_action"],
    average="macro"
)

print("\n========================================")
print("ESCALATION EVALUATION")
print("========================================")

print("Action Accuracy:", round(action_accuracy, 3))
print("Action Accuracy %:", round(action_accuracy * 100, 1))
print("Action Macro F1:", round(action_macro_f1, 3))

print("\nAction Classification Report:")
print(
    classification_report(
        df["expected_action"],
        df["predicted_action"],
        zero_division=0
    )
)


# -------------------------------------------------
# 4. Save evaluation results
# -------------------------------------------------

df.to_csv("agent_evaluation_results.csv", index=False)

print("\nSaved detailed results to agent_evaluation_results.csv")