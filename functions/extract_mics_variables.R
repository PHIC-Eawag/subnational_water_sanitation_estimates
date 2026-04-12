#title: "Functions for extracting Variables from Survey data"


loadSurveys <- function(pathToSurveys){
  filenames <- list.files(path = pathToSurveys, full.names = FALSE)
  
  for (filename in filenames){
    name <- strsplit(filename, split = ".", fixed = TRUE)[[1]][1]
    dfCountrySurvey <- sjlabelled::read_spss(paste(pathToSurveys,"/",filename, sep=""))
    assign(name,dfCountrySurvey,envir = .GlobalEnv)
  }
}

extractStandardSurveyVariables <- function(hh_Survey){
  hh_Survey <- hh_Survey %>% 
    select("HH1","HH2","WQ27", "WS7", "WS3","HH7","HH6","WS1","HH48","WS4","wqsweight","WS2","hhweight", "WS8", "country", "HH5D", "HH5M", "HH5Y", "PSU", "stratum") 
  return(hh_Survey)
}

extractStandardSurveyVariables_psu_lowercaps <- function(hh_Survey){
  hh_Survey <- hh_Survey %>% 
    select("HH1","HH2","WQ27", "WS7", "WS3","HH7","HH6","WS1","HH48","WS4","wqsweight","WS2","hhweight", "WS8", "country", "HH5D", "HH5M", "HH5Y", "psu", "stratum") 
  names(hh_Survey)[names(hh_Survey) == 'psu'] <- 'PSU'
  return(hh_Survey)
}

extractStandardSurveyVariables_strata <- function(hh_Survey){
  hh_Survey <- hh_Survey %>% 
    select("HH1","HH2","WQ27", "WS7", "WS3","HH7","HH6","WS1","HH48","WS4","wqsweight","WS2","hhweight", "WS8", "country", "HH5D", "HH5M", "HH5Y", "PSU", "strata") 
  names(hh_Survey)[names(hh_Survey) == 'strata'] <- 'stratum'
  return(hh_Survey)
}

extractStandardSurveyVariables_stratum_SE <- function(hh_Survey){
  hh_Survey <- hh_Survey %>% 
    select("HH1","HH2","WQ27", "WS7", "WS3","HH7","HH6","WS1","HH48","WS4","wqsweight","WS2","hhweight", "WS8", "country", "HH5D", "HH5M", "HH5Y", "PSU", "stratum_SE") 
  names(hh_Survey)[names(hh_Survey) == 'stratum_SE'] <- 'stratum'
  return(hh_Survey)
}

extractVariablesFromBangladesh <- function(hh_Bangladesh){
  
  hh_Bangladesh_SMDW <- hh_Bangladesh %>% 
    select("HH1","HH2", "WQ27", "WS7", "WS3","HH7","HH6","WS1","HH48","WS4","wqeweight","WS2","hhweight", "WS8", "country","HH5D", "HH5M", "HH5Y", "PSU", "stratum") 
  names(hh_Bangladesh_SMDW)[names(hh_Bangladesh_SMDW) == 'wqeweight'] <- 'wqsweight'
  return(hh_Bangladesh_SMDW)
}

extractVariablesFromCongo <- function(hh_Congo){
  hh_Congo_SMDW <- hh_Congo %>%  
    select("HH1","HH2","WQ27", "WS3","HH7","HH6","WS1","WS4","WS2","hhweight","WS8","HH48", "country","HH5D", "HH5M", "HH5Y","PSU", "stratum")
  hh_Congo_SMDW$WS7 <- 0
  hh_Congo_SMDW$WS8 <- NA
  return(hh_Congo_SMDW)
}

extractVariablesFromSierraLeone <- function(hh_SierraLeone){
  hh_SierraLeone_SMDW <- hh_SierraLeone %>%  
    mutate(PSU = HH1) %>%
    select("HH1","HH2","WQ27","WS7", "WS3","HH7","HH6","WS1","WS4","WS2", "wqsweight","hhweight","WS8","HH48","country","HH5D","HH5M","HH5Y", "PSU","stratum")
  return(hh_SierraLeone_SMDW)
}

