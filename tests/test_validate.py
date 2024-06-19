
import ee
import os

if 'CI_ROBOT_USER' in os.environ:
    print("Running service account authentication")
    gc_service_account = os.environ['GCLOUD_ACCOUNT_EMAIL']
    credentials = ee.ServiceAccountCredentials(gc_service_account, 'service_account_creds.json')
    ee.Initialize(credentials)

else:
    print("Running individual account authentication")
    ee.Initialize()

import pytest
import heet_data as dta
import logging
import numpy as np
import json

#==============================================================================
#  Set up logger
#==============================================================================


# Create new log each run (TODO; better implementation)
with open("tests.log", 'w') as file:
    pass


# Gets or creates a logger
logger = logging.getLogger(__name__)  

# set log level
logger.setLevel(logging.DEBUG)

# define file handler and set formatter
file_handler = logging.FileHandler('tests.log')
formatter    = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)


#==============================================================================
# Utils
#==============================================================================

def is_valid_json(json_dict):
  json_object = json.dumps(json_dict, indent = 4) 
  try:
    json.loads(json_object)
  except ValueError as e:
    return False
  return True

#==============================================================================
# Output Validation
#==============================================================================

# Output Validation
def test_valid_output():
    """Test that output validation runs successfully on a valid example output file."""
    from heet_validate import valid_output
    from heet_validate import csv_to_df

    output_file_path = "tests/data/output_parameters.csv"
    df_output = csv_to_df(output_file_path)
    
    test_input = {
        'df': df_output,
        'output_file_path': output_file_path,
        'output_folder_path': "tests/tmp"
    }
     
    test_result = True
    calc_result = valid_output(**test_input)['valid'] 
    
    logger.info(f'[test_valid_output] Output Vailidation - HEET {calc_result} '  + 
                f'Manual {test_result} ')     
        
    
    # Within 0.05%
    assert calc_result  == test_result

#==============================================================================
# JSON Export
#==============================================================================

# Output Validation
def test_generate_json_output():
    """Test that json output generate produces valid json (single dam)"""
    from heet_export import generate_json_output

    out_ft =  ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/output_parameters").first()
    
    test_input = {
        'out_ft': out_ft
    }
     

    test_result = True
    calc_result = is_valid_json(generate_json_output(**test_input))
    
    logger.info(f'[test_generate_json_output] JSON Output Validation - HEET {calc_result} '  + 
                f'Manual {test_result} ')     
        
    assert calc_result  == test_result

#==============================================================================
# Input validation
#==============================================================================
# Input Validation
def test_valid_fields_true():
    """Test that field validation works on a correct input file"""
    from heet_validate import valid_fields
    from heet_validate import csv_to_df
    
    input_file_path = "tests/data/dams_valid.csv"
    df_input = csv_to_df(input_file_path)
    
    test_input = {
        'df' : df_input
    }
     

    test_result = True
    calc_result = valid_fields(**test_input)['valid']
    
    logger.info(f'[test_valid_fields_true]  Vaidate input fields - HEET {calc_result} '  + 
                f'Manual {test_result} ')     
        
    assert calc_result  == test_result


def test_valid_fields_false():
    """Test that field validation works on a correct input file"""
    from heet_validate import valid_fields
    from heet_validate import csv_to_df
    
    input_file_path = "tests/data/dams_invalid_fields.csv"
    df_input = csv_to_df(input_file_path)
    
    test_input = {
        'df' : df_input
    }
     

    test_result = False
    calc_result = valid_fields(**test_input)['valid']
    
    logger.info(f'[test_valid_fields_true]  Vaidate input fields - HEET {calc_result} '  + 
                f'Manual {test_result} ')     
        
    assert calc_result  == test_result
    

def test_valid_input_true():
    """Test that field validation works on a correct input file"""
    from heet_validate import valid_input
    from heet_validate import csv_to_df
    
    input_file_path = "tests/data/dams_valid.csv"
    df_input = csv_to_df(input_file_path)
    
    test_input = {
        'df' : df_input,
        'input_file_path': input_file_path,
        'output_folder_path': 'tests/tmp'
    }
     

    test_result = True
    calc_result = valid_input(**test_input)['valid']
    
    logger.info(f'[test_valid_input_true]  Vaidate input  - HEET {calc_result} '  + 
                f'Manual {test_result} ')     
        
    assert calc_result  == test_result


def test_valid_input_false():
    """Test that field validation works on a correct input file"""
    from heet_validate import valid_input
    from heet_validate import csv_to_df
    
    input_file_path = "tests/data/dams_invalid_input.csv"
    df_input = csv_to_df(input_file_path)
    
    test_input = {
        'df' : df_input,
        'input_file_path': input_file_path,
        'output_folder_path': 'tests/tmp'
    }
     

    test_result = False
    calc_result = valid_input(**test_input)['valid']
    
    logger.info(f'[test_valid_input_false]  Vaidate input  - HEET {calc_result} '  + 
                f'Manual {test_result} ')     
        
    assert calc_result  == test_result