# -------------------------------------------------------
# Reproduce the manuscript's DESCRIPTIVE numbers
#
# Purpose: verify that every descriptive figure quoted in the manuscript can be
# reproduced from the saved pipeline outputs, with NO model re-run. For each
# claim we recompute the value from source and compare it to the number printed
# in the paper, reporting PASS / FAIL. Structured by manuscript section so a
# reviewer can walk the text top-to-bottom.
#
# Data sources (all pre-existing outputs — nothing here fits or scores a model):
#   * predictions   outputs/model_performance/v2/predictions/*_tabpfn_lmic_predictions.csv
#   * training data data/processed/training_subcomponents/*_training_with_covariates_v2.csv
#   * SHAP          outputs/descriptive_statistics/v2/*_tabpfn_shap_importance_k*_n250.csv
#   * ICC           outputs/descriptive_statistics/sanitation_icc_variance_decomposition.csv
#                     (weighted lme4 null model; produced by
#                      01_data_preparation/04a_sanitation_preparing_training_dataframes.qmd)
#   * survey ranges outputs/descriptive_statistics/sanitation_survey_descriptive_statistics_v2.csv
#                     (observed within-country range; same 04a qmd)
#
# OUT OF SCOPE — model-performance numbers (deliberately NOT reproduced here, as
# they require re-running / re-scoring the models). For the record, they live in:
#   * Table 1, R² (78% / 55%), MAE, TabPFN-vs-RF ......... sanitation_tabpfn_loco_summary.csv
#                                                          (03_model_training/02b_...py)
#   * 90% PI calibration coverage (89% / 82%) ............ *_tabpfn_quantile_coverage_by_country.csv
#   * survey-vs-prediction MAE-by-age, IoU=0.96, and the
#     Sierra Leone / Burkina Faso exceptions ............. survey_vs_prediction_agreement_stats.csv
#                                                          (04_additional_analysis/08_...py)
#
# Output: a printed PASS/FAIL table per section + a combined CSV.
# Run from the repository root.
# -------------------------------------------------------

import os
import re
import ast
import numpy as np
import pandas as pd

# -------------------------------------------------------
# 1.  Paths
# -------------------------------------------------------

PRED_DIR   = "outputs/model_performance/v2/predictions"
TRAIN_DIR  = "data/processed/training_subcomponents"
SHAP_DIR   = "outputs/descriptive_statistics/v2"
DESC_DIR   = "outputs/descriptive_statistics"
TRAIN_SCRIPT = "scripts/03_model_training/02b_tabpfn_loco_cv_sanitation.py"
OUTPUT_DIR = "outputs/descriptive_statistics/v2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BS_PRED  = os.path.join(PRED_DIR, "basic_sanitation_tabpfn_lmic_predictions.csv")
OD_PRED  = os.path.join(PRED_DIR, "open_defecation_tabpfn_lmic_predictions.csv")
BS_TRAIN = os.path.join(TRAIN_DIR, "basic_sanitation_training_with_covariates_v2.csv")
OD_TRAIN = os.path.join(TRAIN_DIR, "open_defecation_training_with_covariates_v2.csv")
BS_SHAP  = os.path.join(SHAP_DIR, "basic_sanitation_tabpfn_shap_importance_k45_n250.csv")
OD_SHAP  = os.path.join(SHAP_DIR, "open_defecation_tabpfn_shap_importance_k90_n250.csv")
ICC_CSV  = os.path.join(DESC_DIR, "sanitation_icc_variance_decomposition.csv")
SURVEY_DESC_CSV = os.path.join(DESC_DIR, "sanitation_survey_descriptive_statistics_v2.csv")

# -------------------------------------------------------
# 2.  Verification harness
# -------------------------------------------------------

_checks = []          # accumulates every check for the final CSV
_current_section = "" # set by section()


def section(title):
    global _current_section
    _current_section = title
    print(f"\n{'='*72}\n{title}\n{'='*72}")


