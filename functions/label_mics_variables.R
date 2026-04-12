#title: "Functions For Re-Labeling Household MICS SPSS files"


#WS1 and WS2 Main and Secondary Drinking Water source 

#Unmproved = 0
#32   unprotected well
#42   unprotected spring
#43   surface water (river/dam/lake/pond/stream/canal/irrigation channel)
#81   surface water
#96   other
#99   no response

#Improved = 1
#13   piped to neighbor
#14   public tap/standpipe
#21   tube well or borehole
#22   BOREHOLE: MOTORIZED PUMP
#23   BOREHOLE: HAND PUMP (Machincal)
#31   protected well
#41   protected spring
#51   rainwater
#61   tanker truck
#62   cart with small tank
#71   CART WITH SMALL TANK
#93   AGUA DE CAMIONCITO PROCESADA

#Improved and on plot = 2
#11   piped into dwelling
#12   piped to yard/plot
#(13   piped water:from the house or yard of the neighbor 
# (classified as on plot in Dominican Republic))

#Improved (bottled/kiosk or desalinated) = 3

#72   WATER KIOSK (WATER SELLING PLANT)
#91   bottled water
#92   PACKAGED WATER: SACHET WATER



setMainSourceLabels <- function(df,WS1) {
  #Unimproved
  df$WS1[df$WS1 == 32|df$WS1 == 42|df$WS1 == 43|df$WS1 == 81|df$WS1 == 96|
           df$WS1 == 99] <- 0
  
  #Improved
  df$WS1[df$WS1 == 13|df$WS1 == 14|df$WS1 == 21|df$WS1 == 22|df$WS1 == 23|df$WS1 == 31
         |df$WS1 == 41|df$WS1 == 51|df$WS1 == 61|df$WS1 == 62|df$WS1 == 71|df$WS1 == 72 
         |df$WS1 == 93] <- 1
  
  
  #Improved and on plot
  df$WS1[df$WS1 == 11|df$WS1 == 12] <- 2
  
  #Improved (bottled/kiosk or desalinated)
  df$WS1[df$WS1 == 91|df$WS1 == 92] <- 3
  
  return(df)
}

setSecondarySourceLabels <- function(df,WS2) {
  #Unimproved
  df$WS2[df$WS2 == 32|df$WS2 == 42|df$WS2 == 43|df$WS2 == 81|df$WS2 == 96|
           df$WS2 == 99] <- 0
  
  #Improved
  df$WS2[df$WS2 == 13|df$WS2 == 14|df$WS2 == 21|df$WS2 == 22|df$WS2 == 23|df$WS2 == 31
         |df$WS2 == 41|df$WS2 == 51|df$WS2 == 61|df$WS2 == 62|df$WS2 == 71|df$WS2 == 72 
         |df$WS2 == 93] <- 1
  
  
  #Improved and on plot
  df$WS2[df$WS2 == 11|df$WS2 == 12] <- 2
  
  #Improved (bottled/kiosk or desalinated)
  df$WS2[df$WS2 == 71|df$WS2 == 91|df$WS2 == 92] <- 3
  
  return(df)
}


#WS3 Water Source location
#1 IN OWN DWELLING   
#2 IN OWN YARD / PLOT
#3 ELSEWHERE         
#-99 NO RESPONSE 

setWS3_WslocationLabels <- function(df,WS3) {
  df$WS3[df$WS3 == 9] <- -99
  return(df)
}

#WS4 time to collect
#0   Members do not collect water
#>0  Number of minutes to collect water
#-99 missing

setWS4timeLabels <- function(df,WS4) {
  df$WS4[df$WS4 == 997|df$WS4 == 998|df$WS4 == 999] <- -99
  return(df)  
}

#WS7 Water Insufficiency
#0   No, always sufficient or members didn't know, I don't know 
#1   Yes, water insufficient
#-99 missing data

setWS7WaterInsufficiencyLabels <- function(df,WS7) {
  df$WS7[df$WS7 == 2|df$WS7 == 8] <- 0
  df$WS7[df$WS7 == 9] <- -99
  return(df)
}


#WS8 Why Insufficient
#0   Other (incl. too expensive)
#2   not accessible
#-99 missing data

setWS8WhyInsufficientLabels <- function(df,WS8) {
  df$WS8[df$WS8 == 1|df$WS8 == 2 |df$WS8 == 6|df$WS8 == 4] <- 1
  df$WS8[df$WS8 == 3] <- 2
  df$WS8[df$WS8 == 8 |df$WS8 == 9 ] <- -99
  return(df)
}
  
  
#WQ27 Water quality at source
#100   100 or more E.coli CFU/ 100ml
#0     No E.coli
#-99   missing

setWQ27SourceWaterQuality <- function(df,WQ27) {
  df$WQ27[df$WQ27 == 101] <- 100
  df$WQ27[df$WQ27 == 991|df$WQ27 == 998|df$WQ27 == 999] <- -99
  return(df)
}
  
setWRiskBIN <- function(df, WQ27){
    df$WQ27[df$WQ27 > 0] <- 1
    return(df)
  }

