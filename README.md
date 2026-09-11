# AI Customer Support Agent for Spotify

## Hiver SDE Intern Take-Home Assignment

This project builds an AI-assisted customer support agent using historical
Spotify support conversations from the Customer Support on Twitter dataset.

Given an incoming customer message, the system performs three main tasks:

1. **Intent Classification** – predicts the type of customer support issue.
2. **Reply Generation** – drafts a safe customer support response using the
   predicted intent and historical support information.
3. **Escalation Decision** – determines whether the request can be
   `AUTO_HANDLE` or should be `ESCALATE` to a human agent, with a reason.

The project focuses not only on building the agent but also on evaluating
its limitations using a hand-reviewed golden set, automated metrics,
manual reply evaluation, and an LLM-as-a-Judge.

---

## System Flow

```text
Customer Message
      ↓
Intent Classification
      ↓
Historical Resolution Retrieval
      ↓
Draft Reply Generation
      ↓
AUTO_HANDLE / ESCALATE
      ↓
Reason for Decision
```

---

## Dataset

The project uses the **Customer Support on Twitter** dataset originally
published on Kaggle.

The full dataset contains approximately **2.8 million tweets** with fields
such as:

- `tweet_id`
- `author_id`
- `inbound`
- `created_at`
- `text`
- `response_tweet_id`
- `in_response_to_tweet_id`

For this project, **Spotify (`SpotifyCares`)** was selected as the target
brand.

Direct customer-to-Spotify support interactions were extracted from the
dataset, producing **43,092 customer-message / brand-reply pairs**.

A reproducible sample of 300 Spotify interactions was then created for
analysis and intent discovery.

The full raw `twcs.csv` dataset is intentionally excluded from the Git
repository because of its size. The extracted Spotify interaction data
required by the prototype is included.

---

## Intent Taxonomy

Seven support intents were defined after reviewing the Spotify support
sample:

| Intent | Description |
|---|---|
| `ACCOUNT_ACCESS` | Login, password, account access, and security problems |
| `BILLING_SUBSCRIPTION` | Premium, payments, charges, refunds, trials, cancellation, family/student plans |
| `PLAYBACK_TECHNICAL` | Playback failures, app problems, crashes, loading, shuffle/repeat, and technical bugs |
| `DOWNLOAD_OFFLINE` | Downloading music, offline listening, missing downloads, and download limits |
| `CONTENT_AVAILABILITY` | Missing songs, albums, artists, regional availability, and licensing-related issues |
| `FEATURE_REQUEST` | Requests for new features, changes, integrations, or device/platform support |
| `OTHER` | Messages without a clear support issue or that do not fit the other categories |

---

## Golden Evaluation Set

A **200-example golden evaluation set** was sampled from the Spotify data.

Each example was reviewed using a predefined labeling rubric and contains:

- Customer message
- Historical Spotify reply
- Intent label
- Expected action (`AUTO_HANDLE` or `ESCALATE`)
- Label notes

The final intent distribution is:

| Intent | Examples |
|---|---:|
| PLAYBACK_TECHNICAL | 47 |
| BILLING_SUBSCRIPTION | 39 |
| FEATURE_REQUEST | 36 |
| OTHER | 30 |
| CONTENT_AVAILABILITY | 21 |
| ACCOUNT_ACCESS | 15 |
| DOWNLOAD_OFFLINE | 12 |
| **Total** | **200** |

The expected action distribution is:

- **AUTO_HANDLE:** 134
- **ESCALATE:** 66

`AUTO_HANDLE` is used when a request can reasonably be answered using
standard support information.

`ESCALATE` is used when the issue requires account-specific investigation,
contains billing/refund/security risk, or otherwise requires human support.

### Sampling and Labeling Note

The golden examples were sampled reproducibly from the Spotify support
sample and reviewed using a fixed intent and escalation rubric.

The taxonomy and evaluation examples were derived from the same initial
Spotify sample. This creates a potential evaluation-design limitation and
is explicitly considered when interpreting the reported results.

---

## Intent Classification

The project compares multiple approaches instead of reporting only one
model.

### Baseline 1 - Majority Class

The trivial baseline predicts the most frequent intent,
`PLAYBACK_TECHNICAL`, for every customer message.

**Accuracy: 23.5%**

This establishes a minimum reference point for intent classification.

### Baseline 2 - Keyword Rules

A simple rule-based classifier uses support-related keywords such as
login, password, Premium, payment, download, offline, feature, and
playback terms.

**Accuracy on the 200-example golden set: 48.0%**

This baseline is simple and interpretable but struggles with ambiguous
language and overlapping intents.

### TF-IDF + Logistic Regression

A lightweight machine-learning classifier was also evaluated.

Configuration:

