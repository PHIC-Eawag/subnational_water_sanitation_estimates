# -------------------------------------------------------
# Drinking water / SMDW — TabPFN modelling pipeline
# Outcomes: smdw, ecoli_free, improved_source,
#           availability, accessibility
#
# Structure:
#   1–7   Setup, data prep, helpers
#   8     Stratified fold samplers (WQ pool / Other pool)
#   9     Feature set comparison (stratified CV)
#   10    Results summary
#   11    [MANUAL] Select final k per outcome
#   12–16 Final model per outcome (LOCO-CV)
#   17    Combined summary
#   18    Quantile predictions (LOCO-CV)
#   19    Final model: LMIC predictions (median + 90% PI)
# -------------------------------------------------------

from zmq import NULL
import gc
import os
import inspect
import warnings

import numpy as np
import pandas as pd
import tabpfn_client

from tabpfn_client import TabPFNRegressor
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

tabpfn_client.init()  # no-op after first login on this machine


# -------------------------------------------------------
# 1.  Paths
# -------------------------------------------------------

VERSION              = "v1"

DATA_DIR             = "data/processed/training_subcomponents"
CLUSTER_DIR          = "outputs/cluster_analysis/smdw"
PRED_COVARIATES_PATH = "data/processed/prediction/prediction_covariates_2024.csv"
OUTPUT_DIR           = "outputs/model_performance"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# -------------------------------------------------------
# 2.  Column names
# -------------------------------------------------------

TARGET_COL  = "outcome_value"
COUNTRY_COL = "country_cov"
OUTCOME_COL = "country_outcome"   # used for country exclusions
REGION_COL  = "HH7_region_outcome"
YEAR_COL    = "analysis_year"
WEIGHT_COL  = "n_psu_weight_scaled"
SDG_COL     = "sdg_region"
INCOME_COL  = "wb_income_group"


# -------------------------------------------------------
# 3.  Feature sets
#
# Full SMDW set (k = 104):
#   shared EO + country-level (99, same as sanitation)
#   + 5 JMP drinking water variables
# -------------------------------------------------------

ALL_EO_FEATURES = [
    "CGIAR_Aridity_Index", "CGIAR_PET",
    "CHELSA_BIO_Annual_Mean_Temperature", "CHELSA_BIO_Annual_Precipitation",
    "CHELSA_BIO_Precipitation_Seasonality",
    "CHELSA_BIO_Precipitation_of_Coldest_Quarter",
    "CHELSA_BIO_Precipitation_of_Driest_Month",
    "CHELSA_BIO_Precipitation_of_Driest_Quarter",
    "CHELSA_BIO_Precipitation_of_Warmest_Quarter",
    "CHELSA_BIO_Precipitation_of_Wettest_Month",
    "CHELSA_BIO_Precipitation_of_Wettest_Quarter",
    "CHELSA_BIO_Temperature_Annual_Range", "CHELSA_BIO_Temperature_Seasonality",
    "CIFOR_TropicalPeatlandExtent", "CSP_Global_Human_Modification",
    "ConsensusLandCoverClass_Barren",
    "ConsensusLandCoverClass_Cultivated_and_Managed_Vegetation",
    "ConsensusLandCoverClass_Deciduous_Broadleaf_Trees",
    "ConsensusLandCoverClass_Evergreen_Broadleaf_Trees",
    "ConsensusLandCoverClass_Evergreen_Deciduous_Needleleaf_Trees",
    "ConsensusLandCoverClass_Herbaceous_Vegetation",
    "ConsensusLandCoverClass_Mixed_Other_Trees",
    "ConsensusLandCoverClass_Open_Water",
    "ConsensusLandCoverClass_Regularly_Flooded_Vegetation",
    "ConsensusLandCoverClass_Shrubs", "ConsensusLandCoverClass_Snow_Ice",
    "ConsensusLandCoverClass_Urban_Builtup",
    "ConsensusLandCover_Human_Development_Percentage",
    "CrowtherLab_Tree_Density", "EarthEnvCloudCover_CloudForestPrediction",
    "EarthEnvTexture_CoOfVar_EVI", "EarthEnvTexture_Contrast_EVI",
    "EarthEnvTexture_Correlation_EVI", "EarthEnvTexture_Dissimilarity_EVI",
    "EarthEnvTexture_Entropy_EVI", "EarthEnvTexture_Evenness_EVI",
    "EarthEnvTexture_Homogeneity_EVI", "EarthEnvTexture_Maximum_EVI",
    "EarthEnvTexture_Range_EVI", "EarthEnvTexture_Shannon_Index",
    "EarthEnvTexture_Simpson_Index", "EarthEnvTexture_Std_EVI",
    "EarthEnvTexture_Uniformity_EVI", "EarthEnvTexture_Variance_EVI",
    "EarthEnvTopoMed_1stOrderPartialDerivEW",
    "EarthEnvTopoMed_1stOrderPartialDerivNS",
    "EarthEnvTopoMed_Eastness", "EarthEnvTopoMed_Elevation",
    "EarthEnvTopoMed_Roughness", "EarthEnvTopoMed_Slope",
    "EarthEnvTopoMed_TerrainRuggednessIndex", "EarthEnvTopoMed_TopoPositionIndex",
    "EsaCci_BurntAreasProbability",
    "FanEtAl_Depth_to_Water_Table_AnnualMean",
    "FanEtAl_Depth_to_Water_Table_AnnualSD",
    "GHS_Population_Density", "GLW3_RuminantsDistribution_downsampled10km",
    "GPWv4_Population_Density", "GiriEtAl_MangrovesExtent",
    "MODIS_EVI", "MODIS_NDVI", "MODIS_NPP",
    "PelletierEtAl_SoilAndSedimentaryDepositThicknesses",
    "SG_Absolute_depth_to_bedrock", "SG_Bulk_density_015cm",
    "SG_Depth_to_bedrock", "SG_H2O_Capacity_015cm",
    "SG_Saturated_H2O_Content_015cm",
    "TootchiEtAl_WetlandsRegularlyFlooded", "WCS_Human_Footprint_2009",
    "chirps_annual_precipitation", "era5_temperature_2m",
    "ghsl_built_surface", "ghsl_population", "ghsl_urban_frac",
    "jrc_building_height", "map_friction", "modis_evi", "modis_ndvi",
    "runoff_max_annualmax", "runoff_min_annualmin",
    "temperature_2m_max_annualmax", "viirs_average",
    "worldpop", "worldpop_sum", "ghsl_population_sum", "area_km2",
]

