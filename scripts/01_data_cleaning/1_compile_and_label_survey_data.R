#title: "Compiling and Labeling Multiple Indicator Cluster Survey Data for Testing Set"


library(foreign)
library(tidyr)
library(dplyr)
library(tidyverse)
library(haven)
library(surveytoolbox)
library(survey)


source("FunctionsForLabelingHHMICS.R")
source("FunctionsForExtractingVariablesFromMICS.R")

PATH_TO_SURVEYS_old <- "~/switchdrive/Eawag/WorldBankProject/MICS_SurveysDrinkingWater/HH_surveys/HH_MICS_old"
PATH_TO_SURVEYS_new <- "~/switchdrive/Eawag/WorldBankProject/MICS_SurveysDrinkingWater/HH_surveys/HH_MICS_new"

loadSurveys(PATH_TO_SURVEYS_old)
loadSurveys(PATH_TO_SURVEYS_new)

#Creating Variable with country name (surveys used in Greenwood et al. 2024)
hh_Algeria$country <- "Algeria"
hh_Bangladesh$country <- "Bangladesh"
hh_Benin$country <- "Benin"
hh_CentralAfricanRepublic$country <- "Central African Republic"
hh_Chad$country <- "Chad"
hh_DominicanRepublic$country <- "Dominican Republic"
hh_Fiji$country <- "Fiji"
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
hh_Malawi$country <- "Malawi"
hh_Mongolia$country <- "Mongolia"
hh_Nepal$country <- "Nepal"
hh_Nigeria$country <- "Nigeria"
hh_PakistanPunjab$country <- "Pakistan Punjab"
hh_Paraguay$country <- "Paraguay"
hh_Samoa$country <- "Samoa" 
hh_SaoTome$country <- "Sao Tome and Principe"
hh_SierraLeone$country <- "Sierra Leone"
hh_Suriname$country <- "Suriname"
hh_Togo$country <- "Togo"
hh_Tonga$country <- "Tonga"
hh_VietNam$country <- "Vietnam"
hh_Palestine$country <- "West Bank and Gaza"
hh_Zimbabwe$country <- "Zimbabwe"

#Creating Variable with country name (surveys not used in Greenwood et al. 2024)
hh_Azerbaijan$country <- "Azerbaijan" 
hh_DRCongo$country <- "DR Congo"
hh_Eswatini$country <- "Eswatini"
hh_Honduras$country <- "Honduras"
hh_LaoPDR_2023$country <-"Lao PDR"
hh_PakistanBalochistan$country <- "Pakistan Balochistan" 
hh_PakistanKhyberPakhtunkhwa$country <- "Pakistan Khyber Pakhtunkhwa" 
hh_Tunisia$country <- "Tunisia"
hh_Tuvalu$country <- "Tuvalu" 
hh_Vanuatu$country <- "Vanuatu"

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
hh_VietNam_SMDW <- extractStandardSurveyVariables(hh_VietNam)
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

#first surveys available with some different variable naming
hh_Bangladesh_SMDW <- extractVariablesFromBangladesh(hh_Bangladesh)
hh_Lesotho_SMDW <- extractVariablesFromLesotho(hh_Lesotho)
hh_Nigeria_SMDW <- extractVariablesFromNigeria(hh_Nigeria)
hh_Paraguay_SMDW <- extractVariablesFromParaguay(hh_Paraguay)
hh_SierraLeone_SMDW <- extractVariablesFromSierraLeone(hh_SierraLeone)

hh_Tuvalu_SMDW <- extractVariablesFromTuvalu(hh_Tuvalu)



# countries to include in the later HH7 / WS1 / relabelling steps
all_surveys <- c(
  "Algeria",
  "Bangladesh",
  "Benin",
  "CentralAfricanRepublic",
  "Chad",
  "DominicanRepublic",
  "Fiji",
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
  "Malawi",
  "Mongolia",
  "Nepal",
  "Nigeria",
  "PakistanPunjab",
  "Paraguay",
  "Samoa",
  "SaoTome",
  "SierraLeone",
  "Suriname",
  "Togo",
  "Tonga",
  "VietNam",
  "Palestine",
  "Zimbabwe",
  
  "Azerbaijan", 
  "DRCongo",
  "Eswatini",
  "Honduras",
  "LaoPDR_2023",
  "PakistanBalochistan", 
  "PakistanKhyberPakhtunkhwa", 
  "Tunisia",
  "Tuvalu", 
  "Vanuatu"
)

# check which extracted survey files are missing variables needed for relabeling
variables_to_check <- c("WS1", "WS2", "WS3", "WS4", "WS7", "WS8", "WQ27", "HH5D", "HH5M", "HH5Y", "stratum", "PSU")