- TF-IDF word features
- Unigrams and bigrams
- Maximum 5,000 features
- Logistic Regression
- Balanced class weights
- 75/25 stratified train/test split
- 150 training examples
- 50 held-out test examples

Held-out results:

- **Accuracy: 48.0%**
- **Macro-F1: 0.43**

Per-class results:

| Intent | Precision | Recall | F1 |
|---|---:|---:|---:|
| ACCOUNT_ACCESS | 1.00 | 0.50 | 0.67 |
| BILLING_SUBSCRIPTION | 0.53 | 0.90 | 0.67 |
| CONTENT_AVAILABILITY | 0.50 | 0.40 | 0.44 |
| DOWNLOAD_OFFLINE | 0.00 | 0.00 | 0.00 |
| FEATURE_REQUEST | 0.33 | 0.44 | 0.38 |
| OTHER | 0.44 | 0.57 | 0.50 |
| PLAYBACK_TECHNICAL | 0.50 | 0.25 | 0.33 |

The keyword baseline and Logistic Regression results come from different
evaluation setups and therefore should not be interpreted as a direct
like-for-like model comparison.

The runnable end-to-end demo currently uses the lightweight keyword
classifier. The Logistic Regression model is retained as a separate
evaluated experiment.

---

## Historical Resolution Retrieval

Historical Spotify support conversations are retrieved using a hybrid
TF-IDF approach.

The retriever combines:

- Word TF-IDF features using unigrams and bigrams
- Character TF-IDF features using character n-grams
- Cosine similarity
- A weighted combination of word and character similarity

The purpose of retrieval is to provide relevant historical support
examples that can help ground the support response.

Retrieval is not perfect. For example, the query:

> "I was charged twice for Spotify Premium."

can retrieve conversations about the artist **TWICE** because lexical
similarity does not fully understand the meaning of the word "twice".

This is retained as a documented failure case rather than hidden through
test-specific tuning.

---

## Escalation Decision

The system predicts one of two actions:

- `AUTO_HANDLE`
- `ESCALATE`

The escalation policy considers the predicted intent together with risk
signals in the customer message.

Examples that may require escalation include:

- Account compromise or access problems
- Duplicate or unauthorized charges
- Refund requests
- Account-specific billing problems
- Explicit requests for human assistance

On the 200-example golden set:

- **Escalation accuracy: 69%**
- **Escalation Macro-F1: 0.475**
- **ESCALATE recall: approximately 8%**

Although overall accuracy appears reasonable, the very low recall for
`ESCALATE` is an important weakness and makes unrestricted automatic
handling inappropriate for the current prototype.

---

## Reply Generation

After predicting the intent and escalation action, the system generates a
draft customer-support response.

The current prototype uses controlled intent/action-based response
templates. This approach was chosen to keep responses predictable and to
reduce unsupported claims.

For sensitive or account-specific issues, the reply directs the customer
toward private or human support rather than requesting sensitive
information publicly.

Example customer message:

> "I was charged twice for Spotify Premium."

System output:

- **Intent:** `BILLING_SUBSCRIPTION`
- **Action:** `ESCALATE`
- **Reason:** Billing or refund issue may require access to account-specific payment information.

Example draft reply:

> Sorry about the billing issue. We'd like to look into your account and
> payment details. Please contact support through a private channel so the
> team can investigate the charge securely.

### Grounding Limitation

Although historical conversations are retrieved, the current reply
generator relies substantially on controlled templates rather than deeply
synthesizing the retrieved historical resolution.

Therefore, this prototype should not be described as a fully grounded
retrieval-augmented generation system. Improving evidence-conditioned
generation is a major next step.

---

## Automated End-to-End Evaluation

The end-to-end evaluation harness was run on all **200 golden examples**.

### Intent Results

- **Accuracy: 48.0%**
- **Macro-F1: 0.493**

### Escalation Results

- **Accuracy: 69.0%**
- **Macro-F1: 0.475**
- **AUTO_HANDLE recall: 99%**
- **ESCALATE recall: 8%**

These results show why accuracy alone is not sufficient for evaluating
the escalation component.

---

## Reply Quality Evaluation

Generated support replies are evaluated on five dimensions using a
1-to-5 rubric:

1. **Relevance** – Does the reply address the customer's issue?
2. **Groundedness** – Is the reply supported by the available context and
   historical support information?
3. **Helpfulness** – Does the reply provide a useful resolution or next step?
4. **Style** – Is the response clear, concise, and professional?
5. **Safety** – Does the reply handle sensitive/account-specific issues
   appropriately?

---

## Manual Review

A 30-example subset was reviewed using the fixed five-dimension rubric.

Average manual scores:

| Dimension | Average / 5 |
|---|---:|
| Relevance | 3.17 |
| Groundedness | 3.07 |
| Helpfulness | 2.50 |
| Style | 4.97 |
| Safety | 4.20 |