COUNTRY_LEVEL_FEATURES = [
    "gdp_per_capita_constant_2015_usd", "secondary_education_duration_years",
    "ww_collection_percent", "ww_treatment_percent", "ww_reuse_percent",
    "control_of_corruption", "governance_effectiveness", "political_stability",
    "regulatory_quality", "rule_of_law", "voice_and_accountability",
    "sanitation_basic", "open_defecation",
]

JMP_WATER_FEATURES = [
    "drinking_water_accessible_on_premises",
    "drinking_water_available_when_needed",
    "drinking_water_free_from_contamination",
    "drinking_water_piped",
    "drinking_water_non_piped",
]

ALL_FEATURES_K104 = ALL_EO_FEATURES + COUNTRY_LEVEL_FEATURES + JMP_WATER_FEATURES

K_VALUES = [5, 10, 15, 20, 30, 45, 90, 104]


def load_feature_set(k):
    """Load representative variables for cluster k. k=104 returns full list."""
    if k == 104:
        return ALL_FEATURES_K104
    path = os.path.join(CLUSTER_DIR, f"representative_variables_k{k}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Cluster file not found: {path}\nRun 01_cluster_analysis.qmd first."
        )
    features = pd.read_csv(path)["representative_variable"].dropna().tolist()
    valid    = [f for f in features if f in ALL_FEATURES_K104]
    dropped  = set(features) - set(valid)
    if dropped:
        warnings.warn(f"k={k}: features not in ALL_FEATURES_K104 dropped: {dropped}")
    return valid


feature_sets = {f"k{k}": load_feature_set(k) for k in K_VALUES}

print("Feature sets loaded:")
for label, feats in feature_sets.items():
    print(f"  {label}: {len(feats)} features")


# -------------------------------------------------------
# 4.  Tasks
#
# Two pools with different country sets and exclusions:
#   wq    — water-quality surveys: smdw, ecoli_free
#           Pakistan excluded
#   other — other surveys: improved_source, availability, accessibility
#           no exclusions
# -------------------------------------------------------

TASKS = {
    "smdw": {
        "filename":          "smdw_training_with_covariates.csv",
        "output_prefix":     "smdw",
        "exclude_countries": ["Pakistan"],
        "pool":              "wq",
    },
    "ecoli_free": {
        "filename":          "ecoli_free_training_with_covariates.csv",
        "output_prefix":     "ecoli_free",
        "exclude_countries": ["Pakistan"],
        "pool":              "wq",
    },
    "improved_source": {
        "filename":          "improved_source_training_with_covariates.csv",
        "output_prefix":     "improved_source",
        "exclude_countries": [],
        "pool":              "other",
    },
    "availability": {
        "filename":          "availability_training_with_covariates.csv",
        "output_prefix":     "availability",
        "exclude_countries": [],
        "pool":              "other",
    },
    "accessibility": {
        "filename":          "accessibility_training_with_covariates.csv",
        "output_prefix":     "accessibility",
        "exclude_countries": [],
        "pool":              "other",
    },
}


# -------------------------------------------------------
# 5.  Data preparation
# -------------------------------------------------------

def prepare_model_data(df, feature_cols, exclude_countries=None):
    """Clean and structure one training dataframe."""
    if exclude_countries:
        for country in exclude_countries:
            mask = df[OUTCOME_COL].astype(str).str.startswith(country, na=False)
            n = mask.sum()
            if n > 0:
                print(f"  Removed {n} {country} rows")
            df = df[~mask].copy()

    valid_features = [c for c in feature_cols if c in df.columns]
    n_skipped = len(feature_cols) - len(valid_features)
    if n_skipped:
        warnings.warn(f"  {n_skipped} feature(s) not in data — skipped")

    keep = valid_features + [
        TARGET_COL, COUNTRY_COL, REGION_COL, YEAR_COL,
        WEIGHT_COL, SDG_COL, INCOME_COL,
    ]
    keep     = [c for c in keep if c in df.columns]
    model_df = df[keep].copy()

    for col in valid_features + [TARGET_COL, WEIGHT_COL]:
        if col in model_df.columns:
            model_df[col] = pd.to_numeric(model_df[col], errors="coerce")

    model_df = model_df.dropna(
        subset=[TARGET_COL, COUNTRY_COL, REGION_COL, YEAR_COL, WEIGHT_COL]
    ).copy()
    model_df = model_df[model_df[WEIGHT_COL] > 0].copy()
    model_df = model_df.drop_duplicates(
        subset=[COUNTRY_COL, YEAR_COL, REGION_COL, TARGET_COL]
    ).copy()

    if model_df[COUNTRY_COL].nunique() < 2:
        raise ValueError("Need at least two countries for CV.")

    country_lookup = (
        model_df[[COUNTRY_COL]]
        .drop_duplicates()
        .sort_values(COUNTRY_COL)
        .reset_index(drop=True)
        .assign(country_fold=lambda x: np.arange(1, len(x) + 1))
    )
    model_df = model_df.merge(country_lookup, on=COUNTRY_COL, how="left")
    return model_df, valid_features


