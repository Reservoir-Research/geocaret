debug_mode = False

import ee
import logging

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

import sys
sys.path.append("..")
import geocaret.lib as lib

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


def simplify_reservoir(r_ftc, c_dam_id_str):
    r_geometry = r_ftc.geometry()

    def extract_polygons(feat):

        polyFeat = ee.Geometry.Polygon(ee.Geometry(feat).coordinates())
        polyFeat = ee.Feature(polyFeat).set("area_m", polyFeat.area(**{"maxError": 1}))

        return polyFeat

    # Simplify reservoir geometry (outer boundary)
    r_all_geometries = r_geometry.geometries()
    r_polygons = ee.FeatureCollection(r_all_geometries.map(extract_polygons))

    properties = ["area_m"]
    largest_area = r_polygons.reduceColumns(
        **{"reducer": ee.Reducer.max(), "selectors": properties}
    ).get("max")

    outer_boundary = r_polygons.filter(ee.Filter.eq("area_m", largest_area))

    # First OK; used to select largest feature
    sr_geometry = outer_boundary.first().geometry()

    sr_vector = ee.FeatureCollection(ee.Feature(sr_geometry))
    # ==========================================================================
    # Export simplified reservoir
    # ==========================================================================

    if cfg.exportSimplifiedReservoir == True:
        msg = "Exporting simplified reservoir"

        try:
            logger.info(f"{msg} {c_dam_id_str}")
            export.export_ftc(sr_vector, c_dam_id_str, "simple_reservoir_vector")

        except Exception as error:
            logger.exception(f"{msg} {c_dam_id_str}")

    return ee.FeatureCollection(ee.Feature(sr_geometry))


def batch_delineate_reservoirs(c_dam_ids):

    for c_dam_id in c_dam_ids:

        c_dam_id_str = str(c_dam_id)

        snapped_point_name = cfg.ps_geocaret_folder + "/" + "PS_" + c_dam_id_str

        # First OK; single feature
        damFeat = ee.FeatureCollection(snapped_point_name).first()

        catchmentAssetName = cfg.ps_geocaret_folder + "/" + "C_" + c_dam_id_str
        catchmentVector = ee.FeatureCollection(catchmentAssetName)

        if c_dam_id in mtr.existing_dams:
            landcover_delineation_file_str = str(
                mtr.id_landcover_delineation_file_lookup[c_dam_id]
            )
            reservoirVector = delineate_existing_reservoir(
                catchmentVector, c_dam_id_str, landcover_delineation_file_str
            )
        else:
            reservoirVector = delineate_future_reservoir(catchmentVector, c_dam_id_str)

        # ==========================================================================
        # Export reservoir
        # ==========================================================================

        # [5] Make catchment shape file (i) Find pixels
        msg = "Exporting reservoir vector"

        try:
            logger.info(f"{msg} {c_dam_id_str}")
            if cfg.exportReservoirVector == True:
                reservoirVectorFeat = ee.Feature(reservoirVector)
                reservoirVectorFeat = reservoirVectorFeat.copyProperties(
                    **{"source": damFeat, "exclude": ["ancestor_ids"]}
                )

                export.export_ftc(
                    ee.FeatureCollection(ee.Feature(reservoirVectorFeat)),
                    c_dam_id_str,
                    "reservoir_vector",
                )

        except Exception as error:
            logger.exception(f"{msg} {c_dam_id_str}")
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue


def impute_power_capacity(dam_height, turbine_efficiency, plant_depth, mad_m3_pers):

    # turbine efficiency  * discharge * gravity acceleration * water density
    denominator = (
        turbine_efficiency.divide(100)
        .multiply(mad_m3_pers)
        .multiply(9.81)
        .multiply(1000)
    )
    calc_power_capacity = dam_height.add(plant_depth).multiply(denominator).divide(1e6)

    return calc_power_capacity


def impute_dam_height(power_capacity, turbine_efficiency, plant_depth, mad_m3_pers):

    # turbine efficiency  * discharge * gravity acceleration * water density
    denominator = (
        turbine_efficiency.divide(100)
        .multiply(mad_m3_pers)
        .multiply(9.81)
        .multiply(1000)
    )
    calc_dam_height = (
        power_capacity.multiply(1e6).divide(denominator).subtract(plant_depth)
    )
    calc_dam_height_rounded = calc_dam_height.multiply(1000).round().divide(1000)

    return calc_dam_height_rounded


