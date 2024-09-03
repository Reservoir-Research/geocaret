"""
Module: test_validate.py

This module contains unit tests for validating the input and output data of a hydropower modeling framework.
It uses the `pytest` framework to verify the correctness and integrity of various data processing and validation
functions. The tests ensure that the input and output files conform to specified formats and data profiles,
check for valid JSON outputs, and verify that the appropriate error handling and logging are performed.

Tests included:
- `test_validate_output_profile`: Validates the output profile using the Frictionless Data Resource framework.
- `test_valid_output_fields`: Test output field validation for both valid and invalid output files.
- `test_valid_output`: Test complete output validation with both valid and invalid example output files.
- `test_validate_input_profile`: Validates the input profile using the Frictionless Data Resource framework.
- `test_valid_input_fields`: Test input field validation with both valid and invalid input files.
- `test_valid_input`: Test complete input validation with both valid and invalid input files.
- `test_generate_json_output`: Ensures the generated JSON output for a single dam is valid.

Each test function typically follows the pattern:
1. Setting up test input data.
2. Executing the function being tested.
3. Comparing the function's output with expected results.
4. Logging results and asserting correctness.

Several tests are used for testing successful and unsuccesful validations. We used the
`@pytest.mark.parametrize` decorator for testing both situations within one testing function.

All test functions make use of Earth Engine objects and resources, and require an authenticated session
with the Earth Engine API to run successfully.
"""
import ee
import os
import pytest
import numpy as np
import json
import yaml
from frictionless import Resource

# ==============================================================================
# Output Validation
# ==============================================================================

# Check that the live frictionless output profile
# is valid
def test_validate_output_profile(root_folder) -> None:
    """Test that the live frictionless output profile is valid.

    This test checks if the output profile defined in 'csv-schemas/outputs.resource.yaml'
    is a valid Frictionless resource. It attempts to create a Resource object 
    from the YAML definition and asserts that it is valid.
    
    Args:
        root_folder: A pytest fixture returning root folder of the package.

    Asserts:
        True if the output profile is valid, otherwise False.

    Raises:
        Exception: If the resource definition is not valid, 
        an exception is raised and caught.
    """
    resource_definition = Resource(root_folder / "csv-schemas" / "outputs.resource.yaml")
    try:
        Resource(resource_definition)
        test_result = True
    except Exception as exception:
        print(exception.error)
        print(exception.reasons)
        test_result = False
    assert test_result == True


# Output Field Validation
@pytest.mark.parametrize(
    "output_file_path, expected_validity",
    [
        ("../../tests/data/output_parameters_valid_fields.csv", True),
        ("../../tests/data/output_parameters_invalid_fields.csv", False),
    ],
)
def test_valid_output_fields(get_logger, root_folder, output_file_path, expected_validity) -> None:
    """Test output field validation for both valid and invalid output files.

    This test checks the `valid_output_fields` function using both a valid
    and an invalid CSV file. It expects the function to return the appropriate
    validity status based on the contents of the file.

    Args:
        get_logger: A fixture or callable that returns a logger instance.
        root_folder: A fixture returning root folder of the package.
        output_file_path: Path to the output file being tested.
        expected_validity: The expected validity status of the output file.

    Asserts:
        True if the output fields match the expected validity, otherwise False.
    """
    from geocaret.validate import valid_output_fields
    from geocaret.validate import csv_to_df
    df_output = csv_to_df(root_folder / output_file_path)
    test_input = {"df": df_output}
    calc_return = valid_output_fields(**test_input)
    calc_result = calc_return["valid"]
    calc_issues = calc_return["issues"]
    logger = get_logger
    logger.info(
        f"[test_valid_output_fields_true] Output Fields Validation - GeoCARET {calc_result} " +
        f"Manual {expected_validity}" +
        f"Issues {calc_issues}"
    )
    assert calc_result == expected_validity


# Output Validation
@pytest.mark.parametrize(
    "output_file_path, expected_validity, report_name_suffix",
    [
        ("../../tests/data/output_parameters_valid.csv", True, "true"),
        ("../../tests/data/output_parameters_invalid.csv", False, "false"),
    ],
)
def test_valid_output(get_logger, root_folder, output_file_path, expected_validity, report_name_suffix) -> None:
    """Test complete output validation with both valid and invalid example output files.

    This test checks the `valid_output` function using both a valid and an invalid CSV file.
    It expects the function to return the appropriate validity status based on the contents of the file.

    Args:
        get_logger: A fixture or callable that returns a logger instance.
        root_folder: A fixture returning root folder of the package.
        output_file_path: Path to the output file being tested.
        expected_validity: The expected validity status of the output file.
        report_name_suffix: Suffix for renaming the output report file.

    Asserts:
        True if the output matches the expected validity, otherwise False.
    """
    from geocaret.validate import valid_output
    from geocaret.validate import csv_to_df
    df_output = csv_to_df(root_folder / output_file_path)
    test_input = {
        "df": df_output,
        "output_file_path": root_folder / output_file_path,
        "output_folder_path": root_folder / "../../tests/tmp",
    }
    calc_result = valid_output(**test_input)["valid"]
    
    if calc_result != expected_validity:
        os.rename(
            root_folder / "../../tests/tmp/geocaret_output_report.csv", 
            root_folder / f"../../tests/tmp/geocaret_output_report_{report_name_suffix}.csv"
        )
    logger = get_logger
    logger.info(
        f"[test_valid_output] Output Validation - GeoCARET {calc_result} " +
        f"Expected {expected_validity} "
    )
    # Within 0.05%
    assert calc_result == expected_validity


