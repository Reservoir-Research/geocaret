"""Calculates parameters in reservoir shapes"""
from __future__ import annotations
from typing import Optional, Dict, Callable, Any, List
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
    logger=logger, level=logger_config['parameters']['reservoir'])

data_config_file: pathlib.PosixPath = get_package_file(
    './config/emissions/data.yaml')
data_config = read_config(data_config_file)

# For adding to parameter names, if needed
VAR_PREFIX = "r_"

# (Default) formatting functions
def mghr_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.3f")
    return ee.Number(output.value).format(string_format)

def mean_soil_org_c_formatter_res(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.3f")
    return ee.Number(output.value).format(string_format)

def landcover_bysoil_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.3f")
    start_index = kwargs.get('start_index', 0)
    landcover_bysoil_fracs = output.value.map(
        lambda value : ee.Number(value).format(string_format))
    indexed_var_names = output.name_rollout(start_index)
    return {
        var_name: ee.List(landcover_fracs).get(index) for
        var_name, index in
        zip(indexed_var_names, range(0, len(indexed_var_names)))}

def mean_monthly_temps_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.0f")
    not_defined_val = kwargs.get('not_defined', "ND")
    err_val = kwargs.get('err_val', -999)
    temp_profile = output.value.map(
        lambda value : ee.Algorithms.If(
            ee.Number(value).neq(err_val),
            ee.Number(value).format(string_format),
            not_defined_val)
        )
    indexed_var_names = output.name_rollout(start_index)
    return {
        var_name: ee.List(temp_profile).get(index) for
        var_name, index in
        zip(indexed_var_names, range(0, len(indexed_var_names)))}

def max_depth_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.0f")
    return ee.Number(output.value).format(string_format)

def mean_depth_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.0f")
    return ee.Number(output.value).format(string_format)


def terraclim_mghr_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    return ee.String(output.value)


class MGHRParameter(Parameter):
    """Calculates a 3x1 list of mean horizontal radiation values
        1. Annual mean horizontal radiation
        2. Mean horizontal radiation between November and March
        3. Mean horizontal radiation between May and September
    """

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "mean annual global horizontal irradiance",
            variables: List[str] = [
                "mghr_all", "mghr_nov_mar", "mghr_may_sept"],
            units: List[str] = ["kWh/m2/d", "kWh/m2/d", "kWh/m2/d"],
            formatters: List[OutputFormatter]=[mghr_formatter]) -> None:
        super().__init__(base_data, name, variables, units, formatter)

    AUX_DATA_PATH = data_config['mghr']['url']
    NOV_MAR = ['nov', 'dec', 'jan', 'feb', 'mar']
    MAY_SEPT = ['may', 'jun', 'jul', 'aug', 'sep']

    def calculate(self, **kwargs: Any) -> MGHRParameter:
        """ """
        def mgr_mean(months: list):
            """Calculate mean over a number of months ."""
            return ee.List(ghi_nasa_low.filterBounds(catch_geom)
                           .reduceColumns(ee.Reducer.mean().repeat(
                                len(months)), months)
                           .get('mean')).reduce(ee.Reducer.mean())

        catch_geom = self.base_data.geometry()
        ghi_nasa_low = ee.FeatureCollection(self.AUX_DATA_PATH)
        mghr_all = (ghi_nasa_low.filterBounds(catch_geom).reduceColumns(
            ee.Reducer.mean(), ['annual']).get('mean'))
        mghr_nov_mar = mgr_mean(months=self.NOV_MAR)
        mghr_may_sept = mgr_mean(months=self.MAY_SEPT)
        mghr_values = (mghr_all, mghr_nov_mar, mghr_may_sept)
        logger.debug(
            "[MGHR Parameter] [mghr_all]: %f",
            mghr_all.getInfo())
        logger.debug(
            "[MGHR Parameter] [mghr_nov_mar]: %f",
            mghr_nov_mar.getInfo())
        logger.debug(
            "[MGHR Parameter] [mghr_may_sept]: %f",
            mghr_may_sept.getInfo())
        self._raw_outputs = [
            RawOutput(var_name=var_name, unit=unit, value=value) for
            var_name, unit, value in zip(
                self.variables, self.units, mghr_values)]
        self.format()
        return self


