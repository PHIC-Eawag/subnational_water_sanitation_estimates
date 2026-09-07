# title: "Functions for extracting and relabelling DHS sanitation variables"
#
# Sanitation variable mapping:
#   HV205  → WS11   toilet type (same numeric codes as MICS6 / JMP)
#   HV225  → WS15   shared facility
#   HV005  → hhweight (scaled / 1000000)
#   HV009  → HH48   household members
#   HV024 / SHDISTRICT → HH7  region code
#   HV025  → HH6   urban/rural
#   HV001  → HH1,  HV002 → HH2
#   HV016/HV006/HV007 → HH5D/HH5M/HH5Y
#   HV021 / HV001 → PSU,  HV022/HV023 → stratum
#
# Output column structure matches df_sanitation_MICS_v1.csv so the two
# datasets can be bound directly in 00_prepare_sanitation_training_data.R.
#
# Helper functions (standardise_dhs_names, get_var, get_numeric_var,
# get_character_var, scale_dhs_weight, extractDHSAreaLabels,
# replaceDHS_HH7LabelsWithRegionNames) are defined in
# extract_label_dhs_variables.R and must be sourced before this file.

# =============================================================================
# Extraction
# =============================================================================

extractDHSSanitationSurveyVariables <- function(
    hh_Survey,
    country_name    = NULL,
    area_candidates = c("SHDISTRICT", "HV024")
) {
  hh_Survey <- standardise_dhs_names(hh_Survey)

  if (!is.null(country_name)) {
    country_vec <- rep(country_name, nrow(hh_Survey))
  } else if ("COUNTRY" %in% names(hh_Survey)) {
    country_vec <- as.character(hh_Survey$COUNTRY)
  } else {
    country_vec <- get_character_var(hh_Survey, "HV000")
  }

  out <- tibble::tibble(
    HH1     = get_numeric_var(hh_Survey, "HV001"),
    HH2     = get_numeric_var(hh_Survey, "HV002"),

    # Toilet type — HV205 uses the same JMP numeric codes as MICS6 WS11.
    WS11    = get_numeric_var(hh_Survey, "HV205"),
    # Preserve the raw HV205 code for QC (mirrors WS11_raw in the MICS
    # pipeline). WS11 above is overwritten with the 0/1/2 classification by
    # setDHSWS11ToiletTypeLabels(); WS11_raw keeps the original code so
    # labelling can be audited (see ws11_label_check.R / ws11_raw_value_labels.R).
    WS11_raw = get_numeric_var(hh_Survey, "HV205"),

    # Shared facility — HV225: 0 = no (not shared), 1 = yes (shared).
    WS15    = get_numeric_var(hh_Survey, "HV225"),

    # Region code (label replacement done separately).
    HH7     = get_numeric_var(hh_Survey, area_candidates),

    # Urban/rural.
    HH6     = get_numeric_var(hh_Survey, "HV025"),

    # Household size.
    HH48    = get_numeric_var(hh_Survey, "HV009"),

    # Household weight.
    hhweight = scale_dhs_weight(get_numeric_var(hh_Survey, "HV005")),

    country = country_vec,

    # Interview date.
    HH5D    = get_numeric_var(hh_Survey, "HV016"),
    HH5M    = get_numeric_var(hh_Survey, "HV006"),
    HH5Y    = get_numeric_var(hh_Survey, "HV007"),

    # Survey design.
    PSU     = get_numeric_var(hh_Survey, c("HV021", "HV001")),
    stratum = get_numeric_var(hh_Survey, c("HV022", "HV023"))
  )

  # Keep one row per household (PR files repeat rows per person).
  out <- out %>% dplyr::distinct(country, HH1, HH2, .keep_all = TRUE)

  return(out)
}

# =============================================================================
# Relabeling
# =============================================================================

