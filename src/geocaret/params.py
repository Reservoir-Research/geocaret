debug_mode = False

import ee
import math
import logging

# Import asset locations from config
import sys
sys.path.append("..")
import geocaret.lib as lib

import_exceptions = (ModuleNotFoundError, ee.ee_exception.EEException)
try:
    from geocaret import config as cfg
    from geocaret import data as dta
    from geocaret import export
    from geocaret import monitor as mtr
    from geocaret import log as lg

except import_exceptions:
    if not ee.data._credentials:
        ee.Initialize()

    import geocaret.config as cfg
    import geocaret.data as dta
    import geocaret.export
    import geocaret.monitor as mtr
    import geocaret.log as lg

if debug_mode == True:
    mtr.existing_dams = []
    mtr.buffer_method = []
# ==============================================================================
#  Set up logger
# ==============================================================================

# Gets or creates a logger
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.DEBUG)

# define file handler and set formatter
file_handler = logging.FileHandler(lg.log_file_name)
formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)


# ==============================================================================
# Buffer Zone Delineation
# ==============================================================================
def delineate_buffer_zone(res_ftc):

    res_geometry = res_ftc.geometry()

    res_area_m = res_geometry.area(1)
    buffer_distance = ee.Number(
        res_area_m.divide(ee.Number(3.14159265359)).pow(0.5)
    ).divide(2)

    def add_buffer(feat):
        return feat.buffer(buffer_distance)

    res_buffered_ftc = res_ftc.map(add_buffer)
    buffer_zone_ft = ee.Feature(
        res_buffered_ftc.geometry().difference(res_ftc.geometry(), 1)
    )
    buffer_zone_ftc = ee.FeatureCollection(buffer_zone_ft)

    return buffer_zone_ftc


# ==============================================================================
# Catchment, Reservoir, River Parameters
# ==============================================================================


# Catchment/reservoir area (km)
def area(land_ftc):
    land_geom = land_ftc.geometry()
    return land_geom.area(1).divide(1000 * 1000)


# Mean slope (%)
def degrees_to_perc_slope(mean_slope_degrees_value):
    return (
        ee.Number(mean_slope_degrees_value).multiply(math.pi / 180).tan().multiply(100)
    )


