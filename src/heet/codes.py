"""Module with classes providing error and warning codes."""
from typing import ClassVar, Tuple, TypeVar, Union, Dict
from abc import ABC, abstractmethod

KeyType = TypeVar('KeyType', bound=Union[int, float, str])


class CodeNotFoundException(Exception):
    """Exception raised if attempting to generate a code that is not available.

    Attributes:
        codes (tuple): available code items.
        message (str): explanation of the error
    """
    def __init__(
            self,
            codes: Tuple,
            message: str = "Error code not recognized.") -> None:
        """ """
        self.codes = codes
        self.message = message + \
            f" Available error codes: {self.codes}"
        super().__init__(self.message)


class Codes(ABC):
    """Interface for `Codes` child classes."""
    codes: ClassVar[Dict[KeyType, str]]

    def __init__(self, value: KeyType) -> None:
        """Set code value

        Raise: CodeNotFoundException."""
        if value in self.codes:
            self._value = value  # type: KeyType
        else:
            raise CodeNotFoundException(codes=tuple(self.codes.keys()))

    @property
    @abstractmethod
    def name(self) -> str:
        """Get code name."""

    @property
    @abstractmethod
    def value(self) -> KeyType:
        """Get code value."""


class EmissionsCodes(Codes):
    """Error codes issued during processing of dam-related data for estimation
       of GHG emissions.

       The EmissionCode value is assigned to each dam to indicate whether the
       analysis completed successfully or failed."""

    codes: ClassVar[dict] = {
        0: "No Error (complete analysis).",
        1: "Analysis failed at snapping dam to hydroriver.",
        2: "Analysis failed at catchment delineation or catchment parameter "
           "generation.",
        3: "Analysis failed at reservoir delineation or reservoir parameter "
           "generation.",
        4: "Analysis failed at non-inundated catchment delineation or "
           "non-inundated catchment parameter generation.",
        5: "Analysis failed at river delineation or river parameter "
           "generation."}

    @property
    def name(self) -> str:
        """Get code name.

        Raises: CodeNotFoundException."""
        if self._value in self.codes:
            return self.codes[self._value]
        raise CodeNotFoundException(codes=tuple(self.codes.keys()))

    @property
    def value(self):
        """Get code value."""
        return self._value


class EmissionsMissingDataCodes(Codes):
    """Error codes issued when data is unavailable due to either:
       - data being processed.
       - failed delineation/gis processing.
       - data missing from a GIS layer.
    """

    codes: ClassVar[dict] = {
        "UD": "Under Development",
        "NA": "Delineation Failed",
        "NONE": "Delineation Failed",
        "ND": "Missing Data in GIS Layer",
        "NODATA": "Missing Data in GIS Layer"}

    @property
    def name(self) -> str:
        """Get code name."""
        if self._value in self.codes:
            return self.codes[self._value]
        raise CodeNotFoundException(codes=tuple(self.codes.keys()))

    @property
    def value(self):
        """Get code value."""
        return self._value


class EmissionsDamProvenanceCodes(Codes):
    """Codes issued to indicate the method in which dam height is obtained for
    reservoir delineation.
    """

    codes: ClassVar[dict] = {
        0: "User input water level",
        1: "User input dam height",
        2: "Dam height estimated from power capacity with user defined turbine "
           "efficiency",
        3: "Dam height estimated from power capacity with turbine efficiency "
           "85%"}

    @property
    def name(self) -> str:
        if self._value in self.codes:
            return self.codes[self._value]
        return ""

    @property
    def value(self):
        return self._value


if __name__ == "__main__":
    ...