# WS11 — toilet type
# DHS HV205 numeric scheme:
#   Improved (2):     11, 12, 13, 15, 16, 21, 22, 41, 51, 52, 54
#   Unimproved (1):   14, 23, 42, 43, 53, 96, 99
#   Open defecation:  31
#
# Country/round-specific codes verified against raw value labels (see
# scripts/01_data_preparation/ws11_raw_value_labels.R):
#   16 = flush, bio-digester (Biofil), Ghana        -> improved (flush facility)
#   51 = no flush to piped sewer system (twin of 11) -> improved
#   52 = no flush to septic tank        (twin of 12) -> improved
#   53 = no flush to somewhere else     (twin of 14) -> unimproved
#   54 = no flush, don't know where     (twin of 15) -> improved
# The "no flush" 50-series (Mozambique and other newer DHS) mirror their flush
# twins 11-15. Previously these fell through to NA and were silently dropped.

setDHSWS11ToiletTypeLabels <- function(df) {

  improved_codes   <- c(11, 12, 13, 15, 16, 21, 22, 41, 51, 52, 54)
  unimproved_codes <- c(14, 23, 42, 43, 53, 96, 99)
  od_codes         <- c(31)

  df$WS11 <- dplyr::case_when(
    df$WS11 %in% improved_codes   ~ 2,
    df$WS11 %in% unimproved_codes  ~ 1,
    df$WS11 %in% od_codes          ~ 0,
    is.na(df$WS11)                 ~ NA_real_,
    TRUE                           ~ NA_real_   # any unmapped code → NA for inspection
  )

  return(df)
}

# =============================================================================
# applyDHSSurveySpecificWS11Overrides()
# Some HV205 codes mean different things in different DHS surveys, so the
# generic setDHSWS11ToiletTypeLabels() classification is wrong for them (or
# drops them to NA). This applies documented, survey-specific corrections keyed
# on (country, raw HV205 code). Requires the preserved WS11_raw column and must
# run AFTER setDHSWS11ToiletTypeLabels().
#
# Verified against raw HV205 value labels (see
# scripts/01_data_preparation/ws11_raw_value_labels.R):
#   India        44 = Dry toilet (service / dry latrine)        -> unimproved
#   Malawi       24 = Pit latrine with log/rock                 -> improved
#                     (log/earth slabs count as a slab in Malawi; 2018 census:
#                      83% of pit-latrine slabs are earth/sand and counted improved)
#   Tanzania     24 = Pit latrine with slab (not washable)      -> improved
#   Indonesia    17 = Flush toilet: shared / public (facility)  -> improved
#   Egypt        17 = Flush to pipe connected to canal          -> unimproved
#   Egypt        18 = Flush to pipe connected to ground water   -> unimproved
#   South Africa 44 = Chemical toilet                           -> improved
#   Guatemala    13 = Flush to somewhere else                   -> unimproved
#                     (generic scheme treats 13 as flush-to-pit = improved)
#   Nepal        45 = Biogas attached toilet                    -> improved
#   Nepal        44 = Composting toilet without slab            -> improved
# Codes 17 / 24 / 44 mean different things in different surveys, so they cannot
# be added to the global lists in setDHSWS11ToiletTypeLabels() — they must be
# handled per survey here. (These codes previously fell through to NA and were
# silently dropped.)
# =============================================================================

