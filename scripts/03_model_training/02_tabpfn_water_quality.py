# -------------------------------------------------------
# Household-weighted leave-one-country-out modelling
# Outcome: E. coli-free drinking water proportion
# Models: TabPFN, Random Forest, XGBoost
# -------------------------------------------------------

import os
import inspect

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tabpfn import TabPFNRegressor
from xgboost import XGBRegressor

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import mean_absolute_error, r2_score


# -------------------------------------------------------
# 1. Settings
# -------------------------------------------------------

data_path = "data/training_subcomponents/ecoli_free_training_with_covariates_exact_only.csv"
output_dir = "outputs/04_model_performance"

os.makedirs(output_dir, exist_ok=True)

target_col = "outcome_value"
country_col = "country_outcome"
region_col = "HH7_region_outcome"
year_col = "analysis_year"


# -------------------------------------------------------
# 2. Load data
# -------------------------------------------------------

training_wq = pd.read_csv(data_path)


# -------------------------------------------------------
# 3. Define covariates
# -------------------------------------------------------

feature_cols = [
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
    "EarthEnvTopoMed_TerrainRuggednessIndex",
    "EarthEnvTopoMed_TopoPositionIndex",
    "EsaCci_BurntAreasProbability",
    "FanEtAl_Depth_to_Water_Table_AnnualMean",
    "FanEtAl_Depth_to_Water_Table_AnnualSD",
    "GHS_Population_Density",
    "GPWv4_Population_Density",
    "GiriEtAl_MangrovesExtent",
    "GLW3_RuminantsDistribution_downsampled10km",
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
    "map_friction",
    "chirps_annual_precipitation",
    "era5_temperature_2m",
    "ghsl_built_surface",
    "ghsl_population",
    "ghsl_population_sum",
    "ghsl_urban_frac",
    "jrc_building_height",
    "modis_evi",
    "modis_ndvi",
    "runoff_max_annualmax",
    "runoff_min_annualmin",
    "temperature_2m_max_annualmax",
    "viirs_average",
    "worldpop_sum",
    

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
    "voice_and_accountability"
]


# -------------------------------------------------------
# 4. Identify household weight column
# -------------------------------------------------------

possible_weight_cols = [
    "n_households",
    "n_housholds",
    "HouseholdsInRegion.Freq.x"
]

weight_col = next(
    (col for col in possible_weight_cols if col in training_wq.columns),
    None
)

if weight_col is None:
    raise ValueError(
        "Could not find a household weight column. "
        f"Looked for: {possible_weight_cols}"
    )

print(f"Using household weight column: {weight_col}")


# -------------------------------------------------------
# 5. Remove Pakistan rows
# -------------------------------------------------------
# This removes Pakistan, Pakistan Punjab, Pakistan Balochistan,
# Pakistan Khyber Pakhtunkhwa, and any other country name starting with Pakistan.

training_wq = training_wq[
    ~training_wq[country_col].astype(str).str.startswith("Pakistan", na=False)
].copy()


# -------------------------------------------------------
# 6. Prepare modelling dataframe
# -------------------------------------------------------

