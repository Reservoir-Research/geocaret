
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
#  Biome
#==============================================================================

def test_predominant_biome():
    """Test that mean soil organic carbon works for a ground truth value (10/90)."""
    from heet_params import predominant_biome
    
    biome_poly_1090 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/biome_poly_1090")
    
    test_input = {
        'catchment_ftc': biome_poly_1090,
    }
     
    # 5 - Temperate Conifer Forests
    # 4 - Temperate Broadleaf & Mixed Forests
    test_result = "Temperate Conifer Forests"
    calc_result = predominant_biome(**test_input).getInfo() 
        
    logger.info(f'[test_predominant_biome] Predominant Biome - HEET {calc_result} ' + 
                f'Manual {test_result}')     
    
    assert calc_result  == test_result

#==============================================================================
#  Evapotranspiration (UDEL)
#==============================================================================

def test_twbda_annual_mean_pet():
    """Test that twbda_annual_mean_pet works for a ground truth value (px2)."""
    from heet_params import twbda_annual_mean_pet
    
    twbda_poly_px2 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/twbda_poly_px2")
    
    test_input = {
        'target_ftc': twbda_poly_px2,
    }
     
    test_result = 17.3 
    calc_result = twbda_annual_mean_pet(**test_input).getInfo() 
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[mean_slope_perc] Mean Slope % - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(test_result, rel=5e-2)


#==============================================================================
#  Population
#==============================================================================

def test_population():
    """Test that population works for a ground truth value (px4)."""
    from heet_params import population
    
    pop_poly_px4 = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_POLYS/pop_poly_px4")
    
    test_input = {
        'target_ftc': pop_poly_px4,
    }
     
    test_result =  np.array([1879.612, 900.0527])
    pop_count, pop_density = population(**test_input)
    calc_result =  np.array([pop_count.getInfo(), pop_density.getInfo()])
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    
    logger.info(f'[test_population_px4] Population - HEET {calc_result} ' + 
                f'Manual {test_result} Diff {diff} PDiff {pdiff}')     
    
    # Within 0.05%
    assert calc_result  == pytest.approx(np.array(test_result), rel=5e-2)

#==============================================================================
#  Fekete Runoff
#==============================================================================


# Runoff (Fekete) Cross-reference with hydrobasins
def test_fekete_crossref_ro():
    """Test that fekete ro is same order of magnitude as hydroAtlas value"""
    from heet_params import mean_annual_runoff_mm
        
    REFDATA = ee.FeatureCollection("projects/ee-future-dams/assets/XHEET_TEST_ASSETS/BasinATLAS_v10_lev12") 

    # C1;  4121051890
    target_ftc = (dta.HYDROBASINS12
      .filter(ee.Filter.eq('HYBAS_ID', 4121051890))
    )
    
    test_input = {
        'catchment_ftc': target_ftc
     }
       
    test_result =  ee.Feature(REFDATA
      .filter(ee.Filter.eq('HYBAS_ID', 4121051890)).first()
    ).get('run_mm_syr').getInfo()
    
    calc_result = ee.Number(mean_annual_runoff_mm(**test_input)).getInfo()
    
    
    diff = test_result - calc_result 
    pdiff = (abs(test_result - calc_result)/test_result) * 100
    rdiff = abs(calc_result/test_result)
        
    logger.info(f'[test_fekete_crossref_ro] - HEET Fekete {calc_result} ' + 
                f'HydroAtlas {test_result} Diff {diff} PDiff {pdiff}')      
                    
    
    assert 0.1 < rdiff < 10

