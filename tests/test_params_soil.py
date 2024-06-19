
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
import  numpy as np

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
#  Soil Characteristics
#==============================================================================

# Carbon Stocks
def test_mean_soil_oc_stocks():
    """Test that mean soil organic carbon stocks works for a ground truth value (px4)."""
    from heet_params import mean_soil_oc_stocks
    
    carbon_poly_px4 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/carbon_poly_px4")
    
    test_input = {
        'land_ftc': carbon_poly_px4,
    }
     
    test_result = 8.25
    calc_result = mean_soil_oc_stocks(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_mean_soil_oc_stocks] Mean Soil Organic Carbon Stocks - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)

# Carbon content
def test_mean_soil_oc_content(target_ftc = None):
    """Test that soil organic carbon content (g/kg) is calculated correctly for a single ground truth example"""
    from heet_params import mean_soil_oc_content
    
    psoc_poly_org_px1 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/psoc_poly_org_px1")
    
    test_input = {
        'target_ftc': psoc_poly_org_px1,
    }
     
    # Total C g/kg
    test_result = 208.067
    calc_result = mean_soil_oc_content(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_mean_soil_oc_content] Mean Soil Organic Carbon Content- HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)

# Nitrogen content
def test_mean_soil_nitrogen_content(target_ftc = None):
    """Test that soil nitrogen content is (g/kg) is calculated correctly for a single ground truth example"""
    from heet_params import mean_soil_nitrogen_content
    
    soiln_poly_px1 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/soiln_poly_px1")
    
    test_input = {
        'target_ftc': soiln_poly_px1,
    }
     
    # Total N g/kg
    test_result = 66.368
    calc_result = mean_soil_nitrogen_content(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_mean_soil_nitrogen_content] Mean Soil Nitrogen Content - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)
    

# Soil Bulk Density
def test_mean_soil_bdod(target_ftc = None):
    """Test that bulk soil density (kg/dm3) is calculated correctly for a single ground truth example"""
    from heet_params import mean_soil_bdod
    
    soilbdod_poly_px1 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/soilbdod_poly_px1")
    
    test_input = {
        'target_ftc': soilbdod_poly_px1,
    }
     
    # Soil Density (kg/dm3)
    test_result = 1.077
    calc_result = mean_soil_bdod(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_mean_soil_bdod] Bulk Soil Density - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)