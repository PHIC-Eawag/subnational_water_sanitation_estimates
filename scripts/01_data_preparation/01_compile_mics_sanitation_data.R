# title: "Compiling and Labeling MICS Household Survey Data – Basic Sanitation & Open Defecation"
#
# Output: df_sanitation_MICS_v1.csv
#
# Key variables:
#   WS11            – toilet type: 2 = improved, 1 = unimproved (not OD), 0 = open defecation
#   WS11_category   – factor: "improved" / "unimproved" / "open_defecation"
#   WS11_improved   – binary: 1 = improved facility
#   open_defecation – binary: 1 = open defecation
#   WS15            – shared facility: 1 = shared, 0 = not shared, -99 = missing

library(foreign)
library(tidyr)
library(dplyr)
library(tidyverse)
library(haven)
library(surveytoolbox)
library(survey)

source(here::here("functions/label_mics_sanitation_variables.R"))
source(here::here("functions/extract_mics_sanitation_variables.R"))
source(here::here("configuration/paths.R"))


# 1. LOAD RAW SURVEYS
loadSurveys(PATH_TO_SURVEYS_old_SMDW)
loadSurveys(PATH_TO_SURVEYS_new_SMDW)
loadSurveys(PATH_TO_SURVEYS_new_other)

# 2. ASSIGN COUNTRY NAMES
hh_Afghanistan$country               <- "Afghanistan"
hh_Algeria$country                   <- "Algeria"
hh_Argentina$country                 <- "Argentina"
hh_Azerbaijan$country                <- "Azerbaijan"
hh_Bangladesh$country                <- "Bangladesh"
hh_Belarus$country                   <- "Belarus"
hh_Benin$country                     <- "Benin"
hh_CentralAfricanRepublic$country    <- "Central African Republic"
hh_Chad$country                      <- "Chad"
hh_Comoros$country                   <- "Comoros"
hh_Costa_Rica$country                <- "Costa Rica"
hh_Cuba$country                      <- "Cuba"
hh_DominicanRepublic$country         <- "Dominican Republic"
hh_DRCongo$country                   <- "DR Congo"
hh_Eswatini$country                  <- "Eswatini"
#hh_Fiji$country                      <- "Fiji"
hh_Gambia$country                    <- "Gambia"
hh_Georgia$country                   <- "Georgia"
hh_Ghana$country                     <- "Ghana"
hh_GuineaBissau$country              <- "Guinea Bissau"
hh_Guyana$country                    <- "Guyana"
hh_Honduras$country                  <- "Honduras"
hh_Iraq$country                      <- "Iraq"
hh_Jamaica$country                   <- "Jamaica"
hh_Kazakhstan$country                <- "Kazakhstan"
hh_Kiribati$country                  <- "Kiribati"
hh_Kosovo$country                    <- "Kosovo"
hh_Kyrgyzstan$country                <- "Kyrgyzstan"
hh_LaoPDR_2023$country               <- "Lao PDR"
hh_Lesotho$country                   <- "Lesotho"
hh_Madagascar$country                <- "Madagascar"
hh_Malawi$country                    <- "Malawi"
hh_Mongolia$country                  <- "Mongolia"
hh_Montenegro$country                <- "Montenegro"
hh_Nauru$country                     <- "Nauru"
hh_Nepal$country                     <- "Nepal"
hh_Nigeria$country                   <- "Nigeria"
hh_Nigeria_new$country               <- "Nigeria"
hh_Pakistan_Sindh$country            <- "Pakistan Sindh"
hh_PakistanBalochistan$country       <- "Pakistan Balochistan"
hh_PakistanKhyberPakhtunkhwa$country <- "Pakistan Khyber Pakhtunkhwa"
hh_PakistanPunjab$country            <- "Pakistan Punjab"
hh_Palestine$country                 <- "West Bank and Gaza"
hh_Paraguay$country                  <- "Paraguay"
hh_Qatar$country                     <- "Qatar"
hh_Republic_of_North_Macedonia$country <- "Republic of North Macedonia"
hh_Samoa$country                     <- "Samoa"
hh_SaoTome$country                   <- "Sao Tome and Principe"
hh_Serbia$country                    <- "Serbia"
hh_SierraLeone$country               <- "Sierra Leone"
hh_Suriname$country                  <- "Suriname"
hh_Thailand$country                  <- "Thailand"
hh_Togo$country                      <- "Togo"
hh_Tonga$country                     <- "Tonga"
hh_Trinidad_and_Tobago$country       <- "Trinidad and Tobago"
hh_Tunisia$country                   <- "Tunisia"
hh_Turkmenistan$country              <- "Turkmenistan"
hh_Tuvalu$country                    <- "Tuvalu"
hh_Uzbekistan$country                <- "Uzbekistan"
hh_Vanuatu$country                   <- "Vanuatu"
hh_VietNam$country                   <- "Vietnam"
hh_Yemen$country                     <- "Yemen"
hh_Zimbabwe$country                  <- "Zimbabwe"