# -------------------------------------------------------
# 6.  Metrics helpers
# -------------------------------------------------------

def compute_metrics(y_true, y_pred):
    """Unweighted metrics — used for feature set comparison."""
    r      = y_true - y_pred
    ss_res = np.sum(r ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return {
        "mae":  float(np.mean(np.abs(r))),
        "rmse": float(np.sqrt(np.mean(r ** 2))),
        "r2":   float(1 - ss_res / ss_tot) if ss_tot > 0 else np.nan,
        "n":    len(y_true),
    }


def compute_metrics_full(y_true, y_pred, weights):
    """Weighted and unweighted metrics — used for final LOCO-CV."""
    has_var = len(np.unique(y_true)) > 1
    return {
        "weighted_mae":    mean_absolute_error(y_true, y_pred, sample_weight=weights),
        "weighted_rmse":   mean_squared_error(y_true, y_pred, sample_weight=weights) ** 0.5,
        "weighted_r2":     r2_score(y_true, y_pred, sample_weight=weights) if has_var else np.nan,
        "unweighted_mae":  mean_absolute_error(y_true, y_pred),
        "unweighted_rmse": mean_squared_error(y_true, y_pred) ** 0.5,
        "unweighted_r2":   r2_score(y_true, y_pred) if has_var else np.nan,
    }


# -------------------------------------------------------
# 7.  TabPFN fit helper
# -------------------------------------------------------

def clear_memory():
    gc.collect()


def fit_tabpfn(model, X_train, y_train, sample_weight):
    try:
        params = inspect.signature(model.fit).parameters
        supports_sw = "sample_weight" in params or any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()
        )
    except (TypeError, ValueError):
        supports_sw = False

    if supports_sw:
        try:
            model.fit(X_train, y_train, sample_weight=sample_weight)
            return model, True
        except TypeError:
            pass

    model.fit(X_train, y_train)
    return model, False


# -------------------------------------------------------
# 8.  Stratified fold samplers
#
# Two separate fold lists matching the two survey pools.
#
# WQ pool (smdw, ecoli_free):
#   Built from smdw training data; Pakistan excluded.
# Other pool (improved_source, availability, accessibility):
#   Built from improved_source training data; no exclusions.
#
# Both stratify by SDG region proportions from prediction
# space. High-income countries excluded from folds.
# -------------------------------------------------------

N_REPEATS     = 5
FOLD_FRACTION = 0.15

pred_cov = pd.read_csv(PRED_COVARIATES_PATH)

stratum_targets_base = (
    pred_cov[pred_cov[SDG_COL].notna()]
    .groupby(SDG_COL, as_index=False)
    .size()
    .rename(columns={"size": "n_pred_regions"})
    .assign(fraction=lambda d: d["n_pred_regions"] / d["n_pred_regions"].sum())
)


def build_country_strata(training_path, exclude_countries=None):
    df = pd.read_csv(training_path)
    if exclude_countries:
        for country in exclude_countries:
            df = df[~df[OUTCOME_COL].astype(str).str.startswith(country, na=False)]
    return (
        df.groupby(COUNTRY_COL, as_index=False)
        .agg(
            sdg_region      = (SDG_COL,    "first"),
            wb_income_group = (INCOME_COL, "first"),
            n_regions       = (COUNTRY_COL, "count"),
        )
    )


def make_stratum_targets(country_strata):
    total   = int(country_strata["n_regions"].sum())
    targets = stratum_targets_base.copy()
    targets["n_in_fold"] = (
        targets["fraction"] * FOLD_FRACTION * total
    ).round().astype(int)
    return targets, total


def sample_held_out_countries(country_strata, stratum_targets, seed_i=1):
    """
    Sample whole countries into held-out fold, stratum by stratum.
    Excludes high-income countries. Stops when n_in_fold reached per stratum.
    """
    rng      = np.random.default_rng(seed_i)
    held_out = []
    eligible = country_strata[country_strata["wb_income_group"] != "H"].copy()

    for _, row in stratum_targets.iterrows():
        stratum  = row[SDG_COL]
        target_n = int(row["n_in_fold"])

        pool = (eligible[eligible["sdg_region"] == stratum]
                .copy().reset_index(drop=True))
        if len(pool) == 0 or target_n == 0:
            continue

        sampled_n = 0
        sampled   = []

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


# ── WQ pool ───────────────────────────────────────────────────────────────────
print("\nBuilding WQ pool country strata (smdw, Pakistan excluded)...")
country_strata_wq = build_country_strata(
    os.path.join(DATA_DIR, TASKS["smdw"]["filename"]),
    exclude_countries=["Pakistan"],
)
stratum_targets_wq, total_wq = make_stratum_targets(country_strata_wq)

fold_country_lists_wq = [
    sample_held_out_countries(country_strata_wq, stratum_targets_wq, seed_i=i)
    for i in range(1, N_REPEATS + 1)
]

