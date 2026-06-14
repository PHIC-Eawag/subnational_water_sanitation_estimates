# -------------------------------------------------------
# Household PSU-weighted leave-one-country-out CV
# Outcomes: sanitation
#   - basic_sanitation   (improved, unshared facility)
#   - open_defecation    (no facility)
#
# Model: TabPFN
# Metrics (weighted and unweighted): MAE, RMSE, R²
# Comparable to h2o RF xval_mae / xval_rmse / xval_r2
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

DATA_DIR   = "data/training_subcomponents"
OUTPUT_DIR = "outputs/04_model_performance"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# -------------------------------------------------------
# 2.  Column names (identical across both sanitation files)
# -------------------------------------------------------

TARGET_COL   = "outcome_value"
COUNTRY_COL  = "country_cov"        # used for LOCO fold assignment
PAKISTAN_COL = "country_outcome"    # used for Pakistan row removal
REGION_COL   = "HH7_region_outcome"
YEAR_COL     = "analysis_year"
WEIGHT_COL   = "n_psu_weight_scaled"


# -------------------------------------------------------
# 3.  Feature lists (matching all_EO_features + country-level
#     from 01_modelling_sanitation_outcomes.qmd)
# -------------------------------------------------------

ALL_EO_FEATURES = [
    "CGIAR_Aridity_Index",
    "CGIAR_PET",
    "CHELSA_BIO_Annual_Mean_Temperature",
    "CHELSA_BIO_Annual_Precipitation",
    "CHELSA_BIO_Precipitation_Seasonality",
    "CHELSA_BIO_Precipitation_of_Coldest_Quarter",
    "CHELSA_BIO_Precipitation_of_Driest_Month",
    "CHELSA_BIO_Precipitation_of_Driest_Quarter",
    "CHELSA_BIO_Precipitation_of_Warmest_Quarter",
    "CHELSA_BIO_Precipitation_of_Wettest_Month",
    "CHELSA_BIO_Precipitation_of_Wettest_Quarter",
    "CHELSA_BIO_Temperature_Annual_Range",
    "CHELSA_BIO_Temperature_Seasonality",
    "CIFOR_TropicalPeatlandExtent",
    "CSP_Global_Human_Modification",
    "ConsensusLandCoverClass_Barren",
    "ConsensusLandCoverClass_Cultivated_and_Managed_Vegetation",
    "ConsensusLandCoverClass_Deciduous_Broadleaf_Trees",
    "ConsensusLandCoverClass_Evergreen_Broadleaf_Trees",
    "ConsensusLandCoverClass_Evergreen_Deciduous_Needleleaf_Trees",
    "ConsensusLandCoverClass_Herbaceous_Vegetation",
    "ConsensusLandCoverClass_Mixed_Other_Trees",
    "ConsensusLandCoverClass_Open_Water",
    "ConsensusLandCoverClass_Regularly_Flooded_Vegetation",
    "ConsensusLandCoverClass_Shrubs",
    "ConsensusLandCoverClass_Snow_Ice",
    "ConsensusLandCoverClass_Urban_Builtup",
    "ConsensusLandCover_Human_Development_Percentage",
    "CrowtherLab_Tree_Density",
    "EarthEnvCloudCover_CloudForestPrediction",
    "EarthEnvTexture_CoOfVar_EVI",
    "EarthEnvTexture_Contrast_EVI",
    "EarthEnvTexture_Correlation_EVI",
    "EarthEnvTexture_Dissimilarity_EVI",
    "EarthEnvTexture_Entropy_EVI",
    "EarthEnvTexture_Evenness_EVI",
    "EarthEnvTexture_Homogeneity_EVI",
    "EarthEnvTexture_Maximum_EVI",
    "EarthEnvTexture_Range_EVI",
    "EarthEnvTexture_Shannon_Index",
    "EarthEnvTexture_Simpson_Index",
    "EarthEnvTexture_Std_EVI",
    "EarthEnvTexture_Uniformity_EVI",
    "EarthEnvTexture_Variance_EVI",
    "EarthEnvTopoMed_1stOrderPartialDerivEW",
    "EarthEnvTopoMed_1stOrderPartialDerivNS",
    "EarthEnvTopoMed_Eastness",
    "EarthEnvTopoMed_Elevation",
    "EarthEnvTopoMed_Roughness",
    "EarthEnvTopoMed_Slope",
    "EarthEnvTopoMed_TerrainRuggednessIndex",
    "EarthEnvTopoMed_TopoPositionIndex",
    "EsaCci_BurntAreasProbability",
    "FanEtAl_Depth_to_Water_Table_AnnualMean",
    "FanEtAl_Depth_to_Water_Table_AnnualSD",
    "GHS_Population_Density",
    "GLW3_RuminantsDistribution_downsampled10km",
    "GPWv4_Population_Density",
    "GiriEtAl_MangrovesExtent",
    "MODIS_EVI",
    "MODIS_NDVI",
    "MODIS_NPP",
    "PelletierEtAl_SoilAndSedimentaryDepositThicknesses",
    "SG_Absolute_depth_to_bedrock",
    "SG_Bulk_density_015cm",
    "SG_Depth_to_bedrock",
    "SG_H2O_Capacity_015cm",
    "SG_Saturated_H2O_Content_015cm",
    "TootchiEtAl_WetlandsRegularlyFlooded",
    "WCS_Human_Footprint_2009",
    "chirps_annual_precipitation",
    "era5_temperature_2m",
    "ghsl_built_surface",
    "ghsl_population",
    "ghsl_urban_frac",
    "jrc_building_height",
    "map_friction",
    "modis_evi",
    "modis_ndvi",
    "runoff_max_annualmax",
    "runoff_min_annualmin",
    "temperature_2m_max_annualmax",
    "viirs_average",
    "worldpop",
    "worldpop_sum",
    "ghsl_population_sum",
]

