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

readHouseHoldSurveyData <- function(){
  df.MICS_HH <- read.csv("~/switchdrive/PHD-2020-2024/SMDWs submission/Data_for_reviewers/df_MICS_SMDW_250222.csv")
  return(df.MICS_HH)
}

readHouseHoldSurveyDataForTestSet <- function(){
  df.MICS_HH <- read.csv("~/switchdrive/PHD-2020-2024/SMDWs submission/Data_for_reviewers/df_SMDW_test_final_revised.csv")
  return(df.MICS_HH)
}

readMatchedRegionNamesForTestSet <- function(){
  df.MICS_HH <- read.csv(here("./2_Data_cleaning/3_MICS_Preprocessing_Dataframes/1_Compiling_MICS_test_and_training_sets/GADMandHH7_regionNamesForTestSet_revised.csv"))
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
