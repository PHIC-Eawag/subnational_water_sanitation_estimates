# -------------------------------------------------------
# Sanitation — TabPFN modelling pipeline
# Outcomes: basic_sanitation, open_defecation
#
# Structure:
#   1–7   Setup, data prep, helpers
#   8     Stratified fold sampler
#   9     Feature set comparison (stratified CV)
#   10    Results summary
#   11    [MANUAL] Select final k per outcome
#   12    Final model — basic sanitation (LOCO-CV)
#   13    Final model — open defecation (LOCO-CV)
#   14    Combined summary
#   15+   Quantile predictions and uncertainty
# -------------------------------------------------------

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

DATA_DIR             = "data/training_subcomponents"
CLUSTER_DIR          = "outputs/03b_cluster_analysis/sanitation"
PRED_COVARIATES_PATH = "data/prediction/prediction_covariates_2024.csv"
OUTPUT_DIR           = "outputs/04_model_performance"
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

ALL_FEATURES_K100 = ALL_EO_FEATURES + COUNTRY_LEVEL_FEATURES

K_VALUES = [5, 10, 15, 20, 30, 45, 90, 100]


def load_feature_set(k):
    """Load representative variables for cluster k. k=100 returns full list."""
    if k == 100:
        return ALL_FEATURES_K100
    path = os.path.join(CLUSTER_DIR, f"representative_variables_k{k}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Cluster file not found: {path}\nRun 01_cluster_analysis.qmd first."
        )
    features = pd.read_csv(path)["representative_variable"].dropna().tolist()
    valid    = [f for f in features if f in ALL_FEATURES_K100]
    dropped  = set(features) - set(valid)
    if dropped:
        warnings.warn(f"k={k}: features not in ALL_FEATURES_K100 dropped: {dropped}")
    return valid


feature_sets = {f"k{k}": load_feature_set(k) for k in K_VALUES}

print("Feature sets loaded:")
for label, feats in feature_sets.items():
    print(f"  {label}: {len(feats)} features")


# -------------------------------------------------------
# 4.  Tasks
# -------------------------------------------------------

