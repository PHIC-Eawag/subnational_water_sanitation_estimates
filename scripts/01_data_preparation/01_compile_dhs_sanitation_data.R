# ============================================================
# Compile DHS household data for sanitation outcomes
# ============================================================
#
# Extracts toilet type (HV205 → WS11) and shared facility (HV225 → WS15)
# from DHS HR files and produces a data frame with the same column
# structure as df_sanitation_MICS_v1.csv so the two can be bound
# directly in 00_prepare_sanitation_training_data.R.
#
# Surveys:  Same DHS HR files as used for SMDW other subcomponents.
# Path:     PATH_TO_SURVEYS_DHS_other
# Countries: Same sampled_iso2_codes as SMDW
#
# Output:
#   df_sanitation_DHS.csv

library(tidyverse)
library(haven)
library(here)

source("~/Documents/GitHub/mapping_sanitation_access_LMICs/functions/extract_label_dhs_variables.R")
source("~/Documents/GitHub/mapping_sanitation_access_LMICs/functions/extract_label_dhs_sanitation_variables.R")

# ============================================================
# Paths
# ============================================================
PATH_TO_SURVEYS_DHS_other <- "~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/HH_DHS_other/"

country_name_key_WB <- readr::read_csv(
  here::here("data/country_name_key_WB.csv"),
  show_col_types = FALSE
)

# ============================================================
# Country lookup — same as SMDW other
# ============================================================
sampled_iso2_codes <- c(
  "AF", "AL", "AM", "AO", "BD", "BF", "BJ", "BO", "BU",
  "CD", "CF", "CI", "CM", "CO", "DR", "EG", "ET", "GA",
  "GH", "GM", "GN", "GU", "GY", "HN", "HT", "IA", "ID",
  "JO", "KE", "KH", "KM", "KY", "LB", "LS", "MA", "MB",
  "MD", "ML", "MM", "MR", "MW", "MZ", "NG", "NI", "NM",
  "NP", "PE", "PH", "PK", "RW", "SL", "SN", "SZ", "TD",
  "TG", "TJ", "TL", "TZ", "UG", "UZ", "ZA", "ZM", "ZW"
)

dhs_prefix_country_key <- tibble::tribble(
  ~dhs_prefix, ~Code,
  "AF", "AFG", "AL", "ALB", "AM", "ARM", "AO", "AGO", "BD", "BGD",
  "BF", "BFA", "BJ", "BEN", "BO", "BOL", "BU", "BDI", "CD", "COD",
  "CF", "CAF", "CI", "CIV", "CM", "CMR", "CO", "COL", "DR", "DOM",
  "EG", "EGY", "ET", "ETH", "GA", "GAB", "GH", "GHA", "GM", "GMB",
  "GN", "GIN", "GU", "GTM", "GY", "GUY", "HN", "HND", "HT", "HTI",
  "IA", "IND", "ID", "IDN", "JO", "JOR", "KE", "KEN", "KH", "KHM",
  "KM", "COM", "KY", "KGZ", "LB", "LBR", "LS", "LSO", "MA", "MAR",
  "MB", "MDA", "MD", "MDG", "ML", "MLI", "MM", "MMR", "MR", "MRT",
  "MW", "MWI", "MZ", "MOZ", "NG", "NGA", "NI", "NIC", "NM", "NAM",
  "NP", "NPL", "PE", "PER", "PH", "PHL", "PK", "PAK", "RW", "RWA",
  "SL", "SLE", "SN", "SEN", "SZ", "SWZ", "TD", "TCD", "TG", "TGO",
  "TJ", "TJK", "TL", "TLS", "TZ", "TZA", "UG", "UGA", "UZ", "UZB",
  "ZA", "ZAF", "ZM", "ZMB", "ZW", "ZWE"
)

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
    country    = GADM_NAME_0
  ) %>%
  dplyr::left_join(manual_country_names, by = "dhs_prefix") %>%
  dplyr::mutate(country = dplyr::coalesce(country, country_manual)) %>%
  dplyr::select(-country_manual)

missing_country_names <- dhs_country_lookup %>% dplyr::filter(is.na(country))
if (nrow(missing_country_names) > 0) {
  print(missing_country_names)
  stop("Some DHS prefixes did not match country_name_key_WB.")
}

# ============================================================
# Variables to read from each DHS file
# (minimal set — only what is needed for sanitation)
# ============================================================
dhs_sanitation_vars_to_read <- c(
  "HV000",   # country/phase code
  "HV001",   # cluster (→ HH1 / PSU)
  "HV002",   # household number (→ HH2)
  "HV205",   # toilet type (→ WS11)
  "HV225",   # shared toilet (→ WS15)
  "HV024",   # region (→ HH7)
  "SHDISTRICT", # district — preferred region variable in some surveys
  "HV025",   # urban/rural (→ HH6)
  "HV009",   # household members (→ HH48)
  "HV005",   # household weight (→ hhweight)
  "HV016",   # day of interview (→ HH5D)
  "HV006",   # month of interview (→ HH5M)
  "HV007",   # year of interview (→ HH5Y)
  "HV021",   # primary sampling unit (→ PSU)
  "HV022",   # sample stratum (→ stratum)
  "HV023"    # stratum (alternative)
)

