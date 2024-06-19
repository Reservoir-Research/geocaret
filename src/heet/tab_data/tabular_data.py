""" """
from __future__ import annotations
from typing import List, Union, NamedTuple, Optional
import pathlib
import pandas as pd
from heet.tab_data.interfaces import Data
from heet.tab_data.transformers import DataFrameTransformer
from heet.tab_data.validate import DataValidator, ValidationReport
import heet.log_setup

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)


class FileParsingError(Exception):
    """Exception raised if the opened file cannotbe parsed.

    Attributes:
        message: explanation of the error
    """
    def __init__(
            self,
            message="File could not be parsed."):
        self.message = message
        super().__init__(self.message)


class TabularData(Data):
    """ """

    class FieldStatus(NamedTuple):
        """Structure for storing results of tabular data checks.

        Attributes:
            valid: Boolean flag stating whether the data has all fields valid.
            issues: Strings with error messages encountered during checking.
        """
        valid: bool
        issues: str

    def __init__(self, data: pd.DataFrame,
                 transformer: Optional[DataFrameTransformer] = None,
                 validator: Optional[DataValidator] = None) -> None:
        """ """
        self._data = data
        self._transformer = transformer
        self._validator = validator
        self.validation_report: Optional[ValidationReport]=None

    @staticmethod
    def clean_field_names(data: pd.DataFrame) -> pd.DataFrame:
        """Strip spaces and ensure lower case in dataframe's column names."""
        field_names = data.head()
        data.columns = [f.strip().lower() for f in field_names]
        return data

    @property
    def transformer(self) -> None:
        return self._transformer

    @transformer.setter
    def transformer(self, transformer: DataFrameTransformer) -> None:
        self._transformer = transformer

    @property
    def validator(self) -> None:
        return self._validator

    @validator.setter
    def validator(self, validator) -> None:
        self._validator = validator

    @classmethod
    def from_csv(
            cls, csv_file: pathlib.Path,
            transformer: Optional[DataFrameTransformer] = None,
            validator: Optional[DataValidator] = None,
            strip_strings: bool = True,
            clean_fields: bool = True) -> TabularData:
        """Load inputs from csv file containing tabular data."""
        try:
            data = pd.read_csv(csv_file)
        except FileNotFoundError as err:
            err_msg = "Could not locate the input file."
            raise FileNotFoundError(err_msg) from err
        except (
                UnicodeDecodeError,
                pd.errors.ParserError,
                pd.errors.EmptyDataError) as err:
            err_msg = "Encountered a parsing error or data is empty."
            raise FileParsingError(message=err_msg) from err
        if strip_strings:
            data = data.applymap(
                lambda x: x.strip() if isinstance(x, str) else x)
        if clean_fields:
            data = cls.clean_field_names(data)
        return cls(
            data=data, transformer=transformer, validator=validator)

    @classmethod
    def from_excel(
            cls, excel_file: pathlib.Path,
            transformer: Optional[DataFrameTransformer] = None,
            validator: Optional[DataValidator] = None,
            strip_strings: bool = True,
            clean_fields: bool = True) -> TabularData:
        """Load inputs from excel file containing tabular data."""
        try:
            data = pd.read_excel(excel_file)
        except FileNotFoundError as err:
            err_msg = "Could not locate the input file."
            raise FileNotFoundError(err_msg) from err
        except (
                UnicodeDecodeError,
                pd.errors.ParserError,
                pd.errors.EmptyDataError) as err:
            err_msg = "Encountered a parsing error or data is empty."
            raise FileParsingError(message=err_msg) from err
        if strip_strings:
            data = data.applymap(
                lambda x: x.strip() if isinstance(x, str) else x)
        if clean_fields:
            data = cls.clean_field_names(data)
        return cls(
            data=data, transformer=transformer, validator=validator)

    def transform(self) -> None:
        """Transform tabular data using transformations defined in the
        trasformer attribute."""
        if self.transformer is not None:
            self._data = self.transformer.transform(data=self._data)

    @property
    def data(self) -> pd.DataFrame:
        """Return data."""
        return self._data

    def _check_missing_fields(
            self, required_fields: List[str],
            no_required: Union[str, int] = "all") -> FieldStatus:
        """Check tabular data for missing fields (columns).

        Args:
            required_fields: a list of fields that are required in the data.
            no_required: number of fields required.

        Return a named tuple with field values: True and empty string if
            no missing fields have been found.
        Otherwise, return named tuple with field values: False and a string
            with an error message listing the missing fields.
        """
        if isinstance(no_required, str) and no_required != "all":
            raise KeyError("Argument no_required is invalid.")
        emsg: str = ""
        fields_valid: bool = True
        fields_detected: list = self._data.columns.to_list()
        # Check for missing columns (required fields)
        missing_fields = list(set(required_fields) - set(fields_detected))
        # if missing fields have been found
        if len(missing_fields) > 0:
            missing_fields_str: str = ",".join(str(x) for x in missing_fields)
            if no_required == "all" or no_required >= len(required_fields):
                fields_valid = False
                emsg = \
                    f'Required column(s) are missing: {missing_fields_str}\n'
            elif no_required < len(required_fields):
                alt_fields_detected = len(list(set(required_fields) &
                                          set(fields_detected))) > 0
                if alt_fields_detected < no_required:
                    fields_valid = False
                    emsg = \
                        f'  - At least {str(no_required)} of the following ' + \
                        f'columns must be provided: {missing_fields_str}.'
                else:
                    pass
        return self.FieldStatus(valid=fields_valid, issues=emsg)

    def _check_duplicate_fields(self) -> FieldStatus:
        """Check dataframe for duplicate fields (columns).

        Return a named tuple with field values: True and empty string if
            no duplicate fields have been found.
        Otherwise, return named tuple with field values: False and a string
            with a message listing duplicate fields.
        """
        emsg: str = ""
        fields_valid: bool = True
        seen = set()
        duplicates_with_repeats = [
            field for field in self._data.columns.to_list() if field in seen or
            seen.add(field)]
        if len(duplicates_with_repeats) > 0:
            duplicate_fields_str: str = ",".join(duplicates_with_repeats)
            emsg = \
                f'Following columns are duplicated: {duplicate_fields_str}\n.'
            fields_valid = False
        return self.FieldStatus(valid=fields_valid, issues=emsg)

    def check_fields(
            self,
            required_fields: List[str],
            alt_fields: List[str],
            no_alt_required: int) -> FieldStatus:
        """Check dataframe for duplicate colums and missing fields.

        Args:
            required_fields: a list of fields that are required in the data.
            alt_fields: a list of fields out of which only a subset of is
                required.
            no_alt_required: number of alt_fields required.

        Return a named tuple with field values: True and empty string if
            no invalid fields have been found.
        Otherwise, return named tuple with field values: False and a string
            with an error message.
        """
        duplicate_fields_report = self._check_duplicate_fields()
        required_missing_fields_report = self._check_missing_fields(
            required_fields=required_fields)
        alt_missing_fields_report = self._check_missing_fields(
            required_fields=alt_fields, no_required=no_alt_required)
        # Collect the reports and return a single output dict
        reports = [duplicate_fields_report,  required_missing_fields_report,
                   alt_missing_fields_report]
        # Fields are valid if all reports say that the fields are valid
        fields_valid = all(report.valid for report in reports)
        # Append issues messages from all reports
        emsg = ', '.join([report.issues for report in reports if report.issues
                          not in ["", " "]])
        return self.FieldStatus(valid=fields_valid, issues=emsg)

    def validate(
            self,
            csv_report_path: pathlib.Path,
            adapt_schema_to_data: bool = True) -> None:
        """ """
        if self.validator is not None:
            validation_report = self.validator.validate(
                data=self.data,
                csv_report_path=csv_report_path,
                adapt_schema_to_data=adapt_schema_to_data)
            self.validation_report = validation_report

    def is_valid(self) -> str:
        """ """
        if self.validation_report is None:
            return "undefined"
        if self.validation_report.valid:
            return "yes"
        return "no"


class TabularInput(TabularData):
    """ """


class TabularOutput(TabularData):
    """ """
