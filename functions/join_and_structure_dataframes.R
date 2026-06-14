# Title: functions for joining and structuring environmental dataframes


readCountryNamesOfUNPopulationDivisionWorldPopulationProspects <- function(){
  UN_Population_Devision_Names<- read.csv(here("1_Data/CountryNamesUNPopulationDivisionWorldPopulationProspects.csv")) 
  return(UN_Population_Devision_Names)
}

readUNSDMethodologyGlobalRegions <- function(){
  UN_Population_Devision_Names<- read.csv(here("./1_Data/UNSDMethodologyGlobalRegions.csv")) 
  return(UN_Population_Devision_Names)
}

renameCountryNamesAccordingToUNPopulationDevision <- function(df){
  df$NAME_0[df$NAME_0 == "Kosovo"] <- "Kosovo (under UNSC res. 1244)"
  df$NAME_0[df$NAME_0 == "Laos"] <- "Lao People's Democratic Republic"
  df$NAME_0[df$NAME_0 == "Palestina"] <- "State of Palestine"
  return(df)
}


readEarthObservationFeaturesAndRenameCountriesAccordingToUN_WPP <- function(){
  
  EO_features <- read.csv(here("./1_Data/EnvironmentalFeatures/GADM_environmental_trainingData_final.csv")) 
  
  EO_features <-renameCountryNamesAccordingToUNPopulationDevision(EO_features)
  
  return(EO_features)
}

readHouseHoldSurveyData_SMDW_new <- function(){
  df.MICS_HH <- read.csv("~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/df_SMDW_newMICS_v1.csv")
  return(df.MICS_HH)
}

readHouseHoldSurveyData_SMDW_new_other <- function(){
  df.MICS_HH <- read.csv("~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/df_other_MICS.csv")
  return(df.MICS_HH)
}

readHouseHoldSurveyData_SMDW_old <- function(){
  df.MICS_HH <- read.csv("~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/df_SMDW_oldMICS_v1.csv")
  return(df.MICS_HH)
}

readHouseHoldSurveyData_SMDW_DHS <- function(){
  df.MICS_HH <- read.csv("~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/df_SMDW_DHS.csv")
  return(df.MICS_HH)
}

readHouseHoldSurveyData_SMDW_DHS_other <- function(){
  df.MICS_HH <- read.csv("~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/df_other_DHS_SMDW.csv")
  return(df.MICS_HH)
}

readOverviewWaterQualityData <- function(){
  df.water_quality_overview <- read.csv(here::here("./data/overview_water_quality_data_v2.csv"))
  return(df.water_quality_overview)
}

readWGI_lmics <- function(){
  df.MICS_HH <- read.csv("~/switchdrive/Eawag/WorldBankProject/geospatial_covariates/worldwide_governance_indicators_prediction.csv")
  return(df.MICS_HH)
}

readPredictionData_nonpop <- function(){
  df.MICS_HH <- read.csv(here::here("./data/features/worldbank_sampled_pred_v1.0.csv"))
  return(df.MICS_HH)
}




createDataFrameWithValidationHoldOutPredictions <- function(rf_model_SMDW, combined_SMDW_envir_human_39){
    
  TrainAndPredicted_SMDW <- as.data.frame(h2o.cross_validation_holdout_predictions(rf_model_SMDW))

  TrainAndPredicted_SMDW$SMDWcoverageAtRegionalLevel <- as.numeric(combined_SMDW_envir_human_39[["SMDWcoverageAtRegionalLevel"]])

  TrainAndPredicted_SMDW$CountryID <- combined_SMDW_envir_human_39[["country_fold"]]

  TrainAndPredicted_SMDW$Country <- combined_SMDW_envir_human_39[["NAME_0"]]

  TrainAndPredicted_SMDW$NumberOfHouseholdsInRegion  <- as.numeric(combined_SMDW_envir_human_39[["HouseholdsInRegion.Freq.x"]])

return(TrainAndPredicted_SMDW)
  }


joinWithCountryIncomeGroups <- function(TrainAndPredicted_SMDW, UN_Population_Devision_Names, country_Income_Groups){
  
  TrainAndPredicted_SMDW <- TrainAndPredicted_SMDW %>%
    left_join(UN_Population_Devision_Names, by = c("Country"="Country"))%>%
    left_join(country_Income_Groups, by = c("ISO3.Alpha.code"="Code")) 
  
  return(TrainAndPredicted_SMDW)
}

joinWithCountryUNGlobalRegions <- function(regMatrix_SMDW, UN_Population_Devision_Names, GlobalRegions){
  
  regMatrix_SMDW <- regMatrix_SMDW %>%
    left_join(UN_Population_Devision_Names, by = c("NAME_0"="Country")) %>%
    left_join(GlobalRegions, by = c("ISO3.Alpha.code"="ISO.alpha3.Code")) %>%
  
  
  return(regMatrix_SMDW)
}
    
