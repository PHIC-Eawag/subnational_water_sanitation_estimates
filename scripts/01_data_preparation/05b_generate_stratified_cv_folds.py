# -------------------------------------------------------
# 05b — Generate stratified cross-validation folds
#
# Produces the country-level held-out folds shared by BOTH sanitation
# modelling scripts:
#   - scripts/03_model_training/01a_sanitation_modelling_RF.qmd   (Random Forest)
#   - scripts/03_model_training/02b_tabpfn_loco_cv_sanitation.py  (TabPFN)
#
# Folds are defined by whole held-out countries, stratified so each fold
# mirrors the SDG-region mix of the prediction space. Generating them once
# here (in Python) is the single source of truth: both models READ this file
# rather than sampling their own folds, so their feature-set comparisons are
# evaluated on IDENTICAL held-out sets. (R's set.seed()/sample() and NumPy's
# default_rng() diverge even with equal seeds, so folds cannot be reproduced
# across languages by matching parameters alone.)
#
# Must run AFTER:
#   - 05_prepare_prediction_data.qmd  -> data/processed/prediction/prediction_covariates_2024.csv
#   - 04a_sanitation_preparing_training_dataframes.qmd
#         -> data/processed/training_subcomponents/basic_sanitation_training_with_covariates_v2.csv
#
# Output:
#   - data/processed/cv_folds/stratified_cv_folds.csv   (columns: fold, country)
# -------------------------------------------------------

import os
import textwrap
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------------
# 1.  Paths
# -------------------------------------------------------

DATA_DIR             = "data/processed/training_subcomponents"
PRED_COVARIATES_PATH = "data/processed/prediction/prediction_covariates_2024.csv"
BS_FILENAME          = "basic_sanitation_training_with_covariates_v2.csv"

OUTPUT_DIR  = "data/processed/cv_folds"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "stratified_cv_folds.csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------
# 2.  Column names (must match the modelling scripts)
# -------------------------------------------------------

COUNTRY_COL = "country_cov"
OUTCOME_COL = "country_outcome"   # used for country exclusions
SDG_COL     = "sdg_region"
INCOME_COL  = "wb_income_group"

# -------------------------------------------------------
# 3.  Fold parameters (must match 02b Section 8)
# -------------------------------------------------------

N_REPEATS     = 5     # number of independent test folds to create
FOLD_FRACTION = 0.15  # each fold holds out ~15% of the training data

# -------------------------------------------------------
# 4.  Stratum targets from the prediction space
#     (proportional SDG-region composition of the prediction dataset)
# -------------------------------------------------------

pred_cov = pd.read_csv(PRED_COVARIATES_PATH)

stratum_targets = (
    pred_cov[pred_cov[SDG_COL].notna()]
    .groupby(SDG_COL, as_index=False)
    .size()
    .rename(columns={"size": "n_pred_regions"})
    .assign(fraction=lambda d: d["n_pred_regions"] / d["n_pred_regions"].sum())
)

# -------------------------------------------------------
# 5.  Country strata from the basic-sanitation training data
#     (Indonesia excluded to match the modelling scripts)
# -------------------------------------------------------

_bs_raw = pd.read_csv(os.path.join(DATA_DIR, BS_FILENAME))
_bs_raw = _bs_raw[
    ~_bs_raw[OUTCOME_COL].astype(str).str.startswith("Indonesia", na=False)
]

country_strata = (
    _bs_raw
    .groupby(COUNTRY_COL, as_index=False)
    .agg(
        sdg_region      = (SDG_COL,    "first"),
        wb_income_group = (INCOME_COL, "first"),
        n_regions       = (COUNTRY_COL, "count"),
    )
)

total_train_regions = int(country_strata["n_regions"].sum())

stratum_targets["n_in_fold"] = (
    stratum_targets["fraction"] * FOLD_FRACTION * total_train_regions
).round().astype(int)

print("\nStratum targets per fold (SDG region):")
print(stratum_targets.sort_values("n_pred_regions", ascending=False).to_string(index=False))

# -------------------------------------------------------
# 6.  Stratified fold sampler
#     (This is the single authoritative implementation. If it changes, both
#      01a and 02b pick up the new folds automatically on the next run.)
# -------------------------------------------------------


