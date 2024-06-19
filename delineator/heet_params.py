import ee
import math
import heet_config as cfg
import logging
import heet_export
import heet_monitor as mtr
import heet_data as dta
# ==============================================================================
#  Set up logger
# ==============================================================================

# Gets or creates a logger
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.DEBUG)

# define file handler and set formatter
file_handler = logging.FileHandler('heet.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)


# ==============================================================================
# Catchment, Reservoir, River Parameters
# ==============================================================================
debug_mode = False

# Catchment/reservoir area (km)


def area(land_ftc):
    land_geom = land_ftc.geometry()
    return land_geom.area(1).divide(1000 * 1000)


# Mean slope (%)
def degrees_to_perc_slope(mean_slope_degrees):
    return (ee.Number(mean_slope_degrees)
            .multiply(math.pi / 180).tan().multiply(100))


def mean_slope_perc(catchment_ftc):

    catchment_geom = catchment_ftc.geometry()

    DEM = ee.Image("USGS/SRTMGL1_003")
    # Expected SCALE = 30

    projection = ee.Image(DEM).projection()
    SCALE = projection.nominalScale()

    elevationDEM = ee.Image(DEM).select('elevation')
    slopeDEM = ee.Terrain.slope(elevationDEM)

    mean_slope_degrees = slopeDEM.reduceRegion(**{
        'reducer': ee.Reducer.mean(),
        'geometry': catchment_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    }).get('slope')

    mean_slope_perc = degrees_to_perc_slope(mean_slope_degrees)

    return mean_slope_perc


def mean_soil_org_ca(land_ftc):

    SOIL_CARBON = ee.Image("projects/soilgrids-isric/ocs_mean")
    # Expected SCALE = 250

    projection = ee.Image(SOIL_CARBON).projection()
    SCALE = projection.nominalScale()

    land_geom = land_ftc.geometry()

    mean_soil_carbon_kgpm2 = ee.Number(SOIL_CARBON.reduceRegion(**{
        'reducer': ee.Reducer.mean(),
        'geometry': land_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    }).get('ocs_0-30cm_mean')).multiply(0.1)

    # Handle null values
    mean_soil_carbon_kgpm2_value = ee.Number(ee.Algorithms.If(
        mean_soil_carbon_kgpm2,
        mean_soil_carbon_kgpm2,
        -999
    ))

    return(mean_soil_carbon_kgpm2_value)


def landcover(land_ftc):

    LANDCOVER_ESA = ee.Image("users/KamillaHarding/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds-lccs_class")
    # Expected SCALE = 300

    projection = ee.Image(LANDCOVER_ESA).projection()
    SCALE = projection.nominalScale()

    LANDCOVER_IHA = LANDCOVER_ESA.remap(
        # ESA CODES
        [
            0,
            10, 20,
            100, 110, 120, 121, 122, 130, 140, 150, 152, 153, 151, 30, 40, 11,
            12, 50, 60, 61, 62, 70, 71, 72, 80, 81, 82, 90,
            160, 170, 180,
            190,
            200, 201, 202,
            210,
            220
        ],
        # IHA CODES
        [
            0,
            1, 1,
            2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
            4, 4, 4,
            5,
            6, 6, 6,
            7,
            8
        ]
    ).select(['remapped'], ['land_use'])

    land_geom = land_ftc.geometry()
    land_buffer_geom = land_geom.buffer(600)
    land_bbox = land_geom.bounds()

    ihaCategories = ee.Dictionary({
        '0': 'No Data',
        '1': 'Croplands',
        '2': 'Grassland/Shrubland',
        '3': 'Forest',
        '4': 'Wetlands',
        '5': 'Settlements',
        '6': 'Bare Areas',
        '7': 'Water Bodies',
        '8': 'Permanent snow and ice'
    })

    frequency = LANDCOVER_IHA.reduceRegion(**{
        'reducer': ee.Reducer.frequencyHistogram().unweighted(),
        'geometry': land_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    })

    if debug_mode == True:
        print("[DEBUG] Frequency", frequency.getInfo())

    total_count = (
        ee.Dictionary(frequency.get('land_use'))
        .toArray().toList()
    ).reduce(ee.Reducer.sum())

    fractions = (
        ee.Dictionary(frequency.get('land_use')).toArray().toList().map(
            lambda v: ee.Number(v).divide(total_count)
        ))

    group_count = ihaCategories.keys().length()
    codes = ee.Dictionary(frequency.get('land_use')).keys()

    fractions_dict = ee.Dictionary.fromLists(codes, fractions)
    fractions_list = ee.List.sequence(0, group_count.subtract(1))
    fractions_list_str = fractions_list.map(lambda i: ee.Number(i).format("%.0f"))

    if debug_mode == True:
        print("[DEBUG] Frequency", frequency.getInfo())
        print("[DEBUG] Fractions", fractions.getInfo())
        print("[DEBUG] Codes", codes.getInfo())

        print("[DEBUG] fractions_list", fractions_list_str.getInfo())
        print("[DEBUG] fractions_dict", fractions_dict.getInfo())

    populated_fractions_list = fractions_list_str.map(
        lambda i: ee.Number(fractions_dict.get(i, ee.Number(0)))
    )

    return populated_fractions_list


def soil_type(target_ftc):

    # >=40 kg/m2; Organic
    #  <40 kg/m2; Mineral
    target_geom = target_ftc.geometry()

    # Soil Type
    SOIL_CARBON_CAT = (
        ee.Image("projects/soilgrids-isric/ocs_mean").multiply(0.1).gte(40)
    )

    # Expected SCALE = 1000
    projection = ee.Image(SOIL_CARBON_CAT).projection()
    SCALE = projection.nominalScale()

    stats = SOIL_CARBON_CAT.reduceRegion(**{
        'reducer': ee.Reducer.mode(),
        'geometry': target_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    })

    stats = stats.map(
        lambda k, v: ee.Algorithms.If(ee.Algorithms.IsEqual(v, None), -999, stats.get(k))
    )

    metric = ee.Number(stats.get('ocs_0-30cm_mean')).format('%.0f')

    codes = {
        '-999': "NODATA",
        '0': 'MINERAL',
        '1': 'ORGANIC'
    }

    modal_soil_category = ee.Dictionary(codes).get(metric)
    return modal_soil_category


def landcover_bysoil(land_ftc):

    # >=40 kg/m2; Organic
    #  <40 kg/m2; Mineral

    SOIL_CARBON_CAT = (
        ee.Image("projects/soilgrids-isric/ocs_mean").multiply(0.1).gte(40)
    )

    LANDCOVER_ESA = ee.Image("users/KamillaHarding/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds-lccs_class")
    # Expected SCALE = 300

    projection = ee.Image(LANDCOVER_ESA).projection()
    SCALE = projection.nominalScale()

    LANDCOVER_IHA = LANDCOVER_ESA.remap(
        # ESA CODES
        [
            0,
            10, 20,
            100, 110, 120, 121, 122, 130, 140, 150, 152, 153, 151, 30, 40, 11,
            12, 50, 60, 61, 62, 70, 71, 72, 80, 81, 82, 90,
            160, 170, 180,
            190,
            200, 201, 202,
            210,
            220
        ],
        # IHA CODES
        [
            0,
            1, 1,
            2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
            4, 4, 4,
            5,
            6, 6, 6,
            7,
            8
        ]
    ).select(['remapped'], ['land_use'])

    land_geom = land_ftc.geometry()
    land_buffer_geom = land_geom.buffer(600)
    land_bbox = land_geom.bounds()

    ihaCategories = ee.Dictionary({
        '0': 'Mineral - No Data',
        '1': 'Mineral - Croplands',
        '2': 'Mineral - Grassland/Shrubland',
        '3': 'Mineral - Forest',
        '4': 'Mineral - Wetlands',
        '5': 'Mineral - Settlements',
        '6': 'Mineral - Bare Areas',
        '7': 'Mineral - Water Bodies',
        '8': 'Mineral - Permanent snow and ice',
        '9': 'Organic- No Data',
        '10': 'Organic - Croplands',
        '11': 'Organic - Grassland/Shrubland',
        '12': 'Organic - Forest',
        '13': 'Organic - Wetlands',
        '14': 'Organic - Settlements',
        '15': 'Organic - Bare Areas',
        '16': 'Organic - Water Bodies',
        '17': 'Organic - Permanent snow and ice',
        '18': 'No Data - No Data',
        '19': 'No Data - Croplands',
        '20': 'No Data - Grassland/Shrubland',
        '21': 'No Data - Forest',
        '22': 'No Data - Wetlands',
        '23': 'No Data - Settlements',
        '24': 'No Data - Bare Areas',
        '25': 'No Data - Water Bodies',
        '26': 'No Data - Permanent snow and ice'
    })

    # Histogram
    frequency = LANDCOVER_IHA.addBands(SOIL_CARBON_CAT).reduceRegion(**{
        'reducer': ee.Reducer.frequencyHistogram().unweighted().group(0),
        'geometry': land_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    }).get('groups')

    total_count = ee.List(frequency).map(lambda d:
                                         ee.List(ee.Dictionary(ee.Dictionary(d).get('histogram'))
                                                 .toArray().toList().map(lambda v: v))
                                         .reduce(ee.Reducer.sum())
                                         ).reduce(ee.Reducer.sum())

    fractions = ee.List(frequency).map(lambda d:
                                       ee.Dictionary(ee.Dictionary(d).get('histogram'))
                                       .toArray().toList().map(lambda v: ee.Number(v).divide(total_count))
                                       ).flatten()

    group_count = ihaCategories.keys().length()

    key_to_int = {
        '0': 0,
        '1': 1,
        'null': 2
    }

    def generate_codes(d):
        group_no = ee.Number.int(ee.Dictionary(d).get('group'))
        code = ee.Number(
            ee.Dictionary(ee.Dictionary(d).get('histogram'))
            .keys().map(
                lambda k: ee.Number(
                    group_no.add(
                        ee.Number(ee.Dictionary(key_to_int).get(k))
                        .multiply(group_count.divide(3)))
                ).format("%.0f")
            )
        )
        return(code)

    codes = ee.List(ee.List(frequency).map(generate_codes)).flatten()

    fractions_dict = ee.Dictionary.fromLists(codes, fractions)
    fractions_list = ee.List.sequence(0, group_count.subtract(1))
    fractions_list_str = fractions_list.map(lambda i: ee.Number(i).format("%.0f"))

    if debug_mode == True:
        print("[DEBUG] Frequency", frequency.getInfo())
        print("[DEBUG] Fractions", fractions.getInfo())
        print("[DEBUG] Codes", codes.getInfo())

        print("[DEBUG] fractions_list", fractions_list_str.getInfo())
        print("[DEBUG] fractions_dict", fractions_dict.getInfo())

    populated_fractions_list = fractions_list_str.map(
        lambda i: ee.Number(fractions_dict.get(i, ee.Number(0)))
    )

    return(populated_fractions_list)


def mghr(catchment_ftc):

    catch_geom = catchment_ftc.geometry()

    GHI_NASA_low = ee.FeatureCollection("users/KamillaHarding/XHEET_ASSETS/GHI_NASA_low")

    mghr_all = (GHI_NASA_low
                .filterBounds(catch_geom)
                .reduceColumns(ee.Reducer.mean(), ['annual'])
                .get('mean')
                )

    mghr_nov_mar = (ee.List(GHI_NASA_low
                            .filterBounds(catch_geom)
                            .reduceColumns(ee.Reducer.mean().repeat(5), ['nov', 'dec', 'jan', 'feb', 'mar'])
                            .get('mean'))
                    .reduce(ee.Reducer.mean())
                    )

    mghr_may_sept = (ee.List(GHI_NASA_low
                             .filterBounds(catch_geom)
                             .reduceColumns(ee.Reducer.mean().repeat(5), ['may', 'jun', 'jul', 'aug', 'sep'])
                             .get('mean'))
                     .reduce(ee.Reducer.mean())
                     )

    if (debug_mode == True):
        print("[DEBUG] [mghr] [mghr_all]", mghr_all.getInfo())
        print("[DEBUG] [mghr] [mghr_nov_mar]", mghr_nov_mar.getInfo())
        print("[DEBUG] [mghr] [mghr_may_sept]", mghr_may_sept.getInfo())

    return(mghr_all, mghr_nov_mar, mghr_may_sept)


def terraclim_monthly_mean(start_yr, end_yr, target_var, scale_factor, target_ftc):

    target_years = ee.List.sequence(start_yr, end_yr)
    target_geom = target_ftc.geometry()

    #print("[DEBUG]\n [terraclim_monthly_mean]\n ", target_var.getInfo())
    #print("[DEBUG]\n [terraclim_monthly_mean]\n ", target_years.getInfo())

    TERRACLIM = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').select([target_var])

    # Expected SCALE = 4638
    projection = ee.Image(TERRACLIM.first()).projection()
    SCALE = projection.nominalScale()

    # Calculation fails with null values using nominal scale
    # SCALE = 30

    def aggregate_months(year):

        date_start = ee.Date.fromYMD(year, 1, 1)
        date_end = date_start.advance(1, "year")

        year_img = (TERRACLIM
                    .filterDate(date_start, date_end)
                    .mean()
                    .set({'year': year, 'system:time_start': date_start}))
        return(year_img)

    # Convert monthly image collection to yearly
    metric_yearly_cimg = ee.ImageCollection(target_years.map(aggregate_months))

    #print("[DEBUG]\n [terraclim_annual_mean]\n ", metric_yearly_cimg.getInfo())

    # Get regional values
    def get_regional_value(img, first):

        stats = img.reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': target_geom,
            'scale': SCALE,
            'maxPixels': 2e11
        })

        # Map null values to -999
        stats = stats.map(
            lambda k, v: ee.Algorithms.If(ee.Algorithms.IsEqual(v, None), -999, stats.get(k))
        )
        metric = stats.get(target_var)
        returnValue = ee.List(first).add(metric)

        return(returnValue)

    results = ee.List([])
    regional_metrics_yearly = metric_yearly_cimg.iterate(get_regional_value, results)

    if debug_mode == True:
        print("[terraclim_monthly_mean] regional_metrics_yearly", regional_metrics_yearly.getInfo())

    mean_monthly_value = (ee.Number(
        ee.List(regional_metrics_yearly)
        .filter(ee.Filter.neq('item', -999))
        .map(lambda v: ee.Number(v).multiply(scale_factor))
        .reduce('mean')
    ))

    # Handle null values
    mean_monthly_value = ee.Algorithms.If(
        mean_monthly_value,
        mean_monthly_value,
        -999
    )

    return(mean_monthly_value)