def mean_slope_degrees(catchment_ftc):

    catchment_geom = catchment_ftc.geometry()

    if cfg.paramHydroDEM == True:
        DEM = ee.Image(lib.get_public_asset(asset_name="hydrosheds") + cfg.hydrodataset + "CONDEM").rename(
            ["elevation"]
        )
    else:
        DEM = ee.Image(lib.get_public_asset("nasa_srtm"))

    # Expected SCALE = 30

    elevationDEM = ee.Image(DEM).select("elevation")
    slopeDEM = ee.Terrain.slope(elevationDEM)

    projection = ee.Image(slopeDEM).projection()
    SCALE = projection.nominalScale()

    mean_slope_degrees_value = slopeDEM.reduceRegion(
        **{
            "reducer": ee.Reducer.mean(),
            "geometry": catchment_geom,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("slope")

    return mean_slope_degrees_value


def mean_slope(catchment_ftc):

    mean_slope_degrees_value = mean_slope_degrees(catchment_ftc)

    # Handle null values
    mean_slope_perc_value = ee.Algorithms.If(
        ee.Algorithms.IsEqual(mean_slope_degrees_value, None),
        # Else null
        mean_slope_degrees_value,
        degrees_to_perc_slope(mean_slope_degrees_value),
    )

    return mean_slope_perc_value


def mean_soil_oc_stocks(land_ftc):

    SOIL_CARBON = ee.Image(lib.get_public_asset("soilgrids250m_ocs"))
    # Expected SCALE = 250

    projection = ee.Image(SOIL_CARBON).projection()
    SCALE = projection.nominalScale()

    land_geom = land_ftc.geometry()

    mean_soil_carbon_hgpm2 = ee.Number(
        SOIL_CARBON.reduceRegion(
            **{
                "reducer": ee.Reducer.mean(),
                "geometry": land_geom,
                "scale": SCALE,
                "maxPixels": 2e11,
            }
        ).get("ocs_0-30cm_mean")
    )

    # Handle null values
    mean_soil_carbon_kgpm2_value = ee.Algorithms.If(
        ee.Algorithms.IsEqual(mean_soil_carbon_hgpm2, None),
        # Else null
        mean_soil_carbon_hgpm2,
        mean_soil_carbon_hgpm2.multiply(0.1),
    )

    return mean_soil_carbon_kgpm2_value


def mean_soil_oc_content(target_ftc):

    soil_grids_soc = ee.Image(lib.get_public_asset("soilgrids250m_soc"))
    soil_grids_psoc = soil_grids_soc.expression(
        "SOC_GPERKG = (SOC_0to5CM_MEAN * 0.1 * 5 + SOC_5to15CM_MEAN * 0.1 * 10 + SOC_15to30CM_MEAN * 0.1 * 15) / 30",
        {
            "SOC_0to5CM_MEAN": soil_grids_soc.select("soc_0-5cm_mean"),
            "SOC_5to15CM_MEAN": soil_grids_soc.select("soc_5-15cm_mean"),
            "SOC_15to30CM_MEAN": soil_grids_soc.select("soc_15-30cm_mean"),
        },
    )

    target_geom = target_ftc.geometry()

    projection = ee.Image(soil_grids_psoc).projection()
    SCALE = projection.nominalScale()

    mean_soc_gperkg_value = soil_grids_psoc.reduceRegion(
        **{
            "reducer": ee.Reducer.mean(),
            "geometry": target_geom,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("SOC_GPERKG")

    # Explicit null handling not needed

    return mean_soc_gperkg_value


def mean_soil_nitrogen_content(target_ftc):

    soil_grids_nitrogen = ee.Image(lib.get_public_asset("soilgrids250m_n"))

    soil_grids_nitrogen = soil_grids_nitrogen.expression(
        "N_GPERKG = (N_0to5CM_MEAN * 0.01 * 5 + N_5to15CM_MEAN * 0.01 * 10 + N_15to30CM_MEAN * 0.01 * 15) / 30",
        {
            "N_0to5CM_MEAN": soil_grids_nitrogen.select("nitrogen_0-5cm_mean"),
            "N_5to15CM_MEAN": soil_grids_nitrogen.select("nitrogen_5-15cm_mean"),
            "N_15to30CM_MEAN": soil_grids_nitrogen.select("nitrogen_15-30cm_mean"),
        },
    )

    target_geom = target_ftc.geometry()

    projection = ee.Image(soil_grids_nitrogen).projection()
    SCALE = projection.nominalScale()

    mean_n_gperkg_value = soil_grids_nitrogen.reduceRegion(
        **{
            "reducer": ee.Reducer.mean(),
            "geometry": target_geom,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("N_GPERKG")

    # Explicit null handling not needed
    return mean_n_gperkg_value


def mean_soil_bdod(target_ftc):

    soil_grids_bdod = ee.Image(lib.get_public_asset("soilgrids250m_bdod"))
    soil_grids_bdod = soil_grids_bdod.expression(
        "BDOD_KGPERDM3 = (BDOD_0to5CM_MEAN * 0.01 * 5 + BDOD_5to15CM_MEAN * 0.01 * 10 + BDOD_15to30CM_MEAN * 0.01 * 15) / 30",
        {
            "BDOD_0to5CM_MEAN": soil_grids_bdod.select("bdod_0-5cm_mean"),
            "BDOD_5to15CM_MEAN": soil_grids_bdod.select("bdod_5-15cm_mean"),
            "BDOD_15to30CM_MEAN": soil_grids_bdod.select("bdod_15-30cm_mean"),
        },
    )

    target_geom = target_ftc.geometry()

    projection = ee.Image(soil_grids_bdod).projection()
    SCALE = projection.nominalScale()

    mean_bdod_kgperdm3_value = soil_grids_bdod.reduceRegion(
        **{
            "reducer": ee.Reducer.mean(),
            "geometry": target_geom,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("BDOD_KGPERDM3")

    # Explicit null handling not needed
    return mean_bdod_kgperdm3_value


def global_strata_weighted_mol_c():
    soil_grids_soc = ee.Image(lib.get_public_asset("soilgrids250m_soc"))
    # 0.00833257 = 1/120.011
    sum_weighted_mol_c_kg = soil_grids_soc.expression(
        "WMOLCKG = (SOC_0to5CM_MEAN * 0.00833257 * 5 + SOC_5to15CM_MEAN * 0.00833257 * 10 + SOC_15to30CM_MEAN * 0.00833257 * 15 + SOC_30to60CM_MEAN * 0.00833257 * 30 + SOC_60to100CM_MEAN * 0.00833257 * 40) / 100",
        {
            "SOC_0to5CM_MEAN": soil_grids_soc.select("soc_0-5cm_mean"),
            "SOC_5to15CM_MEAN": soil_grids_soc.select("soc_5-15cm_mean"),
            "SOC_15to30CM_MEAN": soil_grids_soc.select("soc_15-30cm_mean"),
            "SOC_30to60CM_MEAN": soil_grids_soc.select("soc_30-60cm_mean"),
            "SOC_60to100CM_MEAN": soil_grids_soc.select("soc_60-100cm_mean"),
        },
    )
    return sum_weighted_mol_c_kg


def mean_strata_weighted_mol_c(target_ftc):
    sum_weighted_mol_c_kg = global_strata_weighted_mol_c()
    target_geom = target_ftc.geometry()

    projection = ee.Image(sum_weighted_mol_c_kg).projection()
    SCALE = projection.nominalScale()

    mean_strata_weighted_mol_c_value = sum_weighted_mol_c_kg.reduceRegion(
        **{
            "reducer": ee.Reducer.mean(),
            "geometry": target_geom,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("WMOLCKG")

    # Explicit null handling not needed
    return mean_strata_weighted_mol_c_value


def global_strata_weighted_mol_n():
    soil_grids_nitrogen = ee.Image(lib.get_public_asset("soilgrids250m_n"))
    # 0.000713944 = 1/1400.67
    sum_weighted_mol_n_kg = soil_grids_nitrogen.expression(
        "WMOLNKG = (N_0to5CM_MEAN * 0.000713944 * 5 + N_5to15CM_MEAN * 0.000713944 * 10 + N_15to30CM_MEAN * 0.000713944 * 15 + N_30to60CM_MEAN * 0.000713944 * 30 + N_60to100CM_MEAN * 0.000713944 * 40) / 100",
        {
            "N_0to5CM_MEAN": soil_grids_nitrogen.select("nitrogen_0-5cm_mean"),
            "N_5to15CM_MEAN": soil_grids_nitrogen.select("nitrogen_5-15cm_mean"),
            "N_15to30CM_MEAN": soil_grids_nitrogen.select("nitrogen_15-30cm_mean"),
            "N_30to60CM_MEAN": soil_grids_nitrogen.select("nitrogen_30-60cm_mean"),
            "N_60to100CM_MEAN": soil_grids_nitrogen.select("nitrogen_60-100cm_mean"),
        },
    )
    return sum_weighted_mol_n_kg


def mean_strata_weighted_mol_n(target_ftc):
    sum_weighted_mol_n_kg = global_strata_weighted_mol_n()
    target_geom = target_ftc.geometry()

    projection = ee.Image(sum_weighted_mol_n_kg).projection()
    SCALE = projection.nominalScale()

    mean_strata_weighted_mol_n_value = sum_weighted_mol_n_kg.reduceRegion(
        **{
            "reducer": ee.Reducer.mean(),
            "geometry": target_geom,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("WMOLNKG")

    # Explicit null handling not needed
    return mean_strata_weighted_mol_n_value


def total_doc_export(target_ftc):

    sum_weighted_mol_n_kg = global_strata_weighted_mol_n()
    sum_weighted_mol_c_kg = global_strata_weighted_mol_c()

    sum_weighted_mol_cn_kg = sum_weighted_mol_c_kg.addBands(sum_weighted_mol_n_kg)

    molar_cn_ratio = sum_weighted_mol_cn_kg.expression(
        "CNRATIO = MOLC / MOLN",
        {
            "MOLC": sum_weighted_mol_cn_kg.select("WMOLCKG"),
            "MOLN": sum_weighted_mol_cn_kg.select("WMOLNKG"),
        },
    )

    kg_doc_ha_yr = molar_cn_ratio.expression(
        "KGDOCHAYR = 4.8634 * CN - 60.873",
        {"CN": molar_cn_ratio.select("CNRATIO")},
    )

    target_geom = target_ftc.geometry()
    target_geom_area_ha = target_geom.area(1).divide(10000)

    projection = ee.Image(kg_doc_ha_yr).projection()
    SCALE = projection.nominalScale()

    mean_kg_doc_ha_yr = kg_doc_ha_yr.reduceRegion(
        **{
            "reducer": ee.Reducer.mean(),
            "geometry": target_geom,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("KGDOCHAYR")

    total_kg_doc_yr_value = ee.Algorithms.If(
        ee.Algorithms.IsEqual(mean_kg_doc_ha_yr, None),
        # Else null
        mean_kg_doc_ha_yr,
        ee.Number(mean_kg_doc_ha_yr).multiply(target_geom_area_ha),
    )
    return total_kg_doc_yr_value


def landcover(land_ftc, landcover_analysis_file_str):

    if debug_mode == True:
        print("[landcover] landcover", landcover_analysis_file_str)

    LANDCOVER_ESA = ee.Image(landcover_analysis_file_str)

    if debug_mode == True:
        print("[landcover object] landcover", LANDCOVER_ESA.getInfo())

    # Expected SCALE = 300
    projection = ee.Image(LANDCOVER_ESA).projection()
    SCALE = projection.nominalScale()

    LANDCOVER_IHA = LANDCOVER_ESA.remap(
        # ESA CODES
        [
            0,
            10,
            20,
            100,
            110,
            120,
            121,
            122,
            130,
            140,
            150,
            152,
            153,
            151,
            30,
            40,
            11,
            12,
            50,
            60,
            61,
            62,
            70,
            71,
            72,
            80,
            81,
            82,
            90,
            160,
            170,
            180,
            190,
            200,
            201,
            202,
            210,
            220,
        ],
        # IHA CODES
        [
            0,
            1,
            1,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            4,
            4,
            4,
            5,
            6,
            6,
            6,
            7,
            8,
        ],
    ).select(["remapped"], ["land_use"])

    land_geom = land_ftc.geometry()

    ihaCategories = ee.Dictionary(
        {
            "0": "No Data",
            "1": "Croplands",
            "2": "Grassland/Shrubland",
            "3": "Forest",
            "4": "Wetlands",
            "5": "Settlements",
            "6": "Bare Areas",
            "7": "Water Bodies",
            "8": "Permanent snow and ice",
        }
    )

    frequency = LANDCOVER_IHA.reduceRegion(
        **{
            "reducer": ee.Reducer.frequencyHistogram().unweighted(),
            "geometry": land_geom,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    )

    if debug_mode == True:
        print("[DEBUG] Frequency", frequency.getInfo())

    total_count = (ee.Dictionary(frequency.get("land_use")).toArray().toList()).reduce(
        ee.Reducer.sum()
    )

    fractions = (
        ee.Dictionary(frequency.get("land_use"))
        .toArray()
        .toList()
        .map(lambda v: ee.Number(v).divide(total_count))
    )

    group_count = ihaCategories.keys().length()
    codes = ee.Dictionary(frequency.get("land_use")).keys()

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

    # Explicit null handling not needed
    return populated_fractions_list


def soil_type_gres(target_ftc):

    # >=40 kg/m2; Organic
    #  <40 kg/m2; Mineral
    target_geom = target_ftc.geometry()

    # Soil Type
    SOIL_CARBON_CAT = (
        ee.Image(lib.get_public_asset("soilgrids250m_ocs")).multiply(0.1).gte(40)
    )

    # Expected SCALE = 1000
    projection = ee.Image(SOIL_CARBON_CAT).projection()
    SCALE = projection.nominalScale()

    stats = SOIL_CARBON_CAT.reduceRegion(
        **{
            "reducer": ee.Reducer.mode(),
            "geometry": target_geom,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    )

    stats = stats.map(
        lambda k, v: ee.Algorithms.If(
            ee.Algorithms.IsEqual(v, None), -999, stats.get(k)
        )
    )

    metric = ee.Number(stats.get("ocs_0-30cm_mean")).format("%.0f")

    codes = {"-999": "NODATA", "0": "MINERAL", "1": "ORGANIC"}
    modal_soil_category = ee.Dictionary(codes).get(metric)

    # Explicit null handling not needed
    return modal_soil_category


def soc_percent(target_ftc=None):

    soil_grids_soc = ee.Image(lib.get_public_asset("soilgrids250m_soc"))
    soil_grids_psoc = soil_grids_soc.expression(
        "PSOC = (SOC_0to5CM_MEAN * 0.01 * 5 + SOC_5to15CM_MEAN * 0.01 * 10 + SOC_15to30CM_MEAN * 0.01 * 15) / 30",
        {
            "SOC_0to5CM_MEAN": soil_grids_soc.select("soc_0-5cm_mean"),
            "SOC_5to15CM_MEAN": soil_grids_soc.select("soc_5-15cm_mean"),
            "SOC_15to30CM_MEAN": soil_grids_soc.select("soc_15-30cm_mean"),
        },
    )

    if target_ftc is not None:

        target_geom = target_ftc.geometry()

        projection = ee.Image(soil_grids_psoc).projection()
        SCALE = projection.nominalScale()

        soc_percent_value = soil_grids_psoc.reduceRegion(
            **{
                "reducer": ee.Reducer.mean(),
                "geometry": target_geom,
                "scale": SCALE,
                "maxPixels": 2e11,
            }
        ).get("PSOC")

        # Explicit null handling not needed
        return soc_percent_value
    else:
        return soil_grids_psoc


def soil_type(target_ftc):

    target_geom = target_ftc.geometry()

    # IPCC definition of organic soils
    # > 12% organic carbon by weight in the 0-30cm soil horizon.
    # The soil grids data arefor 0-5cm, 5-15cm, and 15-30 cm;
    # to achieve a 0-30cm value we  need the data for each strata,
    # and then weight these by the depth before deriving the 0-30cm mean:

    # Soil organic carbon (dg/kg)
    SOIL_CARBON_CAT = soc_percent(target_ftc=None).gt(12)

    # Expected SCALE = 1000
    projection = ee.Image(SOIL_CARBON_CAT).projection()
    SCALE = projection.nominalScale()

    stats = SOIL_CARBON_CAT.reduceRegion(
        **{
            "reducer": ee.Reducer.mode(),
            "geometry": target_geom,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    )

    stats = stats.map(
        lambda k, v: ee.Algorithms.If(
            ee.Algorithms.IsEqual(v, None), -999, stats.get(k)
        )
    )

    metric = ee.Number(stats.get("PSOC")).format("%.0f")

    codes = {"-999": "NODATA", "0": "MINERAL", "1": "ORGANIC"}
    modal_soil_category = ee.Dictionary(codes).get(metric)

    # Explicit null handling not needed
    return modal_soil_category


def landcover_bysoil_buffer(res_ftc, landcover_analysis_file_str, c_dam_id):

    c_dam_id_str = str(c_dam_id)
    res_buffer_ftc = delineate_buffer_zone(res_ftc)

    # [5] Make catchment shape file (i) Find pixels
    msg = "Exporting buffer zone vector"

    try:
        logger.info(f"{msg} {c_dam_id_str}")
        if cfg.exportBufferVector == True:
            export.export_ftc(
                res_buffer_ftc, c_dam_id_str, "reservoir_buffer_zone"
            )

    except Exception as error:
        logger.exception(f"{msg} {c_dam_id_str}")

    # Explicit null handling not needed
    return landcover_bysoil(res_buffer_ftc, landcover_analysis_file_str)


def landcover_bysoil(land_ftc, landcover_analysis_file_str):

    # > 12%; Organic
    # <= 12%; Mineral

    # IPCC definition of organic soils
    # > 12% organic carbon by weight in the 0-30cm soil horizon.
    # The soil grids data arefor 0-5cm, 5-15cm, and 15-30 cm;
    # to achieve a 0-30cm value we  need the data for each strata,
    # and then weight these by the depth before deriving the 0-30cm mean:

    # Soil organic carbon (dg/kg)
    SOIL_CARBON_CAT = soc_percent(target_ftc=None).gt(12)

    LANDCOVER_ESA = ee.Image(landcover_analysis_file_str)

    # Expected SCALE = 300

    projection = ee.Image(LANDCOVER_ESA).projection()
    SCALE = projection.nominalScale()

    LANDCOVER_IHA = LANDCOVER_ESA.remap(
        # ESA CODES
        [
            0,
            10,
            20,
            100,
            110,
            120,
            121,
            122,
            130,
            140,
            150,
            152,
            153,
            151,
            30,
            40,
            11,
            12,
            50,
            60,
            61,
            62,
            70,
            71,
            72,
            80,
            81,
            82,
            90,
            160,
            170,
            180,
            190,
            200,
            201,
            202,
            210,
            220,
        ],
        # IHA CODES
        [
            0,
            1,
            1,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            4,
            4,
            4,
            5,
            6,
            6,
            6,
            7,
            8,
        ],
    ).select(["remapped"], ["land_use"])

    land_geom = land_ftc.geometry()

    ihaCategories = ee.Dictionary(
        {
            "0": "Mineral - No Data",
            "1": "Mineral - Croplands",
            "2": "Mineral - Grassland/Shrubland",
            "3": "Mineral - Forest",
            "4": "Mineral - Wetlands",
            "5": "Mineral - Settlements",
            "6": "Mineral - Bare Areas",
            "7": "Mineral - Water Bodies",
            "8": "Mineral - Permanent snow and ice",
            "9": "Organic- No Data",
            "10": "Organic - Croplands",
            "11": "Organic - Grassland/Shrubland",
            "12": "Organic - Forest",
            "13": "Organic - Wetlands",
            "14": "Organic - Settlements",
            "15": "Organic - Bare Areas",
            "16": "Organic - Water Bodies",
            "17": "Organic - Permanent snow and ice",
            "18": "No Data - No Data",
            "19": "No Data - Croplands",
            "20": "No Data - Grassland/Shrubland",
            "21": "No Data - Forest",
            "22": "No Data - Wetlands",
            "23": "No Data - Settlements",
            "24": "No Data - Bare Areas",
            "25": "No Data - Water Bodies",
            "26": "No Data - Permanent snow and ice",
        }
    )

    # Histogram
    frequency = (
        LANDCOVER_IHA.addBands(SOIL_CARBON_CAT)
        .reduceRegion(
            **{
                "reducer": ee.Reducer.frequencyHistogram().unweighted().group(0),
                "geometry": land_geom,
                "scale": SCALE,
                "maxPixels": 2e11,
            }
        )
        .get("groups")
    )

    total_count = (
        ee.List(frequency)
        .map(
            lambda d: ee.List(
                ee.Dictionary(ee.Dictionary(d).get("histogram"))
                .toArray()
                .toList()
                .map(lambda v: v)
            ).reduce(ee.Reducer.sum())
        )
        .reduce(ee.Reducer.sum())
    )

    fractions = (
        ee.List(frequency)
        .map(
            lambda d: ee.Dictionary(ee.Dictionary(d).get("histogram"))
            .toArray()
            .toList()
            .map(lambda v: ee.Number(v).divide(total_count))
        )
        .flatten()
    )

    group_count = ihaCategories.keys().length()

    key_to_int = {"0": 0, "1": 1, "null": 2}

    def generate_codes(d):
        group_no = ee.Number.int(ee.Dictionary(d).get("group"))
        code = ee.Number(
            ee.Dictionary(ee.Dictionary(d).get("histogram"))
            .keys()
            .map(
                lambda k: ee.Number(
                    group_no.add(
                        ee.Number(ee.Dictionary(key_to_int).get(k)).multiply(
                            group_count.divide(3)
                        )
                    )
                ).format("%.0f")
            )
        )
        return code

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
    # Explicit null handling not needed
    return populated_fractions_list


def mghr(catchment_ftc):

    catch_geom = catchment_ftc.geometry()

    GHI_NASA_low = ee.FeatureCollection(
        lib.get_private_asset("ghi_nasa_low")
    )

    mghr_all = (
        GHI_NASA_low.filterBounds(catch_geom)
        .reduceColumns(ee.Reducer.mean(), ["annual"])
        .get("mean")
    )

    mghr_nov_mar = ee.List(
        GHI_NASA_low.filterBounds(catch_geom)
        .reduceColumns(ee.Reducer.mean().repeat(5), ["nov", "dec", "jan", "feb", "mar"])
        .get("mean")
    ).reduce(ee.Reducer.mean())

    mghr_may_sept = ee.List(
        GHI_NASA_low.filterBounds(catch_geom)
        .reduceColumns(ee.Reducer.mean().repeat(5), ["may", "jun", "jul", "aug", "sep"])
        .get("mean")
    ).reduce(ee.Reducer.mean())

    if debug_mode == True:
        print("[DEBUG] [mghr] [mghr_all]", mghr_all.getInfo())
        print("[DEBUG] [mghr] [mghr_nov_mar]", mghr_nov_mar.getInfo())
        print("[DEBUG] [mghr] [mghr_may_sept]", mghr_may_sept.getInfo())

    # Explicit null handling not needed
    return (mghr_all, mghr_nov_mar, mghr_may_sept)


def twbda_annual_mean_pet(target_ftc):

    twbda_pet = ee.Image(lib.get_private_asset("Eo150_clim"))
    target_geom = target_ftc.geometry()

    projection = ee.Image(twbda_pet).projection()
    SCALE = projection.nominalScale()

    mean_annual_pet_value = twbda_pet.reduceRegion(
        **{
            "reducer": ee.Reducer.mean(),
            "geometry": target_geom,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("b1")

    if debug_mode == True:
        print(
            "[DEBUG] [twbda_annual_mean_pet] [twbda_annual_mean_pet]",
            mean_annual_pet_value.getInfo(),
        )

    # Explicit null handling not needed
    return mean_annual_pet_value


def terraclim_monthly_mean(start_yr, end_yr, target_var, scale_factor, target_ftc):

    target_years = ee.List.sequence(start_yr, end_yr)
    target_geom = target_ftc.geometry()

    # print("[DEBUG]\n [terraclim_monthly_mean]\n ", target_var.getInfo())
    # print("[DEBUG]\n [terraclim_monthly_mean]\n ", target_years.getInfo())

    TERRACLIM = ee.ImageCollection(
        lib.get_public_asset("idaho_terraclimate")).select([target_var])

    # Expected SCALE = 4638
    projection = ee.Image(TERRACLIM.first()).projection()
    SCALE = projection.nominalScale()

    # Calculation fails with null values using nominal scale
    # SCALE = 30

    def aggregate_months(year):

        date_start = ee.Date.fromYMD(year, 1, 1)
        date_end = date_start.advance(1, "year")

        year_img = (
            TERRACLIM.filterDate(date_start, date_end)
            .mean()
            .set({"year": year, "system:time_start": date_start})
        )
        return year_img

    # Convert monthly image collection to yearly
    metric_yearly_cimg = ee.ImageCollection(target_years.map(aggregate_months))

    # print("[DEBUG]\n [terraclim_annual_mean]\n ", metric_yearly_cimg.getInfo())

    # Get regional values
    def get_regional_value(img, first):

        stats = img.reduceRegion(
            **{
                "reducer": ee.Reducer.mean(),
                "geometry": target_geom,
                "scale": SCALE,
                "maxPixels": 2e11,
            }
        )

        # Map null values to -999
        stats = stats.map(
            lambda k, v: ee.Algorithms.If(
                ee.Algorithms.IsEqual(v, None), -999, stats.get(k)
            )
        )
        metric = stats.get(target_var)
        returnValue = ee.List(first).add(metric)

        return returnValue

    results = ee.List([])
    regional_metrics_yearly = metric_yearly_cimg.iterate(get_regional_value, results)

    if debug_mode == True:
        print(
            "[terraclim_monthly_mean] regional_metrics_yearly",
            regional_metrics_yearly.getInfo(),
        )

    mean_monthly_value = ee.Number(
        ee.List(regional_metrics_yearly)
        .filter(ee.Filter.neq("item", -999))
        .map(lambda v: ee.Number(v).multiply(scale_factor))
        .reduce("mean")
    )

    # Explicit null handling not needed
    return mean_monthly_value


def terraclim_annual_mean(start_yr, end_yr, target_var, scale_factor, target_ftc):

    target_years = ee.List.sequence(start_yr, end_yr)
    target_geom = target_ftc.geometry()

    # print("[DEBUG]\n [terraclim_annual_mean]\n ", target_var.getInfo())
    # print("[DEBUG]\n [terraclim_annual_mean]\n ", target_years.getInfo())

    TERRACLIM = ee.ImageCollection(
        lib.get_public_asset("idaho_terraclimate")).select([target_var])

    # Expected SCALE = 4638
    projection = ee.Image(TERRACLIM.first()).projection()
    SCALE = projection.nominalScale()

    # Calculation fails with null values using nominal scale
    # SCALE = 30

    def aggregate_months(year):

        date_start = ee.Date.fromYMD(year, 1, 1)
        date_end = date_start.advance(1, "year")

        year_img = (
            TERRACLIM.filterDate(date_start, date_end)
            .sum()
            .set({"year": year, "system:time_start": date_start})
        )
        return year_img

    # Convert monthly image collection to yearly
    metric_yearly_cimg = ee.ImageCollection(target_years.map(aggregate_months))

    # print("[DEBUG]\n [terraclim_annual_mean]\n ", metric_yearly_cimg.getInfo())

    # Get regional values
    def get_regional_value(img, first):

        stats = img.reduceRegion(
            **{
                "reducer": ee.Reducer.mean(),
                "geometry": target_geom,
                "scale": SCALE,
                "maxPixels": 2e11,
            }
        )

        # Map null values to -999
        stats = stats.map(
            lambda k, v: ee.Algorithms.If(
                ee.Algorithms.IsEqual(v, None), -999, stats.get(k)
            )
        )
        metric = stats.get(target_var)
        returnValue = ee.List(first).add(metric)

        return returnValue

    results = ee.List([])
    regional_metrics_yearly = metric_yearly_cimg.iterate(get_regional_value, results)

    mean_annual_value = ee.Number(
        ee.List(regional_metrics_yearly)
        .filter(ee.Filter.neq("item", -999))
        .map(lambda v: ee.Number(v).multiply(scale_factor))
        .reduce("mean")
    )

    # Explicit null handling not needed
    return mean_annual_value


def smap_annual_mean(start_yr, end_yr, target_var, target_ftc):

    target_years = ee.List.sequence(start_yr, end_yr)
    target_geom = target_ftc.geometry()

    # print("[DEBUG]\n [terraclim_annual_mean]\n ", target_var.getInfo())
    # print("[DEBUG]\n [terraclim_annual_mean]\n ", target_years.getInfo())

    SMAP10KM = ee.ImageCollection(
        lib.get_public_asset("nasa_smap_soil_moisture")).select([target_var])

    # Expected SCALE = 10000
    projection = ee.Image(SMAP10KM.first()).projection()
    SCALE = projection.nominalScale()

    def aggregate_months(year):

        date_start = ee.Date.fromYMD(year, 1, 1)
        date_end = date_start.advance(1, "year")

        year_img = (
            SMAP10KM.filterDate(date_start, date_end)
            .sum()
            .set({"year": year, "system:time_start": date_start})
        )
        return year_img

    # Convert monthly image collection to yearly
    metric_yearly_cimg = ee.ImageCollection(target_years.map(aggregate_months))

    # print("[DEBUG]\n [terraclim_annual_mean]\n ", metric_yearly_cimg.getInfo())

    # Get regional values
    def get_regional_value(img, first):

        stats = img.reduceRegion(
            **{
                "reducer": ee.Reducer.mean(),
                "geometry": target_geom,
                "scale": SCALE,
                "maxPixels": 2e11,
            }
        )

        # Map null values to -999
        stats = stats.map(
            lambda k, v: ee.Algorithms.If(
                ee.Algorithms.IsEqual(v, None), -999, stats.get(k)
            )
        )
        metric = stats.get(target_var)
        returnValue = ee.List(first).add(metric)

        return returnValue

    results = ee.List([])
    regional_metrics_yearly = metric_yearly_cimg.iterate(get_regional_value, results)

    mean_annual_value = ee.Number(
        ee.List(regional_metrics_yearly)
        .filter(ee.Filter.neq("item", -999))
        .reduce("mean")
    )

    # Explicit null handling not needed
    return mean_annual_value


def smap_monthly_mean(start_yr, end_yr, target_var, target_ftc):

    target_years = ee.List.sequence(start_yr, end_yr)
    target_geom = target_ftc.geometry()

    # print("[DEBUG]\n [terraclim_monthly_mean]\n ", target_var.getInfo())
    # print("[DEBUG]\n [terraclim_monthly_mean]\n ", target_years.getInfo())

    SMAP10KM = ee.ImageCollection(
        lib.get_public_asset("nasa_smap_soil_moisture")).select([target_var])

    # Expected SCALE = 10km
    projection = ee.Image(SMAP10KM.first()).projection()
    SCALE = projection.nominalScale()

    # Calculation fails with null values using nominal scale
    # SCALE = 30

    def aggregate_months(year):

        date_start = ee.Date.fromYMD(year, 1, 1)
        date_end = date_start.advance(1, "year")

        year_img = (
            SMAP10KM.filterDate(date_start, date_end)
            .mean()
            .set({"year": year, "system:time_start": date_start})
        )
        return year_img

    # Convert monthly image collection to yearly
    metric_yearly_cimg = ee.ImageCollection(target_years.map(aggregate_months))

    # print("[DEBUG]\n [terraclim_annual_mean]\n ", metric_yearly_cimg.getInfo())

    # Get regional values
    def get_regional_value(img, first):

        stats = img.reduceRegion(
            **{
                "reducer": ee.Reducer.mean(),
                "geometry": target_geom,
                "scale": SCALE,
                "maxPixels": 2e11,
            }
        )

        # Map null values to -999
        stats = stats.map(
            lambda k, v: ee.Algorithms.If(
                ee.Algorithms.IsEqual(v, None), -999, stats.get(k)
            )
        )
        metric = stats.get(target_var)
        returnValue = ee.List(first).add(metric)

        return returnValue

    results = ee.List([])
    regional_metrics_yearly = metric_yearly_cimg.iterate(get_regional_value, results)

    if debug_mode == True:
        print(
            "[terraclim_monthly_mean] regional_metrics_yearly",
            regional_metrics_yearly.getInfo(),
        )

    mean_monthly = ee.Number(
        ee.List(regional_metrics_yearly)
        .filter(ee.Filter.neq("item", -999))
        .reduce("mean")
    )

    # null handling
    mean_monthly_value = ee.Algorithms.If(
        ee.Algorithms.IsEqual(mean_monthly, None),
        # Else null
        mean_monthly,
        mean_monthly.multiply(1000),
    )

    return mean_monthly_value


# Mean annual runoff
def mean_annual_runoff_mm(catchment_ftc):

    catchment_geom = catchment_ftc.geometry()

    # FEKETE (30' ~ 55560 m )
    RUNOFF = ee.Image(lib.get_private_asset("cmp_ro_grdc_runoff"))

    # Expected SCALE = 55560
    projection = ee.Image(RUNOFF).projection()
    SCALE = projection.nominalScale()

    mean_runoff_mm_value = ee.Number(
        RUNOFF.reduceRegion(
            **{
                "reducer": ee.Reducer.mean(),
                "geometry": catchment_geom,
                "scale": SCALE,
                "maxPixels": 2e11,
            }
        ).get("b1")
    )

    # Explicit null handling not needed
    if debug_mode == True:
        print("[DEBUG] [mean_annual_runoff_mm]", mean_runoff_mm_value.getInfo())
    return mean_runoff_mm_value


# Mean precipitation


def mean_annual_prec_mm(catchment_ftc) -> ee.Number:

    # World Clim 2.1 30 Arc seconds resolution; ~900m
    BIOCLIMATE = ee.Image(lib.get_private_asset("worldclim_bio"))
    BIOPRECIPITATION = BIOCLIMATE.select(["b1"], ["bio12"])

    # Expected SCALE = 900
    projection = ee.Image(BIOCLIMATE).projection()
    SCALE = projection.nominalScale()

    catchment_geom = catchment_ftc.geometry()

    mean_annual_prec_mm_value = ee.Number(
        BIOPRECIPITATION.reduceRegion(
            **{
                "reducer": ee.Reducer.mean(),
                "geometry": catchment_geom,
                "scale": SCALE,
                "maxPixels": 2e11,
            }
        ).get("bio12")
    )

    # Explicit null handling not needed
    return mean_annual_prec_mm_value


# Predominant biome
def predominant_biome(catchment_ftc):

    # Biome
    BIOMES = ee.FeatureCollection(lib.get_public_asset("biome2017"))

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

        return ee.Feature(feat).setMulti(
            {
                "AreaBiome": areaBiomeZone,
                "AreaCatch": catchment_area_m,
                "PercentageBiome": perc,
            }
        )

    # Put a bounding box around the catchment
    # to speed up computation

    aCATCH = catchment_ftc.filterBounds(catchment_bbox)
    aBIOMES = BIOMES.filterBounds(catchment_bbox)

    # [[I-1]] Calculate area of overlap between biome and catchment
    catchBiome = aBIOMES.map(get_biome)

    biome_percentages = catchBiome.aggregate_array("PercentageBiome")
    biome_names = catchBiome.aggregate_array("BIOME_NAME")
    index_pb = ee.Array(biome_percentages).argmax().get(0)
    predominant_biome = biome_names.get(index_pb)
    # Explicit null handling not needed
    return predominant_biome


def predominant_climate(catchment_ftc):

    catchment_geom = catchment_ftc.geometry()

    # Climate
    CLIMATE = ee.Image(lib.get_private_asset("beck_clim"))

    # Expected SCALE = 1000
    projection = ee.Image(CLIMATE).projection()
    SCALE = projection.nominalScale()

    modal_climate_category = CLIMATE.reduceRegion(
        **{
            "reducer": ee.Reducer.mode(),
            "geometry": catchment_geom,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("b1")
    # Explicit null handling not needed
    return modal_climate_category


# Population


def population_density(target_ftc):

    target_geom = target_ftc.geometry()

    # ==========================================================================
    #  LOAD DATA
    # ==========================================================================
    POPULATION = ee.ImageCollection(lib.get_public_asset("GPWv411_pop_den"))

    # First image; 2020
    POPULATION = POPULATION.limit(1, "system:time_start", False).first()
    # Expected SCALE = 927.67

    projection = ee.Image(POPULATION).projection()
    SCALE = projection.nominalScale()

    # ==========================================================================
    #  Population
    # ==========================================================================

    mean_pop_density = (
        POPULATION.reduceRegion(
            **{
                "reducer": ee.Reducer.mean(),
                "geometry": target_geom,
                "scale": SCALE,
                "maxPixels": 2e11,
            }
        )
    ).get("population_density")
    # Explicit null handling not needed
    return mean_pop_density


def population(target_ftc):

    mean_pop_density = population_density(target_ftc)

    # Calculate the area of the catchment in km;
    target_geom = target_ftc.geometry()
    targetAreaValue = target_geom.area(1).divide(1000 * 1000)

    # Handle null values
    pop_count_value = ee.Algorithms.If(
        ee.Algorithms.IsEqual(mean_pop_density, None),
        # Else null
        mean_pop_density,
        ee.Number(mean_pop_density).multiply(targetAreaValue),
    )

    return pop_count_value


# ==============================================================================
# Reservoir Parameters
# ==============================================================================

# Utils
def minimum_elevation_dam(reservoir_ftc):

    if cfg.paramHydroDEM == True:
        DEM = ee.Image(lib.get_public_asset("hydrosheds") + cfg.hydrodataset + "CONDEM").rename(
            ["elevation"]
        )
    else:
        DEM = ee.Image(lib.get_public_asset("nasa_srtm"))

    # Expected SCALE = 30 for SRTM
    projection = ee.Image(DEM).projection()
    SCALE = projection.nominalScale()

    snapped_dam_longitude = ee.Number(ee.Feature(reservoir_ftc.first()).get("ps_lon"))
    snapped_dam_latitude = ee.Number(ee.Feature(reservoir_ftc.first()).get("ps_lat"))

    raw_dam_longitude = ee.Number(ee.Feature(reservoir_ftc.first()).get("raw_lon"))
    raw_dam_latitude = ee.Number(ee.Feature(reservoir_ftc.first()).get("raw_lat"))

    # Dam location
    # Use snapped/raw dam location for min elevation as indicated in
    # config file
    if cfg.delineate_snapped == True:
        analysis_dam_point_location = ee.Geometry.Point(
            snapped_dam_longitude, snapped_dam_latitude
        )
    else:
        analysis_dam_point_location = ee.Geometry.Point(
            raw_dam_longitude, raw_dam_latitude
        )

    pt_min_elevation = DEM.reduceRegion(
        **{
            "reducer": ee.Reducer.min(),
            "geometry": analysis_dam_point_location,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("elevation")
    # Explicit null handling not needed
    return pt_min_elevation


# Not needed if maximum_depth_alt2 not used.
def minimum_elevation(reservoir_ftc):

    reservoir_geom = reservoir_ftc.geometry()

    if cfg.paramHydroDEM == True:
        DEM = ee.Image(lib.get_public_asset("hydrosheds") + cfg.hydrodataset + "CONDEM").rename(
            ["elevation"]
        )
    else:
        DEM = ee.Image(lib.get_public_asset("nasa_srtm"))

    # Expected SCALE = 30
    projection = ee.Image(DEM).projection()
    SCALE = projection.nominalScale()

    geom_min_elevation = ee.Number(
        DEM.reduceRegion(
            **{
                "reducer": ee.Reducer.min(),
                "geometry": reservoir_geom,
                "scale": SCALE,
                "maxPixels": 2e11,
            }
        ).get("elevation")
    )
    # Explicit null handling not needed
    return geom_min_elevation


# Not needed if maximum_depth_alt1, maximum_depth_alt2 not used.
def maximum_elevation(reservoir_ftc):

    reservoir_geom = reservoir_ftc.geometry()

    if cfg.paramHydroDEM == True:
        DEM = ee.Image(lib.get_public_asset("hydrosheds") + cfg.hydrodataset + "CONDEM").rename(
            ["elevation"]
        )
    else:
        DEM = ee.Image(lib.get_public_asset("nasa_srtm"))

    # Expected SCALE = 30
    projection = ee.Image(DEM).projection()
    SCALE = projection.nominalScale()

    geom_max_elevation = DEM.reduceRegion(
        **{
            "reducer": ee.Reducer.max(),
            "geometry": reservoir_geom,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("elevation")

    # Explicit null handling not needed
    return geom_max_elevation


# Outputs
def maximum_depth(reservoir_ftc):

    reservoir_geom = reservoir_ftc.geometry()

    # Depth = water surface elevation - elevation
    water_level_elevation = ee.Number.parse(
        reservoir_ftc.first().get("r_imputed_water_elevation")
    )

    if cfg.paramHydroDEM == True:
        DEM = ee.Image(lib.get_public_asset("hydrosheds") + cfg.hydrodataset + "CONDEM").rename(
            ["elevation"]
        )
    else:
        DEM = ee.Image(lib.get_public_asset("nasa_srtm"))

    # Expected SCALE = 30
    projection = ee.Image(DEM).projection()
    SCALE = projection.nominalScale()

    max_depth = (
        DEM.multiply(-1)
        .add(water_level_elevation)
        .reduceRegion(
            **{
                "reducer": ee.Reducer.max(),
                "geometry": reservoir_geom,
                "scale": SCALE,
                "maxPixels": 2e11,
            }
        )
        .get("elevation")
    )

    # Explicit null handling not needed
    return max_depth


def maximum_depth_alt1(reservoir_ftc):

    # Max Depth = maximum elevation - minimum elevation
    max_elevation = ee.Number(maximum_elevation(reservoir_ftc))
    min_elevation_dam = ee.Number(minimum_elevation_dam(reservoir_ftc))

    # Null handling
    max_depth = ee.Algorithms.If(
        ee.Algorithms.IsEqual(max_elevation, None),
        # max or min & max elevation null; return null from max_elevation
        max_elevation,
        ee.Algorithms.If(
            ee.Algorithms.IsEqual(min_elevation_dam, None),
            # Min, but not max elevation are null; return null from min_elevation_dam
            min_elevation_dam,
            ee.Number(max_elevation.subtract(min_elevation_dam)),
        ),
    )

    return max_depth


def maximum_depth_alt2(reservoir_ftc):

    # Max Depth = maximum elevation - minimum elevation
    max_elevation = ee.Number(maximum_elevation(reservoir_ftc))
    min_elevation = ee.Number(minimum_elevation(reservoir_ftc))

    # Null handling
    max_depth = ee.Algorithms.If(
        ee.Algorithms.IsEqual(max_elevation, None),
        # max or min & max elevation null; return null from max_elevation
        max_elevation,
        ee.Algorithms.If(
            ee.Algorithms.IsEqual(min_elevation, None),
            # Min, but not max elevation are null; return null from min_elevation
            min_elevation,
            ee.Number(max_elevation.subtract(min_elevation)),
        ),
    )

    return max_depth


def mean_depth(reservoir_ftc):
    reservoir_geom = reservoir_ftc.geometry()

    # Depth = water surface elevation - elevation
    water_level_elevation = ee.Number.parse(
        reservoir_ftc.first().get("r_imputed_water_elevation")
    )

    if cfg.paramHydroDEM == True:
        DEM = ee.Image(lib.get_public_asset("hydrosheds") + cfg.hydrodataset + "CONDEM").rename(
            ["elevation"]
        )
    else:
        DEM = ee.Image(lib.get_public_asset("nasa_srtm"))

    # Expected SCALE = 30
    projection = ee.Image(DEM).projection()
    SCALE = projection.nominalScale()

    mean_depth_value = (
        DEM.multiply(-1)
        .add(water_level_elevation)
        .reduceRegion(
            **{
                "reducer": ee.Reducer.mean(),
                "geometry": reservoir_geom,
                "scale": SCALE,
                "maxPixels": 2e11,
            }
        )
        .get("elevation")
    )

    # Explicit null handling not needed
    return mean_depth_value


# Reservoir volume
def km2_to_m2(surface_area):
    # Area cannot be null
    # No explicit null handling needed
    return ee.Number(surface_area.multiply(1000 * 1000))


def reservoir_volume(surface_area, mean_depth):

    # Null handling
    # NB: area cannot be null
    reservoir_volumn_value = ee.Algorithms.If(
        ee.Algorithms.IsEqual(mean_depth, None),
        mean_depth,
        ee.Number(surface_area.multiply(mean_depth)),
    )

    return reservoir_volumn_value


# Mean monthly temperatures
def mean_monthly_temps(reservoir_ftc):

    reservoir_geom = reservoir_ftc.geometry()

    TAVG = ee.ImageCollection(lib.get_private_asset("worldclim_tavg"))
    TEMPERATURE = TAVG.select(["b1"]).toList(12)

    # Expected SCALE = 30
    projection = ee.Image(TAVG.first()).projection()
    SCALE = projection.nominalScale()

    months = ee.List.sequence(0, 11, 1)

    def monthly_temp(m):
        temp_value = (
            ee.Image(ee.List(TEMPERATURE).get(m))
            .reduceRegion(
                **{
                    "reducer": ee.Reducer.mean(),
                    "geometry": reservoir_geom,
                    "scale": SCALE,
                    "maxPixels": 2e11,
                }
            )
            .get("b1")
        )

        return temp_value

    temperatures = months.map(monthly_temp)

    if debug_mode == True:
        print("[mean_monthly_temps]", temperatures.getInfo())

    # Explicit null handling not needed
    return temperatures


def mean_olsen_kgperha(catchment_ftc):
    catch_geom = catchment_ftc.geometry()

    OLSEN = ee.Image(lib.get_private_asset("OlsenP_kgha1_World"))
    # Expected SCALE = 30
    projection = ee.Image(OLSEN).projection()
    SCALE = projection.nominalScale()

    mean_p_value = ee.Number(
        OLSEN.reduceRegion(
            **{
                "reducer": ee.Reducer.mean(),
                "geometry": catch_geom,
                "scale": SCALE,
                "maxPixels": 2e11,
            }
        ).get("b1")
    )

    # Explicit null handling not needed
    return mean_p_value


def mean_discharge_peryr(catchment_ftc):
    # Mean discharge
    mar_mm = mean_annual_runoff_mm(catchment_ftc)
    # Null handling
    mad_m3_peryr = ee.Algorithms.If(
        ee.Algorithms.IsEqual(mar_mm, None),
        # Else null
        mar_mm,
        ee.Number(mar_mm).multiply(area(catchment_ftc)).multiply(1000),
    )
    return mad_m3_peryr


def mean_discharge_pers(catchment_ftc):

    mad_m3_peryr = mean_discharge_peryr(catchment_ftc)

    # 1 year = 365.25 days = (365.25 days) × (24 hours/day) × (3600 seconds/hour) = 31557600
    # Null handling
    mad_m3_pers = ee.Algorithms.If(
        ee.Algorithms.IsEqual(mad_m3_peryr, None),
        # Else null
        mad_m3_peryr,
        ee.Number(mad_m3_peryr).divide(31557600),
    )
    return mad_m3_pers


# ==============================================================================
# Empty Profiles
# ==============================================================================

# For handling empty delineations


def profile_empty_point():

    properties_dict = {"ps_snap_displacement": "NA", "ps_lon": "NA", "ps_lat": "NA"}

    logger.warning(
        "[profile_empty_point] Snapped point asset not found, profiling empty point."
    )
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
        "c_mad_m3_peryr": "NA",
        "c_mad_m3_pers": "NA",
        "c_map_mm": "NA",
        "c_map_mm_alt1": "NA",
        "c_biome": "NONE",
        # Soil Characteristics
        "c_msocs_kgperm2": "NA",
        "c_msocc_perc": "NA",
        "c_msocc_gperkg": "NA",
        "c_msnc_gperkg": "NA",
        "c_msbdod_kgperdm3": "NA",
        "c_doc_export": "NA",
        "c_mswn_molperkg": "NA",
        "c_mswc_molperkg": "NA",
        # Soil Moisture
        "c_masm_mm": "NA",  # Slow
        "c_masm_mm_alt1": "NA",
        "c_climate_zone": "NA",
        "c_mpet_mm": "NA",
        "c_mpet_mm_alt1": "NA",
        "c_population": "NA",
        "c_population_density": "NA",
        "c_mar_mm_alt1": "NA",  # Very Slow
        "c_mar_mm_alt2": "NA",
        "c_mmr_mm_alt2": "NA",
        "c_mean_olsen": "NA",
        "c_soil_type": "NONE",
    }

    logger.warning(
        "[profile_empty_catchment] Catchment asset not found, profiling empty catchment."
    )
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
        # Soil Characteristics
        "r_msocs_kgperm2": "NA",
        "r_msocc_perc": "NA",
        "r_msocc_gperkg": "NA",
        "r_msnc_gperkg": "NA",
        "r_msbdod_kgperdm3": "NA",
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
        "r_mean_annual_windspeed": "NA",
    }
    logger.warning(
        "[profile_empty_reservoir] Reservoir asset not found, profiling empty reservoir."
    )
    return properties_dict


def profile_empty_nicatchment():

    properties_dict = {
        "n_population": "NA",
        "n_population_density": "NA",
        "n_doc_export": "NA",
        "n_mswn_molperkg": "NA",
        "n_mswc_molperkg": "NA",
    }

    logger.warning(
        "[profile_empty_nicatchment] NI Catchment asset not found, profiling empty nicatchment."
    )
    return properties_dict


def profile_empty_river():

    properties_dict = {"ms_length": "NA"}

    logger.warning(
        "[profile_empty_river] River asset not found, profiling empty river."
    )
    return properties_dict


# ==============================================================================
# Populated Profiles
# ==============================================================================

metric_format = {
    # Function specific default formats
    "area": "%.3f",
    "maximum_depth": "%.0f",
    "mean_slope": "%.0f",
    "landcover": "%.3f",
    "mean_annual_runoff_mm": "%.0f",
    "terraclim_annual_mean": "%.0f",
    "terraclim_monthly_mean": "%.0f",
    "mean_annual_prec_mm": "%.0f",
    "mean_soil_oc_stocks": "%.3f",
    "mean_soil_oc_content": "%.3f",
    "soc_percent": "%.3f",
    "mean_soil_nitrogen_content": "%.3f",
    "mean_soil_bdod": "%.3f",
    "total_doc_export": "%.3f",
    "mean_strata_weighted_mol_n": "%.3f",
    "mean_strata_weighted_mol_c": "%.3f",
    "twbda_annual_mean_pet": "%.0f",
    "population": "%.0f",
    "population_density": "%.2f",
    "mean_olsen_kgperha": "%.3f",
    "mean_discharge_peryr": "%.0f",
    "mean_discharge_pers": "%.9f",
    "mean_depth": "%.1f",
    "maximum_depth": "%.0f",
    "maximum_depth_alt1": "%.0f",
    "maximum_depth_alt2": "%.0f",
    "reservoir_volume": "%.0f",
    "mean_monthly_temps": "%.1f",
    "landcover_bysoil": "%.3f",
    "landcover_bysoil_buffer": "%.3f",
    "smap_monthly_mean": "%.0f",
    "mghr": "%.3f",
    # Function specific default formats (testing only)
    "minimum_elevation": "%.0f",
    # Metric specific formats (overrides function default)
    "mean_annual_windpseed_mpers": "%.2f",
}


def metric_formatter(metric_value, metric_function_name):

    if debug_mode == True:
        print(f"[DEBUG][metric_formatter] {metric_function_name}")
        print(f"[DEBUG][metric_formatter] {metric_value.getInfo()}")

    formatted_metric_value = ee.Algorithms.If(
        ee.Algorithms.IsEqual(metric_value, None),
        "ND",
        ee.Number(metric_value).format(metric_format[metric_function_name]),
    )

    if debug_mode == True:
        print(f"[DEBUG][metric_formatter] {formatted_metric_value.getInfo()}")

    return formatted_metric_value


def profile_catchment(catchment_ftc, landcover_analysis_file_str):

    # Catchment area
    area_km2 = metric_formatter(area(catchment_ftc), "area")

    if debug_mode == True:
        print("[DEBUG] [profile_catchment] area_km2", area_km2.getInfo(), "\n")

    # Catchment slope, [%], DEM
    mean_slope_pc = metric_formatter(mean_slope(catchment_ftc), "mean_slope")

    if debug_mode == True:
        print(
            "[DEBUG] [profile_catchment] mean_slope_pc", mean_slope_pc.getInfo(), "\n"
        )

    # Landcover, proportions, European Space Agency
    landcover_fracs = landcover(catchment_ftc, landcover_analysis_file_str)

    if debug_mode == True:
        print(
            "[DEBUG] [profile_catchment] landcover_fracs",
            landcover_fracs.getInfo(),
            "\n",
        )

    landcover_profile = {}
    for f in range(0, 9):
        var_name = f"landcover_{f}"
        if debug_mode == True:
            print(var_name)
        landcover_profile[var_name] = metric_formatter(
            ee.Number(ee.List(landcover_fracs).get(f)), "landcover"
        )

    if debug_mode == True:
        print(
            "[DEBUG] [profile_catchment] landcover_profile",
            landcover_profile,
            "\n",
        )

    # Mean annual Runoff, [mm yr-1], Fekete
    mar_mm = metric_formatter(
        mean_annual_runoff_mm(catchment_ftc), "mean_annual_runoff_mm"
    )

    # Alt Mean annual runnoff (gldas)
    # mean_annual_runoff_mm_gldas(catchment_ftc)
    mar_mm_alt1 = "UD"

    # Alt Mean annual runnoff (terraclim)
    mar_mm_alt2 = metric_formatter(
        terraclim_annual_mean(2000, 2019, "ro", 1, catchment_ftc),
        "terraclim_annual_mean",
    )

    # Alt Mean monthly discharge
    mmr_mm_alt2 = metric_formatter(
        terraclim_monthly_mean(2000, 2019, "ro", 1, catchment_ftc),
        "terraclim_monthly_mean",
    )

    # Mean annual precipitation, [mm yr-1], WorldClim 2.1
    map_mm = metric_formatter(mean_annual_prec_mm(catchment_ftc), "mean_annual_prec_mm")

    map_mm_alt1 = metric_formatter(
        terraclim_annual_mean(2000, 2019, "pr", 1.0, catchment_ftc),
        "terraclim_annual_mean",
    )

    # Predominant biome, Dinerstein et al. (2017)
    biome = predominant_biome(catchment_ftc)

    # Mean soil organic carbon stocks (0-30cm), [kg m-2], Soil Grids
    msocs_kgperm2 = metric_formatter(
        mean_soil_oc_stocks(catchment_ftc), "mean_soil_oc_stocks"
    )

    # Mean soil organic carbon content (0-30cm), [g/kg], Soil Grids
    msocc_gperkg = metric_formatter(
        mean_soil_oc_content(catchment_ftc),
        "mean_soil_oc_content",
    )

    # Mean soil organic carbon content (0-30cm), [%], Soil Grids
    msocc_perc = metric_formatter(soc_percent(catchment_ftc), "soc_percent")

    # Mean soil organic nitrogen content (0-30cm), [g/kg], Soil Grids
    msnc_gperkg = metric_formatter(
        mean_soil_nitrogen_content(catchment_ftc), "mean_soil_nitrogen_content"
    )

    # Mean soil bulk density
    msbdod_kgperdm3 = metric_formatter(mean_soil_bdod(catchment_ftc), "mean_soil_bdod")

    # DOC export
    doc_export = metric_formatter(total_doc_export(catchment_ftc), "total_doc_export")

    # Moles N
    mswn_molperkg = metric_formatter(
        mean_strata_weighted_mol_n(catchment_ftc), "mean_strata_weighted_mol_n"
    )

    # Moles C
    mswc_molperkg = metric_formatter(
        mean_strata_weighted_mol_c(catchment_ftc), "mean_strata_weighted_mol_c"
    )

    # Predominant climate zone
    climate_zone = predominant_climate(catchment_ftc)

    # Evapotranspiration, terraclim (scaled by 0.1)
    mpet_mm = metric_formatter(
        terraclim_annual_mean(2000, 2019, "pet", 0.1, catchment_ftc),
        "terraclim_annual_mean",
    )

    mpet_mm_alt1 = metric_formatter(
        twbda_annual_mean_pet(catchment_ftc), "twbda_annual_mean_pet"
    )

    # Soil Moisture
    masm_mm = metric_formatter(
        terraclim_monthly_mean(2000, 2019, "soil", 0.1, catchment_ftc),
        "terraclim_monthly_mean",
    )

    # Alternative soil moisture
    masm_mm_alt1 = metric_formatter(
        smap_monthly_mean(2016, 2021, "smp", catchment_ftc), "smap_monthly_mean"
    )

    # Population
    current_population_density = metric_formatter(
        population_density(catchment_ftc), "population_density"
    )

    current_population = metric_formatter(population(catchment_ftc), "population")

    # Olsen P
    mean_olsen = metric_formatter(
        mean_olsen_kgperha(catchment_ftc), "mean_olsen_kgperha"
    )

    # Soil Type
    soil_type_cat = soil_type(catchment_ftc)

    # Mean discharge
    mad_m3_peryr = metric_formatter(
        mean_discharge_peryr(catchment_ftc), "mean_discharge_peryr"
    )

    mad_m3_pers = metric_formatter(
        mean_discharge_pers(catchment_ftc), "mean_discharge_pers"
    )

    # Set parameters
    updated_catchment_ftc = catchment_ftc.map(
        lambda feat: feat.set(
            {
                "c_area_km2": area_km2,
                "c_mean_slope_pc": mean_slope_pc,
                # Landcover
                "c_landcover_0": landcover_profile["landcover_0"],
                "c_landcover_1": landcover_profile["landcover_1"],
                "c_landcover_2": landcover_profile["landcover_2"],
                "c_landcover_3": landcover_profile["landcover_3"],
                "c_landcover_4": landcover_profile["landcover_4"],
                "c_landcover_5": landcover_profile["landcover_5"],
                "c_landcover_6": landcover_profile["landcover_6"],
                "c_landcover_7": landcover_profile["landcover_7"],
                "c_landcover_8": landcover_profile["landcover_8"],
                "c_mar_mm": mar_mm,
                "c_mad_m3_peryr": mad_m3_peryr,
                "c_mad_m3_pers": mad_m3_pers,
                "c_map_mm": map_mm,
                "c_map_mm_alt1": map_mm_alt1,
                "c_biome": biome,
                # Soil Characteristics
                "c_msocs_kgperm2": msocs_kgperm2,
                "c_msocc_perc": msocc_perc,
                "c_msocc_gperkg": msocc_gperkg,
                "c_msnc_gperkg": msnc_gperkg,
                "c_msbdod_kgperdm3": msbdod_kgperdm3,
                "c_doc_export": doc_export,
                "c_mswn_molperkg": mswn_molperkg,
                "c_mswc_molperkg": mswc_molperkg,
                # Soil Moisture
                "c_masm_mm": masm_mm,  # Slow
                "c_masm_mm_alt1": masm_mm_alt1,
                "c_climate_zone": climate_zone,
                "c_mpet_mm": mpet_mm,
                "c_mpet_mm_alt1": mpet_mm_alt1,
                "c_population": current_population,
                "c_population_density": current_population_density,
                "c_mar_mm_alt1": mar_mm_alt1,  # Very Slow
                "c_mar_mm_alt2": mar_mm_alt2,
                "c_mmr_mm_alt2": mmr_mm_alt2,
                "c_mean_olsen": mean_olsen,
                "c_soil_type": soil_type_cat,
            }
        )
    )

    return ee.FeatureCollection(updated_catchment_ftc)


def profile_nicatchment(nicatchment_ftc):

    # Population
    current_population_density = metric_formatter(
        population_density(nicatchment_ftc), "population_density")

    current_population = metric_formatter(population(nicatchment_ftc), "population")

    # DOC export
    doc_export = metric_formatter(total_doc_export(nicatchment_ftc), "total_doc_export")

    # Moles N
    mswn_molperkg = metric_formatter(
        mean_strata_weighted_mol_n(nicatchment_ftc), "mean_strata_weighted_mol_n")

    # Moles C
    mswc_molperkg = metric_formatter(
        mean_strata_weighted_mol_c(nicatchment_ftc), "mean_strata_weighted_mol_c")

    updated_nicatchment_ftc = nicatchment_ftc.map(
        lambda feat: feat.set(
            {
                "n_population": current_population,
                "n_population_density": current_population_density,
                "n_doc_export": doc_export,
                "n_mswn_molperkg": mswn_molperkg,
                "n_mswc_molperkg": mswc_molperkg,
            }
        )
    )

    return ee.FeatureCollection(updated_nicatchment_ftc)


def river_length(river_ftc):
    def set_river_length(rfeat):
        calculated_length = ee.Number(rfeat.geometry().length()).divide(1000)
        rfeat = rfeat.set("ee_length_km", calculated_length)
        return rfeat

    inundated_river_ftc = river_ftc.map(set_river_length)

    inundated_river_length = inundated_river_ftc.aggregate_array("ee_length_km").reduce(
        ee.Reducer.sum()
    )

    return inundated_river_length


def profile_river(river_ftc):

    length = ee.Number(river_length(river_ftc)).format("%.3f")

    updated_river_ftc = river_ftc.map(lambda feat: feat.set({"ms_length": length}))

    return ee.FeatureCollection(updated_river_ftc)


def profile_reservoir(reservoir_ftc, landcover_analysis_file_str, c_dam_id):

    # Reservoir Area
    area_km2 = metric_formatter(area(reservoir_ftc), "area")

    # Only assess depth for future dams
    if c_dam_id not in mtr.existing_dams:
        # Reservoir mean depth
        mean_depth_m = metric_formatter(mean_depth(reservoir_ftc), "mean_depth")

        # Reservoir maximum depth
        maximum_depth_m = metric_formatter(
            maximum_depth(reservoir_ftc), "maximum_depth"
        )

        maximum_depth_m_alt1 = metric_formatter(
            maximum_depth_alt1(reservoir_ftc), "maximum_depth_alt1"
        )

        maximum_depth_m_alt2 = metric_formatter(
            maximum_depth_alt2(reservoir_ftc), "maximum_depth_alt2"
        )

        # Reservoir volume
        volume_m3 = metric_formatter(
            reservoir_volume(km2_to_m2(area(reservoir_ftc)), mean_depth(reservoir_ftc)),
            "reservoir_volume",
        )

    else:
        # Reservoir mean depth
        mean_depth_m = ee.String("NA")

        # Reservoir maximum depth
        maximum_depth_m = ee.String("NA")
        maximum_depth_m_alt1 = ee.String("NA")
        maximum_depth_m_alt2 = ee.String("NA")

        # Reservoir volume
        volume_m3 = ee.String("NA")

    # Mean monthly temperatures
    temperature_profile_c = mean_monthly_temps(reservoir_ftc)
    temperature_profile = {}
    for t in range(0, 12):
        temperature_profile[f"mean_temp_{t+1}"] = metric_formatter(
            ee.List(temperature_profile_c).get(t), "mean_monthly_temps"
        )

    # Mean annual global horizontal irradiance (NASA) 2005
    maghr_kwhperm2perday = mghr(reservoir_ftc)

    mghr_all_kwhperm2perday = metric_formatter(
        ee.Number(maghr_kwhperm2perday[0]), "mghr"
    )

    mghr_nov_mar_kwhperm2perday = metric_formatter(
        ee.Number(maghr_kwhperm2perday[1]), "mghr"
    )

    mghr_may_sept_kwhperm2perday = metric_formatter(
        ee.Number(maghr_kwhperm2perday[2]), "mghr"
    )

    # Mean annual global horizontal irradiance (terraclim)
    #  TODO terraclim_mghr underdevelopment (see geocaret_params_draft)
    # Example use: terraclim_mghr(2000, 2019, reservoir_ftc)
    mghr_all_kwhperm2perday_alt1 = "UD"
    mghr_nov_mar_kwhperm2perday_alt1 = "UD"
    mghr_may_sept_kwhperm2perday_alt1 = "UD"

    # Mean soil organic carbon stocks (0-30cm), [kg m-2], Soil Grids
    msocs_kgperm2 = metric_formatter(
        mean_soil_oc_stocks(reservoir_ftc), "mean_soil_oc_stocks"
    )

    # Mean soil organic carbon content (0-30cm), [g/kg], Soil Grids
    msocc_gperkg = metric_formatter(
        mean_soil_oc_content(reservoir_ftc), "mean_soil_oc_content"
    )

    # Mean soil organic carbon content (0-30cm), [%], Soil Grids
    msocc_perc = metric_formatter(soc_percent(reservoir_ftc), "soc_percent")

    # Mean soil organic nitrogen content (0-30cm), [g/kg], Soil Grids
    msnc_gperkg = metric_formatter(
        mean_soil_nitrogen_content(reservoir_ftc), "mean_soil_nitrogen_content"
    )

    # Mean soil bulk density
    msbdod_kgperdm3 = metric_formatter(mean_soil_bdod(reservoir_ftc), "mean_soil_bdod")

    # Landcover (stratification by soil type needed)
    if c_dam_id in mtr.buffer_method:
        landcover_bysoil_fracs = landcover_bysoil_buffer(
            reservoir_ftc, landcover_analysis_file_str, c_dam_id
        )

        landcover_bysoil_profile = {}
        for f in range(0, 27):
            var_name = f"landcover_bysoil_{f}"
            landcover_bysoil_profile[var_name] = metric_formatter(
                ee.List(landcover_bysoil_fracs).get(f), "landcover_bysoil_buffer"
            )
    else:
        landcover_bysoil_fracs = landcover_bysoil(
            reservoir_ftc, landcover_analysis_file_str
        )

        landcover_bysoil_profile = {}
        for f in range(0, 27):
            var_name = f"landcover_bysoil_{f}"
            landcover_bysoil_profile[var_name] = metric_formatter(
                ee.List(landcover_bysoil_fracs).get(f), "landcover_bysoil"
            )

    # Mean annual windspeed
    mean_annual_windpseed_mpers = metric_formatter(
        terraclim_monthly_mean(2000, 2019, "vs", 0.01, reservoir_ftc),
        "mean_annual_windpseed_mpers",
    )

    if debug_mode == True:
        print(
            "[profile_reservoir] mean_annual_windpseed_mpers",
            mean_annual_windpseed_mpers.getInfo(),
        )

    updated_reservoir_ftc = reservoir_ftc.map(
        lambda feat: feat.set(
            {
                "r_area_km2": area_km2,
                "r_mean_depth_m": mean_depth_m,
                "r_maximum_depth_m": maximum_depth_m,
                "r_maximum_depth_m_alt1": maximum_depth_m_alt1,
                "r_maximum_depth_m_alt2": maximum_depth_m_alt2,
                "r_volume_m3": volume_m3,
                "r_mean_temp_1": temperature_profile["mean_temp_1"],
                "r_mean_temp_2": temperature_profile["mean_temp_2"],
                "r_mean_temp_3": temperature_profile["mean_temp_3"],
                "r_mean_temp_4": temperature_profile["mean_temp_4"],
                "r_mean_temp_5": temperature_profile["mean_temp_5"],
                "r_mean_temp_6": temperature_profile["mean_temp_6"],
                "r_mean_temp_7": temperature_profile["mean_temp_7"],
                "r_mean_temp_8": temperature_profile["mean_temp_8"],
                "r_mean_temp_9": temperature_profile["mean_temp_9"],
                "r_mean_temp_10": temperature_profile["mean_temp_10"],
                "r_mean_temp_11": temperature_profile["mean_temp_11"],
                "r_mean_temp_12": temperature_profile["mean_temp_12"],
                "r_mghr_all_kwhperm2perday": mghr_all_kwhperm2perday,
                "r_mghr_nov_mar_kwhperm2perday": mghr_nov_mar_kwhperm2perday,
                "r_mghr_may_sept_kwhperm2perday": mghr_may_sept_kwhperm2perday,
                "r_mghr_all_kwhperm2perday_alt1": mghr_all_kwhperm2perday_alt1,
                "r_mghr_nov_mar_kwhperm2perday_alt1": mghr_nov_mar_kwhperm2perday_alt1,
                "r_mghr_may_sept_kwhperm2perday_alt1": mghr_may_sept_kwhperm2perday_alt1,
                # Soil Characteristics
                "r_msocs_kgperm2": msocs_kgperm2,
                "r_msocc_perc": msocc_perc,
                "r_msocc_gperkg": msocc_gperkg,
                "r_msnc_gperkg": msnc_gperkg,
                "r_msbdod_kgperdm3": msbdod_kgperdm3,
                # Landcover
                "r_landcover_bysoil_0": landcover_bysoil_profile["landcover_bysoil_0"],
                "r_landcover_bysoil_1": landcover_bysoil_profile["landcover_bysoil_1"],
                "r_landcover_bysoil_2": landcover_bysoil_profile["landcover_bysoil_2"],
                "r_landcover_bysoil_3": landcover_bysoil_profile["landcover_bysoil_3"],
                "r_landcover_bysoil_4": landcover_bysoil_profile["landcover_bysoil_4"],
                "r_landcover_bysoil_5": landcover_bysoil_profile["landcover_bysoil_5"],
                "r_landcover_bysoil_6": landcover_bysoil_profile["landcover_bysoil_6"],
                "r_landcover_bysoil_7": landcover_bysoil_profile["landcover_bysoil_7"],
                "r_landcover_bysoil_8": landcover_bysoil_profile["landcover_bysoil_8"],
                "r_landcover_bysoil_9": landcover_bysoil_profile["landcover_bysoil_9"],
                "r_landcover_bysoil_10": landcover_bysoil_profile[
                    "landcover_bysoil_10"
                ],
                "r_landcover_bysoil_11": landcover_bysoil_profile[
                    "landcover_bysoil_11"
                ],
                "r_landcover_bysoil_12": landcover_bysoil_profile[
                    "landcover_bysoil_12"
                ],
                "r_landcover_bysoil_13": landcover_bysoil_profile[
                    "landcover_bysoil_13"
                ],
                "r_landcover_bysoil_14": landcover_bysoil_profile[
                    "landcover_bysoil_14"
                ],
                "r_landcover_bysoil_15": landcover_bysoil_profile[
                    "landcover_bysoil_15"
                ],
                "r_landcover_bysoil_16": landcover_bysoil_profile[
                    "landcover_bysoil_16"
                ],
                "r_landcover_bysoil_17": landcover_bysoil_profile[
                    "landcover_bysoil_17"
                ],
                "r_landcover_bysoil_18": landcover_bysoil_profile[
                    "landcover_bysoil_18"
                ],
                "r_landcover_bysoil_19": landcover_bysoil_profile[
                    "landcover_bysoil_19"
                ],
                "r_landcover_bysoil_20": landcover_bysoil_profile[
                    "landcover_bysoil_20"
                ],
                "r_landcover_bysoil_21": landcover_bysoil_profile[
                    "landcover_bysoil_21"
                ],
                "r_landcover_bysoil_22": landcover_bysoil_profile[
                    "landcover_bysoil_22"
                ],
                "r_landcover_bysoil_23": landcover_bysoil_profile[
                    "landcover_bysoil_23"
                ],
                "r_landcover_bysoil_24": landcover_bysoil_profile[
                    "landcover_bysoil_24"
                ],
                "r_landcover_bysoil_25": landcover_bysoil_profile[
                    "landcover_bysoil_25"
                ],
                "r_landcover_bysoil_26": landcover_bysoil_profile[
                    "landcover_bysoil_26"
                ],
                "r_mean_annual_windspeed": mean_annual_windpseed_mpers,
            }
        )
    )

    return ee.FeatureCollection(updated_reservoir_ftc)


def batch_delete_shapes(c_dam_ids, output_type):

    file_prefix = export.export_job_specs[output_type]["fileprefix"]

    for c_dam_id in c_dam_ids:

        c_dam_id_str = str(c_dam_id)

        targetAssetName = cfg.ps_geocaret_folder + "/" + file_prefix + c_dam_id_str

        try:
            ee.data.deleteAsset(targetAssetName)
        except Exception as error:
            msg = f"Problem deleting intermediate output {targetAssetName}"
            logger.exception(f"{msg}")
            continue


def batch_profile_reservoirs(c_dam_ids):

    for c_dam_id in c_dam_ids:

        c_dam_id_str = str(c_dam_id)

        reservoirAssetName = cfg.ps_geocaret_folder + "/" + "r_" + c_dam_id_str
        reservoir_ftc = ee.FeatureCollection(reservoirAssetName)

        try:
            landcover_analysis_file_str = str(
                mtr.id_landcover_analysis_file_lookup[c_dam_id]
            )
            updated_reservoir_ftc = profile_reservoir(
                reservoir_ftc, landcover_analysis_file_str, c_dam_id
            )
            export.export_ftc(
                updated_reservoir_ftc, c_dam_id_str, "reservoir_vector_params"
            )
        except Exception as error:
            msg = "Problem updating Reservoir vector with calculated parameters"
            logger.exception(f"{msg}")
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue


def batch_profile_catchments(c_dam_ids):

    for c_dam_id in c_dam_ids:

        c_dam_id_str = str(c_dam_id)

        catchmentAssetName = cfg.ps_geocaret_folder + "/" + "c_" + c_dam_id_str
        catchment_ftc = ee.FeatureCollection(catchmentAssetName)

        try:
            landcover_analysis_file_str = str(
                mtr.id_landcover_analysis_file_lookup[c_dam_id]
            )
            updated_catchment_ftc = profile_catchment(
                catchment_ftc, landcover_analysis_file_str
            )
            export.export_ftc(
                updated_catchment_ftc, c_dam_id_str, "catchment_vector_params"
            )
        except Exception as error:
            msg = "Problem updating Catchment vector with calculated parameters"
            logger.exception(f"{msg}")
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue


def batch_profile_rivers(c_dam_ids):

    for c_dam_id in c_dam_ids:

        c_dam_id_str = str(c_dam_id)

        riverAssetName = cfg.ps_geocaret_folder + "/" + "ms_" + c_dam_id_str
        river_ftc = ee.FeatureCollection(riverAssetName)

        try:
            updated_river_ftc = profile_river(river_ftc)
            export.export_ftc(
                ee.FeatureCollection(updated_river_ftc),
                c_dam_id_str,
                "main_river_vector_params",
            )
        except Exception as error:
            msg = "Problem updating River vector with calculated parameters"
            logger.exception(f"{msg}")
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue


def batch_profile_nicatchments(c_dam_ids):

    for c_dam_id in c_dam_ids:

        c_dam_id_str = str(c_dam_id)

        nicatchmentAssetName = cfg.ps_geocaret_folder + "/" + "n_" + c_dam_id_str
        nicatchment_ftc = ee.FeatureCollection(nicatchmentAssetName)

        try:
            updated_nicatchment_ftc = profile_nicatchment(nicatchment_ftc)
            export.export_ftc(
                updated_nicatchment_ftc, c_dam_id_str, "ni_catchment_vector_params"
            )
        except Exception as error:
            msg = "Problem updating NI Catchment vector with calculated parameters"
            logger.exception(f"{msg}")
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue


if __name__ == "__main__":

    # Development
    print("Development...")

    catchment_ftc = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/C_1201"
    )
    reservoir_ftc = ee.FeatureCollection(
        "users/kkh451/XHEET/GAWLAN_20230130-1040/R_1201"
    )
    catchment_geom = catchment_ftc.geometry()

    catchment_ftc = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/soil_poly_px2N"
    )
    # landcover_analysis_file_str = "projects/ee-future-dams/assets/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds"
    # catchment_properties = profile_catchment(catchment_ftc, landcover_analysis_file_str)
    # print(catchment_properties.getInfo())
    # print(reservoir_ftc.getInfo())
    landcover_analysis_file_str = "projects/ee-future-dams/assets/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds"
    reservoir_properties = profile_reservoir(
        reservoir_ftc, landcover_analysis_file_str, "1201"
    )
    print(reservoir_properties.getInfo())
