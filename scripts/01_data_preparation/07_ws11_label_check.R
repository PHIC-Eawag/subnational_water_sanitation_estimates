# =============================================================================
# 1. WS11 label check — audit how raw toilet-type codes map to the WS11
# open defecation / unimproved / improved classification.
#
# Purpose
# -------
# When a country's national basic-sanitation or open-defecation estimate
# diverges from JMP, the first thing to rule out is a labelling mistake: a
# raw survey code being classified into the wrong WS11 category (or silently
# dropped to NA). This script builds a raw-code -> classification crosstab per
# country so those cases are easy to spot.
#
# MICS vs DHS
# -----------
# The MICS pipeline (01a) preserves the original code in `WS11_raw`, so a full
# raw-code -> category crosstab is possible. The DHS pipeline (01b) does NOT
# currently preserve the raw HV205 code — it overwrites WS11 with the final
# 0/1/2 classification — so for DHS this script can only show the final
# classification distribution. To enable the full crosstab for DHS, preserve
# `WS11_raw = HV205` in 01b (mirroring 01a) and rerun it.
#
# Usage
# -----
#   Rscript scripts/01_data_preparation/ws11_label_check.R
# or source() it interactively. Edit the CONFIG block below to choose which
# countries to inspect and whether to write CSVs.
# =============================================================================

suppressMessages({
  library(dplyr)
  library(readr)
  library(here)
})

# ── CONFIG ───────────────────────────────────────────────────────────────────
# Countries to inspect. Set to NULL for all countries, or a character vector
# to focus (names must match the `country` column in the processed files).
COUNTRIES <- c(
  # surveys flagged as diverging from JMP by >5 pp (edit as needed):
  "Afghanistan", "Paraguay", "Nepal",                     # MICS
  "Mauritania", "Zambia", "Mozambique", "Ghana", "Cambodia"  # DHS
)

WRITE_CSV <- TRUE  # write results to outputs/descriptive_statistics/
OUTPUT_DIR <- here::here("outputs/descriptive_statistics")

PATH_MICS <- here::here("data/processed/household_surveys/df_sanitation_MICS_v2.csv")
PATH_DHS  <- here::here("data/processed/household_surveys/df_sanitation_DHS_v2.csv")

# ── Helpers ──────────────────────────────────────────────────────────────────

# Map the numeric WS11 code to a readable category (used for DHS, which has no
# WS11_category column, and as a fallback).
ws11_category_from_code <- function(x) {
  dplyr::case_when(
    x == 2 ~ "improved",
    x == 1 ~ "unimproved",
    x == 0 ~ "open_defecation",
    TRUE   ~ NA_character_
  )
}

filter_countries <- function(df) {
  if (is.null(COUNTRIES)) return(df)
  df %>% dplyr::filter(country %in% COUNTRIES)
}

# MICS: full raw-code -> category crosstab, one row per country x raw code.
build_mics_crosstab <- function(df) {
  df %>%
    dplyr::mutate(
      WS11_category = as.character(WS11_category),
      WS11_category = dplyr::coalesce(WS11_category, ws11_category_from_code(WS11))
    ) %>%
    dplyr::count(country, WS11_raw, WS11_category, name = "n") %>%
    dplyr::group_by(country) %>%
    dplyr::mutate(pct_of_country = round(100 * n / sum(n), 2)) %>%
    dplyr::ungroup() %>%
    dplyr::arrange(country, WS11_raw)
}

# DHS: if the raw HV205 code was preserved (WS11_raw, added to 01b), build the
# full raw-code -> classification crosstab like MICS. Otherwise fall back to
# the final classification distribution (older DHS outputs without WS11_raw).
dhs_has_raw <- function(df) "WS11_raw" %in% names(df)

build_dhs_crosstab <- function(df) {
  df %>%
    dplyr::mutate(WS11_category = ws11_category_from_code(WS11)) %>%
    dplyr::count(country, WS11_raw, WS11, WS11_category, name = "n") %>%
    dplyr::group_by(country) %>%
    dplyr::mutate(pct_of_country = round(100 * n / sum(n), 2)) %>%
    dplyr::ungroup() %>%
    dplyr::arrange(country, WS11_raw)
}

build_dhs_distribution <- function(df) {
  df %>%
    dplyr::mutate(WS11_category = ws11_category_from_code(WS11)) %>%
    dplyr::count(country, WS11, WS11_category, name = "n") %>%
    dplyr::group_by(country) %>%
    dplyr::mutate(pct_of_country = round(100 * n / sum(n), 2)) %>%
    dplyr::ungroup() %>%
    dplyr::arrange(country, WS11)
}

# ── Load ─────────────────────────────────────────────────────────────────────
mics <- readr::read_csv(PATH_MICS, show_col_types = FALSE) %>% filter_countries()
dhs  <- readr::read_csv(PATH_DHS,  show_col_types = FALSE) %>% filter_countries()

