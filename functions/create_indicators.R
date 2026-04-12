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
  df <- df %>% select("country","HH7_region","HH48","wqsweight","WQ27_sourcewaterBIN") %>% na.omit()
  return(df)
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

createColumnWithNumberOfTotalRegionalHouseholds <-function(df){
    df <- transform(df, HouseholdsInRegion = table(HH7_region)[HH7_region])
    df <- df %>% select(-"HouseholdsInRegion.HH7_region")
    return(df)
}

createColumnWithNumberOfTotalCountryHouseholds <-function(df){
  df <- transform(df, HouseholdsInCountry = table(country)[country])
  df <- df %>% select(-"HouseholdsInCountry.country")
  return(df)
}


countWeightedHHMembersByRegion<- function(df){
  #detach("package:plyr")
  df <- df %>%
    dplyr::group_by(HH7_region) %>%
    mutate(HouseholdMembersInRegion = sum(HH48_wqsweight))
  return(df)
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

FilterForSMDWandCountWeightedHHMembers <-function(df){
  df <- df %>%
    filter(SMDW == "1") %>%
    dplyr::group_by(HH7_region) %>%
    mutate(HHmembers_withSMDW = sum(HH48_wqsweight)) %>%
    distinct(HH7_region, .keep_all = TRUE)
  
return(df)
}

FilterForSMDWandCountWeightedHHMembersInCountry <-function(df){
  df <- df %>%
    filter(SMDW == "1") %>%
    dplyr::group_by(country) %>%
    mutate(HHmembers_withSMDW = sum(HH48_wqsweight)) %>%
    distinct(country, .keep_all = TRUE)
  
  return(df)
}

FilterForFreeOfEcoliAndCountWeightedHHMembers <-function(df){
  df <- df %>%
    filter(WQ27_sourcewaterBIN == "0") %>%
    dplyr::group_by(HH7_region) %>%
    mutate(HHmembers_NoEcoli = sum(HH48_wqsweight)) %>%
    distinct(HH7_region, .keep_all = TRUE)
  
  return(df)
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


creatingUnweightedPercentageOfSMDWHousholdCoverage<- function(df){
  df <-df %>%
  group_by(HH7_region) %>%
  mutate(pct.SMDWHH = mean(SMDW == "1")) %>%
  distinct(HH7_region, .keep_all = TRUE)
  return(df)
}

creatingUnweightedCountryPercentageOfSMDW<- function(df){
  df <-df %>%
    group_by(country) %>%
    mutate(pct.SMDWHH = mean(SMDW == "1")) %>%
    distinct(country, .keep_all = TRUE)
  return(df)
}

creatingUnweightedPercentageOfEcoliHousholdCoverage<- function(df){
  df <-df %>%
    group_by(HH7_region) %>%
    mutate(pct.No_Ecoli = mean(WQ27_sourcewaterBIN == "0")) %>%
    distinct(HH7_region, .keep_all = TRUE)
  return(df)
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
  df.MICS_Ecoli <-creatingColumnWithWeightedHouseholdMemberUsingSourceWaterSampleWeight(df.MICS_Ecoli)
  
  df.MICS_Ecoli  <-createColumnWithNumberOfTotalRegionalHouseholds(df.MICS_Ecoli)
  
  df.MICS_Ecoli  <- countWeightedHHMembersByRegion(df.MICS_Ecoli)
  
  df.MICS_Ecoli_FilteredForEcoli <- FilterForFreeOfEcoliAndCountWeightedHHMembers(df.MICS_Ecoli)
  
  df.MICS_Ecoli_FilteredForEcoli$No_EcoliAtRegionalLevel <- creatingRegionalProportionOfPopulationWithNoEcoliInWater(df.MICS_Ecoli_FilteredForEcoli)
  
  df.MICS_NoEcoli_RegionalProportion <-creatingUnweightedPercentageOfEcoliHousholdCoverage(df.MICS_Ecoli)
  
  EcoliFreeRegionalProportion <- df.MICS_NoEcoli_RegionalProportion  %>% 
    left_join(df.MICS_Ecoli_FilteredForEcoli, by = c("HH7_region"="HH7_region")) %>%
    select(all_of("No_EcoliAtRegionalLevel"),all_of("HH7_region"),all_of("country.x"), all_of("HouseholdsInRegion.Freq.x")) 
  
  EcoliFreeRegionalProportion$No_EcoliAtRegionalLevel[is.na(EcoliFreeRegionalProportion$No_EcoliAtRegionalLevel)] <- 0
  
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


createIndicatorForRegionalWaterAccessibility <-function(df.MICS_Accessibility){ 
df.MICS_Accessibility <-creatingColumnWithWeightedHouseholdMemberUsing_hhweight(df.MICS_Accessibility)

df.MICS_Accessibility  <-createColumnWithNumberOfTotalRegionalHouseholds(df.MICS_Accessibility)

df.MICS_Accessibility  <- count_hhWeighted_HHMembersByRegion(df.MICS_Accessibility)

df.MICS_FilteredForAccessibility <- FilterForAccessAndCountWeightedHHMembers(df.MICS_Accessibility)

df.MICS_FilteredForAccessibility$AccessAtRegionalLevel <- creatingRegionalProportionOfPopulationWithAccess(df.MICS_FilteredForAccessibility)

df.MICS_Access_RegionalProportion <-creatingUnweightedPercentageOfAccess(df.MICS_Accessibility)

RegionalAccess <- df.MICS_Access_RegionalProportion  %>% 
  left_join(df.MICS_FilteredForAccessibility, by = c("HH7_region"="HH7_region")) %>% select(all_of("AccessAtRegionalLevel"),all_of("HH7_region"),all_of("country.x"), all_of("HouseholdsInRegion.Freq.x")) 

RegionalAccess$AccessAtRegionalLevel[is.na(RegionalAccess$AccessAtRegionalLevel)] <- 0
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
  df.MICS_Availability <-creatingColumnWithWeightedHouseholdMemberUsing_hhweight(df.MICS_Availability)

  df.MICS_Availability  <-createColumnWithNumberOfTotalRegionalHouseholds(df.MICS_Availability)
  
  df.MICS_Availability  <- count_hhWeighted_HHMembersByRegion(df.MICS_Availability)
  
  df.MICS_FilteredForAvailability <- FilterForAvailableAndCountWeightedHHMembers(df.MICS_Availability)
  
  df.MICS_FilteredForAvailability$AvailableAtRegionalLevel <- creatingRegionalProportionOfPopulationWithAvailability(df.MICS_FilteredForAvailability)
  
  df.MICS_Availability_RegionalProportion <-creatingUnweightedPercentageOfAvailable(df.MICS_Availability)
  
  Availability_RegionalProportion <- df.MICS_Availability_RegionalProportion  %>% 
    left_join(df.MICS_FilteredForAvailability, by = c("HH7_region"="HH7_region")) %>%
    select(all_of("AvailableAtRegionalLevel"),all_of("HH7_region"),all_of("country.x"), all_of("HouseholdsInRegion.Freq.x")) 
  
  Availability_RegionalProportion$AvailableAtRegionalLevel[is.na(Availability_RegionalProportion$AvailableAtRegionalLevel)] <- 0
  
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
  df.MICS_WaterSource <-creatingColumnWithWeightedHouseholdMemberUsing_hhweight(df.MICS_WaterSource)
  
  df.MICS_WaterSource  <-createColumnWithNumberOfTotalRegionalHouseholds(df.MICS_WaterSource)
  
  df.MICS_WaterSource  <- count_hhWeighted_HHMembersByRegion(df.MICS_WaterSource)
  
  df.MICS_FilteredForImprovedSource <- FilterForImprovedSourceAndCountWeightedHHMembers(df.MICS_WaterSource)
  
  df.MICS_FilteredForImprovedSource$ImprovedAtRegionalLevel <- creatingRegionalProportionOfPopulationWithImprovedSource(df.MICS_FilteredForImprovedSource)
  
  df.MICS_WaterSource_RegionalProportion <-creatingUnweightedPercentageOfImprovedSource(df.MICS_WaterSource)
  
  Improved_RegionalProportion <- df.MICS_WaterSource_RegionalProportion  %>% 
    left_join(df.MICS_FilteredForImprovedSource, by = c("HH7_region"="HH7_region")) %>%
    select(all_of("ImprovedAtRegionalLevel"),all_of("HH7_region"),all_of("country.x"), all_of("HouseholdsInRegion.Freq.x")) 
  
  Improved_RegionalProportion$ImprovedAtRegionalLevel[is.na(Improved_RegionalProportion$ImprovedAtRegionalLevel)] <- 0
  
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


createColumnForCVfoldBasedOnCountries <- function(df){
  library(plyr)
  df$country_fold <- revalue(df$NAME_0,
c("Bangladesh"="1", "Gambia"="2", "Georgia"="3", "Ghana"="4", "Guinea-Bissau"="5","Iraq"="6", "Kosovo (under UNSC res. 1244)"="7", "Lao People's Democratic Republic"="8", "Lesotho"="9", 
  "Madagascar"="10","Mongolia"="11", "Nigeria"="12", "Pakistan"="13", "Suriname"="14", 
  "Togo"="15",  "Tunisia"="16","Zimbabwe"="17","Chad"="18", "Guyana"="19", 
  "State of Palestine"="20", "Paraguay"="21", "Sierra Leone"="22", "Tonga"= "23", 
  "Sao Tome and Principe"="24","Algeria"="25","Central African Republic"="26",
  "Kiribati"="27" ))
  df$country_fold <- as.factor(df$country_fold)
  detach("package:plyr", unload = TRUE)
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