relabelingSurveyQuestionResponses <- function(df.MICS.SMDW_test,WS1,WS2,WS3,WS4,WS7,WS8,WQ27){
  df.MICS.SMDW_test <- setMainSourceLabels(df.MICS.SMDW_test,WS1)
  df.MICS.SMDW_test <- setSecondarySourceLabels(df.MICS.SMDW_test,WS2)
  df.MICS.SMDW_test <- setWS3_WslocationLabels(df.MICS.SMDW_test,WS3)
  df.MICS.SMDW_test <- setWS4timeLabels(df.MICS.SMDW_test,WS4)
  df.MICS.SMDW_test <- setWS7WaterInsufficiencyLabels(df.MICS.SMDW_test,WS7)
  df.MICS.SMDW_test <- setWS8WhyInsufficientLabels(df.MICS.SMDW_test,WS8)
  df.MICS.SMDW_test <- setWQ27SourceWaterQuality(df.MICS.SMDW_test,WQ27)
  df.MICS.SMDW_test <- setWRiskBIN(df.MICS.SMDW_test, WQ27)
  return(df.MICS.SMDW_test)
}
  



#Translation of Variable Values from Household MICS SPSS files
# WS1 and WS2 Water source 

setMainSource	 <- function(vector) {			
  
  #not improved
  vector[which(vector == "Agua de superficie (río, arroyo,represa,lago,estanque,canal de irrigación)")] = 0
  vector[which(vector == "DUG WELL: UNPROTECTED WELL")] = 0
  vector[which(vector == "EAU DE SURFACE (RIVIERE, BARRAGE, LAC, MARE, COURANT, CANAL, SYSTEME D’IRRIGATION)")] = 0
  vector[which(vector == "Eau de surface (rivière, fleuve, barrage, lac, mare, canal, canal d?irrigation)")] = 0
  vector[which(vector == "Água de Superfície (Rio, Barragem, Lago, Mar, Corrente, Canal, Sistema de irrigação 81")] = 0
  vector[which(vector == "Manantial no protegido")] = 0
  vector[which(vector == "Other specify")] = 0
  vector[which(vector == "Otra")] = 0
  vector[which(vector == "Autre")] = 0
  vector[which(vector == "AUTRE")] = 0
  vector[which(vector == "Other")] = 0
  vector[which(vector == "OTHER")] = 0
  vector[which(vector == "OTHER ")] = 0
  vector[which(vector == "OTRO")] = 0
  vector[which(vector == "OTRO (Especifique)")] = 0
  
  vector[which(vector == "Pozo no protegido")] = 0
  vector[which(vector == "PUITS CREUSE: PAS PROTEGE")] = 0
  vector[which(vector == "Puits non protégé")] = 0
  vector[which(vector == "Source non protégée")] = 0
  vector[which(vector == "SOURCE: SOURCE NON PROTEGEE")] = 0
  vector[which(vector == "SPRING: UNPROTECTED SPRING")] = 0
  vector[which(vector == "SURFACE WATER (RIVER, DAM, LAKE, POND, STREAM, CANAL, IRRIGATION CHANNEL)")] = 0
  vector[which(vector == "Surface water (river, stream, dam, lake, pond, canal, irrigation channel)")] = 0
  vector[which(vector == "Unprotected spring")] = 0
  vector[which(vector == "Unprotected well")] = 0
  vector[which(vector == "Água de Superfície (Rio, Barragem, Lago, Mar, Corrente, Canal, Sistema de irrigação)")] = 0
  vector[which(vector == "AGUA DA NASCENTE: NASCENTE DESPROTEGIDA")] = 0
  vector[which(vector == "ÁGUA SUPERFICIAL (RIO, BARRAGEM, LAGO, LAGOA, CORRENTE, CANAL, SISTEMA DE IRRIGAÇÃO)")] = 0
  vector[which(vector == "EAU DE SURFACE (RIVIERE, BARRAGE, LAC, MARE, COURANT, CANAL, SYSTEME D?IRRIGATION)")] = 0
  vector[which(vector == "DUG WELL UNPROTECTED WELL")] = 0
  vector[which(vector == "Eau de surface (Rivière, Barrage, Lac, Mare, Courant, Canal, système d'irrigation) ")] = 0
  vector[which(vector == "Nascente desprotegida")] = 0
  vector[which(vector == "OTHER (specify)")] = 0
  vector[which(vector == "Outra(Especificar)")] = 0
  vector[which(vector == "Poço não protegido")] = 0
  vector[which(vector == "Puits creusé: pas protègé")] = 0
  vector[which(vector == "Source: source non protègée")] = 0
  vector[which(vector == "SPRINGS UNPROTECTED SPRINGS")] = 0
  vector[which(vector == "TUBE WELL / BOREHOLE UNPROTECTED WELL")] = 0
  vector[which(vector == "0")] = 0
  vector[which(vector == "Água de Superfície (Rio, Barragem, Lago, Mar, Corrente, Canal, Sistema de irrigação)")] = 0
  vector[which(vector == "AGUA PERFURADA: DESPROTEGIDA")] = 0
  vector[which(vector == "EAU DE SURFACE (OUED,LAC, BARRAGE)")] = 0
  vector[which(vector == "Manantial no protegido")] = 0
  vector[which(vector == "Nascente desprotegida")] = 0
  vector[which(vector == "Source: source non protègée")] = 0
  vector[which(vector == "SPRINGS UNPROTECTED SPRINGS")] = 0
  vector[which(vector == "TUBE WELL / BOREHOLE UNPROTECTED WELL")] = 0
  vector[which(vector ==  "AUTRE (? pr?ciser)")] = 0
  vector[which(vector ==  "Other specify")] = 0
  vector[which(vector ==  "OUTRO")] = 0
  vector[which(vector ==  "AUTRE (pr?ciser)")] = 0
  vector[which(vector ==  "SOURCE:  NON PROTEGEE")] = 0
  vector[which(vector ==  "UNPROTECTED WELL")] = 0
  vector[which(vector ==  "AGUA DE MANANTIAL OJO DE AGUA (NO PROTEGIDO)")] = 0
  vector[which(vector ==  "AGUA DE RÍO, REPRESA, LAGO, ESTANQUE, ARROYO, CANAL, CANAL DE RIEGO)")] = 0
  vector[which(vector ==  "AGUA DE SUPERFICIE (RÍO, REPRESA,LAGO,ESTANQUE,ARROYO,CANAL, CANAL DE IRRIGACIÓN)")] = 0
  vector[which(vector ==  "POZO CAVADO (MALACATE NO PROTEGIDO)")] = 0
  vector[which(vector ==  "POZO CAVADO: POZO NO PROTEGIDO")] = 0
  vector[which(vector ==  "AGUA DE MANANTIAL: MANANTIAL NO PROTEGIDO")] = 0
  vector[which(vector ==  "AGUA DE RÃO, REPRESA, LAGO, ESTANQUE, ARROYO, CANAL, CANAL DE RIEGO")] = 0
  vector[which(vector == "AGUA DE MANANTIAL, OJO DE AGUA (NO PROTEGIDO)")] = 0
  vector[which(vector == "AGUA DE RÍO, REPRESA, LAGO, ESTANQUE, ARROYO, CANAL, CANAL DE RIEGO")] = 0
  vector[which(vector == "Eau de surface (rivière, fleuve, barrage, lac, mare, canal, canal d'irrigation)")] = 0
  vector[which(vector == "Non Déclarée")] = 0 # according to JMP
  vector[which(vector ==  "Missing")] = 0# according to JMP
  vector[which(vector ==  "NO RESPONSE")] = 0# according to JMP
  vector[which(vector ==  "NON REPONSE")] = 0# according to JMP
  vector[which(vector ==  "DK")] = 0# according to JMP
  vector[which(vector ==  "NO RESPONDE")] = 0# according to JMP
  
  
  #improved
  vector[which(vector == "POZO CAVADO (MALACATE PROTEGIDO)")] = 1
  vector[which(vector == "BORE HOLE: MOTORIZED PUMP")] = 1
  vector[which(vector == "AGUA DE MANANTIAL: MANANTIAL PROTEGIDO")] = 1
  vector[which(vector == "AGUA DE MANANTIAL, OJO DE AGUA(PROTEGIDO)")] = 1
  vector[which(vector == "NEIGHBOUR?S CEMENT OR OTHER TANK")] = 1
  vector[which(vector ==  "Agua com pequena cisterna")] = 1
  vector[which(vector == "OWN CEMENT OR OTHER TANK")] = 1
  vector[which(vector == "COMMUNITY CEMENT OR OTHER TANK")] = 1
  vector[which(vector == "Agua com pequena cisterna")] = 1
  vector[which(vector == "ROBINET: ROBINET PUBLIC/FONTAINE PUBLIQUE")] = 1
  vector[which(vector == "Camion-citerne")] = 1
  vector[which(vector == "CAMION CITERNE")] = 1
  vector[which(vector == "Puits protégé")] = 1
  vector[which(vector == "RAINWATER")] = 1
  vector[which(vector == "Rainwater collection")] = 1
  vector[which(vector == "Recogen agua de lluvia")] = 1
  vector[which(vector == "Canilla/llave/grifo público")] = 1
  vector[which(vector == "Carreta con tanque/tambor pequeño")] = 1
  vector[which(vector == "Carro-tanque/camión cisterna")] = 1
  vector[which(vector == "CART WITH SMALL TANK")] = 1
  vector[which(vector == "Cart with small tank / drum")] = 1
  vector[which(vector == "CART WITH SMALL TANK /DRUM/CANE")] = 1
  vector[which(vector == "CHARRETTE AVEC PETITE CITERNE")] = 1
  vector[which(vector == "DUG WELL: PROTECTED WELL")] = 1
  vector[which(vector == "Eau de pluie")] = 1
  vector[which(vector == "EAU DE PLUIE")] = 1
  vector[which(vector == "HAND PUMP (Machincal)")] = 1
  vector[which(vector == "Manantial protegido")] = 1
  vector[which(vector == "MOTORIZED PUMP")] = 1
  vector[which(vector == "Piped to neighbour")] = 1
  vector[which(vector == "PIPED WATER: PIPED TO NEIGHBOUR")] = 1
  vector[which(vector == "ROBINET: ROBINET PUBLIC/BORNE FONTAINE")] = 1
  vector[which(vector == "PIPED WATER: PUBLIC TAP / STANDPIPE")] = 1
  vector[which(vector == "Pozo con tubería")] = 1
  vector[which(vector == "Pozo protegido")] = 1
  vector[which(vector == "Protected spring")] = 1
  vector[which(vector == "Protected well")] = 1
  vector[which(vector == "Public tap / standpipe")] = 1
  vector[which(vector == "Puits à pompe / Forage")] = 1
  vector[which(vector == "PUITS A POMPE/FORAGE")] = 1
  vector[which(vector == "PUITS CREUSE: PROTEGE")] = 1
  vector[which(vector == "Robinet du voisin")] = 1
  vector[which(vector == "Robinet public / Borne fontaine")] = 1
  vector[which(vector == "ROBINET: CHEZ LE VOISIN")] = 1
  vector[which(vector == "ROBINET: ROBIENT PUBLIC/BORNE FONTAINE")] = 1
  vector[which(vector == "Source protégée")] = 1
  vector[which(vector == "SOURCE: SOURCE PROTEGEE")] = 1
  vector[which(vector == "SPRING: PROTECTED SPRING")] = 1
  vector[which(vector == "HAND PUMP")] = 1
  vector[which(vector == "MOTORIZED PUMP (DONKEY/TURBINE)")] = 1
  vector[which(vector == "Puits à pompe")] = 1
  vector[which(vector == "Agua da chuva")] = 1
  vector[which(vector == "ANIMAL DRAWN WATER CART")] = 1
  vector[which(vector == "Camion citerne ")] = 1
  vector[which(vector == "Charrette avec petite citerne ")] = 1
  vector[which(vector == "DUG WELL PROTECTED WELL")] = 1
  vector[which(vector == "Fontenário público/boca do incendio")] = 1
  vector[which(vector == "Nascente protegida")] = 1
  vector[which(vector == "PIPED TO NEIGHBOUR")] = 1
  vector[which(vector == "Poço protegido")] = 1
  vector[which(vector == "PROTECTED WELL")] = 1
  vector[which(vector == "PUBLIC TAP / STANDPIPE")] = 1
  vector[which(vector == "Puits creusé: protègé")] = 1
  vector[which(vector == "RAIN, SNOW WATER")] = 1
  vector[which(vector == "Robinet: chez le voisin")] = 1
  vector[which(vector == "Robinet: robinet publics / Borne fontaine / Kiosque à eau")] = 1
  vector[which(vector == "Source: source protègée")] = 1
  vector[which(vector == "SPRINGS PROTECTED SPRINGS")] = 1
  vector[which(vector == "TANKER TRUCK")] = 1
  vector[which(vector == "TUBE WELL / BOREHOLE PROTECTED WELL")] = 1
  vector[which(vector == "CAMINHÃO CISTERNA")] = 1
  vector[which(vector == "Carro-tanque/camión cisterna")] = 1
  vector[which(vector == "CART WITH SMALL TANK /DRUM/CANE")] = 1
  vector[which(vector == "Charrette avec petite citerne ")] = 1
  vector[which(vector ==  "1")] = 1
  vector[which(vector ==  "Agua da chuva")] = 1
  vector[which(vector ==  "ÁGUA DA CHUVA")] = 1
  vector[which(vector ==  "AGUA DA NASCENTE: NASCENTE PROTEGIDA")] = 1
  vector[which(vector ==  "AGUA PERFURADA: PROTEGIDA")] = 1
  vector[which(vector ==  "BOMBA / PERFURAÇÃO")] = 1
  vector[which(vector ==  "BOMBA / PERFURAÇÃO")] = 1
  vector[which(vector ==  "HAND PUMP (Machincal)")] = 1
  vector[which(vector ==  "Manantial protegido")] = 1
  vector[which(vector ==  "MOTORIZED PUMP")] = 1
  vector[which(vector ==  "Nascente protegida")] = 1
  vector[which(vector ==  "Pozo protegido")] = 1
  vector[which(vector ==  "Puits creusé: protègé")] = 1
  vector[which(vector ==  "RAIN, SNOW WATER")] = 1
  vector[which(vector ==  "ROBINET: CHEZ LE VOISIN")] = 1
  vector[which(vector ==  "ROBINET: ROBINET PUBLIC/BORNE FONTAINE")] = 1
  vector[which(vector ==  "SPRINGS PROTECTED SPRINGS")] = 1
  vector[which(vector ==  "TORNEIRA: DO CHAFARIZ PÚBLICO")] = 1
  vector[which(vector ==  "TORNEIRA: NO VIZINHO")] = 1
  vector[which(vector ==  "TUBE WELL")] = 1
  vector[which(vector ==  "SOURCE: PROTEGEE")] = 1
  vector[which(vector ==  "Tanker-truck")] = 1
  vector[which(vector ==  "TANKER-TRUCK")] = 1
  vector[which(vector ==  "TUBE WELL / BOREHOLE")] = 1
  vector[which(vector ==  "Tube well, Borehole")] = 1
  vector[which(vector ==  "Tubería al vecino")] = 1
  vector[which(vector ==  "WATER REFILL FACILITY")] = 1
  vector[which(vector ==  "AGUA DE CAMIONCITO PROCESADA")] = 1
  vector[which(vector ==  "AGUA DE LLUVIA")] = 1
  vector[which(vector ==  "AGUA DE MANANTIAL, OJO DE AGUA(PROTEGIDO))")] = 1
  vector[which(vector ==  "AGUA POR TUBERÍA: LLAVE PÚBLICA")] = 1
  vector[which(vector ==  "AGUA POR TUBERÍA: POR TUBERÍA  DE LA CASA O PATIO DE UN VECINO")] = 1
  vector[which(vector ==  "BOREHOLE: HAND PUMP (Machincal)")] = 1
  vector[which(vector ==  "BOREHOLE: MOTORIZED PUMP")] = 1
  vector[which(vector ==  "CAMIÓN-TANQUE O CAMIÓN CISTERNA")] = 1
  vector[which(vector ==  "CARRETA CON TANQUE PEQUEÑO")] = 1
  vector[which(vector ==  "CARRO CISTERNA")] = 1
  vector[which(vector ==  "LLAVE/GRIFO PÚBLICO")] = 1
  vector[which(vector ==  "PICKUP CON DRONES O BARRILES")] = 1 
  vector[which(vector ==  "POR TUBERÍA DE POZO TUBULAR O PERFORADO")] = 1 
  vector[which(vector ==  "POZO CAVADO(MALACATE PROTEGIDO)")] = 1
  vector[which(vector ==  "POZO CAVADO: POZO PROTEGIDO")] = 1
  vector[which(vector ==  "POZO PERFORADO")] = 1
  vector[which(vector ==  "PUESTO DE AGUA")] = 1
  vector[which(vector ==  "TUBERÍA DEL VECINO")] = 1
  vector[which(vector ==  "WATER FOUNTAIN")] = 1
  vector[which(vector == "Furo")] = 1
  vector[which(vector == "Na casa do vizinho")] = 1
  vector[which(vector == "Charrette avec petite citerne / tonneau")] = 1
  vector[which(vector == "Puits à pompe, forage")] = 1
  vector[which(vector == "Robinet dans quartier, cour ou parcelle")] = 1
  vector[which(vector == "Robinet public / borne fontaine")] = 1
  
  
  #improved and on plot
  vector[which(vector == "AGUA POR TUBERÍA: TUBERÍA DENTRO DE LA VIVIENDA")] = 2
  vector[which(vector == "TUBERÍA DENTRO DE LA VIVIENDA")] = 2
  vector[which(vector == "TUBERÍA  DENTRO DEL TERRENO/ LOTE")] = 2
  vector[which(vector == "AGUA POR TUBERÍA: POR TUBERÍA EN EL PATIO, SOLAR O TERRENO")] = 2
  vector[which(vector == "AGUA POR TUBERÍA: POR TUBERÍA DENTRO DE LA VIVIENDA")] = 2
  vector[which(vector == "TORNEIRA: NO QUINTAL")] = 2
  vector[which(vector == "TORNEIRA: NO ALOJAMENTO")] = 2
  vector[which(vector == "Piped into compound, yard or plot")] = 2
  vector[which(vector == "Piped into dwelling")] = 2
  vector[which(vector == "PIPED WATER : PIPED INTO DWELLING")] = 2
  vector[which(vector == "PIPED WATER: PIPED INTO DWELLING")] = 2
  vector[which(vector == "PIPED WATER: PIPED TO COMPOUND/YARD / PLOT")] = 2
  vector[which(vector == "PIPED WATER: PIPED TO YARD / PLOT")] = 2
  vector[which(vector == "Robinet dans la concession, cour ou parcelle")] = 2
  vector[which(vector == "Robinet dans le logement")] = 2
  vector[which(vector == "ROBINET: DANS LA CONCESSION/JARDIN/ PARCELLE")] = 2
  vector[which(vector == "ROBINET: DANS LE LOGEMENT")] = 2
  vector[which(vector == "Tubería dentro de la vivienda")] = 2
  vector[which(vector == "Tubería dentro del terreno,patio o lote")] = 2
  vector[which(vector == "PIPED INTO DWELLING")] = 2
  vector[which(vector == "PIPED TO YARD / PLOT")] = 2
  vector[which(vector == "PIPED WATER PIPED INTO DWELLING")] = 2
  vector[which(vector == "PIPED WATER PIPED TO YARD / PLOT")] = 2
  vector[which(vector == "Robinet: dans la concession / Jardin / Parcelle ")] = 2
  vector[which(vector == "Robinet: dans le logement ")] = 2
  vector[which(vector ==  "2")] = 2
  vector[which(vector ==  "PIPED WATER PIPED TO YARD / PLOT")] = 2
  vector[which(vector ==  "PIPED WATER: PIPED TO COMPOUND/YARD / PLOT")] = 2
  vector[which(vector ==  "ROBINET: DANS LA COUR/JARDIN/PARCELLE")] = 2
  vector[which(vector ==  "Robinet: dans le logement ")] = 2
  vector[which(vector == "DANS LA COUR/JARDIN/PARCELLE")] = 2
  vector[which(vector == "Dans concession, cour ou parcelle")] = 2
  vector[which(vector == "Dans le logement")] = 2
  vector[which(vector == "No interior da casa")] = 2
  vector[which(vector == "No quintal/jardim, parcela")] = 2
  
  #improved (bottled/kiosk or desalinated)
  vector[which(vector ==  "DISALINATION PLANT WATER")] = 3
  vector[which(vector == "Agua embotellada/envasada")] = 3
  vector[which(vector == "Bottled water")] = 3
  vector[which(vector == "EAU CONDITIONNEE: EAU EN BOUTEILLE")] = 3
  vector[which(vector == "EAU CONDITIONNEE: EAU EN SACHET")] = 3
  vector[which(vector == "SACHET WATER")] = 3
  vector[which(vector == "Eau en bouteille")] = 3
  vector[which(vector == "PACKAGED WATER: BOTTLED WATER")] = 3
  vector[which(vector == "PACKAGED WATER: DESALINIZED & STERILIZED WATER")] = 3
  vector[which(vector == "PACKAGED WATER: SACHET WATER")] = 3
  vector[which(vector == "Sachet (pure) water")] = 3
  vector[which(vector == "WATER KIOSK")] = 3
  vector[which(vector == "WATER KIOSK (WATER SELLING PLANT)")] = 3
  vector[which(vector == "DISALINATION PLANT WATER")] = 3
  vector[which(vector == "Agua empacotada")] = 3
  vector[which(vector == "Agua engarrafada")] = 3
  vector[which(vector == "BOTTLED WATER")] = 3
  vector[which(vector == "Eau conditionnée: Eau en bouteille")] = 3
  vector[which(vector == "Eau conditionnée: Eau en sachet (pure water)")] = 3
  vector[which(vector == "Quiosque de agua")] = 3
  vector[which(vector == "WATER KIOSK CONNECTED WITH PIPED WATER")] = 3
  vector[which(vector == "WATER KIOSK NOT CONNECTED WITH PIPED WATER")] = 3
  vector[which(vector == "Quiosque de Agua")] = 3
  vector[which(vector == "KIOSQUE A EAU")] = 3
  vector[which(vector == "Quiosque de agua")] = 3
  vector[which(vector ==  "3")] = 3
  vector[which(vector ==  "20 LITER WATER BOTTLES")] = 3
  vector[which(vector ==  "ÁGUA CONDICIONADA: ÁGUA EM SAQUETA OU SACO")] = 3
  vector[which(vector ==  "ÁGUA CONDICIONADA: ÁGUA ENGARRAFADA")] = 3
  vector[which(vector ==  "Agua empacotada")] = 3
  vector[which(vector ==  "Agua engarrafada")] = 3
  vector[which(vector ==  "Bottled water")] = 3
  vector[which(vector ==  "EAU CONDITIONNEE: EAU EN BOUTEILLE")] = 3
  vector[which(vector ==  "EAU CONDITIONNEE: EAU EN SACHET")] = 3
  vector[which(vector ==  "PACKAGED WATER: SACHET WATER")] = 3
  vector[which(vector ==  "PACKAGED WATER: WATER IN PLASTIC BAG")] = 3
  vector[which(vector ==  "Sachet (pure) water")] = 3
  vector[which(vector ==  "AGUA EMBOTELLADA")] = 3
  vector[which(vector ==  "AGUA ENVASADA: AGUA EMBOTELLADA O ENVASADA (BOTELLONES)")] = 3
  vector[which(vector ==  "AGUA ENVASADA: FUNDITA DE AGUA")] = 3
  vector[which(vector ==  "BOLSA DE AGUA")] = 3
  vector[which(vector ==  "Eau en sachet")] = 3
  vector[which(vector ==  "PACKAGED WATER: JAR WATER")] = 3
  vector[which(vector ==  "OPEN WATER RETAILER/SELLER")] = 3

  return(vector)			
}	


