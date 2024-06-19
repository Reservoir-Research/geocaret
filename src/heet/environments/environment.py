""" """
from abc import ABC, abstractmethod
from functools import partial
from typing import Optional
import time
from yaspin import yaspin
from yaspin.core import Yaspin
from yaspin.spinners import Spinners
from yaspin.base_spinner import Spinner

# Default spinner attributes
DEFAULT_SPINNER = Spinners.line
DEFAULT_SPINNER_COLOR = "yellow"


class Environment(ABC):
    """Interface for execution environments that act as wrappers around
    objects performing e.g. calculations or other time-consuming taks.
    Environment can be implemented either as a context manager or a decorator
    decorators not implemented yet.
    """

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, ex_type, ex_value, ex_traceback):
        pass

    @abstractmethod
    def __call__(self):
        pass


class SpinnerEnvironment(Environment):
    """Environment used to wrap objects with the spinner object."""
    def __init__(self, spinner: Yaspin) -> None:
        self._spinner = spinner

    @classmethod
    def from_scratch(
            cls,
            text: str = "",
            spinner_type: Spinner = DEFAULT_SPINNER,
            color: str = DEFAULT_SPINNER_COLOR):
        return cls(spinner=yaspin(spinner_type, text=text, color=color))

    @property
    def spinner(self) -> Yaspin:
        return self._spinner

    @spinner.setter
    def spinner(self, spinner: Yaspin) -> None:
        self._spinner = spinner

    def __enter__(self):
        self.spinner.start()
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        self.spinner.stop()

    def __call__(self) -> None:
        pass


if __name__ == '__main__':

    class TestClass:
        def __init__(self, sleepy_time: int,
                     environment: Optional[Environment] = None) -> None:
            self.executable = partial(time.sleep, sleepy_time)
            self.environment = environment

        def run(self) -> None:
            if self.environment is not None:
                with self.environment:
                    self.executable()
            else:
                self.executable()

    env1 = SpinnerEnvironment.from_scratch(
        text="Spinning sleepy function")
    env1 = SpinnerEnvironment(
        spinner=yaspin(Spinners.clock, text='Clock spinner', color='blue'))
    sleepy_class1 = TestClass(sleepy_time=2, environment=env1)
    env2 = SpinnerEnvironment(
        spinner=yaspin(Spinners.clock, text='Clock spinner', color='red'))
    sleepy_class2 = TestClass(sleepy_time=2, environment=env2)
    sleepy_class3 = TestClass(sleepy_time=2, environment=None)
    sleepy_class1.run()
    sleepy_class2.run()
    sleepy_class3.run()
