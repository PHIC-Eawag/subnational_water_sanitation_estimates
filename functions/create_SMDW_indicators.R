#title: "functions for creating SMDWs indicator"

replaceMinus99WithNa <- function(df){
  df[df == -99] <- NA
  return(df)
}

renameVariable <- function(df,oldVariableName, newVariableName){
  names(df)[names(df) == oldVariableName] <- newVariableName 
  return(df)
}

renameVariables <- function(df){
   df <- renameVariable(df,'WQ27','WQ27_sourcewaterBIN')
   df <- renameVariable(df,'WS7','WS7_sufficiency')
   df <- renameVariable(df,'WS3','WS3_Wslocation')
   df <- renameVariable(df,'HH7','HH7_region')
   df <- renameVariable(df,'WS1','WS1_mainWaterSourceDrink')
   df <- renameVariable(df,'WS2','WS2_mainWaterSourceOther')
   df <- renameVariable(df,'WS4','WS4_timeToCollect')
   df <- renameVariable(df,'WS8','WS8_whyInsufficient')
   return(df)
}

  renameDuplicateHH7RegionNamesFromDifferentCountries <- function(df){
    df$HH7_region[df$HH7_region == "Central" & df$country == "Paraguay"] <- "Central Paraguay"
    df$HH7_region[df$HH7_region == "Central" & df$country == "Ghana"] <- "Central Ghana"
    df$HH7_region[df$HH7_region == "NORD OUEST" & df$country == "Tunisia"] <- "NORD OUEST Tunisia"
    df$HH7_region[df$HH7_region == "NORD OUEST" & df$country == "Algeria"] <- "NORD OUEST Algeria"
    return(df)
  }

makeWS1_WS2_WS4_WS8_WS3ToCharacter <- function(df){
  df$WS1_mainWaterSourceDrink <- as.character(df$WS1_mainWaterSourceDrink)
  df$WS2_mainWaterSourceOther <- as.character(df$WS2_mainWaterSourceOther)
  df$WS4_timeToCollect <- as.character(df$WS4_timeToCollect)
  df$WS8_whyInsufficient <- as.character(df$WS8_whyInsufficient)
  df$WS3_Wslocation <- as.character(df$WS3_Wslocation)
  return(df)
}  

replaceNaWithMinus99forWS1_WS2_WS4_WS8_WS3 <- function(df){
  df$WS1_mainWaterSourceDrink[is.na(df$WS1_mainWaterSourceDrink)] <- -99
  df$WS2_mainWaterSourceOther[is.na(df$WS2_mainWaterSourceOther)] <- -99
  df$WS3_Wslocation[is.na(df$WS3_Wslocation)] <- -99
  df$WS4_timeToCollect[is.na(df$WS4_timeToCollect)] <- -99
  df$WS8_whyInsufficient[is.na(df$WS8_whyInsufficient)] <- -99
  return(df)
}
#TODO: this code would be neater than the alternative than that above but not working  
#replaceNaWithMinus99 <- function(df,variable){ 
  #df$variable[is.na(df$variable)] <- -99  
  #return(df)
#}

#replaceNaWithMinus99forWS1_WS2_WS4_WS8_WS3 <- function(df.MICS_HH){
  #df <- replaceNaWithMinus99(df,WS1_mainWaterSourceDrink)
  #df <- replaceNaWithMinus99(df,WS2_mainWaterSourceOther)
  #df <- replaceNaWithMinus99(df,WS4_timeToCollect)  
  #df <- replaceNaWithMinus99(df,WS8_whyInsufficient)
  #df <- replaceNaWithMinus99(df,WS3_Wslocation) 
  #return(df.MICS_HH)
#}

renameDuplicateHH7RegionNamesFromDifferentCountries <- function(df){
  df$HH7_region[df$HH7_region == "Central" & df$country == "Paraguay"] <- "Central Paraguay"
  df$HH7_region[df$HH7_region == "Central" & df$country == "Ghana"] <- "Central Ghana"
  df$HH7_region[df$HH7_region == "NORD OUEST" & df$country == "Tunisia"] <- "NORD OUEST Tunisia"
  df$HH7_region[df$HH7_region == "NORD OUEST" & df$country == "Algeria"] <- "NORD OUEST Algeria"
  return(df)
}
  
  
createAccessibilityIndicator <- function(df){
    df<- df %>% 
    mutate(Accessible = ifelse(
        (  WS4_timeToCollect == 0 #fetching water takes 0 minutes
         | WS3_Wslocation == 1 #water source is dwelling
         | WS3_Wslocation == 2 #water source is on plot 
         | WS1_mainWaterSourceDrink == 2 #primary drinking water source water is improved and on plot
         | WS2_mainWaterSourceOther == 2),#secondary drinking water source is improved and on plot 
      "1", "0"))
    return(df)
}

createImprovedAccessibleIndicator<- function(df){
    df <- df %>% 
    mutate(ImprovedAccessible = 
          ifelse(WS1_mainWaterSourceDrink  == 2 |
          (WS1_mainWaterSourceDrink == 1 & Accessible == 1) |
          (WS1_mainWaterSourceDrink == 3 & Accessible == 1), "1", "0")) 
  return(df)
}

createSMDWIndicator <- function(df){
    df <- df %>% 
    mutate(SMDW = ifelse( WQ27_sourcewaterBIN== 0 & #source water has no E.coli
                          ImprovedAccessible == 1 &  #improved and either main or secondary source is on premices
                          WS7_sufficiency == 0,  # no insufficiency reported or known
                          "1", "0"))
  return(df)
}

creatingSMDWIndicators_forTestSet <- function(df.MICS_HH){
  df.MICS_HH_WithNa <- replaceMinus99WithNa(df.MICS_HH)
  df.MICS_HH_WithNaRename <- renameVariables(df.MICS_HH_WithNa)
  df.MICS_HH_WithNaRename_chr <- makeWS1_WS2_WS4_WS8_WS3ToCharacter(df.MICS_HH_WithNaRename)
  df.MICS_HH_ReplacedNa<-replaceNaWithMinus99forWS1_WS2_WS4_WS8_WS3(df.MICS_HH_WithNaRename_chr)
  df.MICS_HH_WithAccessibility<- createAccessibilityIndicator(df.MICS_HH_ReplacedNa)
  df.MICS_HH_WithAccessibilityWithNA <- replaceMinus99WithNa(df.MICS_HH_WithAccessibility)
  df.MICS_HH_SMDWvariablesWithoutNA <- df.MICS_HH_WithAccessibilityWithNA %>%  
    select("Accessible","country","WQ27_sourcewaterBIN","WS7_sufficiency","HH7_region","HH48","WS1_mainWaterSourceDrink","wqsweight") %>% na.omit()  
  df.MICS_HH_SMDWvariablesWithImprovedAccessibilityWithoutNA <-createImprovedAccessibleIndicator(df.MICS_HH_SMDWvariablesWithoutNA)
  df.MICS_HH_SMDW <- createSMDWIndicator(df.MICS_HH_SMDWvariablesWithImprovedAccessibilityWithoutNA)
  df.MICS_HH_SMDW <- df.MICS_HH_SMDW %>% select("country","HH7_region","HH48","wqsweight","SMDW")
  return(df.MICS_HH_SMDW)
}

