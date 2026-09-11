import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# =====================================================
# 1. LOAD GOLDEN DATASET
# =====================================================

df = pd.read_csv("golden_set.csv")

print("Dataset loaded!")
print("Total examples:", len(df))

# Customer messages are the input
X = df["customer_message"].fillna("")

# Intent is what we want to predict
y = df["intent"]

# =====================================================
# 2. TRAIN / TEST SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

print("\nTraining examples:", len(X_train))
print("Testing examples:", len(X_test))

# =====================================================
# 3. CONVERT TEXT TO TF-IDF FEATURES
# =====================================================

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    max_features=5000
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# =====================================================
# 4. TRAIN LOGISTIC REGRESSION
# =====================================================

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train_tfidf, y_train)

# =====================================================
# 5. MAKE PREDICTIONS
# =====================================================

predictions = model.predict(X_test_tfidf)

# =====================================================
# 6. EVALUATE
# =====================================================

accuracy = accuracy_score(y_test, predictions)

print("\n--- TF-IDF + LOGISTIC REGRESSION ---")
print("Accuracy:", round(accuracy, 3))
print("Accuracy %:", round(accuracy * 100, 2))

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)

# =====================================================
# 7. SAVE PREDICTIONS FOR ERROR ANALYSIS
# =====================================================

results = pd.DataFrame({
    "customer_message": X_test,
    "actual_intent": y_test,
    "predicted_intent": predictions
})

results["correct"] = (
    results["actual_intent"] == results["predicted_intent"]
)

results.to_csv("intent_test_results.csv", index=False)

print("\nSaved predictions to intent_test_results.csv")

print("\nCorrect predictions:")
print(results["correct"].value_counts())