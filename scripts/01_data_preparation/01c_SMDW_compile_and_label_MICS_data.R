#title: "Compiling and Labeling Multiple Indicator Cluster Survey Data"


library(foreign)
library(tidyr)
library(dplyr)
library(tidyverse)
library(haven)
library(surveytoolbox)
library(survey)


source(here::here("functions/label_mics_SMDW_variables.R"))
source(here::here("functions/extract_mics_SMDW_variables.R"))
source(here::here("configuration/paths.R"))



loadSurveys(PATH_TO_SURVEYS_old_SMDW)
loadSurveys(PATH_TO_SURVEYS_new_SMDW)
loadSurveys(PATH_TO_SURVEYS_new_other)


#Creating Variable with country name (previously matched for Greenwood et al. 2024)
hh_Algeria$country <- "Algeria"
hh_Bangladesh$country <- "Bangladesh"
hh_CentralAfricanRepublic$country <- "Central African Republic"
hh_Chad$country <- "Chad"
hh_Gambia$country <- "Gambia"
hh_Georgia$country <- "Georgia"
hh_Ghana$country <- "Ghana"
hh_GuineaBissau$country <- "Guinea Bissau"
hh_Guyana$country <- "Guyana"
hh_Iraq$country <- "Iraq"
hh_Kiribati$country <- "Kiribati"
hh_Kosovo$country <- "Kosovo"
hh_Lesotho$country <- "Lesotho"
hh_Madagascar$country <- "Madagascar"
hh_Mongolia$country <- "Mongolia"
hh_Nigeria$country <- "Nigeria"
hh_PakistanPunjab$country <- "Pakistan Punjab"
hh_Paraguay$country <- "Paraguay"
hh_SaoTome$country <- "Sao Tome and Principe"
hh_SierraLeone$country <- "Sierra Leone"
hh_Suriname$country <- "Suriname"
hh_Togo$country <- "Togo"
hh_Tonga$country <- "Tonga"
hh_Palestine$country <- "West Bank and Gaza"
hh_Zimbabwe$country <- "Zimbabwe"

#Creating Variable with country name (surveys with drinking water quality data 
#not used in Greenwood et al. 2024)
hh_Azerbaijan$country <- "Azerbaijan" 
hh_Benin$country <- "Benin"
hh_DRCongo$country <- "DR Congo"
hh_DominicanRepublic$country <- "Dominican Republic"
hh_Fiji$country <- "Fiji"
hh_Eswatini$country <- "Eswatini"
hh_Honduras$country <- "Honduras"
hh_LaoPDR_2023$country <-"Lao PDR"
hh_Malawi$country <- "Malawi"
hh_Nepal$country <- "Nepal"
hh_PakistanBalochistan$country <- "Pakistan Balochistan" 
hh_PakistanKhyberPakhtunkhwa$country <- "Pakistan Khyber Pakhtunkhwa" 
hh_Samoa$country <- "Samoa" 
hh_Tunisia$country <- "Tunisia"
hh_Tuvalu$country <- "Tuvalu" 
hh_Vanuatu$country <- "Vanuatu"
hh_VietNam$country <- "Vietnam"

#Creating Variable with country name (other MICS surveys without drinking water quality data)
hh_Afghanistan$country <- "Afghanistan" 
hh_Argentina$country <- "Argentina"
hh_Belarus$country <- "Belarus"
hh_Comoros$country <- "Comoros"
hh_Costa_Rica$country <- "Costa Rica"
hh_Cuba$country <- "Cuba"
hh_Jamaica$country <- "Jamaica"
hh_Kazakhstan$country <- "Kazakhstan"
hh_Kyrgyzstan$country <- "Kyrgyzstan"
hh_Montenegro$country <- "Montenegro"
hh_Nauru$country <- "Nauru"
hh_Nigeria_new$country <- "Nigeria"
hh_Pakistan_Sindh$country <- "Pakistan Sindh"
hh_Qatar$country <- "Qatar"
hh_Republic_of_North_Macedonia$country <- "Republic of North Macedonia"
hh_Serbia$country <- "Serbia"
hh_Suriname$country <- "Suriname"
hh_Thailand$country <- "Thailand"
hh_Trinidad_and_Tobago$country <- "Trinidad and Tobago"
hh_Turkmenistan$country <- "Turkmenistan"
hh_Uzbekistan$country <- "Uzbekistan"
hh_Yemen$country <- "Yemen"