def terraclim_annual_mean(start_yr, end_yr, target_var, scale_factor, target_ftc):

    target_years = ee.List.sequence(start_yr, end_yr)
    target_geom = target_ftc.geometry()

    #print("[DEBUG]\n [terraclim_annual_mean]\n ", target_var.getInfo())
    #print("[DEBUG]\n [terraclim_annual_mean]\n ", target_years.getInfo())

    TERRACLIM = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').select([target_var])

    # Expected SCALE = 4638
    projection = ee.Image(TERRACLIM.first()).projection()
    SCALE = projection.nominalScale()

    # Calculation fails with null values using nominal scale
    # SCALE = 30

    def aggregate_months(year):

        date_start = ee.Date.fromYMD(year, 1, 1)
        date_end = date_start.advance(1, "year")

        year_img = (TERRACLIM
                    .filterDate(date_start, date_end)
                    .sum()
                    .set({'year': year, 'system:time_start': date_start}))
        return(year_img)

    # Convert monthly image collection to yearly
    metric_yearly_cimg = ee.ImageCollection(target_years.map(aggregate_months))

    #print("[DEBUG]\n [terraclim_annual_mean]\n ", metric_yearly_cimg.getInfo())

    # Get regional values
    def get_regional_value(img, first):

        stats = img.reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': target_geom,
            'scale': SCALE,
            'maxPixels': 2e11
        })

        # Map null values to -999
        stats = stats.map(
            lambda k, v: ee.Algorithms.If(ee.Algorithms.IsEqual(v, None), -999, stats.get(k))
        )
        metric = stats.get(target_var)
        returnValue = ee.List(first).add(metric)

        return(returnValue)

    results = ee.List([])
    regional_metrics_yearly = metric_yearly_cimg.iterate(get_regional_value, results)

    mean_annual_value = (ee.Number(
        ee.List(regional_metrics_yearly)
        .filter(ee.Filter.neq('item', -999))
        .map(lambda v: ee.Number(v).multiply(scale_factor))
        .reduce('mean')
    ))

    return(mean_annual_value)