dhs_sanitation_vars_to_read <- unique(c(
  toupper(dhs_sanitation_vars_to_read),
  tolower(dhs_sanitation_vars_to_read)
))

# ============================================================
# Read minimal columns from one DHS file
# ============================================================
read_dhs_sanitation_minimal <- function(file_path) {
  haven::read_sav(
    file       = file_path,
    user_na    = TRUE,
    col_select = tidyselect::any_of(dhs_sanitation_vars_to_read)
  )
}

# ============================================================
# List DHS files and match to country names
# ============================================================
dhs_files <- list.files(
  path       = PATH_TO_SURVEYS_DHS_other,
  pattern    = "\\.sav$",
  full.names  = TRUE,
  ignore.case = TRUE
)

DHS_sanitation_index <- tibble::tibble(
  file_path  = dhs_files,
  file_name  = basename(dhs_files),
  survey_id  = toupper(tools::file_path_sans_ext(basename(dhs_files))),
  dhs_prefix = stringr::str_sub(survey_id, 1, 2)
) %>%
  dplyr::left_join(dhs_country_lookup, by = "dhs_prefix") %>%
  dplyr::filter(!is.na(country))

if (nrow(DHS_sanitation_index) == 0) {
  stop("No DHS files matched dhs_country_lookup. Check DHS file prefixes and sampled_iso2_codes.")
}

message("DHS sanitation files that will be processed:")
print(DHS_sanitation_index %>% dplyr::select(file_name, survey_id, dhs_prefix, country))

# ============================================================
# Process one DHS file
# ============================================================
process_one_dhs_sanitation_file <- function(file_path, survey_id, country_name) {

  message("Processing ", survey_id, " (", country_name, ")")

  dhs_raw <- read_dhs_sanitation_minimal(file_path)

  area_candidates <- if (country_name == "Cambodia") {
    c("HV024", "SHDISTRICT")
  } else {
    c("SHDISTRICT", "HV024")
  }

  # Extract
  dhs_san <- extractDHSSanitationSurveyVariables(
    hh_Survey    = dhs_raw,
    country_name = country_name,
    area_candidates = area_candidates
  )

  # Region labels
  dhs_region_labels <- extractDHSAreaLabels(
    dhs_raw,
    candidates = area_candidates
  )

  dhs_san <- replaceDHS_HH7LabelsWithRegionNames(dhs_san, dhs_region_labels)

  # Relabel WS11, WS15, HH6
  dhs_san <- relabelingDHSSanitationQuestionResponses(dhs_san)

  # Standardise output columns (same as MICS sanitation output)
  dhs_san <- dhs_san %>%
    dplyr::select(
      HH1, HH2,
      WS11, WS15,
      HH7_region,
      HH6,
      HH48,
      hhweight,
      country,
      HH5D, HH5M, HH5Y,
      PSU, stratum
    ) %>%
    dplyr::mutate(survey_id = survey_id)

  rm(dhs_raw)
  gc()

  return(dhs_san)
}

# ============================================================
# Process all DHS sanitation files
# ============================================================
df.DHS.sanitation_Labeled <- purrr::pmap_dfr(
  list(
    file_path    = DHS_sanitation_index$file_path,
    survey_id    = DHS_sanitation_index$survey_id,
    country_name = DHS_sanitation_index$country
  ),
  process_one_dhs_sanitation_file
)

# ============================================================
# Diagnostics
# ============================================================
checkDHSSanitationVariables(df.DHS.sanitation_Labeled)
checkDHSSanitationUnmappedValues(df.DHS.sanitation_Labeled)

message("Rows by country:")
print(df.DHS.sanitation_Labeled %>% dplyr::count(country, sort = TRUE))

message("Rows by survey:")
print(df.DHS.sanitation_Labeled %>% dplyr::count(survey_id, country, sort = TRUE))

# Check for surveys where WS11 or WS15 are entirely NA
all_na_check <- df.DHS.sanitation_Labeled %>%
  dplyr::group_by(country, survey_id) %>%
  dplyr::summarise(
    WS11_all_NA = all(is.na(WS11)),
    WS15_all_NA = all(is.na(WS15)),
    .groups = "drop"
  ) %>%
  dplyr::filter(WS11_all_NA | WS15_all_NA)

if (nrow(all_na_check) > 0) {
  message("Surveys with all-NA WS11 or WS15 — check HV205/HV225 variable names:")
  print(all_na_check)
}

# ============================================================
# Write output
# ============================================================
readr::write_csv(
  df.DHS.sanitation_Labeled,
  "~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/df_sanitation_DHS.csv"
)
