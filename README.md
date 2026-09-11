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

## System Flow

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
- **ESCALATE recall: approximately 8%**

Although overall accuracy appears reasonable, the very low recall for
ESCALATE is an important weakness and makes unrestricted automatic
handling inappropriate for the current prototype.

## Reply Generation

After predicting the intent and escalation action, the system generates a
draft customer-support response.

The current prototype uses controlled intent/action-based response
templates. This approach was chosen to keep responses predictable and to
reduce unsupported claims.

For sensitive or account-specific issues, the reply directs the customer
toward private or human support rather than requesting sensitive
information publicly.

Example:

Customer message:

> "I was charged twice for Spotify Premium."

System output:

- **Intent:** `BILLING_SUBSCRIPTION`
- **Action:** `ESCALATE`
- **Reason:** Possible duplicate billing charge requiring account-specific investigation.

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

## Reply Quality Evaluation

Generated support replies are evaluated on five dimensions using a
1-to-5 rubric:

1. **Relevance** - Does the reply address the customer's issue?
2. **Groundedness** - Is the reply supported by the available context and
   historical support information?
3. **Helpfulness** - Does the reply provide a useful resolution or next step?
4. **Style** - Is the response clear, concise, and professional?
5. **Safety** - Does the reply handle sensitive/account-specific issues
   appropriately?

## Manual Review

A 30-example subset was reviewed using the fixed five-dimension rubric.

Current average manual scores:

| Dimension | Average / 5 |
|---|---:|
| Relevance | 3.17 |
| Groundedness | 3.07 |
| Helpfulness | 2.50 |
| Style | 4.97 |
| Safety | 4.20 |

The manual review indicates that the prototype generally produces clean
and safe responses, while helpfulness and grounding remain areas for
improvement.

## LLM-as-a-Judge

Gemini is used as an automated reply-quality judge using the same five
dimensions.

The LLM judge receives the customer message, historical Spotify support
reply, and generated draft reply. It returns a 1-to-5 score for each
dimension together with a short explanation.

The LLM scores are compared with the manual ratings using:

- Exact score agreement
- Agreement within +/- 1 point
- Mean Absolute Error (MAE)
- Spearman rank correlation

The LLM evaluation is designed as an additional evaluation signal rather
than a replacement for manual review.

### Interim Judge Agreement

At the time of the current evaluation, 19 of the 30 examples have
successfully completed LLM judging because of API free-tier rate limits.

Interim agreement on those 19 examples:

- **Exact agreement:** 26.3%
- **Within +/- 1 agreement:** 61.1%
- **Mean Absolute Error:** 1.27
- **Spearman correlation:** 0.42

These are interim results and should be replaced with the final 30-example
results once all LLM evaluations are complete.

## What Is Misleading About My Headline Number?

The headline metrics can make the prototype appear stronger than it
actually is.

For example, the escalation component achieves approximately **69%
overall accuracy**. However, the golden set contains 134 AUTO_HANDLE
examples and only 66 ESCALATE examples.

More importantly, recall for the ESCALATE class is only approximately
**8%**.

Therefore, the 69% accuracy hides a serious weakness: many requests that
should be sent to a human agent are incorrectly classified as
AUTO_HANDLE.

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

For these reasons, the reported numbers should be treated as prototype
evaluation results rather than estimates of production performance.

## Top Failure Modes

Five important failure modes were identified:

1. **Lexical ambiguity in retrieval**  
   TF-IDF can confuse words with different meanings. For example,
   "charged twice" can retrieve conversations about the artist TWICE.

2. **Overlapping intent categories**  
   FEATURE_REQUEST, CONTENT_AVAILABILITY, and PLAYBACK_TECHNICAL can
   contain similar language and are sometimes confused.

3. **Limited minority-class data**  
   Intents such as DOWNLOAD_OFFLINE have relatively few labelled
   examples, resulting in weak held-out performance.

4. **Low ESCALATE recall**  
   The rule-based escalation policy misses many cases that should receive
   human review.

5. **Safe but generic replies**  
   Template-based responses are often stylistically clean but may not
   fully address the customer's specific context or previous
   troubleshooting attempts.

More detailed examples and hypotheses are documented in
`failure_analysis.md`.

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
6. Improve ESCALATE recall using confidence-aware and conservative
   routing.
7. Expand human and LLM evaluation and test the complete repository from
   a clean environment.

The goal would be to improve reliability and evaluation quality before
adding additional product features.

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
git clone <REPOSITORY_URL>
cd hiver-sde-assignment