def smap_annual_mean(start_yr, end_yr, target_var, target_ftc):

    target_years = ee.List.sequence(start_yr, end_yr)
    target_geom = target_ftc.geometry()

    #print("[DEBUG]\n [terraclim_annual_mean]\n ", target_var.getInfo())
    #print("[DEBUG]\n [terraclim_annual_mean]\n ", target_years.getInfo())

    SMAP10KM = ee.ImageCollection('NASA_USDA/HSL/SMAP10KM_soil_moisture').select([target_var])

    # Expected SCALE = 10000
    projection = ee.Image(SMAP10KM.first()).projection()
    SCALE = projection.nominalScale()

    def aggregate_months(year):

        date_start = ee.Date.fromYMD(year, 1, 1)
        date_end = date_start.advance(1, "year")

        year_img = (SMAP10KM
                    .filterDate(date_start, date_end)
                    .sum()
                    .set({'year': year, 'system:time_start': date_start}))
        return(year_img)

    # Convert monthly image collection to yearly
    metric_yearly_cimg = ee.ImageCollection(target_years.map(aggregate_months))

    #print("[DEBUG]\n [terraclim_annual_mean]\n ", metric_yearly_cimg.getInfo())

    # Get regional values
    def get_regional_value(img, first):

        stats = img.reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': target_geom,
            'scale': SCALE,
            'maxPixels': 2e11
        })

        # Map null values to -999
        stats = stats.map(
            lambda k, v: ee.Algorithms.If(ee.Algorithms.IsEqual(v, None), -999, stats.get(k))
        )
        metric = stats.get(target_var)
        returnValue = ee.List(first).add(metric)

        return(returnValue)

    results = ee.List([])
    regional_metrics_yearly = metric_yearly_cimg.iterate(get_regional_value, results)

    mean_annual_value = (ee.Number(
        ee.List(regional_metrics_yearly)
        .filter(ee.Filter.neq('item', -999))
        .reduce('mean')
    ))

    return(mean_annual_value)


def smap_monthly_mean(start_yr, end_yr, target_var, target_ftc):

    target_years = ee.List.sequence(start_yr, end_yr)
    target_geom = target_ftc.geometry()

    #print("[DEBUG]\n [terraclim_monthly_mean]\n ", target_var.getInfo())
    #print("[DEBUG]\n [terraclim_monthly_mean]\n ", target_years.getInfo())

    SMAP10KM = ee.ImageCollection('NASA_USDA/HSL/SMAP10KM_soil_moisture').select([target_var])

    # Expected SCALE = 10km
    projection = ee.Image(SMAP10KM.first()).projection()
    SCALE = projection.nominalScale()

    # Calculation fails with null values using nominal scale
    # SCALE = 30

    def aggregate_months(year):

        date_start = ee.Date.fromYMD(year, 1, 1)
        date_end = date_start.advance(1, "year")

        year_img = (SMAP10KM
                    .filterDate(date_start, date_end)
                    .mean()
                    .set({'year': year, 'system:time_start': date_start}))
        return(year_img)

    # Convert monthly image collection to yearly
    metric_yearly_cimg = ee.ImageCollection(target_years.map(aggregate_months))

    #print("[DEBUG]\n [terraclim_annual_mean]\n ", metric_yearly_cimg.getInfo())

    # Get regional values
    def get_regional_value(img, first):

        stats = img.reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': target_geom,
            'scale': SCALE,
            'maxPixels': 2e11
        })

        # Map null values to -999
        stats = stats.map(
            lambda k, v: ee.Algorithms.If(ee.Algorithms.IsEqual(v, None), -999, stats.get(k))
        )
        metric = stats.get(target_var)
        returnValue = ee.List(first).add(metric)

        return(returnValue)

    results = ee.List([])
    regional_metrics_yearly = metric_yearly_cimg.iterate(get_regional_value, results)

    if debug_mode == True:
        print("[terraclim_monthly_mean] regional_metrics_yearly", regional_metrics_yearly.getInfo())

    mean_monthly_value = (ee.Number(
        ee.List(regional_metrics_yearly)
        .filter(ee.Filter.neq('item', -999))
        .reduce('mean')
    ))

    # Handle null values
    mean_monthly_value = ee.Algorithms.If(
        mean_monthly_value,
        mean_monthly_value,
        -999
    )

    return(mean_monthly_value)


# Mean annual runoff

def mean_annual_runoff_mm(catchment_ftc):

    catchment_geom = catchment_ftc.geometry()

    # FEKETE (30' ~ 55560 m )
    RUNOFF = ee.Image("users/KamillaHarding/XHEET_ASSETS/cmp_ro_grdc")

    # Expected SCALE = 55560
    projection = ee.Image(RUNOFF).projection()
    SCALE = projection.nominalScale()

    mean_runoff_mm = ee.Number(RUNOFF.reduceRegion(**{
        'reducer': ee.Reducer.mean(),
        'geometry': catchment_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    }).get('b1'))

    # Handle null values
    mean_runoff_mm_value = ee.Algorithms.If(
        mean_runoff_mm,
        mean_runoff_mm,
        -999
    )

    if debug_mode == True:
        print("[DEBUG] [mean_annual_runoff_mm]", mean_runoff_mm.getInfo())
    return mean_runoff_mm_value

# Mean precipitation


def mean_annual_prec_mm(catchment_ftc):

    # World Clim 2.1 30 Arc seconds resolution; ~900m
    BIOCLIMATE = ee.Image("users/KamillaHarding/XHEET_ASSETS/wc2-1_30s_bio_12")
    BIOPRECIPITATION = BIOCLIMATE.select(['b1'], ['bio12'])

    # Expected SCALE = 900
    projection = ee.Image(BIOCLIMATE).projection()
    SCALE = projection.nominalScale()

    catchment_geom = catchment_ftc.geometry()

    mean_annual_prec_mm = ee.Number(BIOPRECIPITATION.reduceRegion(**{
        'reducer': ee.Reducer.mean(),
        'geometry': catchment_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    }).get('bio12'))

    return mean_annual_prec_mm


