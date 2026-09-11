# Decision Log

This log records the main design decisions made while building the
Spotify AI Customer Support Agent.

| # | Decision | Reason |
|---|---|---|
| 1 | Selected Spotify (`SpotifyCares`) as the target brand | Spotify had a large number of support conversations and diverse customer issues in the dataset. |
| 2 | Subsampled the full dataset instead of manually analysing all ~2.8M tweets | A smaller reproducible sample made development and manual evaluation practical while retaining real support examples. |
| 3 | Extracted direct customer-to-Spotify response pairs | These pairs provide historical examples of customer problems and actual brand responses. |
| 4 | Created a 200-example golden evaluation set | 200 examples provided a manageable hand-reviewed evaluation set within the assignment time constraint. |
| 5 | Used seven intent categories | The categories captured the major recurring Spotify support problems without creating an unnecessarily complex taxonomy. |
| 6 | Kept `OTHER` as an intent | Some tweets do not contain a clear support issue or do not fit the main categories. |
| 7 | Used a majority-class classifier as the trivial baseline | It establishes a minimum reference point that a useful intent classifier should outperform. |
| 8 | Used keyword rules as the simple baseline | Keyword classification is fast, interpretable, and provides a stronger comparison than the majority baseline. |
| 9 | Tested TF-IDF + Logistic Regression as the ML classifier | It is lightweight, reproducible, fast to train, and appropriate for a relatively small labelled text dataset. |
| 10 | Used hybrid word + character TF-IDF for historical retrieval | Word features capture support terminology while character features can provide robustness to spelling variations and short social-media text. |
| 11 | Separated intent prediction from escalation | The same intent can require different handling depending on whether the issue is generic or account-specific/sensitive. |
| 12 | Used conservative escalation rules for sensitive cases | Billing, account-access, security, refund, and similar issues may require private account investigation rather than automatic handling. |
| 13 | Used template-based reply generation for the initial prototype | Templates provide predictable and safe replies while reducing unsupported claims; however, they limit personalization and grounding. |
| 14 | Evaluated replies using five dimensions | Relevance, groundedness, helpfulness, style, and safety capture different aspects of support-reply quality that a single accuracy metric cannot measure. |
| 15 | Added manual review plus an LLM-as-a-Judge | Manual review provides a human reference, while the LLM judge provides a scalable automated evaluation whose agreement with manual ratings can be measured. |

## Notes

The system is intentionally designed as an evaluation-focused prototype
rather than a production-ready autonomous customer-support bot.

Several decisions favor simplicity, reproducibility, and inspectability.
The failure analysis documents where these choices break down and what
would be improved with additional development time.