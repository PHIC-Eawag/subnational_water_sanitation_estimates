# title: "Functions for Re-Labeling Sanitation Variables from Household MICS SPSS files"
#
# Classification uses MICS6 numeric codes directly (read from SPSS as labelled
# integers via sjlabelled). String-label helpers are retained as fallbacks for
# surveys where numeric codes were lost during data prep.
#
# ── WS11  Type of toilet facility (MICS6 codes) ───────────────────────────────
#
#  MICS6 standard codes:
#   11  Flush / pour flush to piped sewer system
#   12  Flush / pour flush to septic tank
#   13  Flush / pour flush to pit latrine
#   14  Flush to open drain                         ← unimproved
#   18  Flush to somewhere else / don't know where  ← improved (JMP)
#   21  Pit latrine – Ventilated Improved Pit (VIP)
#   22  Pit latrine – With slab
#   31  Composting toilet
#   32  Pit latrine – Without slab / Open pit       ← unimproved
#   41  Bucket                                      ← unimproved
#   42  Hanging toilet / hanging latrine            ← unimproved
#   95  No facility / bush / field                  ← OPEN DEFECATION
#   96  Other                                       ← unimproved
#   99  Missing / no response                       ← unimproved (JMP)
#
# Three-way output classification:
#   2  = Improved facility
#   1  = Unimproved, but NOT open defecation
#   0  = Open defecation (no facility / bush / field)
#
# ── WS15  Shared facility (MICS6 codes) ──────────────────────────────────────
#   1  Yes – shared with other households / general public
#   2  No  – not shared
#   → recoded to: 1 = shared, 0 = not shared, -99 = missing
#
# ── HH6  Urban / Rural ────────────────────────────────────────────────────────
#   1 = Urban
#   2 = Rural
#   3 = Camp (where present)

# =============================================================================
# setToiletType_numeric()
# Primary classification function. Works on the underlying integer codes.
# Strips SPSS/haven label attributes before recoding.
# =============================================================================

setToiletType_numeric <- function(v) {
  v <- as.numeric(as.character(sjlabelled::as_label(v, keep.labels = FALSE)))
  
  # MICS6 standard codes + older MICS3/4 codes
  improved_codes   <- c(11, 12, 13, 15, 18, 21, 22, 31)
  # 15 = flush to unknown/DK (old coding) → improved per JMP
  
  unimproved_codes <- c(14, 23, 24, 32, 41, 42, 51, 61, 96, 99)
  # 23 = pit without slab (old MICS3/4, now 32)
  # 24 = hanging latrine / pit without slab variant (old coding)
  # 51 = other (old coding)
  # 61 = other, Ghana-specific
  
  od_codes <- c(25, 95)
  # 25 = no facility/bush/field (old MICS3/4, now 95)
  
  result <- rep(NA_real_, length(v))
  result[v %in% improved_codes]   <- 2
  result[v %in% unimproved_codes] <- 1
  result[v %in% od_codes]         <- 0
  
  return(result)
}
# =============================================================================
# setWS15_shared()
# MICS codes: 1 = Yes (shared), 2 = No (not shared)
# Output:     1 = shared, 0 = not shared, -99 = missing
# =============================================================================

setWS15_shared <- function(v) {
  v_num <- as.numeric(as.character(sjlabelled::as_label(v, keep.labels = FALSE)))

  result <- rep(NA_real_, length(v))
  result[v_num == 1] <-   1   # shared
  result[v_num == 2] <-   0   # not shared
  result[v_num %in% c(8, 9, 98, 99)] <- -99  # missing / DK

  return(result)
}

# =============================================================================
# setArea()   HH6: 1 = urban, 2 = rural, 3 = camp
# Works on both numeric codes and string labels (surveys vary).
# =============================================================================

setArea <- function(v) {
  # Try numeric path first
  v_num <- suppressWarnings(as.numeric(as.character(v)))
  if (!all(is.na(v_num[!is.na(v)]))) return(v_num)

  # String label path
  v_chr <- as.character(v)
  result <- rep(NA_real_, length(v_chr))
  result[v_chr %in% c("Urban", "URBAN", "Urbain", "URBAIN",
                       "Urbano", "Urbana", "URBANO")]            <- 1
  result[v_chr %in% c("Rural", "RURAL", "RURAL WITHOUT ROAD",
                       "RURAL WITH ROAD", "RURAL INTERIOR",
                       "RURAL COASTAL")]                          <- 2
  result[v_chr == "CAMP"]                                         <- 3
  return(result)
}

# =============================================================================
# labelingSurveyVariableResponses_sanitation()
# Wrapper applied to a combined data frame after rbind.
# =============================================================================

labelingSurveyVariableResponses_sanitation <- function(df) {
  df$WS11 <- setToiletType_numeric(df$WS11)
  df$WS15 <- setWS15_shared(df$WS15)
  df$HH6  <- setArea(df$HH6)
  return(df)
}

# =============================================================================
# deriveOpenDefecation()
# Adds derived outcome columns after labeling.
#
#   WS11_category   factor: "improved" / "unimproved" / "open_defecation"
#   WS11_improved   binary: 1 = improved facility (WS11 == 2)
#   open_defecation binary: 1 = open defecation  (WS11 == 0)
# =============================================================================

deriveOpenDefecation <- function(df) {
  df$WS11_improved <- ifelse(df$WS11 == 2, 1, 0)
  df$open_defecation <- ifelse(df$WS11 == 0, 1, 0)
  df$WS11_category <- factor(
    dplyr::case_when(
      df$WS11 == 2 ~ "improved",
      df$WS11 == 1 ~ "unimproved",
      df$WS11 == 0 ~ "open_defecation",
      TRUE         ~ NA_character_
    ),
    levels = c("improved", "unimproved", "open_defecation")
  )
  return(df)
}

# =============================================================================
# checkUncodedWS11()
# Diagnostic: returns rows where WS11 is still NA after labeling.
# Useful for catching surveys with non-standard numeric codes.
# =============================================================================

checkUncodedWS11 <- function(df) {
  uncoded <- df[is.na(df$WS11), ]
  if (nrow(uncoded) == 0) {
    message("checkUncodedWS11: all rows classified.")
  } else {
    message("checkUncodedWS11: ", nrow(uncoded), " uncoded rows.")
    # Return original raw values if raw_WS11 was preserved
    if ("WS11_raw" %in% names(df)) {
      print(table(uncoded$WS11_raw, useNA = "always"))
    }
  }
  return(invisible(uncoded))
}
