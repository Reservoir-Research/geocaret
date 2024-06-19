"""Module with application class templates and class structure."""
from __future__ import annotations
import sys
from typing import Optional, List, Union, Any, Dict
import pathlib
import heet.log_setup
from heet.utils import get_package_file, read_config, set_logging_level
from heet.utils import logging_prefix
from heet.gis.data import FeatureCollectionData, HydroRiversData
from heet.gis.geometry import Point
from heet.assets import EmissionAssets
import ee

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)
logger_config: dict = read_config(
    get_package_file('./config/logging_levels.yaml'))
set_logging_level(logger=logger, level=logger_config['gis']['dams'])
MODULE_PREFIX = logging_prefix(sys.modules[__name__].__file__)

config_file: pathlib.PosixPath = get_package_file(
    './config/emissions/parameters.yaml')
dams_config = read_config(config_file)['dams']
# Read max_number_of_dams that can be processed in a single batch
DAMS_MAX = dams_config['max_dams_in_set']
SEARCH_RADIUS = dams_config['search_radius']


class Dam:
    """Class representing a barrier/dam
    Attributes:
        point (ee.Geometry.Point): A EarthEngine Point representation of dam
            location.
        name (Optional[str]): Name of the dam/barrier.
        feature (ee.Feature): A EarthEngine Feature representation of the dam.
        config (dict): configuration dictionary with key:value pairs.

    Notes:
        Uses Google's Earth's API functionality.
    """
    def __init__(
            self,
            gis_data: Point,
            id: Union[str, int],
            name: Optional[str] = None) -> None:
        """
        Instantiates the Dam class with point geometry, name and id.

        Atrributes:
            gis_data: A Point representation of dam location.
            id: Unique str/int identifier of the dam.
            name: Name of the dam/barrier.
            snapped: Boolean flag determining whether the dam has been aligned
                with a different ee object, e.g. river network.
            aux_data: Auxiliary information about the dam not contained inside
                the point object, e.g. installed capacity, elevation above the
                turbine, etc.
        """
        self.gis_data = gis_data
        self.id = id
        self.name = name
        self.snapped: bool = False
        self.aux_data: Dict[str, Any] = {}

    def add_data(self, key: str, value: Any):
        """Append data to data dictionary"""
        if key not in self.aux_data:
            self.aux_data[key] = value

    # TODO: extract id from feature object
    @classmethod
    def from_feature(
            cls, feature: ee.Feature, id: Union[str, int],
            name: Optional[str] = None, **kwargs) -> Dam:
        """Class method allowing instantiating Dam objects from features
        instead of points.
        Args:
            feature (ee.Feature):
            id: Mandatory id of the dam object
            name: Optional name of the dam object.
        """
        # NOTE: Not sure if it is generic enough - TJ
        point_from_feat = Point.from_feature(feature)
        return cls(gis_data=point_from_feat, id=id, name=name, **kwargs)

    @staticmethod
    def _buffer_points_radius(
            point: ee.Geometry.Point,
            radius: float = SEARCH_RADIUS) -> ee.Feature:
        """Creates a circle from point using radius defined in
        `self.config['search_radius']`.
        Args:
            point (ee.Geometry.Point): A EarthEngine Point representation of dam
                location.
        Returns:
            A buffered EE feature a radius out from original boundary. Since
            the original feature is a point.
        """
        pt_feature = ee.Feature(point)
        return pt_feature.buffer(radius)

    @staticmethod
    def _buffer_points_bounds(
            point: ee.Geometry.Point,
            radius: float = SEARCH_RADIUS) -> ee.Feature:
        """Creates a circle from point and adds the bounding box of the
        created geometry.
        Args:
            point (ee.Geometry.Point): A EarthEngine Point representation of
                dam location.
        """
        return Dam._buffer_points_radius(point=point, radius=radius).bounds()

    def snap(self,
             rivers: FeatureCollectionData,
             interval: float = 5.0,
             inplace: bool = True) -> ee.Feature:
        """Takes a Earth Engine (EE) dam (point) feature and snaps it to the
            nearest river segment.
        Args:
            rivers (ee.FeatureCollection): EE representation of a river system
            interval (float): interval in which the nearest river segment is
                divided into a sequence of points
        Returns:
            ee.Feature representation of the snapped dam point
        """

        def line_to_pts(line):
            return ee.List(line).map(lambda e: ee.Feature(ee.Geometry.Point(
                ee.Number(ee.List(e).get(0)), ee.Number(ee.List(e).get(1)))))

        logger.info(f"Snapping dam location of dam id: {self.id}")
        point_old = self.gis_data.geometry
        point_ftc = ee.FeatureCollection([ee.Feature(point_old)])
        # Find a circle of radius `radius` around the dam point
        search_area = point_ftc.map(self._buffer_points_bounds).geometry()
        # Identify all river reaches within search area
        # Measure their distance to unsnapped pt
        r_ftc = rivers.data.filterBounds(geometry=search_area).map(
            lambda feat: feat.set('dist', feat.distance(point_old, 1)))
        # Identify closet river reach within search radius
        # Keyword arguments don't work with limit in python
        r_closest = r_ftc.limit(1, 'dist', True) # (max, property, ascending)
        # Get length of closest river segment
        section_length = r_closest.geometry().length()
        section_length_10 = ee.Number(
            section_length).divide(10).floor().multiply(10)
        # Break the closet river segment into a set of points at interval size
        # specified in argument interval
        distances = ee.List.sequence(
            start=0,
            end=section_length_10,
            step=ee.Number(interval))
        # Cut the closest river reach into segments
        river_line_string = r_closest.geometry().cutLines(
            distances=distances, maxError=1)
        # Get coordinates of all segments
        river_vertices = ee.List(river_line_string.coordinates())
        point_features = river_vertices.map(line_to_pts).flatten()
        # Identify closest candidate point to dam
        candidate_points = (
            ee.FeatureCollection(point_features).map(
                lambda feat: feat.set('tdist', feat.distance(point_old, 1))))
        # Keyword arguments don't work with limit in python
        snapped_point = (
            candidate_points.limit(1, 'tdist', True).first().geometry())
        # snapped point of type ee.Geometry
        # Create a feature from the original point, update geometry,
        # and add new properties
        if inplace:
            self.gis_data = Point(point=snapped_point)
            self.snapped = True
        # Prepare the feature representation of the snapped point
        displacement_m = snapped_point.distance(point_old, 1)
        ps_lon = ee.Number(snapped_point.coordinates().get(0))
        ps_lat = ee.Number(snapped_point.coordinates().get(1))
        snapped_feat = self.gis_data.to_feature(
            inplace=inplace,
            ps_snap_displacement=displacement_m,
            ps_lon=ps_lon,
            ps_lat=ps_lat)
        logger.info(f"Snapping of dam id: {self.id} successful.")
        return snapped_feat

    @staticmethod
    def impute_dam_height(
            power_capacity: ee.Number,
            turbine_efficiency: ee.Number,
            plant_depth: ee.Number,
            mad: ee.Number) -> ee.Number:
        """Operates on Google EE data structures (ee.Number)
        Calculates dam height from power capacity, turbine efficiency, and
        mean annual discharge (mad) in m3/s.
        """
        # Power = turbine efficiency  * discharge * gravity acceleration *
        #         water density
        den = turbine_efficiency.divide(100).multiply(mad).multiply(9.81)\
            .multiply(1000)
        dam_height = power_capacity.multiply(1e6).divide(den)\
            .subtract(plant_depth)
        dam_height_rounded = dam_height.multiply(1000).round().divide(1000)
        return dam_height_rounded


