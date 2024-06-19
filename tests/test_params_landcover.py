
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


def test_landcover_px1():
    """Test that landcover works for a single pixel ground truth example"""
    from heet_params import landcover
    
    landcover_poly_px1 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_poly_px1")
    
    test_input = {
        'land_ftc': landcover_poly_px1,
	    'landcover_analysis_file_str': 'projects/ee-future-dams/assets/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds'
    }
     
    test_result =  np.array([0, 0, 0, 0, 0, 1, 0, 0, 0])
    calc_result = landcover(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_landcover] Landcover - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    assert calc_result  == pytest.approx(np.array(test_result))
    
def test_landcover_px2():
    """Test that landcover works for a 2 pixel, 2 category ground truth example"""
    from heet_params import landcover
    
    landcover_poly_px2 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_poly_px2")
    
    test_input = {
        'land_ftc': landcover_poly_px2,
	    'landcover_analysis_file_str': 'projects/ee-future-dams/assets/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds'        
    }
     
    test_result =  np.array([0, 0, 0.5, 0, 0, 0.5, 0, 0, 0])
    calc_result = landcover(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_landcover] Landcover - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    assert calc_result  == pytest.approx(np.array(test_result))    


def test_landcover_px3():
    """Test that landcover works for a 3 pixel, 2 category ground truth example"""
    from heet_params import landcover
    
    landcover_poly_px3 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_poly_px3")
    
    test_input = {
        'land_ftc': landcover_poly_px3,
	    'landcover_analysis_file_str': 'projects/ee-future-dams/assets/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds'        
    }
     
    test_result =  np.array([0, 2/3, 0, 0, 0, 1/3, 0, 0, 0])
    calc_result = landcover(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_landcover] Landcover - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    assert calc_result  == pytest.approx(np.array(test_result))    
    
def test_landcover_px4():
    """Test that landcover works for a 4 pixel, 2 category ground truth example"""
    from heet_params import landcover
    
    landcover_poly_px4 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_poly_px4")
    
    test_input = {
        'land_ftc': landcover_poly_px4,
	    'landcover_analysis_file_str': 'projects/ee-future-dams/assets/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds'        
    }
     
    test_result =  np.array([0, 0, 0.25, 0.75, 0, 0, 0, 0, 0])
    calc_result = landcover(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_landcover] Landcover - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    assert calc_result  == pytest.approx(np.array(test_result))
    
        
def test_landcover_px155():
    """Test that landcover works for a 2 pixel (1, 0.5, 0.5), 2 category ground truth example"""
    from heet_params import landcover
    
    landcover_poly_px155 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_poly_px155")
    
    test_input = {
        'land_ftc': landcover_poly_px155,
	    'landcover_analysis_file_str': 'projects/ee-future-dams/assets/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds'        
    }
     
    test_result =  np.array([0, 0, 0.5, 0, 0, 0.5, 0, 0, 0])
    calc_result = landcover(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_landcover_bysoil] Landcover by soil - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    assert calc_result  == pytest.approx(np.array(test_result))           

