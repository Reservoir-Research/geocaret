""" """
from typing import Callable, Any, Callable
from enum import Enum, auto
from abc import ABC, abstractmethod
import ee
from polling2 import poll_decorator
import heet.log_setup
from heet.assets import EmissionAssets

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)


class TaskStatus(Enum):
    """Define status of execution of each task"""
    NOINIT = auto()
    INITIALIZED = auto()
    RUNNING = auto()
    PAUSED = auto()
    INTERRUPTED = auto()
    FAILED_RUN = auto()
    SUCCESS_RUN = auto()


class TaskType(Enum):
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


class Engine:
    pass


#Wrap around spinner?
# Tasks should post events
class TaskMockup:
    """ What should each task have """
    executable: Callable
    args: Any
    kwargs: Any
    status: TaskStatus
    on_success: Callable
    on_fail: Callable

    def run(self) -> None:
        pass

    # Each task has the following steps:
    # 1. Calculate
    # 2. Output


class GenericTask(ABC):
    """ """
    def __init__(self, task_type: TaskType):
        self._status = TaskStatus.NOINIT
        self.task_type = task_type

    @property
    def status(self) -> TaskStatus:
        """Return current status of the task."""
        return self._status

    @abstractmethod
    def init(self, **kwargs: Any) -> None:
        """Initialize task with data and methods."""

    @abstractmethod
    def start(self) -> None:
        """Start the task"""

    @abstractmethod
    def pause(self) -> None:
        """Pause the task."""

    @abstractmethod
    def resume(self) -> None:
        """Resume the task."""

    @abstractmethod
    def stop(self) -> None:
        """Stop the task"""

    @abstractmethod
    def output(self) -> None:
        """Output results."""


class PipelineTask(ABC):
    """ """


class LocalTask(GenericTask):
    """Class for carrying out tasks on the local machine.

    Examples include:
        * Local processing of input/output data.
        * Running local GIS processing calculations.
        * Outputting message to Terminal/Console.
    """
    def __init__(self, task_type: TaskType, engine: Engine):
        super().__init__(task_type)
        self.engine = engine

    def init(self, **kwargs: Any) -> None:
        """Initialize task with data and methods."""
        self.status = TaskStatus.INITIALIZED

    def start(self) -> None:
        """Start the task"""
        # Start the task
        if self.status == TaskStatus.INITIALIZED:
            self.status = TaskStatus.RUNNING

    def pause(self) -> None:
        """Pause the task."""
        if self.status == TaskStatus.RUNNING:
            self.status = TaskStatus.PAUSED

    def resume(self) -> None:
        """Resume the task."""
        if self.status == TaskStatus.PAUSED:
            # Resume the task
            self.status = TaskStatus.RUNNING

    def stop(self) -> None:
        """Stop the task"""
        if self.status == TaskStatus.RUNNING:
            self.status = TaskStatus.INTERRUPTED

    def output(self) -> None:
        """Output results."""
        if self.status == TaskStatus.SUCCESS_RUN:
            return self.model.outputs


class InternetTask(GenericTask):
    """ Class for carrying out tasks requiring internet connection.

    Examples include:
        * Uploding to/downloading from external servers.
        * Runnig calculations on external servers, e.g. Google's Earth Engine.
    """

    def __init__(self, task_type: TaskType, engine: Engine):
        super().__init__(task_type)
        self.engine = engine

    def init(self, **kwargs: Any) -> None:
        """Initialize task with data and methods."""

    def start(self) -> None:
        """Start the task"""

    def pause(self) -> None:
        """Pause the task."""

    def resume(self) -> None:
        """Resume the task."""

    def stop(self) -> None:
        """Stop the task"""

    def output(self) -> None:
        """Output results."""


class EETask(InternetTask):
    """Wrapper for Google Earth Engine's task."""
    #  TODO: Specify somehow at the typing hint stage that task object needs to
    #  have a .start() method

    def __init__(self, task_function: Callable, task_config: dict):
        self.task = task_function(**task_config)

    def start(self) -> None:
        """Start the task. Assumes that the task_function object has a start
        method.
        """
        self.task.start()

    def robust_start(self, max_tries: int = 3, time_step: float = 5):
        """
        Uses polling2 functionality to peform multiple attempts of starting the
        task.

        Note: does not seem to work with EarthEngine's tasks as Google Earth
            Engine seems to be taking care of connectivity issues itself. Code
            left in the codebase for other task running applications. Polling
            seems unresponsive for EE tasks because they do not return
            exceptions in case of lack of connectivity nor do they return a
            status, e.g. (True/False).
        """
        @poll_decorator(step=time_step, max_tries=max_tries)
        def robust_task_start():
            """ """
            task_status = False
            try:
                self.start()
                task_status = True
            # Bare exceptions should be avoided but left here as the original
            # code had a bare exception clause.
            except Exception:
                logger.exception(
                    " Attempted task %d times at %d s intervals but failed" +
                    " Possible connectivity issue.  Task skipped", max_tries,
                    time_step)
            return task_status


if __name__ == "__main__":
    e1 = Engine()
    e2 = Engine()
    t1 = LocalTask(task_type=TaskType.CRITICAL, engine=e1)
    t2 = InternetTask(task_type=TaskType.CRITICAL, engine=e2)
    print(t1.status)
    print(t1.engine)
    print(t2.status)
    print(t2.engine)
    exit()
    assets = EmissionAssets()
    asset_id = assets.working_folder + "/" + "user_inputs"
    geo = {
        "type": "Polygon",
        "coordinates":
            [[[-122.085, 37.423],
              [-122.092, 37.424],
              [-122.085, 37.418],
              [-122.085, 37.423]]]
    }
    feature = ee.Feature(ee.Geometry(geo))
    inputs_ftc = ee.FeatureCollection([feature])
    task_configuration = {
        'collection': inputs_ftc,
        'description': "XHEET-X000-0" + " User Inputs",
        'assetId': asset_id}
    # Task callable is a function
    task = Task(
        task_function=ee.batch.Export.table.toAsset,
        task_config=task_configuration)
    input("Press Enter to continue...")
    task.robust_start()
