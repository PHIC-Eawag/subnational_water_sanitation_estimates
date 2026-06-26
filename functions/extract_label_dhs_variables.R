# title: "Functions for extracting and relabelling DHS household variables"


standardise_dhs_names <- function(df) {
  names(df) <- toupper(names(df))
  return(df)
}

get_var <- function(df, candidates) {
  candidates <- toupper(candidates)
  hit <- candidates[candidates %in% names(df)]
  
  if (length(hit) == 0) {
    return(rep(NA, nrow(df)))
  }
  
  return(df[[hit[1]]])
}

get_numeric_var <- function(df, candidates) {
  x <- get_var(df, candidates)
  
  if (inherits(x, "haven_labelled") || inherits(x, "labelled")) {
    x <- haven::zap_labels(x)
  }
  
  if (is.factor(x)) {
    x <- as.character(x)
  }
  
  suppressWarnings(as.numeric(x))
}

get_character_var <- function(df, candidates) {
  x <- get_var(df, candidates)
  
  if (all(is.na(x))) {
    return(rep(NA_character_, nrow(df)))
  }
  
  if (inherits(x, "haven_labelled") || inherits(x, "labelled")) {
    x <- haven::zap_labels(x)
  }
  
  as.character(x)
}

extractDHSVariableLabelsfromHH7 <- function(dhs_raw) {
  
  dhs_raw <- standardise_dhs_names(dhs_raw)
  
  if (!"HV024" %in% names(dhs_raw)) {
    stop("HV024 not found in DHS file.")
  }
  
  labs <- attr(dhs_raw$HV024, "labels")
  
  if (is.null(labs)) {
    warning("No value labels found for HV024. Returning numeric codes only.")
    
    return(
      tibble(
        id = as.character(sort(unique(haven::zap_labels(dhs_raw$HV024)))),
        HH7_region = as.character(sort(unique(haven::zap_labels(dhs_raw$HV024))))
      )
    )
  }
  
  tibble(
    id = as.character(unname(labs)),
    HH7_region = names(labs)
  ) %>%
    distinct() %>%
    filter(!is.na(id), !is.na(HH7_region))
}

replaceDHS_HH7LabelsWithRegionNames <- function(df, df_regionNames) {
  
  df_regionNames <- df_regionNames %>%
    mutate(id = as.character(id))
  
  df <- df %>%
    mutate(HH7 = as.character(HH7)) %>%
    left_join(df_regionNames, by = c("HH7" = "id")) %>%
    select(-HH7)
  
  return(df)
}

scale_dhs_weight <- function(x) {
  x <- suppressWarnings(as.numeric(x))
  x / 1000000
}


extractDHSAreaLabels <- function(dhs_raw, candidates = c("SHDISTRICT", "HV024")) {
  
  dhs_raw <- standardise_dhs_names(dhs_raw)
  candidates <- toupper(candidates)
  
  varname <- NA
  for (cand in candidates) {
    if (cand %in% names(dhs_raw) && !is.null(attr(dhs_raw[[cand]], "labels"))) {
      varname <- cand
      break
    }
  }
  if (is.na(varname)) {
    varname <- candidates[candidates %in% names(dhs_raw)][1]
  }
  
  if (is.na(varname)) stop("No area variable found.")
  
  x <- dhs_raw[[varname]]
  labs <- attr(x, "labels")
  
  if (is.null(labs)) {
    values <- sort(unique(haven::zap_labels(x)))
    
    tibble(
      id = as.character(values),
      HH7_region = as.character(values)
    )
  } else {
    tibble(
      id = as.character(unname(labs)),
      HH7_region = names(labs)
    ) %>%
      distinct() %>%
      filter(!is.na(id), !is.na(HH7_region))
  }
}

# Extract DHS variables into MICS-style names


