import pandas as pd

FILE_NAME = "human_eval_30_with_replies.csv"

df = pd.read_csv(FILE_NAME)

print("Human Rating Helper")
print("===================")
print("Rate each criterion from 1 to 5.")
print("5 = Excellent")
print("4 = Good")
print("3 = Acceptable but incomplete")
print("2 = Poor")
print("1 = Very poor/wrong")


def get_score(name):
    while True:
        try:
            score = int(input(f"{name} (1-5): "))

            if 1 <= score <= 5:
                return score

            print("Please enter a number from 1 to 5.")

        except ValueError:
            print("Please enter only a number from 1 to 5.")


for index, row in df.iterrows():

    # Skip examples already rated
    if pd.notna(row["human_relevance"]):
        continue

    print("\n")
    print("=" * 70)
    print(f"EXAMPLE {index + 1} OF {len(df)}")
    print("=" * 70)

    print("\nCUSTOMER MESSAGE:")
    print(row["customer_message"])

    print("\nHISTORICAL SPOTIFY REPLY:")
    print(row["brand_reply"])

    print("\nOUR AGENT DRAFT REPLY:")
    print(row["draft_reply"])

    print("\nEXPECTED INTENT:")
    print(row["intent"])

    print("\nEXPECTED ACTION:")
    print(row["expected_action"])

    print("\nPREDICTED INTENT:")
    print(row["predicted_intent"])

    print("\nPREDICTED ACTION:")
    print(row["predicted_action"])

    print("\n--- ENTER YOUR HUMAN RATINGS ---")

    relevance = get_score("Relevance")
    groundedness = get_score("Groundedness")
    helpfulness = get_score("Helpfulness")
    style = get_score("Style")
    safety = get_score("Safety")

    notes = input("Short note (optional): ")

    df.loc[index, "human_relevance"] = relevance
    df.loc[index, "human_groundedness"] = groundedness
    df.loc[index, "human_helpfulness"] = helpfulness
    df.loc[index, "human_style"] = style
    df.loc[index, "human_safety"] = safety
    df.loc[index, "human_notes"] = notes

    # Save after every example
    df.to_csv(FILE_NAME, index=False)

    print("\nSaved successfully!")

print("\n======================================")
print("All 30 human evaluations are complete!")
print("======================================")