The manual review suggests that the prototype is generally safe and
stylistically consistent, while helpfulness and evidence grounding remain
important areas for improvement.

---

## LLM-as-a-Judge

Gemini is used as an automated reply-quality judge using the same five
dimensions.

The LLM judge receives:

- Customer message
- Historical Spotify support reply
- Generated draft reply

It returns a 1-to-5 score for each evaluation dimension together with a
short explanation.

All **30/30 examples** were successfully evaluated by the LLM judge.

### Final LLM Judge Scores

| Dimension | Average / 5 |
|---|---:|
| Relevance | 1.73 |
| Groundedness | 3.23 |
| Helpfulness | 1.70 |
| Style | 2.87 |
| Safety | 4.80 |

The relatively high safety score and lower relevance/helpfulness scores
are consistent with a system that tends to produce conservative but
generic template responses.

### Human vs LLM Judge Agreement

The LLM scores were compared with the manual ratings using exact
agreement, agreement within one point, Mean Absolute Error, and Spearman
rank correlation.

| Metric | Exact Agreement | Within +/- 1 | MAE | Spearman |
|---|---:|---:|---:|---:|
| Relevance | 13.3% | 43.3% | 1.500 | 0.612 |
| Groundedness | 13.3% | 56.7% | 1.367 | 0.285 |
| Helpfulness | 26.7% | 80.0% | 0.933 | 0.478 |
| Style | 13.3% | 43.3% | 2.100 | 0.243 |
| Safety | 60.0% | 76.7% | 0.667 | 0.416 |

Overall agreement:

- **Exact agreement: 25.3%**
- **Within +/- 1 agreement: 60.0%**
- **Mean Absolute Error: 1.31**
- **Spearman correlation: 0.43**

The overall Spearman correlation indicates moderate rank association,
but exact agreement is low. Therefore, the LLM judge is treated as an
additional evaluation signal rather than a replacement for manual review.

---

## What Is Misleading About My Headline Number?

The headline metrics can make the prototype appear stronger than it
actually is.

For example, the escalation component achieves approximately **69%
overall accuracy**. However, the golden set contains 134 `AUTO_HANDLE`
examples and only 66 `ESCALATE` examples.

More importantly, recall for the `ESCALATE` class is only approximately
**8%**.

Therefore, the 69% accuracy hides a serious weakness: many requests that
should be sent to a human agent are incorrectly classified as
`AUTO_HANDLE`.

This matters especially for billing, account-access, refund, and security
issues, where incorrectly auto-handling a request can be more costly than
unnecessarily escalating one.

The intent results also require careful interpretation. The keyword
classifier achieves 48% accuracy on the complete 200-example golden set,
while TF-IDF + Logistic Regression achieves 48% accuracy and 0.43
macro-F1 on a 50-example held-out test split. These results come from
different evaluation setups and are not a direct like-for-like comparison.

The evaluation dataset is also small. In addition, the intent taxonomy
and golden examples were developed from the same initial Spotify sample,
which introduces a potential evaluation-design limitation.

The LLM-as-a-Judge results also require caution. Exact agreement with the
manual ratings is only 25.3%, so the LLM scores should not be interpreted
as objective ground truth.

For these reasons, the reported numbers should be treated as prototype
evaluation results rather than estimates of production performance.

---

## Top 5 Failure Modes

### 1. Lexical Ambiguity in Retrieval

TF-IDF can confuse words with different meanings.

Example:

> "I was charged twice for Spotify Premium."

The retriever can return conversations about the artist **TWICE** rather
than duplicate billing.

**Hypothesis:** lexical similarity captures shared words but not enough
semantic context.

### 2. Overlapping Intent Categories

`FEATURE_REQUEST`, `CONTENT_AVAILABILITY`, and `PLAYBACK_TECHNICAL` can
contain similar language and are sometimes confused.

**Hypothesis:** the small labelled dataset does not contain enough examples
to learn clear boundaries between related support intents.

### 3. Limited Minority-Class Data

Intents such as `DOWNLOAD_OFFLINE` have relatively few labelled examples.

In the held-out Logistic Regression evaluation, `DOWNLOAD_OFFLINE`
received an F1 score of 0.00.

**Hypothesis:** sparse examples make minority-class patterns difficult to
learn reliably.

### 4. Low ESCALATE Recall

The rule-based escalation policy achieves only approximately **8% recall**
for the `ESCALATE` class.

**Hypothesis:** the current escalation rules cover only a limited set of
explicit risk phrases and miss less obvious account-specific cases.

### 5. Safe but Generic Replies

Template-based responses are often safe and predictable but may not fully
address the customer's specific context or previous troubleshooting
attempts.

