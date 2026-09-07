# -------------------------------------------------------
# Descriptive statistics for results text
#
# Computes medians, IQRs, and counts needed to fill
# placeholders in the results section, for:
#   - SDG regions
#   - Income groups
#   - Fragile contexts
#   - Within-country ranges
#   - Data gap countries (with/without JMP estimates)
#
# Outputs a printed summary and a CSV for reference.
# -------------------------------------------------------

import os
import numpy as np
import pandas as pd

# -------------------------------------------------------
# 1.  Paths
# -------------------------------------------------------

# Read the retrained (_v2) predictions and write stats under a v2 subfolder,
# so this analysis uses the corrected sanitation labelling and does not
# overwrite prior outputs. Repo paths only (never switchdrive).
PRED_DIR   = "outputs/model_performance/v2/predictions"
OUTPUT_DIR = "outputs/descriptive_statistics/v2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BS_PRED = os.path.join(PRED_DIR, "basic_sanitation_tabpfn_lmic_predictions.csv")
OD_PRED = os.path.join(PRED_DIR, "open_defecation_tabpfn_lmic_predictions.csv")

# -------------------------------------------------------
# 2.  Load data
# -------------------------------------------------------

bs = pd.read_csv(BS_PRED)
od = pd.read_csv(OD_PRED)

# Add 90% PI width
bs["width_90"] = bs["pi90_upper"] - bs["pi90_lower"]
od["width_90"] = od["pi90_upper"] - od["pi90_lower"]

INCOME_LABELS = {"L": "Low income", "LM": "Lower middle income",
                 "UM": "Upper middle income"}
bs["income_label"] = bs["wb_income_group"].map(INCOME_LABELS)
od["income_label"] = od["wb_income_group"].map(INCOME_LABELS)

# -------------------------------------------------------
# 3.  Helper
# -------------------------------------------------------

def summarise(df, group_col, value_col="median"):
    """Return n regions, median, Q25, Q75 per group."""
    def stats(x):
        return pd.Series({
            "n_regions":  len(x),
            "n_countries": x["NAME_0"].nunique() if "NAME_0" in x.columns else np.nan,
            "min":        round(x[value_col].min() * 100, 1),
            "median":     round(x[value_col].median() * 100, 1),
            "max":        round(x[value_col].max() * 100, 1),
            "q25":        round(x[value_col].quantile(0.25) * 100, 1),
            "q75":        round(x[value_col].quantile(0.75) * 100, 1),
        })
    return df.groupby(group_col).apply(stats, include_groups=False).reset_index()


def print_section(title, df):
    print(f"\n{'='*60}")
    print(title)
    print('='*60)
    print(df.to_string(index=False))


def versioned_path(directory, filename):
    """Return directory/filename_vN.csv where N is the next unused version."""
    stem = filename.replace(".csv", "")
    version = 1
    while True:
        path = os.path.join(directory, f"{stem}_v{version}.csv")
        if not os.path.exists(path):
            return path
        version += 1


# -------------------------------------------------------
# 4.  SDG region summaries
# -------------------------------------------------------

bs_sdg = summarise(bs, "sdg_region")
od_sdg = summarise(od, "sdg_region")

# Merge for side-by-side comparison
sdg_combined = bs_sdg.rename(columns={
    "min": "BS_min_%", "median": "BS_median_%", "max": "BS_max_%",
    "q25": "BS_q25_%", "q75": "BS_q75_%", "n_regions": "n_regions_BS"
}).merge(
    od_sdg.rename(columns={
        "min": "OD_min_%", "median": "OD_median_%", "max": "OD_max_%",
        "q25": "OD_q25_%", "q75": "OD_q75_%", "n_regions": "n_regions_OD"
    }),
    on="sdg_region", how="outer"
).sort_values("BS_median_%")

print_section("BASIC SANITATION & OPEN DEFECATION — BY SDG REGION", sdg_combined)
sdg_combined.to_csv(versioned_path(OUTPUT_DIR, "stats_sdg_region.csv"), index=False)

