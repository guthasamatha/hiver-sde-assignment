import pandas as pd
from sklearn.metrics import mean_absolute_error

# ==========================================
# LOAD LLM + HUMAN RESULTS
# ==========================================

FILE = "llm_judge_results.csv"

df = pd.read_csv(FILE)

print()
print("Human vs LLM Judge Agreement")
print("============================")
print(f"Examples available: {len(df)}")

metrics = [
    "relevance",
    "groundedness",
    "helpfulness",
    "style",
    "safety"
]

summary = []

# ==========================================
# COMPARE EACH METRIC
# ==========================================

for metric in metrics:

    human_col = f"human_{metric}"
    llm_col = f"llm_{metric}"

    human = pd.to_numeric(df[human_col], errors="coerce")
    llm = pd.to_numeric(df[llm_col], errors="coerce")

    valid = human.notna() & llm.notna()

    human = human[valid]
    llm = llm[valid]

    # Exact agreement
    exact = (human == llm).mean()

    # Agreement within 1 point
    within_one = ((human - llm).abs() <= 1).mean()

    # Mean Absolute Error
    mae = mean_absolute_error(human, llm)

    # Spearman correlation
    spearman = human.corr(llm, method="spearman")

    summary.append({
        "metric": metric,
        "examples": len(human),
        "exact_agreement": round(exact, 3),
        "within_1_agreement": round(within_one, 3),
        "mae": round(mae, 3),
        "spearman": round(spearman, 3)
    })

# ==========================================
# DISPLAY RESULTS
# ==========================================

summary_df = pd.DataFrame(summary)

print()
print(summary_df.to_string(index=False))

# ==========================================
# OVERALL AGREEMENT
# ==========================================

all_human = []
all_llm = []

for metric in metrics:

    human = pd.to_numeric(
        df[f"human_{metric}"],
        errors="coerce"
    )

    llm = pd.to_numeric(
        df[f"llm_{metric}"],
        errors="coerce"
    )

    valid = human.notna() & llm.notna()

    all_human.extend(human[valid].tolist())
    all_llm.extend(llm[valid].tolist())

all_human = pd.Series(all_human)
all_llm = pd.Series(all_llm)

overall_exact = (all_human == all_llm).mean()

overall_within_one = (
    (all_human - all_llm).abs() <= 1
).mean()

overall_mae = mean_absolute_error(
    all_human,
    all_llm
)

overall_spearman = all_human.corr(
    all_llm,
    method="spearman"
)

print()
print("OVERALL AGREEMENT")
print("=================")

print(
    f"Exact agreement: "
    f"{overall_exact * 100:.1f}%"
)

print(
    f"Within-1 agreement: "
    f"{overall_within_one * 100:.1f}%"
)

print(
    f"Mean Absolute Error: "
    f"{overall_mae:.2f}"
)

print(
    f"Spearman correlation: "
    f"{overall_spearman:.2f}"
)

# ==========================================
# SAVE SUMMARY
# ==========================================

summary_df.to_csv(
    "judge_agreement_summary.csv",
    index=False
)

print()
print(
    "Saved: judge_agreement_summary.csv"
)

if len(df) < 30:

    print()
    print(
        f"NOTE: These are interim results using "
        f"{len(df)}/30 examples."
    )

    print(
        "Run this script again after the LLM judge "
        "reaches 30/30."
    )