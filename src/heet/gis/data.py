""" Module defining datasets used for catchment and reservoir delineation
    required for calculation of input data for GHG emission calculations """
from __future__ import annotations
from typing import Union
import ee
from heet.utils import get_package_file, read_config
from heet.web.earth_engine import EarthEngine
# Conditional initilization of Earth Engine API
EarthEngine().init()

# Load the config file with information about data sources
data_sources = read_config(get_package_file('./config/emissions/data.yaml'))


class EEData:
    """Wrapper for a generic EarthEngine data source."""
    def __init__(
            self,
            data: Union[ee.Feature, ee.FeatureCollection, ee.Image,
                        ee.ImageCollection]):
        self._data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data


class FeatureData(EEData):
    """Wrapper for Earth Engine data in the form of ee.FeatureCollection."""
    def __init__(self, data: ee.Feature):
        self._data = data

    @classmethod
    def from_url(cls, url: str) -> FeatureData:
        """Load data from import file"""
        return cls(data=ee.Feature(url))


class FeatureCollectionData(EEData):
    """Wrapper for Earth Engine data in the form of ee.FeatureCollection."""
    def __init__(self, data: ee.FeatureCollection):
        self._data = data

    @classmethod
    def from_url(cls, url: str) -> FeatureCollectionData:
        """Load data from import file"""
        return cls(data=ee.FeatureCollection(url))


class ImageData(EEData):
    """Wrapper for Earth Engine data in the form of ee.Image."""
    @classmethod
    def from_url(cls, url: str) -> ImageData:
        """Load data from import file"""
        return cls(data=ee.Image(url))

    def band(self, *bands: str) -> ee.Image:
        """Data selector for images with ``bands`` attribute."""
        if len(bands) > 0:
            return self.data.select(bands)
        return self.data


class HydroRiversData(FeatureCollectionData):
    """Hydrosheds Hydrorivers."""
    @classmethod
    def from_config(cls, config: dict = data_sources) -> FeatureCollectionData:
        return cls.from_url(url=config['hydrorivers']['url'])


class HydroBasinsData(FeatureCollectionData):
    """Retrieve collection and add a new field with string representation
    of Pfafstetter code (PFAF_ID)."""
    def __init__(self, data: ee.FeatureCollection, level: int) -> None:
        """
        Args:
            data: ee.FeatureCollection representing hydrobasin data
            level: hydrobasins level: from 1 to 12 in the order of increasing
                level of detail."""
        super().__init__(data)
        self.data = data.map(
            lambda feat: feat.set({
                'SPFAF_ID': ee.Number(feat.get('PFAF_ID')).format("%s")}))
        # level is not linked to data, make sure that appropriate level is
        # assigned so that the level information matches the hydrobasins
        # resolution.
        self.level = level

    @classmethod
    def from_config(cls, config: dict = data_sources,
                    level: int = 12) -> HydroBasinsData:
        """Load data from configuration file.
        By default choose Hydrobasins at level 12."""
        url = config['hydrobasins']['url'][level]
        return cls(data=ee.FeatureCollection(url), level=level)


class HydroShedsData:
    """Container for HydroBasinsData in the form of ee.Dictionary."""
    def __init__(self, hydrobasins: ee.Dictionary):
        """ """
        self.data = hydrobasins

    @classmethod
    def from_config(cls, config: dict = data_sources) -> HydroShedsData:
        """Load data from configuration file."""
        hydrobasins_dict = config['hydrobasins']['url']
        ee_dict_data = ee.Dictionary({
            str(id): ee.FeatureCollection(src) for id, src in
            zip(hydrobasins_dict.keys(), hydrobasins_dict.values())})
        return cls(hydrobasins=ee_dict_data)


class FlowAccumulationData(ImageData):
    """Hydrosheds Flow Accumulation - b1 band contains flow accumulation data
    # between 1 and 2.78651e+07."""

    @classmethod
    def from_config(cls, config: dict = data_sources) -> FlowAccumulationData:
        """ """
        return cls.from_url(url=config['flow_accumulation']['url'])


class DrainageDirectionData(ImageData):
    """Hydrosheds Drainage Directions (Image)

    Note: b1 band contains drainage direction information between 0 and 255.
    1=E, 2=SE, 4=S, 8=SW, 16=W, 32=NW, 64=N, 128=NE.

    Final outlet cells to the ocean are flagged with a value of 0 and cells that
    mark the lowest point of an endorheic basin (inland sink) are flagged with a
    value of 255 (original value of -1).
    """

    @classmethod
    def from_config(cls, config: dict = data_sources) -> DrainageDirectionData:
        """ """
        return cls.from_url(url=config['hydrosheds_drainage_dir']['url'])

    def precondition(self) -> ee.Image:
        """Processes HydroSHEDS Drainage Directions dataset.

        Remaps pixel values, adds coordinate and pixel id metadata, returns
        processed image with additional bands.

        Returns:
            EarthEngine Image oject with processed HydroSHEDS Drainage Directions
              dataset
        """
        dd_asset = self.data.select(['b1'], ['d1'])
        # Remap pixel values
        dd_grid = ee.Image(dd_asset).remap(
            **{'from': [1, 2, 4, 8, 16, 32, 64, 128, 0, 255],
               'to': [6, 9, 8, 7, 4, 1, 2, 3, 0, 255],
               'bandName': 'd1',
               'defaultValue': 999})
        # Add longitude and latitude (lnglat) to drainage direction img
        proj = dd_grid.select([0]).projection()
        lnglat = ee.Image.pixelLonLat().reproject(proj)
        coords = ee.Image.pixelCoordinates(proj).rename(['gid', 'j'])
        # Define expressions to be executed for every field variable
        field_expression_map = {
            'gid': coords.select("gid"),
            'j': coords.select("j"), }
        # Bug in EE with renaming means we use gid here (insead of i)
        x_img = ee.Image().expression("gid", field_expression_map)
        y_img = ee.Image().expression("j", field_expression_map)
        # Add pixel id to drainage direction img
        grid_ident = x_img.long().leftShift(32).add(
            y_img.long()).rename(["grid_id"])
        # Add metadata (bands) with pixel id and longitude and latitude
        dd_grid_coord = dd_grid.addBands(grid_ident).addBands(lnglat)
        return dd_grid_coord


if __name__ == "__main__":
    """ """
