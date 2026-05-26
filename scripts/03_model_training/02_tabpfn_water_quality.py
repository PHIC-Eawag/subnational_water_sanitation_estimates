# -------------------------------------------------------
#
# Minimal example to use TabPFN for Classification and Regression
#
# April  7, 2026 -- Andreas Scheidegger
# -------------------------------------------------------

from tabpfn import TabPFNClassifier
from tabpfn import TabPFNRegressor
from xgboost import XGBRegressor

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score, mean_squared_error

# for comparison we can use RandomForest models
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor



# -----------
# 1) Classification example
# See docs for more details: https://docs.priorlabs.ai/capabilities/classification

# -- load data
from sklearn.datasets import load_breast_cancer

X, y = load_breast_cancer(return_X_y = True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# -- build models
model = TabPFNClassifier()
model.fit(X_train, y_train)

modRF = RandomForestClassifier()
modRF.fit(X_train, y_train)

# -- use model
# Predict class labels
preds = model.predict(X_test)
print("Accuracy tabPFN:", accuracy_score(y_test, preds))

predsRF = modRF.predict(X_test)
print("Accuracy RandomForest:", accuracy_score(y_test, predsRF))

# Get class probabilities
model.predict_proba(X_test)



# -----------
# 2) Regression example
# See docs for more details: https://docs.priorlabs.ai/capabilities/regression

# -- load data
from sklearn.datasets import load_diabetes

X, y = load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# -- build models
model = TabPFNRegressor()
model.fit(X_train, y_train)

modRF = RandomForestRegressor()
modRF.fit(X_train, y_train)

# Predict
preds = model.predict(X_test)
predsRF = modRF.predict(X_test)

# Evaluate
print("MSE tabPFN:", mean_squared_error(y_test, preds))
print("MSE RandomForest:", mean_squared_error(y_test, predsRF))
print("R² tabPFN:", r2_score(y_test, preds))
print("R² RandomForest:", r2_score(y_test, predsRF))


# Predict different quantiles
preds = model.predict(X_test,
                      output_type="quantiles",
                      quantiles=[0.05, 0.1, 0.5, 0.9, 0.95])


# -------------------------------------------------------
# Using data on safe drinking water
# -------------------------------------------------------

import pandas as pd

training_wq = pd.read_csv("outputs/03_sampled_features/training_set.csv")

target_col = "No_EcoliAtRegionalLevel"
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

  # sampled for specific year
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
  #"worldpop_sum"
  
]


import numpy as np
from sklearn.ensemble import RandomForestRegressor

# load separate training and test files
training_wq = pd.read_csv("outputs/03_sampled_features/training_set.csv")
test_wq = pd.read_csv("outputs/03_sampled_features/test_set.csv")

# create one shared mapping from country name to numeric id
all_countries = pd.concat([training_wq["country.x"], test_wq["country.x"]], ignore_index=True)
country_codes, country_names = pd.factorize(all_countries)

country_lookup = pd.DataFrame({
    "country.x": country_names,
    "country_fold": np.arange(1, len(country_names) + 1)
})

training_wq = training_wq.merge(country_lookup, on="country.x", how="left")
test_wq = test_wq.merge(country_lookup, on="country.x", how="left")

# keep only needed columns
needed_cols = feature_cols + [target_col, "country.x", "country_fold"]

train_df = training_wq[needed_cols].dropna().copy()
test_df = test_wq[needed_cols].dropna().copy()

# build train/test matrices
X_train = train_df[feature_cols]
y_train = train_df[target_col]

X_test = test_df[feature_cols]
y_test = test_df[target_col]

print(X_train.shape, y_train.shape)
print(X_test.shape, y_test.shape)

# fit models
model = TabPFNRegressor()
model.fit(X_train, y_train)

modRF = RandomForestRegressor(random_state=42)
modRF.fit(X_train, y_train)

modXGB = XGBRegressor(random_state=42)
modXGB.fit(X_train, y_train)


