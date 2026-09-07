# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE for configuration/paths.R
#
# The scripts source configuration/paths.R, which is git-ignored so that each
# user keeps their own local paths out of version control. This template lists
# every path variable the scripts expect, with the values left blank.
#
# To set up:
#   1. Copy this file to configuration/paths.R
#          cp configuration/paths.example.R configuration/paths.R
#   2. Fill in each value below with the absolute path to the corresponding
#      file or directory on the local machine (e.g. the local switchdrive
#      mount). Directory paths should keep their trailing slash where shown.
#   3. Leave this template unchanged so it stays a clean reference for others.
# ─────────────────────────────────────────────────────────────────────────────

# ── Household survey microdata ───────────────────────────────────────────────
PATH_TO_SURVEYS_DHS_water_quality <- ""  # HH DHS water-quality survey directory
PATH_TO_SURVEYS_DHS_other         <- ""  # HH DHS other survey directory
PATH_TO_SURVEYS_MIS               <- ""  # HH DHS MIS survey directory
PATH_TO_SURVEYS_old_SMDW          <- ""  # HH MICS old SMDW survey directory
PATH_TO_SURVEYS_new_SMDW          <- ""  # HH MICS new SMDW survey directory
PATH_TO_SURVEYS_new_other         <- ""  # HH MICS new other survey directory
PATH_SURVEY_SMDW_OLD_MICS         <- ""  # df_SMDW_oldMICS.csv

# ── Collaborator-facing HH survey deliverables ──────────────────────────────
# Full household-level analysis files shared with collaborators. Writing these
# is deliberately gated in the prep scripts (04a/04b) so they are only
# regenerated intentionally, not as a side effect of a rerun.
PATH_SWITCHDRIVE_HH_DIR     <- ""  # base directory holding the HH deliverable files
PATH_HH_SMDW_ANALYSIS       <- file.path(PATH_SWITCHDRIVE_HH_DIR, "df_hh_smdw_analysis.csv")
PATH_HH_SANITATION_ANALYSIS <- file.path(PATH_SWITCHDRIVE_HH_DIR, "df_hh_sanitation_analysis.csv")

# Working household-level sanitation analysis file (v2, WS11 labelling corrections)
PATH_HH_SANITATION_ANALYSIS_V2 <- ""  # df_hh_sanitation_analysis_v2.csv

# ── GADM region names table ──────────────────────────────────────────────────
PATH_GADM_REGIONS <- ""  # all_regions_GADM.csv

# ── Geospatial covariates (GEE-sampled, population) ──────────────────────────
PATH_TO_POP_SUMS_PRED  <- ""  # population sums, prediction directory
PATH_TO_POP_SUMS_WQ    <- ""  # population sums, water-quality training directory
PATH_TO_POP_SUMS_OTHER <- ""  # population sums, other training directory
FILE_NONPOP_WQ         <- ""  # water_quality_covariates_nonpop_*.csv
FILE_NONPOP_OTHER      <- ""  # other_surveys_covariates_nonpop_*.csv

# ── Country-level covariates ─────────────────────────────────────────────────
PATH_GDP        <- ""  # gdp_per_capita_2015.csv
PATH_EDUCATION  <- ""  # secondary_education_years.csv
PATH_WASTEWATER <- ""  # Country_WWctr_Percentage.txt
PATH_OGHIST     <- ""  # OGHIST_*.xlsx (World Bank income groups)
PATH_JMP        <- ""  # JMP_2025_WLD.xlsx
PATH_WGI        <- ""  # worldwide_governance_indicators_prediction.csv

# ── Drinking water estimates ─────────────────────────────────────────────────
PATH_GW_RISK <- ""  # geogenic_groundwater_risk_estimates.xlsx

# ── Version tag (bump when re-running to avoid overwriting previous outputs) ──
VERSION <- "v1"

# ── Deliverable output paths ─────────────────────────────────────────────────
# Base directory/prefix for writing estimate deliverables; VERSION is appended.
PATH_OUT_SMDW       <- paste0("", "smdw_estimates_admin1_", VERSION, ".csv")
PATH_OUT_SANITATION <- ""  # sanitation_estimates_admin1.csv