def sample_held_out_countries(country_strata, stratum_targets, seed_i=1):
    """
    Randomly select which countries go into one held-out test fold.
    - Works region by region (SDG zones), sampling whole countries at a time.
    - Stops adding countries once enough regions have been collected for that zone.
    - High-income countries (wb_income_group == 'H') are never held out.
    - seed_i controls randomness — different seeds give different folds.
    """
    rng      = np.random.default_rng(seed_i)  # reproducible random number generator
    held_out = []
    eligible = country_strata[country_strata["wb_income_group"] != "H"].copy()

    for _, row in stratum_targets.iterrows():
        stratum  = row[SDG_COL]
        target_n = int(row["n_in_fold"])

        # Get all eligible countries in this SDG region
        pool = (eligible[eligible["sdg_region"] == stratum]
                .copy().reset_index(drop=True))
        if len(pool) == 0 or target_n == 0:
            continue

        sampled_n = 0
        sampled   = []

        # Keep drawing countries until we hit the regional target count
        while sampled_n < target_n and len(pool) > 0:
            idx    = int(rng.integers(0, len(pool)))
            chosen = pool.loc[idx, COUNTRY_COL]
            sampled.append(chosen)
            sampled_n += int(pool.loc[idx, "n_regions"])
            pool = pool.drop(index=idx).reset_index(drop=True)

        if sampled_n < target_n:
            warnings.warn(
                f"Stratum '{stratum}': only {sampled_n} regions available, "
                f"target was {target_n}."
            )
        held_out.extend(sampled)

    return held_out


# Generate the N_REPEATS independent folds (each with a different random seed)
fold_country_lists = [
    sample_held_out_countries(country_strata, stratum_targets, seed_i=i)
    for i in range(1, N_REPEATS + 1)
]

# -------------------------------------------------------
# 7.  Save + diagnostics
# -------------------------------------------------------

fold_defs = pd.DataFrame(
    [
        {"fold": i, "country": country}
        for i, countries in enumerate(fold_country_lists, 1)
        for country in countries
    ]
)
fold_defs.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved fold definitions: {OUTPUT_PATH}")

print("\nFold diagnostics:")
for i, countries in enumerate(fold_country_lists, 1):
    n_reg = int(_bs_raw[_bs_raw[COUNTRY_COL].isin(countries)].shape[0])
    pct   = 100 * n_reg / total_train_regions
    print(f"  Fold {i}: {len(countries)} countries, {n_reg} regions ({pct:.1f}%)")

# -------------------------------------------------------
# 8.  Diagnostic plots — do the folds mirror the prediction space?
#
# For each SDG region / income group, compare the % of regions in the
# prediction space (the target mix) against the % in each held-out fold.
# Folds that track the steelblue prediction-space bars are well stratified.
# -------------------------------------------------------

PLOT_DIR = os.path.join(OUTPUT_DIR, "plots")
os.makedirs(PLOT_DIR, exist_ok=True)


def _pct_by(df, col):
    """Percentage of (non-missing) rows falling in each category of `col`."""
    counts = df[df[col].notna()][col].value_counts()
    return (100 * counts / counts.sum()).to_dict() if len(counts) else {}


def plot_fold_distribution(col, title, xlabel, fname):
    # Target distribution across the prediction space
    pred_pct = _pct_by(pred_cov, col)
    # Distribution within each held-out fold (training regions held out)
    fold_pcts = [
        _pct_by(_bs_raw[_bs_raw[COUNTRY_COL].isin(countries)], col)
        for countries in fold_country_lists
    ]

    # Categories ordered by prediction-space share (largest first)
    categories = sorted(pred_pct, key=lambda c: pred_pct[c], reverse=True)

    n_series = 1 + len(fold_pcts)
    x        = np.arange(len(categories))
    width    = 0.8 / n_series

    fig, ax = plt.subplots(figsize=(11, 5))

    # Prediction space (reference target) — steelblue
    ax.bar(
        x + (0 - (n_series - 1) / 2) * width,
        [pred_pct.get(c, 0) for c in categories],
        width, label="Prediction space", color="steelblue",
    )
    # Folds — grey shades, one bar per fold
    greys = plt.cm.Greys(np.linspace(0.45, 0.8, len(fold_pcts)))
    for j, fp in enumerate(fold_pcts):
        ax.bar(
            x + ((j + 1) - (n_series - 1) / 2) * width,
            [fp.get(c, 0) for c in categories],
            width, label=f"Fold {j + 1}", color=greys[j],
        )

    ax.set_xticks(x)
    ax.set_xticklabels([textwrap.fill(str(c), 16) for c in categories], fontsize=8)
    ax.set_ylabel("% of regions")
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.legend(fontsize=8, ncol=2)
    plt.tight_layout()

    out = os.path.join(PLOT_DIR, fname)
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


plot_fold_distribution(
    SDG_COL,
    "Fold distribution by SDG region\n(steelblue = prediction space, grey = folds)",
    "SDG region", "fold_distribution_sdg_region.png",
)
plot_fold_distribution(
    INCOME_COL,
    "Fold distribution by income group\n(steelblue = prediction space, grey = folds)",
    "World Bank income group", "fold_distribution_income_group.png",
)
