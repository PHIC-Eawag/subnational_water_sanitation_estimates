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
# DHS HV205 uses the same JMP numeric scheme as MICS6:
#   Improved (2):     11, 12, 13, 15, 21, 22, 41
#   Unimproved (1):   14, 23, 42, 43, 96, 99
#   Open defecation:  31
# Older DHS surveys may use non-standard codes (see MICS equivalent table).

setDHSWS11ToiletTypeLabels <- function(df) {

  improved_codes   <- c(11, 12, 13, 15, 21, 22, 41)
  unimproved_codes <- c(14, 23, 42, 43, 96, 99)
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
