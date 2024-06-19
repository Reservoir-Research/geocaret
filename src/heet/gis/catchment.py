""" """
import pathlib
import re
import ee
import yaml
import heet.data as dta
import heet.export
import heet.monitor as mtr
import heet.uihi_watershed as watershed
import heet.log_setup
import heet.assets
from heet.utils import load_packaged_data

debug_mode = False


assets = heet.assets.EmissionAssets()

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)

config_file: pathlib.PosixPath = load_packaged_data(
    './config/parameters.yaml')
with open(config_file, "r", encoding="utf8") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)['export']

# ==============================================================================
#  Functions
# ==============================================================================


def vectorise_catchment(damFeat, watershedDptsFtc, c_dam_id_str):

    if debug_mode:
        global rpts
        global start_id
        global ancestor_ids
        global upstream_ids
        global upstream_catchments
        global catch_bbox
        global required_ids
        global ancestor_catchments
        global ancestor_catchments_union
        global ancestor_catchments_union_dissolved
        global ancestor_catchments_ftc
        global fixed_points
        global catchment_points
        global c_geometry
        global c_boundaries_geom
        global new_geometry

        print("[DEBUG] [vectorise_catchment] Vectorising catchment")

    hydrobasins_12 = dta.HYDROBASINS12
    dd_grid_coord = dta.WDRAINAGEDIRECTION

    rpts = watershedDptsFtc
    start_id = ee.Number(damFeat.get('outlet_subcatch_id'))
    ancestor_ids = ee.List(ee.String(damFeat.get('ancestor_ids')).decodeJSON())

    # ==================================================================
    # Construct the full approximate catchment
    # ==================================================================

    #  Hydrobasins Approximate catchment (full dam subbasin and all upsteam)
    upstream_ids = ee.List(ancestor_ids).add(start_id)

    upstream_catchments = (hydrobasins_12
                           .filter(ee.Filter.inList('HYBAS_ID', upstream_ids))
                           )

    catch_bbox = upstream_catchments.geometry().bounds()

    # ==================================================================
    # Construct the full upstream catchment (with a double boundary)
    # ==================================================================

    # Define geometry of upstream catchments
    ancestor_catchments = (hydrobasins_12
                           .filter(ee.Filter.inList('HYBAS_ID', ancestor_ids)))

    ancestor_catchments_union = ee.FeatureCollection(ancestor_catchments).union(1)

    ancestor_catchments_union_dissolved = (
        ancestor_catchments_union.geometry().dissolve(**{'maxError': 1})
    )

    # Start preprocessing of ancestor_catchments_union_dissolved
    # Get coordinates of ancestor catchments
    coords_list = (ee.Feature(ancestor_catchments_union_dissolved)
                   .geometry()
                   .coordinates()
                   )

    # Separate coordinates into subpolygons
    # Sort in descending order of area
    def coords_to_subpolys(coords):
        subpolyFeat = ee.Feature(ee.Geometry.Polygon(coords))
        subpolyFeat = subpolyFeat.set('area_m', subpolyFeat.area(**{'maxError': 1}))
        return subpolyFeat

    sub_polygons_list = coords_list.map(coords_to_subpolys)
    sub_polygons_ftc = ee.FeatureCollection(sub_polygons_list).sort('area_m', False)

    # Create lists of:
    # - All subpolygons/boundary lines
    # - The largest subpolygon (the outer border of the catchment)
    # - All othehr subpolygons (boundaries within catchment e.g. end. basins)
    a_boundary_list = sub_polygons_ftc.toList(100000, 0)
    a_outer_list = sub_polygons_ftc.toList(100000, 0).get(0)
    a_inner_list = sub_polygons_ftc.toList(100000, 1)

    # Buffer the boundary lines:
    # - outer boundary by -1000
    # - inner boundaries by +1000
    # This will allow us to extract pixels around the edge of the catchment

    a_outer_buffered_list = ee.List([a_outer_list]).map(
        lambda feat: ee.Feature(feat).buffer(-1000)).get(0)

    a_inner_buffered_list = a_inner_list.map(
        lambda feat: ee.Feature(feat).buffer(+1000))

    # Combine outer and inner buffered lists
    a_outer_list = ee.List([a_outer_list]).cat(a_inner_buffered_list)
    a_inner_list = ee.List([a_outer_buffered_list]).cat(a_inner_list)
    a_pairs_list = a_outer_list.zip(a_inner_list)

    # Get paired differences
    def geom_diff(pfeat):

        outer_geom = ee.Feature(ee.List(pfeat).get(0)).geometry()
        inner_inner = ee.Feature(ee.List(pfeat).get(1)).geometry()

        dgeom = outer_geom.difference(
            **{'right': inner_inner, 'maxError': 1})

        return ee.Feature(dgeom)

    a_diffs_list = a_pairs_list.map(geom_diff)
    # We have a doubled boundary shape of the upstream catchment that
    # allows us to select points/pixels around the interior edges of the
    # catchement
    ancestor_catchments_ftc = ee.FeatureCollection(a_diffs_list)

    # ==================================================================
    # Get ~edge pixels and pt equivalent
    # ==================================================================
    proj = dd_grid_coord.select([0]).projection()
    dd_grid_coord_reduced = dd_grid_coord.clip(ee.Feature(catch_bbox).geometry())
    fixed_points = (dd_grid_coord_reduced
                    .sampleRegions(**{
                        "collection": ancestor_catchments_ftc,
                        "projection": proj,
                        "geometries": False
                    }))

    # Combine main catchment edge pts and watershed detected pts
    catchment_points = ee.Algorithms.If(
        ee.Number(ee.List(ancestor_ids).length()).eq(0),
        ee.FeatureCollection(rpts),
        ee.FeatureCollection(ee.List([fixed_points, rpts])).flatten()
    )

    # ==================================================================
    # Convert catchment pixels to raster
    # ==================================================================

    outputImgInput = ee.Image(dd_grid_coord).clip(catch_bbox).select(["grid_id"])

    required_ids = ee.FeatureCollection(catchment_points).aggregate_array("grid_id")

    outputImg = outputImgInput.remap(**{
        'from': required_ids,
        'to': ee.List.repeat(1, required_ids.size()),
        'defaultValue': 0
    })

    mask = outputImg.eq(1)
    catchmentPixels = outputImg.updateMask(mask)

    if config['export_catchment_pixels']:
        heet.export.export_image(
            catchmentPixels, c_dam_id_str, "catchment_pixels")

    # ==================================================================
    # Convert watershed raster to vector
    # ==================================================================

    projection = ee.Image(catchmentPixels).projection()
    OUTPUT_SCALE = projection.nominalScale()

    catchmentVector = catchmentPixels.reduceToVectors(**{
        'reducer': ee.Reducer.countEvery(),
        'geometry': catch_bbox,
        'scale': OUTPUT_SCALE,
        'geometryType': 'polygon',
        'maxPixels': 2e10
    })

    catchmentVectorGeom = catchmentVector.geometry()

    # heet.export.export_ftc(ee.FeatureCollection(catchmentVectorGeom), c_dam_id_str, "debugging_vector")

    # catchment vector has double boundaries as a result of working only
    # with edge pixels for the upstream catchments
    # We must remove the inner boundaries

    c_geometry = catchmentVectorGeom

    def extract_polygons(feat):
        """ """
        polyFeat = ee.Geometry.Polygon(ee.Geometry(feat).coordinates())
        polyFeat = ee.Feature(polyFeat).set('area_m', polyFeat.area(
            **{'maxError': 1}))
        return polyFeat

    c_all_geometries_list = c_geometry.geometries()
    c_polygons_ftc = ee.FeatureCollection(
        c_all_geometries_list.map(extract_polygons)).sort('area_m', False)

    c_outer_list = c_polygons_ftc.toList(100000, 0)
    c_inner_list = c_polygons_ftc.toList(100000, 1)

    # Extract inner boundaries
    def extract_inner_bound(polyFeat):
        """ """
        coords_list = ee.Feature(polyFeat).geometry().coordinates()
        sub_polygons_list = coords_list.map(coords_to_subpolys)
        sub_polygons_ftc = ee.FeatureCollection(sub_polygons_list).sort(
            'area_m', False)
        # Select second largest polygon
        inner_poly_boundary = sub_polygons_ftc.toList(100000).get(1)
        return inner_poly_boundary

    c_inner_boundaries_list = c_inner_list.map(extract_inner_bound)
    c_inner_boundaries_ftc = ee.FeatureCollection(c_inner_boundaries_list).union(1)

    # Extract outer boundaries
    def extract_outer_bound(polyFeat):
        """ """
        coords_list = ee.Feature(polyFeat).geometry().coordinates()
        sub_polygons_list = coords_list.map(coords_to_subpolys)
        sub_polygons_ftc = ee.FeatureCollection(sub_polygons_list).sort(
            'area_m', False)
        # Select largest polygon
        outer_poly_boundary = sub_polygons_ftc.toList(100000).get(0)

        return outer_poly_boundary

    c_outer_boundaries_list = ee.List(
        ee.List(c_outer_list).map(extract_outer_bound).get(0))
    c_outer_boundaries_ftc = ee.FeatureCollection([c_outer_boundaries_list])
    # Extract difference between the boundaries (final geometry)
    c_inner_boundaries_geom = c_inner_boundaries_ftc.geometry()
    c_outer_boundaries_geom = c_outer_boundaries_ftc.geometry()
    c_boundaries_geom = c_outer_boundaries_geom.difference(
        **{'right': c_inner_boundaries_geom, 'maxError': 1})

    new_geometry = ee.Algorithms.If(
        ee.Number(ee.List(ancestor_ids).length()).eq(0),
        catchmentVectorGeom,
        c_boundaries_geom)

    return new_geometry


