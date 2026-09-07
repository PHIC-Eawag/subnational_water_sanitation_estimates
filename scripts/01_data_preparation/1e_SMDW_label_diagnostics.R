library(tidyverse)
library(haven)
library(labelled)
library(here)

source(here::here("configuration/paths.R"))

# Expanded so haven::read_sav() (which does not resolve "~") can find the .sav files
SWITCHDRIVE_HH_DIR <- path.expand(PATH_SWITCHDRIVE_HH_DIR)
path_smdw <- PATH_HH_SMDW_ANALYSIS

df <- readr::read_csv(path_smdw, show_col_types = FALSE)

# WS1: find rows with unmapped codes
cat("=== WS1 unmapped codes (44, 94, 95) ===\n")
df |>
  filter(WS1 %in% c(44, 94, 95)) |>
  count(country, survey_id, household_data_source, WS1) |>
  arrange(WS1, country) |>
  print(n = Inf)

# WS2: find rows with unmapped codes
cat("\n=== WS2 unmapped codes ===\n")
ws2_bad <- setdiff(unique(df$WS2), c(0, 1, 2, 3, NA))
df |>
  filter(WS2 %in% ws2_bad) |>
  count(country, survey_id, household_data_source, WS2) |>
  arrange(WS2, country) |>
  print(n = Inf)

# WS3: find rows with unmapped codes
cat("\n=== WS3 unmapped codes (4) ===\n")
df |>
  filter(WS3 == 4) |>
  count(country, survey_id, household_data_source) |>
  arrange(country) |>
  print(n = Inf)

library(haven)
library(labelled)

# --- Guatemala DHS (WS1 code 44) ---
# survey_id = GUHR71FL → DHS_other folder
guatemala_path <- file.path(SWITCHDRIVE_HH_DIR, "HH_survey_data/HH_DHS_other/GUHR71FL.sav")
df_gt <- haven::read_sav(guatemala_path)
cat("Guatemala WS1 value labels:\n")
print(labelled::val_labels(df_gt$WS1))

# --- Thailand MICS (WS1 codes 94, 95) ---
# survey_id = NA, MICS_other → find the Thailand file
thailand_files <- list.files(
  file.path(SWITCHDRIVE_HH_DIR, "HH_survey_data/HH_MICS_new_other"),
  pattern = "(?i)thai", full.names = TRUE
)
cat("\nThailand MICS files found:\n"); print(thailand_files)
if (length(thailand_files) > 0) {
  df_th <- haven::read_sav(thailand_files[1])
  cat("Thailand WS1 value labels:\n")
  print(labelled::val_labels(df_th$WS1))
}

# --- Chad MICS (WS3 code 4) ---
# survey_id = NA, MICS_water_quality → HH_MICS_new_SMDW or HH_MICS_old_SMDW
chad_files <- list.files(
  file.path(SWITCHDRIVE_HH_DIR, "HH_survey_data"),
  pattern = "(?i)chad", full.names = TRUE, recursive = TRUE
)
cat("\nChad MICS files found:\n"); print(chad_files)
if (length(chad_files) > 0) {
  df_chad <- haven::read_sav(chad_files[1])
  cat("Chad WS3 value labels:\n")
  print(labelled::val_labels(df_chad$WS3))
}

# Find the drinking water variable in the Guatemala DHS file
df_gt <- haven::read_sav(guatemala_path)
cat("All variables in Guatemala DHS file:\n")
print(names(df_gt))

# Once you find the right variable name (likely hv201), check its labels:

print(labelled::val_labels(df_gt$HV201))


# ── Step 1: find which surveys contain each unmapped code ─────────────────────

codes_to_check <- c(15, 16, 33,44, 52, 53, 54, 63, 73, 82)

cat("=== WS1 unmapped codes by survey ===\n")
df |>
  filter(WS1 %in% codes_to_check) |>
  count(country, survey_id, household_data_source, WS1) |>
  arrange(WS1, country) |>
  print(n = Inf)

cat("\n=== WS2 unmapped codes by survey ===\n")
df |>
  filter(WS2 %in% codes_to_check) |>
  count(country, survey_id, household_data_source, WS2) |>
  arrange(WS2, country) |>
  print(n = Inf)

# ── Step 2: look up SPSS labels for each unique survey found ──────────────────
# Identifies one representative file per survey and prints WS1/WS2 value labels.

check_spss_labels <- function(spss_path, country_name) {
  cat("\n", strrep("=", 60), "\n")
  cat(country_name, "\n")
  cat("File:", basename(spss_path), "\n")
  cat(strrep("=", 60), "\n")
  
  if (!file.exists(spss_path)) {
    cat("  FILE NOT FOUND — check path\n")
    return(invisible(NULL))
  }
  
  df_raw <- haven::read_sav(spss_path)
  
  # Try both MICS (WS1/WS2) and DHS (HV201/HV202) variable names
  ws1_var <- intersect(c("WS1", "ws1", "HV201", "hv201"), names(df_raw))[1]
  ws2_var <- intersect(c("WS2", "ws2", "HV202", "hv202"), names(df_raw))[1]
  
  if (!is.na(ws1_var)) {
    cat("WS1 /", ws1_var, "value labels:\n")
    print(labelled::val_labels(df_raw[[ws1_var]]))
  } else {
    cat("No WS1/HV201 variable found. Available vars:\n")
    cat(paste(names(df_raw)[1:30], collapse = ", "), "...\n")
  }
  
  if (!is.na(ws2_var)) {
    cat("\nWS2 /", ws2_var, "value labels:\n")
    print(labelled::val_labels(df_raw[[ws2_var]]))
  }
}

# ── Step 3: call check_spss_labels for each survey identified in Step 1 ──────
# Fill in the file paths after seeing the Step 1 output.
# Template — add/remove rows to match what Step 1 returns.

surveys_to_check <- tribble(
  ~country,        ~subfolder,              ~filename,
  # DHS surveys (survey_id known) — in HH_DHS_other/
  "Burkina Faso",  "HH_DHS_other",          "BFHR81FL.sav",
  "Gabon",         "HH_DHS_other",          "GAHR71FL.sav",
  "Angola",        "HH_DHS_other",          "AOHR81FL.sav",
  "Colombia",      "HH_DHS_other",          "COHR72FL.sav",
  "Zambia",        "HH_DHS_other",          "ZMHR81FL.sav",
  # MICS surveys (survey_id = NA) — search by country name
  "Thailand",      "HH_MICS_new_other",     "hh_Thailand.sav",
)

for (i in seq_len(nrow(surveys_to_check))) {
  path <- file.path(
    SWITCHDRIVE_HH_DIR, "HH_survey_data",
    surveys_to_check$subfolder[i],
    surveys_to_check$filename[i]
  )
  check_spss_labels(path, surveys_to_check$country[i])
}
