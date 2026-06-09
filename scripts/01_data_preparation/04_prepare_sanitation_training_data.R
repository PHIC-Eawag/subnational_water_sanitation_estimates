# ============================================================
# Prepare model training datasets for sanitation outcomes
# ============================================================
#
# Outcomes:
#   basic_sanitation  – improved facility (WS11 == 2) AND not shared (WS15 == 0)
#   open_defecation   – no facility / bush / field (WS11 == 0)
#
# Data source:
#   MICS:  df_sanitation_MICS_v1.csv  (compiled by compile_mics_sanitation_data.R)
#   DHS:   PATH_TO_DHS_SANITATION     (placeholder — add when available)
#
# Geospatial covariates:
#   Same as SMDW "other" subcomponents (PATH_TO_POP_SUMS_OTHER / FILE_NONPOP_OTHER)
#
# Region crosswalk fixes:
#   Same as SMDW "other" subcomponents (same underlying surveys)
#
# Outputs:
#   ./data/training_subcomponents/basic_sanitation_training_with_covariates.csv
#   ./data/training_subcomponents/open_defecation_training_with_covariates.csv
#
# Crosswalk review files:
#   ./data/crosswalk_review/

library(tidyverse)
library(here)
library(fuzzyjoin)
library(stringdist)
library(stringi)

source(here::here("./functions/create_indicators.R"))
source(here::here("./functions/create_sanitation_indicators.R"))
source(here::here("./functions/join_and_structure_dataframes.R"))

# ============================================================
# Geospatial covariate paths
# ============================================================
# Sanitation uses the same "other" covariate set as the SMDW subcomponents
# (improved source, availability, accessibility).

PATH_TO_POP_SUMS_OTHER <- "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/pop_sums_training_other"
FILE_NONPOP_OTHER       <- "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/other_surveys_covariates_nonpop_v2.csv"

pop_files_other <- list.files(
  path      = path.expand(PATH_TO_POP_SUMS_OTHER),
  pattern   = "\\.csv$",
  full.names = TRUE
)

covariate_cols <- c(
  "CGIAR_Aridity_Index", "CGIAR_PET",
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
  "MODIS_EVI", "MODIS_NDVI", "MODIS_NPP",
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
  "worldpop"
)

# ============================================================
# Read household survey inputs
# ============================================================

# MICS sanitation data (compiled by compile_mics_sanitation_data.R)
df.MICS_HH_sanitation <- readr::read_csv(
  "~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/df_sanitation_MICS_v1.csv",
  show_col_types = FALSE
) %>%
  dplyr::mutate(household_data_source = "MICS_sanitation")

# DHS sanitation data (compiled by compile_dhs_sanitation_data.R)
df.DHS_HH_sanitation <- readr::read_csv(
  "~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/df_sanitation_DHS.csv",
  show_col_types = FALSE
) %>%
  dplyr::mutate(household_data_source = "DHS_sanitation")

# Combine all sources
df_hh_sanitation <- dplyr::bind_rows(
  df.MICS_HH_sanitation,
  df.DHS_HH_sanitation
)

# ============================================================
# Read lookup and metadata inputs
# ============================================================
df.WGI_lmics <- readWGI_lmics()

country_name_key_WB <- readr::read_csv(
  here::here("./data/country_name_key_WB.csv"),
  show_col_types = FALSE
)

# ============================================================
# Filter to surveys within 2015–2024
# ============================================================
countries_HH5Y_outside_range <- df_hh_sanitation %>%
  dplyr::filter(!is.na(HH5Y), HH5Y < 2015 | HH5Y > 2024) %>%
  dplyr::distinct(country) %>%
  dplyr::arrange(country)
print(countries_HH5Y_outside_range)

df_hh_sanitation <- df_hh_sanitation %>%
  dplyr::mutate(
    HH5Y_original = HH5Y,
    HH5Y = standardise_survey_year(country, HH5Y)
  ) %>%
  dplyr::filter(is.na(HH5Y) | HH5Y >= 2015)

# ============================================================
# Summarise survey years and select one source per country
# ============================================================
country_source_summary <- df_hh_sanitation %>%
  dplyr::mutate(HH5Y = as.integer(HH5Y)) %>%
  dplyr::group_by(country, household_data_source) %>%
  dplyr::summarise(
    min_year     = ifelse(all(is.na(HH5Y)), NA_integer_, min(HH5Y, na.rm = TRUE)),
    max_year     = ifelse(all(is.na(HH5Y)), NA_integer_, max(HH5Y, na.rm = TRUE)),
    survey_years = paste(sort(unique(HH5Y[!is.na(HH5Y)])), collapse = ", "),
    n_rows       = dplyr::n(),
    .groups = "drop"
  )
print(country_source_summary)

source_to_keep <- country_source_summary %>%
  dplyr::group_by(country) %>%
  dplyr::arrange(
    desc(!is.na(max_year)),
    desc(max_year),
    desc(n_rows),
    household_data_source
  ) %>%
  dplyr::slice(1) %>%
  dplyr::ungroup() %>%
  dplyr::select(country, household_data_source)
print(source_to_keep)

source_to_drop <- country_source_summary %>%
  dplyr::anti_join(source_to_keep, by = c("country", "household_data_source")) %>%
  dplyr::arrange(country, household_data_source)
print(source_to_drop)

df_hh_sanitation <- df_hh_sanitation %>%
  dplyr::semi_join(source_to_keep, by = c("country", "household_data_source"))

# ============================================================
# Build covariate table
# ============================================================
df_training_covariates_sanitation <- make_training_covariates(
  pop_files      = pop_files_other,
  nonpop_files   = FILE_NONPOP_OTHER,
  covariate_cols = covariate_cols
)

duplicate_covariate_keys_sanitation <- check_duplicate_covariate_keys(
  df_training_covariates_sanitation
)
duplicate_covariate_keys_sanitation

# ============================================================
# Create outcomes
# ============================================================
basic_sanitation_outcome <- make_basic_sanitation_regional_outcome(
  df_hh_sanitation
)

open_defecation_outcome <- make_open_defecation_regional_outcome(
  df_hh_sanitation
)

# ============================================================
# Year lookups and PSU weights
# ============================================================
sanitation_year_lookup <- make_year_lookup_from_raw_household_data(
  df_hh_sanitation
)

basic_sanitation_outcome <- add_n_psu_weight(
  hh_df      = df_hh_sanitation,
  outcome_df = basic_sanitation_outcome,
  year_lookup = sanitation_year_lookup
)

open_defecation_outcome <- add_n_psu_weight(
  hh_df      = df_hh_sanitation,
  outcome_df = open_defecation_outcome,
  year_lookup = sanitation_year_lookup
)

# Quick check
n_psu_check <- dplyr::bind_rows(
  basic_sanitation_outcome %>% dplyr::mutate(check_outcome = "basic_sanitation"),
  open_defecation_outcome  %>% dplyr::mutate(check_outcome = "open_defecation")
) %>%
  dplyr::group_by(check_outcome) %>%
  dplyr::summarise(
    n_rows       = dplyr::n(),
    missing_n_psu = sum(is.na(n_psu)),
    min_n_psu    = min(n_psu, na.rm = TRUE),
    median_n_psu = median(n_psu, na.rm = TRUE),
    max_n_psu    = max(n_psu, na.rm = TRUE),
    .groups = "drop"
  )
print(n_psu_check)

# ============================================================
# Filter covariates to outcome country-year pairs
# ============================================================
df_covariates_basic_sanitation <- filter_covariates_to_outcome_years(
  outcome_df             = basic_sanitation_outcome,
  df_training_covariates = df_training_covariates_sanitation,
  country_name_key_WB    = country_name_key_WB
)

df_covariates_open_defecation <- filter_covariates_to_outcome_years(
  outcome_df             = open_defecation_outcome,
  df_training_covariates = df_training_covariates_sanitation,
  country_name_key_WB    = country_name_key_WB
)

check_duplicate_covariate_join_keys(df_covariates_basic_sanitation)
check_duplicate_covariate_join_keys(df_covariates_open_defecation)

# ============================================================
# Diagnose countries dropped during covariate filtering
# ============================================================

diagnose_country_year_filtering <- function(
    outcome_name,
    outcome_df,
    raw_covariates,
    filtered_covariates,
    country_name_key_WB
) {
  
  wb_lookup <- build_wb_country_lookup(country_name_key_WB)
  
  outcome_country_years <- outcome_df %>%
    dplyr::transmute(
      outcome_name = outcome_name,
      country_outcome,
      country_key = clean_key(country_outcome),
      analysis_year = as.integer(analysis_year)
    ) %>%
    dplyr::distinct()
  
  raw_cov_country_years <- raw_covariates %>%
    dplyr::transmute(
      country_cov = country,
      country_key = clean_key(country),
      analysis_year = as.integer(analysis_year)
    ) %>%
    dplyr::distinct()
  
  filtered_cov_country_years <- filtered_covariates %>%
    dplyr::transmute(
      country_cov_filtered = country,
      country_key = clean_key(country),
      analysis_year = as.integer(analysis_year)
    ) %>%
    dplyr::distinct()
  
  outcome_country_years %>%
    dplyr::inner_join(
      raw_cov_country_years,
      by = c("country_key", "analysis_year")
    ) %>%
    dplyr::anti_join(
      filtered_cov_country_years,
      by = c("country_key", "analysis_year")
    ) %>%
    dplyr::left_join(
      wb_lookup,
      by = c("country_key" = "country_alias_key")
    ) %>%
    dplyr::mutate(
      likely_issue = dplyr::case_when(
        is.na(country_wb) ~ "country not mapped in build_wb_country_lookup()",
        TRUE ~ "mapped, check another filtering issue"
      )
    ) %>%
    dplyr::arrange(outcome_name, country_outcome, analysis_year)
}

country_year_filtering_issues <- dplyr::bind_rows(
  diagnose_country_year_filtering(
    outcome_name           = "basic_sanitation",
    outcome_df             = basic_sanitation_outcome,
    raw_covariates         = df_training_covariates_sanitation,
    filtered_covariates    = df_covariates_basic_sanitation,
    country_name_key_WB    = country_name_key_WB
  ),
  diagnose_country_year_filtering(
    outcome_name           = "open_defecation",
    outcome_df             = open_defecation_outcome,
    raw_covariates         = df_training_covariates_sanitation,
    filtered_covariates    = df_covariates_open_defecation,
    country_name_key_WB    = country_name_key_WB
  )
)
print(country_year_filtering_issues)

# ============================================================
# Build region crosswalks
# ============================================================
crosswalk_basic_sanitation <- build_crosswalk_for_one_outcome(
  outcome_name           = "basic_sanitation",
  outcome_df             = basic_sanitation_outcome,
  df_training_covariates = df_covariates_basic_sanitation,
  country_name_key_WB    = country_name_key_WB
)

crosswalk_open_defecation <- build_crosswalk_for_one_outcome(
  outcome_name           = "open_defecation",
  outcome_df             = open_defecation_outcome,
  df_training_covariates = df_covariates_open_defecation,
  country_name_key_WB    = country_name_key_WB
)

# Inspect rows needing manual review
crosswalk_basic_sanitation$regions_to_review
crosswalk_open_defecation$regions_to_review

# ============================================================
# Manual region fixes
# ============================================================
# Identical to the SMDW "other" subcomponents — same underlying
# MICS surveys. Add sanitation-specific entries below if needed
# when DHS data is incorporated.

manual_fixes_sanitation <- tibble::tribble(
  ~HH7_region_outcome,                         ~country_cov,                              ~correct_region_name,

  # Afghanistan
  "MAIDAN WARDAK",                             "Afghanistan",                             "Wardak",

  # Chad
  "Ndjamena",                                  "Chad",                                    "Ville de N'Djamena",
  "Ouadda?",                                   "Chad",                                    "Ouaddaï",

  # Democratic Republic of the Congo
  "Maindombe",                                 "Democratic Republic of the Congo",        "Maï-Ndombe",

  # Georgia
  "KHAKHETI",                                  "Georgia",                                 "Kakheti",

  # Guinea-Bissau
  "SAB",                                       "Guinea-Bissau",                           "Bissau",

  # Iraq
  "DUHOK",                                     "Iraq",                                    "Dihok",
  "ERBIL",                                     "Iraq",                                    "Arbil",
  "THIQAR",                                    "Iraq",                                    "Dhi-Qar",
  "NAINAWA",                                   "Iraq",                                    "Ninawa",
  "KARBALAH",                                  "Iraq",                                    "Karbala'",
  "DIALA",                                     "Iraq",                                    "Diyala",
  "SALAHADDIN",                                "Iraq",                                    "Sala ad-Din",
  "ANBAR",                                     "Iraq",                                    "Al-Anbar",
  "BASRAH",                                    "Iraq",                                    "Al-Basrah",
  "QADISYAH",                                  "Iraq",                                    "Al-Qadisiyah",
  "NAJAF",                                     "Iraq",                                    "An-Najaf",
  "MISAN",                                     "Iraq",                                    "Maysan",
  "SULAIMANIYA",                               "Iraq",                                    "As-Sulaymaniyah",
  "MUTHANA",                                   "Iraq",                                    "Al-Muthannia",
  "KIRKUK",                                    "Iraq",                                    "At-Ta'mim",

  # Kiribati
  "LINE AND PHOENIX GROUP",                    "Kiribati",                                "LINE_AND_PHOENIX",

  # Lao PDR
  "XAYSOMBOUN",                                "Lao People's Democratic Republic",        "Xaysomboune",
  "KHAMMUAN",                                  "Lao People's Democratic Republic",        "Khammua",

  # Lesotho
  "MOHALES HOEK",                              "Lesotho",                                 "Mohale's Hoek",
  "QACHAS NEK",                                "Lesotho",                                 "Qacha's Nek",

  # Malawi
  "Dowa (Camps)",                              "Malawi",                                  "Dowa",

  # Nepal
  "Sudurpashchim",                             "Nepal",                                   "Sudur Paschim",

  # Pakistan
  "Chaghi",                                    "Pakistan",                                "Chagai",
  "DG Khan",                                   "Pakistan",                                "Dera Ghazi Khan",
  "Kachhi (Bolan)",                            "Pakistan",                                "Kachhi",
  "Bajor",                                     "Pakistan",                                "Bajaur",
  "TT Singh",                                  "Pakistan",                                "Toba Tek Singh",
  "RY Khan",                                   "Pakistan",                                "Rahim Yar Khan",
  "Laki Marwat",                               "Pakistan",                                "Lakki Marwat",
  "Abbotabad",                                 "Pakistan",                                "Abbottabad",
  "Nowshehra",                                 "Pakistan",                                "Nowshera",
  "Sheerani",                                  "Pakistan",                                "Sherani",
  "Hari Pur",                                  "Pakistan",                                "Haripur",
  "Torghar",                                   "Pakistan",                                "Tor Ghar",
  "Kuram",                                     "Pakistan",                                "Kurram",
  "Sibbi",                                     "Pakistan",                                "Sibi",
  "Mohmind",                                   "Pakistan",                                "Mohmand",
  "Kech (Turbat)",                             "Pakistan",                                "Kech",

  # São Tomé and Príncipe
  "REGIÃO AUTÓNOMA DO PRÍNCIPE",               "São Tomé and Príncipe",                   "Príncipe",

  # Tonga
  "ONGO NIUA",                                 "Tonga",                                   "Niuas",

  # Tuvalu
  "Nanumaga",                                  "Tuvalu",                                  "Nanumanga",
  "Funafuti",                                  "Tuvalu",                                  "Funafuti",
  "Nanumea",                                   "Tuvalu",                                  "Nanumea",
  "Niutao",                                    "Tuvalu",                                  "Niutao",
  "Nui",                                       "Tuvalu",                                  "Nui",
  "Nukufetau",                                 "Tuvalu",                                  "Nukufetau",
  "Vaitupu",                                   "Tuvalu",                                  "Vaitupu",

  # Vietnam
  "NORTH CENTRAL AND CENTRAL COASTAL",         "Vietnam",                                 "NORTH_CENTRAL_AND_COASTAL",

  # West Bank and Gaza
  "Qalqilia",                                  "Palestina",                               "Qalqilya",
  "Ariha & Al Aghwar",                         "Palestina",                               "Jericho",
  "North Gaza",                                "Palestina",                               "Gaza ash Shamaliyah",

  # Argentina
  "CIUDAD Y PARTIDOS DE BUENOS AIRES",                     "Argentina",   "CIUDAD_Y_PARTIDOS_DE_BUENOS_AIRES_Argentina",
  "RESTO PROVINCIA DE BUENOS AIRES",                       "Argentina",   "RESTO_PROVINCIA_DE_BUENOS_AIRES_Argentina",
  "CUYO",                                                  "Argentina",   "CUYO_Argentina",
  "NOA",                                                   "Argentina",   "NOA_Argentina",
  "NEA",                                                   "Argentina",   "NEA_Argentina",
  "PAMPEANA (EXCLUYE RESTO DE PROVINCIA DE BUENOS AIRES",  "Argentina",   "PAMPEANA_Argentina",
  "PATAGÓNICA",                                            "Argentina",   "PATAGONICA_Argentina",

  # Nauru
  "AIWO",      "Nauru",  "AIWO_Nauru",
  "ANABAR",    "Nauru",  "ANABAR_Nauru",
  "ANETAN",    "Nauru",  "ANETAN_Nauru",
  "ANIBARE",   "Nauru",  "ANIBARE_Nauru",
  "BAITSI",    "Nauru",  "BAITSI_Nauru",
  "BOE",       "Nauru",  "BOE_Nauru",
  "BUADA",     "Nauru",  "BUADA_Nauru",
  "DENIGOMODU","Nauru",  "DENIGOMODU_Nauru",
  "EWA",       "Nauru",  "EWA_Nauru",
  "IJUW",      "Nauru",  "IJUW_Nauru",
  "MENENG",    "Nauru",  "MENENG_Nauru",
  "NIBOK",     "Nauru",  "NIBOK_Nauru",
  "UABOE",     "Nauru",  "UABOE_Nauru",
  "YAREN",     "Nauru",  "YAREN_Nauru",

  # Trinidad and Tobago
  "Eastern RHA",       "Trinidad and Tobago",  "Eastern_RHA_Trinidad_and_Tobago",
  "North-Central RHA", "Trinidad and Tobago",  "North_Central_RHA_Trinidad_and_Tobago",
  "North-West RHA",    "Trinidad and Tobago",  "North_West_RHA_Trinidad_and_Tobago",
  "South-West RHA",    "Trinidad and Tobago",  "South_West_RHA_Trinidad_and_Tobago",
  "Tobago RHA",        "Trinidad and Tobago",  "Tobago_RHA_Trinidad_and_Tobago",

  # North Macedonia
  "EAST",       "North Macedonia",  "EAST_North_Macedonia",
  "NORTHEAST",  "North Macedonia",  "NORTHEAST_North_Macedonia",
  "PELAGONIJA", "North Macedonia",  "PELAGONIJA_North_Macedonia",
  "POLOG",      "North Macedonia",  "POLOG_North_Macedonia",
  "SKOPJE",     "North Macedonia",  "SKOPJE_North_Macedonia",
  "SOUTHEAST",  "North Macedonia",  "SOUTHEAST_North_Macedonia",
  "SOUTHWEST",  "North Macedonia",  "SOUTHWEST_North_Macedonia",
  "VARDAR",     "North Macedonia",  "VARDAR_North_Macedonia",

  # Costa Rica
  "Alajuela",   "Costa Rica",  "Alajuela_Costa_Rica",
  "Cartago",    "Costa Rica",  "Cartago_Costa_Rica",
  "Guanacaste", "Costa Rica",  "Guanacaste_Costa_Rica",
  "Heredia",    "Costa Rica",  "Heredia_Costa_Rica",
  "Limón",      "Costa Rica",  "Limon_Costa_Rica",
  "Limon",      "Costa Rica",  "Limon_Costa_Rica",
  "Puntarenas", "Costa Rica",  "Puntarenas_Costa_Rica",
  "San José",   "Costa Rica",  "San_Jose_Costa_Rica",
  "San Jose",   "Costa Rica",  "San_Jose_Costa_Rica"
)

# ============================================================
# Apply manual fixes
# ============================================================
basic_sanitation_crosswalk_final <- apply_manual_fixes_for_one_outcome(
  outcome_name     = "basic_sanitation",
  crosswalk_results = crosswalk_basic_sanitation,
  manual_region_fixes = manual_fixes_sanitation
)

open_defecation_crosswalk_final <- apply_manual_fixes_for_one_outcome(
  outcome_name     = "open_defecation",
  crosswalk_results = crosswalk_open_defecation,
  manual_region_fixes = manual_fixes_sanitation
)

# ============================================================
# Join outcomes to covariates and write training CSVs
# ============================================================
basic_sanitation_training_output <- join_and_save_one_training_dataset(
  outcome_name           = "basic_sanitation",
  outcome_df             = basic_sanitation_outcome,
  df_training_covariates = df_covariates_basic_sanitation,
  region_crosswalk_final = basic_sanitation_crosswalk_final
)

open_defecation_training_output <- join_and_save_one_training_dataset(
  outcome_name           = "open_defecation",
  outcome_df             = open_defecation_outcome,
  df_training_covariates = df_covariates_open_defecation,
  region_crosswalk_final = open_defecation_crosswalk_final
)

basic_sanitation_training_with_covariates <- basic_sanitation_training_output$training_with_covariates
open_defecation_training_with_covariates  <- open_defecation_training_output$training_with_covariates

basic_sanitation_missing_covariates <- basic_sanitation_training_output$missing_covariates
open_defecation_missing_covariates  <- open_defecation_training_output$missing_covariates

# ============================================================
# Add GDP and secondary education
# ============================================================
gdp_per_capita_2015 <- readr::read_csv(
  "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/gdp_per_capita_2015.csv"
)
secondary_education_years <- readr::read_csv(
  "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/secondary_education_years.csv"
)

add_country_join_key <- function(df, country_col, country_name_key_WB) {
  
  wb_lookup <- build_wb_country_lookup(country_name_key_WB)
  
  df %>%
    dplyr::mutate(
      country_alias_key = clean_key({{ country_col }})
    ) %>%
    dplyr::left_join(
      wb_lookup,
      by = "country_alias_key"
    ) %>%
    dplyr::mutate(
      # If country is not in WB lookup, keep cleaned country name as fallback
      country_join = dplyr::coalesce(country_wb, country_alias_key)
    ) %>%
    dplyr::select(-country_alias_key, -country_wb)
}


gdp_clean <- gdp_per_capita_2015 %>%
  dplyr::rename(
    country_name = Country.Name,
    analysis_year = Year,
    gdp_per_capita_constant_2015_usd = `GDP per capita (constant 2015 US$)`
  ) %>%
  dplyr::mutate(
    analysis_year = as.integer(analysis_year),
    gdp_per_capita_constant_2015_usd = as.numeric(gdp_per_capita_constant_2015_usd)
  ) %>%
  add_country_join_key(country_col = country_name, country_name_key_WB = country_name_key_WB) %>%
  dplyr::select(country_join, analysis_year, gdp_per_capita_constant_2015_usd) %>%
  dplyr::distinct()

education_clean <- secondary_education_years %>%
  dplyr::rename(
    country_name = Country.Name,
    analysis_year = Year,
    secondary_education_duration_years = `Secondary education, duration (years)`
  ) %>%
  dplyr::mutate(
    analysis_year = as.integer(analysis_year),
    secondary_education_duration_years = as.numeric(secondary_education_duration_years)
  ) %>%
  add_country_join_key(country_col = country_name, country_name_key_WB = country_name_key_WB) %>%
  dplyr::select(country_join, analysis_year, secondary_education_duration_years) %>%
  dplyr::distinct()

country_year_covariates_clean <- gdp_clean %>%
  dplyr::full_join(education_clean, by = c("country_join", "analysis_year"))

add_country_year_covariates <- function(training_df) {
  training_df %>%
    dplyr::mutate(analysis_year = as.integer(analysis_year)) %>%
    add_country_join_key(country_col = country_outcome, country_name_key_WB = country_name_key_WB) %>%
    dplyr::left_join(country_year_covariates_clean, by = c("country_join", "analysis_year")) %>%
    dplyr::select(-country_join)
}

basic_sanitation_training_with_covariates <- add_country_year_covariates(
  basic_sanitation_training_with_covariates
)
open_defecation_training_with_covariates <- add_country_year_covariates(
  open_defecation_training_with_covariates
)

# Check missing GDP / education
check_missing_country_year_covariates <- function(training_df, outcome_name) {
  training_df %>%
    dplyr::filter(
      is.na(gdp_per_capita_constant_2015_usd) | is.na(secondary_education_duration_years)
    ) %>%
    dplyr::distinct(country_outcome, analysis_year,
                    gdp_per_capita_constant_2015_usd, secondary_education_duration_years) %>%
    dplyr::mutate(outcome_type = outcome_name) %>%
    dplyr::arrange(country_outcome, analysis_year)
}

missing_country_year_covariates <- dplyr::bind_rows(
  check_missing_country_year_covariates(basic_sanitation_training_with_covariates, "basic_sanitation"),
  check_missing_country_year_covariates(open_defecation_training_with_covariates,  "open_defecation")
)
print(missing_country_year_covariates)

# ============================================================
# Add wastewater country-level covariates
# ============================================================
ww_country_raw <- readr::read_tsv(
  "~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/Country_WWctr_Percentage.txt",
  show_col_types = FALSE
)

add_country_join_key_country_level <- function(df, country_col, country_name_key_WB) {
  
  wb_lookup <- build_wb_country_lookup(country_name_key_WB)
  
  df %>%
    dplyr::select(
      -dplyr::any_of(c("country_join", "country_alias_key", "country_wb"))
    ) %>%
    dplyr::mutate(
      country_alias_key = clean_key({{ country_col }})
    ) %>%
    dplyr::left_join(
      wb_lookup,
      by = "country_alias_key"
    ) %>%
    dplyr::mutate(
      country_join_raw = dplyr::coalesce(country_wb, country_alias_key),
      
      country_join_raw = dplyr::case_when(
        country_alias_key == "bolivia plurinational state of" ~ "Bolivia",
        country_alias_key == "congo dem republic" ~ "Congo, Dem. Rep.",
        country_alias_key == "congo rep" ~ "Congo, Rep.",
        country_alias_key == "cote d ivoire" ~ "Cote d'Ivoire",
        country_alias_key == "iran islamic republic of" ~ "Iran, Islamic Rep.",
        country_alias_key %in% c("lao peoples democratic republic", "lao people s democratic republic") ~ "Lao PDR",
        country_alias_key == "macedonia fyr" ~ "North Macedonia",
        country_alias_key == "sao tome and principe" ~ "Sao Tome and Principe",
        country_alias_key %in% c("swaziland", "eswatini") ~ "Eswatini",
        country_alias_key == "tanzania" ~ "Tanzania",
        country_alias_key == "venezuela bolivarian republic of" ~ "Venezuela, RB",
        country_alias_key %in% c("viet nam", "vietnam") ~ "Viet Nam",
        country_alias_key %in% c("west bank gaza", "west bank and gaza") ~ "West Bank and Gaza",
        TRUE ~ country_join_raw
      ),
      
      country_join = clean_key(country_join_raw)
    ) %>%
    dplyr::select(-country_alias_key, -country_wb, -country_join_raw)
}