_smdw_raw = pd.read_csv(os.path.join(DATA_DIR, TASKS["smdw"]["filename"]))
_smdw_raw = _smdw_raw[
    ~_smdw_raw[OUTCOME_COL].astype(str).str.startswith("Pakistan", na=False)
]
print("WQ pool fold diagnostics:")
for i, countries in enumerate(fold_country_lists_wq, 1):
    n_reg = int(_smdw_raw[_smdw_raw[COUNTRY_COL].isin(countries)].shape[0])
    pct   = 100 * n_reg / total_wq
    print(f"  Fold {i}: {len(countries)} countries, {n_reg} regions ({pct:.1f}%)")


# ── Other pool ────────────────────────────────────────────────────────────────
print("\nBuilding Other pool country strata (improved_source, no exclusions)...")
country_strata_other = build_country_strata(
    os.path.join(DATA_DIR, TASKS["improved_source"]["filename"]),
)
stratum_targets_other, total_other = make_stratum_targets(country_strata_other)

fold_country_lists_other = [
    sample_held_out_countries(country_strata_other, stratum_targets_other, seed_i=i)
    for i in range(1, N_REPEATS + 1)
]

_impr_raw = pd.read_csv(os.path.join(DATA_DIR, TASKS["improved_source"]["filename"]))
print("Other pool fold diagnostics:")
for i, countries in enumerate(fold_country_lists_other, 1):
    n_reg = int(_impr_raw[_impr_raw[COUNTRY_COL].isin(countries)].shape[0])
    pct   = 100 * n_reg / total_other
    print(f"  Fold {i}: {len(countries)} countries, {n_reg} regions ({pct:.1f}%)")

FOLD_LISTS = {
    "wq":    fold_country_lists_wq,
    "other": fold_country_lists_other,
}


# -------------------------------------------------------
# 9.  Feature set comparison (stratified CV)
# -------------------------------------------------------

def run_one_fold(training_df, held_out_countries, features):
    """Train on non-held-out, predict on held-out. Return unweighted metrics."""
    train_df = training_df[~training_df[COUNTRY_COL].isin(held_out_countries)].copy()
    test_df  = training_df[ training_df[COUNTRY_COL].isin(held_out_countries)].copy()

    if len(test_df) == 0:
        return None

    valid = [f for f in features if f in train_df.columns]
    X_tr  = train_df[valid].to_numpy(dtype=float)
    y_tr  = train_df[TARGET_COL].to_numpy(dtype=float)
    w_tr  = train_df[WEIGHT_COL].to_numpy(dtype=float)
    X_te  = test_df[valid].to_numpy(dtype=float)
    y_te  = test_df[TARGET_COL].to_numpy(dtype=float)

    train_mask = ~np.isnan(X_tr).any(axis=1)
    test_mask  = ~np.isnan(X_te).any(axis=1)
    X_tr, y_tr, w_tr = X_tr[train_mask], y_tr[train_mask], w_tr[train_mask]
    X_te, y_te       = X_te[test_mask],  y_te[test_mask]

    if len(X_tr) == 0 or len(X_te) == 0:
        return None

    w_tr_norm = w_tr / w_tr.mean()
    model = TabPFNRegressor()
    model, _ = fit_tabpfn(model, X_tr, y_tr, sample_weight=w_tr_norm)
    preds = np.asarray(model.predict(X_te)).reshape(-1)

    del model; clear_memory()
    return compute_metrics(y_te, preds)


def run_feature_set_comparison(training_df, outcome_name, fold_country_lists):
    print(f"\n== Feature set comparison: {outcome_name} ==")
    rows = []

    for k_label, features in feature_sets.items():
        print(f"  {k_label} ({len(features)} features)", end="", flush=True)
        repeat_results = []

        for i, countries in enumerate(fold_country_lists):
            result = run_one_fold(training_df, countries, features)
            if result is not None:
                result["repeat_i"] = i + 1
                repeat_results.append(result)
            print(".", end="", flush=True)
        print()

        if not repeat_results:
            continue

        rep_df = pd.DataFrame(repeat_results)
        rows.append({
            "outcome":     outcome_name,
            "feature_set": k_label,
            "n_features":  len(features),
            "mean_r2":     rep_df["r2"].mean(),
            "sd_r2":       rep_df["r2"].std(),
            "mean_mae":    rep_df["mae"].mean(),
            "sd_mae":      rep_df["mae"].std(),
            "mean_rmse":   rep_df["rmse"].mean(),
            "sd_rmse":     rep_df["rmse"].std(),
            "n_repeats":   len(rep_df),
        })

    return pd.DataFrame(rows)


print("\nLoading training data for feature set comparison...")
all_comparisons = []
for outcome_name, cfg in TASKS.items():
    training_df, _ = prepare_model_data(
        pd.read_csv(os.path.join(DATA_DIR, cfg["filename"])),
        feature_cols=ALL_FEATURES_K104,
        exclude_countries=cfg["exclude_countries"],
    )
    result = run_feature_set_comparison(
        training_df, outcome_name, FOLD_LISTS[cfg["pool"]]
    )
    all_comparisons.append(result)

cv_comparison = pd.concat(all_comparisons, ignore_index=True)


# -------------------------------------------------------
# 10. Comparison results
# -------------------------------------------------------

print("\nStratified CV — feature set comparison:")
print(
    cv_comparison
    .sort_values(["outcome", "mean_r2"], ascending=[True, False])
    .to_string(index=False)
)

cv_comparison.to_csv(
    os.path.join(OUTPUT_DIR, f"smdw_tabpfn_feature_set_cv_comparison_{VERSION}.csv"),
    index=False,
)
print(f"\nSaved: {OUTPUT_DIR}/smdw_tabpfn_feature_set_cv_comparison_{VERSION}.csv")