class TerraClimMGHRParameter(Parameter):
    """Calculates a 3x1 list of mean horizontal radiation values using
    Terraclim dataset.
        1. Annual mean horizontal radiation
        2. Mean horizontal radiation between November and March
        3. Mean horizontal radiation between May and September
    """
    AUX_DATA_PATH = data_config['terraclimate']['url']
    TARGET_VAR = 'srad'
    TARGET_VAR_SCALE = 0.1
    DAYS_PER_MONTH = ee.Dictionary({
        '1':  31, '2' : 28, '3' : 31,'4' : 30,'5' : 31,'6' : 30,
        '7' : 31, '8' : 31, '9' : 30,'10' :31,'11' : 30, '12' : 31})

    def __init__(
            self, base_data: ee.FeatureCollection,
            averaging_type: str,
            name: str = "mean annual global horizontal irradiance terraclim",
            variables: List[str] = [
                "mghr_all", "mghr_nov_mar", "mghr_may_sept"],
            units: List[str] = ["kWh/m2/d", "kWh/m2/d", "kWh/m2/d"],
            formatters: List[OutputFormatter] = [terraclim_mghr_formatter],
            **kwargs) -> None:
        super().__init__(base_data, name, variables, units, formatters)
        self.start_year: int = kwargs['start_year']
        self.end_year: int = kwargs['end_year']
        self.target_var: str = kwargs['target_var']

    def calculate(self) -> TerraClimMGHRParameter:

        def mean_total_energy(k, v):
            month_no = ee.Number.parse(k)
            seconds_in_month = ee.Date.unitRatio('days', 'second').multiply(v)
            img_month = (
                terraclim_img_col.filter(
                    ee.Filter.calendarRange(start_yr, end_yr,'year'))
                    .filter(ee.Filter.calendarRange(month_no, month_no,'month'))
                    .map(lambda img : img.multiply(target_var_scale_factor)
                    .multiply(seconds_in_month))
            ).mean()
            return img_month

        def mghr(months: List[str]) -> ee.Number:
            """ """
            J2KWH = 3600000
            mghr = ee.Number(
                ee.ImageCollection(mean_tot_energy_per_month.select(
                    **{'selectors': months}).values())
                 # Mean total annual energy; J m-2
                .sum()
                # Mean annual energy per day; J m-2 d-1
                .divide(ee.Date.unitRatio('year', 'days')
                .multiply(len(months)/12))
                # Mean annual energy per day; kWh m-2 d-1
                .divide(J2KWH)
                .reduceRegion(**{
                    'reducer': ee.Reducer.mean(),
                    'geometry': target_geom,
                    'scale': projection_scale
                }).get(self.TARGET_VAR))
            return mghr

        target_geom = self.base_data.geometry()
        target_var = ee.List([self.TARGET_VAR])
        target_var_scale_factor = ee.Number(self.TARGET_VAR_SCALE)
        target_years = ee.List.sequence(self.start_year, self.end_year)
        terraclim_img_col =  ee.ImageCollection(self.AUX_DATA_PATH)\
            .select(target_var)
        # Expected SCALE = 4638
        projection = ee.Image(terraclim_img_col.first()).projection()
        projection_scale = projection.nominalScale()

        all_months = [str(num+1) for num in range(0,12)]
        nov_mar_months = all_months[10:12] + all_months[0:3]
        may_sept_months = all_monhs[4:9]

        # J m-2
        mean_tot_energy_per_month: ee.Dictionary = \
            self.DAYS_PER_MONTH.map(mean_total_energy)

        mghr_all = mghr(months=all_months)
        mghr_nov_mar = mghr(months=nov_mar_months)
        mghr_may_sept = mghr(months=may_sept_months)
        mghr_values = (mghr_all, mghr_nov_mar, mghr_may_sept)
        logger.debug(
            "[MGHR Terraclim Parameter] [mghr_all]: %f",
            mghr_all.getInfo())
        logger.debug(
            "[MGHR Terraclim Parameter] [mghr_nov_mar]: %f",
            mghr_nov_mar.getInfo())
        logger.debug(
            "[MGHR Terraclim Parameter] [mghr_may_sept]: %f",
            mghr_may_sept.getInfo())
        self._raw_outputs = [
            RawOutput(var_name=var_name, unit=unit, value=value) for
            var_name, unit, value in zip(
                self.variables, self.units, mghr_values)]
        self.format()
        return self