# -------------------------------------------------------
# 5.  Income group summaries
# -------------------------------------------------------

INCOME_ORDER = ["Low income", "Lower middle income", "Upper middle income"]

bs_inc = summarise(bs[bs["income_label"].notna()], "income_label")
od_inc = summarise(od[od["income_label"].notna()], "income_label")

inc_combined = bs_inc.rename(columns={
    "min": "BS_min_%", "median": "BS_median_%", "max": "BS_max_%",
    "q25": "BS_q25_%", "q75": "BS_q75_%", "n_regions": "n_regions_BS"
}).merge(
    od_inc.rename(columns={
        "min": "OD_min_%", "median": "OD_median_%", "max": "OD_max_%",
        "q25": "OD_q25_%", "q75": "OD_q75_%", "n_regions": "n_regions_OD"
    }),
    on="income_label", how="outer"
)
inc_combined["income_label"] = pd.Categorical(
    inc_combined["income_label"], categories=INCOME_ORDER, ordered=True
)
inc_combined = inc_combined.sort_values("income_label")

print_section("BASIC SANITATION & OPEN DEFECATION — BY INCOME GROUP", inc_combined)
inc_combined.to_csv(versioned_path(OUTPUT_DIR, "stats_income_group.csv"), index=False)

# -------------------------------------------------------
# 6.  Fragile context summaries
# -------------------------------------------------------

def label_fragile(x):
    if isinstance(x, str) and x.strip() == "Fragile or Extremely Fragile":
        return "Fragile or Extremely Fragile"
    return "Non-fragile"

bs["fragile_label"] = bs["fragile_context"].apply(label_fragile)
od["fragile_label"] = od["fragile_context"].apply(label_fragile)

bs_frag = summarise(bs, "fragile_label")
od_frag = summarise(od, "fragile_label")

frag_combined = bs_frag.rename(columns={
    "min": "BS_min_%", "median": "BS_median_%", "max": "BS_max_%",
    "q25": "BS_q25_%", "q75": "BS_q75_%", "n_regions": "n_regions_BS"
}).merge(
    od_frag.rename(columns={
        "min": "OD_min_%", "median": "OD_median_%", "max": "OD_max_%",
        "q25": "OD_q25_%", "q75": "OD_q75_%", "n_regions": "n_regions_OD"
    }),
    on="fragile_label", how="outer"
)

print_section("BASIC SANITATION & OPEN DEFECATION — BY FRAGILE CONTEXT", frag_combined)
frag_combined.to_csv(versioned_path(OUTPUT_DIR, "stats_fragile_context.csv"), index=False)

# -------------------------------------------------------
# 7.  Within-country range (max - min across Admin-1 units)
# -------------------------------------------------------

country_col = "NAME_0" if "NAME_0" in bs.columns else "country"

bs_range = (
    bs.groupby(country_col)["median"]
    .agg(["min", "max", "count"])
    .assign(range=lambda x: (x["max"] - x["min"]) * 100)
    .reset_index()
    .sort_values("range", ascending=False)
)
bs_range["min_pct"]  = (bs_range["min"] * 100).round(1)
bs_range["max_pct"]  = (bs_range["max"] * 100).round(1)
bs_range["range"]    = bs_range["range"].round(1)

print_section("TOP 10 COUNTRIES BY WITHIN-COUNTRY RANGE — BASIC SANITATION",
              bs_range.head(10)[[country_col, "count", "min_pct", "max_pct", "range"]])

od_range = (
    od.groupby(country_col)["median"]
    .agg(["min", "max", "count"])
    .assign(range=lambda x: (x["max"] - x["min"]) * 100)
    .reset_index()
    .sort_values("range", ascending=False)
)
od_range["min_pct"] = (od_range["min"] * 100).round(1)
od_range["max_pct"] = (od_range["max"] * 100).round(1)
od_range["range"]   = od_range["range"].round(1)

print_section("TOP 10 COUNTRIES BY WITHIN-COUNTRY RANGE — OPEN DEFECATION",
              od_range.head(10)[[country_col, "count", "min_pct", "max_pct", "range"]])

