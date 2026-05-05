

countryLevel1 = ['Gambia','Iraq','Togo', 'Chad','Georgia','Ghana','Guinea-Bissau','Guyana','Laos','Lesotho','Nigeria','Paraguay','Sierra Leone','Suriname','Tonga','Zimbabwe','Kongo','Benin','Honduras', 'Tuvalu','Vanuatu', 'Swaziland' ]


##/ Define the new regions for Level 1

# Tunisia (Nour)
TUNISIA_DISTRICT_TUNIS = ['Tunis','Manubah']
TUNISIA_NORD_EST = ['Bizerte','Nabeul','Zaghouan']
TUNISIA_NORD_OUEST = ['Béja','Jendouba','Le Kef','Siliana']
TUNISIA_CENTRE_EST = ['Mahdia','Monastir','Sfax','Sousse']
TUNISIA_CENTRE_OUEST = ['Kassérine','Kairouan','Sidi Bou Zid']
TUNISIA_SUD_EST = ['Gabès','Médenine','Tataouine']
TUNISIA_SUD_OUEST = ['Gafsa','Kebili','Tozeur']

# Vietnam (Nour)
NORTHERN_MIDLAND = ['Hà Giang','Cao Bằng','Lào Cai','Lai Châu','Bắc Kạn','Tuyên Quang','Lạng Sơn','Yên Bái','Điện Biên','Thái Nguyên','Bắc Giang','Phú Thọ','Sơn La','Hòa Bình']
RED_RIVER_DELTA = ['Vĩnh Phúc','Quảng Ninh','Bắc Ninh','Hà Nội','Hải Dương','Hưng Yên','Hải Phòng','Hà Nam','Thái Bình','Nam Định','Ninh Bình']
NORTH_CENTRAL_AND_COASTAL = ['Thanh Hóa','Nghệ An','Hà Tĩnh','Quảng Bình','Quảng Trị','Thừa Thiên - Huế','Đà Nẵng','Quảng Nam','Quảng Ngãi','Bình Định','Phú Yên','Khánh Hòa','Ninh Thuận','Bình Thuận']
CENTRAL_HIGHLANDS = ['Kon Tum','Gia Lai','Đắk Lắk','Đăk Nông','Lâm Đồng']
SOUTH_EAST = ['Bình Phước','Tây Ninh','Bình Dương','Đồng Nai','Hồ Chí Minh city','Bà Rịa - Vũng Tàu']
MEKONG_DELTA = ['Long An','Đồng Tháp','An Giang','Tiền Giang','Bến Tre','Cần Thơ','Vĩnh Long','Kiên Giang','Trà Vinh','Hậu Giang','Sóc Trăng','Bạc Liêu','Cà Mau']

# Dominican Republic (Nour )
OZAMA = ['Distrito Nacional','Santo Domingo']
VALDESIA = ['Azua','Peravia','San José de Ocoa','San Cristóbal']
ENRIQUILLO = ['Barahona','Bahoruco','Independencia','Pedernales']
CIBAO_NORDESTE = ['Duarte','Salcedo','María Trinidad Sánchez','Samaná']
CIBAO_NOROESTE = ['Dajabón','Monte Cristi','Santiago Rodríguez','Valverde']
CIBAO_NORTE = ['Espaillat','Puerto Plata','Santiago']
CIBAO_SUR = ['La Vega','Monseñor Nouel','Sánchez Ramírez']
EL_VALLE = ['La Estrelleta','San Juan']
HIGUAMO = ['Hato Mayor','Monte Plata','San Pedro de Macorís']
YUMA = ['El Seybo','La Romana','La Altagracia']

# Malawi (Nour)
NORTH = ['Chitipa','Karonga','Likoma','Mzimba','Nkhata Bay','Rumphi']
CENTRAL = ['Dedza','Dowa','Kasungu','Lilongwe','Mchinji','Nkhotakota','Ntcheu','Ntchisi','Salima']
SOUTH = ['Balaka','Blantyre','Chikwawa','Chiradzulu','Machinga','Mangochi','Mulanje','Mwanza','Neno','Nsanje','Phalombe','Thyolo','Zomba']


# Fidji (Nour)
#WESTERN =  ["Western"]
#EASTERN =  ["Eastern"]
#CENTRAL =  ["Central"]
#NORTHERN = ["Northern"]



# NEW COUNTRIES

# Vietnam
NORTHERN_MIDLAND = GADM_level1_prep.filterMetadata('NAME_0','equals','Vietnam').filter(ee.Filter.inList("NAME_1",NORTHERN_MIDLAND))
RED_RIVER_DELTA = GADM_level1_prep.filterMetadata('NAME_0','equals','Vietnam').filter(ee.Filter.inList("NAME_1",RED_RIVER_DELTA))
NORTH_CENTRAL_AND_COASTAL = GADM_level1_prep.filterMetadata('NAME_0','equals','Vietnam').filter(ee.Filter.inList("NAME_1",NORTH_CENTRAL_AND_COASTAL))
CENTRAL_HIGHLANDS = GADM_level1_prep.filterMetadata('NAME_0','equals','Vietnam').filter(ee.Filter.inList("NAME_1",CENTRAL_HIGHLANDS))
SOUTH_EAST = GADM_level1_prep.filterMetadata('NAME_0','equals','Vietnam').filter(ee.Filter.inList("NAME_1",SOUTH_EAST))
MEKONG_DELTA = GADM_level1_prep.filterMetadata('NAME_0','equals','Vietnam').filter(ee.Filter.inList("NAME_1",MEKONG_DELTA))