# ==============================================================================
# Input validation
# ==============================================================================

# Check that the frictionless input profile
# is valid
def test_validate_input_profile(root_folder) -> None:
    """Test that the frictionless input profile is valid.

    This test checks if the input profile defined in 'csv-schemas/inputs.resource.yaml'
    is a valid Frictionless resource. It attempts to create a Resource object 
    from the YAML definition and asserts that it is valid.

    Asserts:
        True if the input profile is valid, otherwise False.

    Raises:
        Exception: If the resource definition is not valid, 
        an exception is raised and caught.
    """
    resource_definition = Resource(root_folder / "csv-schemas" / "inputs.resource.yaml")
    try:
        Resource(resource_definition)
        test_result = True
    except Exception as exception:
        print(exception.error)
        print(exception.reasons)
        test_result = False
    assert test_result == True


# Input Validation
@pytest.mark.parametrize(
    "input_file_path, expected_validity",
    [
        ("../../tests/data/dams_valid.csv", True),
        ("../../tests/data/dams_invalid_fields.csv", False),
    ],
)
def test_valid_input_fields(get_logger, root_folder, input_file_path, expected_validity) -> None:
    """Test input field validation with both valid and invalid input files.

    This test checks the `valid_input_fields` function using both a valid and an invalid CSV file.
    It expects the function to return the appropriate validity status based on the contents of the file.

    Args:
        get_logger: A fixture or callable that returns a logger instance.
        root_folder: A fixture returning root folder of the package.
        input_file_path: Path to the input file being tested.
        expected_validity: The expected validity status of the input file.

    Asserts:
        True if the input matches the expected validity, otherwise False.
    """
    from geocaret.validate import valid_input_fields
    from geocaret.validate import csv_to_df
    df_input = csv_to_df(root_folder / input_file_path)
    test_input = {"df": df_input}
    calc_result = valid_input_fields(**test_input)["valid"]
    logger = get_logger
    logger.info(
        f"[test_valid_input_fields]  Validate input fields - GeoCARET {calc_result} " +
        f"Expected {expected_validity} "
    )
    assert calc_result == expected_validity


@pytest.mark.parametrize(
    "input_file_path, expected_result",
    [
        ("../../tests/data/dams_valid.csv", True),
        ("../../tests/data/dams_invalid_input.csv", False),
    ]
)
def test_valid_input(get_logger, root_folder, input_file_path, expected_result) -> None:
    """Test complete input validation with both valid and invalid input files.

    This test checks the `valid_input` function using both valid and invalid CSV files.
    It expects the function to return `True` for valid input files and `False` for invalid ones.

    Args:
        get_logger: A fixture or callable that returns a logger instance.
        root_folder: A fixture returning root folder of the package.
        input_file_path: Path to the CSV file to be tested.
        expected_result: Expected boolean result of the validation.

    Asserts:
        The result of the input validation matches the expected_result.
    """
    from geocaret.validate import valid_input
    from geocaret.validate import csv_to_df
    df_input = csv_to_df(root_folder / input_file_path)
    test_input = {
        "df": df_input,
        "input_file_path": input_file_path,
        "output_folder_path": root_folder / "../../tests/tmp",
    }
    calc_result = valid_input(**test_input)["valid"]
    logger = get_logger
    logger.info(
        f"[test_valid_input]  Validate input  - GeoCARET {calc_result} " +
        f"Expected {expected_result} "
    )
    assert calc_result == expected_result


# ==============================================================================
# Utils
# ==============================================================================


def is_valid_json(json_dict) -> bool:
    """Helper function to check if a dictionary is valid JSON.

    Converts a dictionary to a JSON string and attempts to parse it back.
    If parsing fails, the dictionary is not valid JSON.
    
    Args:
        json_dict: A dictionary object to be checked.
    
    Returns:
        bool: `True` if the dictionary is valid JSON, otherwise `False`.

    Raises:
        TypeError: If the input is not a dictionary.
        ValueError: If the dictionary cannot be serialized into JSON.
    """
    json_object = json.dumps(json_dict, indent=4)
    try:
        json.loads(json_object)
    except ValueError as e:
        return False
    return True


# ==============================================================================
# JSON Export
# ==============================================================================

# Output Validation
def test_generate_json_output(get_logger) -> None:
    """Test that JSON output generation produces valid JSON for a single dam.

    This test checks the `generate_json_output` function to ensure it produces valid JSON output.
    It retrieves a feature from a specified Earth Engine FeatureCollection, generates JSON output using 
    the function, and verifies that the output is valid JSON.

    Args:
        get_logger: A fixture or callable that returns a logger instance.

    Asserts:
        True if the generated JSON output is valid, otherwise False.

    Raises:
        AssertionError: If the generated JSON output is not valid.
    """
    from geocaret.export import generate_json_output
    out_ft = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/output_parameters"
    ).first()
    test_input = {"out_ft": out_ft}
    test_result = True
    calc_result = is_valid_json(generate_json_output(**test_input))
    logger = get_logger
    logger.info(
        f"[test_generate_json_output] JSON Output Validation - GeoCARET {calc_result} " +
        f"Manual {test_result} "
    )
    assert calc_result == test_result
