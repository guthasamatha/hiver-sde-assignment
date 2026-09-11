import pandas as pd

df = pd.read_csv("spotify_sample_300.csv")

print("Total sampled conversations:", len(df))

for i, row in df.head(50).iterrows():
    print("\n-----------------------------------")
    print("CUSTOMER:", row["customer_message"])
    print("SPOTIFY :", row["brand_reply"])