#WS3_Wslocation
setWslocation <- function(vector){
  #IN HOME
  vector[which(vector == "DANS LEUR LOGEMENT")] = 1
  vector[which(vector == "Dans logement")] = 1
  vector[which(vector == "In own dwelling")] = 1
  vector[which(vector == "IN OWN DWELLING")] = 1
  vector[which(vector == "En el interior de la propia vivienda")] = 1
  vector[which(vector == "Dans leur logement")] = 1
  vector[which(vector == "DANS VOTRE LOGEMENT")] = 1
  vector[which(vector == "Dans leur propre logement")] = 1
  vector[which(vector == "No alojamento")] = 1
  vector[which(vector == "Dentro do proprio alojamento")] = 1
  vector[which(vector == "NO ALOJAMENTO")] = 1
  vector[which(vector == "EN EL INTERIOR DE LA PROPIA VIVIENDA")] = 1
  vector[which(vector == "EN EL INTERIOR DE LA VIVIENDA")] = 1
  
  #IN COURTYARD
  vector[which(vector == "Dans cour / parcelle")] = 2
  vector[which(vector == "DANS LEUR JARDIN/PARCELLE")] = 2
  vector[which(vector == "Dans leur jardin / Parcelle  ")] = 2
  vector[which(vector == "In own yard / plot")] = 2
  vector[which(vector == "IN OWN YARD / PLOT")] = 2
  vector[which(vector == "En el propio patio/lote")] = 2
  vector[which(vector == "Dans leur jardin / Parcelle ")] = 2
  vector[which(vector == "No quintal/jardim, parcela")] = 2
  vector[which(vector == "No quintal/Parcela")] = 2
  vector[which(vector == "DANS VOTRE COUR/JARDIN/PARCELLE")] = 2
  vector[which(vector == "NO QUINTAL/TERRENO")] = 2
  vector[which(vector == "EN EL PATIO DE LA VIVIENDA")] = 2
  vector[which(vector == "EN EL PROPIO PATIO/LOTE")] = 2
  
  #ELSEWHERE
  vector[which(vector == "Ailleurs")] = 3
  vector[which(vector == "Algures")] = 3
  vector[which(vector == "AILLEURS")] = 3
  vector[which(vector == "Elsewhere")] = 3
  vector[which(vector == "ELSEWHERE")] = 3
  vector[which(vector == "En otro lado")] = 3
  vector[which(vector == "Em outro lugar")] = 3
  vector[which(vector == "NUM OUTRO LUGAR")] = 3
  vector[which(vector == "PORTEUR D'EAU")] = 3
  vector[which(vector == "EN OTRO LADO")] = 3
  vector[which(vector == "EN OTRO LUGAR")] = 3
  
  #missing data
  
  vector[which(vector == "NO RESPONSE")] = -99
  vector[which(vector == "NON REPONSE")] = -99
  vector[which(vector == "SEM RESPOSTA")] = -99
  vector[which(vector == "Incohérent")] = -99
  vector[which(vector == "No reportado")] = -99
  vector[which(vector == "Missing")] = -99
  vector[which(vector == "-99")] = -99
  vector[which(vector == "NO RESPONDE")] = -99
  vector[which(vector == "Non déclaré/Pas de réponse")] = -99
  vector[which(vector == "Non Déclarée")] = -99
  
  return (vector)
}

