import pandas as pd

# Load the golden dataset
df = pd.read_csv("golden_set.csv")

print("Golden set loaded successfully!")
print("Total examples:", len(df))

# Make a backup before changing anything
df.to_csv("golden_set_backup.csv", index=False)

print("Backup created: golden_set_backup.csv")

# Show every example with its row number
print("\n--- ALL GOLDEN SET EXAMPLES ---")

for i, row in df.iterrows():
    print("=" * 80)
    print("Excel Row:", i + 2)
    print("MESSAGE:", row["customer_message"])
    print("CURRENT INTENT:", row["intent"])
    print("CURRENT ACTION:", row["expected_action"])


# Columns that were shifted
label_cols = ["intent", "expected_action", "label_notes"]

# Excel Row 28 is the first row after the correctly labelled
# Family Plan question at Excel Row 27.
# Excel Row 28 = dataframe index 26.
start_index = 26

# Shift the existing labels ONE ROW UP
# so each message receives the label that currently belongs to the next row.
df.loc[start_index:len(df)-2, label_cols] = (
    df.loc[start_index + 1:len(df)-1, label_cols].to_numpy()
)

# We cannot recover the final row automatically because there
# is no next row from which to copy a label.
df.loc[len(df)-1, "intent"] = "REVIEW_NEEDED"
df.loc[len(df)-1, "expected_action"] = "REVIEW_NEEDED"
df.loc[len(df)-1, "label_notes"] = "Final example requires manual review"

# Save as a NEW file first — do not overwrite golden_set.csv yet
df.to_csv("golden_set_fixed.csv", index=False)

print("Label shift completed.")
print("Created: golden_set_fixed.csv")
print("Original golden_set.csv was NOT overwritten.")
print("Final row marked REVIEW_NEEDED.")