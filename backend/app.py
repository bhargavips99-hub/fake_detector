import os
import re
import joblib

from flask import Flask, request, jsonify
from flask_cors import CORS


# --------------------------------
# CREATE APP
# --------------------------------
app = Flask(__name__)

CORS(app)


# --------------------------------
# LOAD MODEL
# --------------------------------
MODEL_PATH = "model/fake_news_model.pkl"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        "Model not found. "
        "Please run train_model.py first."
    )

model = joblib.load(MODEL_PATH)


# --------------------------------
# CLEAN TEXT
# --------------------------------
def clean_text(text):

    text = str(text).lower()

    # Remove URLs
    text = re.sub(
        r"http\S+|www\S+",
        " ",
        text
    )

    # Remove special characters
    text = re.sub(
        r"[^a-zA-Z\s]",
        " ",
        text
    )

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# --------------------------------
# CLICKBAIT ANALYSIS
# --------------------------------
def analyze_clickbait(text):

    suspicious_words = [

        "shocking",
        "unbelievable",
        "secret",
        "urgent",
        "must read",
        "breaking",
        "exposed",
        "viral",
        "100 percent",
        "miracle",
        "they dont want you to know",
        "share immediately"

    ]

    text_lower = text.lower()

    detected_words = []

    for word in suspicious_words:

        if word in text_lower:
            detected_words.append(word)

    return detected_words


# --------------------------------
# TEXT WARNING SIGNALS
# --------------------------------
def analyze_text_signals(text):

    warnings = []

    # Excessive uppercase
    letters = [
        char for char in text
        if char.isalpha()
    ]

    if len(letters) > 20:

        uppercase_count = sum(
            char.isupper()
            for char in letters
        )

        uppercase_ratio = (
            uppercase_count /
            len(letters)
        )

        if uppercase_ratio > 0.50:

            warnings.append(
                "Excessive capital letters detected"
            )


    # Too many exclamation marks
    if text.count("!") >= 3:

        warnings.append(
            "Excessive exclamation marks detected"
        )


    # Very short claim
    words = text.split()

    if len(words) < 15:

        warnings.append(
            "Very short claim - limited context available"
        )


    return warnings


# --------------------------------
# CALCULATE TRUST SCORE
# --------------------------------
def calculate_trust_score(
    model_probability,
    prediction,
    clickbait_words,
    warnings
):

    # Start with model probability

    if prediction == 1:
        trust_score = model_probability

    else:
        trust_score = 100 - model_probability


    # Penalize suspicious signals
    trust_score -= (
        len(clickbait_words) * 5
    )

    trust_score -= (
        len(warnings) * 5
    )


    # Keep score between 0 and 100
    trust_score = max(
        0,
        min(100, trust_score)
    )

    return round(trust_score, 2)


# --------------------------------
# GENERATE FINAL LABEL
# --------------------------------
def get_final_label(
    prediction,
    confidence,
    trust_score
):

    if (
        prediction == 1
        and trust_score >= 70
    ):

        return "Likely Reliable"


    elif (
        prediction == 0
        and confidence >= 70
    ):

        return "Likely Misleading"


    else:

        return "Needs Verification"


# --------------------------------
# GENERATE EXPLANATION
# --------------------------------
def generate_explanation(
    prediction,
    clickbait_words,
    warnings,
    confidence
):

    reasons = []

    if prediction == 0:

        reasons.append(
            "The AI model found patterns "
            "similar to articles labelled as "
            "misleading in its training data."
        )

    else:

        reasons.append(
            "The AI model found patterns "
            "similar to articles labelled as "
            "reliable in its training data."
        )


    if clickbait_words:

        reasons.append(
            "Clickbait-style words detected: "
            + ", ".join(clickbait_words)
        )


    reasons.extend(warnings)


    if confidence < 70:

        reasons.append(
            "The AI confidence is moderate, "
            "so independent verification is recommended."
        )


    return reasons


# --------------------------------
# HOME API
# --------------------------------
@app.route("/", methods=["GET"])
def home():

    return jsonify({

        "project": "TrustLens",
        "description": (
            "AI-based Fake News Detection "
            "and Verification System"
        ),

        "status": "Backend is running",

        "endpoint": "/api/analyze"

    })


# --------------------------------
# ANALYZE API
# --------------------------------
@app.route(
    "/api/analyze",
    methods=["POST"]
)
def analyze_news():

    try:

        # Get JSON data
        data = request.get_json()


        # Check request
        if not data:

            return jsonify({

                "success": False,

                "error": (
                    "No JSON data received"
                )

            }), 400


        # Get news text
        news_text = data.get(
            "text",
            ""
        ).strip()


        # Validate
        if not news_text:

            return jsonify({

                "success": False,

                "error": (
                    "News text is required"
                )

            }), 400


        # Clean text
        cleaned_text = clean_text(
            news_text
        )


        # -------------------------
        # AI PREDICTION
        # -------------------------
        prediction = model.predict(
            [cleaned_text]
        )[0]


        probabilities = (
            model.predict_proba(
                [cleaned_text]
            )[0]
        )


        # 0 = fake
        # 1 = real
        probability = (
            probabilities[prediction]
            * 100
        )


        confidence = round(
            probability,
            2
        )


        # -------------------------
        # CLICKBAIT CHECK
        # -------------------------
        clickbait_words = (
            analyze_clickbait(
                news_text
            )
        )


        # -------------------------
        # TEXT SIGNALS
        # -------------------------
        warnings = (
            analyze_text_signals(
                news_text
            )
        )


        # -------------------------
        # TRUST SCORE
        # -------------------------
        trust_score = (
            calculate_trust_score(

                confidence,

                prediction,

                clickbait_words,

                warnings

            )
        )


        # -------------------------
        # FINAL LABEL
        # -------------------------
        final_label = (
            get_final_label(

                prediction,

                confidence,

                trust_score

            )
        )


        # -------------------------
        # EXPLANATION
        # -------------------------
        explanation = (
            generate_explanation(

                prediction,

                clickbait_words,

                warnings,

                confidence

            )
        )


        # -------------------------
        # RESPONSE
        # -------------------------
        return jsonify({

            "success": True,

            "input": news_text,

            "prediction": final_label,

            "raw_prediction": (
                "Fake"
                if prediction == 0
                else "Real"
            ),

            "confidence": confidence,

            "trust_score": trust_score,

            "clickbait_words": (
                clickbait_words
            ),

            "warning_signals": (
                warnings
            ),

            "explanation": (
                explanation
            ),

            "disclaimer": (
                "This is an AI-assisted "
                "assessment, not definitive proof. "
                "Verify important claims using "
                "reliable sources."
            )

        })


    except Exception as error:

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# --------------------------------
# RUN SERVER
# --------------------------------
if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )