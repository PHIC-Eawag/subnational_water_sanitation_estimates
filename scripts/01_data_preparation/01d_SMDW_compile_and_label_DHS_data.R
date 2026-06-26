library(foreign)
library(tidyr)
library(dplyr)
library(tidyverse)
library(haven)
library(surveytoolbox)
library(survey)

source(here::here("functions/extract_label_dhs_variables.R"))
source(here::here("configuration/paths.R"))

country_name_key_WB <- readr::read_csv(
  here::here("configuration/country_name_key_WB.csv"),
  show_col_types = FALSE
)

loadSurveys(PATH_TO_SURVEYS_DHS_water_quality)


#Creating Variable with country name 
CIHR81FL$country <- "Côte d'Ivoire"
MWPR81FL$country <- "Malawi"
MZHR81FL$country <- "Mozambique"


# ------------------------------------------------------------
# Extract DHS variables into MICS-style columns
# ------------------------------------------------------------

hh_CotedIvoire_DHS <- extractDHSStandardSurveyVariables(
  CIHR81FL,
  country_name = "Côte d'Ivoire"
)

hh_Malawi_DHS <- extractDHSStandardSurveyVariables(
  MWPR81FL,
  country_name = "Malawi"
)

hh_Mozambique_DHS <- extractDHSStandardSurveyVariables(
  MZHR81FL,
  country_name = "Mozambique"
)

# ------------------------------------------------------------
# Check missing variables before relabelling
# ------------------------------------------------------------

DHS_surveys <- c(
  "CotedIvoire",
  "Malawi",
  "Mozambique"
)

for (survey_name in DHS_surveys) {
  dhs_data <- get(paste0("hh_", survey_name, "_DHS"))
  missing_variables <- checkDHSVariables(dhs_data)
  
  if (length(missing_variables) > 0) {
    message(survey_name, " is missing: ", paste(missing_variables, collapse = ", "))
  }
}

# ------------------------------------------------------------
# Extract DHS HH7 / HV024 region labels from raw files
# ------------------------------------------------------------

hh_CotedIvoire_HH7extract_DHS <- extractDHSAreaLabels(CIHR81FL, candidates = c("SHDISTRICT", "HV024"))
hh_Malawi_HH7extract_DHS      <- extractDHSAreaLabels(MWPR81FL, candidates = c("SHDISTRICT", "HV024"))
hh_Mozambique_HH7extract_DHS  <- extractDHSAreaLabels(MZHR81FL, candidates = c("SHDISTRICT", "HV024"))

# ------------------------------------------------------------
# Replace HH7 codes with region names
# ------------------------------------------------------------

hh_CotedIvoire_DHS <- replaceDHS_HH7LabelsWithRegionNames(
  hh_CotedIvoire_DHS,
  hh_CotedIvoire_HH7extract_DHS
)

hh_Malawi_DHS <- replaceDHS_HH7LabelsWithRegionNames(
  hh_Malawi_DHS,
  hh_Malawi_HH7extract_DHS
)

hh_Mozambique_DHS <- replaceDHS_HH7LabelsWithRegionNames(
  hh_Mozambique_DHS,
  hh_Mozambique_HH7extract_DHS
)
# ------------------------------------------------------------
# Bind DHS surveys
# ------------------------------------------------------------

df.DHS.SMDW <- rbind(
  hh_CotedIvoire_DHS,
  hh_Malawi_DHS,
  hh_Mozambique_DHS
)

# ------------------------------------------------------------
# Relabel DHS responses using MICS-compatible coding
# ------------------------------------------------------------

df.DHS.SMDW_Labeled <- relabelingDHSQuestionResponses(df.DHS.SMDW)

# Optional diagnostic check
checkDHSUnmappedValues(df.DHS.SMDW_Labeled)

# ------------------------------------------------------------
# Keep same core output structure as the MICS labelled data
# ------------------------------------------------------------

df.DHS.SMDW_Labeled <- df.DHS.SMDW_Labeled %>%
  select(
    HH1,
    HH2,
    WQ27,
    WS7,
    WS3,
    HH7_region,
    HH6,
    WS1,
    HH48,
    WS4,
    wqsweight,
    WS2,
    hhweight,
    WS8,
    country,
    HH5D,
    HH5M,
    HH5Y,
    PSU,
    stratum
  )

df.DHS.SMDW_Labeled <- df.DHS.SMDW_Labeled %>%
  rename(HH7_region = HH7_region)


# ------------------------------------------------------------
# Write output
# ------------------------------------------------------------

write.csv(
  df.DHS.SMDW_Labeled,
  here::here("data/processed/household_surveys/df.SMDW_wq_DHS.csv"),
  fileEncoding = "UTF-8",
  row.names = FALSE
)


# ============================================================
# DHS OTHER SURVEYS
# Extract all DHS household variables except WQ27
#
# Paste this directly below the DHS WQ27 code above.
#
# Requires helper functions:
#   build_sampled_dhs_country_lookup()
#   get_country_name_from_dhs_filename()
#   extractDHSOtherSurveyVariables()
#   extractDHSAreaLabels()
#   replaceDHS_HH7LabelsWithRegionNames()
#   relabelingDHSOtherQuestionResponses()
#   checkDHSOtherVariables()
#   checkDHSOtherUnmappedValues()
# ============================================================


# ------------------------------------------------------------
# Define DHS countries to include
# ------------------------------------------------------------

# These are DHS filename prefixes, taken from the first two letters
# of each DHS HR file name.
#
# Example:
#   AFHR71FL -> AF
#   CIHR81FL -> CI
#   MWHR81FL -> MW

sampled_iso2_codes <- c(
  "AF", "AL", "AM", "AO", "BD", "BF", "BJ", "BO", "BU",
  "CD", "CF", "CI", "CM", "CO", "DR", "EG", "ET", "GA",
  "GH", "GM", "GN", "GU", "GY", "HN", "HT", "IA", "ID",
  "JO", "KE", "KH", "KM", "KY", "LB", "LS", "MA", "MB",
  "MD", "ML", "MM", "MR", "MW", "MZ", "NG", "NI", "NM",
  "NP", "PE", "PH", "PK", "RW", "SL", "SN", "SZ", "TD",
  "TG", "TJ", "TL", "TZ", "UG", "UZ", "ZA", "ZM", "ZW"
)


# ------------------------------------------------------------
# Manually match DHS prefixes to country_name_key_WB
# ------------------------------------------------------------

# This table maps the DHS filename prefix to the country Code
# used in country_name_key_WB.
#
# country_name_key_WB must contain:
#   Code
#   GADM_NAME_0

dhs_prefix_country_key <- tibble::tribble(
  ~dhs_prefix, ~Code,
  "AF", "AFG",  # Afghanistan
  "AL", "ALB",  # Albania
  "AM", "ARM",  # Armenia
  "AO", "AGO",  # Angola
  "BD", "BGD",  # Bangladesh
  "BF", "BFA",  # Burkina Faso
  "BJ", "BEN",  # Benin
  "BO", "BOL",  # Bolivia
  "BU", "BDI",  # Burundi
  "CD", "COD",  # Democratic Republic of the Congo
  "CF", "CAF",  # Central African Republic
  "CI", "CIV",  # Côte d'Ivoire
  "CM", "CMR",  # Cameroon
  "CO", "COL",  # Colombia
  "DR", "DOM",  # Dominican Republic
  "EG", "EGY",  # Egypt
  "ET", "ETH",  # Ethiopia
  "GA", "GAB",  # Gabon
  "GH", "GHA",  # Ghana
  "GM", "GMB",  # Gambia
  "GN", "GIN",  # Guinea
  "GU", "GTM",  # Guatemala
  "GY", "GUY",  # Guyana
  "HN", "HND",  # Honduras
  "HT", "HTI",  # Haiti
  "IA", "IND",  # India
  "ID", "IDN",  # Indonesia
  "JO", "JOR",  # Jordan
  "KE", "KEN",  # Kenya
  "KH", "KHM",  # Cambodia
  "KM", "COM",  # Comoros
  "KY", "KGZ",  # Kyrgyz Republic
  "LB", "LBR",  # Liberia
  "LS", "LSO",  # Lesotho
  "MA", "MAR",  # Morocco
  "MB", "MDA",  # Moldova
  "MD", "MDG",  # Madagascar
  "ML", "MLI",  # Mali
  "MM", "MMR",  # Myanmar
  "MR", "MRT",  # Mauritania
  "MW", "MWI",  # Malawi
  "MZ", "MOZ",  # Mozambique
  "NG", "NGA",  # Nigeria
  "NI", "NIC",  # Nicaragua
  "NM", "NAM",  # Namibia
  "NP", "NPL",  # Nepal
  "PE", "PER",  # Peru
  "PH", "PHL",  # Philippines
  "PK", "PAK",  # Pakistan
  "RW", "RWA",  # Rwanda
  "SL", "SLE",  # Sierra Leone
  "SN", "SEN",  # Senegal
  "SZ", "SWZ",  # Eswatini / Swaziland
  "TD", "TCD",  # Chad
  "TG", "TGO",  # Togo
  "TJ", "TJK",  # Tajikistan
  "TL", "TLS",  # Timor-Leste
  "TZ", "TZA",  # Tanzania
  "UG", "UGA",  # Uganda
  "UZ", "UZB",  # Uzbekistan
  "ZA", "ZAF",  # South Africa
  "ZM", "ZMB",  # Zambia
  "ZW", "ZWE"   # Zimbabwe
)


# Manual fallback for countries missing from country_name_key_WB
manual_country_names <- tibble::tribble(
  ~dhs_prefix, ~country_manual,
  "GY", "Guyana"
)

dhs_country_lookup <- dhs_prefix_country_key %>%
  dplyr::filter(dhs_prefix %in% sampled_iso2_codes) %>%
  dplyr::left_join(
    country_name_key_WB %>%
      dplyr::mutate(Code = toupper(as.character(Code))) %>%
      dplyr::select(Code, GADM_NAME_0),
    by = "Code"
  ) %>%
  dplyr::transmute(
    dhs_prefix = dhs_prefix,
    country = GADM_NAME_0
  ) %>%
  dplyr::left_join(manual_country_names, by = "dhs_prefix") %>%
  dplyr::mutate(
    country = dplyr::coalesce(country, country_manual)
  ) %>%
  dplyr::select(-country_manual)

# Check that every DHS prefix matched to a country name
missing_country_names <- dhs_country_lookup %>%
  dplyr::filter(is.na(country))

if (nrow(missing_country_names) > 0) {
  print(missing_country_names)
  stop(
    "Some DHS prefixes did not match country_name_key_WB. ",
    "Check the Code values in country_name_key_WB."
  )
}

print(dhs_country_lookup)

# ------------------------------------------------------------
# Variables to read from each DHS_other file
# ------------------------------------------------------------

dhs_other_vars_to_read <- c(
  "HV000",
  "HV001",
  "HV002",
  "HV201B",
  "HV201A",
  "HV235",
  "SHDISTRICT",
  "HV024",
  "HV025",
  "HV201",
  "HV009",
  "HV204",
  "HV202",
  "HV005",
  "HV016",
  "HV006",
  "HV007",
  "HV021",
  "HV022",
  "HV023"
)

dhs_other_vars_to_read <- unique(c(
  toupper(dhs_other_vars_to_read),
  tolower(dhs_other_vars_to_read)
))


# ------------------------------------------------------------
# Read only needed variables from one DHS_other file
# ------------------------------------------------------------

read_dhs_other_minimal <- function(file_path) {
  
  haven::read_sav(
    file = file_path,
    user_na = TRUE,
    col_select = tidyselect::any_of(dhs_other_vars_to_read)
  )
}


# ------------------------------------------------------------
# List DHS_other files and match to country names
# ------------------------------------------------------------

dhs_other_files <- list.files(
  path        = PATH_TO_SURVEYS_DHS_other,
  pattern     = "\\.sav$",
  full.names  = TRUE,
  ignore.case = TRUE
)

mis_files <- list.files(
  path        = PATH_TO_SURVEYS_MIS,
  pattern     = "\\.sav$",
  full.names  = TRUE,
  ignore.case = TRUE
)

# Combine DHS and MIS files; where both exist for a country, keep MIS only
# (mirrors the logic in 01_compile_dhs_sanitation_data.R)
DHS_other_index_sampled <- dplyr::bind_rows(
  tibble::tibble(file_path = dhs_other_files, survey_type = "DHS"),
  tibble::tibble(file_path = mis_files,       survey_type = "MIS")
) %>%
  dplyr::mutate(
    file_name  = basename(file_path),
    survey_id  = toupper(tools::file_path_sans_ext(basename(file_path))),
    dhs_prefix = stringr::str_sub(survey_id, 1, 2)
  ) %>%
  dplyr::left_join(dhs_country_lookup, by = "dhs_prefix") %>%
  dplyr::filter(!is.na(country)) %>%
  dplyr::group_by(country) %>%
  dplyr::filter(
    dplyr::n_distinct(survey_type) == 1 | survey_type == "MIS"
  ) %>%
  dplyr::ungroup()

if (nrow(DHS_other_index_sampled) == 0) {
  stop(
    "No DHS_other/MIS files matched dhs_country_lookup. ",
    "Check DHS file prefixes and sampled_iso2_codes."
  )
}

message("DHS/MIS other files that will be processed:")
print(
  DHS_other_index_sampled %>%
    dplyr::select(file_name, survey_id, dhs_prefix, country, survey_type)
)


# ------------------------------------------------------------
# Process one DHS_other file at a time
# ------------------------------------------------------------

process_one_dhs_other_file <- function(file_path, survey_id, country_name) {
  
  message("Processing ", survey_id, " as ", country_name)
  
  dhs_raw <- read_dhs_other_minimal(file_path)
  
  # Select area variable candidates per country, matching the logic used in
  # 01_compile_dhs_sanitation_data.R so region boundaries are consistent.
  # - Gambia/Rwanda/Cambodia: HV024 first (province/district labels stored there)
  # - Nigeria: state then district
  # - Sierra Leone: SHDIST then SHDISTRICT
  # - Uganda: HV024 only (province level; SHDISTRICT gives 116 districts with
  #   no matching covariate boundaries)
  # - Default: SHDISTRICT then HV024
  area_candidates <- dplyr::case_when(
    country_name %in% c("Cambodia", "Gambia", "Rwanda") ~ list(c("HV024", "SHDISTRICT")),
    country_name == "Nigeria"                            ~ list(c("SHSTATE", "SHDISTRICT", "HV024")),
    country_name == "Sierra Leone"                       ~ list(c("SHDIST", "SHDISTRICT", "HV024")),
    country_name == "Uganda"                             ~ list(c("HV024")),
    TRUE                                                 ~ list(c("SHDISTRICT", "HV024"))
  ) %>% .[[1]]
  
  dhs_other <- extractDHSOtherSurveyVariables(
    dhs_raw,
    country_name = country_name,
    area_candidates = area_candidates
  )
  
  dhs_region_labels <- extractDHSAreaLabels(
    dhs_raw,
    candidates = area_candidates
  )
  
  dhs_other <- replaceDHS_HH7LabelsWithRegionNames(
    dhs_other,
    dhs_region_labels
  )
  
  dhs_other <- relabelingDHSOtherQuestionResponses(dhs_other)
  
  dhs_other <- dhs_other %>%
    dplyr::select(
      HH1,
      HH2,
      WS7,
      WS3,
      HH7_region,
      HH6,
      WS1,
      HH48,
      WS4,
      WS2,
      hhweight,
      WS8,
      country,
      HH5D,
      HH5M,
      HH5Y,
      PSU,
      stratum
    ) %>%
    dplyr::mutate(
      survey_id = survey_id
    )
  
  rm(dhs_raw)
  gc()
  
  return(dhs_other)
}


# ------------------------------------------------------------
# 7. Extract, relabel, and bind all sampled DHS_other surveys
# ------------------------------------------------------------

df.DHS.other_Labeled <- purrr::pmap_dfr(
  list(
    file_path = DHS_other_index_sampled$file_path,
    survey_id = DHS_other_index_sampled$survey_id,
    country_name = DHS_other_index_sampled$country
  ),
  process_one_dhs_other_file
)

# ------------------------------------------------------------
# Final checks
# ------------------------------------------------------------

checkDHSOtherVariables(df.DHS.other_Labeled)

checkDHSOtherUnmappedValues(df.DHS.other_Labeled)

message("Number of rows by country:")
print(
  df.DHS.other_Labeled %>%
    dplyr::count(country, sort = TRUE)
)

message("Number of rows by survey:")
print(
  df.DHS.other_Labeled %>%
    dplyr::count(survey_id, country, sort = TRUE)
)

# ------------------------------------------------------------
# Simple check: variables that are all NA by DHS survey/country
# ------------------------------------------------------------

vars_to_check <- c(
  "WS7",      # availability
  "WS3",      # source location
  "WS1",      # main drinking water source
  "WS4",      # collection time
  "WS2",      # other water source
  "HH6",      # urban/rural
  "HH48",     # household size
  "hhweight", # household weight
  "PSU",
  "stratum"
)

dhs_other_all_na_check <- df.DHS.other_Labeled %>%
  dplyr::group_by(country, survey_id) %>%
  dplyr::summarise(
    dplyr::across(
      dplyr::all_of(vars_to_check),
      ~ all(is.na(.x)),
      .names = "{.col}"
    ),
    .groups = "drop"
  )

countries_to_check_dhs_other <- dhs_other_all_na_check %>%
  tidyr::pivot_longer(
    cols = dplyr::all_of(vars_to_check),
    names_to = "variable",
    values_to = "all_values_are_NA"
  ) %>%
  dplyr::filter(all_values_are_NA) %>%
  dplyr::arrange(country, survey_id, variable)

print(countries_to_check_dhs_other)

# ------------------------------------------------------------
# Corrected check: do expected raw DHS columns exist?
# ------------------------------------------------------------

raw_var_lookup <- tibble::tribble(
  ~variable, ~raw_variable,
  "WS7", "HV201B",
  "WS7", "HV201A",
  "WS3", "HV235",
  "WS4", "HV204",
  "WS2", "HV202"
)

check_raw_column_names <- function(file_path, survey_id) {
  
  raw_names <- haven::read_sav(
    file = file_path,
    n_max = 0
  ) %>%
    names() %>%
    toupper()
  
  raw_var_lookup %>%
    dplyr::mutate(
      survey_id = survey_id,
      raw_variable_found = raw_variable %in% raw_names
    ) %>%
    dplyr::group_by(survey_id, variable) %>%
    dplyr::summarise(
      expected_raw_variables = paste(raw_variable, collapse = ", "),
      raw_variables_found = paste(raw_variable[raw_variable_found], collapse = ", "),
      raw_column_exists = any(raw_variable_found),
      .groups = "drop"
    )
}

raw_column_name_check <- purrr::map2_dfr(
  DHS_other_index_sampled$file_path,
  DHS_other_index_sampled$survey_id,
  check_raw_column_names
)

countries_to_check_with_raw_column_status <- countries_to_check_dhs_other %>%
  dplyr::left_join(
    raw_column_name_check,
    by = c("survey_id", "variable")
  ) %>%
  dplyr::mutate(
    issue_type = dplyr::case_when(
      raw_column_exists == FALSE ~ "Expected raw column name not found",
      raw_column_exists == TRUE  ~ "Raw column exists, but extracted values are all NA",
      TRUE ~ "Not checked"
    )
  ) %>%
  dplyr::arrange(country, survey_id, variable)

print(countries_to_check_with_raw_column_status, n=26)

# ------------------------------------------------------------
# Write output
# ------------------------------------------------------------

write.csv(
  df.DHS.other_Labeled,
  here::here("data/processed/household_surveys/df.SMDW_other_DHS.csv"),
  fileEncoding = "UTF-8",
  row.names = FALSE
)

# ------------------------------------------------------------
# Optional regional summary, parallel to your MICS summary
# ------------------------------------------------------------

df_region_summary_DHS <- df.DHS.SMDW_Labeled %>%
  mutate(household_id = paste(HH1, HH2, sep = "_")) %>%
  group_by(country, HH7_region) %>%
  summarise(
    households_in_region = n_distinct(household_id),
    clusters_in_region = n_distinct(HH1),
    households_with_WQ27 = n_distinct(household_id[!is.na(WQ27) & WQ27 != -99]),
    .groups = "drop"
  ) %>%
  rename(
    `Country name` = country,
    `HH7 region` = HH7_region,
    `number of households in the region (HH2)` = households_in_region,
    `number of clusters in the region (HH1)` = clusters_in_region,
    `number of households with data on water quality (WQ27)` = households_with_WQ27
  )

#write.csv(
 # df_region_summary_DHS,
  #"X/HH_surveys/HH_survey_data/regionalSummary_DHSquality.csv",
  #fileEncoding = "UTF-8",
  #row.names = FALSE
#)

# ------------------------------------------------------------
# Optional survey design for WQ27 estimates
# ------------------------------------------------------------

options(survey.lonely.psu = "adjust")
options(survey.adjust.domain.lonely = TRUE)

df_wq_se_DHS <- df.DHS.SMDW_Labeled %>%
  mutate(
    household_id = paste(HH1, HH2, sep = "_"),
    PSU_calc = interaction(country, PSU, drop = TRUE),
    stratum_calc = interaction(country, stratum, drop = TRUE),
    WQ27 = as.numeric(WQ27),
    wqsweight = as.numeric(wqsweight)
  )

design_wq_DHS <- svydesign(
  ids = ~PSU_calc,
  strata = ~stratum_calc,
  weights = ~wqsweight,
  data = df_wq_se_DHS,
  nest = TRUE
)