# Predominant biome
def predominant_biome(catchment_ftc):

    # Biome
    BIOMES = ee.FeatureCollection("RESOLVE/ECOREGIONS/2017")

    catchment_geom = catchment_ftc.geometry()
    catchment_buffer_geom = catchment_geom.buffer(500)
    catchment_bbox = catchment_buffer_geom.bounds()

    catchment_area_m = area(catchment_ftc).multiply(1000 * 1000)

    def get_biome(feat):

        # Define biome geometry
        geom = ee.Feature(feat).geometry()

        # Calculate the area of the biome zone
        areaBiomeZone = geom.area(1)

        # calculate that area of catchment that intersects with each biome zone (A_Inter)
        unionBiomes = aCATCH.filterBounds(geom).union().first().geometry()
        A_Inter = unionBiomes.intersection(geom, 1).area(1)

        # Divide A_Inter/catchAreaValue to calculate the percentage of catch area within the biome
        perc = A_Inter.divide(catchment_area_m).multiply(100)

        return ee.Feature(feat).setMulti({'AreaBiome': areaBiomeZone, 'AreaCatch': catchment_area_m, 'PercentageBiome': perc})

    # Put a bounding box around the catchment
    # to speed up computation

    aCATCH = catchment_ftc.filterBounds(catchment_bbox)
    aBIOMES = BIOMES.filterBounds(catchment_bbox)

    # [[I-1]] Calculate area of overlap between biome and catchment
    catchBiome = aBIOMES.map(get_biome)

    biome_percentages = catchBiome.aggregate_array('PercentageBiome')
    biome_names = catchBiome.aggregate_array('BIOME_NAME')
    index_pb = ee.Array(biome_percentages).argmax().get(0)
    predominant_biome = biome_names.get(index_pb)

    return predominant_biome


def predominant_climate(catchment_ftc):

    catchment_geom = catchment_ftc.geometry()

    # Climate
    CLIMATE = ee.Image("users/KamillaHarding/XHEET_ASSETS/Beck_KG_V1_present_0p0083")

    # Expected SCALE = 1000
    projection = ee.Image(CLIMATE).projection()
    SCALE = projection.nominalScale()

    modal_climate_category = CLIMATE.reduceRegion(**{
        'reducer': ee.Reducer.mode(),
        'geometry': catchment_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    }).get('b1')

    return modal_climate_category

# Population


def population(target_ftc):

    target_geom = target_ftc.geometry()

    # ==========================================================================
    #  LOAD DATA
    # ==========================================================================
    POPULATION = ee.ImageCollection("CIESIN/GPWv411/GPW_Population_Density")

    # First image; 2020
    POPULATION = POPULATION.limit(1, 'system:time_start', False).first()
    # Expected SCALE = 927.67

    projection = ee.Image(POPULATION).projection()
    SCALE = projection.nominalScale()

    # ==========================================================================
    #  Population
    # ==========================================================================

    # Calculate the area of the catchment in km;
    targetAreaValue = target_geom.area(1).divide(1000 * 1000)

    mean_pop_density = (POPULATION
                        .reduceRegion(**{
                            'reducer': ee.Reducer.mean(),
                            'geometry': target_geom,
                            'scale': SCALE,
                            'maxPixels': 2e11
                        })).get('population_density')

    pop_count = ee.Number(mean_pop_density).multiply(targetAreaValue)

    return pop_count, mean_pop_density

# ==============================================================================
# Reservoir Parameters
# ==============================================================================

# Utils


def minimum_elevation_dam(reservoir_ftc):

    DEM = ee.Image("USGS/SRTMGL1_003")

    # Expected SCALE = 30
    projection = ee.Image(DEM).projection()
    SCALE = projection.nominalScale()

    dam_latitude = ee.Number(ee.Feature(reservoir_ftc.first()).get('ps_lat'))
    dam_longitude = ee.Number(ee.Feature(reservoir_ftc.first()).get('ps_lon'))

    dam_point_location = ee.Geometry.Point(dam_longitude, dam_latitude)

    pt_min_elevation = DEM.reduceRegion(**{
        'reducer': ee.Reducer.min(),
        'geometry': dam_point_location,
        'scale': SCALE,
        'maxPixels': 2e11
    }).get('elevation')

    return pt_min_elevation


# Not needed if maximum_depth_alt2 not used.
def minimum_elevation(reservoir_ftc):

    reservoir_geom = reservoir_ftc.geometry()

    DEM = ee.Image("USGS/SRTMGL1_003")

    # Expected SCALE = 30
    projection = ee.Image(DEM).projection()
    SCALE = projection.nominalScale()

    geom_min_elevation = ee.Number(DEM.reduceRegion(**{
        'reducer': ee.Reducer.min(),
        'geometry': reservoir_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    }).get('elevation'))

    return geom_min_elevation

# Not needed if maximum_depth_alt1, maximum_depth_alt2 not used.


def maximum_elevation(reservoir_ftc):

    reservoir_geom = reservoir_ftc.geometry()

    DEM = ee.Image("USGS/SRTMGL1_003")

    # Expected SCALE = 30
    projection = ee.Image(DEM).projection()
    SCALE = projection.nominalScale()

    geom_max_elevation = ee.Number(DEM.reduceRegion(**{
        'reducer': ee.Reducer.max(),
        'geometry': reservoir_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    }).get('elevation'))

    return geom_max_elevation

# Outputs


def maximum_depth(reservoir_ftc):

    reservoir_geom = reservoir_ftc.geometry()

    # Depth = water surface elevation - elevation
    water_level = ee.Number.parse(reservoir_ftc.first().get('_imputed_water_level'))
    min_elevation_dam = minimum_elevation_dam(reservoir_ftc)
    water_level_elevation = ee.Number(min_elevation_dam).add(water_level)

    DEM = ee.Image("USGS/SRTMGL1_003")

    # Expected SCALE = 30
    projection = ee.Image(DEM).projection()
    SCALE = projection.nominalScale()

    max_depth = ee.Number(DEM.multiply(-1).add(water_level_elevation).reduceRegion(**{
        'reducer': ee.Reducer.max(),
        'geometry': reservoir_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    }).get('elevation'))

    return max_depth


def maximum_depth_alt1(reservoir_ftc):

    # Max Depth = maximum elevation - minimum elevation
    max_elevation = ee.Number(maximum_elevation(reservoir_ftc))
    min_elevation_dam = ee.Number(minimum_elevation_dam(reservoir_ftc))

    max_depth = ee.Number(max_elevation.subtract(min_elevation_dam))

    return max_depth


def maximum_depth_alt2(reservoir_ftc):

    # Max Depth = maximum elevation - minimum elevation
    max_elevation = ee.Number(maximum_elevation(reservoir_ftc))
    min_elevation = ee.Number(minimum_elevation(reservoir_ftc))

    max_depth = ee.Number(max_elevation.subtract(min_elevation))

    return max_depth


def mean_depth(reservoir_ftc):
    reservoir_geom = reservoir_ftc.geometry()

    # Depth = water surface elevation - elevation
    water_level = ee.Number.parse(reservoir_ftc.first().get('_imputed_water_level'))
    #print("[DEBUG] reservoir_ftc", reservoir_ftc.getInfo())
    #print("[DEBUG] water_level", water_level.getInfo())
    min_elevation_dam = minimum_elevation_dam(reservoir_ftc)
    water_level_elevation = ee.Number(min_elevation_dam).add(water_level)

    DEM = ee.Image("USGS/SRTMGL1_003")

    # Expected SCALE = 30
    projection = ee.Image(DEM).projection()
    SCALE = projection.nominalScale()

    mean_depth = ee.Number(DEM.multiply(-1).add(water_level_elevation).reduceRegion(**{
        'reducer': ee.Reducer.mean(),
        'geometry': reservoir_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    }).get('elevation'))

    return mean_depth


# Reservoir volume
def km2_to_m2(surface_area):
    return ee.Number(surface_area.multiply(1000 * 1000))


def reservoir_volume(surface_area, mean_depth):
    return ee.Number(surface_area.multiply(mean_depth))


# Mean monthly temperatures
def mean_monthly_temps(reservoir_ftc):

    reservoir_geom = reservoir_ftc.geometry()

    TAVG = ee.ImageCollection("users/KamillaHarding/XHEET_ASSETS/wc2-1_30s_tavg")
    TEMPERATURE = (
        TAVG
        .select(['b1'])
        .toList(12)
    )

    # Expected SCALE = 30
    projection = ee.Image(TAVG.first()).projection()
    SCALE = projection.nominalScale()

    months = ee.List.sequence(0, 11, 1)

    def monthly_temp(m):
        stats = ee.Image(ee.List(TEMPERATURE).get(m)).reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': reservoir_geom,
            'scale': SCALE,
            'maxPixels': 2e11
        })

        stats = stats.map(
            lambda k, v: ee.Algorithms.If(ee.Algorithms.IsEqual(v, None), -999, stats.get(k))
        )

        temp_value = ee.Number(stats.get('b1')).multiply(10).round().divide(10)
        return temp_value

    temperatures = months.map(monthly_temp)

    if debug_mode == True:
        print("[mean_monthly_temps]", temperatures.getInfo())
    return temperatures