# -------------------------------------------------------
# 11. [MANUAL] Select final k per outcome
#
# Inspect the table above, set all five values below,
# then run Sections 12–16.
# -------------------------------------------------------

FINAL_K_SMDW             = 104   # e.g. 20
FINAL_K_ECOLI_FREE       = 104   # e.g. 15
FINAL_K_IMPROVED_SOURCE  = 30   # e.g. 30
FINAL_K_AVAILABILITY     = 90   # e.g. 20
FINAL_K_ACCESSIBILITY    = 15   # e.g. 20

_final_ks = {
    "smdw":            FINAL_K_SMDW,
    "ecoli_free":      FINAL_K_ECOLI_FREE,
    "improved_source": FINAL_K_IMPROVED_SOURCE,
    "availability":    FINAL_K_AVAILABILITY,
    "accessibility":   FINAL_K_ACCESSIBILITY,
}
if any(v is None for v in _final_ks.values()):
    raise ValueError(
        "Set all five FINAL_K_* values before running Sections 12–16.\n"
        + "\n".join(f"  {k}: {v}" for k, v in _final_ks.items())
    )

for outcome_name, k in _final_ks.items():
    print(f"  {outcome_name}: k={k} ({len(feature_sets[f'k{k}'])} features)")


# -------------------------------------------------------
# 12. LOCO-CV helper + per-outcome runner
# -------------------------------------------------------

def run_loco_cv(model_df, feature_cols, outcome_name, final_k):
    """PSU-weighted LOCO-CV with TabPFN."""
    X       = model_df[feature_cols].to_numpy(dtype=float)
    y       = model_df[TARGET_COL].to_numpy(dtype=float)
    groups  = model_df["country_fold"].to_numpy()
    weights = model_df[WEIGHT_COL].to_numpy(dtype=float)

    oof_preds   = np.full(len(model_df), np.nan)
    logo        = LeaveOneGroupOut()
    fold_rows   = []
    used_sw_all = []

    for fold, (train_idx, val_idx) in enumerate(
        logo.split(X, y, groups=groups), start=1
    ):
        held_out = model_df.iloc[val_idx][COUNTRY_COL].iloc[0]
        print(f"  Fold {fold:>3d} | held-out: {held_out}")

        X_tr, y_tr   = X[train_idx], y[train_idx]
        X_val, y_val = X[val_idx],   y[val_idx]
        w_tr         = weights[train_idx]
        w_tr_norm    = w_tr / w_tr.mean()

        model = TabPFNRegressor()
        model, used_sw = fit_tabpfn(model, X_tr, y_tr, sample_weight=w_tr_norm)
        used_sw_all.append(used_sw)

        preds = np.asarray(model.predict(X_val)).reshape(-1)
        oof_preds[val_idx] = preds

        del model; clear_memory()

        fold_rows.append({
            "outcome":          outcome_name,
            "fold":             fold,
            "held_out_country": held_out,
            "n_train_rows":     len(train_idx),
            "n_val_rows":       len(val_idx),
            **compute_metrics(y_val, preds),
        })

    if np.isnan(oof_preds).any():
        raise RuntimeError(
            f"Missing OOF predictions: {np.isnan(oof_preds).sum()} rows"
        )

    fold_df = pd.DataFrame(fold_rows)

    overall_df = pd.DataFrame([{
        "outcome":               outcome_name,
        "model":                 "TabPFN",
        "feature_set":           f"k{final_k}",
        "n_features":            len(feature_cols),
        "n_rows":                len(y),
        "n_countries":           model_df[COUNTRY_COL].nunique(),
        "used_training_weights": all(used_sw_all),
        **compute_metrics_full(y, oof_preds, weights),
    }])

    oof_df = model_df[
        [COUNTRY_COL, REGION_COL, YEAR_COL, TARGET_COL, WEIGHT_COL, "country_fold"]
    ].copy()
    oof_df.insert(0, "outcome", outcome_name)
    oof_df["pred_tabpfn"]      = oof_preds
    oof_df["error_tabpfn"]     = oof_df[TARGET_COL] - oof_preds
    oof_df["abs_error_tabpfn"] = np.abs(oof_df[TARGET_COL] - oof_preds)

    return fold_df, overall_df, oof_df


def run_and_save_loco(outcome_name, final_k):
    """Prepare data, run LOCO-CV, print and save results."""
    cfg = TASKS[outcome_name]
    print(f"\n{'='*60}")
    print(f"Final model: {outcome_name}  (k={final_k})")
    print(f"{'='*60}")

    model_df, feature_cols = prepare_model_data(
        pd.read_csv(os.path.join(DATA_DIR, cfg["filename"])),
        feature_cols=feature_sets[f"k{final_k}"],
        exclude_countries=cfg["exclude_countries"],
    )

    fold_df, overall_df, oof_df = run_loco_cv(
        model_df, feature_cols, outcome_name, final_k
    )

    print("\n  LOCO-CV metrics:")
    print(overall_df[[
        "outcome", "feature_set", "n_rows", "n_features", "n_countries",
        "unweighted_mae", "unweighted_rmse", "unweighted_r2",
    ]].to_string(index=False))

    prefix = cfg["output_prefix"]
    fold_df.to_csv(
        os.path.join(OUTPUT_DIR,
                     f"{prefix}_tabpfn_loco_by_country_k{final_k}_{VERSION}.csv"),
        index=False,
    )
    overall_df.to_csv(
        os.path.join(OUTPUT_DIR,
                     f"{prefix}_tabpfn_loco_overall_k{final_k}_{VERSION}.csv"),
        index=False,
    )
    oof_df.to_csv(
        os.path.join(OUTPUT_DIR,
                     f"{prefix}_tabpfn_loco_oof_k{final_k}_{VERSION}.csv"),
        index=False,
    )
    print(f"  Saved: {OUTPUT_DIR}/{prefix}_tabpfn_loco_*_k{final_k}_{VERSION}.csv")
    return overall_df