applyDHSSurveySpecificWS11Overrides <- function(df) {
  if (!"WS11_raw" %in% names(df)) {
    stop("applyDHSSurveySpecificWS11Overrides(): WS11_raw column is required ",
         "(added to the DHS extraction in extract_label_dhs_sanitation_variables.R).")
  }

  raw <- suppressWarnings(as.numeric(df$WS11_raw))

  df$WS11 <- dplyr::case_when(
    df$country == "India"        & raw == 44 ~ 1,  # dry toilet -> unimproved
    df$country == "Malawi"       & raw == 24 ~ 2,  # pit latrine w/ log/rock -> improved (log/earth slab counts as a slab in Malawi)
    df$country == "Tanzania"     & raw == 24 ~ 2,  # pit latrine w/ slab -> improved
    df$country == "Indonesia"    & raw == 17 ~ 2,  # flush shared/public -> improved
    df$country == "Egypt"        & raw == 17 ~ 1,  # flush to canal -> unimproved
    df$country == "Egypt"        & raw == 18 ~ 1,  # flush to ground water -> unimproved
    df$country == "South Africa" & raw == 44 ~ 2,  # chemical toilet -> improved
    df$country == "Nepal"        & raw == 45 ~ 2,  # biogas attached toilet -> improved
    df$country == "Nepal"        & raw == 44 ~ 2,  # composting toilet w/o slab -> improved
    df$country == "Guatemala"    & raw == 13 ~ 1,  # flush to somewhere else -> unimproved
    TRUE                                     ~ df$WS11
  )

  return(df)
}

# WS15 — shared facility
# DHS HV225: 0 = not shared, 1 = shared, 8/9 = DK/missing.
# Output matches MICS coding: 1 = shared, 0 = not shared, -99 = missing.

setDHSWS15SharedFacilityLabels <- function(df) {

  df$WS15 <- dplyr::case_when(
    df$WS15 == 0             ~  0,   # not shared
    df$WS15 == 1             ~  1,   # shared
    df$WS15 %in% c(8, 9, 98, 99) ~ -99,
    is.na(df$WS15)           ~ NA_real_,
    TRUE                     ~ NA_real_
  )

  return(df)
}

# HH6 — urban/rural (same as SMDW)
setDHSAreaLabels_sanitation <- function(df) {
  df$HH6 <- dplyr::case_when(
    df$HH6 %in% c(1, 2)         ~ df$HH6,
    df$HH6 %in% c(8, 9, 98, 99) ~ -99,
    is.na(df$HH6)               ~ NA_real_,
    TRUE                        ~ df$HH6
  )
  return(df)
}

# Wrapper — apply all sanitation relabeling steps in sequence.
relabelingDHSSanitationQuestionResponses <- function(df) {
  df <- setDHSWS11ToiletTypeLabels(df)
  df <- applyDHSSurveySpecificWS11Overrides(df)  # per-survey code corrections
  df <- setDHSWS15SharedFacilityLabels(df)
  df <- setDHSAreaLabels_sanitation(df)
  return(df)
}

# =============================================================================
# Diagnostics
# =============================================================================

checkDHSSanitationVariables <- function(df) {

  variables_to_check <- c(
    "HH1", "HH2", "WS11", "WS15", "HH7_region", "HH6",
    "HH48", "hhweight", "country",
    "HH5D", "HH5M", "HH5Y", "PSU", "stratum"
  )

  missing_variables <- setdiff(variables_to_check, names(df))

  if (length(missing_variables) > 0) {
    message("Missing variables: ", paste(missing_variables, collapse = ", "))
  } else {
    message("All expected DHS sanitation variables are present.")
  }

  return(invisible(missing_variables))
}

checkDHSSanitationUnmappedValues <- function(df) {

  message("Unique WS11 values after relabelling (expect 0/1/2/NA only):")
  print(sort(unique(df$WS11)))

  message("Unique WS15 values after relabelling (expect -99/0/1/NA only):")
  print(sort(unique(df$WS15)))

  message("Unique HH6 values:")
  print(sort(unique(df$HH6)))

  # Flag any WS11 values that weren't mapped (should be empty)
  unmapped_ws11 <- df %>%
    dplyr::filter(is.na(WS11)) %>%
    dplyr::count(country, name = "n_unmapped_WS11") %>%
    dplyr::filter(n_unmapped_WS11 > 0)

  if (nrow(unmapped_ws11) > 0) {
    message("Countries with unmapped WS11 values:")
    print(unmapped_ws11)
  }

  return(invisible(NULL))
}