# extracting standard survey variables
hh_Algeria_SMDW <- extractStandardSurveyVariables(hh_Algeria)
hh_Benin_SMDW <- extractStandardSurveyVariables(hh_Benin)
hh_CentralAfricanRepublic_SMDW <- extractStandardSurveyVariables(hh_CentralAfricanRepublic)
hh_Chad_SMDW <- extractStandardSurveyVariables(hh_Chad) 
hh_DominicanRepublic_SMDW <- extractStandardSurveyVariables(hh_DominicanRepublic)
hh_Fiji_SMDW <- extractStandardSurveyVariables_psu_lowercaps(hh_Fiji)
hh_Gambia_SMDW <- extractStandardSurveyVariables(hh_Gambia) 
hh_Georgia_SMDW <- extractStandardSurveyVariables(hh_Georgia)
hh_Ghana_SMDW <- extractStandardSurveyVariables(hh_Ghana)
hh_GuineaBissau_SMDW <- extractStandardSurveyVariables(hh_GuineaBissau)
hh_Guyana_SMDW <- extractStandardSurveyVariables(hh_Guyana)
hh_Iraq_SMDW <- extractStandardSurveyVariables_strata(hh_Iraq) 
hh_Kiribati_SMDW <- extractStandardSurveyVariables(hh_Kiribati)
hh_Kosovo_SMDW <- extractStandardSurveyVariables(hh_Kosovo)
hh_Malawi_SMDW <- extractStandardSurveyVariables(hh_Malawi)
hh_Madagascar_SMDW <- extractStandardSurveyVariables(hh_Madagascar)
hh_Mongolia_SMDW <- extractStandardSurveyVariables(hh_Mongolia)
hh_Nepal_SMDW <- extractStandardSurveyVariables(hh_Nepal)
hh_PakistanPunjab_SMDW <- extractStandardSurveyVariables_psu_lowercaps(hh_PakistanPunjab)
hh_Palestine_SMDW <- extractStandardSurveyVariables(hh_Palestine) 
hh_Samoa_SMDW <- extractStandardSurveyVariables(hh_Samoa)
hh_SaoTome_SMDW <- extractStandardSurveyVariables(hh_SaoTome)
hh_Suriname_SMDW <- extractStandardSurveyVariables(hh_Suriname)
hh_Togo_SMDW <- extractStandardSurveyVariables(hh_Togo) 
hh_Tonga_SMDW <- extractStandardSurveyVariables(hh_Tonga)
hh_Vietnam_SMDW <- extractStandardSurveyVariables(hh_VietNam)
hh_Zimbabwe_SMDW <- extractStandardSurveyVariables_psu_lowercaps(hh_Zimbabwe)

hh_Azerbaijan_SMDW <- extractStandardSurveyVariables(hh_Azerbaijan)
hh_DRCongo_SMDW <- extractStandardSurveyVariables(hh_DRCongo)
hh_Eswatini_SMDW<- extractStandardSurveyVariables_psu_lowercaps(hh_Eswatini)
hh_Honduras_SMDW <- extractStandardSurveyVariables(hh_Honduras)
hh_LaoPDR_2023_SMDW <- extractStandardSurveyVariables_stratum_SE(hh_LaoPDR_2023)
hh_PakistanKhyberPakhtunkhwa_SMDW <- extractStandardSurveyVariables_psu_lowercaps(hh_PakistanKhyberPakhtunkhwa)
hh_PakistanBalochistan_SMDW <- extractStandardSurveyVariables_psu_lowercaps(hh_PakistanBalochistan)
hh_Tunisia_SMDW <- extractStandardSurveyVariables(hh_Tunisia)
hh_Vanuatu_SMDW <- extractStandardSurveyVariables(hh_Vanuatu)