readAndRenameStandardGlobalRegionNames <- function(){
  UNStandardGlobalRegion <- read.csv(here("1_Data/UNSDMethodologyGlobalRegions.csv"), encoding = "UTF-8")
  
  UNStandardGlobalRegion <- UNStandardGlobalRegion %>% 
    select("Region.Code","Region.Name","Sub.region.Code", "Sub.region.Name", "ISO.alpha3.Code","Least.Developed.Countries..LDC.","Land.Locked.Developing.Countries..LLDC.", "Small.Island.Developing.States..SIDS.")
  
  names(UNStandardGlobalRegion)[names(UNStandardGlobalRegion) == 'Sub.region.Code'] <- 'UNSubRegionCode'
  names(UNStandardGlobalRegion)[names(UNStandardGlobalRegion) == 'Sub.region.Name'] <- 'UNSubRegionName'
  names(UNStandardGlobalRegion)[names(UNStandardGlobalRegion) == 'Region.Code'] <- 'UNRegionCode'
  names(UNStandardGlobalRegion)[names(UNStandardGlobalRegion) == 'Region.Name'] <- 'UNRegionName'
  
return(UNStandardGlobalRegion)
}

readCountryIncomeGroup <- function(){
  countryIncomeGroup <- read.csv(here("./1_Data/WorldBankIncomeGroup2020.csv"))
  
  countryIncomeGroup <- countryIncomeGroup %>% 
    select("Code", "Region", "Income.group")
  
  names(countryIncomeGroup)[names(countryIncomeGroup) == 'Region'] <- 'World Bank Region'
  
  return(countryIncomeGroup)
  
}

renameCountryCodeForKosovo <- function(countryIncomeGroup){
  
  countryIncomeGroup[countryIncomeGroup == "XKX"] <- "XKO"
  
  return(countryIncomeGroup)
  
}
  

readAndRenameCountryIncomeGroup <- function(){
  countryIncomeGroup <- read.csv(here("./1_Data/WorldBankIncomeGroup2020.csv"))
  
  countryIncomeGroup[countryIncomeGroup == "XKX"] <- "XKO"

  countryIncomeGroup <- countryIncomeGroup %>% 
  select("Code", "Region", "Income.group")

  names(countryIncomeGroup)[names(countryIncomeGroup) == 'Region'] <- 'World Bank Region'

return(countryIncomeGroup)

}

read_feature_list <- function(path, feature_col = "representative_variables") {
  
  x <- read_csv(path, show_col_types = FALSE)
  
  x[[feature_col]] %>%
    as.character() %>%
    na.omit() %>%
    unique()
}




addMissingIncomeGroups <- function(df){
  library(plyr)
  df$Income.group <- revalue(df$GID_0,
                             c("ALA"="High income",
                               "ATF"= "High income",
                               "BES" = "High income",
                               "ESH" = "Unknown",
                               "GGY" = "High income",
                               "JEY" = "High income",
                               "MSR" = "High income",
                               "MTQ"= "High income",
                               "MYT"= "High income",
                               "REU"= "High income",
                               "SHN"= "High income",
                               "SJM"= "High income",
                               "TKL"= "High income",
                               "UMI"= "High income",
                               "WLF"= "High income",
                               "XAD"= "High income",
                               "XNC"= "High income"
                               ))

  detach("package:plyr", unload = TRUE)
  return(df)
}
renameUNRegionForKosovo <- function(df){
  df$UNSubRegionName[df$NAME_0 == "Kosovo"] <- "Southern Europe"
  df$UNRegionName[df$NAME_0 == "Kosovo"] <- "Europe"
  df$UNSubRegionCode[df$NAME_0 == "Kosovo"] <- 39
  df$UNRegionCode[df$NAME_0 == "Kosovo"] <- 150

return(df)
}

clean_name <- function(x) {
  x %>%
    as.character() %>%
    stringi::stri_trans_general("Latin-ASCII") %>%
    str_squish() %>%
    str_to_lower() %>%
    str_replace_all("[^a-z0-9]+", " ") %>%
    str_squish()
}


clean_key <- function(x) {
  x %>%
    as.character() %>%
    str_replace_all("_", " ") %>%
    str_trim() %>%
    str_to_lower() %>%
    stringi::stri_trans_general("Latin-ASCII") %>%
    str_replace_all("&", " and ") %>%
    str_replace_all("[^[:alnum:] ]", " ") %>%
    str_squish()
}

normalise_region_key <- function(region, country_wb) {
  map2_chr(clean_key(region), clean_key(country_wb), function(r, cty) {
    if (is.na(r) || is.na(cty)) return(r)
    
    # remove common non-region words
    r <- str_remove(r, "^resto\\s+")
    
    # remove WB country name if accidentally appended/prepended to region
    country_pattern <- str_replace_all(cty, "\\s+", "\\\\s+")
    r <- str_remove(r, paste0("^", country_pattern, "\\s+"))
    r <- str_remove(r, paste0("\\s+", country_pattern, "$"))
    
    str_squish(r)
  })
}