#WS4_time to collect
setWs4time <- function(vector){
  vector[which(vector == "NO RESPONSE")] = -99
  vector[which(vector == "NON REPONSE")] = -99
  vector[which(vector == "SEM RESPOSTA")] = -99
  vector[which(vector == "Incohérent")] = -99
  vector[which(vector == "No reportado")] = -99
  vector[which(vector == "Missing")] = -99
  vector[which(vector == "NSP")] = -99
  vector[which(vector == "Ne sait pas")] = -99
  vector[which(vector == "Inconsistent")] = -99
  vector[which(vector == "NON REPONSE")] = -99
  vector[which(vector == "No sabe")] = -99
  vector[which(vector == "Incohérent  ")] = -99
  vector[which(vector == "DK")] = -99
  vector[which(vector == "NS")] = -99
  vector[which(vector == "NO RESPONDE")] = -99
  vector[which(vector == "NO SABE")] = -99
  vector[which(vector == "Non déclaré/Pas de réponse")] = -99
  vector[which(vector == "Non Déclarée")] = -99
  
  vector[which(vector == "Membros de AF não coletam agua fora")] = 0
  vector[which(vector == "MEMBRES NE COLLECTENT PAS D?EAU")] = 0
  vector[which(vector == "OS MEMBROS NÃO APANHAM A ÁGUA")] = 0
  vector[which(vector == "MEMBRES NE COLLECTENT PAS D’EAU")] = 0
  vector[which(vector == "Membres ne collectent pas d'eau")] = 0
  vector[which(vector == "MEMBERS DO NOT COLLECT")] = 0
  return (vector)
}