creatingSMDWIndicators_toJoinWithClimateVariables <- function(df.MICS_HH){
  df.MICS_HH_WithNa <- replaceMinus99WithNa(df.MICS_HH)
  df.MICS_HH_WithNaRename <- renameVariables(df.MICS_HH_WithNa)
  df.MICS_HH_WithNaRename_chr <- makeWS1_WS2_WS4_WS8_WS3ToCharacter(df.MICS_HH_WithNaRename)
  df.MICS_HH_ReplacedNa<-replaceNaWithMinus99forWS1_WS2_WS4_WS8_WS3(df.MICS_HH_WithNaRename_chr)
  df.MICS_HH_WithAccessibility<- createAccessibilityIndicator(df.MICS_HH_ReplacedNa)
  df.MICS_HH_WithAccessibilityWithNA <- replaceMinus99WithNa(df.MICS_HH_WithAccessibility)
  df.MICS_HH_SMDWvariablesWithoutNA <- df.MICS_HH_WithAccessibilityWithNA %>%  
    select("Accessible","country","WQ27_sourcewaterBIN","WS7_sufficiency","HH7_region","HH48","WS1_mainWaterSourceDrink","wqsweight","HH1","HH2") %>% na.omit()  
  df.MICS_HH_SMDWvariablesWithImprovedAccessibilityWithoutNA <-createImprovedAccessibleIndicator(df.MICS_HH_SMDWvariablesWithoutNA)
  df.MICS_HH_SMDW <- createSMDWIndicator(df.MICS_HH_SMDWvariablesWithImprovedAccessibilityWithoutNA)
  df.MICS_HH_SMDW <- df.MICS_HH_SMDW %>% select("country","HH7_region","HH48","wqsweight","SMDW","HH1","HH2")
  return(df.MICS_HH_SMDW)
}

creatingSMDWIndicators <- function(df.MICS_HH){
    df.MICS_HH_WithNa <- replaceMinus99WithNa(df.MICS_HH)
    df.MICS_HH_WithNaRename <- renameVariables(df.MICS_HH_WithNa)
    df.MICS_HH_WithNaRename_chr <- makeWS1_WS2_WS4_WS8_WS3ToCharacter(df.MICS_HH_WithNaRename)
    df.MICS_HH_ReplacedNa<-replaceNaWithMinus99forWS1_WS2_WS4_WS8_WS3(df.MICS_HH_WithNaRename_chr)
    df.MICS_HH_WithAccessibility<- createAccessibilityIndicator(df.MICS_HH_ReplacedNa)
    df.MICS_HH_WithAccessibilityWithNA <- replaceMinus99WithNa(df.MICS_HH_WithAccessibility)
    df.MICS_HH_SMDWvariablesWithoutNA <- df.MICS_HH_WithAccessibilityWithNA %>%  
    select("Accessible","country","WQ27_sourcewaterBIN","WS7_sufficiency","HH7_region","HH48","WS1_mainWaterSourceDrink","wqsweight") %>% na.omit()  
    df.MICS_HH_SMDWvariablesWithImprovedAccessibilityWithoutNA <-createImprovedAccessibleIndicator(df.MICS_HH_SMDWvariablesWithoutNA)
    df.MICS_HH_SMDW <- createSMDWIndicator(df.MICS_HH_SMDWvariablesWithImprovedAccessibilityWithoutNA)
    df.MICS_HH_SMDW <- df.MICS_HH_SMDW %>% select("country","HH7_region","HH48","wqsweight","SMDW")
    return(df.MICS_HH_SMDW)
}

createIndicatorForRegionalSMDWCoverage_forTestSet <- function(df.MICS_SMDW_FullTestSet) { 
  df.MICS_HH_SMDW <- renameDuplicateHH7RegionNamesFromDifferentCountries(df.MICS_SMDW_FullTestSet)
  df.MICS_HH_SMDW <-creatingColumnWithWeightedHouseholdMemberUsingSourceWaterSampleWeight(df.MICS_HH_SMDW)
  df.MICS_HH_SMDW <-createColumnWithNumberOfTotalRegionalHouseholds(df.MICS_HH_SMDW)
  df.MICS_HH_SMDW <-countWeightedHHMembersByRegion(df.MICS_HH_SMDW)
  df.MICS_HH_SMDW_FilteredForSMDW <- FilterForSMDWandCountWeightedHHMembers(df.MICS_HH_SMDW)
  df.MICS_HH_SMDW_FilteredForSMDW$SMDWcoverageAtRegionalLevel <- creatingRegionalProportionOfPopulationWithSMDWIndicator(df.MICS_HH_SMDW_FilteredForSMDW)
  df.MICS_HH_SMDWwithSMDWHouldholdCoverage <-creatingUnweightedPercentageOfSMDWHousholdCoverage(df.MICS_HH_SMDW)
  SMDW_RegionalCoverage <- df.MICS_HH_SMDWwithSMDWHouldholdCoverage  %>% 
    left_join(df.MICS_HH_SMDW_FilteredForSMDW, by = c("HH7_region"="HH7_region")) %>%
    select("SMDWcoverageAtRegionalLevel", "HH7_region", "country.x", "HouseholdsInRegion.Freq.x") 
  SMDW_RegionalCoverage$SMDWcoverageAtRegionalLevel[is.na(SMDW_RegionalCoverage$SMDWcoverageAtRegionalLevel)] <- 0
  return(SMDW_RegionalCoverage)
}

createIndicatorForRegionalSMDWCoverage <- function(df.MICS_HH_SMDW) { 
  df.MICS_HH_SMDW <- renameDuplicateHH7RegionNamesFromDifferentCountries(df.MICS_HH_SMDW)
  df.MICS_HH_SMDW <-creatingColumnWithWeightedHouseholdMemberUsingSourceWaterSampleWeight(df.MICS_HH_SMDW)
  df.MICS_HH_SMDW <-createColumnWithNumberOfTotalRegionalHouseholds(df.MICS_HH_SMDW)
  df.MICS_HH_SMDW <-countWeightedHHMembersByRegion(df.MICS_HH_SMDW)
  df.MICS_HH_SMDW_FilteredForSMDW <- FilterForSMDWandCountWeightedHHMembers(df.MICS_HH_SMDW)
  df.MICS_HH_SMDW_FilteredForSMDW$SMDWcoverageAtRegionalLevel <- creatingRegionalProportionOfPopulationWithSMDWIndicator(df.MICS_HH_SMDW_FilteredForSMDW)
  df.MICS_HH_SMDWwithSMDWHouldholdCoverage <-creatingUnweightedPercentageOfSMDWHousholdCoverage(df.MICS_HH_SMDW)
  SMDW_RegionalCoverage <- df.MICS_HH_SMDWwithSMDWHouldholdCoverage  %>% 
    left_join(df.MICS_HH_SMDW_FilteredForSMDW, by = c("HH7_region"="HH7_region")) %>%
    select(all_of("SMDWcoverageAtRegionalLevel"),all_of("HH7_region"),all_of("country.x"), all_of("HouseholdsInRegion.Freq.x")) 
  SMDW_RegionalCoverage$SMDWcoverageAtRegionalLevel[is.na(SMDW_RegionalCoverage$SMDWcoverageAtRegionalLevel)] <- 0
  return(SMDW_RegionalCoverage)
}


