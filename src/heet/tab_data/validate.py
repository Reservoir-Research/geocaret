""" Functions for veryfying tabular data using frictionless framework """
from abc import ABC, abstractmethod
import pathlib
import copy
from typing import Iterator, List, Callable, Dict, Optional, NamedTuple
import pandas as pd
from frictionless import validate
from frictionless import errors
import heet.log_setup
from heet.tab_data.schemas import Schema
from heet.tab_data.interfaces import Data

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)


class ValidationReport(NamedTuple):
    """Structure for storing results of tabular data validation.

    Attributes:
        valid: Boolean flag stating whether the data has is valid.
        message: String with error messages encountered during checking.
    """
    valid: bool
    message: str


class Validation(ABC):
    """ """
    @abstractmethod
    def run(self, row: pd.Series) -> Iterator[errors.RowError]:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class ValueValidation(Validation):
    """Row validator that makes sure that the value in the list of variables
       / fields are within the specified ranges."""

    def __init__(self, name: str, variables: List[str], min_value: float,
                 max_value: float, condition: str) -> None:
        """Object for validating values in a data table."""
        self._name = name
        self.variables = variables
        self.min_value = min_value
        self.max_value = max_value
        self.condition = condition
        self.problem_fields: str = ""
        self._comp_methods: Dict[str, Callable] = {
            'min-max': lambda value: self.min_value < value <= self.max_value,
            'above-max': lambda value: value > self.max_value}

    @property
    def name(self) -> str:
        return self._name

    def run(self, row: pd.Series) -> Iterator[errors.RowError]:
        """ Detect and flag improbable values in data row """
        value_correct: bool = True
        marked_fields = []
        for variable in self.variables:
            check_conditions: List[bool] = [
                variable in row,
                row[variable] is not None,
                not isinstance(row[variable], str)]
            if all(check_conditions):
                try:
                    if self._comp_methods[self.condition](row[variable]):
                        value_correct = False
                        marked_fields.append(variable)
                except KeyError as err:
                    raise KeyError(
                        f'Comparison method {self.condition} not supported') \
                        from err
        self.problem_fields = ", ".join(marked_fields)
        if not value_correct:
            note = f"An improbable value of {self.name} was detected in " + \
                   f"fields: {self.problem_fields}."
            yield errors.RowError.from_row(row, note=note)


class HPDataValidation(Validation):
    """Row validator that checks if sufficient data has been provided to model
    a hydroelectric reservoir."""

    def __init__(self, name: str, height_var: str = 'dam_height',
                 water_level_var: str = 'water_level',
                 power_capacity_var: str = 'power_capacity', *args, **kwargs):
        """ """
        super().__init__(*args, **kwargs)
        self._name = name
        self.checked_vars = [height_var, water_level_var, power_capacity_var]

    @property
    def name(self) -> str:
        return self._name

    def run(self, row: pd.Series) -> Iterator[errors.RowError]:
        """ Check if enough data has been provided to describe a hydroelectric
            reservoir """
        missing_values = 0
        for variable in self.checked_vars:
            if variable not in row or variable is None:
                missing_values += 1
        if missing_values == 3:
            note = "A non-missing value must be provided for at least " \
                   "one of: " + ", ".join(self.checked_vars)
            yield errors.RowError.from_row(row, note=note)


class DataValidator:
    """Data validation class that uses frictionless framework for checking
    tabular data for incorrect/implausible values"""
    def __init__(self, schema: Schema,
                 validations: Optional[List[Validation]] = None):
        """ """
        self.validations: List[Validation] = []
        if validations:
            self.validations.extend(validations)
        self.schema = schema

    def list_validations(self) -> List[str]:
        """List all registered validation function names"""
        return [validator.name for validator in self.validations]

    def add_validation(self, validation: Validation) -> None:
        """Appends a validation object to the list of validators that
        will be executed as a batch."""
        self.validations.append(validation)

    def validate(self, data: Data,
                 csv_report_path: pathlib.Path,
                 adapt_schema_to_data: bool = True) -> ValidationReport:
        """Validata data using frictionless framework schema and list of
        validation checks."""
        for validation in self.validations:
            check_list = []

            # Define a function returning the validation object's method
            # as a function (required for the frictionless framework)
            def check_fun(row, obj=validation):
                return obj.run(row)
            check_list.append(copy.copy(check_fun))

        if adapt_schema_to_data:
            self.schema.adapt_to_data(data=data.data)
        report = validate(
            data.data,
            schema=self.schema.schema['schema'],
            checks=check_list)
        if report['stats']['errors'] > 0:
            report_content = report.flatten(
                ["fieldPosition", "rowPosition", "fieldName", "code",
                 "message", "note"])
            df_validation = pd.DataFrame(
                report_content, columns=[
                    "column", "row", "field_name", "error_code",
                    "error_message", "note"])
            df_validation.to_csv(csv_report_path, index=False)
            error_messages = [
                "  - " + e for e in df_validation['error_message'].to_list()]
            emsg = "\n".join(error_messages)
            return ValidationReport(valid=False, message=emsg)
        return ValidationReport(valid=True, message="")


if __name__ == '__main__':
    """ """
