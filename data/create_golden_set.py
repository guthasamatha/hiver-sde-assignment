import pandas as pd

# Load the 300 conversations we sampled earlier
df = pd.read_csv("spotify_sample_300.csv")

# Select 200 examples reproducibly
golden = df.sample(n=200, random_state=123).copy()

# Add empty columns for manual labels
golden["intent"] = ""
golden["expected_action"] = ""
golden["label_notes"] = ""

# Save the template
golden.to_csv("golden_set.csv", index=False)

print("Golden set created successfully!")
print("Total examples:", len(golden))
print("\nColumns:")
print(golden.columns.tolist())

print("\nFirst 20 golden-set examples:")

for number, (_, row) in enumerate(golden.head(20).iterrows(), start=1):
    print("\n-----------------------------------")
    print("EXAMPLE:", number)
    print("CUSTOMER:", row["customer_message"])
    print("SPOTIFY :", row["brand_reply"])