# Malawi 
NORTH = GADM_level1_prep.filterMetadata('NAME_0','equals','Malawi').filter(ee.Filter.inList("NAME_1",NORTH))
CENTRAL = GADM_level1_prep.filterMetadata('NAME_0','equals','Malawi').filter(ee.Filter.inList("NAME_1",CENTRAL))
SOUTH = GADM_level1_prep.filterMetadata('NAME_0','equals','Malawi').filter(ee.Filter.inList("NAME_1",SOUTH))

# Dominican Republic
OZAMA = GADM_level1_prep.filterMetadata('NAME_0','equals','Dominican Republic').filter(ee.Filter.inList("NAME_1",OZAMA))
VALDESIA = GADM_level1_prep.filterMetadata('NAME_0','equals','Dominican Republic').filter(ee.Filter.inList("NAME_1",VALDESIA))
ENRIQUILLO = GADM_level1_prep.filterMetadata('NAME_0','equals','Dominican Republic').filter(ee.Filter.inList("NAME_1",ENRIQUILLO))
CIBAO_NORDESTE = GADM_level1_prep.filterMetadata('NAME_0','equals','Dominican Republic').filter(ee.Filter.inList("NAME_1",CIBAO_NORDESTE))
CIBAO_NOROESTE = GADM_level1_prep.filterMetadata('NAME_0','equals','Dominican Republic').filter(ee.Filter.inList("NAME_1",CIBAO_NOROESTE))
CIBAO_NORTE = GADM_level1_prep.filterMetadata('NAME_0','equals','Dominican Republic').filter(ee.Filter.inList("NAME_1",CIBAO_NORTE))
CIBAO_SUR = GADM_level1_prep.filterMetadata('NAME_0','equals','Dominican Republic').filter(ee.Filter.inList("NAME_1",CIBAO_SUR))
EL_VALLE = GADM_level1_prep.filterMetadata('NAME_0','equals','Dominican Republic').filter(ee.Filter.inList("NAME_1",EL_VALLE))
HIGUAMO = GADM_level1_prep.filterMetadata('NAME_0','equals','Dominican Republic').filter(ee.Filter.inList("NAME_1",HIGUAMO))
YUMA = GADM_level1_prep.filterMetadata('NAME_0','equals','Dominican Republic').filter(ee.Filter.inList("NAME_1",YUMA))


# (new ones  added)

Vietnam = ee.FeatureCollection([
    ee.Feature(NORTHERN_MIDLAND.union().geometry()).set('NAME_0','Vietnam').set('NAME_1','NORTHERN MIDLAND').set('NAME_1s',NORTHERN_MIDLAND.aggregate_array('NAME_1').join('|')).set('GID_1s',NORTHERN_MIDLAND.aggregate_array('GID_1').join('|')).set('HH7','NORTHERN_MIDLAND'),
    ee.Feature(RED_RIVER_DELTA.union().geometry()).set('NAME_0','Vietnam').set('NAME_1','RED RIVER DELTA').set('NAME_1s',RED_RIVER_DELTA.aggregate_array('NAME_1').join('|')).set('GID_1s',RED_RIVER_DELTA.aggregate_array('GID_1').join('|')).set('HH7','RED_RIVER_DELTA'),
    ee.Feature(NORTH_CENTRAL_AND_COASTAL.union().geometry()).set('NAME_0','Vietnam').set('NAME_1','NORTH CENTRAL AND CENTRAL COASTAL AREA').set('NAME_1s',NORTH_CENTRAL_AND_COASTAL.aggregate_array('NAME_1').join('|')).set('GID_1s',NORTH_CENTRAL_AND_COASTAL.aggregate_array('GID_1').join('|')).set('HH7','NORTH_CENTRAL_AND_COASTAL'),
    ee.Feature(CENTRAL_HIGHLANDS.union().geometry()).set('NAME_0','Vietnam').set('NAME_1','CENTRAL HIGHLANDS').set('NAME_1s',CENTRAL_HIGHLANDS.aggregate_array('NAME_1').join('|')).set('GID_1s',CENTRAL_HIGHLANDS.aggregate_array('GID_1').join('|')).set('HH7','CENTRAL_HIGHLANDS'),
    ee.Feature(SOUTH_EAST.union().geometry()).set('NAME_0','Vietnam').set('NAME_1','SOUTH EAST').set('NAME_1s',SOUTH_EAST.aggregate_array('NAME_1').join('|')).set('GID_1s',SOUTH_EAST.aggregate_array('GID_1').join('|')).set('HH7','SOUTH_EAST'),
    ee.Feature(MEKONG_DELTA.union().geometry()).set('NAME_0','Vietnam').set('NAME_1','MEKONG DELTA').set('NAME_1s',MEKONG_DELTA.aggregate_array('NAME_1').join('|')).set('GID_1s',MEKONG_DELTA.aggregate_array('GID_1').join('|')).set('HH7','MEKONG_DELTA')
])