for (survey_name in all_surveys) {
  smdw_data <- get(paste0("hh_", survey_name, "_SMDW"))
  missing_variables <- setdiff(variables_to_check, names(smdw_data))
  
  if (length(missing_variables) > 0) {
    message(survey_name, " is missing: ", paste(missing_variables, collapse = ", "))
  }
}

# extracting region names from survey data
for (survey_name in all_surveys) {
  hh_data <- get(paste0("hh_", survey_name, "_SMDW"))
  hh7_extract <- extractVariableLabelsfromHH7(hh_data)
  hh7_extract$id <- as.factor(hh7_extract$id)
  assign(paste0("hh_", survey_name, "_HH7extract"), hh7_extract)
}

# checking for any new labels in WS1
for (survey_name in all_surveys) {
  hh_data <- get(paste0("hh_", survey_name, "_SMDW"))
  ws1_extract <- extractVariableLabelsfromWS1(hh_data)
  assign(paste0("hh_", survey_name, "_WS1extract"), ws1_extract)
}

# replace HH7 labels with region names in the SMDW files
for (survey_name in all_surveys) {
  hh_data <- get(paste0("hh_", survey_name, "_SMDW"))
  hh7_extract <- get(paste0("hh_", survey_name, "_HH7extract"))
  hh_data <- replaceHH7LabelsWithRegionNames(hh_data, hh7_extract)
  assign(paste0("hh_", survey_name, "_SMDW"), hh_data)
}

# convert factor variables to character to avoid generation of NAs
for (survey_name in all_surveys) {
  hh_data <- get(paste0("hh_", survey_name, "_SMDW"))
  hh_data <- VariablesWhichWereFactorsAsCharacterToAvoidGenerationOfNA(hh_data)
  assign(paste0("hh_", survey_name, "_SMDW"), hh_data)
}

df.MICS.SMDW_old <- rbind(
  hh_Algeria_SMDW,
  hh_Bangladesh_SMDW,
  hh_Benin_SMDW,
  hh_CentralAfricanRepublic_SMDW,
  hh_Chad_SMDW,
  hh_DominicanRepublic_SMDW,
  hh_Fiji_SMDW,
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
  hh_Malawi_SMDW,
  hh_Mongolia_SMDW,
  hh_Nepal_SMDW,
  hh_Nigeria_SMDW,
  hh_PakistanPunjab_SMDW,
  hh_Paraguay_SMDW,
  hh_Samoa_SMDW,
  hh_SaoTome_SMDW,
  hh_SierraLeone_SMDW,
  hh_Suriname_SMDW,
  hh_Togo_SMDW,
  hh_Tonga_SMDW,
  hh_VietNam_SMDW,
  hh_Palestine_SMDW,
  hh_Zimbabwe_SMDW
)

df.MICS.SMDW_old$WS7 <- as.character(df.MICS.SMDW_old$WS7)
df.MICS.SMDW_old$WS8 <- as.character(df.MICS.SMDW_old$WS8)

df.MICS.SMDW_old_Labeled <- relabelingSurveyQuestionResponses(
  df.MICS.SMDW_old, WS1, WS2, WS3, WS4, WS7, WS8, WQ27
)

write.csv(df.MICS.SMDW_old_Labeled, "~/switchdrive/Eawag/WorldBankProject/MICS_SurveysDrinkingWater/HH_surveys/df_SMDW_oldMICS.csv", fileEncoding = "UTF-8", row.names = F)

df.MICS.SMDW_new <- rbind(
hh_Azerbaijan_SMDW, 
hh_DRCongo_SMDW, 
hh_Eswatini_SMDW, 
hh_Honduras_SMDW, 
hh_LaoPDR_2023_SMDW, 
hh_PakistanKhyberPakhtunkhwa_SMDW, 
hh_PakistanBalochistan_SMDW, 
hh_Tunisia_SMDW, 
hh_Tuvalu_SMDW, 
hh_Vanuatu_SMDW) 

df.MICS.SMDW_new$WS7 <- as.character(df.MICS.SMDW_new$WS7)
df.MICS.SMDW_new$WS8 <- as.character(df.MICS.SMDW_new$WS8)

df.MICS.SMDW_new_Labeled <- relabelingSurveyQuestionResponses(
  df.MICS.SMDW_new, WS1, WS2, WS3, WS4, WS7, WS8, WQ27
)

write.csv(df.MICS.SMDW_new_Labeled, "~/switchdrive/Eawag/WorldBankProject/MICS_SurveysDrinkingWater/HH_surveys/df_SMDW_newMICS.csv", fileEncoding = "UTF-8", row.names = F)


