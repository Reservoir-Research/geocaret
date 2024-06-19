""" """
from __future__ import annotations
from typing import List, Any, Dict, Callable
import math
import pathlib
import ee
import heet.log_setup
from heet.parameters.parameters import (
    Parameter, RawOutput, FormattedOutput, OutputFormatter,
    FormattedOutputValue)
from heet.utils import get_package_file, read_config, set_logging_level

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)
logger_config: dict = read_config(
    get_package_file('./config/logging_levels.yaml'))
set_logging_level(
    logger=logger, level=logger_config['parameters']['catchment'])

data_config_file: pathlib.PosixPath = get_package_file(
    './config/emissions/data.yaml')
data_config = read_config(data_config_file)

# For adding to parameter names, if needed
VAR_PREFIX = "c_"


# Catchment/reservoir area (km2)
def area(land_ftc: ee.FeatureCollection) -> ee.Number:
    """Calculate area of a feature collection that is composed of geometry
    that contains the area method."""
    land_geom = land_ftc.geometry()
    return land_geom.area(1).divide(1000 * 1000)


# (Default) formatting functions
def mean_slope_perc_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.0f")
    return ee.Number(output.value).format(string_format)


def mean_annual_runoff_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.0f")
    not_defined_val = kwargs.get('not_defined', "ND")
    err_val = kwargs.get('err_val', -999)
    return ee.Algorithms.If(
        ee.Number(output).neq(err_val),
        ee.Number(output).format(string_format), not_defined_val)


def mean_annual_prec_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.0f")
    return ee.Number(output.value).format(string_format)


def predominant_biome_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    return ee.String(output.value)


def predominant_climate_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    return ee.String(output.value)


def mean_olsen_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.3f")
    return ee.Number(output.value).format(string_format)


def landcover_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """Landcover output is a list of fractions, each representing a different
    landcover type/category."""
    string_format = kwargs.get('string_format', "%.3f")
    start_index = kwargs.get('start_index', 0)
    landcover_fracs = output.value.map(
        lambda value: ee.Number(value).format(string_format))
    indexed_var_names = output.name_rollout(start_index)
    return {
        var_name: ee.List(landcover_fracs).get(index) for
        var_name, index in
        zip(indexed_var_names, range(0, len(indexed_var_names)))}


def mean_soil_org_c_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.3f")
    err_val = kwargs.get('err_val', -999)
    not_defined_val = kwargs.get('not_defined', "ND")
    return ee.Algorithms.If(
        ee.Number(output.value).neq(err_val),
        ee.Number(output.value).format(string_format), not_defined_val)


def soiltype_fomatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    return output.value


def population_fomatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.0f")
    return ee.Number(output.value).format(string_format)


def population_density_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.2f")
    return ee.Number(output.value).format(string_format)


def terra_clim_monthly_default_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.0f")
    return ee.Number(output.value).format(string_format)


def terra_clim_annual_default_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.2f")
    return ee.Number(output.value).format(string_format)


def smap_mean_default_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.0f")
    multiplier = kwargs.get('multiplier', 1000)
    return ee.Number(output.value).multiply(multiplier).format(string_format)


