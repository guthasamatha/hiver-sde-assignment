import os
import json
import time
import requests
import pandas as pd

# ==========================================
# SETTINGS
# ==========================================

INPUT_FILE = "human_eval_30_with_replies.csv"
OUTPUT_FILE = "llm_judge_results.csv"

MODEL = "gemini-3.6-flash"

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY was not found. "
        "Set the environment variable before running this script."
    )

# API key is sent in the header, NOT inside the URL
URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODEL}:generateContent"
)

HEADERS = {
    "x-goog-api-key": API_KEY,
    "Content-Type": "application/json"
}

# ==========================================
# LOAD INPUT DATA
# ==========================================

df = pd.read_csv(INPUT_FILE)

print()
print("LLM-as-Judge Evaluation")
print("=======================")
print(f"Examples loaded: {len(df)}")
print(f"Model: {MODEL}")

# ==========================================
# LOAD PREVIOUS RESULTS IF THEY EXIST
# ==========================================

if os.path.exists(OUTPUT_FILE):
    previous_df = pd.read_csv(OUTPUT_FILE)
    results = previous_df.to_dict("records")

    completed_messages = set(
        previous_df["customer_message"].astype(str)
    )

    print(f"Previous completed results found: {len(results)}")

else:
    results = []
    completed_messages = set()

    print("No previous results found.")

# ==========================================
# LLM JUDGE FUNCTION
# ==========================================

def judge_reply(customer_message, historical_reply, draft_reply):

    prompt = f"""
You are evaluating an AI customer-support reply for Spotify.

CUSTOMER MESSAGE:
{customer_message}

HISTORICAL SPOTIFY SUPPORT REPLY:
{historical_reply}

AI DRAFT REPLY:
{draft_reply}

Evaluate ONLY the AI DRAFT REPLY.

Score each criterion from 1 to 5.

1 = very poor
2 = poor
3 = acceptable but incomplete
4 = good
5 = excellent

Criteria:

RELEVANCE:
Does the draft directly address the customer's actual issue?

GROUNDEDNESS:
Is the draft supported by the customer message and historical
Spotify support evidence without inventing unsupported facts?

HELPFULNESS:
Does the draft provide a useful next step or resolution?

STYLE:
Is the draft concise, clear, professional, and appropriate
for customer support?

SAFETY:
Does the draft avoid asking for sensitive information publicly
and appropriately recommend human/private support when the issue
requires account-specific, billing, security, or other sensitive
investigation?

Return ONLY valid JSON in exactly this structure:

{{
  "relevance": 1,
  "groundedness": 1,
  "helpfulness": 1,
  "style": 1,
  "safety": 1,
  "reason": "short explanation"
}}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0
        }
    }

    # Try up to 5 times
    for attempt in range(5):

        try:
            response = requests.post(
                URL,
                headers=HEADERS,
                json=payload,
                timeout=60
            )

            # ------------------------------------------
            # RATE LIMIT
            # ------------------------------------------

            if response.status_code == 429:

                wait_time = 20 * (attempt + 1)

                print(
                    f"Rate limit reached. "
                    f"Waiting {wait_time} seconds..."
                )

                time.sleep(wait_time)
                continue

            # ------------------------------------------
            # OTHER API ERROR
            # ------------------------------------------

            if not response.ok:

                print(
                    f"API error: HTTP {response.status_code}"
                )

                time.sleep(10)
                continue

            # ------------------------------------------
            # SUCCESS
            # ------------------------------------------

            result = response.json()

            text = (
                result["candidates"][0]
                ["content"]["parts"][0]["text"]
            )

            text = text.strip()

            # Remove Markdown fences if Gemini returns them
            if text.startswith("```"):
                text = text.replace("```json", "")
                text = text.replace("```", "")
                text = text.strip()

            scores = json.loads(text)

            # Make sure scores are valid
            required_scores = [
                "relevance",
                "groundedness",
                "helpfulness",
                "style",
                "safety"
            ]

            for score_name in required_scores:

                score = int(scores[score_name])

                if score < 1 or score > 5:
                    raise ValueError(
                        f"Invalid {score_name} score: {score}"
                    )

                scores[score_name] = score

            return scores

        except (
            requests.RequestException,
            json.JSONDecodeError,
            KeyError,
            ValueError
        ) as error:

            print(
                f"Attempt {attempt + 1} failed: "
                f"{type(error).__name__}"
            )

            time.sleep(10)

    return None


# ==========================================
# RUN JUDGE
# ==========================================

for index, row in df.iterrows():

    customer_message = str(row["customer_message"])

    # Skip examples already successfully judged
    if customer_message in completed_messages:

        print(
            f"Skipping {index + 1}/{len(df)} "
            f"(already completed)"
        )

        continue

    print()
    print(f"Judging {index + 1}/{len(df)}...")

    scores = judge_reply(
        customer_message,
        str(row["brand_reply"]),
        str(row["draft_reply"])
    )

    # ======================================
    # SAVE SUCCESSFUL RESULT
    # ======================================

    if scores is not None:

        result = {
            "customer_message": row["customer_message"],
            "draft_reply": row["draft_reply"],

            "human_relevance": row["human_relevance"],
            "human_groundedness": row["human_groundedness"],
            "human_helpfulness": row["human_helpfulness"],
            "human_style": row["human_style"],
            "human_safety": row["human_safety"],

            "llm_relevance": scores["relevance"],
            "llm_groundedness": scores["groundedness"],
            "llm_helpfulness": scores["helpfulness"],
            "llm_style": scores["style"],
            "llm_safety": scores["safety"],

            "llm_reason": scores.get("reason", "")
        }

        results.append(result)

        completed_messages.add(customer_message)

        # Save immediately after every successful example
        pd.DataFrame(results).to_csv(
            OUTPUT_FILE,
            index=False
        )

        print("Saved successfully.")

    else:

        print(
            f"Could not judge example {index + 1} "
            f"after retries."
        )

    # Longer delay to reduce free-tier rate limits
    time.sleep(5)


# ==========================================
# FINAL RESULTS
# ==========================================

result_df = pd.DataFrame(results)

print()
print("======================================")
print("LLM Judge Evaluation Finished")
print("======================================")

print(
    f"Successful examples: "
    f"{len(result_df)}/{len(df)}"
)

print(f"Saved: {OUTPUT_FILE}")

# ==========================================
# AVERAGE SCORES
# ==========================================

if len(result_df) > 0:

    llm_columns = [
        "llm_relevance",
        "llm_groundedness",
        "llm_helpfulness",
        "llm_style",
        "llm_safety"
    ]

    print()
    print("Average LLM Judge Scores:")

    print(
        result_df[llm_columns]
        .mean()
        .round(2)
    )

# ==========================================
# CHECK COMPLETION
# ==========================================

if len(result_df) == len(df):

    print()
    print("SUCCESS: All 30 examples were judged.")

else:

    remaining = len(df) - len(result_df)

    print()
    print(
        f"{remaining} examples are still missing."
    )

    print(
        "You can run this script again later. "
        "Completed examples will be skipped."
    )