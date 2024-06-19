""" """
from typing import List
import pathlib
from heet.tab_data.validate import ValueValidation, DataValidator
from heet.tab_data.tabular_data import TabularOutput
from heet.tab_data.schemas import Schema
from heet.utils import get_package_file


def prepare_output_data_validations() -> List[ValueValidation]:
    """ """
    print("Preparing output data validations...")
    # Create value validators for GHG emissions application
    improbable_mean_slope = ValueValidation(
        name="mean catchment slope", variables=['c_mean_slope_pc'],
        min_value=100, max_value=241.41, condition="min-max")
    improbable_mean_annual_runoff = ValueValidation(
        name="mean annual runoff",
        variables=['c_mar_mm', 'c_mar_mm_alt1', 'c_mar_mm_alt2'],
        min_value=3500, max_value=6000, condition="min-max")
    improbable_windspeed = ValueValidation(
        name="mean annual wind speed", variables=['r_mean_annual_windpseed'],
        min_value=0, max_value=15, condition="above-max")
    improbable_precipitation = ValueValidation(
        name="mean annual precipitation", variables=['c_map_mm'],
        min_value=4000, max_value=6000, condition="min-max")
    improbable_evapotranspiration = ValueValidation(
        name="mean evapotranspiration", variables=['c_mpet_mm'],
        min_value=1500, max_value=2500, condition="min-max")
    improbable_soil_wetness = ValueValidation(
        name="mean soil wetness", variables=['c_masm_mm'],
        min_value=0, max_value=800, condition="above-max")
    improbable_soil_carbon = ValueValidation(
        name="mean soil carbon", variables=['c_msoc_kgperm'],
        min_value=12.5, max_value=22, condition="min-max")
    improbable_olsen = ValueValidation(
        name="mean soil Olsen P", variables=['c_mean_olsen'],
        min_value=0, max_value=70, condition="above-max")
    improbable_mghr = ValueValidation(
        name="mean annual global horizontal irradiance",
        variables=[
            'r_mghr_all_kwhperm2perday',
            'r_mghr_all_kwhperm2perday_alt1',
            'r_mghr_may_sept_kwhperm2perday',
            'r_mghr_may_sept_kwhperm2perday_alt1',
            'r_mghr_nov_mar_kwhperm2perday',
            'r_mghr_nov_mar_kwhperm2perday_alt1'
        ], min_value=0, max_value=10, condition="above-max")
    improbable_pop_dens = ValueValidation(
        name="population density",
        variables=[
            'r_population_density',
            'n_population_density',
            'c_population_density'
        ], min_value=0, max_value=350, condition="above-max")

    return [
        improbable_mean_slope,
        improbable_mean_annual_runoff,
        improbable_windspeed,
        improbable_precipitation,
        improbable_evapotranspiration,
        improbable_soil_wetness,
        improbable_soil_carbon,
        improbable_olsen,
        improbable_mghr,
        improbable_pop_dens]


if __name__ == '__main__':
    """ """
    # Load outputs
    output_data = get_package_file('data/outputs_chris_31_05.xlsx')
    output_data = TabularOutput.from_excel(
        excel_file=pathlib.Path(__file__).parent.joinpath(
            'data/outputs_chris_31_05.xlsx'))
    # Prepare the list of output validation steps
    output_validation_list = prepare_output_data_validations()
    # Create the validator object
    output_validator = DataValidator(
        schema=Schema.from_file(file_name=get_package_file(
            'schemas/emissions/outputs.resource.yaml')))
    for validation in output_validation_list:
        output_validator.add_validation(validation)
    # Validate the output data
    validation_report = output_validator.validate(
        data=output_data,
        csv_report_path=pathlib.Path(__file__).parent.joinpath(
            'outputs/heet_output_report.csv'),
        adapt_schema_to_data=True)
    print(validation_report.message)
