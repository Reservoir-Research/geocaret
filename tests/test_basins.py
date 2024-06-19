"""Collection of tests for """
import ee
from heet.earth_engine import EarthEngine
import heet.basins

EarthEngine.init()


def test_get_trailA():
    """Check that given two Pfafstetter ids A and B, extracts trailing digits of A"""

    test_input = {
        "A": ee.String("987654321987"),
        "B": ee.String("987654321900")}

    test_result = "87"

    assert heet.basins.get_trailA(**test_input).getInfo() == test_result

    test_input = {
        "A": ee.String("987654321900"),
        "B": ee.String("987654321987")}

    test_result = "00"

    assert heet.basins.get_trailA(**test_input).getInfo() == test_result


def test_all_odd_or_zero():
    """Check correctly identifies strings containing all odd or zero"""

    test_input = {
        "digit_string": ee.String("624"),
    }

    test_result = 0
    assert heet.basins.all_odd_or_zero(**test_input).getInfo() == test_result

    test_input = {
        "digit_string": ee.String("357"),
    }

    test_result = 1

    assert heet.basins.all_odd_or_zero(**test_input).getInfo() == test_result

    test_input = {
        "digit_string": ee.String(""),
    }

    test_result = 0

    assert heet.basins.all_odd_or_zero(**test_input).getInfo() == test_result
