import pandas as pd

df = pd.read_csv("golden_set.csv")

print("Total rows:", len(df))

print("\nMissing values:")
print(df[["intent", "expected_action"]].isnull().sum())

print("\nIntent counts:")
print(df["intent"].value_counts())

print("\nFirst 20 labelled examples:\n")

for i, row in df.iloc[20:60].iterrows():
    print("=" * 70)
    print("Excel Row:", i + 2)
    print("MESSAGE:", row["customer_message"])
    print("INTENT:", row["intent"])
    print("ACTION:", row["expected_action"])