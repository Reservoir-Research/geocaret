
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
#  Slope
#==============================================================================

def test_mean_slope_degrees1():
    """Test that mean slope works for a ground truth value (px4)."""
    from heet_params import mean_slope_degrees
    
    slope_poly_px4 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/slope_poly_px4")
    
    test_input = {
        'catchment_ftc': slope_poly_px4,
    }
     
    # Degrees  2.100007
    # % 3.67 P
    test_result = 2.100007
    calc_result = mean_slope_degrees(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[mean_slope_perc] Mean Slope Deg - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)
    
def test_mean_slope_degrees2():
    """Test that mean slope works for a ground truth value (px1)."""
    from heet_params import mean_slope_degrees
    
    slope_poly_px1 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/slope_poly_px1")
    
    test_input = {
        'catchment_ftc': slope_poly_px1,
    }
     
    # Degrees  4.140905380249023
    # % 7.24 
    test_result = 4.140905380249023
    calc_result = mean_slope_degrees(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[mean_slope_perc] Mean Slope Deg - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)    
    
    
def test_mean_slope_degrees3():
    """Test that mean slope works for a ground truth value (px0)."""
    from heet_params import mean_slope_degrees
    
    slope_poly_px0 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/slope_poly_px0")
    
    test_input = {
        'catchment_ftc': slope_poly_px0,
    }
     
    # Degrees  1.7956430912017822
    # % 3.13  
    test_result = 1.7956430912017822
    calc_result = mean_slope_degrees(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[mean_slope_perc] Mean Slope Deg - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)        
    
def test_mean_slope():
    """Test that mean slope works for a ground truth value (px4)."""
    from heet_params import mean_slope
    
    slope_poly_px4 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/slope_poly_px4")
    
    test_input = {
        'catchment_ftc': slope_poly_px4,
    }
     
    # Degrees  2.100007
    # % 3.67 P
    test_result = 3.67 
    calc_result = mean_slope(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[mean_slope_perc] Mean Slope % - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)

#==============================================================================
#  Elevation
#==============================================================================

def test_minimum_elevation():
    """Test that minimum elevation works for a ground truth value (px4)."""
    from heet_params import minimum_elevation
    
    elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/elev_poly_px4").first()
    ).set('r_imputed_water_elevation', "98")
    elev_poly_px4_ftc = ee.FeatureCollection(elev_poly_px4_ft)
    
    test_input = {
        'reservoir_ftc': elev_poly_px4_ftc,
    }
     
    test_result = 96
    calc_result = minimum_elevation(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[minimum_elevation] Minimum Elevation - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)
    
def test_maximum_elevation():
    """Test that minimum elevation works for a ground truth value (px4)."""
    from heet_params import maximum_elevation
    
    elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/elev_poly_px4").first()
    ).set('r_imputed_water_elevation', "98")
    elev_poly_px4_ftc = ee.FeatureCollection(elev_poly_px4_ft)
    
    test_input = {
        'reservoir_ftc': elev_poly_px4_ftc,
    }

     
    test_result = 98
    calc_result = maximum_elevation(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[maximum_elevation] Maximum Elevation - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)    

#==============================================================================
#  Depth
#==============================================================================

def test_maximum_depth():
    """Test that maximum depth works for a ground truth value (px4)."""
    from heet_params import maximum_depth
    
    elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/elev_poly_px4").first()
    ).set('r_imputed_water_elevation', "98")
    elev_poly_px4_ftc = ee.FeatureCollection(elev_poly_px4_ft)
    
    test_input = {
        'reservoir_ftc': elev_poly_px4_ftc,
    }

     
    test_result = 2
    calc_result = maximum_depth(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[maximum_depth] Maximum Depth - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)    
    
    
def test_maximum_depth_alt1():
    """Test that maximum depth (alt1) works for a ground truth value (px4)."""
    from heet_params import maximum_depth_alt1
    
    elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/elev_poly_px4").first()
    ).set('r_imputed_water_elevation', "98")
    elev_poly_px4_ftc = ee.FeatureCollection(elev_poly_px4_ft)
    
    test_input = {
        'reservoir_ftc': elev_poly_px4_ftc,
    }
     
    test_result = 1
    calc_result = maximum_depth_alt1(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[maximum_depth_alt1] Maximum Depth Alt1 - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)     
    
def test_maximum_depth_alt2():
    """Test that maximum depth (alt2) works for a ground truth value (px4)."""
    from heet_params import maximum_depth_alt2
    
    elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/elev_poly_px4").first()
    ).set('r_imputed_water_elevation', "98")
    elev_poly_px4_ftc = ee.FeatureCollection(elev_poly_px4_ft)
    
    test_input = {
        'reservoir_ftc': elev_poly_px4_ftc,
    }
    
    test_result = 2
    calc_result = maximum_depth_alt2(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[maximum_elevation] Maximum Depth Alt1 - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)         
    
def test_mean_depth():
    """Test that mean depth works for a ground truth value (px4)."""
    from heet_params import mean_depth
    
    elev_poly_px4_ft = ee.Feature(
        ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/elev_poly_px4").first()
    ).set('r_imputed_water_elevation', "98")
    elev_poly_px4_ftc = ee.FeatureCollection(elev_poly_px4_ft)
    
    test_input = {
        'reservoir_ftc': elev_poly_px4_ftc,
    }

     
    test_result = 1
    calc_result = mean_depth(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[maximum_elevation] Mean Depth - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)             
