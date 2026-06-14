# title: "Functions for extracting Sanitation Variables from MICS data"
# Variables extracted: HH1, HH2, WS11 (toilet type), WS15 (shared facility),
#   HH6 (urban/rural), HH7 (region), HH48, HH5D/M/Y (interview date),
#   PSU, stratum, hhweight, country
#
# Known alternative variable names across MICS rounds:
#   WS11 (toilet type)  <- WS8  in Nigeria MICS4, Paraguay MICS4
#                       <- WS9  in some MICS3/early surveys
#                       <- TT   in a small number of pre-MICS4 datasets
#   WS15 (shared fac.)  <- WS9  in Nigeria MICS4, Paraguay MICS4
#                       <- WS10 in some MICS3/early surveys
#   DHS equivalents:    hv205 (toilet type), hv225 (shared toilet)
#
# Notes:
#   - wqsweight is NOT included (no water quality module for sanitation surveys)
#   - Rename WS8->WS11 and WS9->WS15 BEFORE calling extract functions for
#     surveys with non-standard naming (see compile script for examples)

# ── Load all .sav files from a directory into the global environment ──────────
loadSurveys <- function(pathToSurveys) {
  filenames <- list.files(path = pathToSurveys, full.names = FALSE)
  for (filename in filenames) {
    name <- strsplit(filename, split = ".", fixed = TRUE)[[1]][1]
    dfCountrySurvey <- sjlabelled::read_spss(paste(pathToSurveys, "/", filename, sep = ""))
    assign(name, dfCountrySurvey, envir = .GlobalEnv)
  }
}

# ── Standard extraction (PSU uppercase, stratum lowercase) ────────────────────
extractStandardSurveyVariables_sanitation <- function(hh_Survey) {
  hh_Survey <- hh_Survey %>%
    select("HH1", "HH2", "WS11", "WS15",
           "HH7", "HH6", "HH48",
           "hhweight",
           "country",
           "HH5D", "HH5M", "HH5Y",
           "PSU", "stratum")
  return(hh_Survey)
}


# ── psu lowercase variant ─────────────────────────────────────────────────────
extractStandardSurveyVariables_sanitation_psu_lowercaps <- function(hh_Survey) {
  hh_Survey <- hh_Survey %>%
    select("HH1", "HH2", "WS11", "WS15",
           "HH7", "HH6", "HH48",
           "hhweight",
           "country",
           "HH5D", "HH5M", "HH5Y",
           "psu", "stratum")
  names(hh_Survey)[names(hh_Survey) == "psu"] <- "PSU"
  return(hh_Survey)
}

# ── strata (plural) variant ───────────────────────────────────────────────────
extractStandardSurveyVariables_sanitation_strata <- function(hh_Survey) {
  hh_Survey <- hh_Survey %>%
    select("HH1", "HH2", "WS11", "WS15",
           "HH7", "HH6", "HH48",
           "hhweight",
           "country",
           "HH5D", "HH5M", "HH5Y",
           "PSU", "strata")
  names(hh_Survey)[names(hh_Survey) == "strata"] <- "stratum"
  return(hh_Survey)
}

# ── stratum_SE variant (e.g. Lao PDR 2023) ───────────────────────────────────
extractStandardSurveyVariables_sanitation_stratum_SE <- function(hh_Survey) {
  hh_Survey <- hh_Survey %>%
    select("HH1", "HH2", "WS11", "WS15",
           "HH7", "HH6", "HH48",
           "hhweight",
           "country",
           "HH5D", "HH5M", "HH5Y",
           "PSU", "stratum_SE")
  names(hh_Survey)[names(hh_Survey) == "stratum_SE"] <- "stratum"
  return(hh_Survey)
}

# ── Stratum uppercase variant (e.g. Kazakhstan, Turkmenistan) ─────────────────
extractStandardSurveyVariables_sanitation_Stratum <- function(hh_Survey) {
  hh_Survey <- hh_Survey %>%
    select("HH1", "HH2", "WS11", "WS15",
           "HH7", "HH6", "HH48",
           "hhweight",
           "country",
           "HH5D", "HH5M", "HH5Y",
           "PSU", "Stratum")
  names(hh_Survey)[names(hh_Survey) == "Stratum"] <- "stratum"   # ← add this line
  return(hh_Survey)
}

# ── No HH6 variant (e.g. Nauru) ──────────────────────────────────────────────
extractStandardSurveyVariables_sanitation_withoutHH6 <- function(hh_Survey) {
  hh_Survey <- hh_Survey %>%
    select("HH1", "HH2", "WS11", "WS15",
           "HH7", "HH48",
           "hhweight",
           "country",
           "HH5D", "HH5M", "HH5Y",
           "PSU", "stratum")
  hh_Survey$HH6 <- NA
  return(hh_Survey)
}

# ── No HH6 + psu lowercase ────────────────────────────────────────────────────
extractStandardSurveyVariables_sanitation_withoutHH6_psu <- function(hh_Survey) {
  hh_Survey <- hh_Survey %>%
    select("HH1", "HH2", "WS11", "WS15",
           "HH7", "HH48",
           "hhweight",
           "country",
           "HH5D", "HH5M", "HH5Y",
           "psu", "stratum")
  names(hh_Survey)[names(hh_Survey) == "psu"] <- "PSU"
  hh_Survey$HH6 <- NA
  return(hh_Survey)
}

