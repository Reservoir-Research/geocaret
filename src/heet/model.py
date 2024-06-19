""" """
from abc import ABC, abstractmethod
from heet.earth_engine import EarthEngine


class Model(ABC):
    """ """

    @abstractmethod
    def load_inputs(self) -> None:
        """ """

    @abstractmethod
    def compute(self) -> None:
        """ """

    @abstractmethod
    def save_outputs(self) -> None:
        """ """


class EEModel(Model):
    """Model implementing the calculations on Google's servers using the
       Google's Earth Engine API."""

    def __init__(self) -> None:
        # Initialize the Engine
        self.earth_engine = EarthEngine()
        # Initialize Earth Engine
        self.earth_engine.init()

    def load_inputs(self) -> None:
        """ """
        print(f"Saving inputs for the {EEModel.__name__} model.")

    def compute(self) -> None:
        """ """
        print(f"Computing the {EEModel.__name__} model.")

    def save_outputs(self) -> None:
        """ """
        print(f"Saving outputs from the {EEModel.__name__} model.")


if __name__ == '__main__':
    m1 = EEModel()
    m1.compute()