##WS7

setWaterSuff <- function(vector) {			
  vector[which(vector == "YES, AT LEAST ONCE")] = 1
  vector[which(vector == "OUI, AU MOINS UNE FOIS")] = 1
  vector[which(vector == "SIM, PELO MENOS UMA VEZ")] = 1
  vector[which(vector == "YES, AT LEAST FOR ONE TIME")] = 1
  vector[which(vector == "Oui, au moins une fois")] = 1
  vector[which(vector == "SÍ, AL MENOS UNA VEZ")] = 1
  vector[which(vector == "SI, AL MENOS UNA VEZ")] = 1
  vector[which(vector == "Yes")] = 1
  vector[which(vector == "YES")] = 1
  vector[which(vector == "Oui")] = 1
  vector[which(vector == "OUI")] = 1
  vector[which(vector == "Si")] = 1
  vector[which(vector == "Sim")] = 1
  vector[which(vector == "SIM")] = 1
  
  vector[which(vector == "NO, ALWAYS SUFFICIENT")] = 0
  vector[which(vector == "NÃO, SEMPRE SUFICIENTE")] = 0
  vector[which(vector == "NON, TOUJOURS SUFFISANT")] = 0
  vector[which(vector == "Non, toujours suffisant  ")] = 0
  vector[which(vector == "No,EXIST SUFFICIENT WATER PERMANENTLY")] = 0
  vector[which(vector == "Non, toujours suffisant")] = 0
  vector[which(vector == "Non, toujours suffisant ")] = 0
  vector[which(vector == "No")] = 0
  vector[which(vector == "NO")] = 0
  vector[which(vector == "Non")] = 0
  vector[which(vector == "NON")] = 0
  vector[which(vector == "Não")] = 0
  vector[which(vector == "NO, SIEMPRE FUE SUFICIENTE")] = 0
  vector[which(vector == "NO, SIEMPRE FUÉ SUFICIENTE")] = 0
  vector[which(vector == "DK")] = 0 #according to JMP
  vector[which(vector == "NSP")] = 0#according to JMP
  vector[which(vector == "NS")] = 0 #according to JMP
  vector[which(vector == "DON?T KNOW")] = 0 #according to JMP
  vector[which(vector == "No sabe")] = 0 #according to JMP
  vector[which(vector == "Ne sait pas")] = 0 #according to JMP
  vector[which(vector == "NO SABE")] = 0
  
  #missing data
  vector[which(vector == "NO RESPONSE")] = -99
  vector[which(vector == "NON REPONSE")] = -99
  vector[which(vector == "SEM RESPOSTA")] = -99
  vector[which(vector == "-99")] = -99
  vector[which(vector == "NO RESPONDE")] = -99
  vector[which(vector == "Missing")] = -99
  return(vector)
}