country_match_key <- function(x) {
  x <- clean_name(x)
  
  case_when(
    x %in% c("congo dem rep", "dr congo", "democratic republic of the congo") ~ "democratic republic of the congo",
    x %in% c("guinea bissau") ~ "guinea bissau",
    x %in% c("lao pdr", "lao people s democratic republic") ~ "lao pdr",
    x %in% c("palestina", "west bank and gaza", "palestine") ~ "west bank and gaza",
    x %in% c("sao tome and principe", "sao tome principe") ~ "sao tome and principe",
    x %in% c("cote d ivoire", "c ote d ivoire", "cote divoire", "cote d'ivoire") ~ "cote d ivoire",
    x %in% c("gambia", "gambia the", "the gambia") ~ "gambia",
    x %in% c("viet nam", "vietnam") ~ "viet nam",
    str_detect(x, "^pakistan") ~ "pakistan",
    TRUE ~ x
  )
}

# ============================================================
# Generic joining and crosswalk helper functions
# ============================================================
# These functions are outcome-neutral.
# They can be used for E. coli, improved water source, or later outcomes.


add_missing_columns <- function(df, cols) {
  missing_cols <- setdiff(cols, names(df))
  
  for (col in missing_cols) {
    df[[col]] <- NA
  }
  
  df
}


read_existing_csvs <- function(files, col_types = readr::cols(.default = readr::col_character())) {
  files <- path.expand(files)
  files <- files[file.exists(files)]
  
  if (length(files) == 0) {
    stop("No input files found. Check the file paths.")
  }
  
  purrr::map_dfr(
    files,
    ~ readr::read_csv(.x, col_types = col_types)
  )
}


clean_key <- function(x) {
  x %>%
    as.character() %>%
    stringr::str_replace_all("_", " ") %>%
    stringr::str_trim() %>%
    stringr::str_to_lower() %>%
    stringi::stri_trans_general("Latin-ASCII") %>%
    stringr::str_replace_all("&", " and ") %>%
    stringr::str_replace_all("[^[:alnum:] ]", " ") %>%
    stringr::str_squish()
}


normalise_region_key <- function(region, country_wb) {
  purrr::map2_chr(
    clean_key(region),
    clean_key(country_wb),
    function(r, cty) {
      if (is.na(r) || is.na(cty)) {
        return(r)
      }
      
      # Remove common non-region words.
      r <- stringr::str_remove(r, "^resto\\s+")
      
      # Remove WB country name if it has accidentally been attached
      # to the region name.
      country_pattern <- stringr::str_replace_all(cty, "\\s+", "\\\\s+")
      r <- stringr::str_remove(r, paste0("^", country_pattern, "\\s+"))
      r <- stringr::str_remove(r, paste0("\\s+", country_pattern, "$"))
      
      stringr::str_squish(r)
    }
  )
}



  # Creates one common region column, HH7_region, from the different
  # geography columns used across MICS, DHS, and geospatial files.
  #
  # Pakistan is handled separately because the useful modelling region
  # is often in adm2_name rather than adm1_name.

make_hh7_region_from_geo_columns <- function(df) {
  geo_cols <- c("MICSGEO", "REGNAME", "adm2_name", "adm1_name", "HH7")
  
  df %>%
    add_missing_columns(geo_cols) %>%
    dplyr::mutate(
      dplyr::across(
        dplyr::all_of(geo_cols),
        ~ dplyr::na_if(as.character(.x), "")
      ),
      
      HH7_region = dplyr::if_else(
        country == "Pakistan",
        dplyr::coalesce(MICSGEO, REGNAME, adm2_name, HH7, adm1_name),
        dplyr::coalesce(MICSGEO, REGNAME, HH7, adm1_name, adm2_name)
      )
    )
}

clean_population_covariates <- function(df_pop) {
  df_pop %>%
    make_hh7_region_from_geo_columns() %>%
    dplyr::transmute(
      country = as.character(country),
      analysis_year = as.integer(analysis_year),
      HH7_region = as.character(HH7_region),
      source = as.character(source),
      worldpop_sum = as.numeric(worldpop_sum),
      ghsl_population_sum = as.numeric(ghsl_population_sum)
    ) %>%
    dplyr::filter(!is.na(country), !is.na(analysis_year), !is.na(HH7_region))
}


clean_nonpop_covariates <- function(df_nonpop, covariate_cols) {
  df_nonpop %>%
    make_hh7_region_from_geo_columns() %>%
    dplyr::select(
      country,
      analysis_year,
      HH7_region,
      source,
      dplyr::any_of(covariate_cols)
    ) %>%
    dplyr::mutate(
      country = as.character(country),
      analysis_year = as.integer(analysis_year),
      HH7_region = as.character(HH7_region),
      source = as.character(source)
    ) %>%
    dplyr::filter(!is.na(country), !is.na(analysis_year), !is.na(HH7_region))
}


