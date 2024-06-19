"""Wrappers for Google Earth Engine geometry objects"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, Optional
import ee


class Geometry(ABC):
    """Interface for EE geometry objects:
    Supports the following ee geometries, in the order of increasing
    dimensionality and/or size of the container:
       * Point: single point in space
       * MultiPoint: a number of (isolated) points
       * LineString: a geometry constructed from a number of lines
       * MultiLineString: a collection composed of a number of line strings
       * LinearRing: a closed LineString
       * Polygon: a polygon shape
       * Rectangle: a polygon with rectangular shape
       * MultiPolygon: a collection of polygons
    """

    @abstractmethod
    def to_feature(self):
        """ """

    @classmethod
    @abstractmethod
    def from_feature(cls, feature: ee.Feature) -> Geometry:
        """ """

    @property
    @abstractmethod
    def geometry(self) -> ee.Geometry:
        """ """

    @property
    @abstractmethod
    def feature(self) -> ee.Feature:
        """ """


class Point(Geometry):
    """AA base class for for point feature classes.

    Attributes:
        point (ee.Geometry.Point): EarthEngine Point representation of the
            geographical point.
        projection (ee.Projection): EarthEngine projection object
    """
    def __init__(self,
                 point: ee.Geometry.Point,
                 projection: Optional[ee.Projection] = None):
        self._geometry = point
        self._feature = self.to_feature()
        self.projection = projection

    @property
    def geometry(self) -> ee.Geometry:
        return self._geometry

    @property
    def feature(self) -> ee.Feature:
        return self._feature

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
            self._feature = feat
        return feat

    def feature_geometry(self):
        return self.to_feature().geometry()