def mean_olsen_kgperha(catchment_ftc):
    catch_geom = catchment_ftc.geometry()

    OLSEN = ee.Image("users/KamillaHarding/XHEET_ASSETS/OlsenP_kgha1_World")
    # Expected SCALE = 30
    projection = ee.Image(OLSEN).projection()
    SCALE = projection.nominalScale()

    mean_p = ee.Number(OLSEN.reduceRegion(**{
        'reducer': ee.Reducer.mean(),
        'geometry': catch_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    }).get('b1'))

    return mean_p


def impute_dam_height(power_capacity, turbine_efficiency, plant_depth, mad_m3_pers):

    # turbine efficiency  * discharge * gravity acceleration * water density
    denominator = turbine_efficiency.divide(100).multiply(mad_m3_pers).multiply(9.81).multiply(1000)
    calc_dam_height = power_capacity.multiply(1e6).divide(denominator).subtract(plant_depth)
    calc_dam_height_rounded = calc_dam_height.multiply(1000).round().divide(1000)

    return calc_dam_height_rounded

# ==============================================================================
# Empty Profiles
# ==============================================================================

# For handling empty delineations


def profile_empty_point():

    properties_dict = {
        "ps_snap_displacement": "NA",
        "ps_lon": "NA",
        "ps_lat": "NA"
    }

    logger.warning('[profile_empty_point] Snapped point asset not found, profiling empty point.')
    return properties_dict


def profile_empty_catchment():

    properties_dict = {
        "c_area_km2": "NA",
        "c_mean_slope_pc": "NA",
        # Landcover
        "c_landcover_0": "NA",
        "c_landcover_1": "NA",
        "c_landcover_2": "NA",
        "c_landcover_3": "NA",
        "c_landcover_4": "NA",
        "c_landcover_5": "NA",
        "c_landcover_6": "NA",
        "c_landcover_7": "NA",
        "c_landcover_8": "NA",
        "c_mar_mm": "NA",
        "c_map_mm": "NA",
        "c_biome": "NONE",
        "c_msoc_kgperm": "NA",
        "c_masm_mm": "NA",  # Slow
        "c_masm_mm_alt1": "NA",
        "c_climate_zone": "NA",
        "c_mpet_mm": "NA",
        "c_population": "NA",
        "c_population_density": "NA",
        "c_mar_mm_alt1": "NA",  # Very Slow
        "c_mar_mm_alt2": "NA",
        "c_mean_olsen": "NA",
        "c_soil_type": "NONE",
        "c_imputed_water_level": "NA",
        "c_imputed_water_level_prov": "NA"
    }

    logger.warning('[profile_empty_catchment] Catchment asset not found, profiling empty catchment.')
    return properties_dict


def profile_empty_reservoir():

    properties_dict = {
        "r_area_km2": "NA",
        "r_mean_depth_m": "NA",
        "r_maximum_depth_m": "NA",
        "r_maximum_depth_m_alt1": "NA",
        "r_maximum_depth_m_alt2": "NA",
        "r_volume_m3": "NA",
        "r_mean_temp_1": "NA",
        "r_mean_temp_2": "NA",
        "r_mean_temp_3": "NA",
        "r_mean_temp_4": "NA",
        "r_mean_temp_5": "NA",
        "r_mean_temp_6": "NA",
        "r_mean_temp_7": "NA",
        "r_mean_temp_8": "NA",
        "r_mean_temp_9": "NA",
        "r_mean_temp_10": "NA",
        "r_mean_temp_11": "NA",
        "r_mean_temp_12": "NA",
        "r_mghr_all_kwhperm2perday": "NA",
        "r_mghr_nov_mar_kwhperm2perday": "NA",
        "r_mghr_may_sept_kwhperm2perday": "NA",
        "r_mghr_all_kwhperm2perday_alt1": "NA",
        "r_mghr_nov_mar_kwhperm2perday_alt1": "NA",
        "r_mghr_may_sept_kwhperm2perday_alt1": "NA",
        "r_msoc_kgperm2": "NA",
        # Landcover
        "r_landcover_bysoil_0": "NA",
        "r_landcover_bysoil_1": "NA",
        "r_landcover_bysoil_2": "NA",
        "r_landcover_bysoil_3": "NA",
        "r_landcover_bysoil_4": "NA",
        "r_landcover_bysoil_5": "NA",
        "r_landcover_bysoil_6": "NA",
        "r_landcover_bysoil_7": "NA",
        "r_landcover_bysoil_8": "NA",
        "r_landcover_bysoil_9": "NA",
        "r_landcover_bysoil_10": "NA",
        "r_landcover_bysoil_11": "NA",
        "r_landcover_bysoil_12": "NA",
        "r_landcover_bysoil_13": "NA",
        "r_landcover_bysoil_14": "NA",
        "r_landcover_bysoil_15": "NA",
        "r_landcover_bysoil_16": "NA",
        "r_landcover_bysoil_17": "NA",
        "r_landcover_bysoil_18": "NA",
        "r_landcover_bysoil_19": "NA",
        "r_landcover_bysoil_20": "NA",
        "r_landcover_bysoil_21": "NA",
        "r_landcover_bysoil_22": "NA",
        "r_landcover_bysoil_23": "NA",
        "r_landcover_bysoil_24": "NA",
        "r_landcover_bysoil_25": "NA",
        "r_landcover_bysoil_26": "NA",
        "r_mean_annual_windspeed": "NA"
    }
    logger.warning('[profile_empty_reservoir] Reservoir asset not found, profiling empty reservoir.')
    return properties_dict


def profile_empty_nicatchment():

    properties_dict = {
        "n_population": "NA",
        "n_population_density": "NA"
    }

    logger.warning('[profile_empty_nicatchment] NI Catchment asset not found, profiling empty nicatchment.')
    return properties_dict


def profile_empty_river():

    properties_dict = {
        "ms_length": "NA"
    }

    logger.warning('[profile_empty_river] River asset not found, profiling empty river.')
    return properties_dict

# ==============================================================================
# Populated Profiles
# ==============================================================================


