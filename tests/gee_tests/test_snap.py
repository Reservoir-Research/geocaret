"""
Module for testing functions in the `heet_snap` module.

This module includes unit tests for snapping points to lines and verifying intersections
with hydro-river features. The tests ensure that the snapping operations are accurate and
correctly handle various edge cases.
"""
from typing import Tuple
import ee
import os
import pytest
import numpy as np


@pytest.mark.parametrize(
    "point, start_of_line_segment, end_of_line_segment, expected_result",
    [
        ((5, 3), (-6, 1), (10, 9), (3.6, 5.8)),
        ((-8, 0), (-6, 1), (10, 9), (-6, 1)),
        ((12, 10), (-6, 1), (10, 9), (10, 9))
    ]
)
def test_snap_pt_to_line(
        get_logger, 
        point: Tuple[int, int], 
        start_of_line_segment: Tuple[int, int], 
        end_of_line_segment: Tuple[int, int], 
        expected_result: Tuple[int, int]) -> None:
    """
    Tests the `snap_pt_to_line` function for various snapping scenarios:
    - Point projects onto the line segment.
    - Point does not project onto the line segment, and is closest to the start of the line segment.
    - Point does not project onto the line segment, and is closest to the end of the line segment.

    Args:
        get_logger (function): A pytest fixture to obtain a logger instance for logging test results.
        point (Tuple[int, int]): The point to be snapped.
        start_of_line_segment (Tuple[int, int]): The start of the line segment.
        end_of_line_segment (Tuple[int, int]): The end of the line segment.
        expected_result (Tuple[int, int]): The expected result of the snapping operation.

    Asserts:
        - The calculated snapped point should be approximately equal to the expected result.
    """
    from heet_snap import snap_pt_to_line
    test_input = {
        "P": ee.Array(list(point)),
        "A": ee.Array(list(start_of_line_segment)),
        "B": ee.Array(list(end_of_line_segment))
    }
    calc_result = np.array(snap_pt_to_line(**test_input).getInfo())
    diff = expected_result - calc_result
    logger = get_logger
    logger.info(
        f"[test_snap_pt_to_line] Snapped point - GeoCARET {calc_result} " +
        f"Manual {expected_result} Diff {diff}"
    )
    expected_result_ee = np.array(list(expected_result))
    assert calc_result == pytest.approx(expected_result_ee)


def test_snap_intersects_hydroriver(get_logger) -> None:
    """
    Test that a snapped dam location intersects with a hydro-river feature.

    This test verifies that the `jensen_snap_hydroriver` function from the `heet_snap` module
    correctly snaps a dam location to a hydro-river feature. It checks if the snapped location
    intersects with any hydro-river features in the dataset.

    Args:
        get_logger (function): A pytest fixture to obtain a logger instance for logging test results.

    Assertions:
        - The number of intersecting hydro-river features should be greater than 0.

    Test Details:
        - Input:
            - Dam location: Point(98.580461, 26.051936)
    """
    from heet_snap import jensen_snap_hydroriver
    import heet_data as dta
    damFeat = ee.Feature(ee.Geometry.Point(ee.Number(98.580461), ee.Number(26.051936)))
    snappedDamFeat = jensen_snap_hydroriver(damFeat)
    interReaches = dta.HYDRORIVERS.filterBounds(snappedDamFeat.geometry())
    n_reaches = interReaches.size().getInfo()
    logger = get_logger
    logger.info(
        f"[test_snap_intersects_hydroriver] Reaches intersecting snapped dam ({n_reaches}) "
    )
    assert n_reaches > 0