# Warn about any requested country not found in either file.
if (!is.null(COUNTRIES)) {
  found   <- union(unique(mics$country), unique(dhs$country))
  missing <- setdiff(COUNTRIES, found)
  if (length(missing) > 0) {
    warning("Requested countries not found in processed files: ",
            paste(missing, collapse = ", "))
  }
}

# ── MICS crosstab ────────────────────────────────────────────────────────────
mics_crosstab <- build_mics_crosstab(mics)

cat("\n============================================================\n")
cat("MICS — WS11_raw -> WS11_category crosstab (raw codes preserved)\n")
cat("Look for: a raw code classified into an unexpected category,\n")
cat("or rows with WS11_category = NA (uncoded raw values).\n")
cat("============================================================\n")
for (ctry in sort(unique(mics_crosstab$country))) {
  cat("\n----", ctry, "----\n")
  mics_crosstab %>%
    dplyr::filter(country == ctry) %>%
    dplyr::select(WS11_raw, WS11_category, n, pct_of_country) %>%
    as.data.frame() %>%
    print(row.names = FALSE)
}

# ── DHS crosstab / distribution ──────────────────────────────────────────────
if (dhs_has_raw(dhs)) {
  dhs_crosstab <- build_dhs_crosstab(dhs)
  cat("\n\n============================================================\n")
  cat("DHS — WS11_raw -> WS11_category crosstab (raw HV205 codes preserved)\n")
  cat("Look for: a raw code classified into an unexpected category,\n")
  cat("or rows with WS11_category = NA (uncoded raw values, silently dropped).\n")
  cat("============================================================\n")
  for (ctry in sort(unique(dhs_crosstab$country))) {
    cat("\n----", ctry, "----\n")
    dhs_crosstab %>%
      dplyr::filter(country == ctry) %>%
      dplyr::select(WS11_raw, WS11, WS11_category, n, pct_of_country) %>%
      as.data.frame() %>%
      print(row.names = FALSE)
  }
} else {
  dhs_distribution <- build_dhs_distribution(dhs)
  cat("\n\n============================================================\n")
  cat("DHS — final WS11 classification distribution\n")
  cat("NOTE: this DHS file has no WS11_raw column, so a raw-code crosstab is\n")
  cat("not possible. Rerun 01b (which now preserves WS11_raw = HV205) to enable it.\n")
  cat("============================================================\n")
  for (ctry in sort(unique(dhs_distribution$country))) {
    cat("\n----", ctry, "----\n")
    dhs_distribution %>%
      dplyr::filter(country == ctry) %>%
      dplyr::select(WS11, WS11_category, n, pct_of_country) %>%
      as.data.frame() %>%
      print(row.names = FALSE)
  }
}

# ── Optional CSV output ──────────────────────────────────────────────────────
#if (WRITE_CSV) {
#  dir.create(OUTPUT_DIR, recursive = TRUE, showWarnings = FALSE)
 # readr::write_csv(mics_crosstab,
  #                 file.path(OUTPUT_DIR, "ws11_label_check_mics_crosstab.csv"))
  #readr::write_csv(dhs_distribution,
   #                file.path(OUTPUT_DIR, "ws11_label_check_dhs_distribution.csv"))
  #cat("\nWritten:\n",
   #   " ", file.path(OUTPUT_DIR, "ws11_label_check_mics_crosstab.csv"), "\n",
    #  " ", file.path(OUTPUT_DIR, "ws11_label_check_dhs_distribution.csv"), "\n")
#}

# =============================================================================
# 2. Extract toilet-type value labels from raw MICS / DHS survey files, for the
# surveys whose national estimates diverge from JMP.
#
# Purpose
# -------
# The processed data stores only the numeric toilet code (WS11_raw for MICS;
# nothing for DHS). To confirm what each code actually MEANS in a specific
# survey — and whether the pipeline classifies it correctly — read the
# original SPSS value labels straight from the raw .sav and print them next to
# the pipeline's current classification (open defecation / unimproved /
# improved). Any row where the raw label and the pipeline class disagree is a
# labelling bug to fix in:
#   - MICS: setToiletType_numeric() in functions/label_mics_sanitation_variables.R
#   - DHS:  setDHSWS11ToiletTypeLabels() in functions/extract_label_dhs_sanitation_variables.R
#
# READ-ONLY: this only reads the raw survey files on switchdrive; it never
# writes anything back there.
#
# Usage
# -----
#   Rscript scripts/01_data_preparation/ws11_raw_value_labels.R
# Edit the SURVEYS table below to add/remove surveys.
# =============================================================================

suppressMessages({
  library(dplyr)
  library(sjlabelled)
  library(haven)
  library(tibble)
  library(tidyr)
  library(here)
})

# Source the REAL labelling functions so the classification column always
# reflects the actual pipeline (no duplicated code lists that can drift out of
# sync). Provides setToiletType_numeric() + applyMICSSurveySpecificWS11Overrides()
# (MICS) and setDHSWS11ToiletTypeLabels() + applyDHSSurveySpecificWS11Overrides()
# (DHS).
source(here::here("functions/label_mics_sanitation_variables.R"))
source(here::here("functions/extract_label_dhs_sanitation_variables.R"))