bs_range.to_csv(versioned_path(OUTPUT_DIR, "stats_within_country_range_BS.csv"), index=False)
od_range.to_csv(versioned_path(OUTPUT_DIR, "stats_within_country_range_OD.csv"), index=False)

# -------------------------------------------------------
# 8.  Data gap countries
#     (countries with/without JMP national estimates)
#     Requires a 'has_jmp_data' column in predictions.
#     If not present, flag for manual check.
# -------------------------------------------------------

if "sanitation_basic" in bs.columns:
    # Countries where JMP national estimate is available (non-null)
    bs["has_jmp"] = bs["sanitation_basic"].notna()
    n_countries_total      = bs[country_col].nunique()
    n_countries_with_jmp   = bs[bs["has_jmp"]][country_col].nunique()
    n_countries_without_jmp = bs[~bs["has_jmp"]][country_col].nunique()
    n_regions_total        = len(bs)
    n_regions_with_jmp     = bs[bs["has_jmp"]].shape[0]
    n_regions_without_jmp  = bs[~bs["has_jmp"]].shape[0]

    print(f"\n{'='*60}")
    print("DATA GAP FILLING — BASIC SANITATION")
    print('='*60)
    print(f"  Total countries:              {n_countries_total}")
    print(f"  Countries with JMP data:      {n_countries_with_jmp}")
    print(f"  Countries without JMP data:   {n_countries_without_jmp}")
    print(f"  Total Admin-1 regions:        {n_regions_total}")
    print(f"  Regions with JMP data:        {n_regions_with_jmp}")
    print(f"  Regions without JMP data:     {n_regions_without_jmp}")

    # Which SDG regions/income groups have most data gaps?
    gap_countries = bs[~bs["has_jmp"]][[country_col, "sdg_region", "income_label"]].drop_duplicates()
    gap_by_sdg = gap_countries.groupby("sdg_region").size().sort_values(ascending=False)
    print("\n  Data gap countries by SDG region:")
    print(gap_by_sdg.to_string())
    gap_by_sdg.to_csv(versioned_path(OUTPUT_DIR, "stats_data_gaps_by_sdg.csv"))
else:
    print("\n  [NOTE] 'sanitation_basic' column not found — "
          "cannot compute data gap statistics. "
          "Ensure JMP estimates are joined to prediction file.")

# -------------------------------------------------------
# 9.  90% PI width by SDG region
# -------------------------------------------------------

def summarise_width(df, group_col, value_col="width_90"):
    def stats(x):
        return pd.Series({
            "min_width_%":    round(x[value_col].min() * 100, 1),
            "median_width_%": round(x[value_col].median() * 100, 1),
            "max_width_%":    round(x[value_col].max() * 100, 1),
        })
    return df.groupby(group_col).apply(stats, include_groups=False).reset_index()

bs_width_sdg = summarise_width(bs, "sdg_region")
od_width_sdg = summarise_width(od, "sdg_region")

# Order by ascending BS median width (matches figure)
sdg_width_order = bs_width_sdg.set_index("sdg_region")["median_width_%"].sort_values().index

width_sdg_combined = bs_width_sdg.rename(columns={
    "min_width_%": "BS_min_width_%", "median_width_%": "BS_median_width_%",
    "max_width_%": "BS_max_width_%"
}).merge(
    od_width_sdg.rename(columns={
        "min_width_%": "OD_min_width_%", "median_width_%": "OD_median_width_%",
        "max_width_%": "OD_max_width_%"
    }),
    on="sdg_region", how="outer"
).set_index("sdg_region").loc[sdg_width_order].reset_index()

print_section("90% PREDICTION INTERVAL WIDTH — BY SDG REGION", width_sdg_combined)
width_sdg_combined.to_csv(versioned_path(OUTPUT_DIR, "stats_pi_width_sdg_region.csv"), index=False)

# -------------------------------------------------------
# 9b.  90% PI width by income group & fragile context
#      Supports the uncertainty paragraph (larger intervals in low/LM-income
#      and fragile settings).
# -------------------------------------------------------

