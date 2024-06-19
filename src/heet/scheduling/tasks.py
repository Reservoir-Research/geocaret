""" """
from enum import Enum, auto
from abc import ABC, abstractmethod
from functools import partial
from typing import Callable, Any, Optional
from heet.events.event_handler import EventHandler


class TaskStatus(Enum):
    """Define status of execution of each task"""
    NOINIT = auto()
    INITIALIZED = auto()
    RUNNING = auto()
    PAUSED = auto()
    INTERRUPTED = auto()
    FAILED_RUN = auto()
    SUCCESS_RUN = auto()


class TaskLevel(Enum):
    """Define the level of importance of the task.
        * NOTCRITICAL: the task can fail and the next step in the pipeline
            can be executed.
        * CRITICAL: if the task fails, then the rest of the steps in the
            pipeline cannot execute.
        * MUSTFAIL: the next steps in the pipeline will be executed ONLY IF
            this task FAILS.
    """
    NOTCRITICAL = auto()
    CRITICAL = auto()
    MUSTFAIL = auto()


class ExecStatus(Enum):
    UNDEFINED = auto()
    FAIL = auto()
    SUCCESS = auto()


class Executable:
    """Class for creating an pre-initialized executable for delayed execution.
    without arguments."""
    def __init__(self, fun: Callable, fail_out: Any, success_out: Any,
                 *args, **kwargs):
        """Partially initialize the function with arguments."""
        self.exec = partial(fun, *args, **kwargs)
        self.fail_out = fail_out
        self.success_out = success_out
        self.exec_status = ExecStatus.UNDEFINED

    def _success(self) -> bool:
        self.exec_status = ExecStatus.SUCCESS

    def _fail(self) -> bool:
        self._exec_status = ExecStatus.FAIL

    def run(self) -> Any:
        """Execute the function."""
        output = self.exec()
        if output == self.fail_out:
            self._fail()
        elif output == self.success_out:
            self._success()
        return output


class Task(ABC):
    """ """
    def __init__(
            self,
            model: Executable,
            event_handler: Optional[EventHandler] = None,
            task_level: TaskLevel = TaskLevel.NOTCRITICAL):
        self._status = TaskStatus.NOINIT
        self.task_level = task_level
        self.events = event_handler

    @property
    def status(self) -> TaskStatus:
        return self._status

    def supports_events(self) -> bool:
        return isinstance(self.events, EventHandler)

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def on_success(self) -> None:
        pass

    @abstractmethod
    def on_fail(self) -> None:
        pass

    @abstractmethod
    def kill(self) -> None:
        pass


class LocalTask(Task):
    """Generic tasks performed on the local machine.

    Examples include:
        * Local processing of input/output data.
        * Running local GIS processing calculations.
        * Outputting message to Terminal/Console.
    """


class WebTask(Task):
    """Tasks requiring sustained internet connection.

    Requires implementation of internet connection monitoring.
    """


class GoogleTask(WebTask):
    """Tasks requiring sustained internet connection and authentication with
    Google's web servers.
    """