extractDHSStandardSurveyVariables <- function(hh_Survey, country_name = NULL) {
  
  hh_Survey <- standardise_dhs_names(hh_Survey)
  
  if (!is.null(country_name)) {
    country_vec <- rep(country_name, nrow(hh_Survey))
  } else if ("COUNTRY" %in% names(hh_Survey)) {
    country_vec <- as.character(hh_Survey$COUNTRY)
  } else {
    country_vec <- get_character_var(hh_Survey, c("HV000"))
  }
  
  out <- tibble(
    HH1 = get_numeric_var(hh_Survey, c("HV001")),
    HH2 = get_numeric_var(hh_Survey, c("HV002")),
    
    # MICS WQ27 equivalent: source water test, 100 ml.
    WQ27 = get_numeric_var(hh_Survey, c("SH3227","SHWA26","SWA26N")),
    
    # DHS 8: HV201B = water for drinking not sufficient in last month.
    # DHS 7 fallback: HV201A = water not available for at least one full day in past two weeks.
    WS7 = get_numeric_var(hh_Survey, c("HV201B", "HV201A")),
    
    # Location of water source.
    WS3 = get_numeric_var(hh_Survey, c("HV235")),
    
    # Region code and region label.
    # Region or district code.
    HH7 = get_numeric_var(hh_Survey, c("SHDISTRICT", "HV024")),
    
    # Urban/rural.
    HH6 = get_numeric_var(hh_Survey, c("HV025")),
    
    # Main drinking water source.
    WS1 = get_numeric_var(hh_Survey, c("HV201")),
    
    # Number of household members.
    HH48 = get_numeric_var(hh_Survey, c("HV009")),
    
    # Time to collect water.
    WS4 = get_numeric_var(hh_Survey, c("HV204")),
    
    # No separate WQ weight found in your DHS dictionary.
    # Use household weight unless DHS documentation gives a specific WQ weight.
    wqsweight = scale_dhs_weight(
      get_numeric_var(
        hh_Survey,
        c("SHWQWT", "SHWQWGT", "SH322WT", "WQWEIGHT", "WQWGT", "SHWGT", "HV005")
      )
    ),
    
    # Source of water for other purposes.
    WS2 = get_numeric_var(hh_Survey, c("HV202")),
    
    # Household weight.
    hhweight = scale_dhs_weight(get_numeric_var(hh_Survey, c("HV005"))),
    
    # No standard DHS equivalent found for MICS WS8.
    WS8 = NA_real_,
    
    country = country_vec,
    
    # Interview date.
    HH5D = get_numeric_var(hh_Survey, c("HV016")),
    HH5M = get_numeric_var(hh_Survey, c("HV006")),
    HH5Y = get_numeric_var(hh_Survey, c("HV007")),
    
    # Survey design variables.
    PSU = get_numeric_var(hh_Survey, c("HV021", "HV001")),
    stratum = get_numeric_var(hh_Survey, c("HV022", "HV023"))
  )
  
  # If the input is a PR file, household variables are repeated by person.
  # Keep one row per household.
  out <- out %>%
    distinct(country, HH1, HH2, .keep_all = TRUE)
  
  return(out)
}


# DHS-specific recoding to match MICS output coding


setDHSMainSourceLabels <- function(df) {
  
  # DHS drinking water source codes differ slightly from MICS:
  # in DHS 8, 71 = bottled water and 72 = water bag.
  # Therefore 71/72 are coded as packaged water = 3.
  
  df$WS1 <- case_when(
    df$WS1 %in% c(32, 42, 43, 96, 99) ~ 0,
    df$WS1 %in% c(10, 13, 14, 20, 21, 31, 41, 51, 61, 62) ~ 1,
    df$WS1 %in% c(11, 12) ~ 2,
    df$WS1 %in% c(71, 72, 91, 92) ~ 3,
    is.na(df$WS1) ~ NA_real_,
    TRUE ~ df$WS1
  )
  
  return(df)
}

setDHSSecondarySourceLabels <- function(df) {
  
  df$WS2 <- case_when(
    df$WS2 %in% c(32, 42, 43, 96, 99) ~ 0,
    df$WS2 %in% c(10, 13, 14, 20, 21, 31, 41, 51, 61, 62) ~ 1,
    df$WS2 %in% c(11, 12) ~ 2,
    df$WS2 %in% c(71, 72, 91, 92) ~ 3,
    is.na(df$WS2) ~ NA_real_,
    TRUE ~ df$WS2
  )
  
  return(df)
}

setDHSWS3_WslocationLabels <- function(df) {
  
  df$WS3 <- case_when(
    df$WS3 %in% c(1, 2, 3) ~ df$WS3,
    df$WS3 %in% c(8, 9, 98, 99) ~ -99,
    is.na(df$WS3) ~ NA_real_,
    TRUE ~ df$WS3
  )
  
  return(df)
}

setDHSWS4timeLabels <- function(df) {
  
  # DHS HV204:
  # 996 = on premises, equivalent to 0 collection time.
  # 998 = don't know.
  
  df$WS4 <- case_when(
    df$WS4 == 996 ~ 0,
    df$WS4 %in% c(997, 998, 999) ~ -99,
    is.na(df$WS4) ~ NA_real_,
    TRUE ~ df$WS4
  )
  
  return(df)
}

setDHSWS7WaterInsufficiencyLabels <- function(df) {
  
  # DHS HV201B:
  # 1 = yes, insufficient
  # 0 = no
  # 8 = don't know
  #
  # DHS HV201A fallback:
  # 1 = yes, interrupted for a full day or more
  # 0 = no
  # 8 = don't know
  
  df$WS7 <- case_when(
    df$WS7 == 1 ~ 1,
    df$WS7 %in% c(0, 2, 8) ~ 0,
    df$WS7 %in% c(9, 98, 99) ~ -99,
    is.na(df$WS7) ~ NA_real_,
    TRUE ~ df$WS7
  )
  
  return(df)
}

