# functions/diagnostics.R
# Reusable diagnostic helpers for covariate–outcome matching workflows.

#' Flag training rows missing values in specified covariate columns
#'
#' @param training_df  A training dataset data frame
#' @param outcome_name Character label for the outcome (used in output column)
#' @param check_cols   Character vector of column names to check for NAs
check_missing_covariates <- function(training_df, outcome_name, check_cols) {
  training_df %>%
    dplyr::filter(dplyr::if_any(dplyr::all_of(check_cols), is.na)) %>%
    dplyr::distinct(country_outcome, analysis_year,
                    dplyr::across(dplyr::all_of(check_cols))) %>%
    dplyr::mutate(outcome_type = outcome_name) %>%
    dplyr::arrange(country_outcome, analysis_year)
}

#' Identify country–years present in outcomes and raw covariates but lost after filtering
#'
#' Useful for diagnosing why certain countries drop out during
#' filter_covariates_to_outcome_years(). Common causes: country name mismatch
#' or the country not being mapped in build_wb_country_lookup().
diagnose_country_year_filtering <- function(
    outcome_name,
    outcome_df,
    raw_covariates,
    filtered_covariates,
    country_name_key_WB
) {
  wb_lookup <- build_wb_country_lookup(country_name_key_WB)
  
  outcome_cys <- outcome_df %>%
    dplyr::transmute(
      outcome_name  = outcome_name,
      country_outcome,
      country_key   = clean_key(country_outcome),
      analysis_year = as.integer(analysis_year)
    ) %>%
    dplyr::distinct()
  
  raw_cov_cys <- raw_covariates %>%
    dplyr::transmute(
      country_key   = clean_key(country),
      analysis_year = as.integer(analysis_year)
    ) %>%
    dplyr::distinct()
  
  filtered_cov_cys <- filtered_covariates %>%
    dplyr::transmute(
      country_key   = clean_key(country),
      analysis_year = as.integer(analysis_year)
    ) %>%
    dplyr::distinct()
  
  outcome_cys %>%
    dplyr::inner_join(raw_cov_cys,      by = c("country_key", "analysis_year")) %>%
    dplyr::anti_join(filtered_cov_cys,  by = c("country_key", "analysis_year")) %>%
    dplyr::left_join(wb_lookup, by = c("country_key" = "country_alias_key")) %>%
    dplyr::mutate(
      likely_issue = dplyr::case_when(
        is.na(country_wb) ~ "country not mapped in build_wb_country_lookup()",
        TRUE              ~ "mapped — check another filtering issue"
      )
    ) %>%
    dplyr::arrange(outcome_name, country_outcome, analysis_year)
}