class LandCoverBySoilParameter(Parameter):
    """[what does this parameter calculate?]

    Calculation of soil type:
        If soil carbon in the area >=[CUTOFF_POINT] kg/m2 -> soil type Organic
        If soil carbon in the area <[CUTOFF_POINT] kg/m2 -> soil type Mineral
    """
    AUX_DATA_PATH_1 = data_config['org_soil_carbon']['url']
    AUX_DATA_PATH_2 = data_config['landcover_esa']['url']
    ESA_IHA_CODE_MAP = {
        0: 0, 10: 1, 20: 1, 12: 2, 50: 2, 60: 2, 61: 2, 62: 2, 70: 2, 71: 2,
        72: 2, 80: 2, 81: 2, 82: 2, 90: 2, 100: 3, 110: 3, 120: 3, 121: 3,
        122: 3, 130: 3, 140: 3, 150: 3, 152: 3, 153: 3, 151: 3, 30: 3, 40: 3,
        11: 3, 160: 4, 170: 4, 180: 4, 190: 5, 200: 6, 201: 6, 202: 6, 210: 7,
        220: 8}
    IHA_CATEGORIES = {
        '0': 'Mineral - No Data', '1': 'Mineral - Croplands',
        '2': 'Mineral - Forest', '3': 'Mineral - Grassland/Shrubland',
        '4': 'Mineral - Wetlands', '5': 'Mineral - Settlements',
        '6': 'Mineral - Bare Areas', '7': 'Mineral - Water Bodies',
        '8': 'Mineral - Permanent snow and ice', '9': 'Organic- No Data',
        '10': 'Organic - Croplands', '11': 'Organic - Forest',
        '12': 'Organic - Grassland/Shrubland', '13': 'Organic - Wetlands',
        '14': 'Organic - Settlements', '15': 'Organic - Bare Areas',
        '16': 'Organic - Water Bodies', '17': 'Organic - Permanent snow and ice',
        '18': 'No Data - No Data', '19': 'No Data - Croplands',
        '20': 'No Data - Forest', '21': 'No Data - Grassland/Shrubland',
        '22': 'No Data - Wetlands', '23': 'No Data - Settlements',
        '24': 'No Data - Bare Areas', '25': 'No Data - Water Bodies',
        '26': 'No Data - Permanent snow and ice'}
    CUTOFF_POINT_1 = 40
    VALUE_FIELD = "land_use"
    KEY_TO_INT = {'0': 0, '1': 1, 'null': 2}

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "land cover catergory by soil type",
            variables: List[str] = ["landcover_bysoil"],
            units: List[str] = ["-"],
            formatter: List[OutputFormatter] =
            [landcover_bysoil_formatter]) -> None:
        super().__init__(base_data, name, variables, units, formatter)

    def calculate(self) -> LandCoverBySoilParameter:
        """ """
        def generate_codes(digit):
            """ """
            group_no = ee.Number.int(ee.Dictionary(digit).get('group'))
            code = ee.Number(
                ee.Dictionary(ee.Dictionary(digit).get('histogram'))
                .keys().map(
                    lambda key: ee.Number(
                        group_no.add(
                            ee.Number(ee.Dictionary(self.KEY_TO_INT).get(key))
                            .multiply(group_count.divide(3)))
                        ).format("%.0f")))
            return code

        soil_carbon_cat = ee.Image(self.AUX_DATA_PATH_1).multiply(0.1).gte(
            self.CUTOFF_POINT_1)
        landcover_esa = ee.Image(self.AUX_DATA_PATH_2)
        # Expected SCALE = 300
        projection = ee.Image(landcover_esa).projection()
        scale = projection.nominalScale()
        landcover_iha = landcover_esa.remap(
            list(self.ESA_IHA_CODE_MAP.keys()),
            list(self.ESA_IHA_CODE_MAP.values())).select(
                ['remapped'], [self.VALUE_FIELD])
        land_geom = self.base_data.geometry()
        iha_categories = ee.Dictionary(self.IHA_CATEGORIES)
        # Histogram
        frequency = landcover_iha.addBands(soil_carbon_cat).reduceRegion(**{
            'reducer': ee.Reducer.frequencyHistogram().unweighted().group(0),
            'geometry': land_geom,
            'scale': scale,
            'maxPixels': 2e1}).get('groups')
        total_count = ee.List(frequency).map(
            lambda d: ee.List(ee.Dictionary(
                ee.Dictionary(d).get('histogram')).toArray().toList().map(
                lambda v: v)
            ).reduce(ee.Reducer.sum())).reduce(ee.Reducer.sum())
        fractions = ee.List(frequency).map(
            lambda d: ee.Dictionary(
                ee.Dictionary(d).get('histogram')).toArray().toList().map(
                lambda v: ee.Number(v).divide(total_count))
            ).flatten()
        group_count = iha_categories.keys().length()
        codes = ee.List(ee.List(frequency).map(generate_codes)).flatten()
        fractions_dict = ee.Dictionary.fromLists(codes, fractions)
        fractions_list = ee.List.sequence(0, group_count.subtract(1))
        fractions_list_str = fractions_list.map(
            lambda i: ee.Number(i).format("%.0f"))
        logger.debug(f"Frequency: {frequency.getInfo()}")
        logger.debug(f"Fractions: {fractions.getInfo()}")
        logger.debug(f"Codes: {codes.getInfo()}")
        logger.debug(f"Fractions list: {fractions_list_str.getInfo()}")
        logger.debug(f"Fractions dict: {fractions_dict.getInfo()}")
        raw_output_value = fractions_list_str.map(
            lambda i: ee.Number(fractions_dict.get(i, ee.Number(0))))
        self._raw_outputs = [RawOutput(
            var_name=self.variables[0],
            unit=self.units[0],
            value=raw_output_value)]
        self.format()
        return self


