import pandas as pd

df = pd.read_csv(
    "twcs.csv",
    usecols=[
        "tweet_id",
        "author_id",
        "inbound",
        "text",
        "response_tweet_id",
        "in_response_to_tweet_id"
    ]
)

print("Dataset loaded:", len(df))

# Select replies written by Spotify support
spotify_replies = df[
    (df["author_id"] == "SpotifyCares") &
    (df["inbound"] == False)
].copy()

print("Spotify support replies:", len(spotify_replies))

# Remove replies where we cannot identify the previous customer tweet
spotify_replies = spotify_replies.dropna(
    subset=["in_response_to_tweet_id"]
)

spotify_replies["in_response_to_tweet_id"] = (
    spotify_replies["in_response_to_tweet_id"].astype(int)
)

# Select customer tweets
customer_tweets = df[df["inbound"] == True][
    ["tweet_id", "text"]
].copy()

# Connect each customer message to Spotify's reply
pairs = customer_tweets.merge(
    spotify_replies[
        ["in_response_to_tweet_id", "text"]
    ],
    left_on="tweet_id",
    right_on="in_response_to_tweet_id",
    how="inner"
)

pairs = pairs.rename(
    columns={
        "text_x": "customer_message",
        "text_y": "brand_reply"
    }
)

pairs = pairs[
    ["tweet_id", "customer_message", "brand_reply"]
]

print("\nCustomer -> Spotify pairs:", len(pairs))

print("\nFirst 10 examples:")

for _, row in pairs.head(10).iterrows():
    print("\nCUSTOMER:", row["customer_message"])
    print("SPOTIFY :", row["brand_reply"])

# Save smaller dataset
pairs.to_csv("spotify_pairs.csv", index=False)

print("\nSaved spotify_pairs.csv successfully!")

# Take 300 random conversations for manual analysis
sample = pairs.sample(n=300, random_state=42)

# Save the sample
sample.to_csv("spotify_sample_300.csv", index=False)

print("Saved spotify_sample_300.csv successfully!")