# ── Final models ──────────────────────────────────────────────────────────────
smdw_overall         = run_and_save_loco("smdw",            FINAL_K_SMDW)
ecoli_overall        = run_and_save_loco("ecoli_free",      FINAL_K_ECOLI_FREE)
improved_overall     = run_and_save_loco("improved_source", FINAL_K_IMPROVED_SOURCE)
availability_overall = run_and_save_loco("availability",    FINAL_K_AVAILABILITY)
accessibility_overall = run_and_save_loco("accessibility",  FINAL_K_ACCESSIBILITY)


# -------------------------------------------------------
# 17. Combined summary
# -------------------------------------------------------

summary_df = pd.concat([
    smdw_overall, ecoli_overall, improved_overall,
    availability_overall, accessibility_overall,
], ignore_index=True)

summary_path = os.path.join(OUTPUT_DIR, f"smdw_tabpfn_loco_summary_{VERSION}.csv")
summary_df.to_csv(summary_path, index=False)

print(f"\n{'='*60}")
print("SMDW / Drinking water — TabPFN final LOCO-CV summary:")
print(summary_df[[
    "outcome", "feature_set", "n_rows", "n_features", "n_countries",
    "unweighted_mae", "unweighted_rmse", "unweighted_r2",
    "weighted_mae",   "weighted_rmse",   "weighted_r2",
]].to_string(index=False))
print(f"\nSaved: {summary_path}")


# -------------------------------------------------------
# 18. TabPFN quantile predictions (LOCO-CV)
# -------------------------------------------------------

QUANTILE_LEVELS = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]

QUANTILE_TASKS = {
    "smdw":            FINAL_K_SMDW,
    "ecoli_free":      FINAL_K_ECOLI_FREE,
    "improved_source": FINAL_K_IMPROVED_SOURCE,
    "availability":    FINAL_K_AVAILABILITY,
    "accessibility":   FINAL_K_ACCESSIBILITY,
}


def run_loco_cv_tabpfn_quantiles(model_df, feature_cols, outcome_name,
                                 quantiles=None):
    if quantiles is None:
        quantiles = QUANTILE_LEVELS

    X       = model_df[feature_cols].to_numpy(dtype=float)
    y       = model_df[TARGET_COL].to_numpy(dtype=float)
    groups  = model_df["country_fold"].to_numpy()
    weights = model_df[WEIGHT_COL].to_numpy(dtype=float)

    n_q   = len(quantiles)
    oof_q = np.full((len(model_df), n_q), np.nan)
    logo  = LeaveOneGroupOut()

    for fold, (train_idx, val_idx) in enumerate(
        logo.split(X, y, groups=groups), start=1
    ):
        held_out  = model_df.iloc[val_idx][COUNTRY_COL].iloc[0]
        print(f"  Fold {fold:>3d} | held-out: {held_out}")

        X_tr, y_tr = X[train_idx], y[train_idx]
        X_val      = X[val_idx]
        w_tr       = weights[train_idx]
        w_tr_norm  = w_tr / w_tr.mean()

        model = TabPFNRegressor()
        model, _ = fit_tabpfn(model, X_tr, y_tr, sample_weight=w_tr_norm)

        try:
            q_preds = model.predict(
                X_val, output_type="quantiles", quantiles=quantiles,
            )
            q_preds = np.asarray(q_preds)
            if q_preds.ndim == 2 and q_preds.shape[0] == n_q and q_preds.shape[1] != n_q:
                q_preds = q_preds.T
        except (TypeError, AttributeError) as exc:
            del model; clear_memory()
            raise RuntimeError(
                "TabPFN client does not support quantile output in this version."
            ) from exc

        oof_q[val_idx] = q_preds
        del model; clear_memory()

    q_col_names = [f"q{int(q * 100):02d}" for q in quantiles]
    oof_df = model_df[
        [COUNTRY_COL, REGION_COL, YEAR_COL, TARGET_COL, WEIGHT_COL, "country_fold"]
    ].copy().reset_index(drop=True)
    oof_df.insert(0, "outcome", outcome_name)
    for i, col in enumerate(q_col_names):
        oof_df[col] = oof_q[:, i]

    coverage_rows = []
    for (country, fold_id), grp in oof_df.groupby([COUNTRY_COL, "country_fold"]):
        y_g = grp[TARGET_COL].to_numpy(dtype=float)
        w_g = grp[WEIGHT_COL].to_numpy(dtype=float)
        for lo_q, hi_q, label in [
            ("q05", "q95", "90pct"), ("q10", "q90", "80pct"),
        ]:
            lo      = grp[lo_q].to_numpy(dtype=float)
            hi      = grp[hi_q].to_numpy(dtype=float)
            covered = (y_g >= lo) & (y_g <= hi)
            coverage_rows.append({
                "outcome":            outcome_name,
                "country_fold":       int(fold_id),
                "held_out_country":   country,
                "interval":           label,
                "n_val":              len(y_g),
                "mean_width":         round(float((hi - lo).mean()), 6),
                "empirical_coverage": round(float(covered.mean()), 4),
                "weighted_coverage":  round(
                    float(np.average(covered.astype(float), weights=w_g)), 4
                ),
            })

    return oof_df, pd.DataFrame(coverage_rows)


