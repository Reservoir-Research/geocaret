"""Module providing functionality for creating and deleting Googles EE jobs.

"""
import re
import sys
from abc import ABC, abstractmethod, abstractproperty
from enum import Enum, auto
from typing import Tuple, List
from datetime import datetime
from pathlib import Path
import ee
from heet.web.earth_engine import EarthEngine
from heet.tasks import GenericTask


class JobStatus(Enum):
    """Define status of execution of each job"""
    SUCCEEDED = auto()
    CANCELLED = auto()
    FAILED = auto()


class Job(ABC):
    """ """
    @abstractmethod
    def run(self) -> None:
        pass

    @abstractproperty
    def name(self) -> str:
        pass


class GenericJob(Job):
    """Class representing a job (pipeline) of tasks performed by the
    application.

    A job can include several tasks.
    """

    finished_states = ['SUCCEEDED', 'CANCELLED', 'FAILED']
    task_pattern = r"^XHEET-X\d\d\d-\d+"  # Precede the string with r, if gives
    # error, remove the r prefix.

    def __init__(self, name: str):
        self.name: str = name
        self._tasks: List[GenericTask] = []

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        # Always make sure that the name is in upper case (convention)
        name = name.upper()
        # Validate jobname before setting it as the object attribute
        pattern = re.compile("^[a-zA-Z0-9\\-]{3,10}$")
        if not bool(re.search(pattern, name)):
            sys.exit(
                f"[ERROR] Application encountered an error and could not start."
                f"\n[ERROR] Job name {name} must be 3-10 characters long and only "
                f"contain: A-Z, 0-9 or - ")
        self._name = name

    @property
    def tasks(self):
        return self._tasks

    def run(self) -> None:
        print('running job...')

    @classmethod
    def running_tasks(cls) -> list:
        """
        Check if there are any currently running tasks whose descriptions match
        the application task pattern.
        """
        # Get the list of all tasks
        tasks = ee.data.listOperations()
        # Find the tasks that are running and matching the pattern
        running_tasks = [
            task for task in tasks if (
                (task['metadata']['state'] not in cls.finished_states) and
                re.match(cls.task_pattern, task['metadata']['description']))]
        return running_tasks

    @classmethod
    def existing_tasks_running(cls) -> bool:
        """
        Check if there are any currently running tasks whose descriptions match
        the application task pattern.
        """
        return bool(len(cls.running_tasks()) > 0)

    @classmethod
    def kill_all_running_tasks(cls) -> None:
        """ """
        for job in cls.running_tasks():
            ee.data.cancelOperation(job['name'])

    def output_asset_folder(self) -> Tuple[str, Path]:
        """Produce a name for the asset folder where calculation results
        are stored locally."""
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        time = now.strftime("%H%M")
        folder_name = self.name + "_" + year + month + day + "-" + time
        return folder_name, Path("outputs", folder_name)


if __name__ == '__main__':
    engine1 = EarthEngine()
    engine1.init()
    job = Job(name="job1")
    print(job.name)
    task_list = ee.data.listOperations()
    print(Job.existing_tasks_running())