# predict
preds = model.predict(X_test)
predsRF = modRF.predict(X_test)
predsXGB = modXGB.predict(X_test)

# Evaluate
print("MSE tabPFN:", mean_squared_error(y_test, preds))
print("MSE RandomForest:", mean_squared_error(y_test, predsRF))
print("R² tabPFN:", r2_score(y_test, preds))
print("R² RandomForest:", r2_score(y_test, predsRF))

from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# -----------------------------
# Leave-one-country-out CV on the training set only
# row-weighted metrics via out-of-fold predictions
# -----------------------------
logo = LeaveOneGroupOut()

cv_X = train_df[feature_cols]
cv_y = train_df[target_col]
cv_groups = train_df["country_fold"]

# store one out-of-fold prediction for each training row
oof_preds_tabpfn = np.full(len(train_df), np.nan)
oof_preds_rf = np.full(len(train_df), np.nan)

cv_results = []

for fold, (cv_train_idx, cv_val_idx) in enumerate(logo.split(cv_X, cv_y, groups=cv_groups), start=1):
    held_out_country = cv_groups.iloc[cv_val_idx].iloc[0]

    X_tr = cv_X.iloc[cv_train_idx]
    y_tr = cv_y.iloc[cv_train_idx]

    X_val = cv_X.iloc[cv_val_idx]
    y_val = cv_y.iloc[cv_val_idx]

    # TabPFN
    model_cv = TabPFNRegressor()
    model_cv.fit(X_tr, y_tr)
    preds_val = model_cv.predict(X_val)

    # Random Forest
    modRF_cv = RandomForestRegressor(random_state=42)
    modRF_cv.fit(X_tr, y_tr)
    predsRF_val = modRF_cv.predict(X_val)

    # save predictions back to the original positions in train_df
    oof_preds_tabpfn[cv_val_idx] = preds_val
    oof_preds_rf[cv_val_idx] = predsRF_val

    # optional: keep per-country metrics too
    r2_tabpfn = r2_score(y_val, preds_val) if len(y_val) > 1 and y_val.nunique() > 1 else float("nan")
    r2_rf = r2_score(y_val, predsRF_val) if len(y_val) > 1 and y_val.nunique() > 1 else float("nan")

    cv_results.append({
        "fold": fold,
        "held_out_country": held_out_country,
        "n_val_rows": len(cv_val_idx),
        "mae_tabPFN": mean_absolute_error(y_val, preds_val),
        "mse_tabPFN": mean_squared_error(y_val, preds_val),
        "rmse_tabPFN": mean_squared_error(y_val, preds_val) ** 0.5,
        "r2_tabPFN": r2_tabpfn,
        "mae_RF": mean_absolute_error(y_val, predsRF_val),
        "mse_RF": mean_squared_error(y_val, predsRF_val),
        "rmse_RF": mean_squared_error(y_val, predsRF_val) ** 0.5,
        "r2_RF": r2_rf,
    })

cv_results_df = pd.DataFrame(cv_results)

print("\nLeave-one-country-out CV results by country:")
print(cv_results_df)

# overall row-weighted CV metrics:
# every row in train_df contributes once
print("\nOverall row-weighted CV metrics on training set:")
print("MAE tabPFN:", mean_absolute_error(cv_y, oof_preds_tabpfn))
print("MSE tabPFN:", mean_squared_error(cv_y, oof_preds_tabpfn))
print("RMSE tabPFN:", mean_squared_error(cv_y, oof_preds_tabpfn) ** 0.5)
print("R² tabPFN:", r2_score(cv_y, oof_preds_tabpfn))

print("MAE RandomForest:", mean_absolute_error(cv_y, oof_preds_rf))
print("MSE RandomForest:", mean_squared_error(cv_y, oof_preds_rf))
print("RMSE RandomForest:", mean_squared_error(cv_y, oof_preds_rf) ** 0.5)
print("R² RandomForest:", r2_score(cv_y, oof_preds_rf))

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score