make_training_covariates <- function(pop_files, nonpop_files, covariate_cols) {
  # Reads population and non-population geospatial covariates,
  # standardises their region names, and joins them into one table.
  
  join_cols <- c("country", "analysis_year", "HH7_region", "source")
  
  df_pop_raw <- read_existing_csvs(pop_files) %>%
    readr::type_convert()
  
  df_nonpop_raw <- read_existing_csvs(nonpop_files) %>%
    readr::type_convert()
  
  df_pop_clean <- clean_population_covariates(df_pop_raw)
  df_nonpop_clean <- clean_nonpop_covariates(df_nonpop_raw, covariate_cols)
  
  df_training_covariates <- df_pop_clean %>%
    dplyr::mutate(dplyr::across(dplyr::all_of(join_cols), as.character)) %>%
    dplyr::left_join(
      df_nonpop_clean %>%
        dplyr::mutate(dplyr::across(dplyr::all_of(join_cols), as.character)),
      by = join_cols
    ) %>%
    dplyr::mutate(
      analysis_year = as.integer(analysis_year)
    )
  
  df_training_covariates
}


check_duplicate_covariate_keys <- function(df_training_covariates) {
  join_cols <- c("country", "analysis_year", "HH7_region", "source")
  
  df_training_covariates %>%
    dplyr::count(dplyr::across(dplyr::all_of(join_cols)), name = "n") %>%
    dplyr::filter(n > 1) %>%
    dplyr::arrange(country, analysis_year, source, HH7_region)
}


build_wb_country_lookup <- function(country_name_key_WB) {
  # Creates a lookup between different country-name spellings and
  # the World Bank country name used for matching.
  
  wb_lookup_base <- dplyr::bind_rows(
    country_name_key_WB %>%
      dplyr::transmute(
        country_alias = Country,
        country_wb = Country
      ),
    
    country_name_key_WB %>%
      dplyr::transmute(
        country_alias = GADM_NAME_0,
        country_wb = Country
      )
  ) %>%
    dplyr::filter(!is.na(country_alias), !is.na(country_wb)) %>%
    dplyr::mutate(country_alias_key = clean_key(country_alias)) %>%
    dplyr::distinct(country_alias_key, country_wb)
  
  wb_lookup_manual <- tibble::tribble(
    ~country_alias,                     ~country_wb,
    "Republic of North Macedonia",      "North Macedonia",
    "DR Congo",                         "Congo, Dem. Rep.",
    "Democratic Republic of the Congo", "Congo, Dem. Rep.",
    "Lao People's Democratic Republic", "Lao PDR",
    "Laos",                             "Lao PDR",
    "Palestina",                        "West Bank and Gaza",
    "Palestine",                        "West Bank and Gaza",
    "Vietnam",                          "Viet Nam",
    "Gambia",                           "Gambia, The",
    "The Gambia",                       "Gambia, The",
    "Pakistan Balochistan",             "Pakistan",
    "Pakistan Khyber Pakhtunkhwa",      "Pakistan",
    "Pakistan Punjab",                  "Pakistan",
    "Sao Tome and Principe",            "Sao Tome and Principe",
    "São Tomé and Príncipe",            "Sao Tome and Principe",
    "Guyana",                           "Guyana",
    "Costa Rica",                       "Costa Rica",
    "Nauru",                            "Nauru",
    "Trinidad and Tobago",              "Trinidad and Tobago"
  ) %>%
    dplyr::mutate(country_alias_key = clean_key(country_alias)) %>%
    dplyr::select(country_alias_key, country_wb)
  
  dplyr::bind_rows(wb_lookup_base, wb_lookup_manual) %>%
    dplyr::distinct(country_alias_key, .keep_all = TRUE)
}


# Filter covariates to country-year pairs present in the outcome


filter_covariates_to_outcome_years <- function(
    outcome_df,
    df_training_covariates,
    country_name_key_WB
) {
  wb_lookup <- build_wb_country_lookup(country_name_key_WB)
  
  outcome_country_years <- outcome_df %>%
    dplyr::transmute(
      country_alias_key = clean_key(country_outcome),
      analysis_year = as.integer(analysis_year)
    ) %>%
    dplyr::left_join(wb_lookup, by = "country_alias_key") %>%
    dplyr::filter(!is.na(country_wb), !is.na(analysis_year)) %>%
    dplyr::distinct(country_wb, analysis_year)
  
  df_training_covariates %>%
    dplyr::mutate(
      country_alias_key = clean_key(country),
      analysis_year = as.integer(analysis_year)
    ) %>%
    dplyr::left_join(wb_lookup, by = "country_alias_key") %>%
    dplyr::semi_join(
      outcome_country_years,
      by = c("country_wb", "analysis_year")
    ) %>%
    dplyr::select(-country_alias_key, -country_wb)
}


check_duplicate_covariate_join_keys <- function(df_training_covariates) {
  df_training_covariates %>%
    dplyr::count(
      country,
      analysis_year,
      HH7_region,
      name = "n"
    ) %>%
    dplyr::filter(n > 1) %>%
    dplyr::arrange(country, analysis_year, HH7_region)
}