ww_country_clean <- ww_country_raw %>%
  dplyr::rename(
    ww_country_name          = Country,
    ww_region                = Region,
    ww_economic_classification = Economic_Classification,
    ww_collection_percent    = WWc_Percent,
    ww_treatment_percent     = WWt_Percent,
    ww_reuse_percent         = WWr_Percent
  ) %>%
  dplyr::mutate(
    ww_collection_percent = as.numeric(ww_collection_percent),
    ww_treatment_percent  = as.numeric(ww_treatment_percent),
    ww_reuse_percent      = as.numeric(ww_reuse_percent)
  ) %>%
  add_country_join_key_country_level(
    country_col = ww_country_name, country_name_key_WB = country_name_key_WB
  ) %>%
  dplyr::select(
    country_join, ww_country_name, ww_region,
    ww_economic_classification,
    ww_collection_percent, ww_treatment_percent, ww_reuse_percent
  ) %>%
  dplyr::distinct(country_join, .keep_all = TRUE)

add_ww_country_covariates <- function(training_df) {
  training_df %>%
    dplyr::select(-dplyr::any_of(c(
      "country_join", "ww_country_name", "ww_region",
      "ww_economic_classification",
      "ww_collection_percent", "ww_treatment_percent", "ww_reuse_percent"
    ))) %>%
    add_country_join_key_country_level(
      country_col = country_outcome, country_name_key_WB = country_name_key_WB
    ) %>%
    dplyr::left_join(ww_country_clean, by = "country_join") %>%
    dplyr::select(-country_join)
}

basic_sanitation_training_with_covariates <- add_ww_country_covariates(
  basic_sanitation_training_with_covariates
)
open_defecation_training_with_covariates <- add_ww_country_covariates(
  open_defecation_training_with_covariates
)

# Check missing wastewater covariates
check_missing_ww_covariates <- function(training_df, outcome_name) {
  training_df %>%
    dplyr::filter(
      is.na(ww_collection_percent) | is.na(ww_treatment_percent) | is.na(ww_reuse_percent)
    ) %>%
    dplyr::distinct(country_outcome, ww_country_name,
                    ww_collection_percent, ww_treatment_percent, ww_reuse_percent) %>%
    dplyr::mutate(outcome_type = outcome_name) %>%
    dplyr::arrange(country_outcome)
}

missing_ww_covariates <- dplyr::bind_rows(
  check_missing_ww_covariates(basic_sanitation_training_with_covariates, "basic_sanitation"),
  check_missing_ww_covariates(open_defecation_training_with_covariates,  "open_defecation")
)
print(missing_ww_covariates)

# Manually assign Kosovo ww_region
fix_ww_region_manual <- function(training_df) {
  training_df %>%
    dplyr::mutate(
      ww_region = dplyr::case_when(
        country_outcome == "Kosovo" & is.na(ww_region) ~ "Eastern Europe & Central Asia",
        TRUE ~ ww_region
      )
    )
}
basic_sanitation_training_with_covariates <- fix_ww_region_manual(basic_sanitation_training_with_covariates)
open_defecation_training_with_covariates  <- fix_ww_region_manual(open_defecation_training_with_covariates)

# ============================================================
# Add WGI governance indicators
# ============================================================
indicator_map <- c(
  "Government Effectiveness - Governance score (0-100)" = "governance_effectiveness",
  "Control of Corruption - Governance score (0-100)"    = "control_of_corruption",
  "Political Stability - Governance score (0-100)"      = "political_stability",
  "Regulatory Quality - Governance score (0-100)"       = "regulatory_quality",
  "Rule of Law - Governance score (0-100)"              = "rule_of_law",
  "Voice and Accountability - Governance score (0-100)" = "voice_and_accountability"
)

add_country_join_key_wgi <- function(df, country_col, country_name_key_WB) {
  
  wb_lookup <- build_wb_country_lookup(country_name_key_WB)
  
  df %>%
    dplyr::select(
      -dplyr::any_of(c("country_join", "country_alias_key", "country_wb"))
    ) %>%
    dplyr::mutate(
      country_alias_key = clean_key({{ country_col }})
    ) %>%
    dplyr::left_join(
      wb_lookup,
      by = "country_alias_key"
    ) %>%
    dplyr::mutate(
      country_join_raw = dplyr::coalesce(country_wb, country_alias_key),
      
      country_join_raw = dplyr::case_when(
        country_alias_key == "bolivia plurinational state of" ~ "Bolivia",
        country_alias_key == "congo dem republic" ~ "Congo, Dem. Rep.",
        country_alias_key == "congo rep" ~ "Congo, Rep.",
        country_alias_key == "cote d ivoire" ~ "Cote d'Ivoire",
        country_alias_key == "iran islamic republic of" ~ "Iran, Islamic Rep.",
        country_alias_key %in% c("lao peoples democratic republic", "lao people s democratic republic") ~ "Lao PDR",
        country_alias_key == "macedonia fyr" ~ "North Macedonia",
        country_alias_key == "sao tome and principe" ~ "Sao Tome and Principe",
        country_alias_key %in% c("swaziland", "eswatini") ~ "Eswatini",
        country_alias_key == "tanzania" ~ "Tanzania",
        country_alias_key == "venezuela bolivarian republic of" ~ "Venezuela, RB",
        country_alias_key %in% c("viet nam", "vietnam") ~ "Viet Nam",
        country_alias_key %in% c("west bank gaza", "west bank and gaza") ~ "West Bank and Gaza",
        TRUE ~ country_join_raw
      ),
      
      country_join = clean_key(country_join_raw)
    ) %>%
    dplyr::select(-country_alias_key, -country_wb, -country_join_raw)
}