df_wq_estimates_DHS <- svyby(
  ~WQ27,
  ~country + HH7_region,
  design = subset(
    design_wq_DHS,
    !is.na(WQ27) &
      WQ27 != -99 &
      !is.na(wqsweight) &
      !is.na(PSU_calc) &
      !is.na(stratum_calc)
  ),
  FUN = svymean,
  vartype = c("se"),
  na.rm = TRUE,
  deff = TRUE
) %>%
  as.data.frame() %>%
  mutate(
    ci_lower = pmax(0, WQ27 - 1.96 * se),
    ci_upper = pmin(1, WQ27 + 1.96 * se),
    contamination_percent = 100 * WQ27,
    se_percent = 100 * se,
    ci_lower_percent = 100 * ci_lower,
    ci_upper_percent = 100 * ci_upper
  )

df_region_summary_DHS_SE <- df_wq_se_DHS %>%
  group_by(country, HH7_region) %>%
  summarise(
    households_in_region = n_distinct(household_id),
    clusters_in_region = n_distinct(HH1),
    households_with_WQ27 = n_distinct(household_id[!is.na(WQ27) & WQ27 != -99]),
    households_with_wqsweight = n_distinct(household_id[!is.na(wqsweight)]),
    households_with_PSU = n_distinct(household_id[!is.na(PSU)]),
    households_with_stratum = n_distinct(household_id[!is.na(stratum)]),
    households_used_in_SE = n_distinct(
      household_id[
        !is.na(WQ27) &
          WQ27 != -99 &
          !is.na(wqsweight) &
          !is.na(PSU) &
          !is.na(stratum)
      ]
    ),
    PSUs_used_in_SE = n_distinct(
      PSU[
        !is.na(WQ27) &
          WQ27 != -99 &
          !is.na(wqsweight) &
          !is.na(PSU) &
          !is.na(stratum)
      ]
    ),
    strata_used_in_SE = n_distinct(
      stratum[
        !is.na(WQ27) &
          WQ27 != -99 &
          !is.na(wqsweight) &
          !is.na(PSU) &
          !is.na(stratum)
      ]
    ),
    .groups = "drop"
  ) %>%
  left_join(df_wq_estimates_DHS, by = c("country", "HH7_region")) %>%
  rename(
    `Country name` = country,
    `HH7 region` = HH7_region,
    `number of households in the region (HH2)` = households_in_region,
    `number of clusters in the region (HH1)` = clusters_in_region,
    `number of households with data on water quality (WQ27)` = households_with_WQ27,
    `number of households with water quality weights (wqsweight)` = households_with_wqsweight,
    `number of households with PSU` = households_with_PSU,
    `number of households with stratum` = households_with_stratum,
    `number of households used in SE calculation` = households_used_in_SE,
    `number of PSUs used in SE calculation` = PSUs_used_in_SE,
    `number of strata used in SE calculation` = strata_used_in_SE,
    `weighted proportion contaminated (WQ27=1)` = WQ27,
    `standard error` = se,
    `95% CI lower` = ci_lower,
    `95% CI upper` = ci_upper,
    `weighted percent contaminated` = contamination_percent,
    `SE percentage points` = se_percent,
    `95% CI lower percent` = ci_lower_percent,
    `95% CI upper percent` = ci_upper_percent,
    `design effect` = DEff.WQ27
  )

#write.csv(
 # df_region_summary_DHS_SE,
  #"X/HH_surveys/HH_survey_data/regionalSummary_DHSquality_SE.csv",
  #fileEncoding = "UTF-8",
  #row.names = FALSE
#)





dhs <- MZHR81FL


# ---- 3. Extract variable names and variable labels ----
var_dictionary <- tibble(
  variable = names(dhs),
  variable_label = map_chr(dhs, ~ {
    lbl <- attr(.x, "label")
    if (is.null(lbl)) "" else as.character(lbl)
  }),
  class = map_chr(dhs, ~ paste(class(.x), collapse = ", ")),
  has_value_labels = map_lgl(dhs, ~ !is.null(attr(.x, "labels"))),
  n_value_labels = map_int(dhs, ~ {
    labs <- attr(.x, "labels")
    if (is.null(labs)) 0 else length(labs)
  })
)

# ---- 4. Extract value labels into long format ----
value_labels <- imap_dfr(dhs, function(x, varname) {
  labs <- attr(x, "labels")
  
  if (is.null(labs)) {
    return(tibble(
      variable = character(),
      value = character(),
      value_label = character()
    ))
  }
  
  tibble(
    variable = varname,
    value = as.character(unname(labs)),
    value_label = names(labs)
  )
})



# ---- 6. Write files you can upload/share ----
#write_csv(var_dictionary, "dhs_variable_dictionary.csv")
#write_csv(value_labels, "dhs_value_labels.csv")


