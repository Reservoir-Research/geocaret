"""Module containig the pipeline architecture component for running tasks
   in series."""
from typing import List
from abc import ABC, abstractmethod
from heet.tasks import PipelineTask


class PipelineInterface(ABC):
    """ """

    @abstractmethod
    def register(self, tasks: List[PipelineTask]) -> None:
        """ """

    @abstractmethod
    def add_task(self, task: PipelineTask) -> None:
        """ """

    @abstractmethod
    def remove_task(self, task: PipelineTask) -> None:
        """ """

    @abstractmethod
    def execute(self) -> None:
        """Execute pipeline."""

    @abstractmethod
    def circuit_breaker(self) -> None:
        """Break the pipeline if one of the steps fail."""


class Pipeline(PipelineInterface):
    """ """
    def __init__(self) -> None:
        """ """
        self.tasks: List[PipelineTask] = []
        self.current_position: int = 0

    def register(self, tasks: List[PipelineTask]) -> None:
        """ """
        for task in tasks:
            self.add_task(task)

    def add_task(self, task: PipelineTask) -> None:
        """ """
        self.tasks.append(task)

    def remove_task(self, task: PipelineTask) -> None:
        """ """

    def execute(self) -> None:
        """Execute pipeline."""

    def circuit_breaker(self) -> None:
        """Break the pipeline if one of the steps fail."""


if __name__ == '__main__':
    pipeline = Pipeline()
    print(pipeline.current_position)