createDataFrameWithEcoliIndicator <- function(df){
  df <- renameVariables(df)
  df <- df %>% select("country","HH7_region","HH48","wqsweight","WQ27_sourcewaterBIN","HH5Y") %>% na.omit()
  return(df)
}

createDataFrameWithEcoliIndicator_design <- function(df) {
  df <- renameVariables(df)
  
  df %>%
    dplyr::select(
      country,
      HH7_region,
      HH48,
      wqsweight,
      WQ27_sourcewaterBIN,
      HH5Y,
      HH1,     # PSU / cluster
      HH6      # stratum; remove this line if not available
    ) %>%
    tidyr::drop_na(
      country,
      HH7_region,
      HH48,
      wqsweight,
      WQ27_sourcewaterBIN,
      HH5Y,
      HH1
    )
}

createDataFrameWithmainWaterSourceType <- function(df){
  df <- renameVariables(df)
  df <-renameDuplicateHH7RegionNamesFromDifferentCountries(df)
  df <- df %>% select("country","HH7_region","HH48","hhweight","WS1_mainWaterSourceDrink") %>% na.omit()
  return(df)
}

createDataFrameWithAvailabilty <- function(df){
  df <- renameVariables(df)
  df <-renameDuplicateHH7RegionNamesFromDifferentCountries(df)
  df <- df %>% select("country","HH7_region","HH48","hhweight","WS7_sufficiency") %>% na.omit()
  return(df)
}

createDataFrameWithAccessibilityIndicator <- function(df){
  df <- replaceMinus99WithNa(df)
  df <- renameVariables(df)
  df <- makeWS1_WS2_WS4_WS8_WS3ToCharacter(df)
  df<-replaceNaWithMinus99forWS1_WS2_WS4_WS8_WS3(df)
  df<- createAccessibilityIndicator(df)
  df <-renameDuplicateHH7RegionNamesFromDifferentCountries(df)
  df <- replaceMinus99WithNa(df)
  df <- df %>%  
    select("Accessible","country","HH7_region","HH48","hhweight") %>% na.omit()  
  return(df)
}


#No longer needed:
#creatingImprovedAccessible_forCongoAndCotedIvoire <- function(df.MICS_HH){
  #df.MICS_HH_WithNa <- replaceMinus99WithNa(df.MICS_HH)
  #df.MICS_HH_WithNaRename <- renameVariables(df.MICS_HH_WithNa)
  #df.MICS_HH_WithNaRename_chr <- makeWS1_WS2_WS4_WS8_WS3ToCharacter(df.MICS_HH_WithNaRename)
  #df.MICS_HH_ReplacedNa<-replaceNaWithMinus99forWS1_WS2_WS4_WS8_WS3(df.MICS_HH_WithNaRename_chr)
  #df.MICS_HH_WithAccessibility<- createAccessibilityIndicator(df.MICS_HH_ReplacedNa)
  #df.MICS_HH_WithAccessibilityWithNA <- replaceMinus99WithNa(df.MICS_HH_WithAccessibility)
  #df.MICS_HH_WithImprovedAccessibility <-createImprovedAccessibleIndicator(df.MICS_HH_WithAccessibilityWithNA)
  #return(df.MICS_HH_WithImprovedAccessibility)
#}


creatingColumnWithWeightedHouseholdMemberUsingSourceWaterSampleWeight <- function(df){
    df$HH48_wqsweight <- as.numeric(df$HH48)*as.numeric(df$wqsweight)
    return(df)
}

creatingColumnWithWeightedHouseholdMemberUsing_hhweight <- function(df){
  df$HH48_hhweight <- as.numeric(df$HH48)*as.numeric(df$hhweight)
  return(df)
}

createColumnWithNumberOfTotalRegionalHouseholds <- function(df) {
  df %>%
    dplyr::group_by(country, HH7_region) %>%
    dplyr::mutate(HouseholdsInRegion = dplyr::n()) %>%
    dplyr::ungroup()
}

createColumnWithNumberOfTotalCountryHouseholds <-function(df){
  df <- transform(df, HouseholdsInCountry = table(country)[country])
  df <- df %>% select(-"HouseholdsInCountry.country")
  return(df)
}


countWeightedHHMembersByRegion <- function(df) {
  df %>%
    dplyr::group_by(country, HH7_region) %>%
    dplyr::mutate(
      HouseholdMembersInRegion = sum(HH48_wqsweight, na.rm = TRUE)
    ) %>%
    dplyr::ungroup()
}

count_wqsWeightedHHMembersByCountry<- function(df){
  #detach("package:plyr")
  df <- df %>%
    dplyr::group_by(country) %>%
    mutate(HouseholdMembersInCountry = sum(HH48_wqsweight))
  return(df)
}

count_hhWeighted_HHMembersByRegion<- function(df){
  #detach("package:plyr")
  df <- df %>%
    dplyr::group_by(HH7_region) %>%
    mutate(HouseholdMembersInRegion = sum(HH48_hhweight))
  return(df)
}

count_hhWeighted_HHMembersByCountry<- function(df){
  #detach("package:plyr")
  df <- df %>%
    dplyr::group_by(country) %>%
    mutate(HouseholdMembersInCountry = sum(HH48_hhweight))
  return(df)
}

count_regionsByCountry<- function(df){
  df %>% 
    group_by(country.x) %>%
    summarise(number = n())
  return(df)
}

FilterForSMDWandCountWeightedHHMembers <- function(df) {
  df %>%
    dplyr::filter(SMDW == "1") %>%
    dplyr::group_by(country, HH7_region) %>%
    dplyr::mutate(
      HHmembers_withSMDW = sum(HH48_wqsweight, na.rm = TRUE)
    ) %>%
    dplyr::ungroup() %>%
    dplyr::distinct(country, HH7_region, .keep_all = TRUE)
}

FilterForSMDWandCountWeightedHHMembersInCountry <-function(df){
  df <- df %>%
    filter(SMDW == "1") %>%
    dplyr::group_by(country) %>%
    mutate(HHmembers_withSMDW = sum(HH48_wqsweight)) %>%
    distinct(country, .keep_all = TRUE)
  
  return(df)
}

FilterForFreeOfEcoliAndCountWeightedHHMembers <- function(df) {
  df %>%
    dplyr::filter(WQ27_sourcewaterBIN == "0" | WQ27_sourcewaterBIN == 0) %>%
    dplyr::group_by(country, HH7_region) %>%
    dplyr::mutate(
      HHmembers_NoEcoli = sum(HH48_wqsweight, na.rm = TRUE)
    ) %>%
    dplyr::ungroup() %>%
    dplyr::distinct(country, HH7_region, .keep_all = TRUE)
}

FilterForFreeOfEcoliAndCountWeightedHHMembersInCountry <-function(df){
  df <- df %>%
    filter(WQ27_sourcewaterBIN == "0") %>%
    dplyr::group_by(country) %>%
    mutate(HHmembers_NoEcoliCountry = sum(HH48_wqsweight)) %>%
    distinct(country, .keep_all = TRUE)
  
  return(df)
}

FilterForAccessAndCountWeightedHHMembers <-function(df){
  df <- df %>%
    filter(Accessible == "1") %>%
    dplyr::group_by(HH7_region) %>%
    mutate(HHmembersWithAccess = sum(HH48_hhweight)) %>%
    distinct(HH7_region, .keep_all = TRUE)
  
  return(df)
}

