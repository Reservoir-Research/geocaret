import ee
import os

if "CI_ROBOT_USER" in os.environ:
    print("Running service account authentication")
    gc_service_account = os.environ["GCLOUD_ACCOUNT_EMAIL"]
    credentials = ee.ServiceAccountCredentials(
        gc_service_account, "service_account_creds.json"
    )
    ee.Initialize(credentials)

else:
    print("Running individual account authentication")
    ee.Initialize()

import pytest
import heet_data as dta
import logging

# ==============================================================================
#  Set up logger
# ==============================================================================


# Create new log each run (TODO; better implementation)
with open("tests.log", "w") as file:
    pass


# Gets or creates a logger
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.DEBUG)

# define file handler and set formatter
file_handler = logging.FileHandler("tests.log")
formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)

# Delineation of main river
def test_rwo_delineate_river():
    """Test that delineation of main river runs without error
    for a known dam
    """
    from heet_river import delineate_river

    catchmentAssetName = "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/C_1201"
    catchment_ftc = ee.FeatureCollection(catchmentAssetName)

    reservoirAssetName = "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/R_1201"
    res_ftc = ee.FeatureCollection(reservoirAssetName)

    snappedAssetName = "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/PS_1201"
    damFeat = ee.FeatureCollection(snappedAssetName)

    try:
        mainRiverVector, riverVector = delineate_river(damFeat, res_ftc, "1201")
        msg = "delineate_river completed without explicit error(s)"
    except MyError:
        msg = "delineate_river failed with error(s)"
        pytest.fail("delineate_river failed with error(s)")

    logger.info(f"[test_rwo_delineate_river] " + f"{msg}")