setDHSWS8WhyInsufficientLabels <- function(df) {
  
  # No standard DHS equivalent found for MICS WS8.
  df$WS8 <- NA_real_
  
  return(df)
}

setDHSWQ27SourceWaterQuality <- function(df) {
  
  # Keep comparable with your MICS approach:
  # 0 = no E. coli
  # >0 = contaminated
  # 101 or >100 = 100
  # common DHS/MICS missing/result-not-readable codes = -99
  
  df$WQ27 <- case_when(
    df$WQ27 %in% c(991, 995, 996, 997, 998, 999) ~ -99,
    df$WQ27 >= 101 ~ 100,
    is.na(df$WQ27) ~ NA_real_,
    TRUE ~ df$WQ27
  )
  
  return(df)
}

setDHSWRiskBIN <- function(df) {
  
  df$WQ27 <- case_when(
    df$WQ27 > 0 ~ 1,
    df$WQ27 == 0 ~ 0,
    df$WQ27 == -99 ~ -99,
    is.na(df$WQ27) ~ NA_real_,
    TRUE ~ df$WQ27
  )
  
  return(df)
}

setDHSAreaLabels <- function(df) {
  
  # DHS HV025:
  # 1 = urban
  # 2 = rural
  
  df$HH6 <- case_when(
    df$HH6 %in% c(1, 2) ~ df$HH6,
    df$HH6 %in% c(8, 9, 98, 99) ~ -99,
    is.na(df$HH6) ~ NA_real_,
    TRUE ~ df$HH6
  )
  
  return(df)
}

relabelingDHSQuestionResponses <- function(df.DHS.SMDW) {
  
  df.DHS.SMDW <- setDHSMainSourceLabels(df.DHS.SMDW)
  df.DHS.SMDW <- setDHSSecondarySourceLabels(df.DHS.SMDW)
  df.DHS.SMDW <- setDHSWS3_WslocationLabels(df.DHS.SMDW)
  df.DHS.SMDW <- setDHSWS4timeLabels(df.DHS.SMDW)
  df.DHS.SMDW <- setDHSWS7WaterInsufficiencyLabels(df.DHS.SMDW)
  df.DHS.SMDW <- setDHSWS8WhyInsufficientLabels(df.DHS.SMDW)
  df.DHS.SMDW <- setDHSWQ27SourceWaterQuality(df.DHS.SMDW)
  df.DHS.SMDW <- setDHSWRiskBIN(df.DHS.SMDW)
  df.DHS.SMDW <- setDHSAreaLabels(df.DHS.SMDW)
  
  return(df.DHS.SMDW)
}

# ------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------

checkDHSVariables <- function(df) {
  
  variables_to_check <- c(
    "HH1", "HH2", "WQ27", "WS7", "WS3", "HH7_region", "HH6",
    "WS1", "HH48", "WS4", "wqsweight", "WS2", "hhweight",
    "WS8", "country", "HH5D", "HH5M", "HH5Y", "PSU", "stratum"
  )
  
  missing_variables <- setdiff(variables_to_check, names(df))
  
  if (length(missing_variables) > 0) {
    message("Missing variables: ", paste(missing_variables, collapse = ", "))
  } else {
    message("All expected DHS/MICS-style variables are present.")
  }
  
  return(invisible(missing_variables))
}

checkDHSUnmappedValues <- function(df) {
  
  message("Unique values after relabelling:")
  
  print(list(
    WS1 = sort(unique(df$WS1)),
    WS2 = sort(unique(df$WS2)),
    WS3 = sort(unique(df$WS3)),
    WS4_missing_codes = sort(unique(df$WS4[df$WS4 < 0])),
    WS7 = sort(unique(df$WS7)),
    WS8 = sort(unique(df$WS8)),
    WQ27 = sort(unique(df$WQ27)),
    HH6 = sort(unique(df$HH6))
  ))
  
  return(invisible(NULL))
}

# ============================================================
# Map ISO-2 country codes to country names
# ============================================================

map_iso2_to_country_names <- function(iso2_codes, country_name_key_WB) {
  
  iso2_codes <- toupper(as.character(iso2_codes))
  
  country_lookup <- country_name_key_WB %>%
    mutate(
      Code = toupper(as.character(Code)),
      country = as.character(GADM_NAME_0),
      iso2_code = case_when(
        nchar(Code) == 2 ~ Code,
        nchar(Code) == 3 ~ countrycode::countrycode(
          Code,
          origin = "iso3c",
          destination = "iso2c"
        ),
        TRUE ~ NA_character_
      )
    ) %>%
    select(iso2_code, country) %>%
    filter(!is.na(iso2_code), !is.na(country)) %>%
    distinct()
  
  mapped <- tibble(
    iso2_code = iso2_codes
  ) %>%
    left_join(country_lookup, by = "iso2_code")
  
  unmatched <- mapped %>%
    filter(is.na(country))
  
  if (nrow(unmatched) > 0) {
    print(unmatched)
    stop("Some ISO-2 codes could not be matched to country_name_key_WB.")
  }
  
  return(mapped)
}