hh_Afghanistan_Variables <- extractOtherStandardSurveyVariables(hh_Afghanistan)
hh_Argentina_Variables <- extractOtherStandardSurveyVariables_withoutHH6_psu(hh_Argentina)
hh_Belarus_Variables <- extractOtherStandardSurveyVariables_withoutWS8(hh_Belarus)
hh_Comoros_Variables <- extractOtherStandardSurveyVariables(hh_Comoros)

# Comoros: the standard HH7 code does not yield usable region labels.
# Build a 4-region variable from HH7Aux (island) and HH7A (Ngazidja sub-area).
hh_Comoros_Variables$HH7_region <- dplyr::case_when(
  as.numeric(hh_Comoros$HH7Aux) == 1                                             ~ "Mwali",
  as.numeric(hh_Comoros$HH7Aux) == 2                                             ~ "Ndzuwani",
  as.numeric(hh_Comoros$HH7Aux) == 3 & as.numeric(hh_Comoros$HH7A) == 1         ~ "Moroni",
  as.numeric(hh_Comoros$HH7Aux) == 3 & as.numeric(hh_Comoros$HH7A) == 2         ~ "Reste de Ngazidja"
)
hh_Comoros_Variables$HH7 <- NULL
# Pre-create empty extract so the loop below can safely skip Comoros
hh_Comoros_HH7extract_other <- data.frame(id = factor())
hh_Costa_Rica_Variables <- extractOtherStandardSurveyVariables_withoutWS8_psu(hh_Costa_Rica)
hh_Cuba_Variables <- extractOtherStandardSurveyVariables(hh_Cuba)
hh_Jamaica_Variables <- extractOtherStandardSurveyVariables(hh_Jamaica)
hh_Kazakhstan_Variables <- extractOtherStandardSurveyVariables_Stratum(hh_Kazakhstan)
hh_Kyrgyzstan_Variables <- extractOtherStandardSurveyVariables(hh_Kyrgyzstan)
hh_Montenegro_Variables <- extractOtherStandardSurveyVariables_psu(hh_Montenegro)
hh_Nauru_Variables <- extractOtherStandardSurveyVariables_withoutHH6(hh_Nauru)
hh_Nigeria_new_Variables <- extractOtherStandardSurveyVariables(hh_Nigeria_new)
hh_Pakistan_Sindh_Variables <- extractOtherStandardSurveyVariables_psu(hh_Pakistan_Sindh)
hh_Republic_of_North_Macedonia_Variables <- extractOtherStandardSurveyVariables(hh_Republic_of_North_Macedonia)
hh_Serbia_Variables <- extractOtherStandardSurveyVariables(hh_Serbia)
hh_Suriname_Variables <- extractOtherStandardSurveyVariables(hh_Suriname)
hh_Thailand_Variables <- extractOtherStandardSurveyVariables(hh_Thailand)

# Thailand: province names are stored in HH7A value labels, not in HH7.
labs  <- sjlabelled::get_labels(hh_Thailand$HH7A, values = "n")
codes <- as.character(hh_Thailand$HH7A)
hh_Thailand_Variables$HH7_region <- unname(labs[codes])
hh_Thailand_Variables$HH7 <- NULL
# Pre-create empty extract so the loop below can safely skip Thailand
hh_Thailand_HH7extract_other <- data.frame(id = factor())
hh_Trinidad_and_Tobago_Variables <- extractOtherStandardSurveyVariables_psu(hh_Trinidad_and_Tobago)
hh_Turkmenistan_Variables <- extractOtherStandardSurveyVariables_Stratum(hh_Turkmenistan)
hh_Uzbekistan_Variables <- extractOtherStandardSurveyVariables(hh_Uzbekistan)
hh_Yemen_Variables <- extractOtherStandardSurveyVariables(hh_Yemen)


#first surveys available with some different variable naming
hh_Bangladesh_SMDW <- extractVariablesFromBangladesh(hh_Bangladesh)
hh_Lesotho_SMDW <- extractVariablesFromLesotho(hh_Lesotho)
hh_Nigeria_SMDW <- extractVariablesFromNigeria(hh_Nigeria)
hh_Paraguay_SMDW <- extractVariablesFromParaguay(hh_Paraguay)
hh_SierraLeone_SMDW <- extractVariablesFromSierraLeone(hh_SierraLeone)