prepare_crosswalk_region_tables <- function(outcome_df, df_training_covariates, country_name_key_WB) {
  wb_lookup <- build_wb_country_lookup(country_name_key_WB)
  
  cov_regions <- df_training_covariates %>%
    dplyr::distinct(country, HH7_region) %>%
    dplyr::transmute(
      country_cov = country,
      HH7_region_cov = HH7_region,
      country_alias_key = clean_key(country)
    ) %>%
    dplyr::left_join(wb_lookup, by = "country_alias_key") %>%
    dplyr::mutate(
      region_key = normalise_region_key(HH7_region_cov, country_wb)
    ) %>%
    dplyr::distinct()
  
  out_regions <- outcome_df %>%
    dplyr::distinct(country_outcome, HH7_region_outcome) %>%
    dplyr::transmute(
      country_outcome,
      HH7_region_outcome,
      country_alias_key = clean_key(country_outcome)
    ) %>%
    dplyr::left_join(wb_lookup, by = "country_alias_key") %>%
    dplyr::mutate(
      region_key = normalise_region_key(HH7_region_outcome, country_wb)
    ) %>%
    dplyr::distinct()
  
  list(
    cov_regions = cov_regions,
    out_regions = out_regions
  )
}


build_region_crosswalk <- function(
    outcome_df,
    df_training_covariates,
    country_name_key_WB,
    fuzzy_max_dist = 0.45
) {
  
  # Builds a region crosswalk from outcome regions to covariate regions.
  #
  # Step 1: map countries to common World Bank names.
  # Step 2: clean region names.
  # Step 3: exact match by country + cleaned region name.
  # Step 4: fuzzy match remaining regions within the same country.
  #
  # Manual overrides are intentionally not included here. Add them after
  # reviewing the exported review table.
  
  region_tables <- prepare_crosswalk_region_tables(
    outcome_df = outcome_df,
    df_training_covariates = df_training_covariates,
    country_name_key_WB = country_name_key_WB
  )
  
  cov_regions <- region_tables$cov_regions
  out_regions <- region_tables$out_regions
  
  cov_countries_not_mapped <- cov_regions %>%
    dplyr::filter(is.na(country_wb)) %>%
    dplyr::distinct(country_cov) %>%
    dplyr::arrange(country_cov)
  
  outcome_countries_not_mapped <- out_regions %>%
    dplyr::filter(is.na(country_wb)) %>%
    dplyr::distinct(country_outcome) %>%
    dplyr::arrange(country_outcome)
  
  exact_crosswalk <- out_regions %>%
    dplyr::filter(!is.na(country_wb)) %>%
    dplyr::inner_join(
      cov_regions %>% dplyr::filter(!is.na(country_wb)),
      by = c("country_wb", "region_key")
    ) %>%
    dplyr::transmute(
      country_wb,
      country_outcome,
      HH7_region_outcome,
      country_cov,
      HH7_region_cov,
      dist = 0,
      match_type = "exact"
    ) %>%
    dplyr::distinct()
  
  unmatched_after_exact <- out_regions %>%
    dplyr::filter(!is.na(country_wb)) %>%
    dplyr::anti_join(
      exact_crosswalk %>%
        dplyr::distinct(country_outcome, HH7_region_outcome),
      by = c("country_outcome", "HH7_region_outcome")
    )
  
  if (nrow(unmatched_after_exact) == 0) {
    fuzzy_crosswalk <- tibble::tibble(
      country_wb = character(),
      country_outcome = character(),
      HH7_region_outcome = character(),
      country_cov = character(),
      HH7_region_cov = character(),
      dist = numeric(),
      match_type = character(),
      n_best_candidates = integer()
    )
  } else {
    fuzzy_crosswalk <- purrr::map_dfr(
      sort(unique(unmatched_after_exact$country_wb)),
      function(cty) {
        out_cty <- unmatched_after_exact %>%
          dplyr::filter(country_wb == cty)
        
        cov_cty <- cov_regions %>%
          dplyr::filter(country_wb == cty) %>%
          dplyr::select(country_cov, HH7_region_cov, region_key)
        
        if (nrow(cov_cty) == 0) {
          return(
            out_cty %>%
              dplyr::transmute(
                country_wb,
                country_outcome,
                HH7_region_outcome,
                country_cov = NA_character_,
                HH7_region_cov = NA_character_,
                dist = NA_real_,
                match_type = "no_covariate_country_match",
                n_best_candidates = NA_integer_
              )
          )
        }
        
        fuzzyjoin::stringdist_left_join(
          out_cty,
          cov_cty,
          by = "region_key",
          method = "jw",
          max_dist = fuzzy_max_dist,
          distance_col = "dist"
        ) %>%
          dplyr::mutate(
            dist_order = dplyr::if_else(is.na(dist), Inf, dist)
          ) %>%
          dplyr::group_by(country_wb, country_outcome, HH7_region_outcome) %>%
          dplyr::slice_min(dist_order, n = 1, with_ties = TRUE) %>%
          dplyr::mutate(
            n_best_candidates = dplyr::n()
          ) %>%
          dplyr::ungroup() %>%
          dplyr::mutate(
            match_type = dplyr::case_when(
              is.na(HH7_region_cov) ~ "no_region_candidate_within_threshold",
              dist <= 0.10 ~ "strong_fuzzy",
              dist <= 0.20 ~ "review_fuzzy",
              TRUE ~ "weak_fuzzy"
            )
          ) %>%
          dplyr::select(
            country_wb,
            country_outcome,
            HH7_region_outcome,
            country_cov,
            HH7_region_cov,
            dist,
            match_type,
            n_best_candidates
          )
      }
    )
  }
  
  region_crosswalk <- dplyr::bind_rows(
    exact_crosswalk %>%
      dplyr::mutate(n_best_candidates = 1L),
    fuzzy_crosswalk
  ) %>%
    dplyr::arrange(country_wb, country_outcome, HH7_region_outcome, dist)
  
  regions_to_review <- region_crosswalk %>%
    dplyr::filter(match_type != "exact") %>%
    dplyr::arrange(country_wb, match_type, dplyr::desc(is.na(dist)), dist)
  
  list(
    region_crosswalk = region_crosswalk,
    regions_to_review = regions_to_review,
    cov_regions = cov_regions,
    out_regions = out_regions,
    cov_countries_not_mapped = cov_countries_not_mapped,
    outcome_countries_not_mapped = outcome_countries_not_mapped
  )
}


