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


if 'CI_ROBOT_USER' in os.environ:
    print("Running service account authentication")
    gc_service_account = os.environ['GCLOUD_ACCOUNT_EMAIL']
    credentials = ee.ServiceAccountCredentials(gc_service_account, 'service_account_creds.json')
    ee.Initialize(credentials)

else:
    print("Running individual account authentication")
    ee.Initialize()

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


def test_impute_dam_height():
    """Test that imputed dam height works for a set of test values."""
    from heet_reservoir import impute_dam_height
    
    test_input = {
        'power_capacity': ee.Number(10),
        'turbine_efficiency': ee.Number(85),
        'plant_depth': ee.Number(0),
        'mad_m3_pers': ee.Number(24),
    }
     
    test_result =  49.969
    calc_result = impute_dam_height(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_impute_dam_height] Dam Height - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    assert calc_result  == test_result

