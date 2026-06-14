# config/manual_region_fixes.R
# Manual crosswalk corrections mapping survey region names to their matching
# names in the geospatial covariate files.
#
# HOW TO ADD A NEW ENTRY:
#   1. Run the pipeline and check `crosswalk_*$regions_to_review`
#   2. Find the correct covariate region name (inspect df_training_covariates)
#   3. Add a row below: HH7_region_outcome | country_cov | correct_region_name
#   4. Re-run the pipeline — do NOT edit the .qmd script directly

manual_fixes_sanitation <- tibble::tribble(
  ~HH7_region_outcome,                         ~country_cov,                              ~correct_region_name,
  #Armenia
  "Aragatsotn",                                "Armenia",                                 "Aragatsotn Aragatsotn Aragatsotn",
  
  # Afghanistan
  "MAIDAN WARDAK",                             "Afghanistan",                             "Wardak",
  
  # Chad
  "Ndjamena",                                  "Chad",                                    "Ville de N'Djamena",
  "Ouadda?",                                   "Chad",                                    "Ouaddaï",
  
  # Democratic Republic of the Congo
  "Maindombe",                                 "Democratic Republic of the Congo",        "Maï-Ndombe",
  
  # Georgia
  "KHAKHETI",                                  "Georgia",                                 "Kakheti",
  
  # Guinea-Bissau
  "SAB",                                       "Guinea-Bissau",                           "Bissau",
  
  # Iraq
  "DUHOK",                                     "Iraq",                                    "Dihok",
  "ERBIL",                                     "Iraq",                                    "Arbil",
  "THIQAR",                                    "Iraq",                                    "Dhi-Qar",
  "NAINAWA",                                   "Iraq",                                    "Ninawa",
  "KARBALAH",                                  "Iraq",                                    "Karbala'",
  "DIALA",                                     "Iraq",                                    "Diyala",
  "SALAHADDIN",                                "Iraq",                                    "Sala ad-Din",
  "ANBAR",                                     "Iraq",                                    "Al-Anbar",
  "BASRAH",                                    "Iraq",                                    "Al-Basrah",
  "QADISYAH",                                  "Iraq",                                    "Al-Qadisiyah",
  "NAJAF",                                     "Iraq",                                    "An-Najaf",
  "MISAN",                                     "Iraq",                                    "Maysan",
  "SULAIMANIYA",                               "Iraq",                                    "As-Sulaymaniyah",
  "MUTHANA",                                   "Iraq",                                    "Al-Muthannia",
  "KIRKUK",                                    "Iraq",                                    "At-Ta'mim",
  
  # Kiribati
  "LINE AND PHOENIX GROUP",                    "Kiribati",                                "LINE_AND_PHOENIX",
  
  # Kazakhstan
  "ABAY",             "Kazakhstan", "Abay Region",
  "AKMOLA",           "Kazakhstan", "Akmola Region",
  "AKTOBE",           "Kazakhstan", "Aktobe Region",
  "ALMATY CITY",      "Kazakhstan", "Almaty",
  "ASTANA CITY",      "Kazakhstan", "Astana",
  "ATYRAU",           "Kazakhstan", "Atyrau Region",
  "EAST KAZAKHSTAN",  "Kazakhstan", "East Kazakhstan Region",
  "KARAGANDA",        "Kazakhstan", "Karaganda Region",
  "KOSTANAY",         "Kazakhstan", "Kostanay Region",
  "KYZYLORDA",        "Kazakhstan", "Kyzylorda Region",
  "MANGYSTAU",        "Kazakhstan", "Mangystau Region",
  "NORTH KAZAKHSTAN", "Kazakhstan", "North Kazakhstan Region",
  "PAVLODAR",         "Kazakhstan", "Pavlodar Region",
  "SHYMKENT CITY",    "Kazakhstan", "Shymkent",
  "TURKISTAN",        "Kazakhstan", "Turkistan Region",
  "ULYTAU",           "Kazakhstan", "Ulytau Region",
  "WEST KAZAKHSTAN",  "Kazakhstan", "West Kazakhstan Region",
  "ZHAMBYL",          "Kazakhstan", "Jambyl Region",
  "ZHETYSU",          "Kazakhstan", "Jetisu Region",
  
  # Lao PDR
  "XAYSOMBOUN",                                "Lao People's Democratic Republic",        "Xaysomboune",
  "KHAMMUAN",                                  "Lao People's Democratic Republic",        "Khammua",
  
  # Lesotho
  "MOHALES HOEK",                              "Lesotho",                                 "Mohale's Hoek",
  "QACHAS NEK",                                "Lesotho",                                 "Qacha's Nek",
  
  # Malawi
  "Dowa (Camps)",                              "Malawi",                                  "Dowa",
  
  # Nepal
  "Sudurpashchim",                             "Nepal",                                   "Sudur Paschim",
  

  # São Tomé and Príncipe
  "REGIÃO AUTÓNOMA DO PRÍNCIPE",               "São Tomé and Príncipe",                   "Príncipe",
  
  # Tonga
  "ONGO NIUA",                                 "Tonga",                                   "Niuas",
  
  # Tuvalu
  "Nanumaga",                                  "Tuvalu",                                  "Nanumanga",
  "Funafuti",                                  "Tuvalu",                                  "Funafuti",
  "Nanumea",                                   "Tuvalu",                                  "Nanumea",
  "Niutao",                                    "Tuvalu",                                  "Niutao",
  "Nui",                                       "Tuvalu",                                  "Nui",
  "Nukufetau",                                 "Tuvalu",                                  "Nukufetau",
  "Vaitupu",                                   "Tuvalu",                                  "Vaitupu",
  
  # Vietnam
  "NORTH CENTRAL AND CENTRAL COASTAL",         "Vietnam",                                 "NORTH_CENTRAL_AND_COASTAL",
  
  # West Bank and Gaza
  "Qalqilia",                                  "Palestina",                               "Qalqilya",
  "Ariha & Al Aghwar",                         "Palestina",                               "Jericho",
  "North Gaza",                                "Palestina",                               "Gaza ash Shamaliyah",
  
  # Argentina
  "CIUDAD Y PARTIDOS DE BUENOS AIRES",                     "Argentina",   "CIUDAD_Y_PARTIDOS_DE_BUENOS_AIRES_Argentina",
  "RESTO PROVINCIA DE BUENOS AIRES",                       "Argentina",   "RESTO_PROVINCIA_DE_BUENOS_AIRES_Argentina",
  "CUYO",                                                  "Argentina",   "CUYO_Argentina",
  "NOA",                                                   "Argentina",   "NOA_Argentina",
  "NEA",                                                   "Argentina",   "NEA_Argentina",
  "PAMPEANA (EXCLUYE RESTO DE PROVINCIA DE BUENOS AIRES",  "Argentina",   "PAMPEANA_Argentina",
  "PATAGÓNICA",                                            "Argentina",   "PATAGONICA_Argentina",
  
  # Nauru
  "AIWO",       "Nauru",  "AIWO_Nauru",
  "ANABAR",     "Nauru",  "ANABAR_Nauru",
  "ANETAN",     "Nauru",  "ANETAN_Nauru",
  "ANIBARE",    "Nauru",  "ANIBARE_Nauru",
  "BAITSI",     "Nauru",  "BAITSI_Nauru",
  "BOE",        "Nauru",  "BOE_Nauru",
  "BUADA",      "Nauru",  "BUADA_Nauru",
  "DENIGOMODU", "Nauru",  "DENIGOMODU_Nauru",
  "EWA",        "Nauru",  "EWA_Nauru",
  "IJUW",       "Nauru",  "IJUW_Nauru",
  "MENENG",     "Nauru",  "MENENG_Nauru",
  "NIBOK",      "Nauru",  "NIBOK_Nauru",
  "UABOE",      "Nauru",  "UABOE_Nauru",
  "YAREN",      "Nauru",  "YAREN_Nauru",

  
  # Turkmenistan
  "AKHAL VELAYAT",    "Turkmenistan",  "AKHAL_ARKADAG_Turkmenistan",
  "ARKADAG CITY",     "Turkmenistan",  "ASHGABAT_CITY_Turkmenistan",
  "BALKAN VELAYAT",   "Turkmenistan",  "BALKAN_Turkmenistan",
  "DASHOGUZ VELAYAT", "Turkmenistan",  "DASHOGUZ_Turkmenistan",
  "LEBAP VELAYAT",    "Turkmenistan",  "LEBAP_Turkmenistan",
  "MARY VELAYAT",     "Turkmenistan",  "MARY_Turkmenistan",
  
  # Trinidad and Tobago
  "Eastern RHA",       "Trinidad and Tobago",  "Eastern_RHA_Trinidad_and_Tobago",
  "North-Central RHA", "Trinidad and Tobago",  "North_Central_RHA_Trinidad_and_Tobago",
  "North-West RHA",    "Trinidad and Tobago",  "North_West_RHA_Trinidad_and_Tobago",
  "South-West RHA",    "Trinidad and Tobago",  "South_West_RHA_Trinidad_and_Tobago",
  "Tobago RHA",        "Trinidad and Tobago",  "Tobago_RHA_Trinidad_and_Tobago",
  
  #Uganda
  "North Buganda",                             "Uganda",                                  "Buganda north",
  "South Buganda",                             "Uganda",                                  "Buganda south",
  
  # North Macedonia
  "EAST",       "North Macedonia",  "EAST_North_Macedonia",
  "NORTHEAST",  "North Macedonia",  "NORTHEAST_North_Macedonia",
  "PELAGONIJA", "North Macedonia",  "PELAGONIJA_North_Macedonia",
  "POLOG",      "North Macedonia",  "POLOG_North_Macedonia",
  "SKOPJE",     "North Macedonia",  "SKOPJE_North_Macedonia",
  "SOUTHEAST",  "North Macedonia",  "SOUTHEAST_North_Macedonia",
  "SOUTHWEST",  "North Macedonia",  "SOUTHWEST_North_Macedonia",
  "VARDAR",     "North Macedonia",  "VARDAR_North_Macedonia"
  

)