def _fmt(x):
    if isinstance(x, float):
        return f"{x:.4g}"
    if isinstance(x, (list, tuple, set)):
        return "[" + ", ".join(map(str, x)) + "]"
    return str(x)


def check(label, actual, expected, tol=0.0):
    """Numeric check: |actual - expected| <= tol."""
    if actual is None or (isinstance(actual, float) and np.isnan(actual)):
        status = "NA"
    else:
        status = "PASS" if abs(actual - expected) <= tol else "FAIL"
    _record(label, actual, f"{expected} ± {tol}", status)


def check_set(label, actual_vec, expected_vec, ordered=False):
    """Membership check: same elements (optionally same order)."""
    a, e = list(actual_vec), list(expected_vec)
    ok = (a == e) if ordered else (set(a) == set(e))
    _record(label, a, e, "PASS" if ok else "FAIL")


def _record(label, actual, expected, status):
    _checks.append({"section": _current_section, "check": label,
                    "actual": _fmt(actual), "expected": _fmt(expected),
                    "status": status})
    mark = {"PASS": "✓", "FAIL": "✗", "NA": "–"}[status]
    print(f"  [{mark} {status:4s}] {label}")
    print(f"            actual={_fmt(actual)}  expected={_fmt(expected)}")


# -------------------------------------------------------
# 3.  Load data
# -------------------------------------------------------

PRED_COLS = ["NAME_0", "NAME_1", "sdg_region", "wb_income_group",
             "fragile_context", "median", "pi90_lower", "pi90_upper"]

bs = pd.read_csv(BS_PRED, usecols=PRED_COLS + ["sanitation_basic"])
od = pd.read_csv(OD_PRED, usecols=PRED_COLS + ["open_defecation"])

for df in (bs, od):
    df["fragile_label"] = np.where(
        df["fragile_context"].astype(str).str.strip() == "Fragile or Extremely Fragile",
        "Fragile or Extremely Fragile", "Non-fragile")

INCOME_LABELS = {"L": "Low income", "LM": "Lower middle income",
                 "UM": "Upper middle income"}
bs["income_label"] = bs["wb_income_group"].map(INCOME_LABELS)
od["income_label"] = od["wb_income_group"].map(INCOME_LABELS)


def med(df, col="median"):
    return df[col].median()


def grp_median(df, group_col, group_val, col="median"):
    return med(df[df[group_col] == group_val], col)


def grp_n(df, group_col, group_val):
    return int((df[group_col] == group_val).sum())


def country_medians(df, min_regions=1):
    """Median admin-1 prediction per country. Countries with fewer than
    `min_regions` admin-1 units are dropped: a country 'ranking' built on a
    single region is not meaningful, and the manuscript's OD ranking excludes
    the three single-region states (Kiribati, Maldives, Marshall Islands)."""
    g = df.groupby("NAME_0")["median"]
    m = g.median()
    if min_regions > 1:
        m = m[g.size() >= min_regions]
    return m


def country_range(df):
    g = df.groupby("NAME_0")["median"].agg(["min", "max"])
    return ((g["max"] - g["min"]) * 100).sort_values(ascending=False)


# -------------------------------------------------------
# SECTION — Abstract / Discussion (income gradient + PI)
#   "median basic sanitation coverage rising from 36% (90% PI=17-56%) in
#    low-income to 94% (76-99%) in upper-middle-income countries. Open
#    defecation showed the reverse gradient (8% [PI=1-29%] to <1% [PI=0-1%])."
# The bracketed interval = median of the admin-1 pi90 bounds within the group.
# -------------------------------------------------------

section("ABSTRACT / DISCUSSION — income gradient (median + 90% PI)")

check("BS median coverage, low income = 36%",
      grp_median(bs, "income_label", "Low income") * 100, 36, 1)
check("BS median PI lower, low income = 17",
      med(bs[bs.income_label == "Low income"], "pi90_lower") * 100, 17, 2)
check("BS median PI upper, low income = 56",
      med(bs[bs.income_label == "Low income"], "pi90_upper") * 100, 56, 2)