# ============================================================
# Extract DHS household variables excluding WQ27
# ============================================================

extractDHSOtherSurveyVariables <- function(
    hh_Survey,
    country_name = NULL,
    area_candidates = c("SHDISTRICT", "HV024")
) {
  
  hh_Survey <- standardise_dhs_names(hh_Survey)
  
  if (!is.null(country_name)) {
    country_vec <- rep(country_name, nrow(hh_Survey))
  } else if ("COUNTRY" %in% names(hh_Survey)) {
    country_vec <- as.character(hh_Survey$COUNTRY)
  } else {
    country_vec <- get_character_var(hh_Survey, c("HV000"))
  }
  
  out <- tibble(
    HH1 = get_numeric_var(hh_Survey, c("HV001")),
    HH2 = get_numeric_var(hh_Survey, c("HV002")),
    WS7 = get_numeric_var(hh_Survey, c("HV201B", "HV201A")),
    WS3 = get_numeric_var(hh_Survey, c("HV235")),
    HH7 = get_numeric_var(hh_Survey, area_candidates),
    HH6 = get_numeric_var(hh_Survey, c("HV025")),
    WS1 = get_numeric_var(hh_Survey, c("HV201")),
    HH48 = get_numeric_var(hh_Survey, c("HV009")),
    WS4 = get_numeric_var(hh_Survey, c("HV204")),
    WS2 = get_numeric_var(hh_Survey, c("HV202")),
    hhweight = scale_dhs_weight(get_numeric_var(hh_Survey, c("HV005"))),
    WS8 = NA_real_,
    country = country_vec,
    HH5D = get_numeric_var(hh_Survey, c("HV016")),
    HH5M = get_numeric_var(hh_Survey, c("HV006")),
    HH5Y = get_numeric_var(hh_Survey, c("HV007")),
    PSU = get_numeric_var(hh_Survey, c("HV021", "HV001")),
    stratum = get_numeric_var(hh_Survey, c("HV022", "HV023"))
  )
  
  out <- out %>%
    distinct(country, HH1, HH2, .keep_all = TRUE)
  
  return(out)
}

# ============================================================
# Relabel DHS other variables excluding WQ27
# ============================================================

relabelingDHSOtherQuestionResponses <- function(df.DHS.other) {
  
  df.DHS.other <- setDHSMainSourceLabels(df.DHS.other)
  df.DHS.other <- setDHSSecondarySourceLabels(df.DHS.other)
  df.DHS.other <- setDHSWS3_WslocationLabels(df.DHS.other)
  df.DHS.other <- setDHSWS4timeLabels(df.DHS.other)
  df.DHS.other <- setDHSWS7WaterInsufficiencyLabels(df.DHS.other)
  df.DHS.other <- setDHSWS8WhyInsufficientLabels(df.DHS.other)
  df.DHS.other <- setDHSAreaLabels(df.DHS.other)
  
  return(df.DHS.other)
}

# ============================================================
# Check expected DHS other variables
# ============================================================

checkDHSOtherVariables <- function(df) {
  
  variables_to_check <- c(
    "HH1", "HH2", "WS7", "WS3", "HH7_region", "HH6",
    "WS1", "HH48", "WS4", "WS2", "hhweight",
    "WS8", "country", "HH5D", "HH5M", "HH5Y",
    "PSU", "stratum"
  )
  
  missing_variables <- setdiff(variables_to_check, names(df))
  
  if (length(missing_variables) > 0) {
    message("Missing variables: ", paste(missing_variables, collapse = ", "))
  } else {
    message("All expected DHS other variables are present.")
  }
  
  return(invisible(missing_variables))
}

# ============================================================
# Check values after DHS other relabelling
# ============================================================

checkDHSOtherUnmappedValues <- function(df) {
  
  message("Unique values after DHS other relabelling:")
  
  print(list(
    WS1 = sort(unique(df$WS1)),
    WS2 = sort(unique(df$WS2)),
    WS3 = sort(unique(df$WS3)),
    WS4_missing_codes = sort(unique(df$WS4[df$WS4 < 0])),
    WS7 = sort(unique(df$WS7)),
    WS8 = sort(unique(df$WS8)),
    HH6 = sort(unique(df$HH6))
  ))
  
  return(invisible(NULL))
}