class MeanSlopePercParameter(Parameter):
    """Calculate mean slope of a catchment or subcatchment area using DEM
    for information about elevations."""
    AUX_DATA_PATH = data_config['dem']['url']
    AUX_DATA_FIELD = 'elevation'
    VALUE_FIELD = 'slope'

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "mean catchment slope",
            variables: List[str] = ["mean_slope_pc"],
            units: List[str] = ["%"],
            formatters: List[OutputFormatter] = [mean_slope_perc_formatter]):
        super().__init__(base_data, name, variables, units, formatters)

    @staticmethod
    def degrees_to_perc_slope(slope_degrees: ee.Number) -> ee.Number:
        """Convert slope in degrees to slope in percent"""
        return ee.Number(slope_degrees).multiply(
            math.pi/180).tan().multiply(100)

    def calculate(self, **kwargs: Any) -> MeanSlopePercParameter:
        """Calculate mean slope of the catchment in percentage."""
        catchment_geom = self.base_data.geometry()
        dem = ee.Image(self.AUX_DATA_PATH)
        # Expected SCALE = 30
        projection = ee.Image(dem).projection()
        scale = projection.nominalScale()
        elevation_dem = ee.Image(dem).select(self.AUX_DATA_FIELD)
        slope_dem = ee.Terrain.slope(elevation_dem)
        mean_slope_degrees = slope_dem.reduceRegion(**{
           'reducer': ee.Reducer.mean(),
           'geometry': catchment_geom,
           'scale': scale,
           'maxPixels': 2e11}).get(self.VALUE_FIELD)
        self._raw_outputs = [RawOutput(
            var_name=self.variables[0], unit=self.units[0],
            value=self.degrees_to_perc_slope(
                slope_degrees=mean_slope_degrees))]
        self.format()
        return self


class MeanAnnualRunoffParameter(Parameter):
    """Calculation of mean annual runoff in a catchment, Fekete."""
    AUX_DATA_PATH = data_config['runoff_orig']['url']

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "mean annual runoff",
            variables: List[str] = ["mar_mm"],
            units: List[str] = ["mm/yr"],
            formatters: List[OutputFormatter] =
            [mean_annual_runoff_formatter]) -> None:
        super().__init__(base_data, name, variables, units, formatters)

    def calculate(self, **kwargs: Any) -> MeanAnnualRunoffParameter:
        """ """
        catchment_geom = self.base_data.geometry()
        # FEKETE (30' ~ 55560 m )
        runoff_img = ee.Image(self.AUX_DATA_PATH)
        # Expected SCALE = 55560
        projection = ee.Image(runoff_img).projection()
        scale = projection.nominalScale()
        mean_runoff_mm = ee.Number(runoff_img.reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': catchment_geom,
            'scale': scale,
            'maxPixels': 2e11}).get('b1'))
        logger.debug(
            "[MeanAnnualRunoffParameter] [mean_annual_runoff_mm]: %f",
            mean_runoff_mm.getInfo())
        # Handle null values, return ee.Number
        self._raw_outputs = [RawOutput(
            var_name=self.variables[0], unit=self.units[0],
            value=ee.Algorithms.If(mean_runoff_mm, mean_runoff_mm, -999))]
        self.format()
        return self


class MeanAnnualPrecParameter(Parameter):
    """Mean annual precipitation, [mm yr-1], WorldClim 2.1"""
    AUX_DATA_PATH = data_config['precipitation']['url']

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "mean annual precipitation",
            variables: List[str] = ["map_mm"],
            units: List[str] = ["mm/yr"],
            formatters: List[OutputFormatter] =
            [mean_annual_prec_formatter]) -> None:
        super().__init__(base_data, name, variables, units, formatters)

    def calculate(self) -> MeanAnnualPrecParameter:
        """ """
        # World Clim 2.1 30 Arc seconds resolution; ~900m
        bioclimate = ee.Image(self.AUX_DATA_PATH)
        bioprecipitation = bioclimate.select(['b1'], ['bio12'])
        # Expected SCALE = 900
        projection = ee.Image(bioclimate).projection()
        scale = projection.nominalScale()
        catchment_geom = self.base_data.geometry()
        map_mm = ee.Number(bioprecipitation.reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': catchment_geom,
            'scale': scale,
            'maxPixels': 2e11}).get('bio12'))
        self._raw_outputs = [RawOutput(
            var_name=self.variables[0], unit=self.units[0],
            value=map_mm)]
        self.format()
        return self


