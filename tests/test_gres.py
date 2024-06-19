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
import numpy as np

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

# Slope
# -------
# Skip this test as GRES uses a different raw datasource of lower
# resolution (possible NOAA DEM)
@pytest.mark.skip
def test_mean_slope_perc_gres():
    """Test that mean slope function produces the same value as GRES for GAWLAN
    catchment (W_12_Catchment).
    """
    from heet_params import mean_slope_perc

    W_12_Catchment = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/W_12_Catchment"
    )

    test_input = {
        "catchment_ftc": W_12_Catchment,
    }

    # GRES Value degrees: 3.855828478191038; perc: 6.74
    test_result = 6.74
    calc_result = mean_slope_perc(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100

    logger.info(
        f"[mean_slope_perc] Mean Slope % - HEET {calc_result} "
        + f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )

    # Within 0.005
    assert calc_result == pytest.approx(test_result, abs=5e-3)


# mghr
# -------
# Skip this test as GRES uses a different, unknown underlying raw datasource
@pytest.mark.skip
def test_mghr_gres():
    """Test that mghr reproduces a ground truth value (W_12_Catchment)."""
    from heet_params import mghr

    W_12_Reservoir = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/W_12_Reservoir_Annotated"
    )

    test_input = {
        "catchment_ftc": W_12_Reservoir,
    }

    # GRES Value
    test_result = 4.46
    calc_result = mghr(**test_input)[0].getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100

    logger.info(
        f"[mghr] MGHR - HEET {calc_result} "
        + f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )

    # Within 0.005
    assert calc_result == pytest.approx(test_result, abs=5e-3)


# mean_annual_runoff_mm
def test_mean_annual_runoff_mm_gres():
    """Test that mean runoff function reproduces a ground truth value (W_12_Catchment)."""
    from heet_params import mean_annual_runoff_mm

    W_12_Catchment = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/W_12_Catchment"
    )

    test_input = {
        "catchment_ftc": W_12_Catchment,
    }

    # GRES Value
    test_result = 1685.5618570695235
    calc_result = mean_annual_runoff_mm(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100

    logger.info(
        f"[mean_annual_runoff_mm] Runoff - HEET {calc_result} "
        + f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )

    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


# population
# -------
# Skip this test as although GRES uses the same data product, the year used
# (unknown) is different to that used by this tool (2020)
@pytest.mark.skip
def test_population_gres():
    """Test that population function reproduces a ground truth value (W_12_Catchment)."""
    from heet_params import population

    W_12_Catchment = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/W_12_Catchment"
    )

    test_input = {
        "target_ftc": W_12_Catchment,
    }

    # GRES Value
    test_result_1 = 8462.955230759912
    test_result_2 = 10.82177198010264

    ee_calc_result_1, ee_calc_result_2 = population(**test_input)

    calc_result_1 = ee_calc_result_1.getInfo()
    calc_result_2 = ee_calc_result_2.getInfo()

    diff1 = test_result_1 - calc_result_1
    pdiff1 = (abs(test_result_1 - calc_result_1) / test_result_1) * 100

    diff2 = test_result_2 - calc_result_2
    pdiff2 = (abs(test_result_2 - calc_result_2) / test_result_2) * 100

    logger.info(
        f"[population] Population Count - HEET {calc_result_1} "
        + f"Manual {test_result_1} Diff {diff1} PDiff {pdiff1}"
    )

    logger.info(
        f"[population] Population Density - HEET {calc_result_2} "
        + f"Manual {test_result_2} Diff {diff2} PDiff {pdiff2}"
    )

    # Within 0.05%
    assert calc_result_1 == pytest.approx(test_result_1, rel=5e-2)
    assert calc_result_2 == pytest.approx(test_result_2, rel=5e-2)


# maximum_depth_alt1
# -------------------
# Skip this test as although GRES uses the same raw data source, the scale at
# which the calculation is done is much higher (300)
# (informally - when the scale of calculation is the same, values do match)
# @pytest.mark.skip
def test_maximum_depth_alt1_gres(monkeypatch):
    """Test that mean runoff function reproduces a ground truth value (W_12_Reservoir)."""
    from heet_params import maximum_depth_alt1

    # Set config parameters
    monkeypatch.setattr("heet_params.cfg.jensen_search_radius", 1000)
    monkeypatch.setattr("heet_params.cfg.upstreamMethod", 3)
    monkeypatch.setattr("heet_params.cfg.paramHydroDEM", False)
    monkeypatch.setattr("heet_params.cfg.resHydroDEM", False)
    monkeypatch.setattr("heet_params.cfg.hydrodataset", "03")
    monkeypatch.setattr("heet_params.cfg.delineate_snapped", True)

    W_12_Reservoir = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/W_12_Reservoir_Annotated"
    )

    test_input = {
        "reservoir_ftc": W_12_Reservoir,
    }

    # GRES Value at 30 m scale
    test_result = 143
    calc_result = maximum_depth_alt1(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100

    logger.info(
        f"[mean_annual_runoff_mm] Runoff - HEET {calc_result} "
        + f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )

    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)


# mean_depth
# Skip this test as although GRES uses a similar approach, they are not equivalent
# GRES uses max elevation as reference point for depth
# HEET uses elevation of imputed water level
@pytest.mark.skip
def test_mean_depth_gres():
    """Test that mean depth function reproduces a ground truth value (W_12_Reservoir)."""
    from heet_params import mean_depth

    W_12_Reservoir = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_POLYS/W_12_Reservoir_Annotated"
    )

    test_input = {
        "reservoir_ftc": W_12_Reservoir,
    }

    # GRES Value (at 30m scale)
    test_result = 105.38015788589671
    calc_result = mean_depth(**test_input).getInfo()
    diff = test_result - calc_result
    pdiff = (abs(test_result - calc_result) / test_result) * 100

    logger.info(
        f"[mean_depth] Mean Depth - HEET {calc_result} "
        + f"Manual {test_result} Diff {diff} PDiff {pdiff}"
    )

    # Within 0.05%
    assert calc_result == pytest.approx(test_result, rel=5e-2)
