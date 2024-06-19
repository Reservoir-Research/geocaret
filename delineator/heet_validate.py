""" Functions for veryfying data (inputs and outputs) and data
    structures """
import logging
import copy
from pathlib import Path
import yaml
import pandas as pd
from typing import Tuple, Iterator, Union
from frictionless import validate
from frictionless import errors


# =============================================================================
#  Set up logger
# =============================================================================
# Gets or creates a logger
logger = logging.getLogger(__name__)
# set log level
logger.setLevel(logging.DEBUG)
# define file handler and set formatter
file_handler = logging.FileHandler('heet.log')
formatter = logging.Formatter(
    '%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
# add file handler to logger
logger.addHandler(file_handler)

# =============================================================================
# Output validation checks for frictionless framework's validate method
# =============================================================================


def improbable_mean_slope(row) -> Iterator[errors.RowError]:
    """ Detect and flag improbable mean slopes """
    value_correct = True
    # Implausible, but possible value range
    value_min = 100
    value_max = 241.41
    if 'c_mean_slope_pc' in row:
        if row['c_mean_slope_pc'] is not None:
            if not isinstance(row['c_mean_slope_pc'], str):
                if value_min < row['c_mean_slope_pc'] <= value_max:
                    value_correct = False
    if not value_correct:
        note = "An improbable value of mean slope was detected"
        yield errors.RowError.from_row(row, note=note)


def improbable_mean_annual_runoff(row) -> Iterator[errors.RowError]:
    """ Detect and flag improbable mean annual runoff values """
    # 3500 - 6000
    # c_mar_mm
    # c_mar_mm_alt1
    # c_mar_mm_alt2
    # Implausible, but possible value range
    c_mar_mm_min = 3500
    c_mar_mm_max = 6000
    fields = []
    value_correct = True
    for var_name in ['c_mar_mm', 'c_mar_mm_alt1', 'c_mar_mm_alt2']:
        if var_name in row:
            if row[var_name] is not None:
                if not isinstance(row[var_name], str):
                    if c_mar_mm_min < row[var_name] <= c_mar_mm_max:
                        value_correct = False
                        fields.append(var_name)
    problem_fields = ",".join(fields)
    if not value_correct:
        note = f"An improbable value of mean annual runoff was detected in fields: {problem_fields}"
        yield errors.RowError.from_row(row, note=note)


def improbable_windspeed(row) -> Iterator[errors.RowError]:
    """ Detect and flag improbable wind speed values """
    # > 15
    # r_mean_annual_windpseed_mpers
    # Upper limit of plausible
    plausible_max = 15
    value_correct = True
    if 'r_mean_annual_windpseed' in row:
        if row['r_mean_annual_windpseed'] is not None:
            if not isinstance(row['r_mean_annual_windpseed'], str):
                if row['r_mean_annual_windpseed'] > plausible_max:
                    value_correct = False
    if not value_correct:
        note = "An improbable value of wind speed was detected"
        yield errors.RowError.from_row(row, note=note)


def improbable_precipitation(row) -> Iterator[errors.RowError]:
    """ Detect and flag improbable precipitation values """
    # 4000-6000
    # c_map_mm
    # Implausible, but possible value range    
    cmap_mm_min = 4000
    cmap_mm_max = 6000
    value_correct = True
    if 'c_map_mm' in row:
        if row['c_map_mm'] is not None:
            if not isinstance(row['c_map_mm'], str):
                if cmap_mm_min < row['c_map_mm'] <= cmap_mm_max:
                    value_correct = False
    if not value_correct:
        note = "An improbable value of mean precipitation was detected"
        yield errors.RowError.from_row(row, note=note)


def improbable_evapotranspiration(row) -> Iterator[errors.RowError]:
    """ Detect and flag improbable evapotranspiration values """
    # c_mpet_mm
    # Implausible, but possible value range        
    c_mpet_mm_min = 1500
    c_mpet_mm_max = 2500
    value_correct = True
    if 'c_mpet_mm' in row:
        if row['c_mpet_mm'] is not None:
            if not isinstance(row['c_mpet_mm'], str):
                if c_mpet_mm_min < row['c_mpet_mm'] <= c_mpet_mm_max:
                    value_correct = False
    if not value_correct:
        note = "An improbable value of mean evapotranspiration was detected"
        yield errors.RowError.from_row(row, note=note)


def improbable_soil_wetness(row) -> Iterator[errors.RowError]:
    """ Detect and flag improbable soil wetness (or mean slope?) """
    value_correct = True
    # > 800
    # Upper limit of plausible 
    plausible_max = 800
    if 'c_masm_mm' in row:
        if row['c_masm_mm'] is not None:
            if not isinstance(row['c_masm_mm'], str):
                if row['c_masm_mm'] > plausible_max:
                    value_correct = False
    if not value_correct:
        note = "An improbable value of mean soil wetness was detected"
        yield errors.RowError.from_row(row, note=note)


def improbable_soil_carbon(row) -> Iterator[errors.RowError]:
    """ Detect and flag improbable soil carbon """
    # 12.5-22
    # Implausible, but possible value range            
    c_msoc_min = 12.5
    c_msoc_max = 22
    value_correct = True
    if 'c_msoc_kgperm' in row:
        if row['c_msoc_kgperm'] is not None:
            if not isinstance(row['c_msoc_kgperm'], str):
                if c_msoc_min < row['c_msoc_kgperm'] <= c_msoc_max:
                    value_correct = False
    if not value_correct:
        note = "An improbable value of mean soil carbon was detected"
        yield errors.RowError.from_row(row, note=note)


def improbable_olsen(row) -> Iterator[errors.RowError]:
    """ Detect and flag improbable olsen values """
    # > 70
    # Upper limit of plausible       
    plausible_max = 70
    value_correct = True
    if 'c_mean_olsen' in row:
        if row['c_mean_olsen'] is not None:
            if not isinstance(row['c_mean_olsen'], str):
                if row['c_mean_olsen'] >  plausible_max:
                    value_correct = False
    if not value_correct:
        note = "An improbable value of mean Soil Olsen P was detected"
        yield errors.RowError.from_row(row, note=note)


def improbable_mghr(row) -> Iterator[errors.RowError]:
    """ Detect and flag improbable mean annual global horizontal irradiance
        (MGHR) values """
    #  > 10
    # Upper limit of plausible 
    plausible_max = 10
    mghr_fields = [
        'r_mghr_all_kwhperm2perday',
        'r_mghr_all_kwhperm2perday_alt1',
        'r_mghr_may_sept_kwhperm2perday',
        'r_mghr_may_sept_kwhperm2perday_alt1',
        'r_mghr_nov_mar_kwhperm2perday',
        'r_mghr_nov_mar_kwhperm2perday_alt1'
    ]
    fields = []
    value_correct = True
    for var_name in mghr_fields:
        if var_name in row:
            if row[var_name] is not None:
                if not isinstance(row[var_name], str):
                    if row[var_name] > plausible_max:
                        value_correct = False
                        fields.append(var_name)
    problem_fields = ",".join(fields)
    if not value_correct:
        note = f"An improbable value of mghr was detected in fields: {problem_fields}"
        yield errors.RowError.from_row(row, note=note)


def improbable_pop_dens(row) -> Iterator[errors.RowError]:
    """ Detect and flag improbable population density values """
    #  > 350
    # Upper limit of plausible     
    plausible_max = 350
    popdens_fields = [
        'r_population_density',
        'n_population_density',
        'c_population_density'
    ]
    fields = []
    value_correct = True
    for var_name in popdens_fields:
        if var_name in row:
            if row[var_name] is not None:
                if not isinstance(row[var_name], str):
                    if row[var_name] > plausible_max:
                        value_correct = False
                        fields.append(var_name)
    problem_fields = ",".join(fields)
    if not value_correct:
        note = f"An improbable value of population density was detected in fields: {problem_fields}"
        yield errors.RowError.from_row(row, note=note)


def valid_water_level_proxy(row) -> Iterator[errors.RowError]:
    """ Check if enough data has been provided to describe a hydroelectric
        reservoir """
    missing_values = 0
    if 'dam_height' not in row:
        missing_values += 1
    elif row['dam_height'] is None:
        missing_values += 1
    if 'water_level' not in row:
        missing_values += 1
    elif row['water_level'] is None:
        missing_values += 1
    if 'power_capacity' not in row:
        missing_values += 1
    elif row['power_capacity'] is None:
        missing_values += 1
    if missing_values == 3:
        note = "A non-missing value must be provided for at least one of: " + \
            "dam_height, water_level or power_capacity"
        yield errors.RowError.from_row(row, note=note)


def clean_field_names(df: pd.DataFrame) -> pd.DataFrame:
    """ Strip spaces and ensure lower case in dataframe's column names """
    field_names = df.head()
    updated_field_names = [f.strip().lower() for f in field_names]
    df.columns = updated_field_names
    return df


def csv_to_df(file_path: str) -> Tuple[bool, Union[pd.DataFrame, str]]:
    """ Convert a csv file to Pandas dataframe """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        logger.exception("HEET could not locate the input file")
        return False, ""
    except (UnicodeDecodeError, pd.errors.ParserError, pd.errors.EmptyDataError):
        logger.exception("HEET encountered a fatal error loading input file")
        return False, ""
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = clean_field_names(df)
    return df


def valid_fields(df: pd.DataFrame) -> Tuple[bool, str]:
    """ Check dataframe for duplicate colums and missing fields.
        Return True if no duplicates and no required fields are missing.
        Otherwise, return False and provide an error message """
    emsg = ""
    fields_valid = True
    fields_detected = df.columns.to_list()
    # Check for duplicate column names
    seen = set()
    duplicate_fields_list = [
        f for f in fields_detected if f in seen or seen.add(f)]
    if len(duplicate_fields_list) > 0:
        duplicate_fields = ",".join(duplicate_fields_list)
        emsg = f'{emsg} - Column names are duplicated: {duplicate_fields}\n'
        fields_valid = False
    # Check for missing columns (required fields)
    required_fields = ['id', 'country', 'name', 'dam_lat', 'dam_lon']
    missing_fields = list(set(required_fields) - set(fields_detected))
    if len(missing_fields) > 0:
        missing_fields_str = ",".join(str(x) for x in missing_fields)
        emsg = f'{emsg}  - Required column(s) are missing: {missing_fields_str}\n'
        fields_valid = False        
    # Check for missing columns (optional fields)
    alt_fields = ['dam_height', 'water_level', 'power_capacity']
    alt_fields_detected = len(list(set(alt_fields) & set(fields_detected))) > 0
    if alt_fields_detected == 0:
        emsg = f'{emsg}  - At least one of the following columns must be ' + \
            'provided: dam_height, water_level, power_capacity.'
        fields_valid = False            
    return {'valid': fields_valid, 'issues': emsg}


def adapt_validation_schema(df: pd.DataFrame, profile: dict) -> dict:
    """ Adapt validation schema to comform with frictionless framework
        requirements - see below """
    # Built in validation capability of frictionless data is very strict
    # - column order is enforced.
    # - optional columns are not supported
    # To address this, we tailor a base validation schema to the input dataset.
    # - We add any extra columns to the schena (no validation)
    # - We reorder columns in the schema to reflect the input data
    updated_profile = copy.deepcopy(profile)
    template = {
        'name': 'Added Variable 1',
        'description': 'Custom variable',
        'type': 'any'
    }
    data_fields = df.columns.to_list()
    schema_fields = copy.deepcopy(profile['schema']['fields'])
    update_data_fields = []
    for field in data_fields:
        #print(field)
        matched_fields = [e for e in schema_fields if e['name'] == field]
        if len(matched_fields) == 0:
            entry = template.copy()
            entry['name'] = field
        else:
            entry = matched_fields[0]
        update_data_fields.append(entry)
    updated_profile['schema']['fields'] = update_data_fields
    return updated_profile


def valid_input(df: pd.DataFrame, input_file_path: str,
                output_folder_path: str) -> Tuple[bool, str]:
    """ Validate the input dataframe using custom schema (profile)
        deined in utils/input.resource.yaml and adapted with
        adapt_validation_schema function
        Write input validation report in csv """
    yaml_file_path = Path("utils", "inputs.resource.yaml")
    with yaml_file_path.open("r", encoding="utf-8") as ymlfile:
        profile = yaml.safe_load(ymlfile)
    custom_profile = adapt_validation_schema(df, profile)
    target_schema = custom_profile['schema']
    check_list = [valid_water_level_proxy]
    report = validate(input_file_path, schema=target_schema, checks=check_list)

    if report['stats']['errors'] > 0:
        report_content = report.flatten(
            ["fieldPosition", "rowPosition", "fieldName", "code", "message",
             "note"])
        df_validation = pd.DataFrame(
            report_content, columns=[
                "column", "row", "field_name", "error_code", "error_message",
                "note"])
        df_validation.to_csv(
            Path(output_folder_path, 'heet_input_report.csv'), index=False)
        error_messages = [
            "  - " + e for e in df_validation['error_message'].to_list()]
        emsg = "\n".join(error_messages)
        return {'valid': False, 'issues': emsg}
    return {'valid': True, 'issues': ""}


def valid_output(df: pd.DataFrame, output_file_path: str,
                 output_folder_path: str) -> Tuple[bool, str]:
    """ Validate the output dataframe using custom schema (profile)
        deined in utils/output.resource.yaml and adapted with
        adapt_validation_schema function
        Write output validation report in csv """
    yaml_file_path = Path("utils", "outputs.resource.yaml")
    with yaml_file_path.open("r", encoding="utf-8") as ymlfile:
        profile = yaml.safe_load(ymlfile)
    custom_profile = adapt_validation_schema(df, profile)
    target_schema = custom_profile['schema']
    check_list = [
        improbable_mean_slope,
        improbable_mean_annual_runoff,
        improbable_windspeed,
        improbable_precipitation,
        improbable_evapotranspiration,
        improbable_soil_wetness,
        improbable_soil_carbon,
        improbable_olsen,
        improbable_mghr,
        improbable_pop_dens
    ]
    report = validate(
        output_file_path, schema=target_schema, checks=check_list)
    if report['stats']['errors'] > 0:
        report_content = report.flatten(
            ["fieldPosition", "rowPosition", "fieldName", "code", "message",
             "note"])
        df_validation = pd.DataFrame(
            report_content, columns=[
                "column", "row", "field_name", "error_code", "error_message",
                "note"])
        df_validation.to_csv(
            Path(output_folder_path, 'heet_output_report.csv'), index=False)
        error_messages = [
            "  - " + e for e in df_validation['error_message'].to_list()]
        emsg = "\n".join(error_messages)
        return {'valid': False, 'issues': emsg}
    return {'valid': True, 'issues': ""}

# =============================================================================
# Input preparation
# =============================================================================


def prepare_input_table(df: pd.DataFrame) -> pd.DataFrame:
    """ Prepare a valid input dataframe """
    d_lookup = {
        'any': 'str',
        'string': 'str',
        'number': 'float',
        'integer': 'int'
    }
    yaml_file_path = Path("utils", "inputs.resource.yaml")
    with yaml_file_path.open("r", encoding="utf-8") as ymlfile:
        profile = yaml.safe_load(ymlfile)
    # Add missing fields
    schema_fields = profile['schema']['fields']
    schema_field_names = [e['name'] for e in schema_fields]
    fields_detected = df.columns.to_list()
    # Filter out extra columns
    missing_fields = list(set(schema_field_names) - set(fields_detected))
    for fname in missing_fields:
        field_type = [e['type'] for e in schema_fields if e['name'] == fname]
        new_type = d_lookup[field_type[0]]
        df[fname] = pd.Series(dtype=new_type)
    # Order fields correctly
    df = df[schema_field_names].copy()
    # Set missing turbine efficiency to 85%
    df['turbine_efficiency_prov'] = df['turbine_efficiency'].isna().astype(int)
    df['t_turbine_efficiency'] = df['turbine_efficiency'].fillna(85)
    # Set missing plant depth to 0
    df['plant_depth_prov'] = df['plant_depth'].isna().astype(int)
    df['t_plant_depth'] = df['plant_depth'].fillna(0)
    # Set missing water level to -999
    df['t_water_level'] = df['water_level'].fillna(-999)
    # Set missing dam height to -999
    df['t_dam_height'] = df['dam_height'].fillna(-999)
    df['x'] = df['dam_lon']
    df['y'] = df['dam_lat']
    return df