class PredominantBiomeParameter(Parameter):
    """Predominant biome, Dinerstein et al. (2017)"""
    AUX_DATA_PATH = data_config['biomes']['url']
    BUFFER_ZONE: int = 500
    AREA_CONV: float = 1000*1000

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "predominant biome in catchment",
            variables: List[str] = ["biome"],
            units: List[str] = ["-"],
            formatters: List[OutputFormatter] =
            [predominant_biome_formatter]) -> None:
        super().__init__(base_data, name, variables, units, formatters)

    # Predominant biome
    def calculate(self) -> PredominantBiomeParameter:
        """ """
        def get_biome(feat: ee.Feature) -> ee.Feature:
            """ """
            # Define biome geometry
            geom = ee.Feature(feat).geometry()
            # Calculate the area of the biome zone
            area_biome_zone = geom.area(1)
            # calculate the area of the catchment that intersects with each
            # biome zone (intersection)
            union_biomes = catchment_area.filterBounds(geom).union()\
                .first().geometry()
            intersection = union_biomes.intersection(geom, 1).area(1)
            # Divide intersection/catchment-area_m to calculate the percentage
            # of catchment area within the biome
            perc = intersection.divide(catchment_area_m).multiply(100)
            return ee.Feature(feat).setMulti(
                {'AreaBiome': area_biome_zone,
                 'AreaCatch': catchment_area_m,
                 'PercentageBiome': perc})

        biomes_fc = ee.FeatureCollection(self.AUX_DATA_PATH)
        catchment_geom = self.base_data.geometry()
        catchment_buffer_geom = catchment_geom.buffer(self.BUFFER_ZONE)
        catchment_bbox = catchment_buffer_geom.bounds()
        catchment_area_m = area(self.base_data).multiply(self.AREA_CONV)
        # Put a bounding box around the catchment
        # to speed up computation
        catchment_area = self.base_data.filterBounds(catchment_bbox)
        a_biomes_fc = biomes_fc.filterBounds(catchment_bbox)
        # [[I-1]] Calculate area of overlap between biome and catchment
        catchment_biome = a_biomes_fc.map(get_biome)
        biome_percentages = catchment_biome.aggregate_array('PercentageBiome')
        biome_names = catchment_biome.aggregate_array('BIOME_NAME')
        index_pb = ee.Array(biome_percentages).argmax().get(0)
        predominant_biome = biome_names.get(index_pb)
        self._raw_outputs = [RawOutput(
            var_name=self.variables[0], unit=self.units[0],
            value=predominant_biome)]
        self.format()
        return self


class PredominantClimateParameter(Parameter):
    """Predominant climate zone"""
    AUX_DATA_PATH = data_config['climate']['url']

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "predominant climate zone",
            variables: List[str] = ["climate_zone"],
            units: List[str] = [""],
            formatters: List[OutputFormatter] =
            [predominant_climate_formatter]) -> None:
        super().__init__(base_data, name, variables, units, formatters)

    def calculate(self, **kwargs: Any) -> PredominantClimateParameter:
        """ """
        catchment_geom = self.base_data.geometry()
        # Climate
        climate_img = ee.Image(self.AUX_DATA_PATH)
        # Expected SCALE = 1000
        projection = ee.Image(climate_img).projection()
        scale = projection.nominalScale()
        modal_climate_category = climate_img.reduceRegion(**{
          'reducer': ee.Reducer.mode(),
          'geometry': catchment_geom,
          'scale': scale,
          'maxPixels': 2e11}).get('b1')
        predominant_climate = modal_climate_category
        self._raw_outputs = [RawOutput(
            var_name=self.variables[0], unit=self.units[0],
            value=predominant_climate)]
        self.format()
        return self