COUNTRY_LEVEL_FEATURES = [
    "gdp_per_capita_constant_2015_usd",
    "secondary_education_duration_years",
    "ww_collection_percent",
    "ww_treatment_percent",
    "ww_reuse_percent",
    "control_of_corruption",
    "governance_effectiveness",
    "political_stability",
    "regulatory_quality",
    "rule_of_law",
    "voice_and_accountability",
]

ALL_FEATURES = ALL_EO_FEATURES + COUNTRY_LEVEL_FEATURES


# -------------------------------------------------------
# 4.  Tasks: one entry per sanitation outcome
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

def prepare_model_data(df, exclude_countries=None):
    """
    Clean and structure one training dataframe for LOCO CV.

    Steps:
      1. Remove Pakistan rows and any task-specific excluded countries
      2. Resolve available features (intersection with data columns)
      3. Coerce to numeric; drop rows with NA in outcome, weight, or identifier columns only
      4. Keep only rows with positive PSU weight
      5. Deduplicate to one row per country_cov × year × region × outcome
      6. Assign integer country fold IDs
    """
    # Remove Pakistan
    mask_pak = df[PAKISTAN_COL].astype(str).str.startswith("Pakistan", na=False)
    n_pak = mask_pak.sum()
    if n_pak > 0:
        print(f"  Removed {n_pak} Pakistan rows")
    df = df[~mask_pak].copy()

    # Remove any additional excluded countries
    if exclude_countries:
        for country in exclude_countries:
            mask = df[PAKISTAN_COL].astype(str).str.startswith(country, na=False)
            n = mask.sum()
            if n > 0:
                print(f"  Removed {n} {country} rows")
            df = df[~mask].copy()

    # Resolve features present in this file
    feature_cols = [c for c in ALL_FEATURES if c in df.columns]
    n_skipped = len(ALL_FEATURES) - len(feature_cols)
    if n_skipped:
        warnings.warn(f"  {n_skipped} candidate feature(s) not found in data — skipped")

    # Select and coerce columns
    keep = feature_cols + [TARGET_COL, COUNTRY_COL, REGION_COL, YEAR_COL, WEIGHT_COL]
    model_df = df[keep].copy()

    for col in feature_cols + [TARGET_COL, WEIGHT_COL]:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")

    model_df = model_df.dropna(
        subset=[TARGET_COL, COUNTRY_COL, REGION_COL, YEAR_COL, WEIGHT_COL]
    ).copy()

    model_df = model_df[model_df[WEIGHT_COL] > 0].copy()

    # One row per country_cov × year × region × outcome_value
    model_df = model_df.drop_duplicates(
        subset=[COUNTRY_COL, YEAR_COL, REGION_COL, TARGET_COL]
    ).copy()

    if model_df[COUNTRY_COL].nunique() < 2:
        raise ValueError("Need at least two countries for leave-one-country-out CV.")

    # Assign integer fold IDs
    country_lookup = (
        model_df[[COUNTRY_COL]]
        .drop_duplicates()
        .sort_values(COUNTRY_COL)
        .reset_index(drop=True)
        .assign(country_fold=lambda x: np.arange(1, len(x) + 1))
    )
    model_df = model_df.merge(country_lookup, on=COUNTRY_COL, how="left")

    return model_df, feature_cols


# -------------------------------------------------------
# 6.  Metrics helper
# -------------------------------------------------------

def compute_metrics(y_true, y_pred, weights):
    """Weighted and unweighted MAE, RMSE, R²."""
    has_variance = len(np.unique(y_true)) > 1
    return {
        "weighted_mae":    mean_absolute_error(y_true, y_pred, sample_weight=weights),
        "weighted_rmse":   mean_squared_error(y_true, y_pred, sample_weight=weights) ** 0.5,
        "weighted_r2":     r2_score(y_true, y_pred, sample_weight=weights) if has_variance else np.nan,
        "unweighted_mae":  mean_absolute_error(y_true, y_pred),
        "unweighted_rmse": mean_squared_error(y_true, y_pred) ** 0.5,
        "unweighted_r2":   r2_score(y_true, y_pred) if has_variance else np.nan,
    }


# -------------------------------------------------------
# 7.  TabPFN fit (pass sample_weight only if supported)
# -------------------------------------------------------

def clear_memory():
    """Free Python memory after each fold."""
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
# 8.  Leave-one-country-out CV
# -------------------------------------------------------

