""" """
from __future__ import annotations
import ee
from typing import List, Dict, Any, Optional
import heet.log_setup
from heet.utils import get_package_file, read_config, set_logging_level

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)
logger_config: dict = read_config(
    get_package_file('./config/logging_levels.yaml'))
set_logging_level(
    logger=logger, level=logger_config['profiles']['profile_output'])


class ProfileOutput:
    """ """
    def __init__(
            self,
            output: Optional[Dict[str, Any]] = None,
            *messages: str) -> None:
        """ """
        self.output: Dict[str, Any] = {}
        if output is not None:
            self.output = output
        self.messages = list(messages)

    def update_fc_data(
            self, base_data: ee.FeatureCollection) -> ee.FeatureCollection:
        """Takes a feature collection and update its fields with self.output
        data."""
        updated_fc_data = base_data.map(lambda feat: feat.set(self.output))
        return ee.FeatureCollection(updated_fc_data)

    def add_output(self, name: str, value: str) -> None:
        """Adds outputs dynamically to allow an iterative building of
        ProfileOutput objects."""
        self.output.update({name: value})

    def remove_output(self, name: str) -> None:
        """Remove outputs dynamically to allow dynamic reduction of data in
        ProfileOutput objects."""
        try:
            self.output.pop(name)
        except KeyError:
            pass

    def validate(self, required_variables: List[str]) -> bool:
        """Checks if all required variables are present in the output dict."""
        output_var_set = set(self.output.keys())
        required_var_set = set(required_variables)
        return bool(output_var_set & required_var_set == required_var_set)

    def missing_values(self, *custom_missing_vars: str) -> bool:
        """Checks if any values are missing in the output data.
        Return True is some values in the output data belong to the set of
            values representing missing values."""
        _missing_vars = {'na', 'n/a', 'none', 'nd', ''}
        for missing_var in custom_missing_vars:
            _missing_vars.add(missing_var)

        def to_lower_case(item):
            try:
                item_lower = item.lower()
            except AttributeError:
                item_lower = item
            return item_lower

        output_set = set(map(to_lower_case, set(self.output.values())))
        return bool(output_set & _missing_vars)

    @classmethod
    def from_var_value_lists(cls, variables: List[str], values: List[Any],
                             *messages: str) -> ProfileOutput:
        """Create a profile output from two lists: list of values and list
        of variables."""
        if len(variables) != len(values):
            raise ValueError(
                "Variable and value lists have different lengths.")
        output = dict(zip(variables, values))
        return cls(output, *messages)

    @classmethod
    def empty(cls,
              var_value_pairs: Dict[str, str],
              default_empty_value: str = "NA",
              *messages: str) -> ProfileOutput:
        """Create an empty profile output. Often, creating an empty profile is
        required if the result of a computation results in error, e.g.
        catchment delineation does not succeeed."""
        output: Dict[str, str] = {}
        for var_name, var_value in var_value_pairs.items():
            if var_value.lower() in ['default', 'none']:
                var_value = default_empty_value
            output[var_name] = var_value
        logger.warning(
            'Creating an empty profile output.\n' +
            'If not intentional, possible reasons can be a missing asset or ' +
            'a computing error.')
        return cls(output, *messages)


if __name__ == '__main__':
    """ """