df_region_summary_new <- df.MICS.SMDW_new_Labeled %>%
  mutate(household_id = paste(HH1, HH2, sep = "_")) %>%
  group_by(country, HH7_region) %>%
  summarise(
    households_in_region = n_distinct(household_id),
    clusters_in_region = n_distinct(HH1),
    households_with_WQ27 = n_distinct(household_id[!is.na(WQ27)]),
    .groups = "drop"
  ) %>%
  rename(
    `Country name` = country,
    `HH7 region` = HH7_region,
    `number of households in the region (HH2)` = households_in_region,
    `number of clusters in the region (HH1)` = clusters_in_region,
    `number of households with data on water quality (WQ27)` = households_with_WQ27
  )

write.csv(df_region_summary_new, "~/switchdrive/Eawag/WorldBankProject/MICS_SurveysDrinkingWater/HH_surveys/regionalSummary_MICSquality_new.csv", row.names = FALSE)




# conservative handling if a stratum has only one PSU in a domain
options(survey.lonely.psu = "adjust")
options(survey.adjust.domain.lonely = TRUE)

# prepare data for the survey design
df_wq_se <- df.MICS.SMDW_old_Labeled %>%
  mutate(
    household_id = paste(HH1, HH2, sep = "_"),
    PSU_calc = interaction(country, PSU, drop = TRUE),
    stratum_calc = interaction(country, stratum, drop = TRUE),
    WQ27 = as.numeric(WQ27),
    wqsweight = as.numeric(wqsweight)
  )

# survey design for water quality
design_wq <- svydesign(
  ids = ~PSU_calc,
  strata = ~stratum_calc,
  weights = ~wqsweight,
  data = df_wq_se,
  nest = TRUE
)

# weighted contamination estimate and Taylor-linearized SE by country and HH7 region
df_wq_estimates <- svyby(
  ~WQ27,
  ~country + HH7_region,
  design = subset(
    design_wq,
    !is.na(WQ27) & !is.na(wqsweight) & !is.na(PSU_calc) & !is.na(stratum_calc)
  ),
  FUN = svymean,
  vartype = c("se"),
  na.rm = TRUE,
  deff = TRUE
) %>%
  as.data.frame() %>%
  mutate(
    ci_lower = pmax(0, WQ27 - 1.96 * se),
    ci_upper = pmin(1, WQ27 + 1.96 * se),
    contamination_percent = 100 * WQ27,
    se_percent = 100 * se,
    ci_lower_percent = 100 * ci_lower,
    ci_upper_percent = 100 * ci_upper
  )

# overview of variables used in the calculation, plus your existing summary columns
df_region_summary <- df_wq_se %>%
  group_by(country, HH7_region) %>%
  summarise(
    households_in_region = n_distinct(household_id),
    clusters_in_region = n_distinct(HH1),
    households_with_WQ27 = n_distinct(household_id[!is.na(WQ27)]),
    households_with_wqsweight = n_distinct(household_id[!is.na(wqsweight)]),
    households_with_PSU = n_distinct(household_id[!is.na(PSU)]),
    households_with_stratum = n_distinct(household_id[!is.na(stratum)]),
    households_used_in_SE = n_distinct(
      household_id[!is.na(WQ27) & !is.na(wqsweight) & !is.na(PSU) & !is.na(stratum)]
    ),
    PSUs_used_in_SE = n_distinct(
      PSU[!is.na(WQ27) & !is.na(wqsweight) & !is.na(PSU) & !is.na(stratum)]
    ),
    strata_used_in_SE = n_distinct(
      stratum[!is.na(WQ27) & !is.na(wqsweight) & !is.na(PSU) & !is.na(stratum)]
    ),
    .groups = "drop"
  ) %>%
  left_join(df_wq_estimates, by = c("country", "HH7_region")) %>%
  rename(
    `Country name` = country,
    `HH7 region` = HH7_region,
    `number of households in the region (HH2)` = households_in_region,
    `number of clusters in the region (HH1)` = clusters_in_region,
    `number of households with data on water quality (WQ27)` = households_with_WQ27,
    `number of households with water quality weights (wqsweight)` = households_with_wqsweight,
    `number of households with PSU` = households_with_PSU,
    `number of households with stratum` = households_with_stratum,
    `number of households used in SE calculation` = households_used_in_SE,
    `number of PSUs used in SE calculation` = PSUs_used_in_SE,
    `number of strata used in SE calculation` = strata_used_in_SE,
    `weighted proportion contaminated (WQ27=1)` = WQ27,
    `standard error` = se,
    `95% CI lower` = ci_lower,
    `95% CI upper` = ci_upper,
    `weighted percent contaminated` = contamination_percent,
    `SE percentage points` = se_percent,
    `95% CI lower percent` = ci_lower_percent,
    `95% CI upper percent` = ci_upper_percent,
    `design effect` = DEff.WQ27
  )
write.csv(df_region_summary, "~/switchdrive/Eawag/WorldBankProject/MICS_SurveysDrinkingWater/HH_surveys/regionalSummary_MICSquality.csv", row.names = FALSE)
