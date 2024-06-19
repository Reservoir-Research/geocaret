"""Calculates parameters in river shapes"""
from __future__ import annotations
from typing import List, Any
import pathlib
import ee
import heet.log_setup
from heet.parameters.parameters import (
    Parameter, RawOutput, OutputFormatter,
    FormattedOutputValue)
from heet.utils import get_package_file, read_config, set_logging_level

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)
logger_config: dict = read_config(
    get_package_file('./config/logging_levels.yaml'))
set_logging_level(
    logger=logger, level=logger_config['parameters']['river'])

data_config_file: pathlib.PosixPath = get_package_file(
    './config/emissions/data.yaml')
data_config = read_config(data_config_file)

# For adding to parameter names, if needed
VAR_PREFIX = "ms_"


# (Default) formatting functions
def river_length_formatter(
        output: RawOutput, **kwargs: Any) -> FormattedOutputValue:
    """ """
    string_format = kwargs.get('string_format', "%.3f")
    return ee.Number(output.value).format(string_format)


class RiverLengthParameter(Parameter):
    """ """
    VALUE_FIELD = 'ee_length_km'

    def __init__(
            self, base_data: ee.FeatureCollection,
            name: str = "inundated river length",
            variables: List[str] = ["length"],
            units: List[str] = ["km"],
            formatters: List[OutputFormatter] =
            [river_length_formatter]) -> None:
        super().__init__(base_data, name, variables, units, formatters)

    def calculate(self) -> RiverLengthParameter:
        """ """
        def set_river_length(rfeat):
            calculated_length = ee.Number(rfeat.geometry().length()).divide(1000)
            rfeat = rfeat.set(self.VALUE_FIELD, calculated_length)
            return rfeat
        inundated_river_ftc = self.base_data.map(set_river_length)
        inundated_river_length = ee.Number(
            inundated_river_ftc.aggregate_array(self.VALUE_FIELD)
            .reduce(ee.Reducer.sum())).multiply(100).round().divide(100)
        self._raw_outputs = [RawOutput(
            var_name=self.variables[0], unit=self.units[0],
            value=inundated_river_length)]
        self.format()
        return self