class MeanOlsenParameter(Parameter):
    """ """
    AUX_DATA_PATH = data_config['mean_olsen_p']['url']

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "mean Olsen P concentration in soil",
            variables: List[str] = ["mean_olsen"],
            units: List[str] = ["kgP/ha"],
            formatters: List[OutputFormatter] = [mean_olsen_formatter]) -> None:
        super().__init__(base_data, name, variables, units, formatters)

    def calculate(self) -> MeanOlsenParameter:
        """ """
        catch_geom = self.base_data.geometry()
        olsen_img = ee.Image(self.AUX_DATA_PATH)
        # Expected SCALE = 30
        olsen_projection = ee.Image(olsen_img).projection()
        olsen_scale = olsen_projection.nominalScale()
        mean_olsen = ee.Number(olsen_img.reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': catch_geom,
            'scale': olsen_scale,
            'maxPixels': 2e11}).get('b1'))
        self._raw_outputs = [RawOutput(
            var_name=self.variables[0], unit=self.units[0],
            value=mean_olsen)]
        self.format()
        return self


class LandcoverParameter(Parameter):
    """Finds ESA landuse categories in a given area and remaps them to
       IHA landuse categories.
       European Space Agency (2010)
    """

    AUX_DATA_PATH = data_config['landcover_esa']['url']
    ESA_IHA_CODE_MAP = {
        0: 0, 10: 1, 20: 1, 12: 2, 50: 2, 60: 2, 61: 2, 62: 2, 70: 2, 71: 2,
        72: 2, 80: 2, 81: 2, 82: 2, 90: 2, 100: 3, 110: 3, 120: 3, 121: 3,
        122: 3, 130: 3, 140: 3, 150: 3, 152: 3, 153: 3, 151: 3, 30: 3, 40: 3,
        11: 3, 160: 4, 170: 4, 180: 4, 190: 5, 200: 6, 201: 6, 202: 6, 210: 7,
        220: 8}
    IHA_CATEGORIES = {'0': 'No Data', '1': 'Croplands', '2': 'Forest',
                      '3': 'Grassland/Shrubland', '4': 'Wetlands',
                      '5': 'Settlements', '6': 'Bare Areas',
                      '7': 'Water Bodies', '8': 'Permanent snow and ice'}
    VALUE_FIELD = "land_use"

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "land cover composition",
            variables: List[str] = ["landcover"],
            units: List[str] = ["-"],
            formatters: List[OutputFormatter] = [landcover_formatter]) -> None:
        super().__init__(base_data, name, variables, units, formatters)

    def calculate(self) -> LandcoverParameter:
        """ """
        landcover_esa_img = ee.Image(self.AUX_DATA_PATH)
        # Expected SCALE = 300
        projection = ee.Image(landcover_esa_img).projection()
        scale = projection.nominalScale()
        landcover_iha_img = landcover_esa_img.remap(
            list(self.ESA_IHA_CODE_MAP.keys()),
            list(self.ESA_IHA_CODE_MAP.values())
        ).select(['remapped'], [self.VALUE_FIELD])
        land_geom = self.base_data.geometry()
        #land_buffer_geom = land_geom.buffer(600)
        #land_bbox = land_geom.bounds()
        iha_categories = ee.Dictionary(self.IHA_CATEGORIES)
        frequency = landcover_iha_img.reduceRegion(**{
            'reducer': ee.Reducer.frequencyHistogram().unweighted(),
            'geometry': land_geom,
            'scale': scale,
            'maxPixels': 2e11})
        total_count = ee.Dictionary(
            frequency.get(self.VALUE_FIELD)).toArray().toList().reduce(
            ee.Reducer.sum())
        fractions = ee.Dictionary(
            frequency.get(self.VALUE_FIELD)).toArray().toList().map(
                lambda v: ee.Number(v).divide(total_count))
        group_count = iha_categories.keys().length()
        codes = ee.Dictionary(frequency.get(self.VALUE_FIELD)).keys()
        fractions_dict = ee.Dictionary.fromLists(codes, fractions)
        fractions_list = ee.List.sequence(0, group_count.subtract(1))
        fractions_list_str = fractions_list.map(
            lambda i: ee.Number(i).format("%.0f"))

        logger.debug(f"Frequency: {frequency.getInfo()}")
        logger.debug(f"Fractions: {fractions.getInfo()}")
        logger.debug(f"Codes: {codes.getInfo()}")
        logger.debug(f"Fractions list: {fractions_list_str.getInfo()}")
        logger.debug(f"Fractions dict: {fractions_dict.getInfo()}")

        self._raw_outputs = [RawOutput(
            var_name=self.variables[0], unit=self.units[0],
            value=fractions_list_str.map(lambda i: ee.Number(
                fractions_dict.get(i, ee.Number(0)))
            )
        )]
        self.format()
        return self