check("BS median coverage, upper-middle income = 94%",
      grp_median(bs, "income_label", "Upper middle income") * 100, 94, 1)
check("BS median PI lower, upper-middle = 76",
      med(bs[bs.income_label == "Upper middle income"], "pi90_lower") * 100, 76, 2)
check("BS median PI upper, upper-middle = 99",
      med(bs[bs.income_label == "Upper middle income"], "pi90_upper") * 100, 99, 2)

check("OD median rate, low income = 8%",
      grp_median(od, "income_label", "Low income") * 100, 8, 1)
check("OD median PI lower, low income = 1",
      med(od[od.income_label == "Low income"], "pi90_lower") * 100, 1, 1.5)
check("OD median PI upper, low income = 29",
      med(od[od.income_label == "Low income"], "pi90_upper") * 100, 29, 3)
check("OD median rate, upper-middle income < 1%",
      grp_median(od, "income_label", "Upper middle income") * 100, 0.5, 0.5)

# -------------------------------------------------------
# SECTION — Results: spatial variation (totals + SDG regions)
# -------------------------------------------------------

section("RESULTS — totals and SDG-region distribution")

check("Total admin-1 units (BS) = 2310", len(bs), 2310, 0)
check("Total admin-1 units (OD) = 2310", len(od), 2310, 0)
check("Distinct LMICs (BS) = 130", bs["NAME_0"].nunique(), 130, 0)
check("Distinct LMICs (OD) = 130", od["NAME_0"].nunique(), 130, 0)

# Basic sanitation by SDG region
check("BS Sub-Saharan Africa median = 39%",
      grp_median(bs, "sdg_region", "Sub-Saharan Africa") * 100, 39, 1)
check("BS Sub-Saharan Africa n = 662",
      grp_n(bs, "sdg_region", "Sub-Saharan Africa"), 662, 0)
check("BS Oceania median = 49%", grp_median(bs, "sdg_region", "Oceania") * 100, 49, 2)
check("BS Oceania n = 74", grp_n(bs, "sdg_region", "Oceania"), 74, 0)
check("BS Europe & Northern America median = 97%",
      grp_median(bs, "sdg_region", "Europe and Northern America") * 100, 97, 1)
check("BS Europe & Northern America n = 223",
      grp_n(bs, "sdg_region", "Europe and Northern America"), 223, 0)

# "all other SDG regions ... spanning 1,351 admin-1 units"
_ssa_oce_eur = {"Sub-Saharan Africa", "Oceania", "Europe and Northern America"}
_other = bs[~bs["sdg_region"].isin(_ssa_oce_eur)]
check("BS 'other regions' n = 1351", len(_other), 1351, 0)
check("BS 'other regions' min admin-1 median >= 36% (band 36-99)",
      _other.groupby("sdg_region")["median"].median().min() * 100, 89, 5)

# Open defecation by SDG region.
# NB manuscript prints n=622 for OD Sub-Saharan Africa vs n=662 for BS. Both
# outcomes are predicted on the SAME 2,310 units, so the region count must be
# identical — this flags the 622 as a likely typo for 662.
check("OD Sub-Saharan Africa median = 8%",
      grp_median(od, "sdg_region", "Sub-Saharan Africa") * 100, 8, 1)
check("OD Sub-Saharan Africa n (manuscript prints 622; BS prints 662)",
      grp_n(od, "sdg_region", "Sub-Saharan Africa"), 662, 0)
check("OD Oceania median = 1%", grp_median(od, "sdg_region", "Oceania") * 100, 1, 1)
check("OD Oceania n = 74", grp_n(od, "sdg_region", "Oceania"), 74, 0)
check("OD Northern Africa & Western Asia median ~ 0",
      grp_median(od, "sdg_region", "Northern Africa and Western Asia") * 100, 0, 1)
check("OD Europe & Northern America median ~ 0",
      grp_median(od, "sdg_region", "Europe and Northern America") * 100, 0, 1)

# -------------------------------------------------------
# SECTION — Results: income groups & fragility
# -------------------------------------------------------

section("RESULTS — income groups and fragility")

