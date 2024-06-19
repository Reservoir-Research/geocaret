"""
Tools for converting data between EarthEngine's and other popular data formats.
"""
from typing import Optional
import pandas as pd
import ee
import heet.log_setup
from heet.assets import EmissionAssets
from heet.application import Application

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)


#  TODO: Experiment with wrapping the converter methods with error handling
#  wrapper functions in internet.py

class Converter:
    """ """
    #TODO: Check if EE is initialized before instantiating the class
    @staticmethod
    def ftc_to_df(
            feat_collection: ee.FeatureCollection) -> Optional[pd.DataFrame]:
        """
        Convert a FeatureCollection into a pandas DataFrame.

        Args:
            feat_collection: EarthEngine's feature collection object
        Returns:
            Pandas DataFrame representation of the feature collection if
            collection found or None
        Raises:
            ee.ee_exception.EEException: An error occurred while accessing
                the collection.
        """
        try:
            features = feat_collection.getInfo()['features']
            rows_dict_list = [feature['properties'] for feature in features]
            return pd.DataFrame(rows_dict_list)
        except ee.ee_exception.EEException as exc:
            logger.error(
                "An Error occurred while accessing the collection. %s",
                repr(exc))
            return None

    @staticmethod
    def df_to_ftc(data: pd.DataFrame) -> Optional[ee.FeatureCollection]:
        """
        Convert a pandas DataFrame to Google's Earth Engine FeatureCollection.

        Args:
            Pandas DataFrame with features and geometry (coordinates) in 'x'
                and 'y' columns.
        Returns:
            Google Earth Engine's FeatureCollection
        Raises:
            AttributeError: if the data argument does not contain 'x' or 'y'
                columns.
            ee.ee_exception.EEException: if geometry information is not valid,
                e.g. values are strings not floats, etc.
        """
        features = []
        # Get the list of properties.
        # Properties are assumed to be defined by column names, except for
        # 'x' and 'y' which hold coordinates
        properties = [col_name for col_name in data.columns if col_name
                      not in ['x', 'y']]
        # Convert data to dictionary to remove types such as int64 that are
        # not serializable. Other options exist.
        data_dict = data.to_dict()
        # Old piece of code replaced by data_dict
        #jdf_str = data_df.to_json()
        #jdf = json.loads(jdf_str)
        # TODO: Think of veorization or convertion to numpy to speed up the
        # iterations.
        for row_index in range(data.shape[0]):
            # Extract geometry
            try:
                geometry = ee.Geometry.Point(
                    [data.x[row_index], data.y[row_index]])
            except AttributeError as exc:
                logger.error(
                    "Data does not contain one or more coordinates. %s",
                    repr(exc))
                return None
            except ee.ee_exception.EEException as exc:
                logger.error("%s", repr(exc))
                return None
            # Build feature from geometry
            feature = ee.Feature(geometry)
            # Append properties
            for prop in properties:
                 # jdf[prop][str(row_index)])
                feature = feature.set(prop, data_dict[prop][row_index])
            features.append(feature)
        return ee.FeatureCollection(features)

    @staticmethod
    def csv_to_df(file_path: str) -> pd.DataFrame:
        """Convert a csv file to Pandas dataframe"""

        def _clean_field_names(data: pd.DataFrame) -> pd.DataFrame:
            """Strip spaces and ensure lower case in dataframe's column names"""
            field_names = data.head()
            updated_field_names = [f.strip().lower() for f in field_names]
            data.columns = updated_field_names
            return data

        try:
            data = pd.read_csv(file_path)
        except FileNotFoundError:
            logger.exception("Could not locate the input file")
            return False, ""
        except (UnicodeDecodeError, pd.errors.ParserError,
                pd.errors.EmptyDataError):
            logger.exception("Fatal error encountered while loading input file")
            return False, ""
        data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        data = _clean_field_names(data)
        return data


if __name__ == '__main__':
    _ = Application(name="GHG Emissions")
    assets = EmissionAssets()

    run_ftc_to_df = False
    run_df_to_ftc = True

    if run_ftc_to_df:
        asset_name = assets.asset_folder + "/" + "output_parameters"
        output_parameters_ftc = ee.FeatureCollection(asset_name)
        print(output_parameters_ftc)
        data_df = Converter.ftc_to_df(feat_collection=output_parameters_ftc)
        if data_df is not None:
            print(data_df)

    if run_df_to_ftc:
        data_dict = {
            'col_1': [3, 2, 1, 0],
            'col_2': ['a', 'b', 'c', 'd'],
            'x': [40.54, '70.43', 342.34, 90],
            'y': [20.3, 10.345, 0.34, 87.34],
            'col_3': ['a', 'b', 'c', 'd']
            }
        data_df = pd.DataFrame.from_dict(data_dict)
        fc = Converter.df_to_ftc(data=data_df)
        print(fc)
