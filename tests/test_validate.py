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
import json
import yaml
from frictionless import Resource

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

# ==============================================================================
# Output Validation
# ==============================================================================

# Check that the live frictionless output profile
# is valid
def test_validate_output_profile():
    resource_definition = Resource("utils/outputs.resource.yaml")

    try:
        Resource(resource_definition)
        test_result = True
    except Exception as exception:
        print(exception.error)
        print(exception.reasons)
        test_result = False

    assert test_result == True


# Output Validation
def test_valid_output_fields_true():
    """Test that output validation runs successfully on a valid example output file."""
    from heet_validate import valid_output_fields
    from heet_validate import csv_to_df

    output_file_path = "tests/data/output_parameters_valid_fields.csv"
    df_output = csv_to_df(output_file_path)

    test_input = {"df": df_output}

    test_result = True
    calc_return = valid_output_fields(**test_input)

    calc_result = calc_return["valid"]
    calc_issues = calc_return["issues"]

    logger.info(
        f"[test_valid_output_fields_true] Output Fields Validation - HEET {calc_result} "
        + f"Manual {test_result}"
        + f"Issues {calc_issues}"
    )

    assert calc_result == test_result


def test_valid_output_fields_false():
    """Test that output validation runs successfully on an invalid example output file."""
    from heet_validate import valid_output_fields
    from heet_validate import csv_to_df

    output_file_path = "tests/data/output_parameters_invalid_fields.csv"
    df_output = csv_to_df(output_file_path)

    test_input = {
        "df": df_output,
    }

    test_result = False

    calc_return = valid_output_fields(**test_input)
    calc_result = calc_return["valid"]
    calc_issues = calc_return["issues"]

    logger.info(
        f"[test_valid_output_fields_false] Output Validation - HEET {calc_result} "
        + f"Manual {test_result}"
        + f"Issues {calc_issues}"
    )

    assert calc_result == test_result


# Output Validation
def test_valid_output_true():
    """Test that output validation runs successfully on a valid example output file."""
    from heet_validate import valid_output
    from heet_validate import csv_to_df

    output_file_path = "tests/data/output_parameters_valid.csv"
    df_output = csv_to_df(output_file_path)

    test_input = {
        "df": df_output,
        "output_file_path": output_file_path,
        "output_folder_path": "tests/tmp",
    }

    test_result = True
    calc_result = valid_output(**test_input)["valid"]

    if test_result == False:
        os.rename(
            "tests/tmp/heet_output_report.csv", "tests/tmp/heet_output_report_true.csv"
        )

    logger.info(
        f"[test_valid_output_true] Output Validation - HEET {calc_result} "
        + f"Manual {test_result} "
    )

    # Within 0.05%
    assert calc_result == test_result


def test_valid_output_false():
    """Test that output validation runs successfully on an invalid example output file."""
    from heet_validate import valid_output
    from heet_validate import csv_to_df

    output_file_path = "tests/data/output_parameters_invalid.csv"
    df_output = csv_to_df(output_file_path)

    test_input = {
        "df": df_output,
        "output_file_path": output_file_path,
        "output_folder_path": "tests/tmp",
    }

    test_result = False
    calc_result = valid_output(**test_input)["valid"]

    if test_result == False:
        os.rename(
            "tests/tmp/heet_output_report.csv", "tests/tmp/heet_output_report_false.csv"
        )

    logger.info(
        f"[test_valid_output_false] Output Validation - HEET {calc_result} "
        + f"Manual {test_result} "
    )

    # Within 0.05%
    assert calc_result == test_result


# ==============================================================================
# Input validation
# ==============================================================================

# Check that the frictionless input profile
# is valid
def test_validate_input_profile():
    resource_definition = Resource("utils/inputs.resource.yaml")
    try:
        Resource(resource_definition)
        test_result = True
    except Exception as exception:
        print(exception.error)
        print(exception.reasons)
        test_result = False

    assert test_result == True


# Input Validation
def test_valid_input_fields_true():
    """Test that field validation works on a correct input file"""
    from heet_validate import valid_input_fields
    from heet_validate import csv_to_df

    input_file_path = "tests/data/dams_valid.csv"
    df_input = csv_to_df(input_file_path)

    test_input = {"df": df_input}

    test_result = True
    calc_result = valid_input_fields(**test_input)["valid"]

    logger.info(
        f"[test_valid_input_fields_true]  Validate input fields - HEET {calc_result} "
        + f"Manual {test_result} "
    )

    assert calc_result == test_result


def test_valid_input_fields_false():
    """Test that field validation works on a correct input file"""
    from heet_validate import valid_input_fields
    from heet_validate import csv_to_df

    input_file_path = "tests/data/dams_invalid_fields.csv"
    df_input = csv_to_df(input_file_path)

    test_input = {"df": df_input}

    test_result = False
    calc_result = valid_input_fields(**test_input)["valid"]

    logger.info(
        f"[test_valid_input_fields_true]  Validate input fields - HEET {calc_result} "
        + f"Manual {test_result} "
    )

    assert calc_result == test_result


def test_valid_input_true():
    """Test that field validation works on a correct input file"""
    from heet_validate import valid_input
    from heet_validate import csv_to_df

    input_file_path = "tests/data/dams_valid.csv"
    df_input = csv_to_df(input_file_path)

    test_input = {
        "df": df_input,
        "input_file_path": input_file_path,
        "output_folder_path": "tests/tmp",
    }

    test_result = True
    calc_result = valid_input(**test_input)["valid"]

    logger.info(
        f"[test_valid_input_true]  Validate input  - HEET {calc_result} "
        + f"Manual {test_result} "
    )

    assert calc_result == test_result


def test_valid_input_false():
    """Test that field validation works on a correct input file"""
    from heet_validate import valid_input
    from heet_validate import csv_to_df

    input_file_path = "tests/data/dams_invalid_input.csv"
    df_input = csv_to_df(input_file_path)

    test_input = {
        "df": df_input,
        "input_file_path": input_file_path,
        "output_folder_path": "tests/tmp",
    }

    test_result = False
    calc_result = valid_input(**test_input)["valid"]

    logger.info(
        f"[test_valid_input_false]  Validate input  - HEET {calc_result} "
        + f"Manual {test_result} "
    )

    assert calc_result == test_result


# ==============================================================================
# Utils
# ==============================================================================


def is_valid_json(json_dict):
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
def test_generate_json_output():
    """Test that json output generate produces valid json (single dam)"""
    from heet_export import generate_json_output

    out_ft = ee.FeatureCollection(
        "projects/ee-future-dams/assets/XHEET_TEST_EXAMPLE/output_parameters"
    ).first()

    test_input = {"out_ft": out_ft}

    test_result = True
    calc_result = is_valid_json(generate_json_output(**test_input))

    logger.info(
        f"[test_generate_json_output] JSON Output Validation - HEET {calc_result} "
        + f"Manual {test_result} "
    )

    assert calc_result == test_result
