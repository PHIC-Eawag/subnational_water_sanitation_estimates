# title: "Functions for creating sanitation indicators"
#
# Sanitation variable coding in df_sanitation_MICS_v1.csv:
#   WS11  toilet type:  2 = improved, 1 = unimproved (not OD), 0 = open defecation
#   WS15  shared:       1 = shared,   0 = not shared,          -99 / NA = missing
#   hhweight  household weight
#   HH48      household size
#   HH7_region, country, PSU, stratum, HH5Y, HH5D, HH5M, HH6, HH1, HH2
#
# Outcome definitions:
#   Basic sanitation:  WS11 == 2 (improved) AND WS15 == 0 (not shared)
#   Open defecation:   WS11 == 0 (no facility / bush / field)
#
# Weight: hhweight (same as SMDW "other" subcomponents — no water quality weight)
#
# These functions follow the same structure as the SMDW indicator functions
# in create_indicators.R so that the same covariate-joining workflow applies.

# =============================================================================
# Helpers shared with SMDW workflow (duplicated here for self-containment)
# =============================================================================

renameDuplicateHH7RegionNamesFromDifferentCountries_sanitation <- function(df) {
  # Extends the SMDW version with any sanitation-specific duplicates.
  # Add further entries here as they are discovered.
  df$HH7_region[df$HH7_region == "Central"    & df$country == "Paraguay"] <- "Central Paraguay"
  df$HH7_region[df$HH7_region == "Central"    & df$country == "Ghana"]    <- "Central Ghana"
  df$HH7_region[df$HH7_region == "NORD OUEST" & df$country == "Tunisia"]  <- "NORD OUEST Tunisia"
  df$HH7_region[df$HH7_region == "NORD OUEST" & df$country == "Algeria"]  <- "NORD OUEST Algeria"
  return(df)
}

# =============================================================================
# Step 1 — Prepare raw sanitation data frame
# =============================================================================
# Selects columns needed for both outcomes, drops rows with missing WS11
# (true missing data), converts WS15 NA to 0 for households that have a
# facility (WS11 > 0) — these are households where the sharing question was
# skipped for a reason other than open defecation.
# Rows where WS11 == 0 (open defecation) legitimately have WS15 == NA.

prepareSanitationData <- function(df) {
  df %>%
    dplyr::mutate(
      WS11 = as.numeric(WS11),
      WS15 = as.numeric(WS15)
    ) %>%
    dplyr::filter(!is.na(WS11)) %>%              # drop true missing toilet type
    dplyr::mutate(
      # For non-OD households where WS15 is NA, treat as unknown sharing
      # (not basic sanitation) — conservative approach consistent with JMP
      WS15_clean = dplyr::case_when(
        WS11 == 0  ~ NA_real_,   # OD: sharing not applicable
        is.na(WS15) ~ NA_real_,  # truly missing: excluded from basic sanitation numerator
        TRUE ~ WS15
      )
    )
}

# =============================================================================
# Step 2a — Basic sanitation data frame
# =============================================================================
# Drops rows where WS11 or hhweight are NA.
# Rows where WS15 is NA contribute to the denominator as "not basic sanitation".

createDataFrameWithBasicSanitationIndicator <- function(df) {
  df %>%
    prepareSanitationData() %>%
    harmonise_household_country_region_names_for_modelling() %>%
    renameDuplicateHH7RegionNamesFromDifferentCountries_sanitation() %>%
    dplyr::mutate(
      basic_sanitation = dplyr::case_when(
        WS11 == 2 & WS15_clean == 0 ~ 1,   # improved AND not shared
        is.na(WS11)                 ~ NA_real_,
        TRUE                        ~ 0
      )
    ) %>%
    dplyr::select(
      country, HH7_region, HH48, hhweight,
      WS11, WS15, basic_sanitation, HH5Y
    ) %>%
    tidyr::drop_na(country, HH7_region, HH48, hhweight, WS11, HH5Y)
}

# =============================================================================
# Step 2b — Open defecation data frame
# =============================================================================
# WS15 is not needed for open defecation. Drop rows where WS11 is NA.

createDataFrameWithOpenDefecationIndicator <- function(df) {
  df %>%
    prepareSanitationData() %>%
    harmonise_household_country_region_names_for_modelling() %>%
    renameDuplicateHH7RegionNamesFromDifferentCountries_sanitation() %>%
    dplyr::mutate(
      open_defecation = dplyr::if_else(WS11 == 0, 1, 0)
    ) %>%
    dplyr::select(
      country, HH7_region, HH48, hhweight,
      WS11, open_defecation, HH5Y
    ) %>%
    tidyr::drop_na(country, HH7_region, HH48, hhweight, WS11, HH5Y)
}