HH <- path.expand("~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data")

# ── Flagged surveys: which raw file + toilet variable for each ───────────────
# MICS toilet var is "WS11" (or "WS8" in older-named files, e.g. Paraguay).
# DHS toilet var is "HV205".
SURVEYS <- tibble::tribble(
  ~country,       ~survey_type, ~file,                                          ~toilet_var,
  "Afghanistan",  "MICS",       file.path(HH, "HH_MICS_new_other/hh_Afghanistan.sav"), "WS11",
  "Nepal",        "MICS",       file.path(HH, "HH_MICS_new_SMDW/hh_Nepal.sav"),        "WS11",
  "Paraguay",     "MICS",       file.path(HH, "HH_MICS_old_SMDW/hh_Paraguay.sav"),     "WS8",
  "Mauritania",   "DHS",        file.path(HH, "HH_DHS_other/MRHR71FL.SAV"),            "HV205",
  "Zambia",       "DHS",        file.path(HH, "HH_DHS_other/ZMHR81FL.sav"),            "HV205",
  "Mozambique",   "DHS",        file.path(HH, "HH_DHS_other/MZHR81FL.SAV"),            "HV205",
  "Ghana",        "DHS",        file.path(HH, "HH_DHS_other/GHHR8CFL.SAV"),            "HV205",
  "Cambodia",     "DHS",        file.path(HH, "HH_DHS_other/KHHR82FL.SAV"),            "HV205"
)

# ── Pipeline classification via the real labelling functions ─────────────────
# Runs the raw codes through the same functions the pipeline uses (including
# the per-survey overrides), so the result matches the reprocessed data exactly.
classify_codes <- function(codes, survey_type, country) {
  df <- data.frame(
    country  = country,
    WS11     = codes,
    WS11_raw = codes,
    stringsAsFactors = FALSE
  )
  if (survey_type == "MICS") {
    df$WS11 <- setToiletType_numeric(df$WS11)
    df      <- applyMICSSurveySpecificWS11Overrides(df)
  } else {
    df <- setDHSWS11ToiletTypeLabels(df)
    df <- applyDHSSurveySpecificWS11Overrides(df)
  }
  dplyr::case_when(
    df$WS11 == 2 ~ "improved",
    df$WS11 == 1 ~ "unimproved",
    df$WS11 == 0 ~ "open_defecation",
    TRUE         ~ "NA (dropped)"
  )
}

# ── Extract labels + observed counts for one survey ──────────────────────────
extract_one <- function(country, survey_type, file, toilet_var) {
  cat("\n============================================================\n")
  cat(country, "(", survey_type, ") —", basename(file), "| var:", toilet_var, "\n")
  cat("============================================================\n")

  if (!file.exists(file)) {
    cat("  FILE NOT FOUND:", file, "\n"); return(invisible(NULL))
  }

  raw <- sjlabelled::read_spss(file)
  if (!toilet_var %in% names(raw)) {
    cat("  Variable", toilet_var, "not found. WS/HV vars present: ",
        paste(grep("^(WS|HV|hv|ws)", names(raw), value = TRUE), collapse = ", "), "\n")
    return(invisible(NULL))
  }

  v <- raw[[toilet_var]]
  cat("Question label:", sjlabelled::get_label(v), "\n\n")

  label_map <- sjlabelled::get_labels(v, values = "n")
  value_labels <- tibble::tibble(
    code  = suppressWarnings(as.integer(names(label_map))),
    label = as.character(label_map)
  )
  observed <- tibble::tibble(
    code = suppressWarnings(as.integer(sjlabelled::as_numeric(v, keep.labels = FALSE)))
  ) %>% dplyr::count(code, name = "n")

  value_labels %>%
    dplyr::full_join(observed, by = "code") %>%
    dplyr::mutate(
      n = tidyr::replace_na(n, 0L),
      pct = round(100 * n / sum(n), 2),
      pipeline_classifies_as = classify_codes(code, survey_type, country)
    ) %>%
    dplyr::arrange(code) %>%
    dplyr::select(code, label, pipeline_classifies_as, n, pct) %>%
    as.data.frame() %>%
    print(row.names = FALSE)

  invisible(NULL)
}

# ── Run for all flagged surveys ──────────────────────────────────────────────
for (i in seq_len(nrow(SURVEYS))) {
  s <- SURVEYS[i, ]
  extract_one(s$country, s$survey_type, s$file, s$toilet_var)
}

cat("\n\nHOW TO READ: compare `label` (what the survey says the code means)\n",
    "against `pipeline_classifies_as` (what the code currently assigns).\n",
    "Any mismatch — e.g. a latrine labelled but classified open_defecation,\n",
    "or a real facility shown as 'NA (dropped)' — is a labelling bug to fix.\n")