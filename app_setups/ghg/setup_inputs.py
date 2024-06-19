""" """
import pathlib
from typing import List
from heet.tab_data.tabular_data import TabularInput
from heet.tab_data.schemas import Schema
from heet.tab_data.transformers import (
    DataFrameTransformation, DataFrameTransformer)
from heet.tab_data.validate import (
    ValueValidation, DataValidator, HPDataValidation)
from heet.utils import get_package_file


def prepare_input_data_transformations() -> List[DataFrameTransformation]:
    """ Create a list of transformations to be perormed on the input data."""
    turbine_eff_tr_1 = DataFrameTransformation(
        column='turbine_efficiency',
        new_column='turbine_efficiency_prov',
        functions=[('isna', None), ('astype', int)],
        comment='get provisional turbine efficiency')
    turbine_eff_tr_2 = DataFrameTransformation(
        column='turbine_efficiency',
        new_column='t_turbine_efficiency',
        functions=[('fillna', 85)],
        comment='get turbine efficiency with filled in blanks')
    plant_depth_tr_1 = DataFrameTransformation(
        column='plant_depth',
        new_column='plant_depth_prov',
        functions=[('isna', None), ('astype', int)],
        comment='get provisional plant depth')
    plant_depth_tr_2 = DataFrameTransformation(
        column='plant_depth',
        new_column='t_plant_depth',
        functions=[('fillna', 0)],
        comment='get plant depth with filled in blanks')
    water_level_tr = DataFrameTransformation(
        column='water_level',
        new_column='t_water_level',
        functions=[('fillna', -999)],
        comment='get water level with filled in blanks')
    dam_height_tr = DataFrameTransformation(
        column='dam_height',
        new_column='t_dam_height',
        functions=[('fillna', -999)],
        comment='get dam height with filled in blanks')
    dam_lon_tr = DataFrameTransformation(
        column='dam_lon',
        new_column='x',
        functions=[],
        comment='add x column with dam location longitude')
    dam_lat_tr = DataFrameTransformation(
        column='dam_lat',
        new_column='y',
        functions=[],
        comment='add y column with dam location latitude')
    # Put transformation in the list
    input_transformations = [
        turbine_eff_tr_1, turbine_eff_tr_2, plant_depth_tr_1,
        plant_depth_tr_2, water_level_tr, dam_height_tr, dam_lon_tr,
        dam_lat_tr]
    return input_transformations


def prepare_input_data_validations() -> List[ValueValidation]:
    valid_water_level_proxy = HPDataValidation(
        name='sufficient data for the description of HP')
    return [valid_water_level_proxy]


def main():
    # Prepare the necessary input dataframe transformations
    input_transformations = prepare_input_data_transformations()
    # Initialize the tabular input data object
    input_data = TabularInput.from_csv(
        csv_file=pathlib.Path(__file__).parent.joinpath('data/dams.csv'),
        transformer=DataFrameTransformer(
            transformations=input_transformations)
    )
    # Check the inputs for presence of mandatory fields (columns)
    required_fields = ['id', 'country', 'name', 'dam_lat', 'dam_lon']
    alt_fields = ['dam_height', 'water_level', 'power_capacity']
    # Inputs checked for the presence of all required_fields plus additionally
    # one out of three alt_fields
    fields_output = input_data.check_fields(
        required_fields=required_fields,
        alt_fields=alt_fields,
        no_alt_required=1)
    print("Are all the fields valid?: ", fields_output.valid)
    # Transform the input data
    if fields_output.valid:
        input_data.transform()
    # Validate the input data
    input_validator = DataValidator(
        schema=Schema.from_file(file_name=get_package_file(
            'schemas/emissions/inputs.resource.yaml')))
    for validation in prepare_input_data_validations():
        input_validator.add_validation(validation)

    validation_report = input_validator.validate(
        data=input_data,
        csv_report_path=pathlib.Path(__file__).parent.joinpath(
            'outputs/heet_input_report.csv'),
        adapt_schema_to_data=True)
    print(validation_report.message)


if __name__ == '__main__':
    main()