class MeanSoilOrgCarbonParameter(Parameter):
    """Finds mean organic carbon concentration in the soil (0-30cm) depth
    in a given area, [kg m-2], Soil Grids."""
    AUX_DATA_PATH = data_config['org_soil_carbon']['url']
    VALUE_FIELD = 'ocs_0-30cm_mean'

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "mean soil organic carbon content",
            variables: List[str] = ["msoc_kgperm2"],
            units: List[str] = ["kg/m2"],
            formatters: List[OutputFormatter] =
            [mean_soil_org_c_formatter]) -> None:
        super().__init__(base_data, name, variables, units, formatters)

    def calculate(self) -> MeanSoilOrgCarbonParameter:
        """ """
        soil_carbon = ee.Image(self.AUX_DATA_PATH)
        # Expected scale = 250
        projection = ee.Image(soil_carbon).projection()
        scale = projection.nominalScale()
        land_geom = self.base_data.geometry()
        msoc = ee.Number(soil_carbon.reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': land_geom,
            'scale': scale,
            'maxPixels': 2e11}).get(self.VALUE_FIELD)).multiply(0.1)
        # Expect only one output
        self._raw_outputs = [RawOutput(
            var_name=self.variables[0], unit=self.units[0], value=msoc)]
        self.format()
        return self


class SoilTypeParameter(Parameter):
    """Calculates soil type characteristic of an area.

    If soil carbon in the area >=[CUTOFF_POINT] kg/m2 -> soil type is Organic
    If soil carbon in the area <[CUTOFF_POINT] kg/m2 -> soil type is Mineral
    """
    AUX_DATA_PATH = data_config['org_soil_carbon']['url']
    AUX_DATA_FIELD = 'ocs_0-30cm_mean'
    SOILTYPE_CODES = {'-999': "NODATA", '0': 'MINERAL', '1': 'ORGANIC'}
    CUTOFF_POINT = 40

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "soil type in area",
            variables: [str] = ["soil_type"],
            units: [str] = ["-"],
            formatters: List[OutputFormatter] = [soiltype_fomatter]) -> None:
        super().__init__(base_data, name, variables, units, formatters)

    def calculate(self) -> SoilTypeParameter:
        """ """
        target_geom = self.base_data.geometry()
        # Soil Type
        soil_carbon_cat = ee.Image(
            self.AUX_DATA_PATH).multiply(0.1).gte(self.CUTOFF_POINT)
        # Expected scale = 1000
        projection = ee.Image(soil_carbon_cat).projection()
        scale = projection.nominalScale()
        stats = soil_carbon_cat.reduceRegion(**{
            'reducer': ee.Reducer.mode(),
            'geometry': target_geom,
            'scale': scale,
            'maxPixels': 2e11})
        stats = stats.map(
            lambda k, v: ee.Algorithms.If(
                ee.Algorithms.IsEqual(v, None), -999, stats.get(k)))
        metric = ee.Number(stats.get(self.AUX_DATA_FIELD)).format('%.0f')
        modal_soil_category = ee.Dictionary(self.SOILTYPE_CODES).get(metric)
        self._raw_outputs = [RawOutput(
            var_name=self.variables[0], unit=self.units[0],
            value=modal_soil_category)]
        self.format()
        return self