apply_manual_region_fixes <- function(
    region_crosswalk,
    manual_region_fixes,
    cov_regions,
    out_regions
) {
  
  # Use this after manually reviewing regions_to_review.
  #
  # manual_region_fixes must have:
  #   HH7_region_outcome
  #   country_cov
  #   correct_region_name
  
  if (nrow(manual_region_fixes) == 0) {
    return(region_crosswalk)
  }
  
  manual_region_fixes <- manual_region_fixes %>%
    dplyr::mutate(
      outcome_region_key = clean_key(HH7_region_outcome),
      country_cov_key = clean_key(country_cov),
      correct_region_key = clean_key(correct_region_name)
    )
  
  cov_lookup_for_manual_fixes <- cov_regions %>%
    dplyr::mutate(
      country_cov_key = clean_key(country_cov),
      cov_region_key = clean_key(HH7_region_cov)
    ) %>%
    dplyr::select(
      country_wb,
      country_cov,
      HH7_region_cov,
      country_cov_key,
      cov_region_key
    )
  
  out_lookup_for_manual_fixes <- out_regions %>%
    dplyr::mutate(
      outcome_region_key = clean_key(HH7_region_outcome)
    ) %>%
    dplyr::select(
      country_wb,
      country_outcome,
      HH7_region_outcome,
      outcome_region_key
    )
  
  manual_crosswalk <- manual_region_fixes %>%
    dplyr::left_join(
      cov_lookup_for_manual_fixes,
      by = c(
        "country_cov_key",
        "correct_region_key" = "cov_region_key"
      )
    ) %>%
    dplyr::left_join(
      out_lookup_for_manual_fixes,
      by = c(
        "country_wb",
        "outcome_region_key"
      )
    ) %>%
    dplyr::transmute(
      country_wb,
      country_outcome,
      HH7_region_outcome = dplyr::coalesce(HH7_region_outcome.y, HH7_region_outcome.x),
      country_cov = dplyr::coalesce(country_cov.y, country_cov.x),
      HH7_region_cov,
      dist = 0,
      match_type = "manual_override",
      n_best_candidates = 1L
    )
  
  region_crosswalk %>%
    dplyr::anti_join(
      manual_crosswalk %>%
        dplyr::distinct(country_wb, country_outcome, HH7_region_outcome),
      by = c("country_wb", "country_outcome", "HH7_region_outcome")
    ) %>%
    dplyr::bind_rows(manual_crosswalk) %>%
    dplyr::arrange(country_wb, country_outcome, HH7_region_outcome, dist)
}


join_outcome_to_covariates <- function(
    outcome_df,
    df_training_covariates,
    region_crosswalk,
    drop_missing_worldpop = TRUE
) {
  # Joins a standardised regional outcome table to the geospatial
  # covariates using:
  #   outcome region -> crosswalk -> covariate region -> covariates
  
  crosswalk_best <- region_crosswalk %>%
    dplyr::filter(!is.na(country_cov), !is.na(HH7_region_cov)) %>%
    dplyr::mutate(
      match_priority = dplyr::case_when(
        match_type == "exact" ~ 1L,
        match_type == "manual_override" ~ 1L,
        match_type == "strong_fuzzy" ~ 2L,
        match_type == "review_fuzzy" ~ 3L,
        match_type == "weak_fuzzy" ~ 4L,
        TRUE ~ 5L
      )
    ) %>%
    dplyr::arrange(match_priority, dist) %>%
    dplyr::group_by(country_outcome, HH7_region_outcome) %>%
    dplyr::slice(1) %>%
    dplyr::ungroup() %>%
    dplyr::select(
      country_outcome,
      HH7_region_outcome,
      country_cov,
      HH7_region_cov,
      match_type,
      dist
    )
  
  out <- outcome_df %>%
    dplyr::left_join(
      crosswalk_best,
      by = c("country_outcome", "HH7_region_outcome")
    ) %>%
    dplyr::left_join(
      df_training_covariates %>%
        dplyr::rename(
          country_cov = country,
          HH7_region_cov = HH7_region,
          covariate_source = source
        ) %>%
        dplyr::mutate(
          analysis_year = as.integer(analysis_year)
        ),
      by = c("country_cov", "HH7_region_cov", "analysis_year")
    ) %>%
    dplyr::distinct()
  
  if (drop_missing_worldpop) {
    out <- out %>%
      tidyr::drop_na(country_outcome, HH7_region_outcome, analysis_year, worldpop_sum)
  }
  
  out
}


