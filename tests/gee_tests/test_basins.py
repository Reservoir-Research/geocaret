""" """
import pytest
import ee
import os


@pytest.mark.parametrize(
    "A, B, expected_result",
    [
        ("987654321987", "987654321900", "87"),
        ("987654321900", "987654321987", "00"),
    ]
)
def test_get_trailA(A, B, expected_result) -> None:
    """Test the get_trailA function for extracting trailing digits of Pfafstetter ID A.
    
    This test checks the correctness of the get_trailA function, which extracts the 
    trailing digits of the Pfafstetter ID 'A' relative to another ID 'B'. The function
    is tested with two sets of inputs to validate its accuracy.

    Args:
        A (str): The Pfafstetter ID 'A'.
        B (str): The Pfafstetter ID 'B'.
        expected_result (str): The expected trailing digits of 'A' relative to 'B'.
    """
    from heet_basins import get_trailA
    test_input = {
        'A': ee.String(A),
        'B': ee.String(B)}
    assert get_trailA(**test_input).getInfo() == expected_result
  

@pytest.mark.parametrize(
    "digit_string, expected_result",
    [
        ("624", 0),   # Test case: not all odd digits
        ("357", 1),   # Test case: all odd digits
        ("", 0),      # Test case: empty string
    ]
)
def test_all_odd_or_zero(digit_string, expected_result) -> None:
    """Test the all_odd_or_zero function for identifying strings with all odd digits.
    
    This test checks the correctness of the all_odd_or_zero function, which identifies
    whether a given string contains all odd digits. The function is tested with 
    three different inputs to validate its accuracy.
    
    Args:
        digit_string (str): The string of digits to check.
        expected_result (int): The expected result (1 if all digits are odd, 0 otherwise).
    """
    from heet_basins import all_odd_or_zero
    test_input = {'digit_string': ee.String(digit_string),}
    result = all_odd_or_zero(**test_input).getInfo()
    assert result == expected_result