class MeanMonthlyTempsParameter(Parameter):
    """ """
    AUX_DATA_PATH = data_config['temperatures']['url']

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "mean monthly temperatures",
            variables: List[str] = ["mean_temp"],
            units: List[str] = ["degC"],
            formatters: List[OutputFormatter] =
            List[mean_monthly_temps_formatter]) -> None:
        super().__init__(base_data, name, variables, units, formatter)

    def calculate(self) -> MeanMonthlyTempsParameter:
        """ """
        def monthly_temp(month: ee.Number) -> ee.Number:
            """ """
            stats = ee.Image(ee.List(temperature_list).get(month))\
                .reduceRegion(**{
                    'reducer': ee.Reducer.mean(),
                    'geometry': reservoir_geom,
                    'scale': scale,
                    'maxPixels': 2e11})
            stats = stats.map(
                lambda k, v: ee.Algorithms.If(
                    ee.Algorithms.IsEqual(v, None), -999, stats.get(k)))
            return ee.Number(stats.get('b1')).multiply(10).round().divide(10)

        # Mean monthly temperatures
        reservoir_geom = self.base_data.geometry()
        ave_temperatures = ee.ImageCollection(self.AUX_DATA_PATH)
        temperature_list = ave_temperatures.select(['b1']).toList(12)
        # Expected SCALE = 30
        projection = ee.Image(ave_temperatures.first()).projection()
        scale = projection.nominalScale()
        month_list = ee.List.sequence(0, 11, 1)
        temperatures = month_list.map(monthly_temp)
        logger.debug(
            f"MeanMonthlyTempsParameter temperatures: {temperatures.getInfo()}")
        self._raw_outputs = [RawOutput(
            var_name=self.variables[0],
            unit=self.units[0],
            value=temperatures)]
        self.format()
        return self


