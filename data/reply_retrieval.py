import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------------------------
# 1. Load historical Spotify support conversations
# -------------------------------------------------

df = pd.read_csv("spotify_pairs.csv")

df = df.dropna(subset=["customer_message", "brand_reply"]).reset_index(drop=True)

print("Historical support pairs loaded:", len(df))


# -------------------------------------------------
# 2. Build WORD TF-IDF index
# -------------------------------------------------

word_vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    max_features=15000,
    sublinear_tf=True
)

word_vectors = word_vectorizer.fit_transform(
    df["customer_message"].astype(str)
)

print("Word TF-IDF index created.")


# -------------------------------------------------
# 3. Build CHARACTER TF-IDF index
# -------------------------------------------------

char_vectorizer = TfidfVectorizer(
    analyzer="char_wb",
    ngram_range=(3, 5),
    max_features=15000,
    sublinear_tf=True
)

char_vectors = char_vectorizer.fit_transform(
    df["customer_message"].astype(str)
)

print("Character TF-IDF index created.")


# -------------------------------------------------
# 4. Retrieve similar historical conversations
# -------------------------------------------------

def retrieve_similar(query, top_k=3):

    # Transform query
    query_word = word_vectorizer.transform([query])
    query_char = char_vectorizer.transform([query])

    # Calculate similarities
    word_similarity = cosine_similarity(
        query_word,
        word_vectors
    ).flatten()

    char_similarity = cosine_similarity(
        query_char,
        char_vectors
    ).flatten()

    # Combine both scores
    combined_similarity = (
        0.7 * word_similarity +
        0.3 * char_similarity
    )

    top_indices = combined_similarity.argsort()[-top_k:][::-1]

    results = []

    for index in top_indices:
        results.append({
            "customer_message": df.iloc[index]["customer_message"],
            "brand_reply": df.iloc[index]["brand_reply"],
            "similarity": round(float(combined_similarity[index]), 3)
        })

    return results


# -------------------------------------------------
# 5. Test the retriever
# -------------------------------------------------

if __name__ == "__main__":

    test_message = "I was charged twice for Spotify Premium"

    print("\nCustomer message:")
    print(test_message)

    print("\nTop historical support examples:")

    results = retrieve_similar(test_message)

    for number, result in enumerate(results, start=1):

        print(f"\n--- Result {number} ---")
        print("Similarity:", result["similarity"])
        print("Historical customer:", result["customer_message"])
        print("Spotify reply:", result["brand_reply"])