def detected_watershed_pts(
        watershed_pt_indices,
        watershedCptsFtc,
        watershedGridFeat):
    """ """
    grid_id_list = ee.Array(watershedGridFeat.get(
        'grid_id')).toList().flatten()
    # ==================================================================
    # Post process the detected catchment area (points)
    # ==================================================================
    #
    # NB: filtering within sub-catch removed
    #
    watershed_pt_ids = ee.List(watershed_pt_indices).map(
        lambda e: grid_id_list.get(e))
    # Keep points inside subcatchment
    watershedDptsFtc = watershedCptsFtc.filter(ee.Filter.inList(
        "grid_id", watershed_pt_ids))
    return watershedDptsFtc


def rapid_catchment_cs(watershedGridFeat, c_dam_id):
    """ """
    search_area_arr = ee.Array(watershedGridFeat.get('remapped'))
    snapped_point_index = ee.Feature(watershedGridFeat).get(
        'snapped_point_index')
    # c_snapped_point_index = str(snapped_point_index.getInfo())
    # logger.debug("[rapid_catchment_cs] snapped_point_index", c_snapped_point_index )
    # ==================================================================
    # Find the catchment area (points)
    # ==================================================================
    # Define catchment search inputs
    # (i) Index of outlet point when 2d search grid is flatten to 1d array
    s = int(snapped_point_index.getInfo())
    outlet_pixels = [s, ]
    # (ii) 2D array of drainage directions
    logger.debug("[rapid_catchment_cs] Inputs prepared")
    watershed_image_data_2d = ee.Array(search_area_arr).getInfo()
    # Run catchment search
    # Returns 1d indices of pixels on search grid which belong to the catchment
    result = watershed.find_watershed_cs(watershed_image_data_2d, outlet_pixels)
    return result