def profile_catchment(catchment_ftc):

    # Catchment area
    area_km2 = ee.Number(area(catchment_ftc)).format("%.3f")

    # Catchment slope, [%], DEM
    mean_slope_pc = ee.Number(mean_slope_perc(catchment_ftc)).format("%.0f")

    # Landcover, proportions, European Space Agency (2010)
    landcover_fracs = landcover(catchment_ftc).map(lambda value: ee.Number(value).format("%.3f"))

    landcover_0 = ee.List(landcover_fracs).get(0)
    landcover_1 = ee.List(landcover_fracs).get(1)
    landcover_2 = ee.List(landcover_fracs).get(2)
    landcover_3 = ee.List(landcover_fracs).get(3)
    landcover_4 = ee.List(landcover_fracs).get(4)
    landcover_5 = ee.List(landcover_fracs).get(5)
    landcover_6 = ee.List(landcover_fracs).get(6)
    landcover_7 = ee.List(landcover_fracs).get(7)
    landcover_8 = ee.List(landcover_fracs).get(8)

    # Mean annual Runoff, [mm yr-1], Fekete
    t_mar_mm = mean_annual_runoff_mm(catchment_ftc)
    mar_mm = ee.Algorithms.If(
        ee.Number(t_mar_mm).neq(-999),
        ee.Number(t_mar_mm).format("%.0f"),
        "ND"
    )

    # Mean annual precipitation, [mm yr-1], WorldClim 2.1
    map_mm = ee.Number(mean_annual_prec_mm(catchment_ftc)).format("%.0f")

    # Predominant biome, Dinerstein et al. (2017)
    biome = predominant_biome(catchment_ftc)

    # Mean soil organic carbon (0-30cm), [kg m-1], Soil Grids
    t_msoc_kgperm2 = mean_soil_org_ca(catchment_ftc)
    msoc_kgperm2 = ee.Algorithms.If(
        ee.Number(t_msoc_kgperm2).neq(-999),
        ee.Number(t_msoc_kgperm2).format("%.3f"),
        "ND"
    )

    # Predominant climate zone
    climate_zone = predominant_climate(catchment_ftc)

    # Evapotranspiration, terraclim (scaled by 0.1)
    mpet_mm = ee.Number(terraclim_annual_mean(2000, 2019, 'pet', 0.1, catchment_ftc)).format("%.0f")
    masm_mm = ee.Number(terraclim_monthly_mean(2000, 2019, 'soil', 0.1, catchment_ftc)).format("%.0f")

    # Alternative soil moisture
    masm_mm_alt1 = ee.Number(smap_monthly_mean(2016, 2021, 'smp', catchment_ftc)).multiply(1000).format("%.0f")

    # Population
    current_population, current_population_density = population(catchment_ftc)
    c_current_population = ee.Number(
        current_population
    ).format("%.0f")

    c_current_population_density = ee.Number(
        current_population_density
    ).format("%.2f")

    # Alt Mean annual runnoff (gldas)
    # mean_annual_runoff_mm_gldas(catchment_ftc)
    mar_mm_alt1 = "UD"

    # Alt Mean annual runnoff (terraclim)
    mar_mm_alt2 = ee.Number(terraclim_annual_mean(2000, 2019, 'ro', 1, catchment_ftc)).format("%.0f")

    # Olsen P
    mean_olsen = ee.Number(
        mean_olsen_kgperha(catchment_ftc)
    ).format("%.3f")

    # Soil Type
    soil_type_cat = soil_type(catchment_ftc)

    # Mean discharge
    mad_m3_peryr = ee.Algorithms.If(
        ee.Number(t_mar_mm).neq(-999),
        ee.Number(mean_annual_runoff_mm(catchment_ftc)).multiply(area(catchment_ftc)).multiply(1000),
        "ND"
    )

    mad_m3_pers = ee.Number(mad_m3_peryr).divide(31557600)

    # Estimated dam height
    catchFeat = catchment_ftc.first()

    water_level = ee.Number(catchFeat.get('t_water_level'))
    dam_height = ee.Number(catchFeat.get('t_dam_height'))
    turbine_efficiency = ee.Number(catchFeat.get('t_turbine_efficiency'))
    power_capacity = ee.Number(catchFeat.get('power_capacity'))
    plant_depth = ee.Number(catchFeat.get('t_plant_depth'))

    #print("[DEBUG] t_water_level", water_level.getInfo())
    #print("[DEBUG] t_dam_height", dam_height.getInfo())
    #print("[DEBUG] t_turbine_efficiency", turbine_efficiency.getInfo())
    #print("[DEBUG] power_capacity", power_capacity.getInfo())
    #print("[DEBUG] t_plant_depth", plant_depth.getInfo())

    #print("[DEBUG] denominator", denominator.getInfo())
    #print("[DEBUG] calc_dam_height", calc_dam_height.getInfo())

    imputed_dam_height = ee.Algorithms.If(
        dam_height.eq(-999),
        impute_dam_height(power_capacity, turbine_efficiency, plant_depth, mad_m3_pers),
        dam_height
    )

    #print("[DEBUG] imputed_dam_height", imputed_dam_height.getInfo())

    # Impute water level
    imputed_water_level = ee.Number(ee.Algorithms.If(
        water_level.eq(-999),
        imputed_dam_height,
        water_level
    )).format("%.0f")

    # print("[DEBUG] imputed_water_level", imputed_water_level.getInfo())

    # Imputed water level provence
    # 0 - User input water level
    # 1 - User input dam height
    # 2 - Dam height estimated from power capacity (known turbine efficiency)
    # 3 - Dam height estimated from power capacity (unknown turbine efficiency)

    turbine_efficiency_prov = catchFeat.get('turbine_efficiency_prov')

    imputed_dam_height_prov = ee.Algorithms.If(
        dam_height.eq(-999),
        ee.Number(2).add(turbine_efficiency_prov),
        1
    )

    # Impute water level
    imputed_water_level_prov = ee.Algorithms.If(
        water_level.eq(-999),
        imputed_dam_height_prov,
        0
    )

    c_imputed_water_level_prov = imputed_water_level_prov
    c_imputed_water_level = imputed_water_level

    # Set parameters

    updated_catchment_ftc = catchment_ftc.map(lambda feat: feat.set({
        "c_area_km2": area_km2,
        "c_mean_slope_pc": mean_slope_pc,
        # Landcover
        "c_landcover_0": landcover_0,
        "c_landcover_1": landcover_1,
        "c_landcover_2": landcover_2,
        "c_landcover_3": landcover_3,
        "c_landcover_4": landcover_4,
        "c_landcover_5": landcover_5,
        "c_landcover_6": landcover_6,
        "c_landcover_7": landcover_7,
        "c_landcover_8": landcover_8,
        "c_mar_mm": mar_mm,
        "c_map_mm": map_mm,
        "c_biome": biome,
        "c_msoc_kgperm": msoc_kgperm2,
        "c_masm_mm": masm_mm,  # Slow
        "c_masm_mm_alt1": masm_mm_alt1,
        "c_climate_zone": climate_zone,
        "c_mpet_mm": mpet_mm,
        "c_population": c_current_population,
        "c_population_density": c_current_population_density,
        "c_mar_mm_alt1": mar_mm_alt1,  # Very Slow
        "c_mar_mm_alt2": mar_mm_alt2,
        "c_mean_olsen": mean_olsen,
        "c_soil_type": soil_type_cat,
        "r_imputed_water_level": c_imputed_water_level,
        "r_imputed_water_level_prov": c_imputed_water_level_prov
    }))

    return ee.FeatureCollection(updated_catchment_ftc)


def profile_nicatchment(nicatchment_ftc):

    # Population
    current_population, current_population_density = population(nicatchment_ftc)

    c_current_population = ee.Number(
        current_population
    ).format("%.0f")

    c_current_population_density = ee.Number(
        current_population_density
    ).format("%.2f")

    updated_nicatchment_ftc = (nicatchment_ftc.map(lambda feat: feat.set({
        "n_population": c_current_population,
        "n_population_density": c_current_population_density
    })))

    return ee.FeatureCollection(updated_nicatchment_ftc)


def river_length(river_ftc):

    def set_river_length(rfeat):
        calculated_length = ee.Number(rfeat.geometry().length()).divide(1000)
        rfeat = rfeat.set('ee_length_km', calculated_length)
        return rfeat

    inundated_river_ftc = river_ftc.map(set_river_length)

    inundated_river_length = (ee.Number(
        inundated_river_ftc.aggregate_array('ee_length_km')
        .reduce(ee.Reducer.sum())
    )
        .multiply(100)
        .round()
        .divide(100))

    return inundated_river_length


def profile_river(river_ftc):

    length = ee.Number(river_length(river_ftc)).format("%.3f")

    updated_river_ftc = (river_ftc.map(lambda feat: feat.set({
        "ms_length": length
    })))

    return ee.FeatureCollection(updated_river_ftc)