def delineate_future_reservoir(catchmentVector, c_dam_id_str):

    if debug_mode == True:
        cfg.exportWaterbodies = True
        cfg.exportReservoirPixels = True

    # ============================================================================
    # Load Source Data
    # ============================================================================
    if cfg.resHydroDEM == True:
        DEM = ee.Image(lib.get_public_asset("hydrosheds") + cfg.hydrodataset + "CONDEM").rename(
            ["elevation"]
        )
    else:
        DEM = ee.Image(lib.get_public_asset("nasa_srtm"))

    # First() used as these are collection level properties, duplicated
    catchFeat = catchmentVector.first()

    # ============================================================================
    # Get dam elevation
    # ============================================================================
    snapped_dam_longitude = ee.Number(catchFeat.get("ps_lon"))
    snapped_dam_latitude = ee.Number(catchFeat.get("ps_lat"))

    snapped_dam_point_location = ee.Geometry.Point(
        snapped_dam_longitude, snapped_dam_latitude
    )

    raw_dam_longitude = ee.Number(catchFeat.get("raw_lon"))
    raw_dam_latitude = ee.Number(catchFeat.get("raw_lat"))

    raw_dam_point_location = ee.Geometry.Point(raw_dam_longitude, raw_dam_latitude)

    # Dam location
    if cfg.delineate_snapped == True:
        analysis_dam_point_location = snapped_dam_point_location
    else:
        analysis_dam_point_location = raw_dam_point_location

    projection = ee.Image(DEM).projection()

    # expected SCALE = 30
    SCALE = projection.nominalScale()

    # Minimum elevation at dam site
    dam_elevation = DEM.reduceRegion(
        **{
            "reducer": ee.Reducer.min(),
            "geometry": analysis_dam_point_location,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("elevation")

    raw_dam_elevation = DEM.reduceRegion(
        **{
            "reducer": ee.Reducer.min(),
            "geometry": raw_dam_point_location,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("elevation")

    snapped_dam_elevation = DEM.reduceRegion(
        **{
            "reducer": ee.Reducer.min(),
            "geometry": snapped_dam_point_location,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("elevation")

    # ==============================================================================
    # Impute water elevation and track provenance
    # ==============================================================================

    fsl_masl = ee.Number(catchFeat.get("t_fsl_masl"))
    dam_height = ee.Number(catchFeat.get("t_dam_height"))
    turbine_efficiency = ee.Number(catchFeat.get("t_turbine_efficiency"))
    power_capacity = ee.Number(catchFeat.get("power_capacity"))
    plant_depth = ee.Number(catchFeat.get("t_plant_depth"))
    # String to 9dp; to nearest mm3
    mad_m3_pers = ee.Number.parse(catchFeat.get("c_mad_m3_pers"))

    # Impute dam height
    imputed_dam_height = ee.Algorithms.If(
        dam_height.eq(-999),
        impute_dam_height(power_capacity, turbine_efficiency, plant_depth, mad_m3_pers),
        dam_height,
    )

    # Impute water level
    water_elevation = ee.Algorithms.If(
        fsl_masl.eq(-999), ee.Number(dam_elevation).add(imputed_dam_height), fsl_masl
    )

    # Imputed water level provence
    # 0 - User input fsl (masl)
    # 1 - User input dam height
    # 2 - Dam height estimated from power capacity (known turbine efficiency)
    # 3 - Dam height estimated from power capacity (unknown turbine efficiency)
    # 4 - NA (commissioned dam)

    turbine_efficiency_prov = catchFeat.get("turbine_efficiency_prov")

    imputed_dam_height_prov = ee.Algorithms.If(
        dam_height.eq(-999), ee.Number(2).add(turbine_efficiency_prov), 1
    )

    # Impute water level
    imputed_water_elevation_prov = ee.Algorithms.If(
        fsl_masl.eq(-999), imputed_dam_height_prov, 0
    )

    if debug_mode == True:
        print(
            "\n [delineate_future_reservoir] fsl_masl",
            fsl_masl.getInfo(),
        )
        print(
            "\n [delineate_future_reservoir] dam_height",
            dam_height.getInfo(),
        )
        print(
            "\n [delineate_future_reservoir] turbine_efficiency",
            turbine_efficiency.getInfo(),
        )
        print(
            "\n [delineate_future_reservoir] plant_depth",
            plant_depth.getInfo(),
        )
        print(
            "\n [delineate_future_reservoir] mad_m3_pers",
            mad_m3_pers.getInfo(),
        )
        print(
            "\n [delineate_future_reservoir] imputed_dam_height",
            imputed_dam_height.getInfo(),
        )
        print(
            "\n [delineate_future_reservoir] imputed_dam_height_prov",
            imputed_dam_height_prov.getInfo(),
        )
        print(
            "\n [delineate_future_reservoir] water_elevation", water_elevation.getInfo()
        )
        print(
            "\n [delineate_future_reservoir] imputed_water_elevation_prov",
            water_elevation.getInfo(),
        )

    # ============================================================================
    #  Set user-specified parameters
    # ============================================================================

    # print("Water elevation:",water_elevation)
    # Pixels of lower elevation than water level are inundated
    catchment_geometry = catchmentVector.geometry()
    inundated_area = DEM.clip(catchment_geometry).lte(ee.Number(water_elevation))
    inundated_area = inundated_area.selfMask()

    # ==========================================================================
    # Export inundated pixels
    # ==========================================================================

    if cfg.exportReservoirPixels == True:
        msg = "Exporting inundated pixels"

        try:
            logger.info(f"{msg} {c_dam_id_str}")
            export.export_image(inundated_area, c_dam_id_str, "waterbodies_pixels")

        except Exception as error:
            logger.exception(f"{msg} {c_dam_id_str}")

    # logger.debug("\n [delineate_future_reservoir] water_elevation", water_elevation.getInfo())

    water_bodies = inundated_area.reduceToVectors(
        **{
            "reducer": ee.Reducer.countEvery(),
            "geometry": catchment_geometry,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    )

    # ==========================================================================
    # Export waterbodies
    # ==========================================================================

    if cfg.exportWaterbodies == True:
        msg = "Exporting waterbodies vector"

        try:
            logger.info(f"{msg} {c_dam_id_str}")
            export.export_ftc(water_bodies, c_dam_id_str, "waterbodies_vector")

        except Exception as error:
            logger.exception(f"{msg} {c_dam_id_str}")

    if debug_mode == True:
        print("\n [delineate_future_reservoir] water_bodies", water_bodies.getInfo())
        print(
            "\n [delineate_future_reservoir] dam_point_location",
            analysis_dam_point_location.getInfo(),
        )

    # logger.debug("\n [delineate_future_reservoir] main_water_body", main_water_body.getInfo())
    # ==============================================================================
    # Select water body that intersects the dam point
    # ==============================================================================

    # Filters out the water bodies that don't intersect the dam
    reservoirVector = ee.FeatureCollection(
        water_bodies.filterBounds(analysis_dam_point_location)
    ).first()

    if debug_mode == True:
        print(
            "\n [delineate_existing_reservoir] raw_dam_*",
            raw_dam_longitude.getInfo(),
            raw_dam_latitude.getInfo(),
        )
        print(
            "\n [delineate_existing_reservoir] raw_dam_point_location",
            raw_dam_point_location.getInfo(),
        )
        print(
            "\n [delineate_future_reservoir] reservoirVector", reservoirVector.getInfo()
        )
        print(
            "\n [delineate_future_reservoir] water_elevation", water_elevation.getInfo()
        )

    imputed_water_elevation_prov_str = ee.Number(imputed_water_elevation_prov).format(
        "%.0f"
    )

    dam_elevation_str = ee.Number(dam_elevation).format("%.3f")
    snapped_dam_elevation_str = ee.Number(snapped_dam_elevation).format("%.3f")
    raw_dam_elevation_str = ee.Number(raw_dam_elevation).format("%.3f")

    water_elevation_str = ee.Number(water_elevation).format("%.0f")

    reservoirVector = ee.Feature(reservoirVector).set(
        "r_imputed_water_elevation", water_elevation_str
    )
    reservoirVector = ee.Feature(reservoirVector).set(
        "r_imputed_water_elevation_prov", imputed_water_elevation_prov_str
    )
    reservoirVector = ee.Feature(reservoirVector).set(
        "d_dam_elevation_analysis", dam_elevation_str
    )
    reservoirVector = ee.Feature(reservoirVector).set(
        "d_dam_elevation_raw", raw_dam_elevation_str
    )
    reservoirVector = ee.Feature(reservoirVector).set(
        "d_dam_elevation_snapped", snapped_dam_elevation_str
    )

    # logger.debug("\n [delineate_future_reservoir] reservoirVector", reservoirVector.getInfo())

    return reservoirVector


def delineate_existing_reservoir(
    catchmentVector, c_dam_id_str, landcover_delineation_file_str
):

    if debug_mode == True:
        cfg.exportWaterbodies = True

    # ============================================================================
    # Get Commission Year Information
    # ============================================================================
    catchFeat = catchmentVector.first()

    # ============================================================================
    # Choose Landcover Data Sources
    # ============================================================================

    LANDCOVER_ESA = ee.Image(landcover_delineation_file_str)

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

    catchment_geometry = catchmentVector.geometry()
    inundated_area = LANDCOVER_IHA.clip(catchment_geometry).eq(7)
    inundated_area = inundated_area.selfMask()

    # ==========================================================================
    # Export inundated pixels
    # ==========================================================================

    if cfg.exportReservoirPixels == True:
        msg = "Exporting inundated pixels"

        try:
            logger.info(f"{msg} {c_dam_id_str}")
            export.export_image(inundated_area, c_dam_id_str, "waterbodies_pixels")

        except Exception as error:
            logger.exception(f"{msg} {c_dam_id_str}")

    projection = ee.Image(LANDCOVER_IHA).projection()

    # SCALE > NATIVE USED (REDUCE RISK OF RESERVOIR
    # CONSISTING OF DIAGONALLY CONNECTED POLYS WHICH
    # PREVENTS IDENTIFICATION OF A CLEAR PERIMETER)
    SCALE = ee.Number(projection.nominalScale()).add(50)

    water_bodies = inundated_area.reduceToVectors(
        **{
            "reducer": ee.Reducer.countEvery(),
            "geometry": catchment_geometry,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    )

    # ==========================================================================
    # Export waterbodies
    # ==========================================================================

    if cfg.exportWaterbodies == True:
        msg = "Exporting waterbodies vector"

        try:
            logger.info(f"{msg} {c_dam_id_str}")
            export.export_ftc(water_bodies, c_dam_id_str, "waterbodies_vector")

        except Exception as error:
            logger.exception(f"{msg} {c_dam_id_str}")

    if debug_mode == True:
        print("\n [delineate_existing_reservoir] water_bodies", water_bodies.getInfo())

    # ==============================================================================
    # Select water body that intersects the dam point
    # ==============================================================================

    raw_dam_longitude = ee.Number(catchFeat.get("raw_lon"))
    raw_dam_latitude = ee.Number(catchFeat.get("raw_lat"))

    snapped_dam_longitude = ee.Number(catchFeat.get("ps_lon"))
    snapped_dam_latitude = ee.Number(catchFeat.get("ps_lat"))

    snapped_dam_point_location = ee.Geometry.Point(
        snapped_dam_longitude, snapped_dam_latitude
    )

    raw_dam_point_location = ee.Geometry.Point(raw_dam_longitude, raw_dam_latitude)

    # ============================================================================
    # Get dam elevation
    # ============================================================================
    if cfg.resHydroDEM == True:
        DEM = ee.Image(lib.get_public_asset("hydrosheds") + cfg.hydrodataset + "CONDEM").rename(
            ["elevation"]
        )
    else:
        DEM = ee.Image(lib.get_public_asset("nasa_srtm"))

    projection = ee.Image(DEM).projection()

    # expected SCALE = 30 or 90 (hydro DEM)
    SCALE = projection.nominalScale()

    # Dam location
    if cfg.delineate_snapped == True:
        analysis_dam_point_location = snapped_dam_point_location
    else:
        analysis_dam_point_location = raw_dam_point_location

    dam_elevation = DEM.reduceRegion(
        **{
            "reducer": ee.Reducer.min(),
            "geometry": analysis_dam_point_location,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("elevation")

    raw_dam_elevation = DEM.reduceRegion(
        **{
            "reducer": ee.Reducer.min(),
            "geometry": raw_dam_point_location,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("elevation")

    snapped_dam_elevation = DEM.reduceRegion(
        **{
            "reducer": ee.Reducer.min(),
            "geometry": snapped_dam_point_location,
            "scale": SCALE,
            "maxPixels": 2e11,
        }
    ).get("elevation")

    # Filters in water bodies that intersect the raw or snapped dam location
    if cfg.delineate_snapped == True:
        # Precedence to any water body intersecting snapped dam location
        reservoirVector = ee.FeatureCollection(
            water_bodies.filterBounds(snapped_dam_point_location),
            water_bodies.filterBounds(raw_dam_point_location),
        ).first()
    else:
        # Precedence to any water body intersecting raw dam location
        reservoirVector = ee.FeatureCollection(
            water_bodies.filterBounds(raw_dam_point_location),
            water_bodies.filterBounds(snapped_dam_point_location),
        ).first()

    if debug_mode == True:
        print(
            "\n [delineate_existing_reservoir] raw_dam_*",
            raw_dam_longitude.getInfo(),
            raw_dam_latitude.getInfo(),
        )
        print(
            "\n [delineate_existing_reservoir] raw_dam_point_location",
            raw_dam_point_location.getInfo(),
        )
        print(
            "\n [delineate_existing_reservoir] analysis_point_location",
            analysis_dam_point_location.getInfo(),
        )
        print(
            "\n [delineate_existing_reservoir] reservoirVector",
            reservoirVector.getInfo(),
        )

    water_elevation_str = "NA"
    imputed_water_elevation_prov_str = ee.Number(4).format("%.0f")

    dam_elevation_str = ee.Number(dam_elevation).format("%.3f")
    snapped_dam_elevation_str = ee.Number(snapped_dam_elevation).format("%.3f")
    raw_dam_elevation_str = ee.Number(raw_dam_elevation).format("%.3f")

    reservoirVector = ee.Feature(reservoirVector).set(
        "r_imputed_water_elevation", water_elevation_str
    )
    reservoirVector = ee.Feature(reservoirVector).set(
        "r_imputed_water_elevation_prov", imputed_water_elevation_prov_str
    )

    reservoirVector = ee.Feature(reservoirVector).set(
        "d_dam_elevation_analysis", dam_elevation_str
    )
    reservoirVector = ee.Feature(reservoirVector).set(
        "d_dam_elevation_raw", raw_dam_elevation_str
    )
    reservoirVector = ee.Feature(reservoirVector).set(
        "d_dam_elevation_snapped", snapped_dam_elevation_str
    )
    # logger.debug("\n [delineate_existing_reservoir] reservoirVector", reservoirVector.getInfo())

    return reservoirVector


# ==============================================================================
# Development
# ==============================================================================


if __name__ == "__main__":

    print("Running in dedug mode...")

    # Debugging reservoir delineation failures
    # Power capacity only; Affected IDs (17)
    # 1183 1293 1313 993 1323
    catchmentAssetName = "users/kkh451/XHEET/FINAL_20230204-2106/C_1052"
    catchment_ftc = ee.FeatureCollection(catchmentAssetName)
    print(catchment_ftc.getInfo())
    # reservoirVector = delineate_existing_reservoir(
    #     catchment_ftc,
    #     "1052",
    #     "projects/ee-future-dams/assets/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-1992-v2-0-7cds",
    # )
    # print(reservoirVector.getInfo())

    # catchmentAssetName = "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/C_1201"
    # catchment_ftc = ee.FeatureCollection(catchmentAssetName)
    # reservoirVector = delineate_future_reservoir(catchment_ftc, "1201")
    # print(reservoirVector.getInfo())