# TODO: FIX THIS CLASS
class DamCollection:
    """ Class storing a list of Dam objects.
    Attributes:
        _dams: list[Dam]: list of Dam objects."""

    def __init__(
            self,
            dams: List[Dam],
            feature_collection: Optional[ee.FeatureCollection] = None):
        self._dams = dams
        self._feature_collection = feature_collection

    @property
    def feature_collection(self):
        return self._feature_collection

    @property
    def dams(self) -> List[Dam]:
        """Return None, empty iterable or an iterable with Dam objects."""
        return self._dams

    @property
    def c_dam_ids(self):
        return self._feature_collection.aggregate_array("id").getInfo()

    @classmethod
    def from_assets(cls, **kwargs):
        """Initialize DamCollection from the assets in Google's Earth Engine.
        Args:
            **config_file (pathlib.PosixPath): configuration file for
                EmissionAssets.
            **working_folder (str): working folder for EmissionAssets.
            **dam_names (Union[List[str], Tuple[str]]): list of dam names
        """
        # Instantiate emission assets object
        emission_assets = EmissionAssets(**kwargs)
        # Create a list of Dam object from information in emission_assets
        dams_feature_collection = ee.FeatureCollection(
            emission_assets.dams_table_path)
        # Convert dams feature collection to list
        dams_list = dams_feature_collection.toList(DAMS_MAX)
        dam_object_list = []
        # Iterate until no objects can be found and exception is raised.
        for item in range(0, DAMS_MAX):
            if "dam_names" in kwargs:
                # Assumes dam_names are an Colllection
                try:
                    dam_name = kwargs.get("dam_names")[item]
                except IndexError:
                    dam_name = None
            try:
                dam_feature = dams_list.get(item).getInfo()
                dam_object_list.append(
                    Dam.from_feature(feature=dam_feature,
                                     id=id, name=dam_name, **kwargs))
            except ee.ee_exception.EEException:
                break
        return cls(dams=dam_object_list,
                   feature_collection=dams_feature_collection)


if __name__ == "__main__":
    from heet.web.earth_engine import EarthEngine
    EarthEngine().init()
    point = Point.from_coordinates(coordinates=(-122.08412, 37.42189))
    rivers = HydroRiversData.from_config()
    dam = Dam(point, id="1", name="Dam number 1")
    print(dam.gis_data.latitude)
    dam.snap(rivers=rivers)
    print(dam.gis_data.latitude)
    print(dam.gis_data.feature.get('ps_snap_displacement').getInfo())