class PopulationParameter(Parameter):
    """ """
    AUX_DATA_PATH = data_config['population_density']['url']
    AREA_CONV: float = 1000*1000

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "population density in area",
            variables: List[str] = ["population", "population_density"],
            units: List[str] = ["-", "-"],
            formatters: List[OutputFormatter] =
            [population_fomatter, population_density_formatter]) -> None:
        super().__init__(base_data, name, variables, units, formatters)

    def calculate(self) -> PopulationParameter:
        """ """
        target_geom = self.base_data.geometry()
        population_img = ee.ImageCollection(self.AUX_DATA_PATH)
        # First image; 2020
        # TODO: How to select a particular year from the image?
        population_img = population_img.limit(
            1, 'system:time_start', False).first()
        # Expected SCALE = 927.67
        projection = ee.Image(population_img).projection()
        scale = projection.nominalScale()
        # Calculate the area of the catchment in km;
        target_area = target_geom.area(1).divide(self.AREA_CONV)
        mean_pop_density = population_img.reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': target_geom,
            'scale': scale,
            'maxPixels': 2e11}).get('population_density')
        pop_count = ee.Number(mean_pop_density).multiply(target_area)
        outputs = (pop_count, mean_pop_density)
        self._raw_outputs = [
            RawOutput(var_name, unit, value) for var_name, unit, value in
            zip(self.variables, self.units, outputs)]
        self.format()
        return self


class TerraClimMeanParameter(Parameter):
    """
    Used to calculate the `pet`, `soil` and `ro' variables (target_var).
    """

    AUX_DATA_PATH = data_config['terraclimate']['url']

    def __init__(
            self, base_data: ee.FeatureCollection,
            averaging_type: str,
            name: str = "mean terraclim model variables",
            variables: List[str] = [""],
            units: List[str] = [""],
            formatters: List[OutputFormatter] = [], **kwargs) -> None:
        super().__init__(base_data, name, variables, units, formatters)
        self.start_year: int = kwargs['start_year']
        self.end_year: int = kwargs['end_year']
        self.target_var: str = kwargs['target_var']
        self.scale_factor: float = kwargs['scale_factor']
        try:
            self.handle_null_values: bool = kwargs['handle_null_values']
        except KeyError:
            self.handle_null_values: bool = True
        self.averaging_type = averaging_type

    def calculate(self) -> TerraClimMeanParameter:
        """ """

        def aggregate_months_monthly_mean(year):
            """ """
            date_start = ee.Date.fromYMD(year, 1, 1)
            date_end = date_start.advance(1, "year")
            return terraclim_img.filterDate(date_start, date_end)\
                .mean().set({'year': year, 'system:time_start': date_start})

        def aggregate_months_yearly_mean(year):
            """ """
            date_start = ee.Date.fromYMD(year, 1, 1)
            date_end = date_start.advance(1, "year")
            return terraclim_img.filterDate(date_start, date_end)\
                .sum().set({'year': year, 'system:time_start': date_start})

        aggregation_fns: Dict[str, Callable] = {
            'monthly': aggregate_months_monthly_mean,
            'annual': aggregate_months_yearly_mean,
            'yearly': aggregate_months_yearly_mean}

        aggregation_fn = aggregation_fns[self.averaging_type]

        # Get regional values
        def get_regional_value(img, first):
            """ """
            stats = img.reduceRegion(**{
                'reducer': ee.Reducer.mean(),
                'geometry': target_geom,
                'scale': scale,
                'maxPixels': 2e11})
            # Map null values to -999
            stats = stats.map(
                lambda k, v: ee.Algorithms.If(
                    ee.Algorithms.IsEqual(v, None), -999, stats.get(k)))
            metric = stats.get(self.target_var)
            return ee.List(first).add(metric)

        target_years = ee.List.sequence(self.start_year, self.end_year)
        target_geom = self.base_data.geometry()
        logger.debug(
            f"[TerraClimMeanParameter]\n {self.target_var.getInfo()}")
        logger.debug(
            f"[TerraClimMeanParameter]\n {target_years.getInfo()}")
        terraclim_img = ee.ImageCollection(
            self.AUX_DATA_PATH).select([self.target_var])
        # Expected scale = 4638
        projection = ee.Image(terraclim_img.first()).projection()
        scale = projection.nominalScale()
        # Calculation fails with null values using nominal scale
        # scale = 30
        # Convert monthly image collection to yearly
        metric_yearly_cimg = ee.ImageCollection(
            target_years.map(aggregation_fn))
        logger.debug(
            f"[TerraClimMeanParameter]\n {metric_yearly_cimg.getInfo()}"
        )
        results = ee.List([])
        regional_metrics_yearly = metric_yearly_cimg.iterate(
            get_regional_value, results)
        logger.debug(
            "[TerraClimMeanParameter] regional_metrics_yearly: " +
            f"{regional_metrics_yearly.getInfo()}")
        mean_value = ee.Number(
                ee.List(regional_metrics_yearly)
                .filter(ee.Filter.neq('item', -999))
                .map(lambda v: ee.Number(v).multiply(self.scale_factor))
                .reduce('mean'))
        # Handle null values
        if self.handle_null_values:
            mean_value = ee.Algorithms.If(mean_value, mean_value, -999)
        self._raw_outputs = [mean_value]
        self._raw_outputs = [
            RawOutput(self.variables[0], self.units[0], mean_value)]
        self.format()
        return self


