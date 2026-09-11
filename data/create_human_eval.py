import pandas as pd

# Load the corrected golden evaluation set
df = pd.read_csv("golden_set.csv")

# Select 30 reproducible examples
sample = df.sample(n=30, random_state=42).copy()

# Keep useful information
columns_to_keep = [
    "customer_message",
    "brand_reply",
    "intent",
    "expected_action"
]

human_eval = sample[columns_to_keep].copy()

# Add empty human-rating columns
human_eval["human_relevance"] = ""
human_eval["human_groundedness"] = ""
human_eval["human_helpfulness"] = ""
human_eval["human_style"] = ""
human_eval["human_safety"] = ""
human_eval["human_notes"] = ""

# Save the evaluation sheet
human_eval.to_csv("human_eval_30.csv", index=False)

print("Human evaluation set created successfully!")
print("Examples:", len(human_eval))
print("Created: human_eval_30.csv")
print("\nEach reply should later be rated from 1 to 5 on:")
print("- Relevance")
print("- Groundedness")
print("- Helpfulness")
print("- Style")
print("- Safety")