cv_y = train_df[target_col].to_numpy() 

from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import mean_squared_error, r2_score
from tabpfn import TabPFNRegressor
from sklearn.ensemble import RandomForestRegressor

# -----------------------------
# Safety checks
# -----------------------------
required_cols = feature_cols + [target_col, "country_fold"]
missing_cols = [c for c in required_cols if c not in train_df.columns]
if missing_cols:
    raise ValueError(f"train_df is missing these columns: {missing_cols}")

if len(train_df) == 0:
    raise ValueError("train_df is empty.")

if train_df["country_fold"].nunique() < 2:
    raise ValueError("Need at least 2 countries in train_df for leave-one-country-out CV.")

# -----------------------------
# Recompute CV predictions so nothing is undefined
# -----------------------------
cv_X = train_df[feature_cols]
cv_y = train_df[target_col].to_numpy()
cv_groups = train_df["country_fold"]

logo = LeaveOneGroupOut()

oof_preds_tabpfn = np.full(len(train_df), np.nan)
oof_preds_rf = np.full(len(train_df), np.nan)

for cv_train_idx, cv_val_idx in logo.split(cv_X, cv_y, groups=cv_groups):
    X_tr = cv_X.iloc[cv_train_idx]
    y_tr = cv_y[cv_train_idx]

    X_val = cv_X.iloc[cv_val_idx]

    model_cv = TabPFNRegressor()
    model_cv.fit(X_tr, y_tr)
    oof_preds_tabpfn[cv_val_idx] = model_cv.predict(X_val)

    modRF_cv = RandomForestRegressor(random_state=42)
    modRF_cv.fit(X_tr, y_tr)
    oof_preds_rf[cv_val_idx] = modRF_cv.predict(X_val)

# Final check that every training row got a CV prediction
if np.isnan(oof_preds_tabpfn).any():
    raise ValueError("Some TabPFN CV predictions are missing.")
if np.isnan(oof_preds_rf).any():
    raise ValueError("Some Random Forest CV predictions are missing.")

# -----------------------------
# Compute overall metrics
# -----------------------------
cv_metrics_tabpfn = {
    "MSE": mean_squared_error(cv_y, oof_preds_tabpfn),
    "R2": r2_score(cv_y, oof_preds_tabpfn),
}
cv_metrics_rf = {
    "MSE": mean_squared_error(cv_y, oof_preds_rf),
    "R2": r2_score(cv_y, oof_preds_rf),
}

test_metrics_tabpfn = {
    "MSE": mean_squared_error(y_test, preds),
    "R2": r2_score(y_test, preds),
}
test_metrics_rf = {
    "MSE": mean_squared_error(y_test, predsRF),
    "R2": r2_score(y_test, predsRF),
}

# -----------------------------
# Plot 1: Overall CV metrics
# -----------------------------
metrics = ["MSE", "R2"]
x = np.arange(len(metrics))
width = 0.35

plt.figure(figsize=(7, 5))
plt.bar(x - width/2, [cv_metrics_tabpfn[m] for m in metrics], width, label="TabPFN")
plt.bar(x + width/2, [cv_metrics_rf[m] for m in metrics], width, label="Random Forest")
plt.xticks(x, metrics)
plt.ylabel("Value")
plt.title("Overall Cross-Validation Metrics")
plt.legend()
plt.tight_layout()
plt.show()

# -----------------------------
# Plot 2: Test metrics
# -----------------------------
plt.figure(figsize=(7, 5))
plt.bar(x - width/2, [test_metrics_tabpfn[m] for m in metrics], width, label="TabPFN")
plt.bar(x + width/2, [test_metrics_rf[m] for m in metrics], width, label="Random Forest")
plt.xticks(x, metrics)
plt.ylabel("Value")
plt.title("Test Set Metrics")
plt.legend()
plt.tight_layout()
plt.show()