# =============================================================================
# 3. RENAME NON-STANDARD VARIABLE NAMES BEFORE EXTRACTION
#    Nigeria MICS4 and Paraguay MICS4 use WS8/WS9 instead of WS11/WS15.
#    These are handled inside their country-specific extract functions.
#    Add further rename blocks here for any other non-standard surveys, e.g.:
#    names(hh_SomeCountry)[names(hh_SomeCountry) == "WS9"]  <- "WS11"
#    names(hh_SomeCountry)[names(hh_SomeCountry) == "WS10"] <- "WS15"
# =============================================================================

# =============================================================================
# 4. EXTRACT STANDARD SURVEY VARIABLES
# =============================================================================
hh_Afghanistan_san               <- extractStandardSurveyVariables_sanitation(hh_Afghanistan)
hh_Algeria_san                   <- extractStandardSurveyVariables_sanitation(hh_Algeria)
hh_Argentina_san                 <- extractStandardSurveyVariables_sanitation_withoutHH6_psu(hh_Argentina)
hh_Azerbaijan_san                <- extractStandardSurveyVariables_sanitation(hh_Azerbaijan)
hh_Bangladesh_san                <- extractVariablesFromBangladesh_sanitation(hh_Bangladesh)
hh_Belarus_san                   <- extractStandardSurveyVariables_sanitation(hh_Belarus)
hh_Benin_san                     <- extractStandardSurveyVariables_sanitation(hh_Benin)
hh_CentralAfricanRepublic_san    <- extractStandardSurveyVariables_sanitation(hh_CentralAfricanRepublic)
hh_Chad_san                      <- extractStandardSurveyVariables_sanitation(hh_Chad)
hh_Comoros_san                   <- extractStandardSurveyVariables_sanitation(hh_Comoros)
hh_Costa_Rica_san                <- extractStandardSurveyVariables_sanitation_withoutHH6_psu(hh_Costa_Rica)
hh_Cuba_san                      <- extractStandardSurveyVariables_sanitation(hh_Cuba)
hh_DominicanRepublic_san         <- extractStandardSurveyVariables_sanitation(hh_DominicanRepublic)
hh_DRCongo_san                   <- extractStandardSurveyVariables_sanitation(hh_DRCongo)
hh_Eswatini_san                  <- extractStandardSurveyVariables_sanitation_psu_lowercaps(hh_Eswatini)
#hh_Fiji_san                      <- extractStandardSurveyVariables_sanitation_psu_lowercaps(hh_Fiji)
hh_Gambia_san                    <- extractStandardSurveyVariables_sanitation(hh_Gambia)
hh_Georgia_san                   <- extractStandardSurveyVariables_sanitation(hh_Georgia)
hh_Ghana_san                     <- extractStandardSurveyVariables_sanitation(hh_Ghana)
hh_GuineaBissau_san              <- extractStandardSurveyVariables_sanitation(hh_GuineaBissau)
hh_Guyana_san                    <- extractStandardSurveyVariables_sanitation(hh_Guyana)
hh_Honduras_san                  <- extractStandardSurveyVariables_sanitation(hh_Honduras)
hh_Iraq_san                      <- extractStandardSurveyVariables_sanitation_strata(hh_Iraq)
hh_Jamaica_san                   <- extractStandardSurveyVariables_sanitation(hh_Jamaica)
hh_Kazakhstan_san                <- extractStandardSurveyVariables_sanitation_Stratum(hh_Kazakhstan)
hh_Kiribati_san                  <- extractStandardSurveyVariables_sanitation(hh_Kiribati)
hh_Kosovo_san                    <- extractStandardSurveyVariables_sanitation(hh_Kosovo)
hh_Kyrgyzstan_san                <- extractStandardSurveyVariables_sanitation(hh_Kyrgyzstan)
hh_LaoPDR_2023_san               <- extractStandardSurveyVariables_sanitation_stratum_SE(hh_LaoPDR_2023)
hh_Lesotho_san                   <- extractVariablesFromLesotho_sanitation(hh_Lesotho)
hh_Madagascar_san                <- extractStandardSurveyVariables_sanitation(hh_Madagascar)
hh_Malawi_san                    <- extractStandardSurveyVariables_sanitation(hh_Malawi)
hh_Mongolia_san                  <- extractStandardSurveyVariables_sanitation(hh_Mongolia)
hh_Montenegro_san                <- extractStandardSurveyVariables_sanitation_psu(hh_Montenegro)
hh_Nauru_san                     <- extractStandardSurveyVariables_sanitation_withoutHH6(hh_Nauru)
hh_Nepal_san                     <- extractStandardSurveyVariables_sanitation(hh_Nepal)
hh_Nigeria_san                   <- extractVariablesFromNigeria_sanitation(hh_Nigeria)
hh_Nigeria_new_san               <- extractStandardSurveyVariables_sanitation(hh_Nigeria_new)
hh_Pakistan_Sindh_san            <- extractStandardSurveyVariables_sanitation_psu(hh_Pakistan_Sindh)
hh_PakistanBalochistan_san       <- extractStandardSurveyVariables_sanitation_psu_lowercaps(hh_PakistanBalochistan)
hh_PakistanKhyberPakhtunkhwa_san <- extractStandardSurveyVariables_sanitation_psu_lowercaps(hh_PakistanKhyberPakhtunkhwa)
hh_PakistanPunjab_san            <- extractStandardSurveyVariables_sanitation_psu_lowercaps(hh_PakistanPunjab)
hh_Palestine_san                 <- extractStandardSurveyVariables_sanitation(hh_Palestine)
hh_Paraguay_san                  <- extractVariablesFromParaguay_sanitation(hh_Paraguay)
hh_Republic_of_North_Macedonia_san <- extractStandardSurveyVariables_sanitation(hh_Republic_of_North_Macedonia)
hh_Samoa_san                     <- extractStandardSurveyVariables_sanitation(hh_Samoa)
hh_SaoTome_san                   <- extractStandardSurveyVariables_sanitation(hh_SaoTome)
hh_Serbia_san                    <- extractStandardSurveyVariables_sanitation(hh_Serbia)
hh_SierraLeone_san               <- extractVariablesFromSierraLeone_sanitation(hh_SierraLeone)
hh_Suriname_san                  <- extractStandardSurveyVariables_sanitation(hh_Suriname)
hh_Thailand_san                  <- extractStandardSurveyVariables_sanitation(hh_Thailand)
hh_Togo_san                      <- extractStandardSurveyVariables_sanitation(hh_Togo)
hh_Tonga_san                     <- extractStandardSurveyVariables_sanitation(hh_Tonga)
hh_Trinidad_and_Tobago_san       <- extractStandardSurveyVariables_sanitation_psu(hh_Trinidad_and_Tobago)
hh_Tunisia_san                   <- extractStandardSurveyVariables_sanitation(hh_Tunisia)
hh_Turkmenistan_san              <- extractStandardSurveyVariables_sanitation_Stratum(hh_Turkmenistan)
hh_Tuvalu_san                    <- extractVariablesFromTuvalu_sanitation(hh_Tuvalu)
hh_Uzbekistan_san                <- extractStandardSurveyVariables_sanitation(hh_Uzbekistan)
hh_Vanuatu_san                   <- extractStandardSurveyVariables_sanitation(hh_Vanuatu)
hh_Vietnam_san                   <- extractStandardSurveyVariables_sanitation(hh_VietNam)
hh_Yemen_san                     <- extractStandardSurveyVariables_sanitation(hh_Yemen)
hh_Zimbabwe_san                  <- extractStandardSurveyVariables_sanitation_psu_lowercaps(hh_Zimbabwe)


