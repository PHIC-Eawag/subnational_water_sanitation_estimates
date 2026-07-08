
# ── Household survey microdata ───────────────────────────────────────────────
PATH_TO_SURVEYS_DHS_water_quality <- "~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/HH_DHS_water_quality/"
PATH_TO_SURVEYS_DHS_other         <- "~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/HH_DHS_other/"
PATH_TO_SURVEYS_MIS               <- "~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/HH_DHS_MIS/"
PATH_TO_SURVEYS_old_SMDW          <- "~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/HH_MICS_old_SMDW"
PATH_TO_SURVEYS_new_SMDW          <- "~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/HH_MICS_new_SMDW/"
PATH_TO_SURVEYS_new_other         <- "~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/HH_MICS_new_other/"
PATH_SURVEY_SMDW_OLD_MICS         <- "~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/df_SMDW_oldMICS.csv"

# ── GADM region names table ──────────────────────────────────────────────────
PATH_GADM_REGIONS <- "~/switchdrive/Eawag/WorldBankProject/regions/all_regions_GADM.csv"

# ── Geospatial covariates (GEE-sampled, population) ──────────────────────────
PATH_TO_POP_SUMS_PRED  <- "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/pop_sums_prediction"
PATH_TO_POP_SUMS_WQ    <- "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/pop_sums_training_water_quality"
PATH_TO_POP_SUMS_OTHER <- "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/pop_sums_training_other"
FILE_NONPOP_WQ         <- "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/water_quality_covariates_nonpop_v4.csv"
FILE_NONPOP_OTHER      <- "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/other_surveys_covariates_nonpop_v3.csv"

# ── Country-level covariates ─────────────────────────────────────────────────
PATH_GDP        <- "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/gdp_per_capita_2015.csv"
PATH_EDUCATION  <- "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/secondary_education_years.csv"
PATH_WASTEWATER <- "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/Country_WWctr_Percentage.txt"
PATH_OGHIST     <- "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/OGHIST_2026_03_10.xlsx"
PATH_JMP        <- "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/JMP_2025_WLD.xlsx"
PATH_WGI        <- "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/worldwide_governance_indicators_prediction.csv"

# ── Drinking water estimates ─────────────────────────────────────────────────
PATH_GW_RISK <- "~/switchdrive/Eawag/WorldBankProject/deliverables_0002020937/datasets/geogenic_groundwater_risk_estimates.xlsx"

# ── Version tag (bump when re-running to avoid overwriting previous outputs) ──
VERSION <- "v1"

# ── Deliverable output paths ─────────────────────────────────────────────────
PATH_OUT_SMDW       <- paste0("~/switchdrive/Eawag/WorldBankProject/smdw_estimates_admin1_", VERSION, ".csv")
#PATH_OUT_SMDW       <- paste0("~/switchdrive/Eawag/WorldBankProject/deliverables_0002020937/smdw_estimates_admin1_", VERSION, ".csv")
PATH_OUT_SANITATION <- "~/switchdrive/Eawag/WorldBankProject/deliverables_0002020937/datasets/sanitation_estimates_admin1.csv"
