import os
import re
import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score


# -----------------------------
# CREATE FOLDERS
# -----------------------------
os.makedirs("model", exist_ok=True)


# -----------------------------
# CLEAN TEXT
# -----------------------------
def clean_text(text):
    text = str(text).lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Remove special characters
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# -----------------------------
# LOAD DATA
# -----------------------------
print("Loading datasets...")

fake = pd.read_csv("dataset/Fake.csv")
real = pd.read_csv("dataset/True.csv")


# 0 = FAKE
fake["label"] = 0

# 1 = REAL
real["label"] = 1


# Combine title and text
fake["content"] = (
    fake["title"].fillna("") + " " +
    fake["text"].fillna("")
)

real["content"] = (
    real["title"].fillna("") + " " +
    real["text"].fillna("")
)


# Combine both datasets
data = pd.concat([
    fake[["content", "label"]],
    real[["content", "label"]]
])


# Remove empty rows
data.dropna(inplace=True)

print("Total articles:", len(data))


# -----------------------------
# CLEAN DATA
# -----------------------------
print("Cleaning text...")

data["content"] = data["content"].apply(clean_text)


# -----------------------------
# SPLIT DATA
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    data["content"],
    data["label"],
    test_size=0.20,
    random_state=42,
    stratify=data["label"]
)


# -----------------------------
# CREATE PIPELINE
# -----------------------------
pipeline = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            stop_words="english",
            max_df=0.95,
            min_df=2,
            ngram_range=(1, 2)
        )
    ),

    (
        "model",
        LogisticRegression(
            max_iter=1000
        )
    )
])


# -----------------------------
# TRAIN MODEL
# -----------------------------
print("Training model...")

pipeline.fit(X_train, y_train)


# -----------------------------
# TEST MODEL
# -----------------------------
print("Testing model...")

predictions = pipeline.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)

print("\nModel Accuracy:")
print(f"{accuracy * 100:.2f}%")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        target_names=["Fake", "Real"]
    )
)


# -----------------------------
# SAVE MODEL
# -----------------------------
joblib.dump(
    pipeline,
    "model/fake_news_model.pkl"
)

print("\nModel saved successfully!")
print("Location: model/fake_news_model.pkl")