#WS8
setWhyInsuff <- function(vector) {			
  
  #not available because of other reasons
  vector[which(vector == "Agua não disponível na fonte")] = 1
  vector[which(vector == "EAU NON DISPONIBLE A LA SOURCE")] = 1
  vector[which(vector == "Eau trop chère  ")] = 1
  vector[which(vector == "WATER NOT AVAILABLE FROM SOURCE")] = 1
  vector[which(vector == "ÁGUA COM PREÇO ELEVADO")] = 1
  vector[which(vector == "ÁGUA NÃO DISPONÍVEL NA FONTE")] = 1
  vector[which(vector == "Eau non disponible à la source")] = 1
  vector[which(vector == "WATER TOO EXPENSIVE")] = 1
  vector[which(vector == "Agua muito cara")] = 1
  vector[which(vector == "EAU TROP CHERE")] = 1
  vector[which(vector == "AGUA DEMASIADO CARA")] = 1
  vector[which(vector == "WATER SALINITY")] = 1
  vector[which(vector == "NO HABÍA AGUA DISPONIBLE EN LA FUENTE")] = 1
  
  #not available because source not accessible
  vector[which(vector == "FUENTE NO ACCESIBLE")] = 2
  vector[which(vector == "SOURCE NOT ACCESSIBLE")] = 2
  vector[which(vector == "Fonte não acessível")] = 2
  vector[which(vector == "Source pas accessible")] = 2
  vector[which(vector == "FONTE NÃO ACESSÍVEL")] = 2
  vector[which(vector == "SOURCE PAS ACCESSIBLE")] = 2
  
  #missing data
  vector[which(vector == "-99")] = -99
  vector[which(vector == "AUTRE")] = 1
  vector[which(vector == "Ne sait pas")] = -99
  vector[which(vector == "NS")] = -99
  vector[which(vector == "OTHER (specify)")] = 1
  vector[which(vector == "AUTRE (pr?ciser)")] = 1
  vector[which(vector == "NO RESPONSE")] = -99
  vector[which(vector == "NSP")] = -99
  vector[which(vector == "Outro")] = 1
  vector[which(vector == "Autre")] = 1
  vector[which(vector == "DK")] = -99
  vector[which(vector == "NON REPONSE")] = -99
  vector[which(vector == "OTHER")] = 1
  vector[which(vector == "OUTRO")] = 1
  vector[which(vector == "NO SABE")] = -99
  vector[which(vector == "OTRO (Especifique)")] = 1
  vector[which(vector == "Ne sait pas")] = -99
  vector[which(vector == "OTRO")] = 1
  return(vector)
}

