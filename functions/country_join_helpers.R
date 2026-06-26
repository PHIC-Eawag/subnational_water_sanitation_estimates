# functions/country_join_helpers.R
# Unified helper to attach a standardised country join key to any data frame.
# Uses the World Bank country name lookup plus manual corrections for names
# that are not in the lookup (e.g. alternative spellings in source datasets).

# Manual corrections: keys are clean_key() output, values are display names
# that will themselves be passed through clean_key() before joining.
.wb_name_manual_fixes <- c(
  "bolivia plurinational state of"                          = "Bolivia",
  "congo dem republic"                                      = "Congo, Dem. Rep.",
  "congo rep"                                               = "Congo, Rep.",
  "cote d ivoire"                                           = "Cote d'Ivoire",
  "iran islamic republic of"                                = "Iran, Islamic Rep.",
  "lao peoples democratic republic"                         = "Lao PDR",
  "lao people s democratic republic"                        = "Lao PDR",
  "macedonia fyr"                                           = "North Macedonia",
  "sao tome and principe"                                   = "Sao Tome and Principe",
  "swaziland"                                               = "Eswatini",
  "eswatini"                                                = "Eswatini",
  "tanzania"                                                = "Tanzania",
  "venezuela bolivarian republic of"                        = "Venezuela, RB",
  "viet nam"                                                = "Viet Nam",
  "vietnam"                                                 = "Viet Nam",
  "west bank gaza"                                          = "West Bank and Gaza",
  "west bank and gaza"                                      = "West Bank and Gaza"
)

#' Add a standardised country join key to a data frame
#'
#' Attaches `country_join` (a clean_key()-normalised World Bank country name)
#' to `df`. Works for both country-year data and country-only data.
#'
#' @param df                  Data frame to augment
#' @param country_col         Unquoted column containing raw country names
#' @param country_name_key_WB The WB country name lookup table
#'
#' @return `df` with added `country_join` column; intermediate key columns removed
add_country_join_key_extended <- function(df, country_col, country_name_key_WB) {
  wb_lookup <- build_wb_country_lookup(country_name_key_WB)
  
  df %>%
    dplyr::select(-dplyr::any_of(c("country_join", "country_alias_key", "country_wb"))) %>%
    dplyr::mutate(country_alias_key = clean_key({{ country_col }})) %>%
    dplyr::left_join(wb_lookup, by = "country_alias_key") %>%
    dplyr::mutate(
      country_join_raw = dplyr::coalesce(country_wb, country_alias_key),
      country_join_raw = dplyr::recode(country_join_raw, !!!.wb_name_manual_fixes),
      country_join     = clean_key(country_join_raw)
    ) %>%
    dplyr::select(-country_alias_key, -country_wb, -country_join_raw)
}