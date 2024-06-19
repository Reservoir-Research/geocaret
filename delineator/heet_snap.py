""" Functions for snapping dams (point features) to the nearest river
    segment """
import logging
import heet_config as cfg
import heet_data as dta
import ee

# =============================================================================
#  Set up logger
# =============================================================================
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
#  Functions
# ==============================================================================
def buffer_points_radius(point: ee.Geometry.Point) -> ee.Feature:
    """ Creates a circle from point in EE """
    radius = cfg.jensen_search_radius
    pt_feature = ee.Feature(point)
    return pt_feature.buffer(radius)


def buffer_points_bounds(point: ee.Geometry.Point) -> ee.Feature:
    """ Creates a circle from point and adds the bounding box of the
        created geometry """
    return buffer_points_radius(point).bounds()


def jensen_snap_hydroriver(dam_feature: ee.Feature) -> ee.Feature:
    """ Takes a EE dam feature and snaps it to the nearest river segment
        in HYDRORIVERS Feature Collection """
    # Convert input argument to EE feature and extract geometry
    dam_feature = ee.Feature(dam_feature)
    dam_point = dam_feature.geometry()
    # TODO check can't remove this
    dam_longitude = ee.Number(dam_point.coordinates().get(0))
    dam_latitude = ee.Number(dam_point.coordinates().get(1))
    # Define EE Point geometry with long and latitude values
    pt = ee.Geometry.Point(dam_longitude, dam_latitude)
    # Define search area
    pt_ftc = ee.FeatureCollection([ee.Feature(pt)])
    search_area = pt_ftc.map(buffer_points_bounds).geometry()
    # Identify all river reaches within search area
    # Measure their distance to unsnapped pt
    r_ftc = dta.HYDRORIVERS.filterBounds(search_area).map(
        lambda feat: feat.set('dist', feat.distance(pt, 1)))
    # Identify closet river reach within search radius
    # Keyword arguments don't work with limit in python
    r_closest = r_ftc.limit(1, 'dist', True)

    # Get length of closest river segment
    section_length = r_closest.geometry().length()
    section_length_10 = ee.Number(
        section_length).divide(10).floor().multiply(10)

    # Break the closet river segment into a set of points at approx 5m intervals
    step = ee.Number(5)
    distances = ee.List.sequence(0, section_length_10, step)
    river_line_string = r_closest.geometry().cutLines(
        **{'distances': distances, 'maxError': 1})

    def line_to_pts(line):
        return ee.List(line).map(lambda e: ee.Feature(ee.Geometry.Point(
            ee.Number(ee.List(e).get(0)), ee.Number(ee.List(e).get(1)))))

    river_vertices = ee.List(river_line_string.coordinates())
    point_features = (river_vertices.map(line_to_pts).flatten())

    # Identify closest candidate point to dam
    candidate_points = (
        ee.FeatureCollection(point_features).map(
            lambda feat: feat.set('tdist', feat.distance(pt, 1))))

    # Keyword arguments don't work with limit in python
    snapped_point = (
        candidate_points.limit(1, 'tdist', True).first().geometry())

    # Distance between input point and snapped point
    displacement_m = snapped_point.distance(pt, 1)
    ps_lon = ee.Number(snapped_point.coordinates().get(0))
    ps_lat = ee.Number(snapped_point.coordinates().get(1))

    feature = dam_feature
    feature = feature.setGeometry(snapped_point)
    feature = feature.set('ps_snap_displacement', displacement_m)
    feature = feature.set('ps_lon', ps_lon)
    feature = feature.set('ps_lat', ps_lat)
    return feature