hh_Tuvalu_SMDW <- extractVariablesFromTuvalu(hh_Tuvalu)

# countries to include in the later HH7 / WS1 / relabelling steps
SMDW_surveys <- c(
  "Algeria",
  "Bangladesh",
  "CentralAfricanRepublic",
  "Chad",
  "DominicanRepublic",
  "Gambia",
  "Georgia",
  "Ghana",
  "GuineaBissau",
  "Guyana",
  "Iraq",
  "Kiribati",
  "Kosovo",
  "Lesotho",
  "Madagascar",
  "Mongolia",
  "Nigeria",
  "PakistanPunjab",
  "Paraguay",
  "SaoTome",
  "SierraLeone",
  "Suriname",
  "Togo",
  "Tonga",
  "Palestine",
  "Zimbabwe",
  
  "Azerbaijan",
  "Benin",
  "DRCongo",
  "Eswatini",
  "Fiji",
  "Honduras",
  "Malawi",
  "Nepal",
  "LaoPDR_2023",
  "PakistanBalochistan", 
  "PakistanKhyberPakhtunkhwa", 
  "Samoa",
  "Tunisia",
  "Tuvalu", 
  "Vanuatu",
  "Vietnam"
)

other_surveys <- c(
"Afghanistan",
"Argentina",
"Belarus",
"Comoros",
"Costa_Rica",
"Cuba",
"Jamaica",
"Kazakhstan",
"Kyrgyzstan",
"Montenegro",
"Nauru",
"Nigeria_new",
"Pakistan_Sindh",
"Republic_of_North_Macedonia",
"Serbia",
"Suriname",
"Thailand",
"Trinidad_and_Tobago",
"Turkmenistan",
"Uzbekistan",
"Yemen")


# =============================================================================
# NORMALISE COLUMN NAMES ACROSS OTHER_SURVEYS
# Mirrors sanitation step 9: standardise psu → PSU and Stratum → stratum
# for all other_surveys before variable checks and HH7 extraction loops.
# =============================================================================
for (survey_name in other_surveys) {
  hh_data <- get(paste0("hh_", survey_name, "_Variables"))
  names(hh_data)[names(hh_data) == "psu"]    <- "PSU"
  names(hh_data)[names(hh_data) == "Stratum"] <- "stratum"
  assign(paste0("hh_", survey_name, "_Variables"), hh_data)
}

# check which extracted survey files are missing variables needed for relabeling
variables_to_check_WQ    <- c("WS1", "WS2", "WS3", "WS4", "WS7", "WS8", "WQ27", "HH5D", "HH5M", "HH5Y", "stratum", "PSU", "HH7")
other_variables_to_check <- c("WS1", "WS2", "WS3", "WS4", "WS7", "WS8",         "HH5D", "HH5M", "HH5Y", "stratum", "PSU", "HH7")

for (survey_name in SMDW_surveys) {
  smdw_data <- get(paste0("hh_", survey_name, "_SMDW"))
  missing_variables <- setdiff(variables_to_check_WQ, names(smdw_data))
  
  if (length(missing_variables) > 0) {
    message(survey_name, " is missing: ", paste(missing_variables, collapse = ", "))
  }
}

for (survey_name in other_surveys) {
  other_data <- get(paste0("hh_", survey_name, "_Variables"))
  missing_variables <- setdiff(other_variables_to_check, names(other_data))
  
  if (length(missing_variables) > 0) {
    message(survey_name, " is missing: ", paste(missing_variables, collapse = ", "))
  }
}


# extracting region names from survey data
for (survey_name in SMDW_surveys) {
  hh_data_SMDW <- get(paste0("hh_", survey_name, "_SMDW"))
  hh7_extract_SMDW <- extractVariableLabelsfromHH7(hh_data_SMDW)
  hh7_extract_SMDW$id <- as.factor(hh7_extract_SMDW$id)
  assign(paste0("hh_", survey_name, "_HH7extract_SMDW"), hh7_extract_SMDW)
}

