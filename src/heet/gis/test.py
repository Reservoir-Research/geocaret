"""Wrappers for Google Earth Engine geometry objects"""
from __future__ import annotations
from typing import Tuple, Optional
import ee


class Point:
    """AA base class for for point feature classes.

    Attributes:
        point (ee.Geometry.Point): EarthEngine Point representation of the
            geographical point.
        projection (ee.Projection): EarthEngine projection object
    """
    def __init__(self,
                 point: ee.Geometry.Point,
                 projection: Optional[ee.Projection] = None):
        self.geometry = point
        self.feature = self.to_feature()
        self.projection = projection

    @classmethod
    def from_coordinates(cls,
                         coordinates: Tuple[float, float],
                         projection: Optional[ee.Projection] = None) -> Point:
        return cls(point=ee.Geometry.Point(list(coordinates)),
                   projection=projection)

    @classmethod
    def from_feature(cls, feature: ee.Feature) -> Point:
        return cls(
            point=ee.Geometry.Point(feature.getInfo()[
                'geometry']['coordinates']),
            projection=None)

    @property
    def longitude(self) -> float:
        return ee.Number(self.geometry.coordinates().get(0)).getInfo()

    @property
    def latitude(self) -> float:
        return ee.Number(self.geometry.coordinates().get(1)).getInfo()

    def to_feature(self, inplace: bool = True, **kwargs) -> ee.Feature:
        """Convert Point object to ee.Feature."""
        feat = ee.Feature(self.geometry)
        feat = feat.setGeometry(self.geometry)
        # Distance between input point and snapped point
        for key, value in kwargs.items():
            feat = feat.set(key, value)
        if inplace:
            self.feature = feat
        return feat

    def feature_geometry(self):
        return self.to_feature().geometry()