def watershed_search_area(damFeat):
    """ """
    # Prepare data sources
    hydrobasins_12 = dta.HYDROBASINS12
    outlet_point = ee.Feature(damFeat).geometry()
    # ==================================================================
    # Define watershed search area (geometry)
    # ==================================================================
    # Define catchment search area
    # (Bounding box of outlet point sub-basin + buffer of hydrobasins 12
    # nominal scale )
    # Get outlet's subcatchment
    # Hydrobasins 12 nominal scale; 15 Arc seconds ~500m at equator
    hydrobasins_12_nscale = 500
    outlet_subcatch = hydrobasins_12.filterBounds(outlet_point)
    buffer_distance = ee.Number(hydrobasins_12_nscale).multiply(2)
    search_area = outlet_subcatch.geometry().buffer(buffer_distance).bounds()

    return search_area


def candidate_watershed_pts(damFeat):
    """ """
    dd_grid_coord = dta.WDRAINAGEDIRECTION
    search_area = watershed_search_area(damFeat)
    # Extract search area drainage directions to feature collection
    outlet_subcatch_ftc = ee.FeatureCollection(search_area)
    proj = dd_grid_coord.select([0]).projection()
    search_area_ftc = (dd_grid_coord.sampleRegions(**{
        "collection": outlet_subcatch_ftc,
        "projection": proj,
        "geometries": True}))
    # Check grid is valid (all unique id)
    grid_id_list = search_area_ftc.aggregate_array("grid_id")
    n_grid_ids = ee.Number(grid_id_list.distinct().length())
    n_grid_points = ee.Number(grid_id_list.length())

    search_area_ftc = search_area_ftc.set(
        "valid_grid",
        ee.Algorithms.If(n_grid_ids.eq(n_grid_points), True, False))

    # TODO Check if search area is within pixel size for analysis (<=262144)
    # logger.debug("[candidate_watershed_pts]", grid_id_list.getInfo()[0:10])
    # logger.debug(f'[candidate_watershed_pts] Number of grid ids {n_grid_ids.getInfo()}')
    # logger.debug(f'[candidate_watershed_pts] Number of grid points {n_grid_points.getInfo()}')

    return search_area_ftc


