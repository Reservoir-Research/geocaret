""" """
from abc import ABC, abstractmethod
import pandas as pd


class Data(ABC):
    """ """
    @property
    @abstractmethod
    def data(self) -> pd.DataFrame:
        """ """