class MeanDepthParameter(Parameter):
    """ """
    AUX_DATA_PATH = data_config['dem']['url']
    BASE_DATA_FIELD = '_imputed_water_level'
    VALUE_FIELD = 'elevation'

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "mean depth of a reservoir",
            variables: List[str] =[ "mean_depth_m"],
            units: List[str] = ["m"],
            formatters: List[OutputFormatter]=
            [mean_depth_formatter]) -> None:
        super().__init__(base_data, name, variables, units, formatter)

    def calculate(self) -> MeanDepthParameter:
        """ """
        reservoir_geom = self.base_data.geometry()
        # Depth = water surface elevation - elevation
        water_level = ee.Number.parse(
            self.base_data.first().get(self.BASE_DATA_FIELD))
        logger.debug(
            f"MeanDepthParameter base_data: {self.base_data.getInfo()}")
        logger.debug(
            f"MeanDepthParameter water_level: {water_level.getInfo()}")
        min_elevation_dam = MinDamElevationParameter(self.base_data)\
            .calculate()
        water_level_elevation = ee.Number(min_elevation_dam).add(water_level)
        dem_img = ee.Image(self.AUX_DATA_PATH)
        # Expected SCALE = 30
        projection = ee.Image(dem_img).projection()
        scale = projection.nominalScale()
        mean_depth = ee.Number(
            dem_img.multiply(-1).add(water_level_elevation)
            .reduceRegion(**{
                'reducer': ee.Reducer.mean(),
                'geometry': reservoir_geom,
                'scale': scale,
                'maxPixels': 2e11}).get(self.VALUE_FIELD))
        self._raw_outputs = [RawOutput(
            var_name=self.variables[0],
            unit=self.units[0],
            value=mean_depth)]
        self.format()
        return self


class MaxDepthParameter(Parameter):
    """ """
    AUX_DATA_PATH = data_config['dem']['url']
    BASE_DATA_FIELD = '_imputed_water_level'
    VALUE_FIELD = 'elevation'

    def __init__(
            self, base_data: ee.FeatureCollection,
            calc_option: str = "default",
            name: str = "maximum depth of a reservoir",
            variables: List[str] = ["maximum_depth_m"],
            units: List[str] = ["m"],
            formatter: List[OutputFormatter] =
            List[max_depth_formatter]) -> None:
        super().__init__(base_data, name, variables, units, formatter)
        self.calc_option = calc_option

    def calculate(self) -> MaxDepthParameter:
        """Calculate maximum depth using different alternative methods"""
        output_map: Dict[str, Callable] = {
            "default": self._calculate_default,
            "alt1": self._calculate_alt1,
            "alt2": self._calculate_alt2}
        self._raw_outputs = [RawOutput(
            var_name=self.variables[0],
            unit=self.units[0],
            value=output_map[self.calc_option]())]
        self.format()
        return self

    # Outputs
    def _calculate_default(self) -> ee.Number:
        """ """
        reservoir_geom = self.base_data.geometry()
        # Depth = water surface elevation - elevation
        water_level = ee.Number.parse(
            self.base_data.first().get(self.BASE_DATA_FIELD))
        min_elevation_dam = \
            MinDamElevationParameter(self.base_data).calculate()
        water_level_elevation = ee.Number(min_elevation_dam).add(water_level)
        dem_img = ee.Image(self.AUX_DATA_PATH)
        # Expected SCALE = 30
        projection = ee.Image(dem_img).projection()
        scale = projection.nominalScale()
        max_depth = ee.Number(
            dem_img.multiply(-1).add(water_level_elevation)
            .reduceRegion(**{
                'reducer': ee.Reducer.max(),
                'geometry': reservoir_geom,
                'scale': scale,
                'maxPixels': 2e11}).get(self.VALUE_FIELD))
        return max_depth

    def _calculate_alt1(self) -> ee.Number:
        """ """
        # Max Depth = maximum elevation - minimum elevation
        max_elevation = ee.Number(
            MaxElevationParameter(self.base_data).calculate())
        min_elevation_dam = ee.Number(
            MinDamElevationParameter(self.base_data).calculate())
        max_depth = ee.Number(max_elevation.subtract(min_elevation_dam))
        return max_depth

    def _calculate_alt2(self) -> ee.Number:
        """ """
        # Max Depth = maximum elevation - minimum elevation
        max_elevation = ee.Number(
            MaxElevationParameter(self.base_data).calculate())
        min_elevation = ee.Number(
            MinElevationParameter(self.base_data).calculate())
        return ee.Number(max_elevation.subtract(min_elevation))