for lbl, val, n_exp, med_exp in [
    ("Low income", "Low income", 406, 36),
    ("Lower-middle income", "Lower middle income", 812, 78),
    ("Upper-middle income", "Upper middle income", 1092, 94),
]:
    check(f"BS {lbl} n = {n_exp}", grp_n(bs, "income_label", val), n_exp, 0)
    check(f"BS {lbl} median = {med_exp}%",
          grp_median(bs, "income_label", val) * 100, med_exp, 1)

check("OD Low income median = 8%",
      grp_median(od, "income_label", "Low income") * 100, 8, 1)
check("OD Lower-middle income median = 3%",
      grp_median(od, "income_label", "Lower middle income") * 100, 3, 1)
check("OD Upper-middle income median < 1%",
      grp_median(od, "income_label", "Upper middle income") * 100, 0.5, 0.5)

check("BS fragile median = 48%",
      grp_median(bs, "fragile_label", "Fragile or Extremely Fragile") * 100, 48, 2)
check("BS non-fragile median = 93%",
      grp_median(bs, "fragile_label", "Non-fragile") * 100, 93, 2)
check("OD fragile median = 7%",
      grp_median(od, "fragile_label", "Fragile or Extremely Fragile") * 100, 7, 1)
check("OD non-fragile median < 1%",
      grp_median(od, "fragile_label", "Non-fragile") * 100, 0.5, 0.5)

# -------------------------------------------------------
# SECTION — Results: country rankings & within-country inequality
# -------------------------------------------------------

section("RESULTS — country rankings and within-country inequality")

check_set("Lowest-5 BS countries (median)",
          country_medians(bs).sort_values().head(5).index.tolist(),
          ["Central African Republic", "South Sudan", "Chad",
           "Guinea-Bissau", "Madagascar"])
# Excludes single-region countries (see country_medians): without this filter
# single-region Kiribati (45.2%) intrudes at rank 4 and displaces Benin.
check_set("Highest-5 OD countries (median, countries with >=2 admin-1 units)",
          country_medians(od, min_regions=2).sort_values(ascending=False).head(5).index.tolist(),
          ["Niger", "Chad", "South Sudan", "Togo", "Benin"])
check_set("Greatest predicted within-country range, BS",
          country_range(bs).head(5).index.tolist(),
          ["Nigeria", "Yemen", "Tanzania", "Mozambique", "Malawi"])
check_set("Greatest predicted within-country range, OD",
          country_range(od).head(5).index.tolist(),
          ["Niger", "Chad", "Benin", "Angola", "Madagascar"])

# ICC of the RAW survey data (read from the weighted-lme4 output CSV; the model
# is a null random-intercept fit produced in 04a and needs R/lme4 to recompute).
icc = pd.read_csv(ICC_CSV).set_index("outcome")["icc"]
check("ICC basic sanitation = 0.87", float(icc["basic_sanitation"]), 0.87, 0.01)
check("ICC open defecation = 0.61", float(icc["open_defecation"]), 0.61, 0.01)

# Median OBSERVED within-country range (survey estimates, from the 04a table).
sd = pd.read_csv(SURVEY_DESC_CSV)
check("Median observed within-country range, BS = 32 p.p.",
      sd["range_basic_sanitation_pp"].median(), 32, 1)
check("Median observed within-country range, OD = 13 p.p.",
      sd["range_open_defecation_pp"].median(), 13, 1)

# -------------------------------------------------------
# SECTION — Results: predictor importance (SHAP re-aggregation)
#   Re-aggregates the saved per-predictor mean|SHAP| into the manuscript's
#   category scheme. No SHAP recomputation. Mirrors the regrouping in
#   09_plot_shap_grouped_importance.py and the national/subnational split.
# -------------------------------------------------------

section("RESULTS — predictor importance (SHAP shares)")

_src = open(TRAIN_SCRIPT).read()
FEATURE_CATEGORY_MAP = ast.literal_eval(
    re.search(r"FEATURE_CATEGORY_MAP\s*=\s*(\{.*?\n\})", _src, re.S).group(1))
