""" Collections of tests for dams.py """
import pytest
import ee
import heet.dams
from heet.earth_engine import EarthEngine


EarthEngine.init()


@pytest.fixture
def point():
    return ee.Geometry.Point([-122.08412, 37.42189])


def test_dam_properties(point):
    """ """
    dam = heet.dams.Dam(point)
    assert dam.longitude == -122.08412
    assert dam.latitude == 37.42189


def test_dam_from_feature(point):
    """Test Dam object instantiation from feature using classmethod."""
    point_feat = ee.Feature(point)
    dam = heet.dams.Dam.from_feature(point_feat)
    assert dam.longitude == -122.08412
    assert dam.latitude == 37.42189


def test_get_snap(point):
    """ """
    dam = heet.dams.Dam(point, "Sample Dam")
    dam.snap(
        rivers=ee.FeatureCollection(
            "users/KamillaHarding/XHEET_ASSETS/HydroRIVERS_v10"))
    assert dam.feature.getInfo() == \
        {'type': 'Feature',
         'geometry': {
            'type': 'Point',
            'coordinates': [-122.08938155931445, 37.4185488976988]},
         'properties': {
            'ps_lat': 37.4185488976988,
            'ps_lon': -122.08938155931445,
            'ps_snap_displacement': 595.3377740209114}}