for (survey_name in other_surveys) {
  # Comoros and Thailand have custom HH7_region built above; skip standard extraction
  if (survey_name %in% c("Comoros", "Thailand")) next
  hh_data_other <- get(paste0("hh_", survey_name, "_Variables"))
  hh7_extract_other <- extractVariableLabelsfromHH7(hh_data_other)
  hh7_extract_other$id <- as.factor(hh7_extract_other$id)
  assign(paste0("hh_", survey_name, "_HH7extract_other"), hh7_extract_other)
}

# checking for any new labels in WS1
for (survey_name in SMDW_surveys) {
  hh_data_SMDW <- get(paste0("hh_", survey_name, "_SMDW"))
  ws1_extract_SMDW <- extractVariableLabelsfromWS1(hh_data_SMDW)
  assign(paste0("hh_", survey_name, "_WS1extract_SMDW"), ws1_extract_SMDW)
}

for (survey_name in other_surveys) {
  hh_data_other <- get(paste0("hh_", survey_name, "_Variables"))
  ws1_extract_other <- extractVariableLabelsfromWS1(hh_data_other)
  assign(paste0("hh_", survey_name, "_WS1extract_other"), ws1_extract_other)
}


# replace HH7 labels with region names in the SMDW files
for (survey_name in SMDW_surveys) {
  hh_data_SMDW <- get(paste0("hh_", survey_name, "_SMDW"))
  hh7_extract_SMDW <- get(paste0("hh_", survey_name, "_HH7extract_SMDW"))
  hh_data_SMDW <- replaceHH7LabelsWithRegionNames(hh_data_SMDW, hh7_extract_SMDW)
  assign(paste0("hh_", survey_name, "_SMDW"), hh_data_SMDW)
}

for (survey_name in other_surveys) {
  # Comoros and Thailand already have HH7_region set; skip standard replacement
  if (survey_name %in% c("Comoros", "Thailand")) next
  hh_data_other <- get(paste0("hh_", survey_name, "_Variables"))
  hh7_extract_other <- get(paste0("hh_", survey_name, "_HH7extract_other"))
  hh_data_other <- replaceHH7LabelsWithRegionNames(hh_data_other, hh7_extract_other)
  assign(paste0("hh_", survey_name, "_Variables"), hh_data_other)
}

# convert factor variables to character to avoid generation of NAs
for (survey_name in SMDW_surveys) {
  hh_data <- get(paste0("hh_", survey_name, "_SMDW"))
  hh_data <- VariablesWhichWereFactorsAsCharacterToAvoidGenerationOfNA(hh_data)
  assign(paste0("hh_", survey_name, "_SMDW"), hh_data)
}

df.MICS.SMDW_old <- rbind(
  hh_Algeria_SMDW,
  hh_Bangladesh_SMDW,
  hh_CentralAfricanRepublic_SMDW,
  hh_Chad_SMDW,
  hh_Gambia_SMDW,
  hh_Georgia_SMDW,
  hh_Ghana_SMDW,
  hh_GuineaBissau_SMDW,
  hh_Guyana_SMDW,
  hh_Iraq_SMDW,
  hh_Kiribati_SMDW,
  hh_Kosovo_SMDW,
  hh_Lesotho_SMDW,
  hh_Madagascar_SMDW,
  hh_Mongolia_SMDW,
  hh_Nigeria_SMDW,
  hh_PakistanPunjab_SMDW,
  hh_Paraguay_SMDW,
  hh_SaoTome_SMDW,
  hh_SierraLeone_SMDW,
  hh_Suriname_SMDW,
  hh_Togo_SMDW,
  hh_Tonga_SMDW,
  hh_Palestine_SMDW,
  hh_Zimbabwe_SMDW
)

df.MICS.SMDW_old$WS7 <- as.character(df.MICS.SMDW_old$WS7)
df.MICS.SMDW_old$WS8 <- as.character(df.MICS.SMDW_old$WS8)

df.MICS.SMDW_old_Labeled <- relabelingSurveyQuestionResponses(
  df.MICS.SMDW_old, WS1, WS2, WS3, WS4, WS7, WS8, WQ27
)

write.csv(df.MICS.SMDW_old_Labeled, here::here("data/processed/household_surveys/df.SMDW_wq_MICS_old.csv"),
          fileEncoding = "UTF-8", row.names = FALSE)