class TerraClimMonthlyMeanParameter(TerraClimMeanParameter):
    """ """
    def __init__(
            self, base_data: ee.FeatureCollection,
            averaging_type: str = "monthly",
            name: str = "mean terraclim monthly model variables",
            variables: [str] = ["terraclim_monthly mean"],
            units: [str] = [""],
            formatters: List[OutputFormatter] =
            [terra_clim_monthly_default_formatter],
            handle_null_values: bool = True, **kwargs) -> None:
        super().__init__(
            base_data, averaging_type, name, variables, units, formatters,
            handle_null_values=handle_null_values, **kwargs)


class TerraClimAnnualMeanParameter(TerraClimMeanParameter):
    """ """
    def __init__(
            self, base_data: ee.FeatureCollection,
            averaging_type: str = "yearly",
            name: str = "mean terraclim annual model variables",
            variables: [str] = ["terraclim_annual mean"],
            units: [str] = [""],
            formatters: List[OutputFormatter] =
            [terra_clim_annual_default_formatter],
            handle_null_values: bool = False, **kwargs) -> None:
        super().__init__(
            base_data, averaging_type, name, variables, units, formatters,
            handle_null_values=handle_null_values, **kwargs)


class SmapMeanParameter(Parameter):
    """ """
    AUX_DATA_PATH = data_config['smap']['url']

    def __init__(
            self, base_data: ee.FeatureCollection,
            averaging_type: str,
            name: str = "mean smap variables",
            variables: List[str] = ["smap_mean"],
            units: List[str] = [""],
            formatters: List[OutputFormatter] = [smap_mean_default_formatter],
            **kwargs) -> None:
        super().__init__(base_data, name, variables, units, formatters)
        self.start_year: int = kwargs['start_year']
        self.end_year: int = kwargs['end_year']
        self.target_var: str = kwargs['target_var']
        try:
            self.handle_null_values: bool = kwargs['handle_null_values']
        except KeyError:
            self.handle_null_values = True
        self.averaging_type = averaging_type

    def calculate(self) -> SmapMeanParameter:
        """ """

        def aggregate_months_monthly_mean(year):
            """ """
            date_start = ee.Date.fromYMD(year, 1, 1)
            date_end = date_start.advance(1, "year")
            return smap_10km_img_collection\
                .filterDate(date_start, date_end).mean()\
                .set({'year': year, 'system:time_start': date_start})

        def aggregate_months_yearly_mean(year):
            """ """
            date_start = ee.Date.fromYMD(year, 1, 1)
            date_end = date_start.advance(1, "year")
            return smap_10km_img_collection\
                .filterDate(date_start, date_end).sum()\
                .set({'year': year, 'system:time_start': date_start})

        aggregation_fns: Dict[str, Callable] = {
            'monthly': aggregate_months_monthly_mean,
            'annual': aggregate_months_yearly_mean,
            'yearly': aggregate_months_yearly_mean}

        # Get regional values
        def get_regional_value(img, first) -> ee.List:
            """ """
            stats = img.reduceRegion(**{
                'reducer': ee.Reducer.mean(),
                'geometry': target_geom,
                'scale': scale,
                'maxPixels': 2e11})
            # Map null values to -999
            stats = stats.map(
                lambda k, v: ee.Algorithms.If(
                    ee.Algorithms.IsEqual(v, None), -999, stats.get(k)))
            metric = stats.get(self.target_var)
            return ee.List(first).add(metric)

        target_years = ee.List.sequence(self.start_year, self.end_year)
        target_geom = self.base_data.geometry()
        logger.debug(
            f"[SmapMeanParameter] target var\n {self.target_var.getInfo()}")
        logger.debug(
            f"[SmapMeanParameter] target years\n {target_years.getInfo()}")
        smap_10km_img_collection = ee.ImageCollection(
            self.AUX_DATA_PATH).select([self.target_var])
        # Expected SCALE = 10000
        projection = ee.Image(smap_10km_img_collection.first()).projection()
        scale = projection.nominalScale()
        # Convert monthly image collection to yearly or monthly average
        # (depending on the choice of the averaging function/type)
        metric_yearly_cimg = ee.ImageCollection(
            target_years.map(aggregation_fns[self.averaging_type]))
        logger.debug(
            "[SmapMeanParameter] metric yearly\n " +
            f"{metric_yearly_cimg.getInfo()}")
        results = ee.List([])
        regional_metrics_yearly = metric_yearly_cimg.iterate(
            get_regional_value, results)
        logger.debug(
            "[SmapMeanParameter] regional metric yearly\n " +
            f"{regional_metrics_yearly.getInfo()}")
        mean_value = ee.Number(
            ee.List(regional_metrics_yearly)
            .filter(ee.Filter.neq('item', -999))
            .reduce('mean'))
        if self.handle_null_values:
            # Handle null values
            mean_value = ee.Algorithms.If(mean_value, mean_value, -999)
        self._output = mean_value
        self._raw_outputs = [RawOutput(
            var_name=self.variables[0], unit=self.units[0],
            value=mean_value)]
        self.format()
        return self


class SmapMonthlyMeanParameter(SmapMeanParameter):
    """ """
    def __init__(
            self, base_data: ee.FeatureCollection,
            averaging_type: str = "monthly",
            name: str = "mean smap monthly model variables",
            variables: List[str] = ["smap_monthly mean"],
            units: List[str] = [""],
            formatters: List[OutputFormatter] = [smap_mean_default_formatter],
            handle_null_values: bool = True, **kwargs) -> None:
        super().__init__(
            base_data, averaging_type, name, variables, units, formatters,
            handle_null_values=handle_null_values, **kwargs)


class SmapAnnualMeanParameter(SmapMeanParameter):
    """ """
    def __init__(
            self, base_data: ee.FeatureCollection,
            averaging_type: str = "yearly",
            name: str = "mean smap annual model variables",
            variables: List[str] = ["smap_annual mean"],
            units: List[str] = [""],
            formatters: List[OutputFormatter] = [smap_mean_default_formatter],
            handle_null_values: bool = False, **kwargs) -> None:
        super().__init__(
            base_data, averaging_type, name, variables, units, formatters,
            handle_null_values=handle_null_values, **kwargs)


if __name__ == '__main__':
    p1 = MeanSlopePercParameter(base_data=None)