bs_width_income = summarise_width(bs[bs["income_label"].notna()], "income_label")
bs_width_frag   = summarise_width(bs, "fragile_label")
od_width_income = summarise_width(od[od["income_label"].notna()], "income_label")
od_width_frag   = summarise_width(od, "fragile_label")

print_section("90% PI WIDTH — BY INCOME GROUP (basic sanitation)", bs_width_income)
print_section("90% PI WIDTH — BY FRAGILE CONTEXT (basic sanitation)", bs_width_frag)
bs_width_income.to_csv(versioned_path(OUTPUT_DIR, "stats_pi_width_income_BS.csv"), index=False)
bs_width_frag.to_csv(versioned_path(OUTPUT_DIR, "stats_pi_width_fragile_BS.csv"), index=False)
od_width_income.to_csv(versioned_path(OUTPUT_DIR, "stats_pi_width_income_OD.csv"), index=False)
od_width_frag.to_csv(versioned_path(OUTPUT_DIR, "stats_pi_width_fragile_OD.csv"), index=False)

# -------------------------------------------------------
# 9c.  Uncertainty vs data availability (survey + JMP)
#      Overlap of prediction uncertainty with data gaps, matching Fig 5.
#        in_training : district's country appears in the training data
#        has_jmp     : national JMP estimate available (sanitation_basic not NaN)
#      Country-level flags, consistent with 05_plot_sanitation_uncertainty.py.
# -------------------------------------------------------

TRAIN_DIR = "data/processed/training_subcomponents"

# Harmonise training country names (country_cov) to the prediction NAME_0
# spelling, so the in_training match is not broken by spelling differences
# (e.g. "North Macedonia" vs "Macedonia").
NAME_FIXES = {
    "North Macedonia":                  "Macedonia",
    "Eswatini":                         "Swaziland",
    "Lao People's Democratic Republic": "Laos",
}

def add_data_flags(df, train_file, jmp_col):
    tr = pd.read_csv(os.path.join(TRAIN_DIR, train_file), usecols=["country_cov"])
    train_countries = set(tr["country_cov"].replace(NAME_FIXES))
    df["in_training"] = df[country_col].isin(train_countries)
    df["has_jmp"]     = df[jmp_col].notna() if jmp_col in df.columns else False
    return df

def data_availability_table(df):
    g = df.groupby(["in_training", "has_jmp"])
    tbl = pd.DataFrame({
        "n_districts":        g.size(),
        "n_countries":        g[country_col].nunique(),
        "median_PI_width_%":  (g["width_90"].median() * 100).round(1),
        "pop_millions":       (g["worldpop_sum"].sum() / 1e6).round(0)
                              if "worldpop_sum" in df.columns else np.nan,
    }).reset_index().sort_values("median_PI_width_%", ascending=False)
    return tbl

for _df, _name, _train, _jmp in [
    (bs, "basic_sanitation", "basic_sanitation_training_with_covariates_v2.csv", "sanitation_basic"),
    (od, "open_defecation",  "open_defecation_training_with_covariates_v2.csv",  "open_defecation"),
]:
    add_data_flags(_df, _train, _jmp)
    _tab = data_availability_table(_df)
    print_section(f"90% PI WIDTH — BY DATA AVAILABILITY ({_name})", _tab)
    _tab.to_csv(versioned_path(OUTPUT_DIR, f"stats_pi_width_data_availability_{_name}.csv"), index=False)

    # Double data gap: neither survey nor JMP national estimate
    _dg = _df[~_df["in_training"] & ~_df["has_jmp"]]
    print(f"\nDOUBLE DATA GAP (no survey + no JMP) — {_name}")
    print(f"  districts:              {len(_dg)}")
    print(f"  countries:              {_dg[country_col].nunique()}")
    if "worldpop_sum" in _dg.columns:
        print(f"  population (millions):  {_dg['worldpop_sum'].sum()/1e6:.0f}")
    print(f"  median 90% PI width:    {_dg['width_90'].median()*100:.1f} %")
    print(f"  share in SSA + Oceania: "
          f"{100*_dg['sdg_region'].isin(['Sub-Saharan Africa', 'Oceania']).mean():.0f}%")

