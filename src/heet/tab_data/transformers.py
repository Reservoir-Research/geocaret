"""Wrappers facilitating configurable transformations of tabular data using
pandas. The transormations are required in order to make sure the data is
compatible with data post-processing and analysis tools, such as e.g. the
Frictionless Framework used fo data validation."""
from typing import Optional, List, Tuple, Any
from dataclasses import dataclass
import pandas as pd
import heet.log_setup

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)


@dataclass
class DataFrameTransformation:
    """Container for data transformation parameters to be performed on a
    Pandas dataframe.

    Attributes:
        column: valid column name, e.g. 'plant_depth',
        new_column: column for storing transformed data, e.g. 't_plant_depth',
        functions: list of tuples with pandas function plus its argument, e.g.
            [('isna', None), ('astype', int)],
        comment: string describing what the transformation does and what it
            is for, e.g. 'plant depth with Nans converted to None'
    """
    column: str
    new_column: Optional[str]
    functions: List[Tuple[str, Any]]
    comment: str


class DataFrameTransformer:
    """Class for performing pandas dataframe transformations using pandas
       built-in methods specified in the DataFrameTransformation object.
    """
    def __init__(self,
                 transformations: Optional[List[DataFrameTransformation]]):
        self.transformations = []
        if transformations:
            self.transformations.extend(transformations)

    def add_transformation(self, transformation: DataFrameTransformation):
        """Add transformation to the list of transformations."""
        self.transformations.append(transformation)

    def remove_transformation(self, transformation: DataFrameTransformation):
        """Remove transformation from the list of transformations."""
        try:
            self.transformations.remove(transformation)
            logger.debug(f'removed transformation {transformation}')
        except ValueError:
            logger.debug('Transformation not present. Nothing removed.')

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Perform a list of transformation defined in the list of
        transformation objects."""
        data_copy = data.copy()
        for transformation in self.transformations:
            column_name = transformation.column
            if transformation.new_column not in (None, ''):
                new_column_name = transformation.new_column
            else:
                new_column_name = transformation.column
            tmp_data = data_copy[column_name].copy()
            for fn_name, arg in transformation.functions:
                if arg not in (None, ''):
                    tmp_data = getattr(tmp_data, fn_name)(arg)
                else:
                    tmp_data = getattr(tmp_data, fn_name)()
            data_copy[new_column_name] = tmp_data
        return data_copy


if __name__ == '__main__':
    """ """