This is also reflected in the LLM judge's relatively high safety score
(**4.80/5**) and low helpfulness score (**1.70/5**).

**Hypothesis:** the reply generator does not yet deeply condition its
response on retrieved historical resolutions.

More detailed failure analysis is available in:

`data/failure_analysis.md`

---

## One-More-Week Plan

With one additional week, the priorities would be:

1. Expand and independently review the labelled evaluation dataset.
2. Create a completely untouched test set and use stratified
   cross-validation during model development.
3. Improve intent classification using stronger semantic text
   representations.
4. Add intent-aware semantic retrieval to reduce lexical retrieval errors.
5. Make reply generation genuinely evidence-conditioned on retrieved
   historical resolutions.
6. Improve `ESCALATE` recall using confidence-aware and conservative
   routing.
7. Expand human and LLM evaluation and test the complete repository from
   a clean environment.

The goal would be to improve reliability and evaluation quality before
adding additional product features.

---

## Decision Log

A 15-entry decision log documents the major implementation and evaluation
choices made during the project, including:

- Spotify brand selection
- Dataset subsampling
- Golden-set construction
- Intent taxonomy design
- Baseline selection
- TF-IDF + Logistic Regression experiment
- Hybrid historical-reply retrieval
- Escalation rules
- Controlled reply templates
- Evaluation methodology

See:

`data/decision_log.md`

---

## Repository Structure

```text
hiver-sde-assignment/
│
├── README.md
├── requirements.txt
├── .gitignore
│
└── data/
    ├── analyze_data.py
    ├── baseline_intent.py
    ├── intent_classifier.py
    ├── reply_retrieval.py
    ├── escalation.py
    ├── reply_generator.py
    ├── support_agent.py
    ├── evaluate_agent.py
    ├── reply_judge.py
    ├── compare_judges.py
    ├── golden_set.csv
    ├── spotify_pairs.csv
    ├── spotify_sample_300.csv
    ├── human_eval_30_with_replies.csv
    ├── llm_judge_results.csv
    ├── judge_agreement_summary.csv
    ├── failure_analysis.md
    └── decision_log.md
```

The original `twcs.csv` dataset is not committed because of its large file
size.

---

## How to Run

### Requirements

- Python 3.10+
- pandas
- scikit-learn
- requests

The main evaluation pipeline is designed to run on a normal laptop without
requiring GPU training.

### 1. Clone the Repository

```bash
git clone https://github.com/guthasamatha/hiver-sde-assignment.git
cd hiver-sde-assignment
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Move to the Data Directory

```bash
cd data
```

### 4. Run the End-to-End Support Agent

```bash
python support_agent.py
```

This demonstrates:

- Intent prediction
- Historical reply retrieval
- Escalation decision
- Draft reply generation
- Escalation reason

### 5. Run Intent Baselines

```bash
python baseline_intent.py
```

### 6. Run the TF-IDF + Logistic Regression Experiment

```bash
python intent_classifier.py
```

### 7. Run the Automated Evaluation Harness

```bash
python evaluate_agent.py
```

This evaluates intent classification and escalation decisions against the
200-example golden set.

### 8. Run Human-vs-LLM Judge Agreement

The repository already contains the completed LLM judge results, so the
agreement calculation can be reproduced without an API key:

```bash
python compare_judges.py
```

### 9. Optional: Re-run Gemini LLM-as-a-Judge

To generate fresh LLM judge scores, set a Gemini API key in the
`GEMINI_API_KEY` environment variable and run:

```bash
python reply_judge.py
```

The LLM judge is optional for reproducing the stored headline results
because the completed judge output is included in the repository.

---

## Key Results Summary

| Component | Result |
|---|---:|
| Majority intent baseline | 23.5% accuracy |
| Keyword intent baseline | 48.0% accuracy |
| TF-IDF + Logistic Regression | 48.0% accuracy, 0.43 Macro-F1 |
| End-to-end intent evaluation | 48.0% accuracy, 0.493 Macro-F1 |
| Escalation | 69.0% accuracy, 0.475 Macro-F1 |
| ESCALATE recall | 8% |
| LLM judge completion | 30/30 |
| Human-LLM exact agreement | 25.3% |
| Human-LLM within +/- 1 | 60.0% |
| Human-LLM MAE | 1.31 |
| Human-LLM Spearman | 0.43 |

---

## Main Limitation

The current prototype is deliberately lightweight.

Its most important limitation is that historical conversations are
retrieved, but draft replies are still largely generated using controlled
intent/action templates rather than being deeply conditioned on the
retrieved resolution.

As a result, the system demonstrates the full support-agent pipeline and
evaluation framework, but it should not be interpreted as a
production-ready retrieval-augmented customer-support system.

The low `ESCALATE` recall is another important deployment blocker and
would need to be improved before allowing unrestricted automatic handling.