# -------------------------------------------------------
# 10.  Top 10 countries by widest prediction intervals
#      Ranked by median width_90 across Admin-1 regions
# -------------------------------------------------------

def top10_wide_pi(df, country_col):
    return (
        df.groupby(country_col)["width_90"]
        .agg(
            n_regions="count",
            min_width=lambda x: round(x.min() * 100, 1),
            median_width=lambda x: round(x.median() * 100, 1),
            max_width=lambda x: round(x.max() * 100, 1),
        )
        .reset_index()
        .sort_values("median_width", ascending=False)
        .head(10)
        .rename(columns={
            "min_width":    "min_width_%",
            "median_width": "median_width_%",
            "max_width":    "max_width_%",
        })
    )

bs_top10_pi = top10_wide_pi(bs, country_col)
od_top10_pi = top10_wide_pi(od, country_col)

print_section("TOP 10 COUNTRIES BY WIDEST 90% PI — BASIC SANITATION", bs_top10_pi)
print_section("TOP 10 COUNTRIES BY WIDEST 90% PI — OPEN DEFECATION", od_top10_pi)

bs_top10_pi.to_csv(versioned_path(OUTPUT_DIR, "stats_wide_pi_top10_BS.csv"), index=False)
od_top10_pi.to_csv(versioned_path(OUTPUT_DIR, "stats_wide_pi_top10_OD.csv"), index=False)

# -------------------------------------------------------
# 11.  Top 10 Admin-1 regions by widest prediction intervals
# -------------------------------------------------------

region_col = "NAME_1" if "NAME_1" in bs.columns else "region"

pi_cols = [country_col, region_col, "width_90", "pi90_lower", "pi90_upper", "median"]

def top10_wide_pi_regions(df, cols):
    available = [c for c in cols if c in df.columns]
    return (
        df[available]
        .assign(
            width_90_pct  = lambda x: (x["width_90"]   * 100).round(1),
            pi90_lower_pct= lambda x: (x["pi90_lower"] * 100).round(1),
            pi90_upper_pct= lambda x: (x["pi90_upper"] * 100).round(1),
            median_pct    = lambda x: (x["median"]      * 100).round(1),
        )
        .sort_values("width_90_pct", ascending=False)
        .head(10)
        .drop(columns=["width_90", "pi90_lower", "pi90_upper", "median"])
    )

bs_top10_regions = top10_wide_pi_regions(bs, pi_cols)
od_top10_regions = top10_wide_pi_regions(od, pi_cols)

print_section("TOP 10 ADMIN-1 REGIONS BY WIDEST 90% PI — BASIC SANITATION", bs_top10_regions)
print_section("TOP 10 ADMIN-1 REGIONS BY WIDEST 90% PI — OPEN DEFECATION",  od_top10_regions)

bs_top10_regions.to_csv(versioned_path(OUTPUT_DIR, "stats_wide_pi_top10_regions_BS.csv"), index=False)
od_top10_regions.to_csv(versioned_path(OUTPUT_DIR, "stats_wide_pi_top10_regions_OD.csv"), index=False)

# -------------------------------------------------------
# 12.  Overall totals
# -------------------------------------------------------

print(f"\n{'='*60}")
print("OVERALL TOTALS")
print('='*60)
print(f"  Basic sanitation — total Admin-1 regions:  {len(bs)}")
print(f"  Basic sanitation — total countries:       {bs[country_col].nunique()}")
print(f"  Open defecation  — total Admin-1 regions: {len(od)}")
print(f"  Open defecation  — total countries:       {od[country_col].nunique()}")
print(f"  BS global median prediction:              {bs['median'].median()*100:.1f}%")
print(f"  OD global median prediction:              {od['median'].median()*100:.1f}%")

print("\nAll statistics saved to:", OUTPUT_DIR, "(versioned _vN files)")