extractVariablesFromCote_dIvoire <- function(hh_Cote_dIvoire){
  hh_Cote_dIvoire_SMDW <- hh_Cote_dIvoire %>% 
    select("HH1","HH2","WQ31", "WS3","HH7","HH11","HH6","WS1","WS4","wqweight","WS2","hhweight", "country", "HH5D", "HH5M", "HH5Y","PSU", "stratum")
  hh_Cote_dIvoire_SMDW$WS7 <- NA
  names(hh_Cote_dIvoire_SMDW)[names(hh_Cote_dIvoire_SMDW) == 'WQ31'] <- 'WQ27'
  names(hh_Cote_dIvoire_SMDW)[names(hh_Cote_dIvoire_SMDW) == 'HH11'] <- 'HH48'
  names(hh_Cote_dIvoire_SMDW)[names(hh_Cote_dIvoire_SMDW) == 'wqweight'] <- 'wqsweight'
  hh_Cote_dIvoire_SMDW$WS8 <- NA
  return(hh_Cote_dIvoire_SMDW)
}
  

extractVariablesFromLesotho <- function(hh_Lesotho){
  hh_Lesotho_SMDW <- hh_Lesotho %>% 
    select("HH1","HH2", "WQ27", "WS7", "WS3","HH6","WS1","HH48","WS4","HH7A","wqsweight","WS2","hhweight","WS8", "country", "HH5D", "HH5M", "HH5Y","psu", "stratum")
  names(hh_Lesotho_SMDW)[names(hh_Lesotho_SMDW) == 'psu'] <- 'PSU'
  names(hh_Lesotho_SMDW)[names(hh_Lesotho_SMDW) == 'HH7A'] <- 'HH7'
  return(hh_Lesotho_SMDW)
}


extractVariablesFromNigeria <- function(hh_Nigeria){
  hh_Nigeria_SMDW <- hh_Nigeria %>% 
    select("HH1","HH2", "WQ23", "WS5A", "WS3","HH7","HH6","WS1","HH11","WS4A","wqsweight","WS2","hhweight", "country","HH5D", "HH5M", "HH5Y","PSU", "stratum") 
  names(hh_Nigeria_SMDW)[names(hh_Nigeria_SMDW) == 'WQ23'] <- 'WQ27'
  names(hh_Nigeria_SMDW)[names(hh_Nigeria_SMDW) == 'WS4A'] <- 'WS4'
  names(hh_Nigeria_SMDW)[names(hh_Nigeria_SMDW) == 'WS5A'] <- 'WS7'
  names(hh_Nigeria_SMDW)[names(hh_Nigeria_SMDW) == 'HH11'] <- 'HH48'
  hh_Nigeria_SMDW$WS8 <- NA
  return(hh_Nigeria_SMDW)
}

extractVariablesFromParaguay <- function(hh_Paraguay){
  hh_Paraguay_SMDW <- hh_Paraguay %>% 
    mutate(psu = HH1) %>%
    select("HH1","HH2", "WQ23", "WS5C", "WS3","HH7","HH6","WS1","HH11","WS4","paweight","WS2","hhweight", "country","HH5D", "HH5M", "HH5Y","psu", "strata2")
  names(hh_Paraguay_SMDW)[names(hh_Paraguay_SMDW) == 'psu'] <- 'PSU'
  names(hh_Paraguay_SMDW)[names(hh_Paraguay_SMDW) == 'strata2'] <- 'stratum'
  names(hh_Paraguay_SMDW)[names(hh_Paraguay_SMDW) == 'paweight'] <- 'wqsweight'
  names(hh_Paraguay_SMDW)[names(hh_Paraguay_SMDW) == 'WQ23'] <- 'WQ27'
  names(hh_Paraguay_SMDW)[names(hh_Paraguay_SMDW) == 'WS5C'] <- 'WS7'
  names(hh_Paraguay_SMDW)[names(hh_Paraguay_SMDW) == 'HH11'] <- 'HH48'
  hh_Paraguay_SMDW$WS8 <- NA
  return(hh_Paraguay_SMDW)
}

extractVariablesFromTuvalu <- function(hh_Tuvalu){
hh_Tuvalu_SMDW <- hh_Tuvalu %>% 
  select("HH1","HH2", "WQ27", "WS7", "WS3","HH7","HH6","WS1","HH48","WS4","wqsweight","WS2","hhweight", "country","HH5D", "HH5M", "HH5Y","PSU_SE", "stratum")
names(hh_Tuvalu_SMDW)[names(hh_Tuvalu_SMDW) == 'PSU_SE'] <- 'PSU'
hh_Tuvalu_SMDW$WS8 <- NA
return(hh_Tuvalu_SMDW)
}