setWaterQuality	 <- function(vector) {			
  #100 or more E.coli CFU
  vector[which(vector == "100 et plus")] = 100
  vector[which(vector == "101")] = 100
  vector[which(vector == "103")] = 100
  vector[which(vector == "More than 100")] = 100
  vector[which(vector == "MORE THAN 100")] = 100
  vector[which(vector == "Plus de 100")] = 100
  vector[which(vector == "MAIS DE 100")] = 100
  vector[which(vector == "Mais de 100")] = 100
  vector[which(vector == "More than 99 colonies counted")] = 100
  
  #no E.coli CFU
  vector[which(vector == "Aucune colonie bleue")] = 0
  
  #missing data
  vector[which(vector == "impossible de lire les rÃƒÂ©sultats/ RÃƒÂ©sultats perdus saisir")] = -99
  vector[which(vector == "impossible de lire les rÃ©sultats/ RÃ©sultats perdus saisir")] = -99
  vector[which(vector == "Not possible to read results/results are lost")] = -99
  vector[which(vector == "Not possible to read the results or the results have been lost")] = -99
  vector[which(vector == "NOT POSSIBLE TO READ THE RESULTS OR THE RESULTS HAVE BEEN LOST")] = -99
  vector[which(vector == "Pas possible de lire les rÃ©sultats ou les rÃ©sultats ont Ã©tÃ© perdus")] = -99
  vector[which(vector == "Pas possible de lire les r?sultats ou les r?sultats ont ?t? perdus")] = -99
  vector[which(vector == "Pas possible de lire les résultats ou les résultats ont été perdus")] = -99
  vector[which(vector == "PAS POSSIBLE DE LIRE LES RESULTATS")] = -99
  vector[which(vector == "NOT POSSIBLE TO READ THE RESULTS")] = -99
  vector[which(vector == "NÃO SE CONSEGUE LER OS RESULTADOS OU RESULTADOS PERDIDOS")] = -99
  vector[which(vector == "Não é possível ler os resultados ou os resultados perderam")] = -99
  vector[which(vector == "LES RESULTATS PERDUS")] = -99
  vector[which(vector == "THE RESULTS HAVE BEEN LOST")] = -99
  vector[which(vector == "test microbienne non rÃ©alisÃ©")] = -99
  vector[which(vector == "Microbial testing not done")] = -99
  vector[which(vector == "impossible de lire les rÃ©sultats/ RÃ©sultats perdus saisir")] = -99
  vector[which(vector == "No Reportado")] = -99
  
  return(vector)				
}	