print(f"\n{'='*60}")
print("Section 18 — TabPFN quantile predictions (LOCO CV)")
print(f"{'='*60}")

for outcome_name, final_k in QUANTILE_TASKS.items():
    cfg    = TASKS[outcome_name]
    prefix = cfg["output_prefix"]
    print(f"\n  Outcome: {outcome_name}  (k={final_k})")

    model_df, feature_cols = prepare_model_data(
        pd.read_csv(os.path.join(DATA_DIR, cfg["filename"])),
        feature_cols=feature_sets[f"k{final_k}"],
        exclude_countries=cfg["exclude_countries"],
    )

    try:
        q_oof_df, q_cov_df = run_loco_cv_tabpfn_quantiles(
            model_df, feature_cols, outcome_name
        )
        q_oof_df.to_csv(
            os.path.join(OUTPUT_DIR, f"{prefix}_tabpfn_quantile_oof_{VERSION}.csv"),
            index=False,
        )
        q_cov_df.to_csv(
            os.path.join(OUTPUT_DIR,
                         f"{prefix}_tabpfn_quantile_coverage_by_country_{VERSION}.csv"),
            index=False,
        )
        if not q_cov_df.empty:
            print(
                q_cov_df.groupby("interval")[["empirical_coverage", "mean_width"]]
                .mean().round(4).to_string()
            )
    except RuntimeError as exc:
        warnings.warn(f"  Quantile prediction skipped for {outcome_name}: {exc}")
        print("  → Use CQR for uncertainty intervals.")


# -------------------------------------------------------
# 19. Final model predictions across LMICs
#
# Trains TabPFN on ALL training data (every country retained)
# then predicts across LMIC locations in the prediction dataset
# (same file used for cluster analysis and fold stratification).
#
# Outputs per outcome:
#   - median        (q50)
#   - pi90_lower    (q05)
#   - pi90_upper    (q95)
#
# High-income countries (wb_income_group == "H") are excluded
# from the prediction set; all income groups are retained in
# training (consistent with earlier modelling stages).
#
# Note: model_df is reloaded here per outcome because
# run_and_save_loco() does not retain it in memory.
# -------------------------------------------------------

PRED_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "predictions")
os.makedirs(PRED_OUTPUT_DIR, exist_ok=True)

# JMP water features are also country-level (joined in 05_prepare_prediction_data.qmd)
# and must be present in the prediction data alongside COUNTRY_LEVEL_FEATURES.
REQUIRED_PRED_COLS = {
    "features":       COUNTRY_LEVEL_FEATURES + JMP_WATER_FEATURES,
    "identifiers":    ["GID_1", "NAME_0", "NAME_1"],
    "stratification": ["sdg_region", "wb_income_group", "fragile_context"],
}

# Reload and validate prediction data
pred_all = pd.read_csv(PRED_COVARIATES_PATH)

_pred_cols          = set(pred_all.columns)
_missing_features   = [c for c in REQUIRED_PRED_COLS["features"]   if c not in _pred_cols]
_missing_ids        = [c for c in REQUIRED_PRED_COLS["identifiers"] if c not in _pred_cols]
_missing_strat      = [c for c in REQUIRED_PRED_COLS["stratification"] if c not in _pred_cols]

if _missing_features:
    raise ValueError(
        f"Country-level / JMP covariates missing from prediction data.\n"
        f"These must be joined in 05_prepare_prediction_data.qmd:\n"
        f"  {_missing_features}"
    )
if _missing_ids:
    raise ValueError(
        f"Identifier columns missing from prediction data "
        f"(needed for shapefile join / mapping):\n  {_missing_ids}"
    )
if _missing_strat:
    raise ValueError(
        f"Stratification columns missing from prediction data "
        f"(needed for SDG region / income group / fragile context analysis):\n"
        f"  {_missing_strat}"
    )

pred_lmic = pred_all[pred_all[INCOME_COL] != "H"].copy().reset_index(drop=True)

print(f"\nPrediction data: {len(pred_all):,} total rows → "
      f"{len(pred_lmic):,} LMIC rows "
      f"({pred_lmic[COUNTRY_COL].nunique() if COUNTRY_COL in pred_lmic.columns else '?'} countries)")

PRED_QUANTILES = [0.05, 0.50, 0.95]

# Map each outcome to its final k value and feature list
PRED_TASKS_DW = {
    "smdw":            {"final_k": FINAL_K_SMDW,            "prefix": "smdw"},
    "ecoli_free":      {"final_k": FINAL_K_ECOLI_FREE,      "prefix": "ecoli_free"},
    "improved_source": {"final_k": FINAL_K_IMPROVED_SOURCE, "prefix": "improved_source"},
    "availability":    {"final_k": FINAL_K_AVAILABILITY,    "prefix": "availability"},
    "accessibility":   {"final_k": FINAL_K_ACCESSIBILITY,   "prefix": "accessibility"},
}