extractVariableLabelsfromHH7 <- function(df){
  df <- df %>% surveytoolbox::extract_vallab("HH7")
  return(df)
}

extractVariableLabelsfromWS1 <- function(df){
  df <- df %>% surveytoolbox::extract_vallab("WS1")
  return(df)
}

replaceHH7_regionNameWithCorrespondingGADMNAme <- function(df){
  df$HH7_region = str_replace(df$HH7_region,"CORTES","CortÃƒÂ©s")
  df$HH7_region = str_replace(df$HH7_region,"SAN PEDRO SULA","CortÃƒÂ©s")
  df$HH7_region = str_replace(df$HH7_region,"DISTRITO CENTRAL","Francisco MorazÃƒÂ¡n")
  df$HH7_region = str_replace(df$HH7_region,"FRANCISCO MORAZAN","Francisco MorazÃƒÂ¡n")
  df$HH7_region = str_replace(df$HH7_region,"Bagh","Azad Kashmir")
  df$HH7_region = str_replace(df$HH7_region,"Bhimber","Azad Kashmir")
  df$HH7_region = str_replace(df$HH7_region,"Haveli","Azad Kashmir")
  df$HH7_region = str_replace(df$HH7_region,"Jhelum","Azad Kashmir")
  df$HH7_region = str_replace(df$HH7_region,"Kotli","Azad Kashmir")
  df$HH7_region = str_replace(df$HH7_region,"Mirpur","Azad Kashmir")
  df$HH7_region = str_replace(df$HH7_region,"Muzaffarabad","Azad Kashmir")
  df$HH7_region = str_replace(df$HH7_region,"Neelum","Azad Kashmir")
  df$HH7_region = str_replace(df$HH7_region,"Poonch","Azad Kashmir")
  df$HH7_region = str_replace(df$HH7_region,"Sudhnoti","Azad Kashmir")
  return(df)
}

replaceHH7NameWithCorrespondingGADMNAme <- function(df){
  df$HH7 = str_replace(df$HH7,"CORTES","CortÃƒÂ©s")
  df$HH7 = str_replace(df$HH7,"SAN PEDRO SULA","CortÃƒÂ©s")
  df$HH7 = str_replace(df$HH7,"DISTRITO CENTRAL","Francisco MorazÃƒÂ¡n")
  df$HH7 = str_replace(df$HH7,"FRANCISCO MORAZAN","Francisco MorazÃƒÂ¡n")
  df$HH7 = str_replace(df$HH7,"Bagh","Azad Kashmir")
  df$HH7 = str_replace(df$HH7,"Bhimber","Azad Kashmir")
  df$HH7 = str_replace(df$HH7,"Haveli","Azad Kashmir")
  df$HH7 = str_replace(df$HH7,"Jhelum","Azad Kashmir")
  df$HH7 = str_replace(df$HH7,"Kotli","Azad Kashmir")
  df$HH7 = str_replace(df$HH7,"Mirpur","Azad Kashmir")
  df$HH7 = str_replace(df$HH7,"Muzaffarabad","Azad Kashmir")
  df$HH7 = str_replace(df$HH7,"Neelum","Azad Kashmir")
  df$HH7 = str_replace(df$HH7,"Poonch","Azad Kashmir")
  df$HH7 = str_replace(df$HH7,"Sudhnoti","Azad Kashmir")
  return(df)
}



VariablesWhichWereFactorsAsCharacterToAvoidGenerationOfNA <-function(df){
  
  df$HH6 <- as.character(df$HH6)
  df$WS3 <- as.character(df$WS3) 
  df$HH6 <- as.character(df$HH6) 
  df$WQ27 <- as.character(df$WQ27) 
  df$WS1 <- as.character(df$WS1) 
  df$WS2 <- as.character(df$WS2)
  return(df)
}

replaceHH7LabelsWithRegionNames <- function(df, df_regionNames){
  df_regionNames$id <- as.factor(df_regionNames$id)
  df <- df %>% left_join(df_regionNames, by = c("HH7"="id"))
  names(df)[names(df) == 'HH7.y'] <- 'HH7_region'
  df <- df %>% select(-"HH7") 
  return(df)
}