FilterForAccessAndCountWeightedHHMembersInCountry <-function(df){
  df <- df %>%
    filter(Accessible == "1") %>%
    dplyr::group_by(country) %>%
    mutate(HHmembersWithAccess = sum(HH48_hhweight)) %>%
    distinct(country, .keep_all = TRUE)
  
  return(df)
}

FilterForAvailableAndCountWeightedHHMembers <-function(df){
  df <- df %>%
    filter(WS7_sufficiency == "0") %>%
    dplyr::group_by(HH7_region) %>%
    mutate(HHmembersWaterAvailable = sum(HH48_hhweight)) %>%
    distinct(HH7_region, .keep_all = TRUE)
  
  return(df)
}

FilterForAvailableAndCountWeightedHHMembersInCountry <-function(df){
  df <- df %>%
    filter(WS7_sufficiency == "0") %>%
    dplyr::group_by(country) %>%
    mutate(HHmembersWaterAvailable = sum(HH48_hhweight)) %>%
    distinct(country, .keep_all = TRUE)
  
  return(df)
}

FilterForImprovedSourceAndCountWeightedHHMembers <-function(df){
  df <- df %>%
    filter(WS1_mainWaterSourceDrink == "1"|
             WS1_mainWaterSourceDrink == "2"|
           WS1_mainWaterSourceDrink == "3") %>%
    dplyr::group_by(HH7_region) %>%
    mutate(HHmembersImproved = sum(HH48_hhweight)) %>%
    distinct(HH7_region, .keep_all = TRUE)
  
  return(df)
}

FilterForImprovedSourceAndCountWeightedHHMembersInCountry <-function(df){
  df <- df %>%
    filter(WS1_mainWaterSourceDrink == "1"|
             WS1_mainWaterSourceDrink == "2"|
             WS1_mainWaterSourceDrink == "3") %>%
    dplyr::group_by(country) %>%
    mutate(HHmembersImproved = sum(HH48_hhweight)) %>%
    distinct(country, .keep_all = TRUE)
  
  return(df)
}



creatingRegionalProportionOfPopulationWithSMDWIndicator<- function(df){
df <- df$HHmembers_withSMDW/df$HouseholdMembersInRegion
return(df)
}

creatingCountryProportionOfPopulationWithSMDWIndicator<- function(df){
  df <- df$HHmembers_withSMDW/df$HouseholdMembersInCountry
  return(df)
}

creatingRegionalProportionOfPopulationWithNoEcoliInWater<- function(df){
  df <- df$HHmembers_NoEcoli/df$HouseholdMembersInRegion
  return(df)
}

creatingCountryProportionOfPopulationWithNoEcoliInWater<- function(df){
  df <- df$HHmembers_NoEcoliCountry/df$HouseholdMembersInCountry
  return(df)
}

creatingRegionalProportionOfPopulationWithAccess<- function(df){
  df <- df$HHmembersWithAccess/df$HouseholdMembersInRegion
  return(df)
}

creatingCountryProportionOfPopulationWithAccess<- function(df){
  df <- df$HHmembersWithAccess/df$HouseholdMembersInCountry
  return(df)
}

creatingRegionalProportionOfPopulationWithAvailability<- function(df){
  df <- df$HHmembersWaterAvailable/df$HouseholdMembersInRegion
  return(df)
}

creatingCountryProportionOfPopulationWithAvailability<- function(df){
  df <- df$HHmembersWaterAvailable/df$HouseholdMembersInCountry
  return(df)
}

creatingRegionalProportionOfPopulationWithImprovedSource<- function(df){
  df <- df$HHmembersImproved/df$HouseholdMembersInRegion
  return(df)
}

creatingCountryProportionOfPopulationWithImprovedSource<- function(df){
  df <- df$HHmembersImproved/df$HouseholdMembersInCountry
  return(df)
}


creatingUnweightedPercentageOfSMDWHousholdCoverage <- function(df) {
  df %>%
    dplyr::group_by(country, HH7_region) %>%
    dplyr::mutate(
      pct.SMDWHH = mean(SMDW == "1", na.rm = TRUE)
    ) %>%
    dplyr::ungroup() %>%
    dplyr::distinct(country, HH7_region, .keep_all = TRUE)
}


creatingUnweightedCountryPercentageOfSMDW<- function(df){
  df <-df %>%
    group_by(country) %>%
    mutate(pct.SMDWHH = mean(SMDW == "1")) %>%
    distinct(country, .keep_all = TRUE)
  return(df)
}

creatingUnweightedPercentageOfEcoliHousholdCoverage <- function(df) {
  df %>%
    dplyr::group_by(country, HH7_region) %>%
    dplyr::mutate(
      pct.No_Ecoli = mean(WQ27_sourcewaterBIN == "0" | WQ27_sourcewaterBIN == 0, na.rm = TRUE)
    ) %>%
    dplyr::ungroup() %>%
    dplyr::distinct(country, HH7_region, .keep_all = TRUE)
}

creatingUnweightedCountrydPercentageOfEcoliFree<- function(df){
  df <-df %>%
    group_by(country) %>%
    mutate(pct.No_Ecoli = mean(WQ27_sourcewaterBIN == "0")) %>%
    distinct(country, .keep_all = TRUE)
  return(df)
}

creatingUnweightedPercentageOfAccess<- function(df){
  df <-df %>%
    group_by(HH7_region) %>%
    mutate(pct.Access = mean(Accessible == "1")) %>%
    distinct(HH7_region, .keep_all = TRUE)
  return(df)
}

creatingUnweightedCountryPercentageOfAccess<- function(df){
  df <-df %>%
    group_by(country) %>%
    mutate(pct.Access = mean(Accessible == "1")) %>%
    distinct(country, .keep_all = TRUE)
  return(df)
}

creatingUnweightedPercentageOfAvailable<- function(df){
  df <-df %>%
    group_by(HH7_region) %>%
    mutate(pct.Available = mean(WS7_sufficiency == "0")) %>%
    distinct(HH7_region, .keep_all = TRUE)
  return(df)
}

creatingUnweightedCountryPercentageOfAvailable<- function(df){
  df <-df %>%
    group_by(country) %>%
    mutate(pct.Available = mean(WS7_sufficiency == "0")) %>%
    distinct(country, .keep_all = TRUE)
  return(df)
}

creatingUnweightedPercentageOfImprovedSource<- function(df){
  df <-df %>%
    group_by(HH7_region) %>%
    mutate(pct.Improved = mean(WS1_mainWaterSourceDrink == "1"|
                                 WS1_mainWaterSourceDrink == "2"|
                                 WS1_mainWaterSourceDrink == "3")) %>%
    distinct(HH7_region, .keep_all = TRUE)
  return(df)
}

creatingUnweightedCountryPercentageOfImprovedSource<- function(df){
  df <-df %>%
    group_by(country) %>%
    mutate(pct.Improved = mean(WS1_mainWaterSourceDrink == "1"|
                                 WS1_mainWaterSourceDrink == "2"|
                                 WS1_mainWaterSourceDrink == "3")) %>%
    distinct(country, .keep_all = TRUE)
  return(df)
}