# ── psu lowercase + no Stratum (e.g. Montenegro, Pakistan Sindh) ──────────────
extractStandardSurveyVariables_sanitation_psu <- function(hh_Survey) {
  hh_Survey <- hh_Survey %>%
    select("HH1", "HH2", "WS11", "WS15",
           "HH7", "HH6", "HH48",
           "hhweight",
           "country",
           "HH5D", "HH5M", "HH5Y",
           "psu", "stratum")
  names(hh_Survey)[names(hh_Survey) == "psu"] <- "PSU"   # ← add this line
  return(hh_Survey)
}

# ── Country-specific extractors ───────────────────────────────────────────────

# Nigeria MICS4: toilet type = WS8, shared = WS9
extractVariablesFromNigeria_sanitation <- function(hh_Nigeria) {
  hh_Nigeria_san <- hh_Nigeria %>%
    select("HH1", "HH2", "WS8", "WS9",
           "HH7", "HH6", "HH11",
           "hhweight",
           "country",
           "HH5D", "HH5M", "HH5Y",
           "PSU", "stratum")
  names(hh_Nigeria_san)[names(hh_Nigeria_san) == "WS8"]  <- "WS11"
  names(hh_Nigeria_san)[names(hh_Nigeria_san) == "WS9"]  <- "WS15"
  names(hh_Nigeria_san)[names(hh_Nigeria_san) == "HH11"]   <- "HH48"
  return(hh_Nigeria_san)
}

# Paraguay MICS4: toilet type = WS8, shared = WS9; also psu/strata2
extractVariablesFromParaguay_sanitation <- function(hh_Paraguay) {
  hh_Paraguay_san <- hh_Paraguay %>%
    mutate(psu = HH1) %>%
    select("HH1", "HH2", "WS8", "WS9",
           "HH7", "HH6", "HH11",
           "hhweight",
           "country",
           "HH5D", "HH5M", "HH5Y",
           "psu", "strata2")
  names(hh_Paraguay_san)[names(hh_Paraguay_san) == "WS8"]    <- "WS11"
  names(hh_Paraguay_san)[names(hh_Paraguay_san) == "WS9"]    <- "WS15"
  names(hh_Paraguay_san)[names(hh_Paraguay_san) == "psu"]    <- "PSU"
  names(hh_Paraguay_san)[names(hh_Paraguay_san) == "strata2"] <- "stratum"
  names(hh_Paraguay_san)[names(hh_Paraguay_san) == "HH11"]   <- "HH48"
  return(hh_Paraguay_san)
}

# Bangladesh MICS (HH7A variant)
extractVariablesFromBangladesh_sanitation <- function(hh_Bangladesh) {
  hh_Bangladesh_san <- hh_Bangladesh %>%
    select("HH1", "HH2", "WS11", "WS15",
           "HH7", "HH6", "HH48",
           "hhweight",
           "country",
           "HH5D", "HH5M", "HH5Y",
           "PSU", "stratum")
  return(hh_Bangladesh_san)
}

# Lesotho MICS (HH7A, psu lowercase)
extractVariablesFromLesotho_sanitation <- function(hh_Lesotho) {
  hh_Lesotho_san <- hh_Lesotho %>%
    select("HH1", "HH2", "WS11", "WS15",
           "HH6", "HH7A", "HH48",
           "hhweight",
           "country",
           "HH5D", "HH5M", "HH5Y",
           "psu", "stratum")
  names(hh_Lesotho_san)[names(hh_Lesotho_san) == "psu"]  <- "PSU"
  names(hh_Lesotho_san)[names(hh_Lesotho_san) == "HH7A"] <- "HH7"
  return(hh_Lesotho_san)
}

# Sierra Leone MICS (HH7A, PSU derived from HH1)
extractVariablesFromSierraLeone_sanitation <- function(hh_SierraLeone) {
  hh_SierraLeone_san <- hh_SierraLeone %>%
    mutate(PSU = HH1) %>%
    select("HH1", "HH2", "WS11", "WS15",
           "HH7A", "HH6", "HH48",
           "hhweight",
           "country",
           "HH5D", "HH5M", "HH5Y",
           "PSU", "stratum")
  names(hh_SierraLeone_san)[names(hh_SierraLeone_san) == "HH7A"] <- "HH7"
  return(hh_SierraLeone_san)
}

# Tuvalu (PSU_SE)
extractVariablesFromTuvalu_sanitation <- function(hh_Tuvalu) {
  hh_Tuvalu_san <- hh_Tuvalu %>%
    select("HH1", "HH2", "WS11", "WS15",
           "HH7", "HH6", "HH48",
           "hhweight",
           "country",
           "HH5D", "HH5M", "HH5Y",
           "PSU_SE", "stratum")
  names(hh_Tuvalu_san)[names(hh_Tuvalu_san) == "PSU_SE"] <- "PSU"
  return(hh_Tuvalu_san)
}

# ── Region-label helpers (reused from SMDW workflow) ─────────────────────────
extractVariableLabelsfromHH7 <- function(df) {
  df <- df %>% surveytoolbox::extract_vallab("HH7")
  return(df)
}

replaceHH7LabelsWithRegionNames <- function(df, df_regionNames) {
  df_regionNames <- as.data.frame(df_regionNames)  # force to data frame if list returned
  df_regionNames$id <- as.factor(df_regionNames$id)
  df <- df %>% left_join(df_regionNames, by = c("HH7" = "id"))
  names(df)[names(df) == "HH7.y"] <- "HH7_region"
  df <- df %>% select(-"HH7")
  return(df)
}

# ── Factor-to-character conversion for variables that cause NA on rbind ───────
VariablesWhichWereFactorsAsCharacterToAvoidGenerationOfNA_sanitation <- function(df) {
  df$HH6  <- as.character(df$HH6)
  df$WS11 <- as.character(df$WS11)
  df$WS15 <- as.character(df$WS15)
  return(df)
}