def run_loco_cv(model_df, feature_cols, outcome_name):
    """
    PSU-weighted LOCO CV with TabPFN.

    Returns
    -------
    fold_df    : per-country metrics
    overall_df : overall OOF metrics
    oof_df     : out-of-fold predictions with metadata
    """
    X       = model_df[feature_cols].to_numpy(dtype=float)
    y       = model_df[TARGET_COL].to_numpy(dtype=float)
    groups  = model_df["country_fold"].to_numpy()
    weights = model_df[WEIGHT_COL].to_numpy(dtype=float)

    oof_preds = np.full(len(model_df), np.nan)
    logo      = LeaveOneGroupOut()
    fold_rows = []
    used_sw_all = []

    for fold, (train_idx, val_idx) in enumerate(
        logo.split(X, y, groups=groups), start=1
    ):
        held_out = model_df.iloc[val_idx][COUNTRY_COL].iloc[0]
        print(f"  Fold {fold:>3d} | held-out: {held_out}")

        X_tr, y_tr = X[train_idx], y[train_idx]
        X_val, y_val = X[val_idx], y[val_idx]
        w_tr  = weights[train_idx]
        w_val = weights[val_idx]

        # Normalise training weights to mean 1
        w_tr_norm = w_tr / w_tr.mean()

        model = TabPFNRegressor()
        model, used_sw = fit_tabpfn(model, X_tr, y_tr, sample_weight=w_tr_norm)
        used_sw_all.append(used_sw)

        preds = np.asarray(model.predict(X_val)).reshape(-1)
        oof_preds[val_idx] = preds

        del model
        clear_memory()

        fold_rows.append({
            "outcome":            outcome_name,
            "fold":               fold,
            "held_out_country":   held_out,
            "n_train_rows":       len(train_idx),
            "n_val_rows":         len(val_idx),
            "sum_psu_weight_val": float(w_val.sum()),
            **compute_metrics(y_val, preds, w_val),
        })

    if np.isnan(oof_preds).any():
        raise RuntimeError(f"Missing OOF predictions: {np.isnan(oof_preds).sum()} rows")

    fold_df = pd.DataFrame(fold_rows)

    overall_df = pd.DataFrame([{
        "outcome":               outcome_name,
        "model":                 "TabPFN",
        "used_training_weights": all(used_sw_all),
        "n_rows":                len(y),
        "n_features":            len(feature_cols),
        "n_countries":           model_df[COUNTRY_COL].nunique(),
        "sum_psu_weight":        float(weights.sum()),
        **compute_metrics(y, oof_preds, weights),
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
# 9.  Main loop
# -------------------------------------------------------

all_overall = []

for outcome_name, cfg in TASKS.items():
    print(f"\n{'='*60}")
    print(f"Outcome: {outcome_name}")
    print(f"{'='*60}")

    data_path = os.path.join(DATA_DIR, cfg["filename"])
    print(f"Loading: {data_path}")
    df = pd.read_csv(data_path)
    print(f"  Raw shape: {df.shape}")

    model_df, feature_cols = prepare_model_data(df, exclude_countries=cfg.get("exclude_countries", []))

    print(f"  Modelling shape : {model_df.shape}")
    print(f"  Features used   : {len(feature_cols)}")
    print(f"  Countries       : {model_df[COUNTRY_COL].nunique()}")
    print(f"  Total PSU weight: {model_df[WEIGHT_COL].sum():,.1f}")

    fold_df, overall_df, oof_df = run_loco_cv(model_df, feature_cols, outcome_name)

    print(f"\n  Overall LOCO CV:")
    print(overall_df[[
        "outcome", "n_rows", "n_features", "n_countries",
        "weighted_mae", "weighted_rmse", "weighted_r2",
    ]].to_string(index=False))

    prefix = cfg["output_prefix"]
    fold_df.to_csv(
        os.path.join(OUTPUT_DIR, f"{prefix}_tabpfn_loco_cv_by_country_v2.csv"),
        index=False,
    )
    overall_df.to_csv(
        os.path.join(OUTPUT_DIR, f"{prefix}_tabpfn_loco_cv_overall_v2.csv"),
        index=False,
    )
    oof_df.to_csv(
        os.path.join(OUTPUT_DIR, f"{prefix}_tabpfn_loco_cv_oof_predictions_v2.csv"),
        index=False,
    )

    all_overall.append(overall_df)
    print(f"  Saved to {OUTPUT_DIR}/{prefix}_tabpfn_loco_cv_*.csv")


# -------------------------------------------------------
# 10. Combined summary
# -------------------------------------------------------

summary_df = pd.concat(all_overall, ignore_index=True)
summary_path = os.path.join(OUTPUT_DIR, "sanitation_tabpfn_loco_cv_summary_v2.csv")
summary_df.to_csv(summary_path, index=False)

print(f"\n{'='*60}")
print("Sanitation — TabPFN LOCO CV summary:")
print(summary_df[[
    "outcome", "n_rows", "n_features", "n_countries",
    "weighted_mae", "weighted_rmse", "weighted_r2",
    "unweighted_mae", "unweighted_rmse", "unweighted_r2",
]].to_string(index=False))
print(f"\nSaved combined summary: {summary_path}")


# -------------------------------------------------------
# 11. TabPFN quantile predictions (LOCO CV)
#
# Re-runs LOCO CV requesting quantile outputs from TabPFN.
# These are raw model quantiles — well-calibrated on average
# but NOT coverage-guaranteed. Section 13 (CQR) corrects
# them to have guaranteed coverage.
#
# If TabPFN does not expose quantile output for the client
# version in use, the fold is skipped and a warning printed.
# In that case go directly to Section 13 (CQR with GBR).
#
# Outputs per outcome:
#   *_tabpfn_quantile_oof.csv   — OOF quantile preds + metadata
#   *_tabpfn_quantile_coverage_by_country.csv — empirical PI coverage
# -------------------------------------------------------

QUANTILE_LEVELS = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]


def run_loco_cv_tabpfn_quantiles(model_df, feature_cols, outcome_name,
                                 quantiles=None):
    """
    LOCO CV collecting per-quantile OOF predictions from TabPFN.

    TabPFN's client exposes quantile output via
        model.predict(X, output_type="quantiles", quantiles=[...])
    returning an array of shape (n_samples, n_quantiles).

    If the installed version does not support this signature the
    function raises RuntimeError; callers should catch it.
    """
    if quantiles is None:
        quantiles = QUANTILE_LEVELS

    X       = model_df[feature_cols].to_numpy(dtype=float)
    y       = model_df[TARGET_COL].to_numpy(dtype=float)
    groups  = model_df["country_fold"].to_numpy()
    weights = model_df[WEIGHT_COL].to_numpy(dtype=float)

    n_q = len(quantiles)
    oof_q = np.full((len(model_df), n_q), np.nan)   # (n_rows, n_quantiles)

    logo = LeaveOneGroupOut()

    for fold, (train_idx, val_idx) in enumerate(
        logo.split(X, y, groups=groups), start=1
    ):
        held_out = model_df.iloc[val_idx][COUNTRY_COL].iloc[0]
        print(f"  Fold {fold:>3d} | held-out: {held_out}")

        X_tr, y_tr = X[train_idx], y[train_idx]
        X_val       = X[val_idx]
        w_tr        = weights[train_idx]
        w_tr_norm   = w_tr / w_tr.mean()

        model = TabPFNRegressor()
        model, _ = fit_tabpfn(model, X_tr, y_tr, sample_weight=w_tr_norm)

        # Request quantile output; raises TypeError if unsupported
        try:
            q_preds = model.predict(
                X_val,
                output_type="quantiles",
                quantiles=quantiles,
            )
            q_preds = np.asarray(q_preds)
            # Shape may be (n_quantiles, n_samples) — normalise to (n_samples, n_quantiles)
            if q_preds.ndim == 2 and q_preds.shape[0] == n_q and q_preds.shape[1] != n_q:
                q_preds = q_preds.T
        except (TypeError, AttributeError) as exc:
            del model
            clear_memory()
            raise RuntimeError(
                "TabPFN client does not support quantile output in this version. "
                "Use Section 13 (CQR with GBR) for coverage-guaranteed intervals."
            ) from exc

        oof_q[val_idx] = q_preds
        del model
        clear_memory()

    # Build OOF dataframe
    q_col_names = [f"q{int(q * 100):02d}" for q in quantiles]
    oof_df = model_df[
        [COUNTRY_COL, REGION_COL, YEAR_COL, TARGET_COL, WEIGHT_COL, "country_fold"]
    ].copy().reset_index(drop=True)
    oof_df.insert(0, "outcome", outcome_name)
    for i, col in enumerate(q_col_names):
        oof_df[col] = oof_q[:, i]

    # Per-country empirical PI coverage for 90 % and 80 % nominal levels
    coverage_rows = []
    for (country, fold_id), grp in oof_df.groupby([COUNTRY_COL, "country_fold"]):
        y_g = grp[TARGET_COL].to_numpy(dtype=float)
        w_g = grp[WEIGHT_COL].to_numpy(dtype=float)
        for lo_q, hi_q, label in [
            ("q05", "q95", "90pct"), ("q10", "q90", "80pct"),
        ]:
            if lo_q not in grp.columns or hi_q not in grp.columns:
                continue
            lo = grp[lo_q].to_numpy(dtype=float)
            hi = grp[hi_q].to_numpy(dtype=float)
            covered = (y_g >= lo) & (y_g <= hi)
            coverage_rows.append({
                "outcome":           outcome_name,
                "country_fold":      int(fold_id),
                "held_out_country":  country,
                "interval":          label,
                "n_val":             len(y_g),
                "mean_width":        round(float((hi - lo).mean()), 6),
                "empirical_coverage":round(float(covered.mean()), 4),
                "weighted_coverage": round(
                    float(np.average(covered.astype(float), weights=w_g)), 4
                ),
            })

    coverage_df = pd.DataFrame(coverage_rows)
    return oof_df, coverage_df


print(f"\n{'='*60}")
print("Section 12 — TabPFN quantile predictions (LOCO CV)")
print(f"{'='*60}")

for outcome_name, cfg in TASKS.items():
    prefix = cfg["output_prefix"]
    data_path = os.path.join(DATA_DIR, cfg["filename"])

    if not os.path.exists(data_path):
        print(f"  Skipping {outcome_name} — data file not found")
        continue

    print(f"\n  Outcome: {outcome_name}")
    df = pd.read_csv(data_path)
    model_df, feature_cols = prepare_model_data(
        df, exclude_countries=cfg.get("exclude_countries", [])
    )

    try:
        q_oof_df, q_cov_df = run_loco_cv_tabpfn_quantiles(
            model_df, feature_cols, outcome_name
        )
        q_oof_df.to_csv(
            os.path.join(OUTPUT_DIR, f"{prefix}_tabpfn_quantile_oof_v2.csv"),
            index=False,
        )
        q_cov_df.to_csv(
            os.path.join(OUTPUT_DIR, f"{prefix}_tabpfn_quantile_coverage_by_country_v2.csv"),
            index=False,
        )
        print(f"  Saved TabPFN quantile OOF to {OUTPUT_DIR}/{prefix}_tabpfn_quantile_v2*.csv")

        # Quick coverage summary
        if not q_cov_df.empty:
            print(
                q_cov_df.groupby("interval")[["empirical_coverage", "mean_width"]]
                .mean()
                .round(4)
                .to_string()
            )

    except RuntimeError as exc:
        warnings.warn(f"  TabPFN quantile prediction skipped: {exc}")
        print("  → Proceeding to Section 13 (CQR with GBR) for uncertainty intervals.")

# -------------------------------------------------------
# 12b. Diagnostic plots for TabPFN quantile predictions
#
# Paste directly after Section 12's output saving block.
#
# Plot A: Interval width vs prediction error (scatter,
#         PSU-weighted point size), for 80 % and 90 % PI.
# Plot B: Observed vs predicted (q50) with 90 % PI error
#         bars, PSU-weighted, coloured by outcome.
# -------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import os

# ── Config ────────────────────────────────────────────
OUTPUT_DIR   = "outputs/04_model_performance"
PLOT_DIR     = os.path.join(OUTPUT_DIR, "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

OUTCOMES = {
    "basic_sanitation": {
        "prefix": "basic_sanitation",
        "label":  "Basic sanitation",
        "colour": "#2166ac",
    },
    "open_defecation": {
        "prefix": "open_defecation",
        "label":  "Open defecation",
        "colour": "#d6604d",
    },
}

WEIGHT_COL  = "n_psu_weight_scaled"
TARGET_COL  = "outcome_value"
# ──────────────────────────────────────────────────────


def load_quantile_oof(prefix, output_dir):
    path = os.path.join(output_dir, f"{prefix}_tabpfn_quantile_oof_v2.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Quantile OOF file not found: {path}")
    df = pd.read_csv(path)
    # Derive useful columns
    df["error"]      = df["q50"] - df[TARGET_COL]   # prediction − observed
    df["width_80"]   = df["q90"] - df["q10"]         # 80 % PI width
    df["width_90"]   = df["q95"] - df["q05"]         # 90 % PI width
    # Normalise weights to mean 1 within dataset (for consistent scatter sizing)
    df["w_norm"]     = df[WEIGHT_COL] / df[WEIGHT_COL].mean()
    return df


# ── Load all outcomes ──────────────────────────────────
dfs = {}
for name, cfg in OUTCOMES.items():
    try:
        dfs[name] = load_quantile_oof(cfg["prefix"], OUTPUT_DIR)
        print(f"Loaded quantile OOF: {name}  ({len(dfs[name])} rows)")
    except FileNotFoundError as e:
        print(f"  Warning: {e}")

if not dfs:
    raise RuntimeError("No quantile OOF files found — run Section 12 first.")


# ═══════════════════════════════════════════════════════
# Plot A — Interval width vs prediction error
#
# Each point = one PSU region-year observation.
# Point size ∝ PSU weight. Vertical dashed line at 0 error.
# One panel per outcome, 80 % and 90 % PI on same axes.
# ═══════════════════════════════════════════════════════

fig, axes = plt.subplots(
    1, len(dfs), figsize=(6 * len(dfs), 5),
    sharey=False, sharex=False,
)
if len(dfs) == 1:
    axes = [axes]

for ax, (name, df) in zip(axes, dfs.items()):
    cfg = OUTCOMES[name]

    # Scale marker sizes: area ∝ weight; cap extremes for readability
    s = np.clip(df["w_norm"] * 18, 2, 120)

    ax.scatter(
        df["error"], df["width_90"],
        s=s, alpha=0.45, linewidths=0,
        color=cfg["colour"], label="90 % PI width",
        zorder=3,
    )
    ax.scatter(
        df["error"], df["width_80"],
        s=s, alpha=0.30, linewidths=0,
        color=cfg["colour"], label="80 % PI width",
        zorder=2,
    )

    # PSU-weighted LOWESS-style running mean per interval
    for width_col, lw, ls, lbl in [
        ("width_90", 2.0, "-",  "90 % PI — weighted trend"),
        ("width_80", 2.0, "--", "80 % PI — weighted trend"),
    ]:
        # Bin errors into 30 quantile bins, take weighted mean width per bin
        df_sorted  = df.sort_values("error")
        bin_labels = pd.qcut(df_sorted["error"], q=30, duplicates="drop")
        binned = df_sorted.groupby(bin_labels, observed=True).apply(
            lambda g: pd.Series({
                "error_mid":   np.average(g["error"],    weights=g[WEIGHT_COL]),
                "width_mean":  np.average(g[width_col],  weights=g[WEIGHT_COL]),
            })
        ).dropna()
        ax.plot(
            binned["error_mid"], binned["width_mean"],
            lw=lw, ls=ls, color="black", label=lbl, zorder=5,
        )

    ax.axvline(0, color="grey", lw=1.0, ls=":", zorder=4)
    ax.set_xlabel("Prediction error  (q50 − observed)", fontsize=11)
    ax.set_ylabel("Prediction interval width", fontsize=11)
    ax.set_title(cfg["label"], fontsize=12, fontweight="bold")
    ax.legend(fontsize=8, framealpha=0.7)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax.spines[["top", "right"]].set_visible(False)

fig.suptitle(
    "TabPFN quantile interval width vs prediction error\n"
    "(point size ∝ PSU weight)",
    fontsize=13, y=1.02,
)
plt.tight_layout()
out_a = os.path.join(PLOT_DIR, "tabpfn_quantile_width_vs_error_v2.png")
plt.savefig(out_a, dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved: {out_a}")


# ═══════════════════════════════════════════════════════
# Plot B — Observed vs predicted (q50) with 90 % PI bars
#
# One panel per outcome.
# Error bars = [q05, q95] — the full 90 % prediction interval.
# Points coloured by outcome; sized by PSU weight.
# Reference line y = x (perfect prediction).
# Weighted R² annotated on each panel.
# ═══════════════════════════════════════════════════════

from sklearn.metrics import r2_score

fig, axes = plt.subplots(
    1, len(dfs), figsize=(6 * len(dfs), 5),
    sharey=False, sharex=False,
)
if len(dfs) == 1:
    axes = [axes]

for ax, (name, df) in zip(axes, dfs.items()):
    cfg = OUTCOMES[name]

    y_obs  = df[TARGET_COL].to_numpy()
    y_pred = df["q50"].to_numpy()
    lo     = df["q05"].to_numpy()
    hi     = df["q95"].to_numpy()
    w      = df[WEIGHT_COL].to_numpy()
    s      = np.clip(df["w_norm"] * 18, 2, 120)

    # Error bar half-widths (asymmetric: distance from q50 to each bound)
    yerr_lo = np.clip(y_pred - lo, 0, None)
    yerr_hi = np.clip(hi - y_pred, 0, None)

    ax.errorbar(
        y_obs, y_pred,
        yerr=[yerr_lo, yerr_hi],
        fmt="none",
        ecolor=cfg["colour"], elinewidth=0.5, alpha=0.25,
        zorder=2,
    )
    ax.scatter(
        y_obs, y_pred,
        s=s, alpha=0.6, linewidths=0,
        color=cfg["colour"], zorder=3,
    )

    # y = x reference line
    lims = [
        min(y_obs.min(), y_pred.min()) - 0.02,
        max(y_obs.max(), y_pred.max()) + 0.02,
    ]
    ax.plot(lims, lims, color="black", lw=1.2, ls="--", zorder=4, label="y = x")
    ax.set_xlim(lims); ax.set_ylim(lims)

    # Weighted R²
    w_r2 = r2_score(y_obs, y_pred, sample_weight=w)
    ax.text(
        0.05, 0.93,
        f"Weighted R² = {w_r2:.3f}",
        transform=ax.transAxes,
        fontsize=9, va="top",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7),
    )

    # Coverage annotation
    covered = (y_obs >= lo) & (y_obs <= hi)
    w_cov   = np.average(covered.astype(float), weights=w)
    ax.text(
        0.05, 0.84,
        f"90 % PI coverage = {w_cov:.1%}",
        transform=ax.transAxes,
        fontsize=9, va="top",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7),
    )

    ax.set_xlabel("Observed proportion", fontsize=11)
    ax.set_ylabel("Predicted proportion (q50)", fontsize=11)
    ax.set_title(cfg["label"], fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, framealpha=0.7)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
    ax.spines[["top", "right"]].set_visible(False)

fig.suptitle(
    "Observed vs predicted (q50) with 90 % prediction intervals\n"
    "(point size ∝ PSU weight; error bars = q05–q95)",
    fontsize=13, y=1.02,
)
plt.tight_layout()
out_b = os.path.join(PLOT_DIR, "tabpfn_quantile_obs_vs_pred_90pct_v2.png")
plt.savefig(out_b, dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved: {out_b}")

# -------------------------------------------------------
# 12c. Calibration diagram (reliability plot)
#
# For each nominal quantile level q, compute the empirical
# proportion of observations where the true value falls
# BELOW the predicted q-th quantile. Perfect calibration
# produces a diagonal line. Sagging below = overconfident
# (intervals too tight). Bowing above = underconfident.
#
# PSU weights applied when computing empirical proportions.
# Both outcomes plotted on the same axes for comparison.
# -------------------------------------------------------

fig, ax = plt.subplots(figsize=(6, 6))

# Quantile levels that exist in the OOF file
q_levels     = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
q_col_names  = [f"q{int(q * 100):02d}" for q in q_levels]   # q05, q10, …

colours = {
    "basic_sanitation": "#2166ac",
    "open_defecation":  "#d6604d",
}
labels = {
    "basic_sanitation": "Basic sanitation",
    "open_defecation":  "Open defecation",
}

for name, df in dfs.items():

    # Check all quantile columns are present
    missing = [c for c in q_col_names if c not in df.columns]
    if missing:
        print(f"  Skipping {name} — missing columns: {missing}")
        continue

    w = df[WEIGHT_COL].to_numpy()
    y = df[TARGET_COL].to_numpy()

    empirical = []
    for q, col in zip(q_levels, q_col_names):
        q_pred  = df[col].to_numpy()
        below   = (y < q_pred).astype(float)          # 1 where obs < predicted quantile
        emp_cov = float(np.average(below, weights=w))  # weighted proportion
        empirical.append(emp_cov)

    ax.plot(
        q_levels, empirical,
        marker="o", markersize=6, linewidth=2,
        color=colours[name], label=labels[name], zorder=3,
    )

    # Annotate the 90th-quantile deviation directly on the plot
    emp_90 = empirical[q_levels.index(0.90)]
    ax.annotate(
        f"{emp_90:.2f}",
        xy=(0.90, emp_90),
        xytext=(0.90 - 0.10, emp_90 - 0.04),
        fontsize=8,
        color=colours[name],
        arrowprops=dict(arrowstyle="-", color=colours[name], lw=0.8),
    )

# Perfect calibration reference line
ax.plot([0, 1], [0, 1], color="black", lw=1.2, ls="--",
        zorder=2, label="Perfect calibration")

# Shaded regions to guide the eye
ax.fill_between([0, 1], [0, 1], [1, 1],
                alpha=0.06, color="steelblue", label="Underconfident region")
ax.fill_between([0, 1], [0, 0], [0, 1],
                alpha=0.06, color="tomato",    label="Overconfident region")

ax.text(0.72, 0.60, "Overconfident\n(intervals too tight)",
        fontsize=8, color="tomato",    ha="center", style="italic")
ax.text(0.25, 0.40, "Underconfident\n(intervals too wide)",
        fontsize=8, color="steelblue", ha="center", style="italic")

ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_xticks(q_levels)
ax.set_xticklabels([f"{int(q*100)}th" for q in q_levels], fontsize=9)
ax.set_xlabel("Nominal quantile level", fontsize=11)
ax.set_ylabel("Empirical proportion below predicted quantile", fontsize=11)
ax.set_title("Calibration diagram — TabPFN raw quantile predictions\n"
             "(PSU-weighted; dashed = perfect calibration)",
             fontsize=11, fontweight="bold")
ax.legend(fontsize=9, framealpha=0.8, loc="upper left")
ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
out_calib = os.path.join(PLOT_DIR, "tabpfn_quantile_calibration_diagram_v2.png")
plt.savefig(out_calib, dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved: {out_calib}")

# -------------------------------------------------------
# 12d. Improved uncertainty visualisations
#
# Plot C: Binned ribbon — obs decile vs weighted mean pred + PI
# Plot D: Hexbin obs vs pred + strip plot of PI width by obs decile
# -------------------------------------------------------

# ── Plot C: Binned ribbon ────────────────────────────────

fig, axes = plt.subplots(1, len(dfs), figsize=(6 * len(dfs), 5), sharey=True)
if len(dfs) == 1:
    axes = [axes]

N_BINS = 10

for ax, (name, df) in zip(axes, dfs.items()):
    cfg = OUTCOMES[name]

    df_s = df.copy()
    df_s["obs_bin"] = pd.qcut(df_s[TARGET_COL], q=N_BINS, duplicates="drop")

    def wstats(g):
        w = g[WEIGHT_COL]
        return pd.Series({
            "obs_mid":    np.average(g[TARGET_COL], weights=w),
            "pred_mean":  np.average(g["q50"],      weights=w),
            "pi90_lo":    np.average(np.clip(g["q05"], 0, 1), weights=w),
            "pi90_hi":    np.average(np.clip(g["q95"], 0, 1), weights=w),
            "pi80_lo":    np.average(np.clip(g["q10"], 0, 1), weights=w),
            "pi80_hi":    np.average(np.clip(g["q90"], 0, 1), weights=w),
            "n":          len(g),
        })

    binned = df_s.groupby("obs_bin", observed=True).apply(wstats).reset_index(drop=True)

    # 90 % PI ribbon
    ax.fill_between(
        binned["obs_mid"], binned["pi90_lo"], binned["pi90_hi"],
        alpha=0.20, color=cfg["colour"], label="90 % PI",
    )
    # 80 % PI ribbon
    ax.fill_between(
        binned["obs_mid"], binned["pi80_lo"], binned["pi80_hi"],
        alpha=0.35, color=cfg["colour"], label="80 % PI",
    )
    # Mean prediction line
    ax.plot(
        binned["obs_mid"], binned["pred_mean"],
        color=cfg["colour"], lw=2, marker="o", ms=5, label="Mean predicted (q50)",
    )
    # Perfect calibration
    lims = [0, 1]
    ax.plot(lims, lims, "k--", lw=1.2, label="y = x")

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("Observed proportion (binned into deciles)", fontsize=11)
    ax.set_ylabel("Predicted proportion (weighted mean)", fontsize=11)
    ax.set_title(cfg["label"], fontsize=12, fontweight="bold")
    ax.legend(fontsize=8, framealpha=0.8)
    ax.spines[["top","right"]].set_visible(False)

fig.suptitle(
    "Binned obs vs predicted with 80 % and 90 % prediction intervals\n"
    "(each point = weighted mean within observed decile)",
    fontsize=12, y=1.02,
)
plt.tight_layout()
out_c = os.path.join(PLOT_DIR, "tabpfn_quantile_binned_ribbon_v2.png")
plt.savefig(out_c, dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved: {out_c}")


# ── Plot D: Hexbin + PI width strip ─────────────────────

fig, axes = plt.subplots(
    2, len(dfs),
    figsize=(5.5 * len(dfs), 9),
    gridspec_kw={"height_ratios": [2, 1]},
)
# Normalise axes indexing for single vs multiple outcomes
if len(dfs) == 1:
    axes = axes.reshape(2, 1)

for col_i, (name, df) in enumerate(dfs.items()):
    cfg   = OUTCOMES[name]
    ax_hx = axes[0, col_i]   # hexbin panel
    ax_st = axes[1, col_i]   # strip panel

    # — Top panel: hexbin obs vs pred —
    hb = ax_hx.hexbin(
        df[TARGET_COL], df["q50"],
        C=df[WEIGHT_COL],             # aggregate by PSU weight
        reduce_C_function=np.sum,
        gridsize=35,
        cmap="Blues",
        linewidths=0.2,
    )
    ax_hx.plot([0,1],[0,1], "k--", lw=1.2, label="y = x")
    cb = fig.colorbar(hb, ax=ax_hx, pad=0.02, shrink=0.8)
    cb.set_label("Sum PSU weight", fontsize=8)

    w_r2 = r2_score(df[TARGET_COL], df["q50"], sample_weight=df[WEIGHT_COL])
    ax_hx.text(0.05, 0.93, f"Weighted R² = {w_r2:.3f}",
               transform=ax_hx.transAxes, fontsize=9, va="top",
               bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))
    ax_hx.set_xlim(0,1); ax_hx.set_ylim(0,1)
    ax_hx.set_xlabel("Observed proportion", fontsize=10)
    ax_hx.set_ylabel("Predicted proportion (q50)", fontsize=10)
    ax_hx.set_title(cfg["label"], fontsize=12, fontweight="bold")
    ax_hx.legend(fontsize=8)
    ax_hx.spines[["top","right"]].set_visible(False)

    # — Bottom panel: 90 % PI width by observed decile —
    df_s = df.copy()
    df_s["width_90"] = np.clip(df_s["q95"], 0, 1) - np.clip(df_s["q05"], 0, 1)
    df_s["obs_bin"]  = pd.qcut(df_s[TARGET_COL], q=N_BINS, duplicates="drop")

    bin_width = (
        df_s.groupby("obs_bin", observed=True)
        .apply(lambda g: pd.Series({
            "obs_mid":      np.average(g[TARGET_COL],  weights=g[WEIGHT_COL]),
            "mean_width":   np.average(g["width_90"],  weights=g[WEIGHT_COL]),
            "q25_width":    np.quantile(g["width_90"], 0.25),
            "q75_width":    np.quantile(g["width_90"], 0.75),
        }))
        .reset_index(drop=True)
    )

    ax_st.bar(
        bin_width["obs_mid"], bin_width["mean_width"],
        width=0.07, color=cfg["colour"], alpha=0.7,
        label="Mean 90 % PI width",
    )
    ax_st.errorbar(
        bin_width["obs_mid"], bin_width["mean_width"],
        yerr=[
            bin_width["mean_width"] - bin_width["q25_width"],
            bin_width["q75_width"]  - bin_width["mean_width"],
        ],
        fmt="none", color="black", capsize=3, lw=1,
    )
    ax_st.set_xlim(0, 1)
    ax_st.set_xlabel("Observed proportion (decile midpoint)", fontsize=10)
    ax_st.set_ylabel("90 % PI width", fontsize=10)
    ax_st.set_title("Interval width by observed level", fontsize=10)
    ax_st.spines[["top","right"]].set_visible(False)
    ax_st.legend(fontsize=8)

fig.suptitle(
    "Point prediction density (hexbin) and interval width by observed level",
    fontsize=12, y=1.01,
)
plt.tight_layout()
out_d = os.path.join(PLOT_DIR, "tabpfn_quantile_hexbin_width_v2.png")
plt.savefig(out_d, dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved: {out_d}")