createIndicatorForRegionalSMDWCoverage <- function(df.MICS_HH_SMDW) { 
  
  df.MICS_HH_SMDW <- renameDuplicateHH7RegionNamesFromDifferentCountries(
    df.MICS_HH_SMDW
  )
  
  df.MICS_HH_SMDW <- creatingColumnWithWeightedHouseholdMemberUsingSourceWaterSampleWeight(
    df.MICS_HH_SMDW
  )
  
  df.MICS_HH_SMDW <- createColumnWithNumberOfTotalRegionalHouseholds(
    df.MICS_HH_SMDW
  )
  
  df.MICS_HH_SMDW <- countWeightedHHMembersByRegion(
    df.MICS_HH_SMDW
  )
  
  df.MICS_HH_SMDW_FilteredForSMDW <- FilterForSMDWandCountWeightedHHMembers(
    df.MICS_HH_SMDW
  )
  
  df.MICS_HH_SMDW_FilteredForSMDW$SMDWcoverageAtRegionalLevel <- 
    creatingRegionalProportionOfPopulationWithSMDWIndicator(
      df.MICS_HH_SMDW_FilteredForSMDW
    )
  
  df.MICS_SMDW_RegionalProportion <- creatingUnweightedPercentageOfSMDWHousholdCoverage(
    df.MICS_HH_SMDW
  )
  
  SMDW_RegionalCoverage <- df.MICS_SMDW_RegionalProportion %>%
    dplyr::left_join(
      df.MICS_HH_SMDW_FilteredForSMDW %>%
        dplyr::select(
          country,
          HH7_region,
          SMDWcoverageAtRegionalLevel
        ),
      by = c("country", "HH7_region")
    ) %>%
    dplyr::select(
      SMDWcoverageAtRegionalLevel,
      HH7_region,
      country,
      HouseholdsInRegion,
      pct.SMDWHH
    ) %>%
    dplyr::rename(
      country.x = country,
      HouseholdsInRegion.Freq.x = HouseholdsInRegion
    )
  
  SMDW_RegionalCoverage$SMDWcoverageAtRegionalLevel[
    is.na(SMDW_RegionalCoverage$SMDWcoverageAtRegionalLevel)
  ] <- 0
  
  return(SMDW_RegionalCoverage)
}

createIndicatorForCountrySMDWCoverage <- function(df.MICS_HH_SMDW) { 
  df.MICS_HH_SMDW <- renameDuplicateHH7RegionNamesFromDifferentCountries(df.MICS_HH_SMDW)
  
  df.MICS_HH_SMDW <-creatingColumnWithWeightedHouseholdMemberUsingSourceWaterSampleWeight(df.MICS_HH_SMDW)
  
  df.MICS_HH_SMDW <-createColumnWithNumberOfTotalCountryHouseholds(df.MICS_HH_SMDW)
  
  df.MICS_HH_SMDW <-count_wqsWeightedHHMembersByCountry(df.MICS_HH_SMDW)
  
  df.MICS_HH_SMDW_FilteredForSMDW <- FilterForSMDWandCountWeightedHHMembersInCountry(df.MICS_HH_SMDW)
  
  df.MICS_HH_SMDW_FilteredForSMDW$SMDWcoverageAtCountryLevel <- creatingCountryProportionOfPopulationWithSMDWIndicator(df.MICS_HH_SMDW_FilteredForSMDW)
  
  df.MICS_HH_SMDWwithSMDWHouldholdCoverage <-creatingUnweightedCountryPercentageOfSMDW(df.MICS_HH_SMDW)
  
  SMDW_CountryCoverage <- df.MICS_HH_SMDWwithSMDWHouldholdCoverage  %>% 
    left_join(df.MICS_HH_SMDW_FilteredForSMDW, by = c("country"="country")) %>%
    select(all_of("SMDWcoverageAtCountryLevel"),all_of("country"), all_of("HouseholdsInCountry.Freq.x")) 
  
  SMDW_CountryCoverage$SMDWcoverageAtCountryLevel[is.na(SMDW_CountryCoverage$SMDWcoverageAtCountryLevel)] <- 0
  return(SMDW_CountryCoverage)
}


createIndicatorForRegionalProportionFreeOfEcoli <- function(df.MICS_Ecoli) { 
  
  df.MICS_Ecoli <- creatingColumnWithWeightedHouseholdMemberUsingSourceWaterSampleWeight(df.MICS_Ecoli)
  
  df.MICS_Ecoli <- createColumnWithNumberOfTotalRegionalHouseholds(df.MICS_Ecoli)
  
  df.MICS_Ecoli <- countWeightedHHMembersByRegion(df.MICS_Ecoli)
  
  df.MICS_Ecoli_FilteredForEcoli <- FilterForFreeOfEcoliAndCountWeightedHHMembers(df.MICS_Ecoli)
  
  df.MICS_Ecoli_FilteredForEcoli$No_EcoliAtRegionalLevel <- 
    creatingRegionalProportionOfPopulationWithNoEcoliInWater(df.MICS_Ecoli_FilteredForEcoli)
  
  df.MICS_NoEcoli_RegionalProportion <- creatingUnweightedPercentageOfEcoliHousholdCoverage(df.MICS_Ecoli)
  
  EcoliFreeRegionalProportion <- df.MICS_NoEcoli_RegionalProportion %>% 
    dplyr::left_join(
      df.MICS_Ecoli_FilteredForEcoli %>%
        dplyr::select(country, HH7_region, No_EcoliAtRegionalLevel),
      by = c("country", "HH7_region")
    ) %>%
    dplyr::select(
      No_EcoliAtRegionalLevel,
      HH7_region,
      country,
      HouseholdsInRegion,
      HH5Y
    ) %>%
    dplyr::rename(
      country.x = country,
      HouseholdsInRegion.Freq.x = HouseholdsInRegion,
      HH5Y.x = HH5Y
    )
  
  EcoliFreeRegionalProportion$No_EcoliAtRegionalLevel[
    is.na(EcoliFreeRegionalProportion$No_EcoliAtRegionalLevel)
  ] <- 0
  
  return(EcoliFreeRegionalProportion)
}

createIndicatorForCountryProportionFreeOfEcoli <- function(df.MICS_Ecoli) { 
df.MICS_Ecoli <-creatingColumnWithWeightedHouseholdMemberUsingSourceWaterSampleWeight(df.MICS_Ecoli)

df.MICS_Ecoli  <-createColumnWithNumberOfTotalCountryHouseholds(df.MICS_Ecoli)

df.MICS_Ecoli  <- count_wqsWeightedHHMembersByCountry(df.MICS_Ecoli)

df.MICS_Ecoli_FilteredForEcoliFree <- FilterForFreeOfEcoliAndCountWeightedHHMembersInCountry(df.MICS_Ecoli)

df.MICS_Ecoli_FilteredForEcoliFree$No_EcoliAtCountryLevel <- creatingCountryProportionOfPopulationWithNoEcoliInWater(df.MICS_Ecoli_FilteredForEcoliFree)

df.MICS_NoEcoli_CountryProportion <-creatingUnweightedCountrydPercentageOfEcoliFree(df.MICS_Ecoli)

EcoliFreeCountryProportion <- df.MICS_NoEcoli_CountryProportion  %>% 
  left_join(df.MICS_Ecoli_FilteredForEcoliFree, by = c("country"="country")) %>%
  select(all_of("No_EcoliAtCountryLevel"),all_of("country"), all_of("HouseholdsInCountry.Freq.x")) 

EcoliFreeCountryProportion$No_EcoliAtCountryLevel[is.na(EcoliFreeCountryProportion$No_EcoliAtCountryLevel)] <- 0

return(EcoliFreeCountryProportion)
}


