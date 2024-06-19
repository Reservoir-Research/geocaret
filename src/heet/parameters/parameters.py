"""Template for an abstract Parameter class and containers (FormattedOutput
and RawOutput) for storage of outputs/results of calculation of concrete
Parameter implementations."""
from __future__ import annotations
from _collections_abc import list_iterator
from functools import wraps
from abc import ABC, abstractmethod
from typing import Optional, List, Callable, Dict, Union, Any, Generator
from typing import Sized
import ee
import heet.log_setup
from heet.utils import get_package_file, read_config, set_logging_level

# Create type aliases
FormattedOutputValue = Union[ee.String, Dict[str, ee.String]]
RawOutputValue = Union[ee.Number, ee.ComputedObject, ee.List]
OutputFormatter = Callable[['RawOutput'], FormattedOutputValue]

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)
logger_config: dict = read_config(
    get_package_file('./config/logging_levels.yaml'))
set_logging_level(
    logger=logger, level=logger_config['parameters']['base_classes'])


def inplace(attribute: str) -> Callable:
    """Decorator for methods that allows the method to alter
    the value of the attribute of the object in which it resides."""
    def decorator_inplace(method):
        @wraps(method)
        def wrapper_inplace(self, *args, **kwargs):
            out = method(self, *args, **kwargs)
            setattr(self, attribute, out)
            return out
        return wrapper_inplace
    return decorator_inplace


class FormattedOutput(Sized):
    """Formatted parameter output"""

    def __init__(self, var_name: str, unit: str,
                 value: FormattedOutputValue) -> None:
        """ """
        self.var_name = var_name
        self.unit = unit
        self.value = value

    def __len__(self) -> int:
        """ Find the output size """
        try:
            return len(self.value)
        except TypeError:
            return 0

    @staticmethod
    def var_name_checker(var_name: str) -> str:
        """Check variable name and update if the variable does not conform
        to naming convention. Return a modified variable name, if different
        from original."""
        # remove spaces from both ends fo variable name, replace inner spaces
        # with underscores. remove trailing undescores if present
        new_var_name = var_name.strip().replace(" ", "_").strip('_')
        if new_var_name != var_name:
            logger.debug(
                "The variable name `%s` does not follow naming convenion.",
                var_name)
            logger.debug(
                "Proposed variable name after changes: %s.", new_var_name)
        return new_var_name

    def validate_variables(self, update: bool = True) -> FormattedOutputValue:
        """ """
        value_copy = self.value.copy()
        validated_value: FormattedOutputValue = {}
        for var_name, var_value in value_copy.copy().items():
            new_var_name = self.var_name_checker(var_name)
            if new_var_name != var_name:
                var_name = new_var_name
            validated_value[var_name] = var_value
        if update is True:
            self.value = validated_value
        return validated_value

    @property
    def variables(self) -> List[str]:
        """ """
        return list(self.value.keys())


class RawOutput(Sized):
    """Raw parameter output value"""

    def __init__(
            self, var_name: str, unit: str, value: RawOutputValue) -> None:
        """ """
        self.var_name = var_name
        self.unit = unit
        self.value = value

    def __len__(self) -> int:
        """ Find the output size """
        try:
            return self.value.length().getInfo()
        except AttributeError:
            # Probably a number
            return 1

    def format(self, formatter: OutputFormatter) -> FormattedOutputValue:
        """Apply formatter to format raw output into formattter output"""
        return formatter(self)

    def name_rollout(self, start_index: int = 0) -> List[str]:
        """Creates a list of variables names representing single variables in
        the variable vector of a given length"""
        if len(self) <= 1:
            var_names = [self.var_name]
        else:
            var_names = [
                '_'.join([self.var_name, str(index+start_index)])
                for index in range(len(self))]
        return var_names


class Parameter(ABC):
    """ """
    def __init__(
            self, base_data: ee.FeatureCollection, name: str,
            variables: List[str], units: List[str],
            formatters: Optional[List[OutputFormatter]] = None) -> None:
        self.base_data = base_data
        self.name = name
        # Single parameter can output more than one values
        self.variables = variables
        self.units = units
        self.formatters = formatters
        self._raw_outputs: Optional[List[RawOutput]] = None
        self._formatted_outputs: Optional[List[FormattedOutput]] = None
        # Perform the input value check
        self._initialisation_check()

    def __len__(self) -> int:
        """ Find the parameter size via the length of variables """
        return len(self.variables)

    def _initialisation_check(self) -> None:
        """ """
        # Check if output list lengths are equal if both are provided,
        # Find list length if only one provided
        # Otherwise length is None
        def check_length(
                data: List[List[Any]],
                err_msg: str) -> int:
            """Check if all lists are of the same legth. If True, return
            list length, otherwise raise an error."""
            data_iterator: list_iterator = iter(data)
            the_len = len(next(data_iterator))
            if not all(len(item) == the_len for item in data_iterator):
                raise ValueError(err_msg)
            return the_len
        check_length(
            data=[self.variables, self.units],
            err_msg="List of variables and units of unequal lenghts.")

    @property
    def raw_outputs(self) -> Generator[Optional[RawOutput], None, None]:
        """ """
        if self._raw_outputs is None:
            yield None
        else:
            for output in self._raw_outputs:
                yield output

    @property
    def formatted_outputs(self) -> \
            Generator[Optional[FormattedOutput], None, None]:
        """ """
        if self._formatted_outputs is None:
            yield None
        else:
            for output in self._formatted_outputs:
                yield output

    def format(self, **kwargs: Any) -> None:
        """Conversion of a list of raw outputs to the list of formatted
        outputs used e.g. for presentation."""
        if self.formatters is None:
            logger.warning(
                "No formatters found. Outputs could not be formatted.")
            return None
        if self._raw_outputs is None:
            logger.debug("No outputs present, nothing to format.")
            return None
        if len(self.formatters) > 1:
            # If more than one formatter provided, we need to have
            # one formatter per raw_output in the list of outputs
            assert len(self.formatters) == len(self._raw_outputs)
            formatted_values = [formatter_fun(raw_output, **kwargs) for
                                formatter_fun, raw_output in
                                zip(self.formatters, self._raw_outputs)]
        else:
            # If one formatter provided, use a single (first) formatter for all
            # outputs in self._raw_outputs
            formatted_values = [self.formatters[0](raw_output, **kwargs) for
                                raw_output in self._raw_outputs]
        self._formatted_outputs = [FormattedOutput(
            var_name=raw_output.var_name,
            unit=raw_output.unit,
            value={raw_output.var_name: formatted_value}) for
            raw_output, formatted_value in
            zip(self._raw_outputs, formatted_values)]
        return None

    @abstractmethod
    def calculate(self, **kwargs: Any) -> Parameter:
        """Calculate the value of the parameter."""
        raise NotImplementedError("Method `calculate` not implemented.")


if __name__ == '__main__':
    """ """

    def test_formatter(output: RawOutput) -> str:
        out = output.value.upper()
        print(out)
        return out

    class TestParameter(Parameter):
        """ """
        def calculate(self) -> None:
            output = RawOutput(var_name="", unit="", value="test_output")
            self._raw_outputs = [output]
            self.format()

        def format(self):
            for output in self._raw_outputs:
                self.formatter(output)

    out1 = RawOutput(var_name='output1', unit="unknown", value=666)
    par1 = TestParameter(
            base_data="",
            name="Test parameter",
            variables=['ll', 'x'],
            units=['mm', 'dd'],
            formatters=[test_formatter])
    par1.calculate()