# ============================================================
#  helpers for joining subcomponent outcomes
# ============================================================


build_crosswalk_for_one_outcome <- function(
    outcome_name,
    outcome_df,
    df_training_covariates,
    country_name_key_WB,
    output_dir = here::here("./outputs/01_matching_regions/crosswalk_review")
) {
  # Builds and exports an initial crosswalk and a review file for one outcome.
  # Manual corrections are added later.
  
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  
  crosswalk_results <- build_region_crosswalk(
    outcome_df = outcome_df,
    df_training_covariates = df_training_covariates,
    country_name_key_WB = country_name_key_WB
  )
  
  readr::write_csv(
    crosswalk_results$region_crosswalk,
    file.path(output_dir, paste0(outcome_name, "_region_crosswalk_initial.csv"))
  )
  
  readr::write_csv(
    crosswalk_results$regions_to_review,
    file.path(output_dir, paste0(outcome_name, "_region_crosswalk_review_needed.csv"))
  )
  
  crosswalk_results
}


apply_manual_fixes_for_one_outcome <- function(
    outcome_name,
    crosswalk_results,
    manual_region_fixes,
    output_dir = here::here("./data/crosswalk_review")
) {
  # Applies manual corrections after you have reviewed the crosswalk file.
  # For now, manual_region_fixes can be an empty tibble.
  
  region_crosswalk_final <- apply_manual_region_fixes(
    region_crosswalk = crosswalk_results$region_crosswalk,
    manual_region_fixes = manual_region_fixes,
    cov_regions = crosswalk_results$cov_regions,
    out_regions = crosswalk_results$out_regions
  )
  
  readr::write_csv(
    region_crosswalk_final,
    file.path(output_dir, paste0(outcome_name, "_region_crosswalk_final.csv"))
  )
  
  region_crosswalk_final
}


join_and_save_one_training_dataset <- function(
    outcome_name,
    outcome_df,
    df_training_covariates,
    region_crosswalk_final,
    output_dir = here::here("./data/training_subcomponents")
) {
  # Joins one outcome to the geospatial covariates and saves:
  #   1. the final model-ready training CSV
  #   2. a diagnostic file showing regions that did not get covariates
  
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  
  training_with_covariates_check <- join_outcome_to_covariates(
    outcome_df = outcome_df,
    df_training_covariates = df_training_covariates,
    region_crosswalk = region_crosswalk_final,
    drop_missing_worldpop = FALSE
  )
  
  missing_covariates <- training_with_covariates_check %>%
    dplyr::filter(is.na(worldpop_sum)) %>%
    dplyr::select(
      outcome_type,
      country_outcome,
      HH7_region_outcome,
      analysis_year,
      country_cov,
      HH7_region_cov,
      match_type,
      dist
    ) %>%
    dplyr::arrange(country_outcome, HH7_region_outcome)
  
  training_with_covariates <- training_with_covariates_check %>%
    tidyr::drop_na(
      country_outcome,
      HH7_region_outcome,
      analysis_year,
      worldpop_sum
    ) %>%
    dplyr::arrange(
      outcome_type,
      country_outcome,
      analysis_year,
      HH7_region_outcome,
      match_type,
      dist
    ) %>%
    dplyr::distinct(
      outcome_type,
      country_outcome,
      analysis_year,
      HH7_region_outcome,
      outcome_value,
      .keep_all = TRUE
    )
  
  readr::write_csv(
    training_with_covariates,
    file.path(output_dir, paste0(outcome_name, "_training_with_covariates.csv"))
  )
  
  readr::write_csv(
    missing_covariates,
    file.path(output_dir, paste0(outcome_name, "_missing_covariates_after_join.csv"))
  )
  
  list(
    training_with_covariates = training_with_covariates,
    missing_covariates = missing_covariates
  )
}


summarise_training_dataset <- function(training_df) {
  training_df %>%
    dplyr::summarise(
      outcome_type = dplyr::first(outcome_type),
      n_rows = dplyr::n(),
      n_countries = dplyr::n_distinct(country_outcome),
      n_regions = dplyr::n_distinct(paste(country_outcome, HH7_region_outcome)),
      min_year = min(analysis_year, na.rm = TRUE),
      max_year = max(analysis_year, na.rm = TRUE)
    )
}


# ============================================================
# Standardise country names for GDP join
# ============================================================

standardise_country_for_gdp_join <- function(x) {
  x_clean <- clean_key(x)
  
  dplyr::case_when(
    x_clean %in% c("cote d ivoire", "cote divoire") ~ "Cote d'Ivoire",
    x_clean %in% c("dr congo", "democratic republic of the congo") ~ "Congo, Dem. Rep.",
    x_clean %in% c("gambia", "the gambia", "gambia the") ~ "Gambia, The",
    x_clean %in% c("guinea bissau") ~ "Guinea-Bissau",
    x_clean %in% c("lao people s democratic republic", "lao pdr", "laos") ~ "Lao PDR",
    stringr::str_detect(x_clean, "^pakistan") ~ "Pakistan",
    x_clean %in% c("palestina", "palestine", "west bank and gaza") ~ "West Bank and Gaza",
    x_clean %in% c("sao tome and principe", "sao tome principe") ~ "Sao Tome and Principe",
    x_clean %in% c("vietnam", "viet nam") ~ "Viet Nam",
    TRUE ~ as.character(x)
  )
}

