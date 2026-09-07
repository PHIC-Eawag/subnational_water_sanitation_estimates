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

DATA_DIR             = "data/processed/training_subcomponents"
CLUSTER_DIR          = "outputs/cluster_analysis/sanitation"
PRED_COVARIATES_PATH = "data/processed/prediction/prediction_covariates_2024.csv"
# Version all model outputs under a subfolder so retraining on the corrected
# (_v2) training data does not overwrite previous runs. Written to the git
# repo (outputs/), never to the switchdrive deliverables folder.
MODEL_OUTPUT_VERSION = "v2"
OUTPUT_DIR           = os.path.join("outputs/model_performance", MODEL_OUTPUT_VERSION)
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

# -------------------------------------------------------
# 3b. Feature categories (Table S1 / S2)
#
# Maps every feature to the category it belongs to, used by the by-category
# SHAP contribution summary (Section 21). Nine groups:
#   Climate, HP (human presence), S (hydrology & soil), Topography,
#   VT (vegetation texture), VC (vegetation coverage)   -> Table S1 (EO features)
#   SEG (socio-economic & governance), JMP (national estimates)  -> Table S2
#   Region size (administrative-area size, area_km2)
# Assignments are taken verbatim from Table S1 (note the deliberate oddities:
# Snow/Ice -> Climate, Open_Water -> S, CloudForestPrediction -> Topography).
# -------------------------------------------------------

FEATURE_CATEGORY_MAP = {
    # ── Climate ──────────────────────────────────────────────────────────────
    "CGIAR_Aridity_Index":                        "Climate",
    "CGIAR_PET":                                  "Climate",
    "CHELSA_BIO_Annual_Mean_Temperature":         "Climate",
    "CHELSA_BIO_Annual_Precipitation":            "Climate",
    "CHELSA_BIO_Precipitation_Seasonality":       "Climate",
    "CHELSA_BIO_Precipitation_of_Coldest_Quarter": "Climate",
    "CHELSA_BIO_Precipitation_of_Driest_Month":   "Climate",
    "CHELSA_BIO_Precipitation_of_Driest_Quarter": "Climate",
    "CHELSA_BIO_Precipitation_of_Warmest_Quarter": "Climate",
    "CHELSA_BIO_Precipitation_of_Wettest_Month":  "Climate",
    "CHELSA_BIO_Precipitation_of_Wettest_Quarter": "Climate",
    "CHELSA_BIO_Temperature_Annual_Range":        "Climate",
    "CHELSA_BIO_Temperature_Seasonality":         "Climate",
    "ConsensusLandCoverClass_Snow_Ice":           "Climate",
    "chirps_annual_precipitation":                "Climate",
    "era5_temperature_2m":                        "Climate",
    "temperature_2m_max_annualmax":               "Climate",
    # ── HP (human presence) ──────────────────────────────────────────────────
    "CSP_Global_Human_Modification":                            "Human presence",
    "ConsensusLandCoverClass_Cultivated_and_Managed_Vegetation": "Human presence",
    "ConsensusLandCoverClass_Urban_Builtup":                    "Human presence",
    "ConsensusLandCover_Human_Development_Percentage":          "Human presence",
    "EsaCci_BurntAreasProbability":                             "Human presence",
    "GHS_Population_Density":                                   "Human presence",
    "GLW3_RuminantsDistribution_downsampled10km":              "Human presence",
    "GPWv4_Population_Density":                                 "Human presence",
    "WCS_Human_Footprint_2009":                                "Human presence",
    "ghsl_built_surface":                                      "Human presence",
    "ghsl_population":                                         "Human presence",
    "ghsl_urban_frac":                                         "Human presence",
    "jrc_building_height":                                     "Human presence",
    "map_friction":                                            "Human presence",
    "viirs_average":                                           "Human presence",
    "worldpop":                                                "Human presence",
    "worldpop_sum":                                            "Human presence",
    "ghsl_population_sum":                                     "Human presence",
    # ── S (hydrology and soil) ───────────────────────────────────────────────
    "ConsensusLandCoverClass_Open_Water":                 "Hydrology & Soil",
    "FanEtAl_Depth_to_Water_Table_AnnualMean":            "Hydrology & Soil",
    "FanEtAl_Depth_to_Water_Table_AnnualSD":              "Hydrology & Soil",
    "PelletierEtAl_SoilAndSedimentaryDepositThicknesses": "Hydrology & Soil",
    "SG_Absolute_depth_to_bedrock":                       "Hydrology & Soil",
    "SG_Bulk_density_015cm":                              "Hydrology & Soil",
    "SG_Depth_to_bedrock":                                "Hydrology & Soil",
    "SG_H2O_Capacity_015cm":                              "Hydrology & Soil",
    "SG_Saturated_H2O_Content_015cm":                     "Hydrology & Soil",
    "runoff_max_annualmax":                               "Hydrology & Soil",
    "runoff_min_annualmin":                               "Hydrology & Soil",
    # ── Topography ───────────────────────────────────────────────────────────
    "EarthEnvCloudCover_CloudForestPrediction": "Topography",
    "EarthEnvTopoMed_1stOrderPartialDerivEW":   "Topography",
    "EarthEnvTopoMed_1stOrderPartialDerivNS":   "Topography",
    "EarthEnvTopoMed_Eastness":                 "Topography",
    "EarthEnvTopoMed_Elevation":                "Topography",
    "EarthEnvTopoMed_Roughness":                "Topography",
    "EarthEnvTopoMed_Slope":                    "Topography",
    "EarthEnvTopoMed_TerrainRuggednessIndex":   "Topography",
    "EarthEnvTopoMed_TopoPositionIndex":        "Topography",
    # ── VT (vegetation texture) ──────────────────────────────────────────────
    "EarthEnvTexture_CoOfVar_EVI":       "Vegetation texture",
    "EarthEnvTexture_Contrast_EVI":      "Vegetation texture",
    "EarthEnvTexture_Correlation_EVI":   "Vegetation texture",
    "EarthEnvTexture_Dissimilarity_EVI": "Vegetation texture",
    "EarthEnvTexture_Entropy_EVI":       "Vegetation texture",
    "EarthEnvTexture_Evenness_EVI":      "Vegetation texture",
    "EarthEnvTexture_Homogeneity_EVI":   "Vegetation texture",
    "EarthEnvTexture_Maximum_EVI":       "Vegetation texture",
    "EarthEnvTexture_Range_EVI":         "Vegetation texture",
    "EarthEnvTexture_Shannon_Index":     "Vegetation texture",
    "EarthEnvTexture_Simpson_Index":     "Vegetation texture",
    "EarthEnvTexture_Std_EVI":           "Vegetation texture",
    "EarthEnvTexture_Uniformity_EVI":    "Vegetation texture",
    "EarthEnvTexture_Variance_EVI":      "Vegetation texture",
    # ── VC (vegetation coverage) ─────────────────────────────────────────────
    "CIFOR_TropicalPeatlandExtent":                              "Vegetation coverage",
    "ConsensusLandCoverClass_Barren":                           "Vegetation coverage",
    "ConsensusLandCoverClass_Deciduous_Broadleaf_Trees":        "Vegetation coverage",
    "ConsensusLandCoverClass_Evergreen_Broadleaf_Trees":        "Vegetation coverage",
    "ConsensusLandCoverClass_Evergreen_Deciduous_Needleleaf_Trees": "Vegetation coverage",
    "ConsensusLandCoverClass_Herbaceous_Vegetation":            "Vegetation coverage",
    "ConsensusLandCoverClass_Mixed_Other_Trees":               "Vegetation coverage",
    "ConsensusLandCoverClass_Regularly_Flooded_Vegetation":    "Vegetation coverage",
    "ConsensusLandCoverClass_Shrubs":                          "Vegetation coverage",
    "CrowtherLab_Tree_Density":                                "Vegetation coverage",
    "GiriEtAl_MangrovesExtent":                                "Vegetation coverage",
    "MODIS_EVI":                                               "Vegetation coverage",
    "MODIS_NDVI":                                              "Vegetation coverage",
    "MODIS_NPP":                                               "Vegetation coverage",
    "TootchiEtAl_WetlandsRegularlyFlooded":                    "Vegetation coverage",
    "modis_evi":                                               "Vegetation coverage",
    "modis_ndvi":                                              "Vegetation coverage",
    # ── Region size ──────────────────────────────────────────────────────────
    "area_km2": "Region size",
    # ── SEG (socio-economic & governance, Table S2) ──────────────────────────
    "gdp_per_capita_constant_2015_usd":   "Socio-economic & governance",
    "secondary_education_duration_years": "Socio-economic & governance",
    "ww_collection_percent":              "Socio-economic & governance",
    "ww_treatment_percent":               "Socio-economic & governance",
    "ww_reuse_percent":                   "Socio-economic & governance",
    "control_of_corruption":              "Socio-economic & governance",
    "governance_effectiveness":           "Socio-economic & governance",
    "political_stability":                "Socio-economic & governance",
    "regulatory_quality":                 "Socio-economic & governance",
    "rule_of_law":                        "Socio-economic & governance",
    "voice_and_accountability":           "Socio-economic & governance",
    # ── JMP (national estimates, Table S2) ───────────────────────────────────
    "sanitation_basic": "JMP",
    "open_defecation":  "JMP",
}

# Fixed display order and colours for the category groups (Section 21 plot).
CATEGORY_ORDER = [
    "Climate", "Human presence", "Hydrology & Soil", "Topography", "Vegetation texture", "Vegetation coverage",
    "Socio-economic & governance", "JMP", "Region size",
]
CATEGORY_COLOURS = {
    "Climate":     "#4393c3",
    "Human presence":          "#d6604d",
    "Hydrology & Soil":           "#5aae61",
    "Topography":  "#8073ac",
    "Vegetation texture":          "#bf812d",
    "Vegetation coverage":          "#1b7837",
    "Socio-economic & governance":         "#e08214",
    "JMP":         "#c51b7d",
    "Region size": "#878787",
}


def category_of(feature):
    """Return the Table S1/S2 category for a feature, or 'Uncategorised'."""
    return FEATURE_CATEGORY_MAP.get(feature, "Uncategorised")


