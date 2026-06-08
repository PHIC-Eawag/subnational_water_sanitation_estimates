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
    #"ww_collection_percent",
    #"ww_treatment_percent",
    #"ww_reuse_percent",
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
        os.path.join(OUTPUT_DIR, f"{prefix}_tabpfn_loco_cv_by_country_noWW.csv"),
        index=False,
    )
    overall_df.to_csv(
        os.path.join(OUTPUT_DIR, f"{prefix}_tabpfn_loco_cv_overall_noWW.csv"),
        index=False,
    )
    oof_df.to_csv(
        os.path.join(OUTPUT_DIR, f"{prefix}_tabpfn_loco_cv_oof_predictions_noWW.csv"),
        index=False,
    )

    all_overall.append(overall_df)
    print(f"  Saved to {OUTPUT_DIR}/{prefix}_tabpfn_loco_cv_noWW*.csv")


# -------------------------------------------------------
# 10. Combined summary
# -------------------------------------------------------

summary_df = pd.concat(all_overall, ignore_index=True)
summary_path = os.path.join(OUTPUT_DIR, "sanitation_tabpfn_loco_cv_summary_noWW.csv")
summary_df.to_csv(summary_path, index=False)

print(f"\n{'='*60}")
print("Sanitation — TabPFN LOCO CV summary:")
print(summary_df[[
    "outcome", "n_rows", "n_features", "n_countries",
    "weighted_mae", "weighted_rmse", "weighted_r2",
    "unweighted_mae", "unweighted_rmse", "unweighted_r2",
]].to_string(index=False))
print(f"\nSaved combined summary: {summary_path}")