def watershed_search_grid(damFeat):
    """ """
    dd_grid_coord = dta.WDRAINAGEDIRECTION
    hydrobasins_12 = dta.HYDROBASINS12
    search_area = watershed_search_area(damFeat)
    # Extract search area drainage directions to numeric array
    outlet_point = ee.Feature(damFeat).geometry()
    outlet_subcatch = hydrobasins_12.filterBounds(outlet_point)
    sdd_grid_coord = dd_grid_coord.clip(outlet_subcatch.geometry())
    # NB: lat lon removed from properies list
    # Default value of 999 is used to ensure that search does not exit subcatchment
    search_area_ft = (sdd_grid_coord.sampleRectangle(
        **{"region": search_area,
           "defaultValue": 999,
           "properties": ee.List(
            ["gid", "remapped", "latitude", "longitude"])}))

    # Check grid is valid
    # [!IMPORTANT] NAME MIGHT BE grid_id or gid depending on evaluation (EE bug?)
    # Id of masked pixels (999) is set to 999 so must be filtered out

    grid_id_list = ee.Array(search_area_ft.get('grid_id')).toList().flatten(
        ).filter(ee.Filter.neq('item', 999))

    n_grid_ids = ee.Number(grid_id_list.distinct().length())
    n_grid_points = ee.Number(grid_id_list.length())

    search_area_ft = search_area_ft.set(
        "valid_grid",
        ee.Algorithms.If(n_grid_ids.eq(n_grid_points), True, False)
    )

    # logger.debug("[watershed_search_grid]", grid_id_list.getInfo()[0:10])
    # logger.debug(f'[watershed_search_grid] Number of grid ids {n_grid_ids.getInfo()}')
    # logger.debug(f'[watershed_search_grid] Number of grid pixels {n_grid_points.getInfo()}')

    return search_area_ft


def watershed_grid_index(damFeat, watershedCptsFtc, watershedGridFeat):
    """ """
    outlet_point = ee.Feature(damFeat).geometry()
    grid_id_list = ee.Array(watershedGridFeat.get('grid_id')).toList().flatten()
    # Get 1d position (index) of outlet point on search grid
    candidate_points = watershedCptsFtc.map(
        lambda feat: feat.set('tdist', feat.distance(outlet_point, 1)))
    # Python API won't accept keyword arguments (property/ascending)
    snapped_point = candidate_points.sort('tdist', True).first()
    snapped_point_id = ee.Number(ee.Feature(snapped_point).get("grid_id"))
    snapped_point_index = grid_id_list.indexOf(snapped_point_id)

    return snapped_point_index