# Warn at import if a modelled feature is missing a category mapping, so new
# covariates can't silently fall into 'Uncategorised' in the plots. (Uses the
# source lists directly — ALL_FEATURES_K100 is assembled a few lines below.)
_uncategorised = [
    f for f in (ALL_EO_FEATURES + COUNTRY_LEVEL_FEATURES)
    if f not in FEATURE_CATEGORY_MAP
]
if _uncategorised:
    warnings.warn(
        f"{len(_uncategorised)} feature(s) missing from FEATURE_CATEGORY_MAP "
        f"(will show as 'Uncategorised'): {_uncategorised}"
    )

# -------------------------------------------------------
# SETUP: Define which features (input variables) to use
# -------------------------------------------------------

# Combine satellite/earth observation features with country-level statistics
# into one master list called ALL_FEATURES_K100.
# Think of this as the full "menu" of information the model can learn from.
ALL_FEATURES_K100 = ALL_EO_FEATURES + COUNTRY_LEVEL_FEATURES

# These are the different "sizes" of feature shortlists we want to test.
# k=5 means only 5 representative variables; k=100 means use all of them.
# The goal is to find the smallest set that still predicts well.
K_VALUES = [5, 10, 15, 20, 30, 45, 90, 100]


def load_feature_set(k):
    """
    Load the list of input variables for a given shortlist size k.
    - If k=100, return the full feature list (no shortlisting needed).
    - Otherwise, read a pre-saved CSV file that lists the best k variables
      chosen by a prior clustering analysis (run separately in 01_cluster_analysis.qmd).
    - Any variables in the file that aren't in our master list are dropped with a warning.
    """
    if k == 100:
        return ALL_FEATURES_K100

    # Build the file path for this shortlist size
    path = os.path.join(CLUSTER_DIR, f"representative_variables_k{k}.csv")

    # Stop with a clear error if the file hasn't been generated yet
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Cluster file not found: {path}\nRun 01_cluster_analysis.qmd first."
        )

    # Read the CSV and extract the column of variable names, dropping any blanks
    features = pd.read_csv(path)["representative_variable"].dropna().tolist()

    # Keep only variables that actually exist in our master feature list
    valid   = [f for f in features if f in ALL_FEATURES_K100]
    dropped = set(features) - set(valid)

    # Warn the user if any variables were silently removed
    if dropped:
        warnings.warn(f"k={k}: features not in ALL_FEATURES_K100 dropped: {dropped}")

    return valid


# Build a dictionary that maps each shortlist label (e.g. "k20") to its feature list.
# Example: feature_sets["k20"] = [list of 20 variable names]
feature_sets = {f"k{k}": load_feature_set(k) for k in K_VALUES}

# Print a summary so we can confirm everything loaded correctly
print("Feature sets loaded:")
for label, feats in feature_sets.items():
    print(f"  {label}: {len(feats)} features")


# -------------------------------------------------------
# 4.  Tasks — define what we are predicting
# -------------------------------------------------------

# Two separate prediction tasks, each pointing to its own training data file.
# Indonesia is no longer manually excluded from "basic_sanitation": its
# survey has no WS15 (shared-facility) data at all, so improved-facility
# rows now come through as NA outcome_value and are dropped upstream in
# 04a (join_and_save_one_training_dataset()). The remaining Indonesia rows
# (open defecation / unimproved facilities) don't depend on WS15 and stay in
# the training data as a small, determinate-but-skewed-toward-0 sample.
# "open_defecation" uses all available countries.
TASKS = {
    "basic_sanitation": {
        "filename":          "basic_sanitation_training_with_covariates_v2.csv",
        "output_prefix":     "basic_sanitation",
        "exclude_countries": [],
    },
    "open_defecation": {
        "filename":          "open_defecation_training_with_covariates_v2.csv",
        "output_prefix":     "open_defecation",
        "exclude_countries": [],
    },
}


# -------------------------------------------------------
# 5.  Data preparation — clean the training data
# -------------------------------------------------------

def prepare_model_data(df, feature_cols, exclude_countries=None):
    """
    Takes a raw training spreadsheet and prepares it for modelling:
    1. Removes rows from excluded countries.
    2. Keeps only the columns (variables) we need.
    3. Converts all feature and target columns to numbers.
    4. Drops rows with no covariate-matched country (needed to assign a
       country fold for cross-validation).
    5. Assigns each country a numeric fold ID for cross-validation.

    Missing outcome/weight values, zero-or-negative weights, and exact
    duplicate rows are no longer handled here — they are already removed
    upstream in 04a/04b_*_preparing_training_dataframes.qmd
    (join_and_save_one_training_dataset()), so every model (this script, the
    drinking-water TabPFN script, and the RF scripts) trains on the same
    cleaned data. Missing feature/covariate values are also NOT dropped here:
    TabPFN handles missing feature values natively (see fit_tabpfn() /
    predict_lmics()).
    """

    # Step 1: Remove excluded countries by checking the outcome column name
    if exclude_countries:
        for country in exclude_countries:
            mask = df[OUTCOME_COL].astype(str).str.startswith(country, na=False)
            n = mask.sum()
            if n > 0:
                print(f"  Removed {n} {country} rows")
            df = df[~mask].copy()

    # Step 2: Only keep feature columns that actually exist in this dataset
    valid_features = [c for c in feature_cols if c in df.columns]
    n_skipped = len(feature_cols) - len(valid_features)
    if n_skipped:
        warnings.warn(f"  {n_skipped} feature(s) not in data — skipped")

    # Step 3: Select only the columns we need (features + metadata columns)
    keep = valid_features + [
        TARGET_COL, COUNTRY_COL, REGION_COL, YEAR_COL,
        WEIGHT_COL, SDG_COL, INCOME_COL,
    ]
    keep     = [c for c in keep if c in df.columns]
    model_df = df[keep].copy()

    # Step 4: Convert feature/target/weight columns to numeric (non-numeric → NaN)
    for col in valid_features + [TARGET_COL, WEIGHT_COL]:
        if col in model_df.columns:
            model_df[col] = pd.to_numeric(model_df[col], errors="coerce")

    # Step 5: Drop rows with no covariate-matched country (COUNTRY_COL is
    # "country_cov", set during the crosswalk join — distinct from
    # country_outcome, which 04a/04b already guarantee is non-missing).
    # Needed because country_fold below requires a non-missing country.
    n_before = len(model_df)
    model_df = model_df.dropna(subset=[COUNTRY_COL]).copy()
    n_dropped = n_before - len(model_df)
    if n_dropped:
        print(f"  Dropped {n_dropped} row(s) with no covariate-matched country")

    # Assign a unique integer ID (fold number) to each country, used later
    # when we hold out one country at a time during cross-validation
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
# 6.  Metrics helpers — measure how accurate predictions are
# -------------------------------------------------------

def compute_metrics(y_true, y_pred, weights=None):
    """
    Calculate three standard accuracy measures. When `weights` (PSU survey
    weights for the evaluated rows) is given, the metrics are PSU-weighted;
    with weights=None they are unweighted.
    - MAE  (Mean Absolute Error):  average size of prediction mistakes
    - RMSE (Root Mean Squared Error): similar to MAE but penalises large errors more
    - R²   (R-squared): 1 = perfect predictions, 0 = no better than guessing the mean
    Used during the feature-set comparison stage. Passing the held-out PSU
    weights makes the reported R²/MAE/RMSE population-weighted, consistent with
    the survey weights applied during training and with the LOCO metrics.
    """
    has_var = len(np.unique(y_true)) > 1  # can't compute R² if all values identical
    return {
        "mae":  float(mean_absolute_error(y_true, y_pred, sample_weight=weights)),
        "rmse": float(mean_squared_error(y_true, y_pred, sample_weight=weights) ** 0.5),
        "r2":   float(r2_score(y_true, y_pred, sample_weight=weights)) if has_var else np.nan,
        "n":    len(y_true),
    }


def compute_metrics_full(y_true, y_pred, weights):
    """
    Calculate both weighted and unweighted accuracy measures.
    Weighted metrics give more importance to data points from larger surveys
    (larger PSU weight = represents more people).
    Used for the final cross-validation evaluation.
    """
    has_var = len(np.unique(y_true)) > 1  # can't compute R² if all values identical
    return {
        "weighted_mae":    mean_absolute_error(y_true, y_pred, sample_weight=weights),
        "weighted_rmse":   mean_squared_error(y_true, y_pred, sample_weight=weights) ** 0.5,
        "weighted_r2":     r2_score(y_true, y_pred, sample_weight=weights) if has_var else np.nan,
        "unweighted_mae":  mean_absolute_error(y_true, y_pred),
        "unweighted_rmse": mean_squared_error(y_true, y_pred) ** 0.5,
        "unweighted_r2":   r2_score(y_true, y_pred) if has_var else np.nan,
    }


# -------------------------------------------------------
# 7.  TabPFN fit helper — train the machine learning model
# -------------------------------------------------------

def clear_memory():
    # Free up RAM after each model is trained — important when running many folds
    gc.collect()


def fit_tabpfn(model, X_train, y_train, sample_weight):
    """
    Train a TabPFN model (a type of AI/neural network designed for small tabular data).
    - First tries to pass survey weights so larger surveys have more influence.
    - If the installed version of TabPFN doesn't support weights, trains without them.
    Returns the trained model and a flag indicating whether weights were used.
    """
    # Check whether this version of TabPFN accepts a sample_weight argument
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
            return model, True   # weights were used
        except TypeError:
            pass

    # Fall back to training without weights
    model.fit(X_train, y_train)
    return model, False


# -------------------------------------------------------
# 8.  Stratified CV folds — loaded from the shared definition
#
# Folds are generated once by
#   01_data_preparation/05b_generate_stratified_cv_folds.py
# and read here so that BOTH this script and 01a_sanitation_modelling_RF.qmd
# evaluate on IDENTICAL held-out country sets. (R and NumPy RNGs diverge even
# with equal seeds, so folds must be shared via a file, not re-sampled.)
# Each fold is a set of whole held-out countries, stratified to mirror the
# SDG-region mix of the prediction space and excluding high-income countries.
# -------------------------------------------------------