Malawi = ee.FeatureCollection([
    ee.Feature(NORTH.union().geometry()).set('NAME_0','Malawi').set('NAME_1','NORTH').set('NAME_1s',NORTH.aggregate_array('NAME_1').join('|')).set('GID_1s',NORTH.aggregate_array('GID_1').join('|')).set('HH7','NORTH'),
    ee.Feature(CENTRAL.union().geometry()).set('NAME_0','Malawi').set('NAME_1','CENTRAL').set('NAME_1s',CENTRAL.aggregate_array('NAME_1').join('|')).set('GID_1s',CENTRAL.aggregate_array('GID_1').join('|')).set('HH7','CENTRAL'),
    ee.Feature(SOUTH.union().geometry()).set('NAME_0','Malawi').set('NAME_1','SOUTH').set('NAME_1s',SOUTH.aggregate_array('NAME_1').join('|')).set('GID_1s',SOUTH.aggregate_array('GID_1').join('|')).set('HH7','SOUTH')
])

Dominican_Republic = ee.FeatureCollection([
    ee.Feature(OZAMA.union().geometry()).set('NAME_0','Dominican Republic').set('NAME_1','OZAMA').set('NAME_1s',OZAMA.aggregate_array('NAME_1').join('|')).set('GID_1s',OZAMA.aggregate_array('GID_1').join('|')).set('HH7','OZAMA'),
    ee.Feature(VALDESIA.union().geometry()).set('NAME_0','Dominican Republic').set('NAME_1','VALDESIA').set('NAME_1s',VALDESIA.aggregate_array('NAME_1').join('|')).set('GID_1s',VALDESIA.aggregate_array('GID_1').join('|')).set('HH7','VALDESIA'),
    ee.Feature(ENRIQUILLO.union().geometry()).set('NAME_0','Dominican Republic').set('NAME_1','ENRIQUILLO').set('NAME_1s',ENRIQUILLO.aggregate_array('NAME_1').join('|')).set('GID_1s',ENRIQUILLO.aggregate_array('GID_1').join('|')).set('HH7','ENRIQUILLO'),
    ee.Feature(CIBAO_NORDESTE.union().geometry()).set('NAME_0','Dominican Republic').set('NAME_1','CIBAO_NORDESTE').set('NAME_1s',CIBAO_NORDESTE.aggregate_array('NAME_1').join('|')).set('GID_1s',CIBAO_NORDESTE.aggregate_array('GID_1').join('|')).set('HH7','CIBAO_NORDESTE'),
    ee.Feature(CIBAO_NOROESTE.union().geometry()).set('NAME_0','Dominican Republic').set('NAME_1','CIBAO_NOROESTE').set('NAME_1s',CIBAO_NOROESTE.aggregate_array('NAME_1').join('|')).set('GID_1s',CIBAO_NOROESTE.aggregate_array('GID_1').join('|')).set('HH7','CIBAO_NOROESTE'),
    ee.Feature(CIBAO_NORTE.union().geometry()).set('NAME_0','Dominican Republic').set('NAME_1','CIBAO_NORTE').set('NAME_1s',CIBAO_NORTE.aggregate_array('NAME_1').join('|')).set('GID_1s',CIBAO_NORTE.aggregate_array('GID_1').join('|')).set('HH7','CIBAO_NORTE'),
    ee.Feature(CIBAO_SUR.union().geometry()).set('NAME_0','Dominican Republic').set('NAME_1','CIBAO_SUR').set('NAME_1s',CIBAO_SUR.aggregate_array('NAME_1').join('|')).set('GID_1s',CIBAO_SUR.aggregate_array('GID_1').join('|')).set('HH7','CIBAO_SUR'),
    ee.Feature(EL_VALLE.union().geometry()).set('NAME_0','Dominican Republic').set('NAME_1','EL_VALLE').set('NAME_1s',EL_VALLE.aggregate_array('NAME_1').join('|')).set('GID_1s',EL_VALLE.aggregate_array('GID_1').join('|')).set('HH7','EL_VALLE'),
    ee.Feature(HIGUAMO.union().geometry()).set('NAME_0','Dominican Republic').set('NAME_1','HIGUAMO').set('NAME_1s',HIGUAMO.aggregate_array('NAME_1').join('|')).set('GID_1s',HIGUAMO.aggregate_array('GID_1').join('|')).set('HH7','HIGUAMO'),
    ee.Feature(YUMA.union().geometry()).set('NAME_0','Dominican Republic').set('NAME_1','YUMA').set('NAME_1s',YUMA.aggregate_array('NAME_1').join('|')).set('GID_1s',YUMA.aggregate_array('GID_1').join('|')).set('HH7','YUMA')
])

GADM_level1 = GADM_level1.merge(Algeria).merge(CAR).merge(Tunisia).merge(Mongolia).merge(Vietnam).merge(Malawi).merge(Dominican_Republic)