TASKS = {
    "basic_sanitation": {
        "filename":          "basic_sanitation_training_with_covariates.csv",
        "output_prefix":     "basic_sanitation",
        "exclude_countries": ["Indonesia"],
    },
    "open_defecation": {
        "filename":          "open_defecation_training_with_covariates.csv",
        "output_prefix":     "open_defecation",
        "exclude_countries": [],
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
# 8.  Stratified fold sampler
#
# Mirrors 01_modelling_sanitation_RF.qmd:
# - Stratum targets from prediction space (SDG region proportions)
# - Sample whole countries per stratum without replacement
# - Exclude high-income countries (wb_income_group == 'H')
# - N_REPEATS independent folds, shared across both outcomes
# -------------------------------------------------------

N_REPEATS     = 5
FOLD_FRACTION = 0.15

pred_cov = pd.read_csv(PRED_COVARIATES_PATH)

stratum_targets = (
    pred_cov[pred_cov[SDG_COL].notna()]
    .groupby(SDG_COL, as_index=False)
    .size()
    .rename(columns={"size": "n_pred_regions"})
    .assign(fraction=lambda d: d["n_pred_regions"] / d["n_pred_regions"].sum())
)

# Country strata from basic sanitation training data
_bs_raw = pd.read_csv(os.path.join(DATA_DIR, TASKS["basic_sanitation"]["filename"]))
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


def sample_held_out_countries(country_strata, stratum_targets, seed_i=1):
    """
    Sample whole countries into the held-out fold, stratum by stratum.
    - High-income countries excluded from folds.
    - Countries drawn without replacement within each stratum.
    - Stops when cumulative regions >= n_in_fold for that stratum.
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


fold_country_lists = [
    sample_held_out_countries(country_strata, stratum_targets, seed_i=i)
    for i in range(1, N_REPEATS + 1)
]

print("\nFold diagnostics:")
for i, countries in enumerate(fold_country_lists, 1):
    n_reg = int(_bs_raw[_bs_raw[COUNTRY_COL].isin(countries)].shape[0])
    pct   = 100 * n_reg / total_train_regions
    print(f"  Fold {i}: {len(countries)} countries, {n_reg} regions ({pct:.1f}%)")


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


def run_feature_set_comparison(training_df, outcome_name):
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
_bs_df, _ = prepare_model_data(
    pd.read_csv(os.path.join(DATA_DIR, TASKS["basic_sanitation"]["filename"])),
    feature_cols=ALL_FEATURES_K100,
    exclude_countries=TASKS["basic_sanitation"]["exclude_countries"],
)
_od_df, _ = prepare_model_data(
    pd.read_csv(os.path.join(DATA_DIR, TASKS["open_defecation"]["filename"])),
    feature_cols=ALL_FEATURES_K100,
    exclude_countries=TASKS["open_defecation"]["exclude_countries"],
)

comparison_bs = run_feature_set_comparison(_bs_df, "basic_sanitation")
comparison_od = run_feature_set_comparison(_od_df, "open_defecation")
cv_comparison = pd.concat([comparison_bs, comparison_od], ignore_index=True)


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
    os.path.join(OUTPUT_DIR, "tabpfn_feature_set_cv_comparison.csv"),
    index=False,
)
print(f"\nSaved: {OUTPUT_DIR}/tabpfn_feature_set_cv_comparison.csv")


# -------------------------------------------------------
# 11. [MANUAL] Select final k per outcome
#
# Inspect the table above, set the two values below,
# then run Sections 12 and 13.
# -------------------------------------------------------

FINAL_K_BASIC_SANITATION = 100   # e.g. 20
FINAL_K_OPEN_DEFECATION  = 100   # e.g. 15

if FINAL_K_BASIC_SANITATION is None or FINAL_K_OPEN_DEFECATION is None:
    raise ValueError(
        "Set FINAL_K_BASIC_SANITATION and FINAL_K_OPEN_DEFECATION "
        "before running Sections 12 and 13."
    )

final_features_bs = feature_sets[f"k{FINAL_K_BASIC_SANITATION}"]
final_features_od = feature_sets[f"k{FINAL_K_OPEN_DEFECATION}"]

print(f"\nBasic sanitation: k={FINAL_K_BASIC_SANITATION} "
      f"({len(final_features_bs)} features)")
print(f"Open defecation:  k={FINAL_K_OPEN_DEFECATION} "
      f"({len(final_features_od)} features)")


# -------------------------------------------------------
# 12. LOCO-CV helper
# -------------------------------------------------------

def run_loco_cv(model_df, feature_cols, outcome_name, final_k):
    """PSU-weighted LOCO-CV with TabPFN. Reports weighted + unweighted metrics."""
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


# -------------------------------------------------------
# 13. Final model — basic sanitation
# -------------------------------------------------------

print(f"\n{'='*60}")
print(f"Final model: basic_sanitation  (k={FINAL_K_BASIC_SANITATION})")
print(f"{'='*60}")

bs_model_df, bs_features = prepare_model_data(
    pd.read_csv(os.path.join(DATA_DIR, TASKS["basic_sanitation"]["filename"])),
    feature_cols=final_features_bs,
    exclude_countries=TASKS["basic_sanitation"]["exclude_countries"],
)

bs_fold_df, bs_overall_df, bs_oof_df = run_loco_cv(
    bs_model_df, bs_features, "basic_sanitation", FINAL_K_BASIC_SANITATION
)

print("\n  LOCO-CV metrics:")
print(bs_overall_df[[
    "outcome", "feature_set", "n_rows", "n_features", "n_countries",
    "unweighted_mae", "unweighted_rmse", "unweighted_r2",
]].to_string(index=False))

_prefix = TASKS["basic_sanitation"]["output_prefix"]
bs_fold_df.to_csv(
    os.path.join(OUTPUT_DIR,
                 f"{_prefix}_tabpfn_loco_by_country_k{FINAL_K_BASIC_SANITATION}.csv"),
    index=False,
)
bs_overall_df.to_csv(
    os.path.join(OUTPUT_DIR,
                 f"{_prefix}_tabpfn_loco_overall_k{FINAL_K_BASIC_SANITATION}.csv"),
    index=False,
)
bs_oof_df.to_csv(
    os.path.join(OUTPUT_DIR,
                 f"{_prefix}_tabpfn_loco_oof_k{FINAL_K_BASIC_SANITATION}.csv"),
    index=False,
)


# -------------------------------------------------------
# 14. Final model — open defecation
# -------------------------------------------------------

print(f"\n{'='*60}")
print(f"Final model: open_defecation  (k={FINAL_K_OPEN_DEFECATION})")
print(f"{'='*60}")

od_model_df, od_features = prepare_model_data(
    pd.read_csv(os.path.join(DATA_DIR, TASKS["open_defecation"]["filename"])),
    feature_cols=final_features_od,
    exclude_countries=TASKS["open_defecation"]["exclude_countries"],
)

od_fold_df, od_overall_df, od_oof_df = run_loco_cv(
    od_model_df, od_features, "open_defecation", FINAL_K_OPEN_DEFECATION
)

print("\n  LOCO-CV metrics:")
print(od_overall_df[[
    "outcome", "feature_set", "n_rows", "n_features", "n_countries",
    "unweighted_mae", "unweighted_rmse", "unweighted_r2",
]].to_string(index=False))

_prefix = TASKS["open_defecation"]["output_prefix"]
od_fold_df.to_csv(
    os.path.join(OUTPUT_DIR,
                 f"{_prefix}_tabpfn_loco_by_country_k{FINAL_K_OPEN_DEFECATION}.csv"),
    index=False,
)
od_overall_df.to_csv(
    os.path.join(OUTPUT_DIR,
                 f"{_prefix}_tabpfn_loco_overall_k{FINAL_K_OPEN_DEFECATION}.csv"),
    index=False,
)
od_oof_df.to_csv(
    os.path.join(OUTPUT_DIR,
                 f"{_prefix}_tabpfn_loco_oof_k{FINAL_K_OPEN_DEFECATION}.csv"),
    index=False,
)


# -------------------------------------------------------
# 15. Combined summary
# -------------------------------------------------------

summary_df = pd.concat([bs_overall_df, od_overall_df], ignore_index=True)
summary_path = os.path.join(OUTPUT_DIR, "sanitation_tabpfn_loco_summary.csv")
summary_df.to_csv(summary_path, index=False)

print(f"\n{'='*60}")
print("Sanitation — TabPFN final LOCO-CV summary:")
print(summary_df[[
    "outcome", "feature_set", "n_rows", "n_features", "n_countries",
    "unweighted_mae", "unweighted_rmse", "unweighted_r2",
    "weighted_mae",   "weighted_rmse",   "weighted_r2",
]].to_string(index=False))
print(f"\nSaved: {summary_path}")


# -------------------------------------------------------
# 16. TabPFN quantile predictions (LOCO CV)
#
# Re-runs LOCO CV requesting quantile outputs from TabPFN.
# Raw model quantiles — not coverage-guaranteed.
# If TabPFN does not expose quantile output for the client
# version in use, the fold is skipped with a warning.
# -------------------------------------------------------

QUANTILE_LEVELS = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]

QUANTILE_TASKS = {
    "basic_sanitation": {
        "model_df": bs_model_df,
        "features": bs_features,
        "prefix":   "basic_sanitation",
    },
    "open_defecation": {
        "model_df": od_model_df,
        "features": od_features,
        "prefix":   "open_defecation",
    },
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
            if lo_q not in grp.columns or hi_q not in grp.columns:
                continue
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
print("Section 16 — TabPFN quantile predictions (LOCO CV)")
print(f"{'='*60}")

for outcome_name, cfg in QUANTILE_TASKS.items():
    print(f"\n  Outcome: {outcome_name}")
    try:
        q_oof_df, q_cov_df = run_loco_cv_tabpfn_quantiles(
            cfg["model_df"], cfg["features"], outcome_name
        )
        q_oof_df.to_csv(
            os.path.join(OUTPUT_DIR, f"{cfg['prefix']}_tabpfn_quantile_oof.csv"),
            index=False,
        )
        q_cov_df.to_csv(
            os.path.join(OUTPUT_DIR,
                         f"{cfg['prefix']}_tabpfn_quantile_coverage_by_country.csv"),
            index=False,
        )
        if not q_cov_df.empty:
            print(
                q_cov_df.groupby("interval")[["empirical_coverage", "mean_width"]]
                .mean().round(4).to_string()
            )
    except RuntimeError as exc:
        warnings.warn(f"  TabPFN quantile prediction skipped: {exc}")
        print("  → Use CQR for uncertainty intervals.")


# -------------------------------------------------------
# 17. Diagnostic plots for TabPFN quantile predictions
#
# Loads quantile OOF CSVs saved in Section 16.
# Can be re-run independently after Section 16 completes.
#
# Plot A: Interval width vs prediction error
# Plot B: Observed vs predicted (q50) with 90 % PI bars
# Plot C: Calibration diagram (reliability plot)
# Plot D: Residuals vs observed with PI error bars
# -------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

PLOT_DIR = os.path.join(OUTPUT_DIR, "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

OUTCOME_CFG = {
    "basic_sanitation": {"label": "Basic sanitation", "colour": "#2166ac"},
    "open_defecation":  {"label": "Open defecation",  "colour": "#d6604d"},
}

Q_LEVELS    = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
Q_COL_NAMES = [f"q{int(q * 100):02d}" for q in Q_LEVELS]


def load_quantile_oof(prefix):
    path = os.path.join(OUTPUT_DIR, f"{prefix}_tabpfn_quantile_oof.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Quantile OOF file not found: {path}")
    df = pd.read_csv(path)
    df["error"]    = df["q50"] - df[TARGET_COL]
    df["width_80"] = df["q90"] - df["q10"]
    df["width_90"] = df["q95"] - df["q05"]
    df["w_norm"]   = df[WEIGHT_COL] / df[WEIGHT_COL].mean()
    return df


dfs = {}
for name, cfg in OUTCOME_CFG.items():
    prefix = TASKS[name]["output_prefix"]
    try:
        dfs[name] = load_quantile_oof(prefix)
        print(f"Loaded quantile OOF: {name}  ({len(dfs[name])} rows)")
    except FileNotFoundError as e:
        print(f"  Warning: {e}")

if not dfs:
    print("No quantile OOF files found — skipping diagnostic plots.")
else:

    # ── Plot A: interval width vs prediction error ────────────────────────────
    fig, axes = plt.subplots(1, len(dfs), figsize=(6 * len(dfs), 5))
    if len(dfs) == 1:
        axes = [axes]

    for ax, (name, df) in zip(axes, dfs.items()):
        cfg = OUTCOME_CFG[name]
        s   = np.clip(df["w_norm"].to_numpy() * 18, 2, 120)

        ax.scatter(df["error"], df["width_90"], s=s, alpha=0.45,
                   linewidths=0, color=cfg["colour"], label="90 % PI", zorder=3)
        ax.scatter(df["error"], df["width_80"], s=s, alpha=0.30,
                   linewidths=0, color=cfg["colour"], label="80 % PI", zorder=2)

        for width_col, ls, lbl in [
            ("width_90", "-",  "90 % — weighted trend"),
            ("width_80", "--", "80 % — weighted trend"),
        ]:
            df_s   = df.sort_values("error")
            bins   = pd.qcut(df_s["error"], q=30, duplicates="drop")
            binned = df_s.groupby(bins, observed=True).apply(
                lambda g: pd.Series({
                    "error_mid":  np.average(g["error"],      weights=g[WEIGHT_COL]),
                    "width_mean": np.average(g[width_col],    weights=g[WEIGHT_COL]),
                })
            ).dropna()
            ax.plot(binned["error_mid"], binned["width_mean"],
                    lw=2, ls=ls, color="black", label=lbl, zorder=5)

        ax.axvline(0, color="grey", lw=1.0, ls=":", zorder=4)
        ax.set_xlabel("Prediction error  (q50 − observed)", fontsize=11)
        ax.set_ylabel("Prediction interval width", fontsize=11)
        ax.set_title(cfg["label"], fontsize=12, fontweight="bold")
        ax.legend(fontsize=8, framealpha=0.7)
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle(
        "TabPFN: interval width vs prediction error\n(point size ∝ PSU weight)",
        fontsize=13, y=1.02,
    )
    plt.tight_layout()
    out_a = os.path.join(PLOT_DIR, "tabpfn_quantile_width_vs_error.png")
    plt.savefig(out_a, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_a}")


    # ── Plot B: observed vs predicted (q50) with 90 % PI bars ────────────────
    fig, axes = plt.subplots(1, len(dfs), figsize=(6 * len(dfs), 5))
    if len(dfs) == 1:
        axes = [axes]

    for ax, (name, df) in zip(axes, dfs.items()):
        cfg    = OUTCOME_CFG[name]
        y_obs  = df[TARGET_COL].to_numpy(dtype=float)
        y_pred = df["q50"].to_numpy(dtype=float)
        lo     = df["q05"].to_numpy(dtype=float)
        hi     = df["q95"].to_numpy(dtype=float)
        w      = df[WEIGHT_COL].to_numpy(dtype=float)
        s      = np.clip(df["w_norm"].to_numpy() * 18, 2, 120)

        yerr_lo = np.clip(y_pred - lo, 0, None)
        yerr_hi = np.clip(hi - y_pred, 0, None)

        ax.errorbar(y_obs, y_pred, yerr=[yerr_lo, yerr_hi],
                    fmt="none", ecolor=cfg["colour"], elinewidth=0.5,
                    alpha=0.25, zorder=2)
        ax.scatter(y_obs, y_pred, s=s, alpha=0.6, linewidths=0,
                   color=cfg["colour"], zorder=3)

        lims = [min(y_obs.min(), y_pred.min()) - 0.02,
                max(y_obs.max(), y_pred.max()) + 0.02]
        ax.plot(lims, lims, color="black", lw=1.2, ls="--",
                zorder=4, label="y = x")
        ax.set_xlim(lims); ax.set_ylim(lims)

        ax.set_xlabel("Observed proportion", fontsize=11)
        ax.set_ylabel("Predicted proportion (q50)", fontsize=11)
        ax.set_title(cfg["label"], fontsize=12, fontweight="bold")
        ax.legend(fontsize=9, framealpha=0.7)
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle(
        "Observed vs predicted (q50) with 90 % prediction intervals\n"
        "(point size ∝ PSU weight; error bars = q05–q95)",
        fontsize=13, y=1.02,
    )
    plt.tight_layout()
    out_b = os.path.join(PLOT_DIR, "tabpfn_quantile_obs_vs_pred_90pct.png")
    plt.savefig(out_b, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_b}")


    # ── Plot C: calibration diagram ───────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(6, 6))

    for name, df in dfs.items():
        cfg     = OUTCOME_CFG[name]
        w       = df[WEIGHT_COL].to_numpy(dtype=float)
        y       = df[TARGET_COL].to_numpy(dtype=float)
        missing = [c for c in Q_COL_NAMES if c not in df.columns]
        if missing:
            print(f"  Skipping calibration for {name} — missing: {missing}")
            continue

        empirical = []
        for q, col in zip(Q_LEVELS, Q_COL_NAMES):
            below = (y < df[col].to_numpy(dtype=float)).astype(float)
            empirical.append(float(np.average(below, weights=w)))

        ax.plot(Q_LEVELS, empirical, marker="o", markersize=6, lw=2,
                color=cfg["colour"], label=cfg["label"], zorder=3)

        emp_90 = empirical[Q_LEVELS.index(0.90)]
        ax.annotate(
            f"{emp_90:.2f}",
            xy=(0.90, emp_90),
            xytext=(0.80, emp_90 - 0.04),
            fontsize=8, color=cfg["colour"],
            arrowprops=dict(arrowstyle="-", color=cfg["colour"], lw=0.8),
        )

    ax.plot([0, 1], [0, 1], color="black", lw=1.2, ls="--",
            zorder=2, label="Perfect calibration")
    ax.fill_between([0, 1], [0, 1], [1, 1], alpha=0.06, color="steelblue")
    ax.fill_between([0, 1], [0, 0], [0, 1], alpha=0.06, color="tomato")
    ax.text(0.72, 0.60, "Overconfident", fontsize=8,
            color="tomato", ha="center", style="italic")
    ax.text(0.25, 0.40, "Underconfident", fontsize=8,
            color="steelblue", ha="center", style="italic")

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks(Q_LEVELS)
    ax.set_xticklabels([f"{int(q*100)}th" for q in Q_LEVELS], fontsize=9)
    ax.set_xlabel("Nominal quantile level", fontsize=11)
    ax.set_ylabel("Empirical proportion below predicted quantile", fontsize=11)
    ax.set_title("Calibration diagram — TabPFN raw quantile predictions\n"
                 "(PSU-weighted)", fontsize=11, fontweight="bold")
    ax.legend(fontsize=9, framealpha=0.8, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    out_c = os.path.join(PLOT_DIR, "tabpfn_quantile_calibration.png")
    plt.savefig(out_c, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_c}")


    # ── Plot D: residuals vs observed ─────────────────────────────────────────
    fig, axes = plt.subplots(1, len(dfs), figsize=(6 * len(dfs), 5))
    if len(dfs) == 1:
        axes = [axes]

    for ax, (name, df) in zip(axes, dfs.items()):
        cfg      = OUTCOME_CFG[name]
        obs      = df[TARGET_COL].to_numpy(dtype=float)
        resid    = df["error"].to_numpy(dtype=float)
        lo_resid = df["q05"].to_numpy(dtype=float) - obs
        hi_resid = df["q95"].to_numpy(dtype=float) - obs
        w        = df[WEIGHT_COL].to_numpy(dtype=float)
        s        = np.clip(df["w_norm"].to_numpy() * 18, 2, 120)

        yerr_lo = np.clip(resid - lo_resid, 0, None)
        yerr_hi = np.clip(hi_resid - resid, 0, None)

        ax.errorbar(obs, resid, yerr=[yerr_lo, yerr_hi],
                    fmt="none", ecolor=cfg["colour"], alpha=0.15,
                    lw=0.6, zorder=1)
        ax.scatter(obs, resid, s=s, color=cfg["colour"],
                   alpha=0.55, zorder=2, linewidths=0)

        sort_idx = np.argsort(obs)
        obs_s    = obs[sort_idx]
        resid_s  = resid[sort_idx]
        window   = max(1, len(obs_s) // 10)
        running  = np.convolve(resid_s, np.ones(window) / window, mode="valid")
        x_run    = obs_s[window // 2: window // 2 + len(running)]
        ax.plot(x_run, running, color="black", lw=1.5,
                alpha=0.7, label="Running mean")

        ax.axhline(0,      color="black", lw=1.2, ls="--", label="Zero residual")
        ax.axhline( 0.10,  color="grey",  lw=0.5, ls=":",  alpha=0.5)
        ax.axhline(-0.10,  color="grey",  lw=0.5, ls=":",  alpha=0.5)
        ax.set_xlim(0, 1)
        ax.set_xlabel("Observed proportion", fontsize=11)
        ax.set_ylabel("Residual (q50 − observed)", fontsize=11)
        ax.set_title(cfg["label"], fontsize=12, fontweight="bold")
        ax.legend(fontsize=8, framealpha=0.8)
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle(
        "Residuals vs observed  (point size ∝ PSU weight;\n"
        "error bars = q05–q95 residuals)",
        fontsize=12, y=1.02,
    )
    plt.tight_layout()
    out_d = os.path.join(PLOT_DIR, "tabpfn_residuals_vs_observed.png")
    plt.savefig(out_d, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_d}")