CV_FOLDS_PATH = "data/processed/cv_folds/stratified_cv_folds.csv"
if not os.path.exists(CV_FOLDS_PATH):
    raise FileNotFoundError(
        f"CV fold definitions not found: {CV_FOLDS_PATH}\n"
        "Run 01_data_preparation/05b_generate_stratified_cv_folds.py first "
        "(no API calls — pure sampling)."
    )

_fold_defs = pd.read_csv(CV_FOLDS_PATH)
fold_country_lists = [
    grp["country"].tolist()
    for _, grp in _fold_defs.sort_values("fold").groupby("fold", sort=True)
]
N_REPEATS = len(fold_country_lists)

# Training data (Indonesia excluded, matching 05b) — only for fold diagnostics
_bs_raw = pd.read_csv(os.path.join(DATA_DIR, TASKS["basic_sanitation"]["filename"]))
_bs_raw = _bs_raw[
    ~_bs_raw[OUTCOME_COL].astype(str).str.startswith("Indonesia", na=False)
]
total_train_regions = len(_bs_raw)

print(f"\nLoaded {N_REPEATS} folds from {CV_FOLDS_PATH}")
print("Fold diagnostics:")
for i, countries in enumerate(fold_country_lists, 1):
    n_reg = int(_bs_raw[_bs_raw[COUNTRY_COL].isin(countries)].shape[0])
    pct   = 100 * n_reg / total_train_regions
    print(f"  Fold {i}: {len(countries)} countries, {n_reg} regions ({pct:.1f}%)")


# -------------------------------------------------------
# 9.  Feature set comparison — find the best shortlist size
# -------------------------------------------------------

def run_one_fold(training_df, held_out_countries, features):
    """
    Train a model on all countries EXCEPT the held-out ones,
    then test it on the held-out countries.
    Returns PSU-weighted accuracy metrics (or None if the test set is empty).
    This is the core "train on some, test on others" evaluation loop.
    """
    train_df = training_df[~training_df[COUNTRY_COL].isin(held_out_countries)].copy()
    test_df  = training_df[ training_df[COUNTRY_COL].isin(held_out_countries)].copy()

    if len(test_df) == 0:
        return None

    # Use only features that exist in both train and test sets
    valid = [f for f in features if f in train_df.columns]
    X_tr  = train_df[valid].to_numpy(dtype=float)
    y_tr  = train_df[TARGET_COL].to_numpy(dtype=float)
    w_tr  = train_df[WEIGHT_COL].to_numpy(dtype=float)
    X_te  = test_df[valid].to_numpy(dtype=float)
    y_te  = test_df[TARGET_COL].to_numpy(dtype=float)
    w_te  = test_df[WEIGHT_COL].to_numpy(dtype=float)   # held-out PSU weights

    # Feature values are NOT filtered for missingness here — TabPFN handles
    # missing feature values natively (see fit_tabpfn() / predict_lmics()).
    if len(X_tr) == 0 or len(X_te) == 0:
        return None

    # Normalise weights so they average to 1 (helps model training stability)
    w_tr_norm = w_tr / w_tr.mean()
    model = TabPFNRegressor()
    model, _ = fit_tabpfn(model, X_tr, y_tr, sample_weight=w_tr_norm)
    preds = np.asarray(model.predict(X_te)).reshape(-1)

    del model; clear_memory()  # free RAM immediately after use
    # PSU-weighted metrics on the held-out rows (consistent with weighted training)
    return compute_metrics(y_te, preds, weights=w_te)


def run_feature_set_comparison(training_df, outcome_name):
    """
    For each feature shortlist size (k5, k10, ..., k100):
      - Run all 5 test folds
      - Average the accuracy metrics across folds
    Returns a summary table so we can choose the best k.
    """
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
            print(".", end="", flush=True)  # progress dots
        print()

        if not repeat_results:
            continue

        # Summarise across the 5 folds: mean and standard deviation of each metric
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


# Load and clean both training datasets, then run the comparison
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
# 10. Print and save feature set comparison results
# -------------------------------------------------------

# Display the comparison table sorted by R² (best at top for each outcome)
print("\nStratified CV — feature set comparison:")
print(
    cv_comparison
    .sort_values(["outcome", "mean_r2"], ascending=[True, False])
    .to_string(index=False)
)

# Save the table to a CSV file for later reference
cv_comparison.to_csv(
    os.path.join(OUTPUT_DIR, "tabpfn_feature_set_cv_comparison.csv"),
    index=False,
)
print(f"\nSaved: {OUTPUT_DIR}/tabpfn_feature_set_cv_comparison.csv")


# -------------------------------------------------------
# 10b. Plot: RF vs TabPFN feature-set comparison (R² by feature set)
#
# Overlays the Random Forest feature-set CV results (from 01a, read from
# feature_set_cv_comparison.csv) with the TabPFN results computed above, on one
# plot. The comparison is fair: both use the SAME stratified folds (05b) and the
# SAME unweighted R² metric. Requires 01a to have run first for the RF CSV; if
# that file is absent, only the TabPFN curves are drawn (with a warning).
# -------------------------------------------------------

import matplotlib.pyplot as plt

_plot_dir = os.path.join(OUTPUT_DIR, "plots")
os.makedirs(_plot_dir, exist_ok=True)

_rf_path = os.path.join(OUTPUT_DIR, "feature_set_cv_comparison.csv")
_frames  = [cv_comparison.assign(model="TabPFN")]
if os.path.exists(_rf_path):
    _frames.append(pd.read_csv(_rf_path).assign(model="Random Forest"))
else:
    warnings.warn(
        f"RF comparison file not found ({_rf_path}); plotting TabPFN only. "
        "Run 01a_sanitation_modelling_RF.qmd to add the Random Forest curves."
    )
_combined = pd.concat(_frames, ignore_index=True)

# x-axis: feature sets ordered by number of features (k5, k10, ..., k100)
_order = (_combined[["feature_set", "n_features"]]
          .drop_duplicates().sort_values("n_features")["feature_set"].tolist())
_xpos  = {fs: i for i, fs in enumerate(_order)}

_outcomes = sorted(_combined["outcome"].unique())
_colors   = dict(zip(_outcomes, plt.cm.tab10.colors))
_mstyle   = {
    "Random Forest": dict(linestyle="--", marker="s"),
    "TabPFN":        dict(linestyle="-",  marker="o"),
}

fig, ax = plt.subplots(figsize=(8, 5))
for (oc, model), grp in _combined.groupby(["outcome", "model"]):
    grp = grp.assign(_x=grp["feature_set"].map(_xpos)).sort_values("_x")
    ax.errorbar(
        grp["_x"], grp["mean_r2"], yerr=grp["sd_r2"],
        color=_colors[oc], capsize=3, alpha=0.9,
        label=f"{oc} — {model}",
        **_mstyle.get(model, dict(linestyle="-", marker="o")),
    )
