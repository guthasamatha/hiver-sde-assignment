# Failure Analysis

The following failure modes were identified by reviewing errors from the
intent classifier, retrieval system, escalation policy, and generated replies.

## 1. Lexical Ambiguity in Historical Retrieval

Example:
Customer message: "I was charged twice for Spotify Premium."

Expected meaning:
The customer is reporting a duplicate billing charge.

Observed retrieval behavior:
The retrieval system returned historical conversations mentioning the
music group "TWICE" because the word "twice" had high lexical similarity.

Hypothesis:
TF-IDF retrieval primarily relies on overlapping words and does not fully
understand semantic meaning or context.

Impact:
Irrelevant historical evidence can reduce the groundedness and usefulness
of the generated reply.

Possible improvement:
Use semantic embeddings or hybrid retrieval with intent filtering before
retrieving historical support conversations.


## 2. Overlapping Intent Categories

Example:
Messages about adding music, supporting a device, or changing Spotify
behavior were sometimes confused between FEATURE_REQUEST,
CONTENT_AVAILABILITY, and PLAYBACK_TECHNICAL.

Observed examples included content-release requests being predicted as
FEATURE_REQUEST and playback/device problems being predicted as other
categories.

Hypothesis:
Several support intents share similar vocabulary, while the labelled
dataset is relatively small.

Impact:
Incorrect intent prediction can cause the downstream agent to choose an
inappropriate response template.

Possible improvement:
Collect more labelled examples and add hierarchical or context-aware
intent classification.


## 3. Poor Performance on Minority Intents

Example:
DOWNLOAD_OFFLINE had only 12 examples in the 200-example golden set.

In the held-out TF-IDF + Logistic Regression evaluation,
DOWNLOAD_OFFLINE received zero precision and zero recall on its
three test examples.

Hypothesis:
The classifier does not have enough diverse training examples for some
minority classes.

Impact:
Less common support issues may be routed incorrectly even when overall
accuracy appears reasonable.

Possible improvement:
Expand and balance the labelled dataset, use stratified cross-validation,
and investigate stronger pretrained text representations.


## 4. Escalation Policy Misses Risky Cases

The escalation evaluation produced approximately 69% overall accuracy,
but recall for the ESCALATE class was only about 8%.

Hypothesis:
The current escalation policy relies heavily on a limited set of explicit
risk phrases. Many account-specific problems do not contain those exact
phrases.

Impact:
A customer issue requiring human investigation may incorrectly be marked
AUTO_HANDLE. This is more important than the headline accuracy suggests
because false auto-handling can be risky for billing, account-access, and
security problems.

Possible improvement:
Use a conservative confidence-aware escalation policy and expand
account-specific and risk signals. Low-confidence cases should default
to human review.


## 5. Generic Replies Can Be Safe but Not Helpful Enough

Manual review showed that generated replies were generally stylistically
clean and often safe, but helpfulness was weaker.

For example, a customer may already have attempted troubleshooting,
while the generated response gives another generic troubleshooting
instruction instead of acknowledging the steps already attempted.

Hypothesis:
The current reply generator relies substantially on intent/action
templates and does not yet deeply synthesize the retrieved historical
resolution.

Impact:
Replies can sound professional while failing to resolve the customer's
specific problem.

Possible improvement:
Condition generation on higher-quality retrieved evidence, the customer's
previous troubleshooting context, predicted intent, and escalation
decision. Add a grounding check before allowing automatic handling.


# What Is Misleading About My Headline Number?

A headline metric can make this system appear stronger than it actually is.

For example, the escalation component achieves approximately 69% overall
accuracy. However, this number is misleading because the golden set is
imbalanced: 134 of the 200 examples are AUTO_HANDLE, while only 66 are
ESCALATE.

The system correctly identifies many AUTO_HANDLE examples, but recall for
the ESCALATE class is only about 8%. Therefore, a system that appears to
achieve 69% accuracy can still miss many cases that actually require human
support.

This is particularly important for billing, account-access, and security
issues, where incorrectly auto-handling a request can have a larger cost
than unnecessarily escalating one.

Intent accuracy also requires caution. The keyword baseline achieves 48%
accuracy on the 200-example golden set, while the TF-IDF + Logistic
Regression experiment achieves 48% accuracy and approximately 0.43
macro-F1 on its held-out test split. These results come from different
evaluation setups and should not be treated as directly interchangeable.

The evaluation set is also relatively small, and the intent taxonomy and
golden examples were developed from the same initial Spotify sample.
Therefore, the reported results should be treated as evidence from a
prototype evaluation rather than an estimate of production performance.

For deployment, I would prioritize per-class recall, especially ESCALATE
recall, macro-F1, reply groundedness, and human-review results rather than
relying on overall accuracy alone.

# One-More-Week Improvement Plan

If I had one additional week to improve this system, I would focus on
reliability and evaluation rather than adding unnecessary features.

## Day 1 - Improve the Golden Dataset

- Review ambiguous intent labels.
- Add more examples for minority intents such as DOWNLOAD_OFFLINE.
- Create a separate untouched test set.
- Improve class balance where possible.

## Day 2 - Improve Intent Classification

- Compare the keyword baseline and TF-IDF + Logistic Regression model
  using the same evaluation split.
- Use stratified cross-validation.
- Investigate pretrained sentence embeddings for better semantic
  understanding.
- Analyze confusion between FEATURE_REQUEST, CONTENT_AVAILABILITY,
  and PLAYBACK_TECHNICAL.

## Day 3 - Improve Historical Retrieval

- Replace or augment lexical TF-IDF retrieval with semantic embeddings.
- Filter historical examples using the predicted intent before retrieval.
- Test retrieval quality manually on difficult examples.
- Specifically address lexical ambiguity such as "twice" versus the
  artist "TWICE".

## Day 4 - Improve Reply Grounding

- Generate replies using the actual retrieved historical resolutions
  rather than relying mainly on generic intent templates.
- Require the generated response to stay consistent with retrieved
  evidence.
- Add a grounding check before allowing AUTO_HANDLE.

## Day 5 - Improve Escalation Safety

- Expand signals for billing, account-access, and security cases.
- Add confidence-based escalation.
- Default uncertain or sensitive cases to human review.
- Optimize for ESCALATE recall rather than overall accuracy alone.

## Day 6 - Strengthen Evaluation

- Expand manual reply evaluation beyond 30 examples.
- Complete LLM-as-a-Judge evaluation.
- Measure agreement between manual and LLM ratings.
- Evaluate relevance, groundedness, helpfulness, style, and safety.

## Day 7 - Production Readiness

- Add automated tests for major components.
- Improve error handling and logging.
- Finalize reproducible setup instructions.
- Run the complete repository from a clean environment.
- Document remaining limitations and deployment risks.