createIndicatorForRegionalWaterAccessibility <- function(df.MICS_Accessibility) {
  
  RegionalAccess <- df.MICS_Accessibility %>%
    dplyr::mutate(
      HH48_hhweight = as.numeric(HH48) * as.numeric(hhweight),
      accessible_water = dplyr::if_else(
        as.character(Accessible) == "1",
        1,
        0
      )
    ) %>%
    dplyr::group_by(country, HH7_region) %>%
    dplyr::summarise(
      HouseholdsInRegion.Freq.x = dplyr::n(),
      HouseholdMembersInRegion = sum(HH48_hhweight, na.rm = TRUE),
      HHmembersWithAccess = sum(HH48_hhweight * accessible_water, na.rm = TRUE),
      AccessAtRegionalLevel = dplyr::if_else(
        HouseholdMembersInRegion > 0,
        HHmembersWithAccess / HouseholdMembersInRegion,
        NA_real_
      ),
      pct.Access = mean(accessible_water == 1, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    dplyr::mutate(
      AccessAtRegionalLevel = dplyr::coalesce(AccessAtRegionalLevel, 0)
    ) %>%
    dplyr::rename(
      country.x = country
    ) %>%
    dplyr::select(
      AccessAtRegionalLevel,
      HH7_region,
      country.x,
      HouseholdsInRegion.Freq.x,
      pct.Access
    )
  
  return(RegionalAccess)
}


createIndicatorForCountryWaterAccessibility <-function(df.MICS_Accessibility){ 
  df.MICS_Accessibility <-creatingColumnWithWeightedHouseholdMemberUsing_hhweight(df.MICS_Accessibility)
  
  df.MICS_Accessibility  <-createColumnWithNumberOfTotalCountryHouseholds(df.MICS_Accessibility)
  
  df.MICS_Accessibility  <- count_hhWeighted_HHMembersByCountry(df.MICS_Accessibility)
  
  df.MICS_FilteredForAccessibility <- FilterForAccessAndCountWeightedHHMembersInCountry(df.MICS_Accessibility)
  
  df.MICS_FilteredForAccessibility$AccessAtCountryLevel <- creatingCountryProportionOfPopulationWithAccess(df.MICS_FilteredForAccessibility)
  
  df.MICS_Access_CountryProportion <-creatingUnweightedCountryPercentageOfAccess(df.MICS_Accessibility)
  
  CountryAccess <- df.MICS_Access_CountryProportion  %>% 
    left_join(df.MICS_FilteredForAccessibility, by = c("country"="country")) %>% select(all_of("AccessAtCountryLevel"),all_of("country"), all_of("HouseholdsInCountry.Freq.x")) 
  
  CountryAccess$AccessAtCountryLevel[is.na(CountryAccess$AccessAtCountryLevel)] <- 0
  return(CountryAccess)
}



createIndicatorForRegionalAvailability <- function(df.MICS_Availability) {
  
  Availability_RegionalProportion <- df.MICS_Availability %>%
    dplyr::mutate(
      HH48_hhweight = as.numeric(HH48) * as.numeric(hhweight),
      water_available = dplyr::if_else(
        as.character(WS7_sufficiency) == "0",
        1,
        0
      )
    ) %>%
    dplyr::group_by(country, HH7_region) %>%
    dplyr::summarise(
      HouseholdsInRegion.Freq.x = dplyr::n(),
      HouseholdMembersInRegion = sum(HH48_hhweight, na.rm = TRUE),
      HHmembersWaterAvailable = sum(HH48_hhweight * water_available, na.rm = TRUE),
      AvailableAtRegionalLevel = dplyr::if_else(
        HouseholdMembersInRegion > 0,
        HHmembersWaterAvailable / HouseholdMembersInRegion,
        NA_real_
      ),
      pct.Available = mean(water_available == 1, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    dplyr::mutate(
      AvailableAtRegionalLevel = dplyr::coalesce(AvailableAtRegionalLevel, 0)
    ) %>%
    dplyr::rename(
      country.x = country
    ) %>%
    dplyr::select(
      AvailableAtRegionalLevel,
      HH7_region,
      country.x,
      HouseholdsInRegion.Freq.x,
      pct.Available
    )
  
  return(Availability_RegionalProportion)
}


createIndicatorForCountryAvailability <- function(df.MICS_Availability) { 
  df.MICS_Availability <-creatingColumnWithWeightedHouseholdMemberUsing_hhweight(df.MICS_Availability)
  
  df.MICS_Availability  <-createColumnWithNumberOfTotalCountryHouseholds(df.MICS_Availability)
  
  df.MICS_Availability  <- count_hhWeighted_HHMembersByCountry(df.MICS_Availability)
  
  df.MICS_FilteredForAvailability <- FilterForAvailableAndCountWeightedHHMembersInCountry(df.MICS_Availability)
  
  df.MICS_FilteredForAvailability$AvailableAtCountryLevel <- creatingCountryProportionOfPopulationWithAvailability(df.MICS_FilteredForAvailability)
  
  df.MICS_Availability_CountryProportion <-creatingUnweightedCountryPercentageOfAvailable(df.MICS_Availability)
  
  Availability_CountryProportion <- df.MICS_Availability_CountryProportion  %>% 
    left_join(df.MICS_FilteredForAvailability, by = c("country"="country")) %>%
    select(all_of("AvailableAtCountryLevel"),all_of("country"), all_of("HouseholdsInCountry.Freq.x")) 
  
  Availability_CountryProportion$AvailableAtCountryLevel[is.na(Availability_CountryProportion$AvailableAtCountryLevel)] <- 0
  
  return(Availability_CountryProportion)
}



createIndicatorForRegionalWaterSourceType <- function(df.MICS_WaterSource) {
  
  Improved_RegionalProportion <- df.MICS_WaterSource %>%
    dplyr::mutate(
      HH48_hhweight = as.numeric(HH48) * as.numeric(hhweight),
      improved_source = dplyr::if_else(
        as.character(WS1_mainWaterSourceDrink) %in% c("1", "2", "3"),
        1,
        0
      )
    ) %>%
    dplyr::group_by(country, HH7_region) %>%
    dplyr::summarise(
      HouseholdsInRegion.Freq.x = dplyr::n(),
      HouseholdMembersInRegion = sum(HH48_hhweight, na.rm = TRUE),
      HHmembersImproved = sum(HH48_hhweight * improved_source, na.rm = TRUE),
      ImprovedAtRegionalLevel = dplyr::if_else(
        HouseholdMembersInRegion > 0,
        HHmembersImproved / HouseholdMembersInRegion,
        NA_real_
      ),
      pct.Improved = mean(improved_source == 1, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    dplyr::mutate(
      ImprovedAtRegionalLevel = dplyr::coalesce(ImprovedAtRegionalLevel, 0)
    ) %>%
    dplyr::rename(
      country.x = country
    ) %>%
    dplyr::select(
      ImprovedAtRegionalLevel,
      HH7_region,
      country.x,
      HouseholdsInRegion.Freq.x,
      pct.Improved
    )
  
  return(Improved_RegionalProportion)
}

createIndicatorForCountryWaterSourceType <- function(df.MICS_WaterSource) { 
  df.MICS_WaterSource <-creatingColumnWithWeightedHouseholdMemberUsing_hhweight(df.MICS_WaterSource)
  
  df.MICS_WaterSource  <-createColumnWithNumberOfTotalCountryHouseholds(df.MICS_WaterSource)
  
  df.MICS_WaterSource  <- count_hhWeighted_HHMembersByCountry(df.MICS_WaterSource)
  
  df.MICS_FilteredForImprovedSource <- FilterForImprovedSourceAndCountWeightedHHMembersInCountry(df.MICS_WaterSource)
  
  df.MICS_FilteredForImprovedSource$ImprovedAtCountryLevel <- creatingCountryProportionOfPopulationWithImprovedSource(df.MICS_FilteredForImprovedSource)
  
  df.MICS_WaterSource_CountryProportion <-creatingUnweightedCountryPercentageOfImprovedSource(df.MICS_WaterSource)
  
  Improved_CountryProportion <- df.MICS_WaterSource_CountryProportion  %>% 
    left_join(df.MICS_FilteredForImprovedSource, by = c("country"="country")) %>%
    select(all_of("ImprovedAtCountryLevel"),all_of("country"), all_of("HouseholdsInCountry.Freq.x")) 
  
  Improved_CountryProportion$ImprovedAtCountryLevel[is.na(Improved_CountryProportion$ImprovedAtCountryLevel)] <- 0
  
  return(Improved_CountryProportion)
}


createColumnForCVfoldBasedOnCountries <- function(df, country_var = "country.x", countries_per_fold = 3, seed = 123) {
  
  if (!country_var %in% names(df)) {
    stop(paste("Column not found:", country_var))
  }
  
  if (!is.null(seed)) set.seed(seed)
  
  countries <- data.frame(
    country = unique(as.character(df[[country_var]])),
    stringsAsFactors = FALSE
  ) %>%
    filter(!is.na(country))
  
  countries <- countries[order(countries$country), , drop = FALSE]
  countries <- countries[sample(nrow(countries)), , drop = FALSE]
  
  countries$country_fold <- factor(
    ceiling(seq_len(nrow(countries)) / countries_per_fold)
  )
  
  names(countries)[1] <- country_var
  
  df <- dplyr::left_join(df, countries, by = country_var)
  
  return(df)
}

createColumnForCVfoldBasedOnCountriesInTestSet <- function(df){
  library(plyr)
  df$country_fold <- revalue(df$NAME_0,
                             c("Dominican Republic"="1", "Fiji"="2", "Malawi"="3", "Nepal"="4", "Samoa"="5","Vietnam"="6", "Benin"="7"))
  df$country_fold <- as.factor(df$country_fold)
  detach("package:plyr", unload = TRUE)
  return(df)
}

createColumnForCountryIncomeGroup <- function(df){
  library(plyr)
df$Income_group <- revalue(df$NAME_0,
c("Bangladesh"="3", "Gambia"="4", "Georgia"="2", "Ghana"="3", "Guinea-Bissau"="4", 
  "Iraq"="2", "Kosovo"="2", "Laos"="3", "Lesotho"="3", "Madagascar"="4", 
  "Mongolia"="3", "Nigeria"="3", "Pakistan"="3", "Suriname"="2", "Togo"="4",  
  "Tunisia"="3","Zimbabwe"="3","Chad"="4", "Guyana"="2", "Palestina"="3", 
  "Paraguay"="2", "Sierra Leone"="4", "Tonga"= "2", "Sao Tome and Principe"="3",
  "Algeria"="3","Central African Republic"="4","Kiribati"="3" ))
detach("package:plyr", unload = TRUE)
return(df)
}

extract_model_metrics <- function(model, test_h2o, model_name) {
  
  test_perf <- h2o::h2o.performance(model, newdata = test_h2o)
  
  tibble::tibble(
    model = model_name,
    xval_r2 = as.numeric(h2o::h2o.r2(model, xval = TRUE)),
    xval_mae = as.numeric(h2o::h2o.mae(model, xval = TRUE)),
    xval_rmse = as.numeric(h2o::h2o.rmse(model, xval = TRUE)),
    test_r2 = as.numeric(h2o::h2o.r2(test_perf)),
    test_mae = as.numeric(h2o::h2o.mae(test_perf)),
    test_rmse = as.numeric(h2o::h2o.rmse(test_perf))
  )
}

# ============================================================
# Workflow wrappers for safe drinking water subcomponents
# ============================================================
#
# These wrapper functions keep the original indicator calculations,
# but standardise the outputs so that E. coli, improved source,
# availability, and accessibility can all use the same covariate
# joining workflow.
#
# Outcome data sources:
#   - E. coli absence: water-quality surveys only
#   - Improved source: water-quality + other household surveys
#   - Availability: water-quality + other household surveys
#   - Accessibility: water-quality + other household surveys
#
#   The following functions call the original functions:
#     createDataFrameWithEcoliIndicator()
#     createIndicatorForRegionalProportionFreeOfEcoli()
#     createDataFrameWithmainWaterSourceType()
#     createIndicatorForRegionalWaterSourceType()
#     createDataFrameWithAvailabilty()
#     createIndicatorForRegionalAvailability()
#     createDataFrameWithAccessibilityIndicator()
#     createIndicatorForRegionalWaterAccessibility()
#


add_missing_columns_for_outcomes <- function(df, cols) {
  missing_cols <- setdiff(cols, names(df))
  
  for (col in missing_cols) {
    df[[col]] <- NA
  }
  
  df
}


# ============================================================
# Harmonise household country/region names for modelling
# ============================================================

harmonise_household_country_names_for_modelling <- function(df) {
  df %>%
    dplyr::mutate(
      country = dplyr::case_when(
        country == "Sao Tome and Principe" ~ "São Tomé and Príncipe",
        country == "Lao PDR" ~ "Lao People's Democratic Republic",
        country == "West Bank and Gaza" ~ "Palestina",
        TRUE ~ country
      )
    )
}

harmonise_household_country_region_names_for_modelling <- function(df) {
  df %>%
    harmonise_household_country_names_for_modelling() %>%
    dplyr::mutate(
      HH7_region = stringr::str_squish(as.character(HH7_region))
    )
}

harmonise_household_regions_for_modelling <- 
  harmonise_household_country_region_names_for_modelling




prepare_household_data_for_subcomponents <- function(df) {
  # Standardises variable names and region names.
  # The original outcome functions are still used later.
  
  df %>%
    replaceMinus99WithNa() %>%
    renameVariables() %>%
    harmonise_household_regions_for_modelling() %>%
    renameDuplicateHH7RegionNamesFromDifferentCountries()
}

make_year_lookup_from_prepared_household_data <- function(df) {
  # Creates one analysis year per country.
  # This follows your previous E. coli workflow, where analysis_year
  # was assigned as the minimum cleaned survey year within each country.
  
  df %>%
    dplyr::mutate(
      HH5Y_clean = standardise_survey_year(country, HH5Y)
    ) %>%
    dplyr::group_by(country) %>%
    dplyr::summarise(
      analysis_year = min(HH5Y_clean, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    dplyr::mutate(
      analysis_year = dplyr::if_else(
        is.infinite(analysis_year),
        NA_integer_,
        as.integer(analysis_year)
      )
    )
}

make_country_year_lookup <- function(df) {
  # The original E. coli code assigns one analysis year per country.
  # This preserves that structure for all subcomponents.
  
  df %>%
    dplyr::mutate(
      HH5Y_clean = standardise_survey_year(country, HH5Y)
    ) %>%
    dplyr::group_by(country) %>%
    dplyr::summarise(
      analysis_year = min(HH5Y_clean, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    dplyr::mutate(
      analysis_year = dplyr::if_else(
        is.infinite(analysis_year),
        NA_integer_,
        as.integer(analysis_year)
      )
    )
}



make_ecoli_regional_outcome <- function(df_hh_water_quality) {
  # E. coli outcome.
  # Data source: water-quality surveys only.
  # Original calculation and weighting are kept unchanged.
  
  year_lookup <- make_year_lookup_from_raw_household_data(
    df = df_hh_water_quality,
    manual_analysis_year_fixes = manual_analysis_year_fixes_ecoli
  )
  
  ecoli_original <- df_hh_water_quality %>%
    createDataFrameWithEcoliIndicator() %>%
    harmonise_household_country_region_names_for_modelling() %>%
    renameDuplicateHH7RegionNamesFromDifferentCountries() %>%
    createIndicatorForRegionalProportionFreeOfEcoli()
  
  standardise_regional_outcome_table(
    outcome_df = ecoli_original,
    outcome_type = "ecoli_free",
    outcome_value_col = "No_EcoliAtRegionalLevel",
    year_lookup = year_lookup
  )
}


make_improved_source_regional_outcome <- function(df_hh_full) {
  # Improved drinking water source.
  # Data source: water-quality surveys + other household surveys.
  # Original calculation and weighting are kept unchanged.
  
  year_lookup <- make_year_lookup_from_raw_household_data(
    df_hh_full
  )
  
  improved_original <- df_hh_full %>%
    createDataFrameWithmainWaterSourceType() %>%
    harmonise_household_country_region_names_for_modelling() %>%
    renameDuplicateHH7RegionNamesFromDifferentCountries() %>%
    createIndicatorForRegionalWaterSourceType()
  
  standardise_regional_outcome_table(
    outcome_df = improved_original,
    outcome_type = "improved_source",
    outcome_value_col = "ImprovedAtRegionalLevel",
    year_lookup = year_lookup
  )
}


make_availability_regional_outcome <- function(df_hh_full) {
  # Drinking water availability.
  # Data source: water-quality surveys + other household surveys.
  # Original calculation and weighting are kept unchanged.
  
  year_lookup <- make_year_lookup_from_raw_household_data(
    df_hh_full
  )
  
  availability_original <- df_hh_full %>%
    createDataFrameWithAvailabilty() %>%
    harmonise_household_country_region_names_for_modelling() %>%
    renameDuplicateHH7RegionNamesFromDifferentCountries() %>%
    createIndicatorForRegionalAvailability()
  
  standardise_regional_outcome_table(
    outcome_df = availability_original,
    outcome_type = "availability",
    outcome_value_col = "AvailableAtRegionalLevel",
    year_lookup = year_lookup
  )
}


make_accessibility_regional_outcome <- function(df_hh_full) {
  # Drinking water accessibility.
  # Data source: water-quality surveys + other household surveys.
  # Original calculation and weighting are kept unchanged.
  
  year_lookup <- make_year_lookup_from_raw_household_data(
    df_hh_full
  )
  
  accessibility_original <- df_hh_full %>%
    createDataFrameWithAccessibilityIndicator() %>%
    harmonise_household_country_region_names_for_modelling() %>%
    renameDuplicateHH7RegionNamesFromDifferentCountries() %>%
    createIndicatorForRegionalWaterAccessibility()
  
  standardise_regional_outcome_table(
    outcome_df = accessibility_original,
    outcome_type = "accessibility",
    outcome_value_col = "AccessAtRegionalLevel",
    year_lookup = year_lookup
  )
}

# ============================================================
# SMDW regional outcome wrapper
# ============================================================

make_smdw_regional_outcome <- function(df_hh_water_quality) {
  # SMDW outcome.
  # Data source: water-quality surveys only, because WQ27 is needed.
  # Uses the existing SMDW helper functions and standardises the output
  # to the same structure as the other model outcomes.
  
  year_lookup <- make_year_lookup_from_raw_household_data(
    df = df_hh_water_quality,
    manual_analysis_year_fixes = manual_analysis_year_fixes_ecoli
  )
  
  smdw_original <- df_hh_water_quality %>%
    creatingSMDWIndicators() %>%
    harmonise_household_country_region_names_for_modelling() %>%
    renameDuplicateHH7RegionNamesFromDifferentCountries() %>%
    createIndicatorForRegionalSMDWCoverage()
  
  standardise_regional_outcome_table(
    outcome_df = smdw_original,
    outcome_type = "smdw",
    outcome_value_col = "SMDWcoverageAtRegionalLevel",
    year_lookup = year_lookup
  )
}

# ============================================================
# Add number of PSUs as simple reliability weight
# ============================================================

# ------------------------------------------------------------
# Helper: count PSUs by country-region-year and join to outcome
# ------------------------------------------------------------

add_n_psu_weight <- function(hh_df, outcome_df, year_lookup) {
  
  psu_table <- hh_df %>%
    dplyr::select(
      dplyr::any_of(c(
        "country",
        "HH7",
        "HH7_region",
        "HH1",
        "HH6",
        "PSU",
        "stratum"
      ))
    ) %>%
    add_missing_columns(c("country", "HH7", "HH7_region", "HH1", "PSU")) %>%
    dplyr::mutate(
      HH7_region = dplyr::coalesce(
        as.character(HH7_region),
        as.character(HH7)
      )
    ) %>%
    harmonise_household_country_region_names_for_modelling() %>%
    renameDuplicateHH7RegionNamesFromDifferentCountries() %>%
    dplyr::left_join(
      year_lookup,
      by = "country"
    ) %>%
    dplyr::mutate(
      psu_id = dplyr::coalesce(
        as.character(PSU),
        as.character(HH1)
      )
    ) %>%
    dplyr::filter(
      !is.na(country),
      !is.na(HH7_region),
      !is.na(analysis_year),
      !is.na(psu_id)
    ) %>%
    dplyr::group_by(country, HH7_region, analysis_year) %>%
    dplyr::summarise(
      n_psu = dplyr::n_distinct(psu_id),
      .groups = "drop"
    ) %>%
    dplyr::mutate(
      n_psu_weight_raw = as.numeric(n_psu),
      n_psu_weight_scaled = n_psu_weight_raw /
        mean(n_psu_weight_raw, na.rm = TRUE)
    ) %>%
    dplyr::rename(
      country_outcome = country,
      HH7_region_outcome = HH7_region
    )
  
  outcome_df %>%
    dplyr::select(
      -dplyr::any_of(c(
        "n_psu",
        "n_psu_weight_raw",
        "n_psu_weight_scaled"
      ))
    ) %>%
    dplyr::left_join(
      psu_table,
      by = c(
        "country_outcome",
        "HH7_region_outcome",
        "analysis_year"
      )
    )
}