ax.set_xticks(range(len(_order)))
ax.set_xticklabels(_order)
ax.set_xlabel("Feature set (k clusters)")
ax.set_ylabel("PSU-weighted mean R² (±1 SD across repeats)")
ax.set_title("Stratified CV performance by feature set — RF vs TabPFN (PSU-weighted)")
ax.grid(True, alpha=0.3)
ax.legend(fontsize=8)
plt.tight_layout()
_out = os.path.join(_plot_dir, "feature_set_cv_rf_vs_tabpfn_r2.png")
plt.savefig(_out, dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved: {_out}")


# -------------------------------------------------------
# STOP — manual checkpoint before the API-heavy final models
#
# Halts a top-to-bottom run here so the LOCO-CV / prediction sections (12+)
# don't fire automatically. Review the comparison table + plot above, set
# FINAL_K_* in Section 11, then run Section 12 onward.
# Set STOP_AFTER_FEATURE_COMPARISON = False to run straight through.
# -------------------------------------------------------

STOP_AFTER_FEATURE_COMPARISON = True

if STOP_AFTER_FEATURE_COMPARISON:
    raise SystemExit(
        "\nFeature-set comparison complete. Review the table/plot, set "
        "FINAL_K_BASIC_SANITATION / FINAL_K_OPEN_DEFECATION in Section 11, "
        "then run from Section 12 onward (or set "
        "STOP_AFTER_FEATURE_COMPARISON = False to run through)."
    )


# -------------------------------------------------------
# 11. [MANUAL STEP] Choose the final feature shortlist size
#
# Look at the table printed above.
# Set the two k values below to whatever performed best,
# then continue running from Section 12 onwards.
# -------------------------------------------------------

FINAL_K_BASIC_SANITATION = 45   # <-- change this after reviewing Section 10 output
FINAL_K_OPEN_DEFECATION  = 90   # <-- change this after reviewing Section 10 output

# Safety check: both values must be set before continuing
if FINAL_K_BASIC_SANITATION is None or FINAL_K_OPEN_DEFECATION is None:
    raise ValueError(
        "Set FINAL_K_BASIC_SANITATION and FINAL_K_OPEN_DEFECATION "
        "before running Sections 12 and 13."
    )

# Look up the actual feature lists for the chosen k values
final_features_bs = feature_sets[f"k{FINAL_K_BASIC_SANITATION}"]
final_features_od = feature_sets[f"k{FINAL_K_OPEN_DEFECATION}"]

print(f"\nBasic sanitation: k={FINAL_K_BASIC_SANITATION} "
      f"({len(final_features_bs)} features)")
print(f"Open defecation:  k={FINAL_K_OPEN_DEFECATION} "
      f"({len(final_features_od)} features)")


# -------------------------------------------------------
# 12. LOCO-CV helper — Leave-One-Country-Out cross-validation
# -------------------------------------------------------

def run_loco_cv(model_df, feature_cols, outcome_name, final_k):
    """
    Full LOCO-CV: train on all countries except one, predict for that one country,
    then rotate through every country in turn.
    This gives an honest estimate of how well the model generalises to unseen countries.

    Returns:
    - fold_df:    per-country accuracy metrics
    - overall_df: single-row summary across all countries
    - oof_df:     the actual predicted vs observed values for every row
    """
    X       = model_df[feature_cols].to_numpy(dtype=float)
    y       = model_df[TARGET_COL].to_numpy(dtype=float)
    groups  = model_df["country_fold"].to_numpy()   # country IDs used to split folds
    weights = model_df[WEIGHT_COL].to_numpy(dtype=float)

    oof_preds   = np.full(len(model_df), np.nan)   # will store all out-of-fold predictions
    logo        = LeaveOneGroupOut()                # sklearn splitter: one country out each time
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
        w_tr_norm    = w_tr / w_tr.mean()   # normalise weights

        model = TabPFNRegressor()
        model, used_sw = fit_tabpfn(model, X_tr, y_tr, sample_weight=w_tr_norm)
        used_sw_all.append(used_sw)

        preds = np.asarray(model.predict(X_val)).reshape(-1)
        oof_preds[val_idx] = preds   # store predictions in the correct row positions

        del model; clear_memory()

        # Record per-country accuracy stats
        fold_rows.append({
            "outcome":          outcome_name,
            "fold":             fold,
            "held_out_country": held_out,
            "n_train_rows":     len(train_idx),
            "n_val_rows":       len(val_idx),
            **compute_metrics(y_val, preds),
        })

    # Sanity check: every row should have received a prediction
    if np.isnan(oof_preds).any():
        raise RuntimeError(
            f"Missing OOF predictions: {np.isnan(oof_preds).sum()} rows"
        )

    fold_df = pd.DataFrame(fold_rows)

    # Single summary row with overall weighted and unweighted metrics
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

    # Build a detailed row-level output file with predicted vs observed values
    oof_df = model_df[
        [COUNTRY_COL, REGION_COL, YEAR_COL, TARGET_COL, WEIGHT_COL, "country_fold"]
    ].copy()
    oof_df.insert(0, "outcome", outcome_name)
    oof_df["pred_tabpfn"]      = oof_preds
    oof_df["error_tabpfn"]     = oof_df[TARGET_COL] - oof_preds         # signed error
    oof_df["abs_error_tabpfn"] = np.abs(oof_df[TARGET_COL] - oof_preds) # unsigned error

    return fold_df, overall_df, oof_df


# -------------------------------------------------------
# 13. Final model — basic sanitation
# -------------------------------------------------------

print(f"\n{'='*60}")
print(f"Final model: basic_sanitation  (k={FINAL_K_BASIC_SANITATION})")
print(f"{'='*60}")

# Reload and clean the data using only the final chosen feature set
bs_model_df, bs_features = prepare_model_data(
    pd.read_csv(os.path.join(DATA_DIR, TASKS["basic_sanitation"]["filename"])),
    feature_cols=final_features_bs,
    exclude_countries=TASKS["basic_sanitation"]["exclude_countries"],
)

# Run the full LOCO-CV and get results
bs_fold_df, bs_overall_df, bs_oof_df = run_loco_cv(
    bs_model_df, bs_features, "basic_sanitation", FINAL_K_BASIC_SANITATION
)

# Print summary metrics to screen
print("\n  LOCO-CV metrics:")
print(bs_overall_df[[
    "outcome", "feature_set", "n_rows", "n_features", "n_countries",
    "unweighted_mae", "unweighted_rmse", "unweighted_r2",
]].to_string(index=False))

# Save three CSV output files: per-country, overall summary, and row-level predictions
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
# 14. Final model — open defecation (same process as Section 13)
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
# 15. Combined summary — merge both outcomes into one table
# -------------------------------------------------------

# Stack the two outcome summaries and save as a single file
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
# 16. Quantile predictions — estimate uncertainty ranges
#
# Re-runs LOCO-CV but asks TabPFN to output prediction intervals
# (e.g. "we think the true value is between 30% and 60%") rather than
# a single point estimate.
# These are raw model intervals — not statistically guaranteed.
# If this version of TabPFN doesn't support quantile output, the section
# is skipped with a warning.
# -------------------------------------------------------

# The percentile levels we want: 5th, 10th, 25th, 50th (median), 75th, 90th, 95th
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
    """
    Same LOCO-CV loop as Section 12, but requests multiple quantile predictions
    per data point instead of a single value.
    Also computes empirical coverage: how often does the true value actually
    fall inside the predicted interval? (Ideally 90% for a 90% interval.)
    """
    if quantiles is None:
        quantiles = QUANTILE_LEVELS

    X       = model_df[feature_cols].to_numpy(dtype=float)
    y       = model_df[TARGET_COL].to_numpy(dtype=float)
    groups  = model_df["country_fold"].to_numpy()
    weights = model_df[WEIGHT_COL].to_numpy(dtype=float)

    n_q   = len(quantiles)
    oof_q = np.full((len(model_df), n_q), np.nan)  # one column per quantile level
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

        # Ask TabPFN for quantile outputs instead of a single prediction
        try:
            q_preds = model.predict(
                X_val, output_type="quantiles", quantiles=quantiles,
            )
            q_preds = np.asarray(q_preds)
            # Ensure shape is (n_rows, n_quantiles) — transpose if needed
            if q_preds.ndim == 2 and q_preds.shape[0] == n_q and q_preds.shape[1] != n_q:
                q_preds = q_preds.T
        except (TypeError, AttributeError) as exc:
            del model; clear_memory()
            raise RuntimeError(
                "TabPFN client does not support quantile output in this version."
            ) from exc

        oof_q[val_idx] = q_preds
        del model; clear_memory()

    # Build column names like "q05", "q10", ..., "q95"
    q_col_names = [f"q{int(q * 100):02d}" for q in quantiles]
    oof_df = model_df[
        [COUNTRY_COL, REGION_COL, YEAR_COL, TARGET_COL, WEIGHT_COL, "country_fold"]
    ].copy().reset_index(drop=True)
    oof_df.insert(0, "outcome", outcome_name)
    for i, col in enumerate(q_col_names):
        oof_df[col] = oof_q[:, i]

    # Compute interval coverage: for each held-out country, check how often
    # the observed value falls inside the 80% and 90% prediction intervals
    coverage_rows = []
    for (country, fold_id), grp in oof_df.groupby([COUNTRY_COL, "country_fold"]):
        y_g = grp[TARGET_COL].to_numpy(dtype=float)
        w_g = grp[WEIGHT_COL].to_numpy(dtype=float)
        for lo_q, hi_q, label in [
            ("q05", "q95", "90pct"),   # 90% prediction interval
            ("q10", "q90", "80pct"),   # 80% prediction interval
        ]:
            if lo_q not in grp.columns or hi_q not in grp.columns:
                continue
            lo      = grp[lo_q].to_numpy(dtype=float)
            hi      = grp[hi_q].to_numpy(dtype=float)
            covered = (y_g >= lo) & (y_g <= hi)  # True if true value is inside interval
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

# Run quantile LOCO-CV for both outcomes and save results
for outcome_name, cfg in QUANTILE_TASKS.items():
    print(f"\n  Outcome: {outcome_name}")
    try:
        q_oof_df, q_cov_df = run_loco_cv_tabpfn_quantiles(
            cfg["model_df"], cfg["features"], outcome_name
        )
        # Save row-level quantile predictions
        q_oof_df.to_csv(
            os.path.join(OUTPUT_DIR, f"{cfg['prefix']}_tabpfn_quantile_oof.csv"),
            index=False,
        )
        # Save per-country coverage diagnostics
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
# 17. Diagnostic plots for quantile predictions
#
# Produces four charts to assess how reliable the uncertainty
# intervals are. Can be re-run independently once Section 16
# has saved its output files.
#
# Plot A: Are wider intervals associated with larger errors?
# Plot B: Observed vs predicted (median) with 90% interval bars
# Plot C: Calibration — do 90% intervals actually capture 90% of truth?
# Plot D: Residuals vs observed with interval error bars
# -------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Create an output folder for plots if it doesn't already exist
PLOT_DIR = os.path.join(OUTPUT_DIR, "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

# Display labels and colours for each outcome
OUTCOME_CFG = {
    "basic_sanitation": {"label": "Basic sanitation", "colour": "#2166ac"},
    "open_defecation":  {"label": "Open defecation",  "colour": "#d6604d"},
}

Q_LEVELS    = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
Q_COL_NAMES = [f"q{int(q * 100):02d}" for q in Q_LEVELS]


def load_quantile_oof(prefix):
    """
    Load the quantile prediction CSV saved in Section 16.
    Adds derived columns for error, 80% interval width, and 90% interval width.
    """
    path = os.path.join(OUTPUT_DIR, f"{prefix}_tabpfn_quantile_oof.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Quantile OOF file not found: {path}")
    df = pd.read_csv(path)
    df["error"]    = df[TARGET_COL] - df["q50"]    # observed minus median prediction
    df["width_80"] = df["q90"] - df["q10"]          # width of 80% interval
    df["width_90"] = df["q95"] - df["q05"]          # width of 90% interval
    df["w_norm"]   = df[WEIGHT_COL] / df[WEIGHT_COL].mean()  # normalised weight for dot size
    return df


# Load available quantile files; skip with a warning if missing
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
    # If the model is well-calibrated, it should produce wider intervals exactly
    # when it is also making larger errors (uncertainty correlates with difficulty).
    fig, axes = plt.subplots(1, len(dfs), figsize=(6 * len(dfs), 5))
    if len(dfs) == 1:
        axes = [axes]

    for ax, (name, df) in zip(axes, dfs.items()):
        cfg = OUTCOME_CFG[name]
        s   = np.clip(df["w_norm"].to_numpy() * 18, 2, 120)  # dot size ∝ survey weight

        # Scatter: each dot is one sub-national region
        ax.scatter(df["error"], df["width_90"], s=s, alpha=0.45,
                   linewidths=0, color=cfg["colour"], label="90 % PI", zorder=3)
        ax.scatter(df["error"], df["width_80"], s=s, alpha=0.30,
                   linewidths=0, color=cfg["colour"], label="80 % PI", zorder=2)

        # Overlay a weighted running-average trend line for each interval width
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

        ax.axvline(0, color="grey", lw=1.0, ls=":", zorder=4)  # zero-error reference line
        ax.set_xlabel("Residual  (observed − q50)", fontsize=11)
        ax.set_ylabel("Prediction interval width", fontsize=11)
        ax.set_title(cfg["label"], fontsize=12, fontweight="bold")
        ax.legend(fontsize=8, framealpha=0.7)
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle(
        "TabPFN: interval width vs residual (observed − q50)\n(point size ∝ PSU weight)",
        fontsize=13, y=1.02,
    )
    plt.tight_layout()
    out_a = os.path.join(PLOT_DIR, "tabpfn_quantile_width_vs_error.png")
    plt.savefig(out_a, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_a}")


    # ── Plot B: observed vs predicted with 90% interval bars ─────────────────
    # Each dot is a sub-national region. Vertical bars show the 90% interval.
    # Dots near the diagonal dashed line = accurate predictions.
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

        # Error bars extend from the median prediction to the 5th/95th quantiles
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
                zorder=4, label="y = x")  # perfect-prediction reference line
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
    # A perfectly calibrated model's line should follow the diagonal.
    # If the line curves below diagonal → overconfident (intervals too narrow).
    # If the line curves above diagonal → underconfident (intervals too wide).
    fig, ax = plt.subplots(figsize=(6, 6))

    for name, df in dfs.items():
        cfg     = OUTCOME_CFG[name]
        w       = df[WEIGHT_COL].to_numpy(dtype=float)
        y       = df[TARGET_COL].to_numpy(dtype=float)
        missing = [c for c in Q_COL_NAMES if c not in df.columns]
        if missing:
            print(f"  Skipping calibration for {name} — missing: {missing}")
            continue

        # For each quantile level, compute the fraction of true values below it
        empirical = []
        for q, col in zip(Q_LEVELS, Q_COL_NAMES):
            below = (y < df[col].to_numpy(dtype=float)).astype(float)
            empirical.append(float(np.average(below, weights=w)))

        ax.plot(Q_LEVELS, empirical, marker="o", markersize=6, lw=2,
                color=cfg["colour"], label=cfg["label"], zorder=3)

        # Annotate the 90th percentile coverage value.
        # A white background box + high zorder keep the number legible so it is
        # never hidden underneath the calibration lines.
        emp_90 = empirical[Q_LEVELS.index(0.90)]
        ax.annotate(
            f"{emp_90:.2f}",
            xy=(0.90, emp_90),
            xytext=(0.79, emp_90 - 0.07),
            fontsize=8, color=cfg["colour"], zorder=6,
            bbox=dict(boxstyle="round,pad=0.15", fc="white",
                      ec="none", alpha=0.85),
            arrowprops=dict(arrowstyle="-", color=cfg["colour"], lw=0.8,
                            zorder=6),
        )

    ax.plot([0, 1], [0, 1], color="black", lw=1.2, ls="--",
            zorder=2, label="Perfect calibration")
    # Shade regions to label overconfident vs underconfident zones.
    # The zone labels sit deep in their respective triangles (well away from the
    # diagonal and the data lines) and carry a white background + high zorder so
    # they are never covered by the graph lines.
    ax.fill_between([0, 1], [0, 1], [1, 1], alpha=0.06, color="steelblue")
    ax.fill_between([0, 1], [0, 0], [0, 1], alpha=0.06, color="tomato")
    ax.text(0.78, 0.32, "Overconfident", fontsize=8, zorder=5,
            color="tomato", ha="center", style="italic",
            bbox=dict(boxstyle="round,pad=0.2", fc="white",
                      ec="none", alpha=0.7))
    ax.text(0.22, 0.78, "Underconfident", fontsize=8, zorder=5,
            color="steelblue", ha="center", style="italic",
            bbox=dict(boxstyle="round,pad=0.2", fc="white",
                      ec="none", alpha=0.7))

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks(Q_LEVELS)
    ax.set_xticklabels([f"{int(q*100)}th" for q in Q_LEVELS], fontsize=9)
    ax.set_xlabel("Nominal quantile level", fontsize=11)
    ax.set_ylabel("Empirical proportion below predicted quantile", fontsize=11)
    ax.legend(fontsize=9, framealpha=0.8, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)

    # Save the recreated figure (title removed; labels no longer covered by
    # the graph lines) into a versioned "v2" sub-folder.
    V2_DIR = os.path.join(PLOT_DIR, "v2")
    os.makedirs(V2_DIR, exist_ok=True)

    plt.tight_layout()
    out_c = os.path.join(V2_DIR, "tabpfn_quantile_calibration.png")
    plt.savefig(out_c, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_c}")


    # ── Plot D: residuals vs observed ─────────────────────────────────────────
    # Residual = median prediction minus truth.
    # Ideally scattered randomly around zero across all observed values.
    # A systematic trend (e.g. always over-predicting at high values) suggests bias.
    fig, axes = plt.subplots(1, len(dfs), figsize=(6 * len(dfs), 5))
    if len(dfs) == 1:
        axes = [axes]

    for ax, (name, df) in zip(axes, dfs.items()):
        cfg      = OUTCOME_CFG[name]
        obs      = df[TARGET_COL].to_numpy(dtype=float)
        resid    = df["error"].to_numpy(dtype=float)
        lo_resid = obs - df["q95"].to_numpy(dtype=float)  # lower residual bound (observed - upper PI)
        hi_resid = obs - df["q05"].to_numpy(dtype=float)  # upper residual bound (observed - lower PI)
        w        = df[WEIGHT_COL].to_numpy(dtype=float)
        s        = np.clip(df["w_norm"].to_numpy() * 18, 2, 120)

        yerr_lo = np.clip(resid - lo_resid, 0, None)
        yerr_hi = np.clip(hi_resid - resid, 0, None)

        ax.errorbar(obs, resid, yerr=[yerr_lo, yerr_hi],
                    fmt="none", ecolor=cfg["colour"], alpha=0.15,
                    lw=0.6, zorder=1)
        ax.scatter(obs, resid, s=s, color=cfg["colour"],
                   alpha=0.55, zorder=2, linewidths=0)

        # Overlay a simple running average to highlight any systematic trend
        sort_idx = np.argsort(obs)
        obs_s    = obs[sort_idx]
        resid_s  = resid[sort_idx]
        window   = max(1, len(obs_s) // 10)
        running  = np.convolve(resid_s, np.ones(window) / window, mode="valid")
        x_run    = obs_s[window // 2: window // 2 + len(running)]
        ax.plot(x_run, running, color="black", lw=1.5,
                alpha=0.7, label="Running mean")

        ax.axhline(0,      color="black", lw=1.2, ls="--", label="Zero residual")
        ax.axhline( 0.10,  color="grey",  lw=0.5, ls=":",  alpha=0.5)  # ±10% guide lines
        ax.axhline(-0.10,  color="grey",  lw=0.5, ls=":",  alpha=0.5)
        ax.set_xlim(0, 1)
        ax.set_xlabel("Observed proportion", fontsize=11)
        ax.set_ylabel("Residual (observed − q50)", fontsize=11)
        ax.set_title(cfg["label"], fontsize=12, fontweight="bold")
        ax.legend(fontsize=8, framealpha=0.8)
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle(
        "Residuals vs observed  (point size ∝ PSU weight;\n"
        "error bars = observed − q95 to observed − q05)",
        fontsize=12, y=1.02,
    )
    plt.tight_layout()
    out_d = os.path.join(PLOT_DIR, "tabpfn_residuals_vs_observed.png")
    plt.savefig(out_d, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_d}")


# -------------------------------------------------------
# 18. Final model predictions across LMICs
#
# Trains TabPFN on ALL training data (every country retained),
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
# -------------------------------------------------------

PRED_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "predictions")
os.makedirs(PRED_OUTPUT_DIR, exist_ok=True)

# Columns that must be present in the prediction data:
#   - used as model features (country-level covariates)
#   - needed for downstream analysis / mapping
REQUIRED_PRED_COLS = {
    "features":        COUNTRY_LEVEL_FEATURES,          # must be present for modelling
    "identifiers":     ["GID_1", "NAME_0", "NAME_1"],   # shapefile join / mapping
    "stratification":  ["sdg_region", "wb_income_group", "fragile_context"],
}

# Reload prediction data (same source as cluster analysis in 01_cluster_analysis.qmd)
pred_all = pd.read_csv(PRED_COVARIATES_PATH)

# Validate required columns
_pred_cols = set(pred_all.columns)
_missing_features = [c for c in REQUIRED_PRED_COLS["features"] if c not in _pred_cols]
_missing_ids      = [c for c in REQUIRED_PRED_COLS["identifiers"] if c not in _pred_cols]
_missing_strat    = [c for c in REQUIRED_PRED_COLS["stratification"] if c not in _pred_cols]

if _missing_features:
    raise ValueError(
        f"Country-level covariates missing from prediction data.\n"
        f"These are required model inputs and must be joined in "
        f"05_prepare_prediction_data.qmd before predictions can run:\n"
        f"  {_missing_features}"
    )
if _missing_ids:
    raise ValueError(
        f"Identifier columns missing from prediction data (needed for shapefile join / mapping):\n"
        f"  {_missing_ids}\n"
        f"Ensure GID_1 is set in the GEE sampling notebook and "
        f"05_prepare_prediction_data.qmd exports it."
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


def predict_lmics(model_df, feature_cols, outcome_name, pred_df,
                  quantiles=None):
    """
    Train TabPFN on the complete training dataset (all countries) then
    generate quantile predictions for every row in pred_df.

    Parameters
    ----------
    model_df     : cleaned training dataframe (output of prepare_model_data)
    feature_cols : list of feature column names to use
    outcome_name : string label for this outcome
    pred_df      : prediction-space dataframe (LMIC rows only)
    quantiles    : list of quantile levels; defaults to [0.05, 0.50, 0.95]

    Returns
    -------
    DataFrame with all columns from pred_df plus:
        outcome, median, pi90_lower, pi90_upper
    Rows where features are missing receive NaN predictions.
    """
    if quantiles is None:
        quantiles = PRED_QUANTILES

    # ── Training data ────────────────────────────────────────────────
    valid_train = [f for f in feature_cols if f in model_df.columns]
    # TabPFN handles NaN features natively in both training and prediction.
    # Only drop rows where the target or weight is missing (those can't be used).
    X_tr = model_df[valid_train].to_numpy(dtype=float)
    y_tr = model_df[TARGET_COL].to_numpy(dtype=float)
    w_tr = model_df[WEIGHT_COL].to_numpy(dtype=float)

    valid_mask    = ~(np.isnan(y_tr) | np.isnan(w_tr))
    X_tr, y_tr, w_tr = X_tr[valid_mask], y_tr[valid_mask], w_tr[valid_mask]
    w_norm        = w_tr / w_tr.mean()

    print(f"  Training on {len(X_tr):,} rows "
          f"({model_df[COUNTRY_COL].nunique()} countries) …")

    model = TabPFNRegressor()
    model, used_sw = fit_tabpfn(model, X_tr, y_tr, sample_weight=w_norm)
    print(f"  Sample weights used in training: {used_sw}")

    # ── Prediction data ──────────────────────────────────────────────
    # All training features must be present in the prediction data.
    # Missing country-level covariates are a hard error (they are required
    # model inputs that should have been joined in 05_prepare_prediction_data.qmd).
    valid_pred          = [f for f in valid_train if f in pred_df.columns]
    missing             = set(valid_train) - set(valid_pred)
    missing_country_lvl = [f for f in missing if f in COUNTRY_LEVEL_FEATURES]
    missing_eo          = [f for f in missing if f not in COUNTRY_LEVEL_FEATURES]

    if missing_country_lvl:
        raise ValueError(
            f"{outcome_name}: country-level covariates are missing from the "
            f"prediction data. These must be joined in 05_prepare_prediction_data.qmd:\n"
            f"  {missing_country_lvl}"
        )
    if missing_eo:
        warnings.warn(
            f"{outcome_name}: {len(missing_eo)} EO feature(s) absent from prediction "
            f"data — excluded from model input: {missing_eo}"
        )

    # TabPFN handles NaN features natively — pass all rows directly.
    X_pred      = pred_df[valid_pred].to_numpy(dtype=float)
    q_col_names = [f"q{int(q * 100):02d}" for q in quantiles]
    out_df      = pred_df.copy().reset_index(drop=True)

    try:
        q_preds = model.predict(
            X_pred,
            output_type="quantiles",
            quantiles=quantiles,
        )
        q_preds = np.asarray(q_preds)
        # Ensure shape is (n_rows, n_quantiles) — transpose if needed
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

    # Rename quantile columns to human-readable names
    out_df = out_df.rename(columns={
        "q05": "pi90_lower",
        "q50": "median",
        "q95": "pi90_upper",
    })

    # Add outcome label, then reorder: identifiers → stratification → predictions
    # → remaining covariates.
    out_df.insert(0, "outcome", outcome_name)

    _IDENTIFIERS    = ["GID_1", "NAME_0", "NAME_1"]
    _STRATIFICATION = ["sdg_region", "wb_income_group", "fragile_context"]
    _PREDICTIONS    = ["median", "pi90_lower", "pi90_upper"]

    lead_cols = (
        ["outcome"]
        + [c for c in _IDENTIFIERS    if c in out_df.columns]
        + [c for c in _STRATIFICATION if c in out_df.columns]
        + [c for c in _PREDICTIONS    if c in out_df.columns]
    )
    other_cols = [c for c in out_df.columns if c not in lead_cols]
    return out_df[lead_cols + other_cols]


PRED_TASKS = {
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

print(f"\n{'='*60}")
print("Section 18 — Final model: LMIC predictions")
print(f"{'='*60}")

for outcome_name, cfg in PRED_TASKS.items():
    print(f"\n  Outcome: {outcome_name}")
    try:
        pred_out  = predict_lmics(
            cfg["model_df"], cfg["features"], outcome_name, pred_lmic
        )
        out_path  = os.path.join(
            PRED_OUTPUT_DIR,
            f"{cfg['prefix']}_tabpfn_lmic_predictions.csv",
        )
        pred_out.to_csv(out_path, index=False)
        n_valid   = pred_out["median"].notna().sum()
        pi_width  = (pred_out["pi90_upper"] - pred_out["pi90_lower"]).mean()
        print(f"  Saved: {out_path}  ({n_valid:,} / {len(pred_out):,} rows predicted)")
        print(f"  Median range : [{pred_out['median'].min():.3f}, "
              f"{pred_out['median'].max():.3f}]")
        print(f"  Mean PI90 width: {pi_width:.3f}")
    except RuntimeError as exc:
        warnings.warn(f"  Prediction skipped for {outcome_name}: {exc}")


# -------------------------------------------------------
# 19. Feature importance — SHAP values for the final models
# -------------------------------------------------------
# SHAP explains how each feature moves the model's prediction. TabPFN here is
# the CLOUD client, so we use a model-agnostic explainer that only needs the
# predict function. We use PermutationExplainer (see the note by RUN_SHAP for
# why, not KernelExplainer) — it is robust for a black-box model and makes API
# calls proportional to rows × permutation rounds × background size. Set
# RUN_SHAP = False to skip this section.
#
# The per-feature SHAP values feed the by-category contribution summary in
# Section 21 (grouped bar plot). No per-feature bar chart or beeswarm is
# produced — only the mean |SHAP| CSVs are saved.
#
# Outputs (written to the git repo, v2 folders — never switchdrive):
#   OUTPUT_DIR/{outcome}_tabpfn_shap_importance_k{K}.csv          (mean |SHAP| per feature)
#   OUTPUT_DIR/{outcome}_tabpfn_shap_importance_k{K}_seed{S}.csv  (per-seed, for variance checks)

RUN_SHAP          = True
# Run ONE outcome at a time (separate days) so a single run stays within the
# 100M/day TabPFN cap. Start with basic_sanitation; once its CSVs are saved,
# switch this to ["open_defecation"] and re-run (Sections 19 + 21). At the
# settings below (200 rows, bg=5): basic_sanitation ≈20M, open_defecation ≈79M
# — each fits a day, but NOT both together, so keep this list to one outcome.
SHAP_OUTCOMES     = ["basic_sanitation"]
# Suffix appended to all Section 19/21 SHAP output filenames. Section 21 also
# READS the importance CSV with this suffix, so it must match the run you want to
# plot:
#   ""      -> the existing files on disk (..._k45.csv) — use to re-plot those
#   "_n200" -> the new 200-row run (Section 19 writes ..._k45_n200.csv)
# Currently "_n200" for the new 200-row run (Section 19 writes ..._k45_n200.csv,
# Section 21 reads/plots them); set to "" to re-plot the earlier unsuffixed files.
SHAP_RUN_LABEL    = "_n250"
#
# Explainer choice — PermutationExplainer, NOT KernelExplainer.
# KernelExplainer estimates SHAP by solving a weighted least-squares over
# sampled coalitions; for a black-box model with tens of features that system
# is numerically ill-conditioned and the solve overflows to NaN (the shap
# _kernel.py "singular matrix" warnings — no amount of samples/L1 reliably fixed
# it here). PermutationExplainer computes the same Shapley values by averaging
# over feature-ordering permutations, with NO linear solve, so it cannot hit a
# singular matrix. It is the estimator shap.Explainer auto-selects for a plain
# predict function, and it is cheaper. Cost ≈
#   N_SHAP_EXPLAIN × SHAP_NPERM × (2·n_features + 1) × N_SHAP_BACKGROUND_K  rows.
# Robust sample of rows explained (capped at the training-set size at run time;
# the mean |SHAP| feeding the category shares is averaged over these). IDENTICAL
# for both outcomes so their category shares are directly comparable. Cost is
# ~linear in this: at bg=5, measured ≈99k credits/row for k=45, so 200 rows ≈20M
# (basic_sanitation); open defecation (k=90) is ~4×/row ≈79M — both fit the
# 100M/day cap individually. Check headroom with tabpfn_client.get_api_usage().
N_SHAP_EXPLAIN      = 250
# Permutation rounds per explained row. Each round is one exact forward+backward
# pass over a random feature ordering (2·n_features+1 model evals); more rounds
# = smoother per-row estimate at linear cost. The CATEGORY aggregation in
# Section 21 averages over many rows/features, so a few rounds are plenty.
SHAP_NPERM          = 3
# Background reference rows the explainer masks against (a small random real-row
# subsample). Only sets the baseline the model is compared against and multiplies
# cost linearly, so kept lean at 5 to fit open defecation (k=90) within the daily
# cap. Category-level shares stay robust at bg=5 (per-row noise averages out over
# the 200 explained rows); raise it for finer per-feature magnitudes at more cost.
N_SHAP_BACKGROUND_K = 5
SHAP_SEEDS        = [123]  # single seed — within daily API quota for one outcome
SHAP_DPI          = 300

SHAP_COLOURS = {"basic_sanitation": "#4393c3", "open_defecation": "#d6604d"}

# Human-readable feature labels — ported from 01a_sanitation_modelling_RF.qmd
# so these TabPFN SHAP figures are directly comparable to the RF ones.
FEATURE_LABEL_MAP = {
    "worldpop":                               "WorldPop population density",
    "worldpop_sum":                           "WorldPop population sum",
    "ghsl_population":                        "GHSL population density",
    "ghsl_population_sum":                    "GHSL population sum",
    "GHS_Population_Density":                 "GHS population density",
    "GPWv4_Population_Density":               "GPWv4 population density",
    "ghsl_built_surface":                    "Built surface fraction",
    "ghsl_urban_frac":                       "Urban fraction",
    "jrc_building_height":                    "Building height",
    "viirs_average":                          "Night-time lights",
    "gdp_per_capita_constant_2015_usd":       "GDP per capita",
    "secondary_education_duration_years":     "Secondary education duration",
    "ww_collection_percent":                  "Wastewater collection",
    "ww_treatment_percent":                   "Wastewater treatment",
    "ww_reuse_percent":                       "Wastewater reuse",
    "control_of_corruption":                  "Control of corruption",
    "governance_effectiveness":               "Government effectiveness",
    "political_stability":                    "Political stability",
    "regulatory_quality":                     "Regulatory quality",
    "rule_of_law":                            "Rule of law",
    "voice_and_accountability":               "Voice and accountability",
    "sanitation_basic":                       "JMP basic sanitation (national)",
    "open_defecation":                        "JMP open defecation (national)",
    "CGIAR_Aridity_Index":                    "Aridity index",
    "CGIAR_PET":                              "Potential evapotranspiration",
    "CHELSA_BIO_Annual_Mean_Temperature":     "Annual mean temperature",
    "CHELSA_BIO_Annual_Precipitation":        "Annual precipitation",
    "EarthEnvTopoMed_Elevation":              "Elevation",
    "EarthEnvTopoMed_Slope":                  "Slope",
    "FanEtAl_Depth_to_Water_Table_AnnualMean": "Depth to water table",
    "map_friction":                           "Travel friction",
    "WCS_Human_Footprint_2009":               "Human footprint",
    "CSP_Global_Human_Modification":          "Human modification",
}


def label_feature(name):
    """Readable label if mapped, else underscores -> spaces (matches the RF script)."""
    if name in FEATURE_LABEL_MAP:
        return FEATURE_LABEL_MAP[name]
    return " ".join(str(name).replace("_", " ").split())


def _shap_one_seed(model, X, countries, valid, seed):
    """
    Draw one random sample of explanation rows, build a small real-row
    background masker, run PermutationExplainer (no linear solve — robust for a
    black-box model), and return:
      - shap_vals        : (n_explain, n_features) signed SHAP array
      - X_explain        : DataFrame of explained rows
      - countries_explain: Series of country labels aligned to shap_vals rows
    """
    import shap

    rng               = np.random.default_rng(seed)
    n                 = len(X)
    ex_idx            = rng.choice(n, size=min(N_SHAP_EXPLAIN, n), replace=False)
    X_explain         = X.iloc[ex_idx].reset_index(drop=True)
    countries_explain = countries.iloc[ex_idx].reset_index(drop=True)

    # Background = small random subsample of REAL rows, wrapped in an Independent
    # masker. It only sets the baseline the model is compared against.
    n_bg       = min(N_SHAP_BACKGROUND_K, n)
    background = shap.sample(X, n_bg, random_state=seed)
    masker     = shap.maskers.Independent(background, max_samples=n_bg)

    def predict_np(arr):
        return np.asarray(model.predict(np.asarray(arr, dtype=float))).reshape(-1)

    # PermutationExplainer needs at least 2·n_features+1 evals for one full
    # permutation; SHAP_NPERM full passes give a smoother per-row estimate.
    max_evals = SHAP_NPERM * (2 * len(valid) + 1)
    explainer = shap.PermutationExplainer(predict_np, masker)
    explanation = explainer(X_explain, max_evals=max_evals)
    shap_vals = np.asarray(explanation.values)
    return shap_vals, X_explain, countries_explain


def run_shap_for_outcome(model_df, features, outcome_name, final_k):
    """
    Fit the final TabPFN on all rows, then estimate SHAP feature importance.
    Runs PermutationExplainer independently for each seed in SHAP_SEEDS and averages
    the mean |SHAP| values across seeds before saving outputs, giving a more
    stable ranking than a single random draw.  Per-seed CSVs are also saved so
    variance across seeds can be inspected.
    """
    import shap  # imported here so a missing shap install only skips this section

    valid = [f for f in features if f in model_df.columns]

    # Assemble numeric X / y / weights / country; drop rows with missing target or weight.
    X         = model_df[valid].apply(pd.to_numeric, errors="coerce")
    y         = pd.to_numeric(model_df[TARGET_COL], errors="coerce")
    w         = pd.to_numeric(model_df[WEIGHT_COL], errors="coerce")
    countries = model_df[COUNTRY_COL].reset_index(drop=True)
    keep      = y.notna() & w.notna()
    X         = X[keep].reset_index(drop=True)
    y         = y[keep].reset_index(drop=True)
    w         = w[keep].reset_index(drop=True)
    countries = countries[keep].reset_index(drop=True)

    # Replace any non-finite values, then median-impute feature gaps so the
    # background sampling and SHAP masking work cleanly. Columns that are
    # entirely missing (median is NaN) fall back to 0 so no NaN/inf leaks into
    # the explainer.
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median(numeric_only=True)).fillna(0.0)

    # Fit once on the full training set; all seeds share the same fitted model.
    w_norm   = (w / w.mean()).to_numpy()
    model    = TabPFNRegressor()
    model, _ = fit_tabpfn(model, X.to_numpy(dtype=float),
                          y.to_numpy(dtype=float), sample_weight=w_norm)

    # readable: clean labels for the CSVs (no plots produced here any more)
    readable = [label_feature(f) for f in valid]

    # ── Run PermutationExplainer for each seed, collect per-seed arrays ────────
    seed_mean_abs = []   # (n_features,) mean |SHAP| per seed

    for seed in SHAP_SEEDS:
        print(f"    Seed {seed}: explaining {min(N_SHAP_EXPLAIN, len(X))} rows "
              f"({SHAP_NPERM} permutation round(s)) against "
              f"{min(N_SHAP_BACKGROUND_K, len(X))} background rows …")

        sv, _, _ = _shap_one_seed(model, X, countries, valid, seed)

        # Guard: keep the aggregation nan-robust in case the model ever returns a
        # non-finite prediction for a masked row. PermutationExplainer does no
        # linear solve, so this should stay at 0.0%.
        sv = np.where(np.isfinite(sv), sv, np.nan)
        bad_frac = np.isnan(sv).any(axis=1).mean()
        if bad_frac > 0:
            warnings.warn(
                f"  {outcome_name} seed {seed}: {bad_frac:.1%} of explained rows "
                f"had non-finite SHAP values (excluded from the mean)."
            )
        print(f"    Seed {seed}: {bad_frac:.1%} non-finite rows")

        seed_abs = np.nanmean(np.abs(sv), axis=0)
        seed_mean_abs.append(seed_abs)

        # Per-seed importance CSV for inspection / variance checking
        (pd.DataFrame({"feature": valid, "label": readable,
                       "mean_abs_shap": seed_abs})
         .sort_values("mean_abs_shap", ascending=False)
         .reset_index(drop=True)
         .to_csv(
             os.path.join(OUTPUT_DIR,
                          f"{outcome_name}_tabpfn_shap_importance_k{final_k}_seed{seed}{SHAP_RUN_LABEL}.csv"),
             index=False,
         ))

    # ── Average across seeds ───────────────────────────────────────────────────
    mean_abs_avg = np.nanmean(seed_mean_abs, axis=0)

    # ── Rank-stability check: how consistent is the top-5 across seeds? ───────
    print(f"    Rank-stability check (top-5, each seed vs seed-averaged):")
    avg_rank = pd.Series(mean_abs_avg, index=valid).rank(ascending=False)
    for seed, seed_abs in zip(SHAP_SEEDS, seed_mean_abs):
        seed_rank = pd.Series(seed_abs, index=valid).rank(ascending=False)
        top5_avg  = avg_rank.nsmallest(5).index.tolist()
        match     = sum(f in seed_rank.nsmallest(5).index for f in top5_avg)
        print(f"      Seed {seed}: {match}/5 top-5 features match averaged ranking")

    # ── Seed-averaged global importance table ──────────────────────────────────
    imp = (pd.DataFrame({"feature": valid, "label": readable,
                         "mean_abs_shap": mean_abs_avg})
           .sort_values("mean_abs_shap", ascending=False)
           .reset_index(drop=True))
    imp.to_csv(
        os.path.join(OUTPUT_DIR,
                     f"{outcome_name}_tabpfn_shap_importance_k{final_k}{SHAP_RUN_LABEL}.csv"),
        index=False,
    )
    print(f"    Saved: {outcome_name}_tabpfn_shap_importance_k{final_k}{SHAP_RUN_LABEL}.csv")

    # NOTE: the per-feature importance bar chart and beeswarm summary are no
    # longer produced. Feature contributions are now reported at the category
    # level (grouped bar plot) in Section 21, which reads the CSV saved above.

    del model
    clear_memory()
    print(f"    Top feature (seed-avg): {imp.iloc[0]['feature']} "
          f"(mean |SHAP| = {imp.iloc[0]['mean_abs_shap']:.4f})")


if RUN_SHAP:
    print(f"\n{'='*60}")
    print("Section 19 — SHAP feature importance (final models)")
    print(f"{'='*60}")

    _all_shap_tasks = {
        "basic_sanitation": (bs_model_df, bs_features, FINAL_K_BASIC_SANITATION),
        "open_defecation":  (od_model_df, od_features, FINAL_K_OPEN_DEFECATION),
    }
    _shap_tasks = [
        (_name, *_all_shap_tasks[_name])
        for _name in SHAP_OUTCOMES
        if _name in _all_shap_tasks
    ]

    # Pre-flight: report the approximate API load before any calls are made.
    # PermutationExplainer evaluates the model on ~ n_explain × SHAP_NPERM ×
    # (2·n_features + 1) × background rows per outcome per seed.
    print(f"\n  Pre-flight estimate — model evaluations (rows sent to TabPFN):")
    _total_rows = 0
    for _name, _mdf, _feat, _k in _shap_tasks:
        _m        = len([f for f in _feat if f in _mdf.columns])
        _evals    = SHAP_NPERM * (2 * _m + 1)
        _per      = N_SHAP_EXPLAIN * _evals * N_SHAP_BACKGROUND_K * len(SHAP_SEEDS)
        _total_rows += _per
        print(f"    {_name}: {N_SHAP_EXPLAIN} explain × {SHAP_NPERM}×(2·{_m}+1)="
              f"{_evals} evals × {N_SHAP_BACKGROUND_K} background × "
              f"{len(SHAP_SEEDS)} seed = ~{_per:,} rows")
    print(f"    Total ≈ {_total_rows:,} rows "
          f"(explained rows capped at the training-set size at run time)")

    for _name, _mdf, _feat, _k in _shap_tasks:
        print(f"\n  Outcome: {_name}")
        try:
            run_shap_for_outcome(_mdf, _feat, _name, _k)
        except ImportError:
            warnings.warn("  shap not installed — skipping SHAP section "
                          "(install with: pip install shap)")
            break
        except Exception as exc:  # noqa: BLE001 — keep one outcome's failure isolated
            warnings.warn(f"  SHAP skipped for {_name}: {exc}")


# -------------------------------------------------------
# 21. SHAP share summary
#
# Expresses each feature's contribution as a share of the total
# mean |SHAP| across all features, making values interpretable
# as percentages. Reports:
#   a) Top-5 feature shares (row-weighted ranking)
#   b) Aggregate share attributable to country-level vs subnational features
#   c) Aggregate share attributable to each Table S1/S2 category
#      (Climate, HP, S, Topography, VT, VC, SEG, JMP, Region size),
#      plus a grouped bar plot of those category contributions.
#
# Loads the CSVs written in Section 19 so this section can be
# re-run independently without repeating the SHAP computation.
# -------------------------------------------------------

print(f"\n{'='*60}")
print("Section 21 — SHAP share summary")
print(f"{'='*60}")

# Ensure the plot dir exists even when this section is run on its own (without
# Section 17, which is where PLOT_DIR is first defined).
PLOT_DIR = os.path.join(OUTPUT_DIR, "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

_COUNTRY_LEVEL_SET = set(COUNTRY_LEVEL_FEATURES)

_shap_summary_tasks = [
    ("basic_sanitation", FINAL_K_BASIC_SANITATION),
    ("open_defecation",  FINAL_K_OPEN_DEFECATION),
]

for _outcome, _k in _shap_summary_tasks:
    _sub_path = os.path.join(OUTPUT_DIR,
                             f"{_outcome}_tabpfn_shap_importance_k{_k}{SHAP_RUN_LABEL}.csv")

    if not os.path.exists(_sub_path):
        print(f"  {_outcome}: SHAP importance file not found ({_sub_path}) — run Section 19 first.")
        continue

    sub_imp = pd.read_csv(_sub_path)

    total = sub_imp["mean_abs_shap"].sum()
    sub_imp = sub_imp.copy()
    sub_imp["share_pct"] = 100 * sub_imp["mean_abs_shap"] / total
    sub_imp["level"]     = sub_imp["feature"].apply(
        lambda f: "country" if f in _COUNTRY_LEVEL_SET else "subnational"
    )
    sub_imp["category"]  = sub_imp["feature"].apply(category_of)

    top5 = sub_imp.head(5)[["label", "level", "mean_abs_shap", "share_pct"]]
    group_shares = (
        sub_imp.groupby("level")["share_pct"]
        .sum()
        .rename("total_share_pct")
        .reset_index()
    )

    print(f"\n  {_outcome} | Subnational (row-weighted)")
    print(f"  {'─'*55}")
    print("  Top 5 features:")
    for _, row in top5.iterrows():
        marker = " *" if row["level"] == "country" else "  "
        print(f"    {marker}{row['label']:<45} {row['share_pct']:>5.1f}%")
    print("  Aggregate shares by level:")
    for _, row in group_shares.iterrows():
        print(f"    {row['level']:<15} {row['total_share_pct']:>5.1f}%")

    sub_imp.insert(0, "outcome", _outcome)
    _share_path = os.path.join(OUTPUT_DIR,
                               f"{_outcome}_tabpfn_shap_shares_k{_k}{SHAP_RUN_LABEL}.csv")
    sub_imp.to_csv(_share_path, index=False)
    print(f"\n  Saved: {_share_path}")

    # ── Aggregate contribution by Table S1/S2 category ────────────────────────
    # Sum mean |SHAP| (and its share) within each category, then order the
    # categories by the fixed Table S1/S2 sequence for a consistent plot.
    cat_shares = (
        sub_imp.groupby("category")
        .agg(mean_abs_shap=("mean_abs_shap", "sum"),
             share_pct=("share_pct", "sum"),
             n_features=("feature", "size"))
        .reset_index()
    )
    # Keep only categories that actually appear in this feature set, in the
    # canonical order (any 'Uncategorised' features fall to the end).
    _order = [c for c in CATEGORY_ORDER if c in set(cat_shares["category"])]
    _extra = [c for c in cat_shares["category"] if c not in CATEGORY_ORDER]
    cat_shares["category"] = pd.Categorical(
        cat_shares["category"], categories=_order + _extra, ordered=True
    )
    cat_shares = cat_shares.sort_values("category").reset_index(drop=True)
    cat_shares.insert(0, "outcome", _outcome)

    _cat_path = os.path.join(OUTPUT_DIR,
                             f"{_outcome}_tabpfn_shap_category_shares_k{_k}{SHAP_RUN_LABEL}.csv")
    cat_shares.to_csv(_cat_path, index=False)

    print("  Aggregate shares by category (Table S1/S2):")
    for _, row in cat_shares.sort_values("share_pct", ascending=False).iterrows():
        print(f"    {str(row['category']):<15} {row['share_pct']:>5.1f}%  "
              f"({int(row['n_features'])} features)")
    print(f"  Saved: {_cat_path}")

    # ── Grouped bar plot — category contributions ─────────────────────────────
    # Horizontal bars, largest share at the top, coloured by the fixed
    # CATEGORY_COLOURS palette so plots are comparable across outcomes.
    plot_df = cat_shares.sort_values("share_pct", ascending=True)
    bar_colours = [
        CATEGORY_COLOURS.get(str(c), "#666666") for c in plot_df["category"]
    ]
    fig, ax = plt.subplots(figsize=(7.0, 0.45 * len(plot_df) + 1.2))
    ax.barh(plot_df["category"].astype(str), plot_df["share_pct"],
            color=bar_colours)
    for y, (share, n) in enumerate(zip(plot_df["share_pct"], plot_df["n_features"])):
        ax.text(share + 0.4, y, f"{share:.1f}%  (n={int(n)})",
                va="center", ha="left", fontsize=8)
    ax.set_xlabel("Share of total mean |SHAP|  (%)")
    ax.set_xlim(0, min(100, plot_df["share_pct"].max() * 1.20 + 5))
    ax.set_title(
        f"Feature-category contribution: {_outcome} (k = {_k})\n"
        "Grouped by Table S1/S2 category",
        loc="left",
    )
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    _cat_plot_path = os.path.join(
        PLOT_DIR, f"{_outcome}_tabpfn_shap_category_contribution_k{_k}{SHAP_RUN_LABEL}.pdf"
    )
    fig.savefig(_cat_plot_path, bbox_inches="tight")
    fig.savefig(_cat_plot_path.replace(".pdf", ".png"),
                dpi=SHAP_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved plot: {_cat_plot_path}")


# -------------------------------------------------------
# 20. Sensitivity analysis — JMP feature contribution
#
# Quantifies how much the JMP national estimates
# ("sanitation_basic" and "open_defecation" in COUNTRY_LEVEL_FEATURES)
# contribute to model performance by running LOCO-CV under three
# feature sets for each outcome:
#
#   "full"        — the final feature set chosen in Section 11
#   "jmp_only"    — only the two JMP columns (plus any EO features that
#                   also happen to be in the final set; here typically
#                   just the two JMP columns)
#   "no_jmp"      — the final feature set with both JMP columns removed
#
# The difference in LOCO-CV metrics between "full" and "no_jmp" is the
# JMP contribution. "jmp_only" gives an upper bound on what is achievable
# from national estimates alone.
#
# Outputs (CSV) written to OUTPUT_DIR with prefix "jmp_sensitivity_":
#   jmp_sensitivity_loco_overall.csv   — one row per outcome × variant
#   jmp_sensitivity_loco_by_country.csv — per-country fold metrics
# -------------------------------------------------------

JMP_FEATURES = ["sanitation_basic", "open_defecation"]

RUN_JMP_SENSITIVITY = False  # set True to rerun; results already saved to CSV

# Build the three feature variants for each outcome.
# "jmp_only" keeps only those JMP columns present in the final feature set
# (normally both, but safe to intersect).
_sensitivity_tasks = {
    "basic_sanitation": {
        "model_df": bs_model_df,
        "final_k":  FINAL_K_BASIC_SANITATION,
        "variants": {
            "full":     bs_features,
            "jmp_only": [f for f in bs_features if f in JMP_FEATURES],
            "no_jmp":   [f for f in bs_features if f not in JMP_FEATURES],
        },
    },
    "open_defecation": {
        "model_df": od_model_df,
        "final_k":  FINAL_K_OPEN_DEFECATION,
        "variants": {
            "full":     od_features,
            "jmp_only": [f for f in od_features if f in JMP_FEATURES],
            "no_jmp":   [f for f in od_features if f not in JMP_FEATURES],
        },
    },
}

if RUN_JMP_SENSITIVITY:
    print(f"\n{'='*60}")
    print("Section 20 — JMP feature contribution (sensitivity analysis)")
    print(f"{'='*60}")

    _sens_overall_rows = []
    _sens_country_rows = []

    for outcome_name, cfg in _sensitivity_tasks.items():
        model_df = cfg["model_df"]
        final_k  = cfg["final_k"]

        for variant_name, feat_list in cfg["variants"].items():
            if len(feat_list) == 0:
                warnings.warn(
                    f"  {outcome_name} / {variant_name}: feature list is empty — skipping."
                )
                continue

            print(f"\n  {outcome_name} | variant = {variant_name} "
                  f"({len(feat_list)} features)")

            fold_df, overall_df, _ = run_loco_cv(
                model_df, feat_list, outcome_name, final_k
            )

            overall_df.insert(1, "jmp_variant", variant_name)
            fold_df.insert(1,   "jmp_variant", variant_name)

            _sens_overall_rows.append(overall_df)
            _sens_country_rows.append(fold_df)

    if _sens_overall_rows:
        sens_overall = pd.concat(_sens_overall_rows, ignore_index=True)
        sens_country = pd.concat(_sens_country_rows, ignore_index=True)

        _sens_overall_path = os.path.join(OUTPUT_DIR, "jmp_sensitivity_loco_overall.csv")
        _sens_country_path = os.path.join(OUTPUT_DIR, "jmp_sensitivity_loco_by_country.csv")
        sens_overall.to_csv(_sens_overall_path, index=False)
        sens_country.to_csv(_sens_country_path, index=False)

        print(f"\n  Saved: {_sens_overall_path}")
        print(f"  Saved: {_sens_country_path}")

        _display_cols = [
            "outcome", "jmp_variant", "n_features",
            "unweighted_mae", "unweighted_rmse", "unweighted_r2",
            "weighted_mae",   "weighted_rmse",   "weighted_r2",
        ]
        print(f"\n{'='*60}")
        print("JMP sensitivity — LOCO-CV summary:")
        print(
            sens_overall[[c for c in _display_cols if c in sens_overall.columns]]
            .sort_values(["outcome", "jmp_variant"])
            .to_string(index=False)
        )
else:
    print("\nSection 20 skipped (RUN_JMP_SENSITIVITY = False). "
          "Existing results in jmp_sensitivity_loco_overall.csv.")