def prepare_model_data(
    df,
    feature_cols,
    target_col,
    country_col,
    region_col,
    year_col,
    weight_col
):
    needed_cols = feature_cols + [
        target_col,
        country_col,
        region_col,
        year_col,
        weight_col
    ]

    missing_cols = [col for col in needed_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    model_df = df[needed_cols].copy()

    # Convert covariates, outcome, and weights to numeric
    for col in feature_cols + [target_col, weight_col]:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")

    # Drop rows with missing values needed for modelling
    model_df = model_df.dropna(
        subset=feature_cols + [
            target_col,
            country_col,
            region_col,
            year_col,
            weight_col
        ]
    ).copy()

    # Keep only positive household weights
    model_df = model_df[model_df[weight_col] > 0].copy()

    # Keep one row per country-year-region-outcome
    model_df = model_df.drop_duplicates(
        subset=[
            country_col,
            year_col,
            region_col,
            target_col
        ]
    ).copy()

    # Create country fold ID for leave-one-country-out CV
    country_lookup = (
        model_df[[country_col]]
        .drop_duplicates()
        .sort_values(country_col)
        .reset_index(drop=True)
    )

    country_lookup["country_fold"] = np.arange(
        1,
        len(country_lookup) + 1
    )

    model_df = model_df.merge(
        country_lookup,
        on=country_col,
        how="left"
    )

    if model_df[country_col].nunique() < 2:
        raise ValueError("Need at least two countries for leave-one-country-out CV.")

    return model_df


model_df = prepare_model_data(
    df=training_wq,
    feature_cols=feature_cols,
    target_col=target_col,
    country_col=country_col,
    region_col=region_col,
    year_col=year_col,
    weight_col=weight_col
)

print("Final modelling data shape:", model_df.shape)
print("Number of countries:", model_df[country_col].nunique())
print("Number of regions:", model_df[[country_col, region_col]].drop_duplicates().shape[0])
print("Total household weight:", model_df[weight_col].sum())


# -------------------------------------------------------
# 7. Define models
# -------------------------------------------------------

def make_tabpfn():
    return TabPFNRegressor()


def make_random_forest():
    return RandomForestRegressor(
        n_estimators=500,
        random_state=42,
        n_jobs=-1
    )


def make_xgboost():
    return XGBRegressor(
        n_estimators=500,
        learning_rate=0.03,
        max_depth=4,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1
    )


models = {
    "TabPFN": make_tabpfn,
    "Random Forest": make_random_forest,
    "XGBoost": make_xgboost
}


# -------------------------------------------------------
# 8. Helper: fit with household sample weights where supported
# -------------------------------------------------------

def fit_with_optional_sample_weight(model, X_train, y_train, sample_weight):
    try:
        fit_signature = inspect.signature(model.fit)
        fit_params = fit_signature.parameters

        supports_sample_weight = (
            "sample_weight" in fit_params
            or any(
                param.kind == inspect.Parameter.VAR_KEYWORD
                for param in fit_params.values()
            )
        )

    except (TypeError, ValueError):
        supports_sample_weight = False

    if supports_sample_weight:
        try:
            model.fit(
                X_train,
                y_train,
                sample_weight=sample_weight
            )
            return model, True
        except TypeError:
            pass

    model.fit(X_train, y_train)
    return model, False


# -------------------------------------------------------
# 9. Run household-weighted leave-one-country-out CV
# -------------------------------------------------------

def run_weighted_loco_cv(
    model_df,
    models,
    feature_cols,
    target_col,
    country_col,
    region_col,
    year_col,
    weight_col
):
    X = model_df[feature_cols]
    y = model_df[target_col].to_numpy()
    groups = model_df["country_fold"]
    weights = model_df[weight_col].to_numpy()

    logo = LeaveOneGroupOut()

    oof_predictions = {
        model_name: np.full(len(model_df), np.nan)
        for model_name in models.keys()
    }

    used_training_weights = {
        model_name: []
        for model_name in models.keys()
    }

    fold_results = []

    for fold, (train_idx, val_idx) in enumerate(
        logo.split(X, y, groups=groups),
        start=1
    ):
        held_out_country = model_df.iloc[val_idx][country_col].iloc[0]

        X_train = X.iloc[train_idx]
        y_train = y[train_idx]

        X_val = X.iloc[val_idx]
        y_val = y[val_idx]

        w_train = weights[train_idx]
        w_val = weights[val_idx]

        # Normalise training weights to mean 1.
        # This keeps relative household weighting but avoids huge weight scales.
        w_train_norm = w_train / np.mean(w_train)

        fold_row = {
            "fold": fold,
            "held_out_country": held_out_country,
            "n_train_rows": len(train_idx),
            "n_val_rows": len(val_idx),
            "sum_household_weight_val": float(np.sum(w_val))
        }

        print(f"Running fold {fold}: held-out country = {held_out_country}")

        for model_name, model_builder in models.items():
            model = model_builder()

            model, used_weights = fit_with_optional_sample_weight(
                model=model,
                X_train=X_train,
                y_train=y_train,
                sample_weight=w_train_norm
            )

            used_training_weights[model_name].append(used_weights)

            preds = np.asarray(model.predict(X_val)).reshape(-1)

            oof_predictions[model_name][val_idx] = preds

            fold_row[f"weighted_mae_{model_name}"] = mean_absolute_error(
                y_val,
                preds,
                sample_weight=w_val
            )

            fold_row[f"unweighted_mae_{model_name}"] = mean_absolute_error(
                y_val,
                preds
            )

            if len(y_val) > 1 and len(np.unique(y_val)) > 1:
                fold_row[f"weighted_r2_{model_name}"] = r2_score(
                    y_val,
                    preds,
                    sample_weight=w_val
                )

                fold_row[f"unweighted_r2_{model_name}"] = r2_score(
                    y_val,
                    preds
                )
            else:
                fold_row[f"weighted_r2_{model_name}"] = np.nan
                fold_row[f"unweighted_r2_{model_name}"] = np.nan

        fold_results.append(fold_row)

    fold_results_df = pd.DataFrame(fold_results)

    overall_results = []

    for model_name, preds in oof_predictions.items():
        if np.isnan(preds).any():
            n_missing = np.isnan(preds).sum()
            raise ValueError(
                f"{model_name} has {n_missing} missing out-of-fold predictions."
            )

        overall_results.append({
            "model": model_name,
            "used_training_weights": all(used_training_weights[model_name]),
            "weighted_mae": mean_absolute_error(
                y,
                preds,
                sample_weight=weights
            ),
            "weighted_r2": r2_score(
                y,
                preds,
                sample_weight=weights
            ),
            "unweighted_mae": mean_absolute_error(
                y,
                preds
            ),
            "unweighted_r2": r2_score(
                y,
                preds
            ),
            "n_rows": len(y),
            "n_countries": model_df[country_col].nunique(),
            "sum_household_weight": float(np.sum(weights))
        })

    overall_results_df = (
        pd.DataFrame(overall_results)
        .sort_values("weighted_mae")
    )

    oof_df = model_df[
        [
            country_col,
            region_col,
            year_col,
            target_col,
            weight_col,
            "country_fold"
        ]
    ].copy()

    for model_name, preds in oof_predictions.items():
        clean_name = model_name.lower().replace(" ", "_")

        oof_df[f"pred_{clean_name}"] = preds
        oof_df[f"error_{clean_name}"] = oof_df[target_col] - preds
        oof_df[f"abs_error_{clean_name}"] = np.abs(
            oof_df[target_col] - preds
        )

    return fold_results_df, overall_results_df, oof_df, oof_predictions


fold_results_df, overall_results_df, oof_df, oof_predictions = run_weighted_loco_cv(
    model_df=model_df,
    models=models,
    feature_cols=feature_cols,
    target_col=target_col,
    country_col=country_col,
    region_col=region_col,
    year_col=year_col,
    weight_col=weight_col
)


print("\nOverall household-weighted leave-one-country-out CV results:")
print(overall_results_df)

print("\nPer-country household-weighted leave-one-country-out CV results:")
print(fold_results_df)


# -------------------------------------------------------
# 10. Save household-weighted model results
# -------------------------------------------------------

fold_results_df.to_csv(
    os.path.join(output_dir, "ecoli_loco_cv_by_country_household_weighted.csv"),
    index=False
)

overall_results_df.to_csv(
    os.path.join(output_dir, "ecoli_loco_cv_overall_model_comparison_household_weighted.csv"),
    index=False
)

oof_df.to_csv(
    os.path.join(output_dir, "ecoli_loco_cv_oof_predictions_household_weighted.csv"),
    index=False
)


# -------------------------------------------------------
# 11. TabPFN q10-q90 prediction interval with LOCO-CV
# -------------------------------------------------------
# This uses the same cleaned household-weighted model_df.
# If TabPFN supports sample_weight, it will use household weights during training.
# If not, it will still be evaluated against household-weighted errors.

quantiles = [0.10, 0.90]

quantile_colnames = {
    0.10: "tabpfn_q10",
    0.90: "tabpfn_q90"
}


def standardise_quantile_output(preds_quantile, n_rows, n_quantiles):
    arr = np.asarray(preds_quantile)

    if arr.shape == (n_rows, n_quantiles):
        return arr

    if arr.shape == (n_quantiles, n_rows):
        return arr.T

    raise ValueError(
        f"Unexpected TabPFN quantile output shape: {arr.shape}. "
        f"Expected ({n_rows}, {n_quantiles}) or ({n_quantiles}, {n_rows})."
    )


X_quant = model_df[feature_cols]
y_quant = model_df[target_col].to_numpy()
groups_quant = model_df["country_fold"]
weights_quant = model_df[weight_col].to_numpy()

logo_quant = LeaveOneGroupOut()

tabpfn_q10_q90_oof_rows = []

for fold, (train_idx, val_idx) in enumerate(
    logo_quant.split(X_quant, y_quant, groups=groups_quant),
    start=1
):
    held_out_country = model_df.iloc[val_idx][country_col].iloc[0]
    print(f"Running TabPFN q10-q90 fold {fold}: held-out country = {held_out_country}")

    X_train = X_quant.iloc[train_idx]
    y_train = y_quant[train_idx]

    X_val = X_quant.iloc[val_idx]
    y_val = y_quant[val_idx]

    w_train = weights_quant[train_idx]
    w_val = weights_quant[val_idx]

    w_train_norm = w_train / np.mean(w_train)

    model_quant = TabPFNRegressor()

    model_quant, tabpfn_used_weights = fit_with_optional_sample_weight(
        model=model_quant,
        X_train=X_train,
        y_train=y_train,
        sample_weight=w_train_norm
    )

    preds_point = np.asarray(
        model_quant.predict(X_val)
    ).reshape(-1)

    preds_quantile = model_quant.predict(
        X_val,
        output_type="quantiles",
        quantiles=quantiles
    )

    preds_quantile = standardise_quantile_output(
        preds_quantile,
        n_rows=len(X_val),
        n_quantiles=len(quantiles)
    )

    fold_df = model_df.iloc[val_idx][
        [
            country_col,
            region_col,
            year_col,
            target_col,
            weight_col,
            "country_fold"
        ]
    ].copy()

    fold_df["tabpfn_pred_point"] = preds_point

    for i, q in enumerate(quantiles):
        fold_df[quantile_colnames[q]] = preds_quantile[:, i]

    q_sorted = np.sort(
        fold_df[["tabpfn_q10", "tabpfn_q90"]].to_numpy(),
        axis=1
    )

    fold_df["tabpfn_q10_ordered"] = q_sorted[:, 0]
    fold_df["tabpfn_q90_ordered"] = q_sorted[:, 1]

    fold_df["pred_minus_observed"] = (
        fold_df["tabpfn_pred_point"] - fold_df[target_col]
    )

    fold_df["abs_error"] = np.abs(
        fold_df["pred_minus_observed"]
    )

    fold_df["tabpfn_q90_q10_range"] = (
        fold_df["tabpfn_q90_ordered"] - fold_df["tabpfn_q10_ordered"]
    )

    fold_df["tabpfn_used_training_weights"] = tabpfn_used_weights

    fold_df["weighted_abs_error"] = (
        fold_df["abs_error"] * fold_df[weight_col]
    )

    tabpfn_q10_q90_oof_rows.append(fold_df)


tabpfn_q10_q90_oof_df = pd.concat(
    tabpfn_q10_q90_oof_rows,
    ignore_index=True
)


tabpfn_q10_q90_oof_df.to_csv(
    os.path.join(output_dir, "ecoli_tabpfn_loco_q10_q90_predictions_household_weighted.csv"),
    index=False
)


# -------------------------------------------------------
# 12. Plot q90-q10 range against absolute prediction error
# -------------------------------------------------------

plot_x = tabpfn_q10_q90_oof_df["abs_error"].to_numpy()
plot_y = tabpfn_q10_q90_oof_df["tabpfn_q90_q10_range"].to_numpy()

valid = np.isfinite(plot_x) & np.isfinite(plot_y)

plot_x = plot_x[valid]
plot_y = plot_y[valid]

if len(plot_x) > 1:
    slope, intercept = np.polyfit(plot_x, plot_y, 1)

    x_line = np.linspace(
        0,
        max(plot_x.max(), plot_y.max()),
        100
    )

    y_line = intercept + slope * x_line

    plt.figure(figsize=(8, 6))

    plt.scatter(
        plot_x,
        plot_y,
        alpha=0.7
    )

    plt.plot(
        x_line,
        x_line,
        linestyle="--",
        label="1:1 line"
    )

    plt.plot(
        x_line,
        y_line,
        linestyle="-",
        label=f"Linear fit: y = {slope:.2f}x + {intercept:.2f}"
    )

    plt.xlabel("Absolute prediction error: |TabPFN point prediction - observed|")
    plt.ylabel("Predicted q90 - q10 interval width")
    plt.title("TabPFN LOCO-CV uncertainty range vs prediction error")
    plt.legend()
    plt.tight_layout()
    plt.show()


# -------------------------------------------------------
# 13. Plot observed vs predicted with q10-q90 interval
# -------------------------------------------------------

plot_df = tabpfn_q10_q90_oof_df.copy()

hh = pd.to_numeric(plot_df[weight_col], errors="coerce")

if hh.notna().any() and hh.max() > 0:
    point_size = 20 + 180 * (hh / hh.max())
else:
    point_size = 50

xerr_lower = np.maximum(
    plot_df["tabpfn_pred_point"] - plot_df["tabpfn_q10_ordered"],
    0
)

xerr_upper = np.maximum(
    plot_df["tabpfn_q90_ordered"] - plot_df["tabpfn_pred_point"],
    0
)

plt.figure(figsize=(7, 7))

plt.errorbar(
    x=plot_df["tabpfn_pred_point"],
    y=plot_df[target_col],
    xerr=[xerr_lower, xerr_upper],
    fmt="none",
    alpha=0.35,
    linewidth=1
)

plt.scatter(
    plot_df["tabpfn_pred_point"],
    plot_df[target_col],
    s=point_size,
    facecolors="none",
    edgecolors="black",
    alpha=0.8
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    color="black",
    linewidth=1
)

plt.xlim(0, 1)
plt.ylim(0, 1)

plt.xlabel(
    "TabPFN predicted proportion with E. coli-free drinking water\n"
    "point = standard prediction, line = q10-q90"
)
plt.ylabel("Observed proportion with E. coli-free drinking water")
plt.title("Observed vs TabPFN LOCO-CV prediction with q10-q90 range")

plt.tight_layout()
plt.show()


# -------------------------------------------------------
# 14. Display final model comparison
# -------------------------------------------------------

overall_results_df