df.MICS.SMDW_new <- rbind(
hh_Azerbaijan_SMDW,
hh_Benin_SMDW,
hh_DRCongo_SMDW, 
hh_DominicanRepublic_SMDW,
hh_Eswatini_SMDW, 
hh_Fiji_SMDW,
hh_Honduras_SMDW, 
hh_LaoPDR_2023_SMDW, 
hh_Nepal_SMDW,
hh_PakistanKhyberPakhtunkhwa_SMDW, 
hh_PakistanBalochistan_SMDW, 
hh_Samoa_SMDW,
hh_Tunisia_SMDW, 
hh_Tuvalu_SMDW, 
hh_Vanuatu_SMDW,
hh_Vietnam_SMDW) 

df.MICS.SMDW_new$WS7 <- as.character(df.MICS.SMDW_new$WS7)
df.MICS.SMDW_new$WS8 <- as.character(df.MICS.SMDW_new$WS8)

df.MICS.SMDW_new_Labeled <- relabelingSurveyQuestionResponses(
  df.MICS.SMDW_new, WS1, WS2, WS3, WS4, WS7, WS8, WQ27
)

write.csv(df.MICS.SMDW_new_Labeled, here::here("data/processed/household_surveys/df.SMDW_wq_MICS_new.csv"),
          fileEncoding = "UTF-8", row.names = FALSE)


other_surveys <- c(
  "hh_Afghanistan_Variables",
  "hh_Argentina_Variables",
  "hh_Belarus_Variables",
  "hh_Comoros_Variables",
  "hh_Costa_Rica_Variables",
  "hh_Cuba_Variables",
  "hh_Jamaica_Variables",
  "hh_Kazakhstan_Variables",
  "hh_Kyrgyzstan_Variables",
  "hh_Montenegro_Variables",
  "hh_Nauru_Variables",
  "hh_Nigeria_new_Variables",
  "hh_Pakistan_Sindh_Variables",
  "hh_Republic_of_North_Macedonia_Variables",
  "hh_Serbia_Variables",
  "hh_Suriname_Variables",
  "hh_Thailand_Variables",
  "hh_Trinidad_and_Tobago_Variables",
  "hh_Turkmenistan_Variables",
  "hh_Uzbekistan_Variables",
  "hh_Yemen_Variables"
)

# Convert factor variables to character to avoid NAs on rbind.
# Stratum → stratum and psu → PSU normalisation already done above.
for (obj in other_surveys) {
  df <- get(obj)
  df[] <- lapply(df, function(x) {
    if (is.factor(x)) as.character(x) else x
  })
  assign(obj, df)
}


df.MICS.other <- rbind(
  hh_Afghanistan_Variables,
  hh_Argentina_Variables,
  hh_Belarus_Variables,
  hh_Comoros_Variables,
  hh_Costa_Rica_Variables,
  hh_Cuba_Variables,
  hh_Jamaica_Variables,
  hh_Kazakhstan_Variables,
  hh_Kyrgyzstan_Variables,
  hh_Montenegro_Variables,
  hh_Nauru_Variables,
  hh_Nigeria_new_Variables,
  hh_Pakistan_Sindh_Variables,
  hh_Republic_of_North_Macedonia_Variables,
  hh_Serbia_Variables,
  hh_Suriname_Variables,
  hh_Thailand_Variables,
  hh_Trinidad_and_Tobago_Variables,
  hh_Turkmenistan_Variables,
  hh_Uzbekistan_Variables,
  hh_Yemen_Variables
)

df.MICS.other$WS7 <- as.character(df.MICS.other$WS7)
df.MICS.other$WS8 <- as.character(df.MICS.other$WS8)

# add WQ27 as NA so the same relabelling function call structure can be used
df.MICS.other$WQ27 <- NA

df.MICS.other_Labeled <- relabelingSurveyQuestionResponses(
  df.MICS.other, WS1, WS2, WS3, WS4, WS7, WS8, WQ27
)

write.csv(df.MICS.other_Labeled, here::here("data/processed/household_surveys/df.SMDW_other_MICS.csv"),
          fileEncoding = "UTF-8", row.names = FALSE)
