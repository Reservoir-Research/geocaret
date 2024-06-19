"""Tests for codes.py"""
import pytest
import heet.codes


def test_emission_codes():
    """Test error codes issued during processing of dam-related data."""
    code1 = heet.codes.EmissionsCodes(2)
    assert code1.name == "Analysis failed at catchment delineation or " \
        "catchment parameter generation."
    with pytest.raises(heet.codes.CodeNotFoundException):
        heet.codes.EmissionsCodes("4")


def test_emission_missingdata_codes():
    """Test error codes issued when data is unavailable ."""
    code1 = heet.codes.EmissionsMissingDataCodes("ND")
    assert code1.name == "Missing Data in GIS Layer"
    with pytest.raises(heet.codes.CodeNotFoundException):
        heet.codes.EmissionsMissingDataCodes("NDD")


def test_emission_damprovenence_codes():
    """Test error codes issued to indicate the method in which dam height is
    obtained for reservoir delineation."""
    code1 = heet.codes.EmissionsDamProvenanceCodes(1)
    assert code1.name == "User input dam height"
    with pytest.raises(heet.codes.CodeNotFoundException):
        heet.codes.EmissionsDamProvenanceCodes(4)