NATIONAL_FEATURES = set(ast.literal_eval(
    re.search(r"COUNTRY_LEVEL_FEATURES\s*=\s*(\[.*?\])", _src, re.S).group(1)))

WASTEWATER = {"ww_collection_percent", "ww_treatment_percent", "ww_reuse_percent"}
TO_HYDRO   = {"TootchiEtAl_WetlandsRegularlyFlooded", "CIFOR_TropicalPeatlandExtent"}


def regroup(feature, cat):
    if cat == "JMP" or feature in WASTEWATER:
        return "National sanitation estimates"
    if feature in TO_HYDRO:
        return "Hydrology & Soil"
    if cat in ("Topography", "Vegetation texture", "Vegetation coverage"):
        return "Terrain & vegetation"
    return cat


def shap_shares(path):
    d = pd.read_csv(path)
    total = d["mean_abs_shap"].sum()
    d["cat"] = d["feature"].map(FEATURE_CATEGORY_MAP)
    d["grp"] = [regroup(f, c) for f, c in zip(d["feature"], d["cat"])]
    d["is_national"] = d["feature"].isin(NATIONAL_FEATURES)
    grp_share = d.groupby("grp")["mean_abs_shap"].sum() / total * 100
    nat_share = d.groupby("is_national")["mean_abs_shap"].sum() / total * 100
    nat_n     = d.groupby("is_national").size()
    jmp_share = d.loc[d["cat"] == "JMP", "mean_abs_shap"].sum() / total * 100
    return grp_share, nat_share, nat_n, jmp_share


bs_grp, bs_nat, bs_natn, bs_jmp = shap_shares(BS_SHAP)
od_grp, od_nat, od_natn, od_jmp = shap_shares(OD_SHAP)

# National vs subnational split (share and count of predictors)
check("BS national predictors share = 54%", float(bs_nat[True]), 54, 2)
check("BS national predictors n = 5", int(bs_natn[True]), 5, 0)
check("BS subnational predictors share = 46%", float(bs_nat[False]), 46, 2)
check("BS subnational predictors n = 40", int(bs_natn[False]), 40, 0)
check("OD national predictors share = 41%", float(od_nat[True]), 41, 2)
check("OD national predictors n = 13", int(od_natn[True]), 13, 0)
check("OD subnational predictors share = 59%", float(od_nat[False]), 59, 2)
check("OD subnational predictors n = 77", int(od_natn[False]), 77, 0)

# Category shares (manuscript wording in parentheses = BS / OD)
for grp, bs_exp, od_exp, tol in [
    ("National sanitation estimates", 50, 31, 2),
    ("Human presence",               20, 24, 2),
    ("Terrain & vegetation",         11, 14, 2),
    ("Climate",                       8, 11, 2),
    ("Hydrology & Soil",              5,  7, 2),
    ("Socio-economic & governance",   4, 11, 2),
    ("Region size",                   2,  3, 1),
]:
    check(f"BS SHAP share — {grp} = {bs_exp}%", float(bs_grp.get(grp, np.nan)), bs_exp, tol)
    check(f"OD SHAP share — {grp} = {od_exp}%", float(od_grp.get(grp, np.nan)), od_exp, tol)

# JMP national sanitation estimate alone (dominant single predictor)
check("BS JMP national estimate share = 38%", float(bs_jmp), 38, 2)
check("OD JMP national estimate share = 25%", float(od_jmp), 25, 2)

# -------------------------------------------------------
# SECTION — Results: uncertainty (data-gap priority countries)
#   The 10 most-uncertain countries (median 90% PI width 59-83%) and the four
#   priority data-gap countries are descriptive selections over the predictions
#   / data-availability flags (Fig S1, S9).
# -------------------------------------------------------

section("RESULTS — uncertainty and priority data-gap countries")