# =============================================================================
# Step 3a — Regional basic sanitation proportion
# =============================================================================
# Follows the same structure as createIndicatorForRegionalWaterSourceType().

createIndicatorForRegionalBasicSanitation <- function(df) {
  df %>%
    dplyr::mutate(
      HH48_hhweight = as.numeric(HH48) * as.numeric(hhweight)
    ) %>%
    dplyr::group_by(country, HH7_region) %>%
    dplyr::summarise(
      HouseholdsInRegion.Freq.x    = dplyr::n(),
      HouseholdMembersInRegion     = sum(HH48_hhweight, na.rm = TRUE),
      HHmembersBasicSanitation     = sum(
        HH48_hhweight * dplyr::if_else(basic_sanitation == 1, 1, 0, missing = 0),
        na.rm = TRUE
      ),
      BasicSanitationAtRegionalLevel = dplyr::if_else(
        HouseholdMembersInRegion > 0,
        HHmembersBasicSanitation / HouseholdMembersInRegion,
        NA_real_
      ),
      pct.BasicSanitation = mean(basic_sanitation == 1, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    dplyr::mutate(
      BasicSanitationAtRegionalLevel = dplyr::coalesce(
        BasicSanitationAtRegionalLevel, 0
      )
    ) %>%
    dplyr::rename(country.x = country) %>%
    dplyr::select(
      BasicSanitationAtRegionalLevel,
      HH7_region,
      country.x,
      HouseholdsInRegion.Freq.x,
      pct.BasicSanitation
    )
}

# =============================================================================
# Step 3b — Regional open defecation proportion
# =============================================================================

createIndicatorForRegionalOpenDefecation <- function(df) {
  df %>%
    dplyr::mutate(
      HH48_hhweight = as.numeric(HH48) * as.numeric(hhweight)
    ) %>%
    dplyr::group_by(country, HH7_region) %>%
    dplyr::summarise(
      HouseholdsInRegion.Freq.x = dplyr::n(),
      HouseholdMembersInRegion  = sum(HH48_hhweight, na.rm = TRUE),
      HHmembersOD               = sum(
        HH48_hhweight * open_defecation,
        na.rm = TRUE
      ),
      OpenDefecationAtRegionalLevel = dplyr::if_else(
        HouseholdMembersInRegion > 0,
        HHmembersOD / HouseholdMembersInRegion,
        NA_real_
      ),
      pct.OpenDefecation = mean(open_defecation == 1, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    dplyr::mutate(
      OpenDefecationAtRegionalLevel = dplyr::coalesce(
        OpenDefecationAtRegionalLevel, 0
      )
    ) %>%
    dplyr::rename(country.x = country) %>%
    dplyr::select(
      OpenDefecationAtRegionalLevel,
      HH7_region,
      country.x,
      HouseholdsInRegion.Freq.x,
      pct.OpenDefecation
    )
}

# =============================================================================
# Step 4 — Workflow wrappers (mirror make_*_regional_outcome in create_indicators.R)
# =============================================================================

make_basic_sanitation_regional_outcome <- function(df_hh_sanitation) {
  # Basic sanitation outcome.
  # Definition: improved facility (WS11 == 2) that is not shared (WS15 == 0).
  # Data source: MICS sanitation data (+ DHS when available).

  year_lookup <- make_year_lookup_from_raw_household_data(df_hh_sanitation)

  basic_san_original <- df_hh_sanitation %>%
    createDataFrameWithBasicSanitationIndicator() %>%
    createIndicatorForRegionalBasicSanitation()

  standardise_regional_outcome_table(
    outcome_df        = basic_san_original,
    outcome_type      = "basic_sanitation",
    outcome_value_col = "BasicSanitationAtRegionalLevel",
    year_lookup       = year_lookup
  )
}

make_open_defecation_regional_outcome <- function(df_hh_sanitation) {
  # Open defecation outcome.
  # Definition: no facility / bush / field (WS11 == 0).
  # Data source: MICS sanitation data (+ DHS when available).

  year_lookup <- make_year_lookup_from_raw_household_data(df_hh_sanitation)

  od_original <- df_hh_sanitation %>%
    createDataFrameWithOpenDefecationIndicator() %>%
    createIndicatorForRegionalOpenDefecation()

  standardise_regional_outcome_table(
    outcome_df        = od_original,
    outcome_type      = "open_defecation",
    outcome_value_col = "OpenDefecationAtRegionalLevel",
    year_lookup       = year_lookup
  )
}