class MinDamElevationParameter(Parameter):
    """ """
    AUX_DATA_PATH = data_config['dem']['url']
    LAT_FIELD: str = "ps_lat"
    LON_FIELD: str = "ps_lon"

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "minimum elevation of a dam",
            variables: List[str] = ["minimum_dam_elevation"],
            units: List[str] = ["m"],
            formatters: List[OutputFormatter]) -> None:
        super().__init__(base_data, name, variables, units, formatter)

    def calculate(self) -> MinDamElevationParameter:
        """ """
        dem_img = ee.Image(self.AUX_DATA_PATH)
        # Expected SCALE = 30
        projection = ee.Image(dem_img).projection()
        scale = projection.nominalScale()
        dam_latitude = ee.Number(
            ee.Feature(self.base_data.first()).get(self.LAT_FIELD))
        dam_longitude = ee.Number(
            ee.Feature(self.base_data.first()).get(self.LON_FIELD))
        dam_point_location = ee.Geometry.Point(dam_longitude, dam_latitude)
        pt_min_elevation = dem_img.reduceRegion(**{
          'reducer': ee.Reducer.min(),
          'geometry': dam_point_location,
          'scale': scale,
          'maxPixels': 2e11}).get('elevation')
        self._output = pt_min_elevation
        return self


class ElevationParameter(Parameter):
    """Elevation (min/max) of a reservoir"""
    AUX_DATA_PATH = data_config['dem']['url']
    VALUE_FIELD = 'elevation'
    REDUCER_MAP: dict = {"min": ee.Reducer.min(), "max": ee.Reducer.max()}

    def __init__(
            self, base_data: ee.FeatureCollection,
            min_max: str,
            name: str = "elevation of a dam",
            variables: List[str] = ["dam_elevation"],
            units: List[str] = ["m"],
            formatters: List[OutputFormatter]) -> None:
        super().__init__(base_data, name, variables, units, formatter)
        self.reducer: ee.Reducer = self.REDUCER_MAP[min_max]

    def calculate(self) -> ElevationParameter:
        """ """
        reservoir_geom = self.base_data.geometry()
        dem_img = ee.Image(self.AUX_DATA_PATH)
        # Expected SCALE = 30
        projection = ee.Image(dem_img).projection()
        scale = projection.nominalScale()
        self._output = ee.Number(dem_img.reduceRegion(**{
            'reducer': self.reducer,
            'geometry': reservoir_geom,
            'scale': scale,
            'maxPixels': 2e11}).get(self.VALUE_FIELD))
        return self


class MinElevationParameter(ElevationParameter):
    """ """
    # Not needed if maximum_depth_alt2 not used.
    def __init__(
            self, base_data: ee.FeatureCollection,
            min_max: str = "min",
            name: List[str] = ["minimum elevation of a reservoir"],
            variables: List[str] = ["min_reservoir_elevation"],
            units: List[str] = ["m"],
            formatters: List[OutputFormatter]) -> None:
        super().__init__(base_data, min_max, name, variables, units, formatter)


class MaxElevationParameter(ElevationParameter):
    """ """
    # Not needed if maximum_depth_alt1, maximum_depth_alt2 not used.
    def __init__(
            self, base_data: ee.FeatureCollection,
            min_max: str = "max",
            name: str = "maximum elevation of a reservoir",
            variables: [str] = ["max_reservoir_elevation"],
            units: [str] = ["m"]) -> None:
        super().__init__(base_data, min_max, name, variables, units, formatter)
