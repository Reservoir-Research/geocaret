""" """
from abc import ABC, abstractmethod
from typing import Optional, List, Any, Type
from heet.profiles.profile_output import ProfileOutput
from heet.parameters.parameters import Parameter
import heet.log_setup
from heet.utils import get_package_file, read_config, set_logging_level

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)
logger_config: dict = read_config(
    get_package_file('./config/logging_levels.yaml'))
set_logging_level(
    logger=logger, level=logger_config['profiles']['base_classes'])


class Profile(ABC):
    """ """
    def __init__(
            self,
            gis_object: Any,
            parameters: Optional[List[Parameter]] = None,
            unique_parameters: bool = True) -> None:
        """ """
        self.gis_object = gis_object
        self.parameters: List[Parameter] = []
        if parameters is not None:
            for parameter in parameters:
                self.add_parameter(parameter=parameter,
                                   unique=unique_parameters)

    @staticmethod
    def remove_all_occurrences(items: List[Any], item: Any) -> List[Any]:
        while item in items:
            items.remove(item)
        return items

    @property
    def parameter_names(self) -> List[str]:
        return [parameter.name for parameter in self.parameters]

    def add_parameter(
            self, parameter: Parameter, unique: bool = True) -> None:
        """Add parameter to the list of parameters. If unique flag is true
        duplicate parameters will not be added."""
        if parameter in self.parameters:
            logger.info("Parameter %s already exists.", parameter.name)
            if unique:
                logger.info("Parameter skipped.")
            else:
                logger.info("Adding parameter duplicate.")
                self.parameters.append(parameter)
            return None
        if parameter.name in self.parameter_names:
            logger.info("Parameter name %s already exists.", parameter.name)
            if unique:
                logger.info("Parameter skipped.")
            else:
                logger.info("Adding parameter duplicate.")
                self.parameters.append(parameter)
            return None
        self.parameters.append(parameter)
        return None

    @abstractmethod
    def populate(
            self,
            properties: List[str],
            parameter_names: List[str]) -> ProfileOutput:
        """Fills the profile with calculated values."""


if __name__ == '__main__':
    """ """
    test_config = read_config(get_package_file('./profiles/test.yaml'))
    print(test_config)