# ============================================================
# Standardise household survey years
# ============================================================

standardise_survey_year <- function(country, HH5Y) {
  HH5Y <- suppressWarnings(as.integer(HH5Y))
  
  dplyr::case_when(
    # --------------------------------------------------------
    # Different calendar systems
    # --------------------------------------------------------
    
    # Afghanistan: Solar Hijri calendar
    # 1394 -> 2015, 1401 -> 2022
    country == "Afghanistan" & HH5Y >= 1300 & HH5Y < 1500 ~ HH5Y + 621L,
    
    # Nepal: Bikram Sambat calendar / manual survey-year correction
    # 2078 -> 2021, 2079 -> 2022, 2081 -> 2024
    # Keep your existing manual correction: 2082 -> 2024
    country == "Nepal" & HH5Y == 2078 ~ 2021L,
    country == "Nepal" & HH5Y == 2079 ~ 2022L,
    country == "Nepal" & HH5Y == 2081 ~ 2024L,
    country == "Nepal" & HH5Y == 2082 ~ 2024L,
    
    # Thailand: Buddhist Era calendar
    # 2565 -> 2022
    country == "Thailand" & HH5Y >= 2400 & HH5Y < 2700 ~ HH5Y - 543L,
    
    # --------------------------------------------------------
    # Manual correction based on sampled covariate year
    # --------------------------------------------------------
    country == "Ethiopia" & HH5Y == 2011 ~ 2019L,
    country == "Zimbabwe" & HH5Y == 2018 ~ 2019L,
    country == "Myanmar" & HH5Y == 2015 ~ 2016L,
    country == "Armenia" & HH5Y == 2015 ~ 2016L,
    country == "Pakistan Khyber Pakhtunkhwa" & HH5Y == 2019 ~ 2018L,
    country == "Pakistan Balochistan" & HH5Y == 2019 ~ 2018L,
    country == "Pakistan Punjab" & HH5Y == 2017 ~ 2018L,
    country == "India" & HH5Y == 2019 ~ 2020L,
    country == "Mauritania" & HH5Y == 2019 ~ 2020L,
    country == "Nigeria" & HH5Y == 2023 ~ 2024L,
    
    TRUE ~ HH5Y
  )
}

# ============================================================
# Create analysis-year lookup before outcome-specific variables
# are selected
# ============================================================
#
# Some original outcome functions drop HH5Y because they were written
# before analysis_year was needed for joining to covariates.
#
# This helper creates one analysis year per country from the raw household
# data before HH5Y is removed.

make_year_lookup_from_raw_household_data <- function(
    df,
    manual_analysis_year_fixes = tibble::tibble(
      country = character(),
      analysis_year_manual = integer()
    )
) {
  
  if (!"country" %in% names(df)) {
    stop("Column 'country' is missing from the household data.")
  }
  
  if (!"HH5Y" %in% names(df)) {
    stop(
      "Column 'HH5Y' is missing from the household data. ",
      "Check whether the survey year column has a different name."
    )
  }
  
  df %>%
    harmonise_household_country_names_for_modelling() %>%
    dplyr::group_by(country) %>%
    dplyr::summarise(
      raw_years = paste(sort(unique(HH5Y)), collapse = ", "),
      analysis_year = min(HH5Y, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    dplyr::mutate(
      analysis_year = dplyr::if_else(
        is.infinite(analysis_year),
        NA_integer_,
        as.integer(analysis_year)
      )
    ) %>%
    dplyr::left_join(
      manual_analysis_year_fixes,
      by = "country"
    ) %>%
    dplyr::mutate(
      analysis_year = dplyr::coalesce(
        as.integer(analysis_year_manual),
        as.integer(analysis_year)
      )
    ) %>%
    dplyr::select(
      country,
      analysis_year
    )
}

standardise_regional_outcome_table <- function(
    outcome_df,
    outcome_type,
    outcome_value_col,
    year_lookup
) {
  # Converts the output from each original regional indicator function
  # into one shared format for crosswalk creation and covariate joining.
  
  outcome_df %>%
    dplyr::rename(
      country_outcome = country.x,
      HH7_region_outcome = HH7_region,
      n_households = HouseholdsInRegion.Freq.x
    ) %>%
    dplyr::left_join(
      year_lookup,
      by = c("country_outcome" = "country")
    ) %>%
    dplyr::mutate(
      outcome_type = outcome_type,
      outcome_value = as.numeric(.data[[outcome_value_col]])
    ) %>%
    dplyr::select(
      outcome_type,
      country_outcome,
      HH7_region_outcome,
      analysis_year,
      outcome_value,
      n_households,
      dplyr::everything()
    )
}