def predict_lmics_dw(outcome_name, cfg_task, cfg_pred, pred_df,
                     quantiles=None):
    """
    Train TabPFN on the complete training dataset for one drinking water
    outcome, then generate quantile predictions for every LMIC row in pred_df.

    Parameters
    ----------
    outcome_name : string label for this outcome
    cfg_task     : entry from TASKS dict (filename, exclude_countries)
    cfg_pred     : entry from PRED_TASKS_DW dict (final_k, prefix)
    pred_df      : LMIC prediction dataframe
    quantiles    : list of quantile levels; defaults to [0.05, 0.50, 0.95]

    Returns
    -------
    DataFrame with lead identifier/stratification/prediction columns first,
    followed by all remaining covariate columns.
    """
    if quantiles is None:
        quantiles = PRED_QUANTILES

    final_k      = cfg_pred["final_k"]
    feature_cols = feature_sets[f"k{final_k}"]

    # ── Reload and prepare full training data ───────────────────────────
    model_df, valid_train = prepare_model_data(
        pd.read_csv(os.path.join(DATA_DIR, cfg_task["filename"])),
        feature_cols=feature_cols,
        exclude_countries=cfg_task["exclude_countries"],
    )

    # TabPFN handles NaN features natively — only drop rows with missing
    # target or weight values.
    X_tr = model_df[valid_train].to_numpy(dtype=float)
    y_tr = model_df[TARGET_COL].to_numpy(dtype=float)
    w_tr = model_df[WEIGHT_COL].to_numpy(dtype=float)

    valid_mask       = ~(np.isnan(y_tr) | np.isnan(w_tr))
    X_tr, y_tr, w_tr = X_tr[valid_mask], y_tr[valid_mask], w_tr[valid_mask]
    w_norm           = w_tr / w_tr.mean()

    print(f"  Training on {len(X_tr):,} rows "
          f"({model_df[COUNTRY_COL].nunique()} countries) …")

    model = TabPFNRegressor()
    model, used_sw = fit_tabpfn(model, X_tr, y_tr, sample_weight=w_norm)
    print(f"  Sample weights used: {used_sw}")

    # ── Validate prediction features ────────────────────────────────────
    valid_pred          = [f for f in valid_train if f in pred_df.columns]
    missing             = set(valid_train) - set(valid_pred)
    missing_country_lvl = [f for f in missing
                           if f in COUNTRY_LEVEL_FEATURES + JMP_WATER_FEATURES]
    missing_eo          = [f for f in missing
                           if f not in COUNTRY_LEVEL_FEATURES + JMP_WATER_FEATURES]

    if missing_country_lvl:
        raise ValueError(
            f"{outcome_name}: country-level / JMP covariates missing from "
            f"prediction data. Join them in 05_prepare_prediction_data.qmd:\n"
            f"  {missing_country_lvl}"
        )
    if missing_eo:
        warnings.warn(
            f"{outcome_name}: {len(missing_eo)} EO feature(s) absent from "
            f"prediction data — excluded from model input: {missing_eo}"
        )

    # ── Predict ─────────────────────────────────────────────────────────
    X_pred      = pred_df[valid_pred].to_numpy(dtype=float)
    q_col_names = [f"q{int(q * 100):02d}" for q in quantiles]
    out_df      = pred_df.copy().reset_index(drop=True)

    try:
        q_preds = model.predict(
            X_pred, output_type="quantiles", quantiles=quantiles,
        )
        q_preds = np.asarray(q_preds)
        if (q_preds.ndim == 2
                and q_preds.shape[0] == len(quantiles)
                and q_preds.shape[1] != len(quantiles)):
            q_preds = q_preds.T
    except (TypeError, AttributeError) as exc:
        del model; clear_memory()
        raise RuntimeError(
            "TabPFN client does not support quantile output in this version."
        ) from exc

    for i, col in enumerate(q_col_names):
        out_df[col] = q_preds[:, i]

    del model; clear_memory()

    # ── Rename and reorder columns ───────────────────────────────────────
    out_df = out_df.rename(columns={
        "q05": "pi90_lower",
        "q50": "median",
        "q95": "pi90_upper",
    })
    out_df.insert(0, "outcome", outcome_name)

    _IDENTIFIERS    = ["GID_1", "NAME_0", "NAME_1"]
    _STRATIFICATION = ["sdg_region", "wb_income_group", "fragile_context"]
    _PREDICTIONS    = ["median", "pi90_lower", "pi90_upper"]

    lead_cols  = (
        ["outcome"]
        + [c for c in _IDENTIFIERS    if c in out_df.columns]
        + [c for c in _STRATIFICATION if c in out_df.columns]
        + [c for c in _PREDICTIONS    if c in out_df.columns]
    )
    other_cols = [c for c in out_df.columns if c not in lead_cols]
    return out_df[lead_cols + other_cols]


print(f"\n{'='*60}")
print("Section 19 — Final model: LMIC predictions (drinking water)")
print(f"{'='*60}")

for outcome_name, cfg_pred in PRED_TASKS_DW.items():
    cfg_task = TASKS[outcome_name]
    print(f"\n  Outcome: {outcome_name}  (k={cfg_pred['final_k']})")
    try:
        pred_out = predict_lmics_dw(
            outcome_name=outcome_name,
            cfg_task=cfg_task,
            cfg_pred=cfg_pred,
            pred_df=pred_lmic,
        )
        out_path = os.path.join(
            PRED_OUTPUT_DIR,
            f"{cfg_pred['prefix']}_tabpfn_lmic_predictions_{VERSION}.csv",
        )
        pred_out.to_csv(out_path, index=False)
        n_valid  = pred_out["median"].notna().sum()
        pi_width = (pred_out["pi90_upper"] - pred_out["pi90_lower"]).mean()
        print(f"  Saved: {out_path}  ({n_valid:,} / {len(pred_out):,} rows predicted)")
        print(f"  Median range : [{pred_out['median'].min():.3f}, "
              f"{pred_out['median'].max():.3f}]")
        print(f"  Mean PI90 width: {pi_width:.3f}")
    except RuntimeError as exc:
        warnings.warn(f"  Prediction skipped for {outcome_name}: {exc}")