# Pakistan Sindh
names(hh_Pakistan_Sindh_san)[names(hh_Pakistan_Sindh_san) == "psu"] <- "PSU"

# Trinidad and Tobago
names(hh_Trinidad_and_Tobago_san)[names(hh_Trinidad_and_Tobago_san) == "psu"] <- "PSU"

# Turkmenistan
names(hh_Turkmenistan_san)[names(hh_Turkmenistan_san) == "Stratum"] <- "stratum"

hh_Afghanistan_san <- extractStandardSurveyVariables_sanitation(hh_Afghanistan)
hh_Afghanistan_san$PSU <- hh_Afghanistan_san$HH1
# =============================================================================
# 5. DEFINE FULL SURVEY LIST FOR ITERATION
# =============================================================================
all_san_surveys <- c(
  "Afghanistan", "Algeria", "Argentina", "Azerbaijan", "Bangladesh",
  "Belarus", "Benin", "CentralAfricanRepublic", "Chad", "Comoros",
  "Costa_Rica", "Cuba", "DominicanRepublic", "DRCongo", "Eswatini",
  "Gambia", "Georgia", "Ghana", "GuineaBissau", "Guyana",
  "Honduras", "Iraq", "Jamaica", "Kazakhstan", "Kiribati", "Kosovo",
  "Kyrgyzstan", "LaoPDR_2023", "Lesotho", "Madagascar", "Malawi",
  "Mongolia", "Montenegro", "Nauru", "Nepal", "Nigeria", "Nigeria_new",
  "Pakistan_Sindh", "PakistanBalochistan", "PakistanKhyberPakhtunkhwa",
  "PakistanPunjab", "Palestine", "Paraguay", "Republic_of_North_Macedonia",
  "Samoa", "SaoTome", "Serbia", "SierraLeone", "Suriname", "Thailand",
  "Togo", "Tonga", "Trinidad_and_Tobago", "Tunisia", "Turkmenistan",
  "Tuvalu", "Uzbekistan", "Vanuatu", "Vietnam", "Yemen", "Zimbabwe"
)

