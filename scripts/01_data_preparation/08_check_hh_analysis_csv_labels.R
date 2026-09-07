# ============================================================
# Check column headers and possible responses in the two
# analysis CSV files against the README documentation.
#
# Prints all column names and unique values for each column.
# ============================================================

library(tidyverse)

SWITCHDRIVE_HH_DIR <- "/Users/esthergreenwood/switchdrive/Eawag/WorldBankProject/additional_data_0002020937/HH_surveys"

path_sanitation <- file.path(SWITCHDRIVE_HH_DIR, "df_hh_sanitation_analysis.csv")
path_smdw       <- file.path(SWITCHDRIVE_HH_DIR, "df_hh_smdw_analysis.csv")

print_column_summary <- function(path, file_label) {
  df <- readr::read_csv(path, show_col_types = FALSE)

  cat("\n")
  cat(strrep("=", 70), "\n")
  cat(file_label, "\n")
  cat(strrep("=", 70), "\n")
  cat("Columns:", ncol(df), "| Rows:", nrow(df), "\n\n")

  for (col in names(df)) {
    vals <- sort(unique(df[[col]]))

    # Truncate very long value lists (e.g. free-text or continuous variables)
    is_continuous <- is.numeric(df[[col]]) &&
      length(vals) > 30 &&
      !col %in% c("WS11", "WS15", "WS1", "WS2", "WS3", "WS4",
                  "WS7", "WS8", "WQ27", "HH6", "HH5Y", "HH5M",
                  "WS11_improved", "open_defecation", "WS11_raw")

    cat(strrep("-", 50), "\n")
    cat("Column:", col, "\n")

    if (is_continuous) {
      cat("  [Continuous / ID — range:", min(vals, na.rm = TRUE),
          "to", max(vals, na.rm = TRUE), "]\n")
      cat("  N unique values:", length(vals), "| NAs:", sum(is.na(df[[col]])), "\n")
    } else {
      cat("  Unique values (", length(vals), "):", "\n")
      cat(" ", paste(vals, collapse = ", "), "\n")
      cat("  NAs:", sum(is.na(df[[col]])), "\n")
    }
  }
  cat("\n")
}

print_column_summary(path_sanitation, "df_hh_sanitation_analysis.csv")
print_column_summary(path_smdw,       "df_hh_smdw_analysis.csv")