def batch_delineate_nicatchments(c_dam_ids):
    """ """
    for c_dam_id in c_dam_ids:
        dam_id = ee.Number(c_dam_id)
        c_dam_id_str = str(c_dam_id)
        catchment_vector = assets.ps_heet_folder + "/" + "C_" + c_dam_id_str
        reservoir_vector = assets.ps_heet_folder + "/" + "R_" + c_dam_id_str
        catch_geom = ee.FeatureCollection(catchment_vector).geometry()
        res_geom = ee.FeatureCollection(reservoir_vector).geometry()
        # Properties
        core_properties = ee.List([
            'country',
            'dam_height',
            'dam_lat',
            'dam_lon',
            'id',
            'main_basin',
            'name',
            'plant_depth'
            'power_capacity'
            'river'
            'turbine_efficiency'])

        niCatchFeat = ee.Feature(catch_geom.difference(res_geom))
        # First OK for property copying
        catchFeat = ee.FeatureCollection(catchment_vector).first()
        niCatchFeat = niCatchFeat.copyProperties(catchFeat, core_properties)

        # ==========================================================================
        # Export non-inundated catchment
        # ==========================================================================

        # [5] Make catchment shape file (i) Find pixels
        msg = "Exporting non-inundated catchment vector"

        try:
            logger.info(f'{msg} {c_dam_id_str}')
            if config['export_ni_catchment_vector']:
                heet.export.export_ftc(ee.FeatureCollection(ee.Feature(
                    niCatchFeat)), c_dam_id_str, "ni_catchment_vector")
        except Exception as error:
            logger.error(f'{msg} {c_dam_id_str}')
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue


def batch_delineate_catchments(c_dam_ids):
    """ """
    if debug_mode:
        global snapped_point_name
        global damFeat
        global watershedCptsFtc
        global watershedGridFeat
        global watershed_pt_indices
        global watershedDptsFtc
        global catchmentVectorGeom
        global catchmentVectorFeat

    for c_dam_id in c_dam_ids:
        logger.debug(
            f"[batch_delineate_catchments] Processing dam: {c_dam_id}")

        dam_id = ee.Number(c_dam_id)
        c_dam_id_str = str(c_dam_id)
        snapped_point_name = assets.ps_heet_folder + "/" + "PS_" + c_dam_id_str
        # First OK (always single feature)
        damFeat = ee.FeatureCollection(snapped_point_name).first()

        # ==========================================================================
        # Prepare inputs for local catchment search
        # ==========================================================================

        # [1] Generate ftc of Watershed grid points
        msg = """Defining feature collection of candidate watershed points within
        outlet pt sub-basin"""

        try:
            logger.info(f'{msg} {c_dam_id_str}')
            watershedCptsFtc = candidate_watershed_pts(damFeat)

        except Exception as error:
            logger.error(f'{msg} {c_dam_id_str}')
            logger.debug(f"[batch_delineate_catchments] Exception {error}")
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue
        # [1-i] Export ftc of Watershed grid points
        msg = "Exporting feature collection of candidate watershed points within \
               outlet pt sub-basin"
        try:
            logger.info(f'{msg} {c_dam_id_str}')
            if config['export_watershed_cpts']:
                heet.export.export_ftc(
                    watershedCptsFtc, c_dam_id_str, "candidate_watershed_pts")

        except Exception as error:
            logger.error(f'{msg} {c_dam_id_str}')
            logger.debug(f"[batch_delineate_catchments] Exception {error}")
            continue

        # [2] Generate array of Watershed grid points
        msg = "Defining search array of candidate watershed points within outlet \
               pt sub-basin"
        fmsg = re.sub('\s+', ' ', msg)

        try:
            logger.info(f'{fmsg} {c_dam_id_str}')
            watershedGridFeat = watershed_search_grid(damFeat)
            watershedGridFeat.set('dam_id', dam_id)
        except Exception as error:
            logger.error(f'{msg} {c_dam_id_str}')
            logger.debug(f"[batch_delineate_catchments] Exception {error}")
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue

        # [3] Identify position of snapped dam on search grid
        msg = "Finding position of dam on watershed search grid"

        try:
            logger.info(f'{msg} {c_dam_id_str}')
            snapped_point_index = watershed_grid_index(
                damFeat, watershedCptsFtc, watershedGridFeat)
            watershedGridFeat = watershedGridFeat.set(
                'snapped_point_index', snapped_point_index)

        except Exception as error:
            logger.error(f'{msg} {c_dam_id_str}',
                         stack_info=heet.log_setup.STACK_INFO,
                         exc_info=heet.log_setup.EXC_INFO)
            logger.exception(f"[batch_delineate_catchments] Exception {error}")
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue

        # ==========================================================================
        # Refine catchment near dam
        # ==========================================================================

        # [4] Detect points that make up the catchment
        msg = "Detect points that make up the catchment"

        try:
            logger.info(f'{msg} {c_dam_id_str}')
            # Get indices of watershed points
            valid_grid = watershedGridFeat.get('valid_grid').getInfo()
            if valid_grid:
                watershed_pt_indices = rapid_catchment_cs(watershedGridFeat, c_dam_id)
            else:
                mtr.active_analyses.remove(int(c_dam_id_str))
                continue

        except Exception as error:
            logger.error(f'{msg} {c_dam_id_str}')
            logger.debug(f"[batch_delineate_catchments] Exception {error}")
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue

        # [4] Detect points that make up the catchment
        msg = "Collect detected points that make up the catchment"

        try:
            logger.info(f'{msg} {c_dam_id_str}')
            watershedDptsFtc = detected_watershed_pts(
                watershed_pt_indices, watershedCptsFtc, watershedGridFeat)

        except Exception as error:
            logger.error(f'{msg} {c_dam_id_str}')
            logger.debug(f"[batch_delineate_catchments] Exception {error}")
            continue

        # [4-i] Export ftc of detected watershed grid points
        msg = "Exporting feature collection of detected watershed points within \
               outlet pt sub-basin"

        try:
            logger.info(f'{msg} {c_dam_id_str}')

            if config['export_watershed_dpts']:
                heet.export.export_ftc(
                    watershedDptsFtc, c_dam_id_str, "detected_watershed_pts")

        except Exception as error:
            logger.error(f'{msg} {c_dam_id_str}')
            logger.debug(f"[batch_delineate_catchments] Exception {error}")
            continue

        # ==========================================================================
        # Vectorise catchments
        # ==========================================================================

        # [5] Make catchment shape file (i) Find pixels
        msg = "Making catchment vector"
        try:
            logger.info(f'{msg} {c_dam_id_str}')
            catchmentVectorGeom = vectorise_catchment(
                damFeat, watershedDptsFtc, c_dam_id_str)
        except Exception as error:
            logger.error(f'{msg} {c_dam_id_str}')

            if debug_mode:
                print("[DEBUG] [batch_delineate_catchments] Exception", error)
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue

        # ==========================================================================
        # Export catchments
        # ==========================================================================
        # [5] Make catchment shape file (i) Find pixels
        msg = "Exporting catchment vector"
        try:
            logger.info(f'{msg} {c_dam_id_str}')
            if config['export_catchment_vector']:
                catchmentVectorFeat = ee.Feature(None).setGeometry(
                    catchmentVectorGeom)
                catchmentVectorFeat = catchmentVectorFeat.copyProperties(
                    **{'source': damFeat, 'exclude': ['ancestor_ids']})
                heet.export.export_ftc(ee.FeatureCollection(ee.Feature(
                    catchmentVectorFeat)), c_dam_id_str, "catchment_vector")
        except Exception as error:
            logger.error(f'{msg} {c_dam_id_str}')
            logger.debug(f"[batch_delineate_catchments] Exception {error}")
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue

# ==============================================================================
# Development
# ==============================================================================


if __name__ == "__main__":
    print("Development run ...")
    a = heet.assets.Assets()