#setWRiskBIN <- function(vector){
 # vector[which(vector >0)] = 1
  #return(vector)
#}

#HH6

setArea	 <- function(vector) {			
  #urban
  vector[which(vector == "Urbain")] = 1
  vector[which(vector == "URBAN")] = 1
  vector[which(vector == "URBAIN")] = 1
  vector[which(vector == "Urban")] = 1
  vector[which(vector == "Urbano")] = 1
  vector[which(vector == "Urbana")] = 1
  vector[which(vector == "URBANO")] = 1
  #rural
  vector[which(vector == "Rural")] = 2
  vector[which(vector == "RURAL")] = 2
  vector[which(vector == "RURAL WITHOUT ROAD")] = 2
  vector[which(vector == "RURAL WITH ROAD")] = 2
  vector[which(vector == "RURAL INTERIOR")] = 2
  vector[which(vector == "RURAL COASTAL")] = 2
  #camp
  vector[which(vector == "CAMP")] = 3
  return(vector)
}

labelingSurveyVariableResponses <- function(df.MICS.SMDW){
  
  df.MICS.SMDW$WQ27_conc <- setWaterQuality(df.MICS.SMDW$WQ27)
  df.MICS.SMDW$WQ27 <- setWRiskBIN(df.MICS.SMDW$WQ27_conc)#as.numeric()
  df.MICS.SMDW$WS3 <- setWslocation(df.MICS.SMDW$WS3)#as.numeric()
  df.MICS.SMDW$WS7 <- setWaterSuff(df.MICS.SMDW$WS7)#as.numeric()
  df.MICS.SMDW$HH6 <- setArea(df.MICS.SMDW$HH6)#as.numeric()
  df.MICS.SMDW$WS1 <- setMainSource(df.MICS.SMDW$WS1)
  df.MICS.SMDW$WS2 <- setMainSource(df.MICS.SMDW$WS2)
  df.MICS.SMDW$WS4 <- setWs4time(df.MICS.SMDW$WS4)
  df.MICS.SMDW$WS8 <- setWhyInsuff(df.MICS.SMDW$WS8)
  return(df.MICS.SMDW)
}