def profile_reservoir(reservoir_ftc):

    # Reservoir Area
    area_km2 = ee.Number(area(reservoir_ftc)).format("%.3f")
    area_m = ee.Number(km2_to_m2(area(reservoir_ftc))).format("%.3f")

    # Reservoir mean depth
    mean_depth_m = ee.Number(mean_depth(reservoir_ftc)).format("%.1f")

    # Reservoir maximum depth
    maximum_depth_m = ee.Number(maximum_depth(reservoir_ftc)).format("%.0f")

    maximum_depth_m_alt1 = ee.Number(maximum_depth_alt1(reservoir_ftc)).format("%.0f")
    maximum_depth_m_alt2 = ee.Number(maximum_depth_alt2(reservoir_ftc)).format("%.0f")

    # Reservoir volume
    volume_m3 = ee.Number(reservoir_volume(km2_to_m2(area(reservoir_ftc)), mean_depth(reservoir_ftc))).format("%.3f")

    # Mean monthly temperatures
    temperature_profile_c = mean_monthly_temps(reservoir_ftc)

    t_mean_temp_1 = ee.List(temperature_profile_c).get(0)
    t_mean_temp_2 = ee.List(temperature_profile_c).get(1)
    t_mean_temp_3 = ee.List(temperature_profile_c).get(2)
    t_mean_temp_4 = ee.List(temperature_profile_c).get(3)
    t_mean_temp_5 = ee.List(temperature_profile_c).get(4)
    t_mean_temp_6 = ee.List(temperature_profile_c).get(5)
    t_mean_temp_7 = ee.List(temperature_profile_c).get(6)
    t_mean_temp_8 = ee.List(temperature_profile_c).get(7)
    t_mean_temp_9 = ee.List(temperature_profile_c).get(8)
    t_mean_temp_10 = ee.List(temperature_profile_c).get(9)
    t_mean_temp_11 = ee.List(temperature_profile_c).get(10)
    t_mean_temp_12 = ee.List(temperature_profile_c).get(11)

    mean_temp_1 = ee.Algorithms.If(
        ee.Number(t_mean_temp_1).neq(-999),
        ee.Number(t_mean_temp_1).format("%.1f"),
        "ND"
    )
    mean_temp_2 = ee.Algorithms.If(
        ee.Number(t_mean_temp_2).neq(-999),
        ee.Number(t_mean_temp_2).format("%.1f"),
        "ND"
    )
    mean_temp_3 = ee.Algorithms.If(
        ee.Number(t_mean_temp_3).neq(-999),
        ee.Number(t_mean_temp_3).format("%.1f"),
        "ND"
    )
    mean_temp_4 = ee.Algorithms.If(
        ee.Number(t_mean_temp_4).neq(-999),
        ee.Number(t_mean_temp_4).format("%.1f"),
        "ND"
    )
    mean_temp_5 = ee.Algorithms.If(
        ee.Number(t_mean_temp_5).neq(-999),
        ee.Number(t_mean_temp_5).format("%.1f"),
        "ND"
    )
    mean_temp_6 = ee.Algorithms.If(
        ee.Number(t_mean_temp_6).neq(-999),
        ee.Number(t_mean_temp_6).format("%.1f"),
        "ND"
    )
    mean_temp_7 = ee.Algorithms.If(
        ee.Number(t_mean_temp_7).neq(-999),
        ee.Number(t_mean_temp_7).format("%.1f"),
        "ND"
    )
    mean_temp_8 = ee.Algorithms.If(
        ee.Number(t_mean_temp_8).neq(-999),
        ee.Number(t_mean_temp_8).format("%.1f"),
        "ND"
    )
    mean_temp_9 = ee.Algorithms.If(
        ee.Number(t_mean_temp_9).neq(-999),
        ee.Number(t_mean_temp_9).format("%.1f"),
        "ND"
    )
    mean_temp_10 = ee.Algorithms.If(
        ee.Number(t_mean_temp_10).neq(-999),
        ee.Number(t_mean_temp_10).format("%.1f"),
        "ND"
    )
    mean_temp_11 = ee.Algorithms.If(
        ee.Number(t_mean_temp_11).neq(-999),
        ee.Number(t_mean_temp_11).format("%.1f"),
        "ND"
    )
    mean_temp_12 = ee.Algorithms.If(
        ee.Number(t_mean_temp_12).neq(-999),
        ee.Number(t_mean_temp_12).format("%.1f"),
        "ND"
    )

    # Mean annual global horizontal irradiance (NASA) 2005
    maghr_kwhperm2perday = mghr(reservoir_ftc)
    mghr_all_kwhperm2perday = ee.Number(maghr_kwhperm2perday[0]).format("%.3f")
    mghr_nov_mar_kwhperm2perday = ee.Number(maghr_kwhperm2perday[1]).format("%.3f")
    mghr_may_sept_kwhperm2perday = ee.Number(maghr_kwhperm2perday[2]).format("%.3f")

    # Mean annual global horizontal irradiance (terraclim)
    #  TODO terraclim_mghr underdevelopment (see heet_params_draft)
    # Example use: terraclim_mghr(2000, 2019, reservoir_ftc)
    maghr_kwhperm2perday_alt1 = "UD"

    mghr_all_kwhperm2perday_alt1 = "UD"
    mghr_nov_mar_kwhperm2perday_alt1 = "UD"
    mghr_may_sept_kwhperm2perday_alt1 = "UD"

    # Mean soil organic carbon (0-30cm), [kg m-1], Soil Grids
    msoc_kgperm2 = ee.Number(mean_soil_org_ca(reservoir_ftc)).format("%.3f")

    # Landcover (stratification by soil type needed)
    landcover_bysoil_fracs = landcover_bysoil(reservoir_ftc).map(lambda value: ee.Number(value).format("%.3f"))

    landcover_bysoil_0 = ee.List(landcover_bysoil_fracs).get(0)
    landcover_bysoil_1 = ee.List(landcover_bysoil_fracs).get(1)
    landcover_bysoil_2 = ee.List(landcover_bysoil_fracs).get(2)
    landcover_bysoil_3 = ee.List(landcover_bysoil_fracs).get(3)
    landcover_bysoil_4 = ee.List(landcover_bysoil_fracs).get(4)
    landcover_bysoil_5 = ee.List(landcover_bysoil_fracs).get(5)
    landcover_bysoil_6 = ee.List(landcover_bysoil_fracs).get(6)
    landcover_bysoil_7 = ee.List(landcover_bysoil_fracs).get(7)
    landcover_bysoil_8 = ee.List(landcover_bysoil_fracs).get(8)
    landcover_bysoil_9 = ee.List(landcover_bysoil_fracs).get(9)
    landcover_bysoil_10 = ee.List(landcover_bysoil_fracs).get(10)
    landcover_bysoil_11 = ee.List(landcover_bysoil_fracs).get(11)
    landcover_bysoil_12 = ee.List(landcover_bysoil_fracs).get(12)
    landcover_bysoil_13 = ee.List(landcover_bysoil_fracs).get(13)
    landcover_bysoil_14 = ee.List(landcover_bysoil_fracs).get(14)
    landcover_bysoil_15 = ee.List(landcover_bysoil_fracs).get(15)
    landcover_bysoil_16 = ee.List(landcover_bysoil_fracs).get(16)
    landcover_bysoil_17 = ee.List(landcover_bysoil_fracs).get(17)
    landcover_bysoil_18 = ee.List(landcover_bysoil_fracs).get(18)
    landcover_bysoil_19 = ee.List(landcover_bysoil_fracs).get(19)
    landcover_bysoil_20 = ee.List(landcover_bysoil_fracs).get(20)
    landcover_bysoil_21 = ee.List(landcover_bysoil_fracs).get(21)
    landcover_bysoil_22 = ee.List(landcover_bysoil_fracs).get(22)
    landcover_bysoil_23 = ee.List(landcover_bysoil_fracs).get(23)
    landcover_bysoil_24 = ee.List(landcover_bysoil_fracs).get(24)
    landcover_bysoil_25 = ee.List(landcover_bysoil_fracs).get(25)
    landcover_bysoil_26 = ee.List(landcover_bysoil_fracs).get(26)

    # Mean annual windspeed
    t_mean_annual_windpseed_mpers = terraclim_monthly_mean(2000, 2019, 'vs', 0.01, reservoir_ftc)

    mean_annual_windpseed_mpers = ee.Algorithms.If(
        ee.Number(t_mean_annual_windpseed_mpers).neq(-999),
        ee.Number(t_mean_annual_windpseed_mpers).format("%.2f"),
        "ND"
    )

    if debug_mode == True:
        print("[profile_reservoir] t_mean_annual_windpseed_mpers", t_mean_annual_windpseed_mpers.getInfo())

    updated_reservoir_ftc = (reservoir_ftc.map(lambda feat: feat.set({
        "r_area_km2": area_km2,
        "r_mean_depth_m": mean_depth_m,
        "r_maximum_depth_m": maximum_depth_m,
        "r_maximum_depth_m_alt1": maximum_depth_m_alt1,
        "r_maximum_depth_m_alt2": maximum_depth_m_alt2,
        "r_volume_m3": volume_m3,
        "r_mean_temp_1": mean_temp_1,
        "r_mean_temp_2": mean_temp_2,
        "r_mean_temp_3": mean_temp_3,
        "r_mean_temp_4": mean_temp_4,
        "r_mean_temp_5": mean_temp_5,
        "r_mean_temp_6": mean_temp_6,
        "r_mean_temp_7": mean_temp_7,
        "r_mean_temp_8": mean_temp_8,
        "r_mean_temp_9": mean_temp_9,
        "r_mean_temp_10": mean_temp_10,
        "r_mean_temp_11": mean_temp_11,
        "r_mean_temp_12": mean_temp_12,
        "r_mghr_all_kwhperm2perday": mghr_all_kwhperm2perday,
        "r_mghr_nov_mar_kwhperm2perday": mghr_nov_mar_kwhperm2perday,
        "r_mghr_may_sept_kwhperm2perday": mghr_may_sept_kwhperm2perday,
        "r_mghr_all_kwhperm2perday_alt1": mghr_all_kwhperm2perday_alt1,
        "r_mghr_nov_mar_kwhperm2perday_alt1": mghr_nov_mar_kwhperm2perday_alt1,
        "r_mghr_may_sept_kwhperm2perday_alt1": mghr_may_sept_kwhperm2perday_alt1,
        "r_msoc_kgperm2": msoc_kgperm2,
        # Landcover
        "r_landcover_bysoil_0": landcover_bysoil_0,
        "r_landcover_bysoil_1": landcover_bysoil_1,
        "r_landcover_bysoil_2": landcover_bysoil_2,
        "r_landcover_bysoil_3": landcover_bysoil_3,
        "r_landcover_bysoil_4": landcover_bysoil_4,
        "r_landcover_bysoil_5": landcover_bysoil_5,
        "r_landcover_bysoil_6": landcover_bysoil_6,
        "r_landcover_bysoil_7": landcover_bysoil_7,
        "r_landcover_bysoil_8": landcover_bysoil_8,
        "r_landcover_bysoil_9": landcover_bysoil_9,
        "r_landcover_bysoil_10": landcover_bysoil_10,
        "r_landcover_bysoil_11": landcover_bysoil_11,
        "r_landcover_bysoil_12": landcover_bysoil_12,
        "r_landcover_bysoil_13": landcover_bysoil_13,
        "r_landcover_bysoil_14": landcover_bysoil_14,
        "r_landcover_bysoil_15": landcover_bysoil_15,
        "r_landcover_bysoil_16": landcover_bysoil_16,
        "r_landcover_bysoil_17": landcover_bysoil_17,
        "r_landcover_bysoil_18": landcover_bysoil_18,
        "r_landcover_bysoil_19": landcover_bysoil_19,
        "r_landcover_bysoil_20": landcover_bysoil_20,
        "r_landcover_bysoil_21": landcover_bysoil_21,
        "r_landcover_bysoil_22": landcover_bysoil_22,
        "r_landcover_bysoil_23": landcover_bysoil_23,
        "r_landcover_bysoil_24": landcover_bysoil_24,
        "r_landcover_bysoil_25": landcover_bysoil_25,
        "r_landcover_bysoil_26": landcover_bysoil_26,
        "r_mean_annual_windspeed": mean_annual_windpseed_mpers
    })))

    return ee.FeatureCollection(updated_reservoir_ftc)


