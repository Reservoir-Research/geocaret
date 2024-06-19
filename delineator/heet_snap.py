""" Functions for snapping dams (point features) to the nearest river
    segment """
import ee
import logging


try:
    from delineator import heet_config as cfg
    from delineator import heet_data as dta
    from delineator import heet_log as lg

except ModuleNotFoundError:
    if not ee.data._credentials:
        ee.Initialize()

    import heet_config as cfg
    import heet_data as dta
    import heet_log as lg
debug_mode = False

# =============================================================================
#  Set up logger
# =============================================================================
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
#  Functions
# ==============================================================================
def pts_to_linestring(coords):

    pt1_coord_list = ee.List(ee.List(coords).get(0))
    pt2_coord_list = ee.List(ee.List(coords).get(1))

    pt_start = ee.Geometry.Point(
        ee.Number(pt1_coord_list.get(0)), ee.Number(pt1_coord_list.get(1))
    )

    pt_end = ee.Geometry.Point(
        ee.Number(pt2_coord_list.get(0)), ee.Number(pt2_coord_list.get(1))
    )

    output_line = ee.Geometry.LineString(ee.List([pt_start, pt_end]))

    feat = ee.Feature(output_line)

    feat = feat.set("pt_start", pt_start)
    feat = feat.set("pt_end", pt_end)

    return feat


def buffer_points_radius(point: ee.Geometry.Point) -> ee.Feature:
    """Creates a circle from point in EE"""
    radius = cfg.jensen_search_radius
    pt_feature = ee.Feature(point)
    return pt_feature.buffer(radius)


def buffer_points_bounds(point: ee.Geometry.Point) -> ee.Feature:
    """Creates a circle from point and adds the bounding box of the
    created geometry"""
    return buffer_points_radius(point).bounds()


def snap_pt_to_line(P, A, B):
    """Finds the closest point to point P that lies
    on line segment AB"""

    # Vector from point A to point B
    AB = ee.Array(B).subtract(A)

    # Vector from point A to point P
    AP = ee.Array(P).subtract(A)

    # Generic implementations of point to line
    # projection will check that
    # the start and end points of the line are not
    # equal (omitted we never expect to see this in
    # HydroBASINS data)

    # Squared distance from point A to point B
    AB_squared = ee.Array(AB).dotProduct(AB)

    t = ee.Array(AP).dotProduct(AB).divide(AB_squared)

    q = ee.Array(AB).multiply(t).add(A)

    s = ee.Algorithms.If(t.gte(0).And(t.lte(1)), q, ee.Algorithms.If(t.lt(0), A, B))

    return s


def jensen_snap_hydroriver(dam_feature: ee.Feature) -> ee.Feature:
    """Takes a EE dam feature and snaps it to the nearest river segment
    in HYDRORIVERS Feature Collection"""
    # Convert input argument to EE feature and extract geometry
    dam_feature = ee.Feature(dam_feature)
    # Define EE Point geometry with long and latitude values
    pt = dam_feature.geometry()
    # Define search area
    pt_ftc = ee.FeatureCollection([ee.Feature(pt)])
    search_area = pt_ftc.map(buffer_points_bounds).geometry()
    # Identify all river reaches within search area
    # Measure their distance to unsnapped pt
    r_ftc = dta.HYDRORIVERS.filterBounds(search_area).map(
        lambda feat: feat.set("dist", feat.distance(pt, 1))
    )
    # Identify closet river reach within search radius
    # Keyword arguments don't work with limit in python
    r_closest = r_ftc.limit(1, "dist", True)

    # Get length of closest river segment
    section_length = r_closest.geometry().length()
    section_length_10 = ee.Number(section_length).divide(10).floor().multiply(10)

    # Break the closet river segment into a set of points at approx 5m intervals
    step = ee.Number(5)
    distances = ee.List.sequence(0, section_length_10, step)
    river_line_string = r_closest.geometry().cutLines(
        **{"distances": distances, "maxError": 1}
    )

    def line_to_pts(line):
        return ee.List(line).map(
            lambda e: ee.Feature(
                ee.Geometry.Point(
                    ee.Number(ee.List(e).get(0)), ee.Number(ee.List(e).get(1))
                )
            )
        )

    river_vertices = ee.List(river_line_string.coordinates())
    point_features = river_vertices.map(line_to_pts).flatten()

    # Identify closest candidate point to dam
    candidate_points = ee.FeatureCollection(point_features).map(
        lambda feat: feat.set("tdist", feat.distance(pt, 1))
    )

    # Keyword arguments don't work with limit in python
    snapped_point = candidate_points.limit(1, "tdist", True).first().geometry()

    # Distance between input point and snapped point
    displacement_m = snapped_point.distance(pt, 1)
    ps_lon = ee.Number(snapped_point.coordinates().get(0))
    ps_lat = ee.Number(snapped_point.coordinates().get(1))

    dam_longitude = ee.Number(pt.coordinates().get(0))
    dam_latitude = ee.Number(pt.coordinates().get(1))

    feature = dam_feature
    feature = feature.setGeometry(snapped_point)
    feature = feature.set("ps_snap_displacement", displacement_m)
    feature = feature.set("ps_lon", ps_lon)
    feature = feature.set("ps_lat", ps_lat)
    feature = feature.set("raw_lon", dam_longitude)
    feature = feature.set("raw_lat", dam_latitude)
    return feature


if __name__ == "__main__":

    # Development
    print("Development Run...")

    damFeat = ee.Feature(ee.Geometry.Point(ee.Number(98.580461), ee.Number(26.051936)))
    print(damFeat.getInfo())

    snappedDamFeat = jensen_snap_hydroriver(damFeat)
    print(snappedDamFeat.getInfo())

    interReaches = dta.HYDRORIVERS.filterBounds(snappedDamFeat.geometry())
    print("", interReaches.size().getInfo())