# Pakistan
#"Chaghi",                                    "Pakistan",                                "Chagai",
#"DG Khan",                                   "Pakistan",                                "Dera Ghazi Khan",
#"Kachhi (Bolan)",                            "Pakistan",                                "Kachhi",
#"Bajor",                                     "Pakistan",                                "Bajaur",
#"TT Singh",                                  "Pakistan",                                "Toba Tek Singh",
#"RY Khan",                                   "Pakistan",                                "Rahim Yar Khan",
#"Laki Marwat",                               "Pakistan",                                "Lakki Marwat",
#"Abbotabad",                                 "Pakistan",                                "Abbottabad",
#"Nowshehra",                                 "Pakistan",                                "Nowshera",
#"Sheerani",                                  "Pakistan",                                "Sherani",
#"Hari Pur",                                  "Pakistan",                                "Haripur",
#"Torghar",                                   "Pakistan",                                "Tor Ghar",
#"Kuram",                                     "Pakistan",                                "Kurram",
#"Sibbi",                                     "Pakistan",                                "Sibi",
#"Mohmind",                                   "Pakistan",                                "Mohmand",
#"Kech (Turbat)",                             "Pakistan",                                "Kech",

# Costa Rica
#"Alajuela",   "Costa Rica",  "Alajuela_Costa_Rica",
#"Cartago",    "Costa Rica",  "Cartago_Costa_Rica",
#"Guanacaste", "Costa Rica",  "Guanacaste_Costa_Rica",
#"Heredia",    "Costa Rica",  "Heredia_Costa_Rica",
#"Limón",      "Costa Rica",  "Limon_Costa_Rica",
#"Limon",      "Costa Rica",  "Limon_Costa_Rica",
#"Puntarenas", "Costa Rica",  "Puntarenas_Costa_Rica",
#"San José",   "Costa Rica",  "San_Jose_Costa_Rica",
#"San Jose",   "Costa Rica",  "San_Jose_Costa_Rica"