def batch_delete_shapes(c_dam_ids, output_type):

    file_prefix = heet_export.export_job_specs[output_type]['fileprefix']

    for c_dam_id in c_dam_ids:

        c_dam_id_str = str(c_dam_id)

        targetAssetName = cfg.ps_heet_folder + "/" + file_prefix + c_dam_id_str

        try:
            ee.data.deleteAsset(targetAssetName)
        except Exception as error:
            msg = f"Problem deleting intermediate output {targetAssetName}"
            logger.exception(f'{msg}')
            continue


def batch_profile_reservoirs(c_dam_ids):

    for c_dam_id in c_dam_ids:

        c_dam_id_str = str(c_dam_id)

        reservoirAssetName = cfg.ps_heet_folder + "/" + "r_" + c_dam_id_str
        reservoir_ftc = ee.FeatureCollection(reservoirAssetName)

        try:
            updated_reservoir_ftc = profile_reservoir(reservoir_ftc)
            heet_export.export_ftc(updated_reservoir_ftc, c_dam_id_str, "reservoir_vector_params")
        except Exception as error:
            msg = "Problem updating Reservoir vector with calculated parameters"
            logger.exception(f'{msg}')
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue


def batch_profile_catchments(c_dam_ids):

    for c_dam_id in c_dam_ids:

        c_dam_id_str = str(c_dam_id)

        catchmentAssetName = cfg.ps_heet_folder + "/" + "c_" + c_dam_id_str
        catchment_ftc = ee.FeatureCollection(catchmentAssetName)

        try:
            updated_catchment_ftc = profile_catchment(catchment_ftc)
            heet_export.export_ftc(updated_catchment_ftc, c_dam_id_str, "catchment_vector_params")
        except Exception as error:
            msg = "Problem updating Catchment vector with calculated parameters"
            logger.exception(f'{msg}')
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue


def batch_profile_rivers(c_dam_ids):

    for c_dam_id in c_dam_ids:

        c_dam_id_str = str(c_dam_id)

        riverAssetName = cfg.ps_heet_folder + "/" + "ms_" + c_dam_id_str
        river_ftc = ee.FeatureCollection(riverAssetName)

        try:
            updated_river_ftc = profile_river(river_ftc)
            heet_export.export_ftc(ee.FeatureCollection(updated_river_ftc), c_dam_id_str, "main_river_vector_params")
        except Exception as error:
            msg = "Problem updating River vector with calculated parameters"
            logger.exception(f'{msg}')
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue


def batch_profile_nicatchments(c_dam_ids):

    for c_dam_id in c_dam_ids:

        c_dam_id_str = str(c_dam_id)

        nicatchmentAssetName = cfg.ps_heet_folder + "/" + "n_" + c_dam_id_str
        nicatchment_ftc = ee.FeatureCollection(nicatchmentAssetName)

        try:
            updated_nicatchment_ftc = profile_nicatchment(nicatchment_ftc)
            heet_export.export_ftc(updated_nicatchment_ftc, c_dam_id_str, "ni_catchment_vector_params")
        except Exception as error:
            msg = "Problem updating NI Catchment vector with calculated parameters"
            logger.exception(f'{msg}')
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue


if __name__ == "__main__":

    # Development
    print("Development...")

    # reservoir_ftc = ee.FeatureCollection("users/KamillaHarding/XHEET/tmp/r_XXXX")
    #reservoir_geom = reservoir_ftc.geometry()
    #reservoir_properties = profile_reservoir(reservoir_ftc)
    # print(reservoir_properties.getInfo())