# =============================================================================
# 6. CHECK FOR MISSING VARIABLES
# =============================================================================
variables_to_check_san <- c("WS11", "WS15", "HH6", "HH7", "HH5D", "HH5M",
                             "HH5Y", "PSU", "stratum", "hhweight")

for (survey_name in all_san_surveys) {
  san_data <- get(paste0("hh_", survey_name, "_san"))
  missing_vars <- setdiff(variables_to_check_san, names(san_data))
  if (length(missing_vars) > 0) {
    message(survey_name, " is missing: ", paste(missing_vars, collapse = ", "))
  }
}

# =============================================================================
# 7. EXTRACT REGION NAMES FROM HH7
# =============================================================================
for (survey_name in all_san_surveys) {
  hh_data <- get(paste0("hh_", survey_name, "_san"))
  hh7_extract <- extractVariableLabelsfromHH7(hh_data)
  hh7_extract$id <- as.factor(hh7_extract$id)
  assign(paste0("hh_", survey_name, "_HH7extract"), hh7_extract)
}

# =============================================================================
# 8. REPLACE HH7 NUMERIC IDS WITH REGION NAME LABELS
# =============================================================================
for (survey_name in all_san_surveys) {
  hh_data  <- get(paste0("hh_", survey_name, "_san"))
  hh7_extr <- get(paste0("hh_", survey_name, "_HH7extract"))
  hh_data  <- replaceHH7LabelsWithRegionNames(hh_data, hh7_extr)
  assign(paste0("hh_", survey_name, "_san"), hh_data)
}

# =============================================================================
# 9. CONVERT FACTOR VARIABLES TO CHARACTER (avoids NAs on rbind)
# =============================================================================
for (survey_name in all_san_surveys) {
  hh_data <- get(paste0("hh_", survey_name, "_san"))
  hh_data <- VariablesWhichWereFactorsAsCharacterToAvoidGenerationOfNA_sanitation(hh_data)
  # Also normalise Stratum -> stratum where uppercase was used
  names(hh_data)[names(hh_data) == "Stratum"] <- "stratum"
  assign(paste0("hh_", survey_name, "_san"), hh_data)
}

# =============================================================================
# 10. BIND ALL SURVEYS, LABEL, AND DERIVE OUTCOME VARIABLES
# =============================================================================
df.MICS.sanitation <- do.call(rbind, lapply(all_san_surveys, function(s) {
  get(paste0("hh_", s, "_san"))
}))

df.MICS.sanitation$WS11_raw <- df.MICS.sanitation$WS11   # preserve raw codes for QC

df.MICS.sanitation <- labelingSurveyVariableResponses_sanitation(df.MICS.sanitation)
df.MICS.sanitation <- deriveOpenDefecation(df.MICS.sanitation)

checkUncodedWS11(df.MICS.sanitation)

# Check for missing values by country in the final output
variables_to_check_san <- c("WS11", "WS15", "HH6", "HH7_region", "HH5D", "HH5M",
                            "HH5Y", "PSU", "stratum", "hhweight")

missing_by_country <- df.MICS.sanitation %>%
  group_by(country) %>%
  summarise(across(all_of(variables_to_check_san),
                   ~ sum(is.na(.)), 
                   .names = "NA_{.col}")) %>%
  filter(if_any(starts_with("NA_"), ~ . > 0))

print(missing_by_country, n = Inf, width = Inf)

write.csv(df.MICS.sanitation,
          "~/switchdrive/Eawag/WorldBankProject/HH_surveys/HH_survey_data/df_sanitation_MICS_v1.csv",
          fileEncoding = "UTF-8", row.names = FALSE)

# =============================================================================
# Variable summary:
#   WS11            0 = open defecation | 1 = unimproved | 2 = improved
#   WS11_raw        original MICS numeric code (for QC)
#   WS11_category   factor: "improved" / "unimproved" / "open_defecation"
#   WS11_improved   binary: 1 = improved facility
#   open_defecation binary: 1 = open defecation
#   WS15            1 = shared | 0 = not shared | -99 = missing
#   HH6             1 = urban | 2 = rural | 3 = camp
#   HH7_region      admin-1 region name
#   PSU / stratum   survey design variables
#   hhweight        household weight
# =============================================================================