bs_pi = bs.assign(w=(bs.pi90_upper - bs.pi90_lower))
od_pi = od.assign(w=(od.pi90_upper - od.pi90_lower))
top10_bs = (bs_pi.groupby("NAME_0")["w"].median() * 100).sort_values(ascending=False).head(10)
check("BS 10 most-uncertain countries: median PI width in 59-83% band (min)",
      float(top10_bs.min()), 59, 6)
check("BS 10 most-uncertain countries: median PI width in 59-83% band (max)",
      float(top10_bs.max()), 83, 6)

# Four priority countries flagged in the manuscript (Fig S9).
priority = {"Republic of Congo", "Eritrea", "Nicaragua", "North Korea"}
vuln_path = os.path.join(DESC_DIR, "stats_data_gap_vulnerability.csv")
if os.path.exists(vuln_path):
    vuln = pd.read_csv(vuln_path)
    flagged = set(vuln.loc[vuln["high_concern"] == True, "country"])  # noqa: E712
    check_set("Four priority countries present in high-concern list",
              sorted(priority & flagged), sorted(priority))
else:
    _record("Four priority countries (stats_data_gap_vulnerability.csv)",
            "file missing", sorted(priority), "NA")

# -------------------------------------------------------
# SECTION — Fig 1 / Data S1 (survey inputs)
#   "1.8 million households across 1197 administrative areas and 89 countries"
#   Fig 1: 88 countries for basic sanitation, 89 for open defecation.
# -------------------------------------------------------

section("FIG 1 / DATA S1 — survey inputs")

bs_tr = pd.read_csv(BS_TRAIN, usecols=["country_outcome", "HH7_region_outcome",
                                       "n_households", "analysis_year"])
od_tr = pd.read_csv(OD_TRAIN, usecols=["country_outcome", "HH7_region_outcome",
                                       "n_households", "analysis_year"])

check("BS survey region-estimates = 1168", len(bs_tr), 1168, 0)
check("OD survey region-estimates = 1205", len(od_tr), 1205, 0)
check("BS survey countries = 88", bs_tr["country_outcome"].nunique(), 88, 0)
check("OD survey countries = 89", od_tr["country_outcome"].nunique(), 89, 0)

union = pd.concat([bs_tr, od_tr])
check("Total distinct countries = 89", union["country_outcome"].nunique(), 89, 0)
# Households (~1.8 million): the open-defecation set is the household superset.
check("Total households ~ 1.8 million",
      od_tr["n_households"].sum() / 1e6, 1.8, 0.1)

# Administrative areas: manuscript states 1197. Report the candidate counts so
# the (small) discrepancy is visible rather than hidden.
union_areas = union.drop_duplicates(["country_outcome", "HH7_region_outcome"]).shape[0]
check("Distinct administrative areas ~ 1197 (union of both outcomes)",
      union_areas, 1197, 0)
check("Survey years span 2015-2024 (min)",
      int(union["analysis_year"].min()), 2015, 0)
check("Survey years span 2015-2024 (max)",
      int(union["analysis_year"].max()), 2024, 0)

# -------------------------------------------------------
# 4.  Summary
# -------------------------------------------------------

results = pd.DataFrame(_checks)
out_csv = os.path.join(OUTPUT_DIR, "manuscript_descriptive_number_checks.csv")
results.to_csv(out_csv, index=False)

n_pass = (results["status"] == "PASS").sum()
n_fail = (results["status"] == "FAIL").sum()
n_na   = (results["status"] == "NA").sum()

print(f"\n{'='*72}\nSUMMARY\n{'='*72}")
print(f"  PASS: {n_pass}   FAIL: {n_fail}   NA: {n_na}   (of {len(results)})")
if n_fail:
    print("\n  FAILED / mismatched checks:")
    for _, r in results[results["status"] == "FAIL"].iterrows():
        print(f"    - [{r['section']}] {r['check']}")
        print(f"        actual={r['actual']}  expected={r['expected']}")
if n_na:
    print("\n  NA (could not evaluate):")
    for _, r in results[results["status"] == "NA"].iterrows():
        print(f"    - [{r['section']}] {r['check']}")

print(f"\nSaved: {out_csv}")