# landcover_bysoil_fracs
def test_landcover_bysoil_fracs_org_px12():
     """Test that landcover stratified by soil type works for a 12 pixel, 4 category ground truth example
        where only organic soil is present
     """
     from heet_params import landcover_bysoil
    
     landcover_bysoil_poly_org_px12 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_bysoil_poly_org_px12")
    
     test_input = {
         'land_ftc': landcover_bysoil_poly_org_px12,
	     'landcover_analysis_file_str': 'projects/ee-future-dams/assets/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds'         
     }
     
     test_result =  np.array([
         0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 6/12, 1/12, 4/12, 0, 0, 1/12, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0                              
     ])
     
     calc_result = landcover_bysoil(**test_input).getInfo() 
     diff = test_result - calc_result 
     pdiff = (abs(test_result - calc_result)/test_result) * 100
    
     logger.info(f'[test_landcover_bysoil] Landcover by soil - HEET {calc_result} ' + 
                 f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
     assert calc_result  == pytest.approx(np.array(test_result))
     
     
def test_landcover_bysoil_fracs_min_px12():
     """Test that landcover stratified by soil type works for a 12 pixel, 3 category ground truth example
        where only mineral soil is present
     """
     from heet_params import landcover_bysoil
    
     landcover_bysoil_poly_min_px12 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_bysoil_poly_min_px12")
    
     test_input = {
         'land_ftc': landcover_bysoil_poly_min_px12,
 	    'landcover_analysis_file_str': 'projects/ee-future-dams/assets/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds'
     }
     
     test_result =  np.array([
         0, 0, 10/12, 1/12, 1/12, 0, 0, 0, 0,         
         0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0                              
     ])
     
     calc_result = landcover_bysoil(**test_input).getInfo() 
     diff = test_result - calc_result 
     pdiff = (abs(test_result - calc_result)/test_result) * 100
    
     logger.info(f'[test_landcover_bysoil] Landcover by soil - HEET {calc_result} ' + 
                 f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
     assert calc_result  == pytest.approx(np.array(test_result))     

def test_landcover_bysoil_fracs_nodata_px1():
     """Test that landcover stratified by soil type works for a 1 pixel, 1 category ground truth example
        where soil type is unknown
     """
     from heet_params import landcover_bysoil
    
     landcover_bysoil_poly_nodata_px1 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_bysoil_poly_nodata_px1")
    
     test_input = {
       'land_ftc': landcover_bysoil_poly_nodata_px1,
	    'landcover_analysis_file_str': 'projects/ee-future-dams/assets/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds'
     }
     
     test_result =  np.array([
          0, 0, 0, 0, 0, 0, 0, 0, 0, 
          0, 0, 0, 0, 0, 0, 0, 0, 0, 
          0, 0, 0, 0, 0, 0, 0, 1, 0,                              
     ])
     
     calc_result = landcover_bysoil(**test_input).getInfo() 
     diff = test_result - calc_result 
     pdiff = (abs(test_result - calc_result)/test_result) * 100
    
     logger.info(f'[test_landcover] Landcover - HEET {calc_result} ' + 
                  f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
     assert calc_result  == pytest.approx(np.array(test_result))
     
def test_landcover_bysoil_fracs_minorg_px4():
     """Test that landcover stratified by soil type works for a 4 pixel, 1 category ground truth example
        where soil type is 1/4 mineral and 3/4 organic
     """
     from heet_params import landcover_bysoil
    
     landcover_bysoil_poly_minorg_px4 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/landcover_bysoil_poly_minorg_px4")
    
     test_input = {
       'land_ftc': landcover_bysoil_poly_minorg_px4,
	    'landcover_analysis_file_str': 'projects/ee-future-dams/assets/XHEET_ASSETS/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2010-v2-0-7cds'
     }
     
     test_result =  np.array([
          0, 0, 1/4, 0, 0, 0, 0, 0, 0, 
          0, 0, 3/4, 0, 0, 0, 0, 0, 0, 
          0, 0, 0, 0, 0, 0, 0, 0, 0,                              
     ])
     
     calc_result = landcover_bysoil(**test_input).getInfo() 
     diff = test_result - calc_result 
     pdiff = (abs(test_result - calc_result)/test_result) * 100
    
     logger.info(f'[test_landcover] Landcover - HEET {calc_result} ' + 
                  f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
     assert calc_result  == pytest.approx(np.array(test_result))     

def test_soc_percent(target_ftc = None):
    """Test that soc_percent is (%SOC) is calculated correctly for a single ground truth example"""
    from heet_params import soc_percent
    
    psoc_poly_org_px1 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/psoc_poly_org_px1")
    
    test_input = {
        'target_ftc': psoc_poly_org_px1    
    }
     
    test_result = 20.8
    calc_result = soc_percent(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_soc_percent] %SOC - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)
    
    

def test_soil_type_mineral(target_ftc = None):
    """Test that mineral soil type is identified correctly for a single ground truth example"""
    from heet_params import soil_type
    
    psoc_poly_min_px1 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/psoc_poly_min_px1")
    
    test_input = {
        'target_ftc': psoc_poly_min_px1,
    }
     
    test_result = "MINERAL"
    calc_result = soil_type(**test_input).getInfo() 
   
    
    logger.info(f'[test_soil_type_mineral] %SOC - HEET {calc_result} ' + 
                f'Manual {test_result}')     
    
    assert calc_result  == test_result

def test_soil_type_organic(target_ftc = None):
    """Test that organic soil type is identified correctly for a single ground truth example"""
    from heet_params import soil_type
    
    psoc_poly_org_px1 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/psoc_poly_org_px1")
    
    test_input = {
        'target_ftc': psoc_poly_org_px1 
    }
     
    test_result = "ORGANIC"
    calc_result = soil_type(**test_input).getInfo() 
   
    
    logger.info(f'[test_soil_type_mineral] %SOC - HEET {calc_result} ' + 
                f'Manual {test_result}')     
    
    assert calc_result  == test_result
    