wgi_clean <- df.WGI_lmics %>%
  dplyr::filter(`Series.Name` %in% names(indicator_map)) %>%
  dplyr::mutate(indicator = unname(indicator_map[`Series.Name`])) %>%
  tidyr::pivot_longer(
    cols = dplyr::matches("^X20[0-9]{2}$"),
    names_to = "analysis_year",
    values_to = "value"
  ) %>%
  dplyr::mutate(
    analysis_year = as.integer(stringr::str_remove(analysis_year, "^X")),
    value = as.numeric(value)
  ) %>%
  add_country_join_key_wgi(
    country_col = `Country.Name`, country_name_key_WB = country_name_key_WB
  ) %>%
  dplyr::select(country_join, analysis_year, indicator, value) %>%
  tidyr::pivot_wider(names_from = indicator, values_from = value) %>%
  dplyr::distinct()

add_wgi_covariates <- function(training_df) {
  training_df %>%
    dplyr::select(-dplyr::any_of(c(
      "country_join",
      "governance_effectiveness", "control_of_corruption",
      "political_stability", "regulatory_quality",
      "rule_of_law", "voice_and_accountability"
    ))) %>%
    dplyr::mutate(analysis_year = as.integer(analysis_year)) %>%
    add_country_join_key_wgi(
      country_col = country_outcome, country_name_key_WB = country_name_key_WB
    ) %>%
    dplyr::left_join(wgi_clean, by = c("country_join", "analysis_year")) %>%
    dplyr::select(-country_join)
}

basic_sanitation_training_with_covariates <- add_wgi_covariates(
  basic_sanitation_training_with_covariates
)
open_defecation_training_with_covariates <- add_wgi_covariates(
  open_defecation_training_with_covariates
)

# Check missing WGI
check_missing_wgi_covariates <- function(training_df, outcome_name) {
  training_df %>%
    dplyr::filter(
      is.na(governance_effectiveness) | is.na(control_of_corruption) |
        is.na(political_stability) | is.na(regulatory_quality) |
        is.na(rule_of_law) | is.na(voice_and_accountability)
    ) %>%
    dplyr::distinct(
      country_outcome, analysis_year,
      governance_effectiveness, control_of_corruption,
      political_stability, regulatory_quality,
      rule_of_law, voice_and_accountability
    ) %>%
    dplyr::mutate(outcome_type = outcome_name) %>%
    dplyr::arrange(country_outcome, analysis_year)
}

missing_wgi_covariates <- dplyr::bind_rows(
  check_missing_wgi_covariates(basic_sanitation_training_with_covariates, "basic_sanitation"),
  check_missing_wgi_covariates(open_defecation_training_with_covariates,  "open_defecation")
)
print(missing_wgi_covariates)

# ============================================================
# Write final training datasets
# ============================================================
output_dir <- here::here("./data/training_subcomponents")
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

readr::write_csv(
  basic_sanitation_training_with_covariates,
  file.path(output_dir, "basic_sanitation_training_with_covariates.csv")
)
readr::write_csv(
  open_defecation_training_with_covariates,
  file.path(output_dir, "open_defecation_training_with_covariates.csv")
)

# ============================================================
# ww_region overview
# ============================================================
ww_region_summary <- dplyr::bind_rows(
  basic_sanitation_training_with_covariates %>% dplyr::mutate(outcome_type = "basic_sanitation"),
  open_defecation_training_with_covariates  %>% dplyr::mutate(outcome_type = "open_defecation")
) %>%
  dplyr::count(outcome_type, ww_region, name = "n_observations") %>%
  dplyr::group_by(outcome_type) %>%
  dplyr::mutate(
    percent_observations = round(100 * n_observations / sum(n_observations), 2)
  ) %>%
  dplyr::ungroup() %>%
  dplyr::arrange(outcome_type, desc(n_observations))
print(ww_region_summary)
