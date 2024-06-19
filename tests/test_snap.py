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
import numpy as np
import heet_data as dta
import logging


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


def test_snap_pt_to_line_c1():
    """Test that snap_pt_to_line works for a set of test values
    pre-checked with an online calculator
    case 1: point projects onto line segment
    """
    from heet_snap import snap_pt_to_line

    test_input = {
        "P": ee.Array([5, 3]),
        "A": ee.Array([-6, 1]),
        "B": ee.Array([10, 9]),
    }

    test_result = np.array([3.6, 5.8])
    calc_result = np.array(snap_pt_to_line(**test_input).getInfo())
    diff = test_result - calc_result

    logger.info(
        f"[test_snap_pt_to_line] Snapped point- HEET {calc_result} "
        + f"Manual {test_result} Diff {diff}"
    )

    assert calc_result == pytest.approx(test_result)


def test_snap_pt_to_line_c2():
    """Test that snap_pt_to_line works for a set of test values
    pre-checked with an online calculator
    case 2: point does not project onto line segment and is closed to P1 (A)
    """
    from heet_snap import snap_pt_to_line

    test_input = {
        "P": ee.Array([-8, 0]),
        "A": ee.Array([-6, 1]),
        "B": ee.Array([10, 9]),
    }

    test_result = np.array([-6, 1])
    calc_result = np.array(snap_pt_to_line(**test_input).getInfo())
    diff = test_result - calc_result

    logger.info(
        f"[test_snap_pt_to_line] Snapped point- HEET {calc_result} "
        + f"Manual {test_result} Diff {diff}"
    )

    assert calc_result == pytest.approx(test_result)


def test_snap_pt_to_line_c3():
    """Test that snap_pt_to_line works for a set of test values
    pre-checked with an online calculator
    case 3: point does not project onto line segment and is closed to P2 (B)
    """
    from heet_snap import snap_pt_to_line

    test_input = {
        "P": ee.Array([12, 10]),
        "A": ee.Array([-6, 1]),
        "B": ee.Array([10, 9]),
    }

    test_result = np.array([10, 9])
    calc_result = np.array(snap_pt_to_line(**test_input).getInfo())
    diff = test_result - calc_result

    logger.info(
        f"[test_snap_pt_to_line] Snapped point- HEET {calc_result} "
        + f"Manual {test_result} Diff {diff}"
    )

    assert calc_result == pytest.approx(test_result)


def test_snap_intersects_hydroriver():
    """Test snapped dam location intersects a hydroriver"""
    from heet_snap import jensen_snap_hydroriver

    damFeat = ee.Feature(ee.Geometry.Point(ee.Number(98.580461), ee.Number(26.051936)))

    snappedDamFeat = jensen_snap_hydroriver(damFeat)

    interReaches = dta.HYDRORIVERS.filterBounds(snappedDamFeat.geometry())
    n_reaches = interReaches.size().getInfo()

    logger.info(
        f"[test_snap_intersects_hydroriver] Reaches intersecting snapped dam ({n_reaches}) "
    )

    assert n_reaches > 0
