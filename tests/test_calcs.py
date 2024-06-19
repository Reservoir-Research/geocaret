
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


def test_area():
    """Test that area calculation matches a ground truth value for Derbyshire"""
    from heet_params import area
    
    target_roi = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_ASSETS/CTY_DEC_2021_EN_BUC").first() 
    
    test_input = {
        'land_ftc': target_roi,
    }
     
    test_result =  3056053132.916/(1000*1000)
    calc_result = area(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_area] Derbyshire area - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Check calculated area in km2 is equal within 0.005%
    assert calc_result  == pytest.approx(test_result, rel=5e-3)
    
def test_degrees_to_perc_slope1():
    """Test that degrees to slope calculation matches ground truth value
       https://www.calcunation.com/calculator/degrees-to-percent.php
    """
    from heet_params import degrees_to_perc_slope
    
    test_input = {
        'mean_slope_degrees_value': ee.Number(45),
    }
     
    test_result =  100
    calc_result = degrees_to_perc_slope(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_degrees_to_perc_slope] 45 degrees to percentage slope - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.005
    assert calc_result  ==  pytest.approx(test_result, abs=5e-3)
    
def test_degrees_to_perc_slope2():
    """Test that degrees to slope calculation matches ground truth value
       https://www.calcunation.com/calculator/degrees-to-percent.php
    """
    from heet_params import degrees_to_perc_slope
    
    test_input = {
        'mean_slope_degrees_value': ee.Number(48),
    }
     
    test_result =  111.06 
    calc_result = degrees_to_perc_slope(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_degrees_to_perc_slope] 48 degrees to percentage slope - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.005
    assert calc_result  ==  pytest.approx(test_result, abs=5e-3)
    


def test_reservoir_volume():
    """Test"""
    from heet_params import reservoir_volume
    
    test_input = {
        'surface_area': ee.Number(1),
        'mean_depth': ee.Number(0.75),
    }
     
    test_result =  0.75
    calc_result = reservoir_volume(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_reservoir_volume] Reservoir Volume - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    assert calc_result  ==  pytest.approx(test_result)    


def test_km2_to_m2():
    """Test"""
    from heet_params import km2_to_m2
    
    test_input = {
        'surface_area': ee.Number(1)
    }
     
    test_result =  1000000
    calc_result = km2_to_m2(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_km2_to_m2] km2 to m2  - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    assert calc_result  ==  pytest.approx(test_result)    