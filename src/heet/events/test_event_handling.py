""" Use external event handler package """
from __future__ import annotations
from typing import Optional
from heet.events.event_handlers import InternalEventHandler, PyPiEventHandler
from heet.events.abstract import EventListener, EventHandler, Event, EventID


class GISCalculationTask:
    """Simulates some GIS calculation task."""

    def __init__(self, task_name: str):
        """ """
        self.task_name: str = task_name
        self._event_handler: Optional[EventHandler] = None

    @property
    def event_handler(self) -> Optional[EventHandler]:
        return self._event_handler

    @event_handler.setter
    def event_handler(self, event_handler: EventHandler) -> None:
        self._event_handler = event_handler

    def _on_calculation_start(self):
        """ """
        print(f'Task {self.task_name} has started')

    # This callback will be called when onMessage event happens
    @staticmethod
    def _on_calculation_finish(exit_code: int):
        """ """
        print(f'Calculation finished with exit code {exit_code}')

    def calculate(self):
        """Let user (and bots) send a message to the chat room."""
        self._on_calculation_start()
        if self.event_handler is not None:
            self.event_handler.post(Event(EventID('onStart')))
        try:
            print(self.event_handler.events)
        except AttributeError:
            pass
        print('calculation finished')
        exit_code: int = 0
        if self.event_handler is not None:
            self._event_handler.post(
                Event(EventID('onFinish')), exit_code=exit_code)


class EventListener1(EventListener):
    """ """
    @staticmethod
    def congratulate_start():
        """ """
        print("Congratulations for starting the calcs")

    def update(self, _: Event, *args, **kwargs) -> None:
        """ """
        self.congratulate_start()


class EventListener2(EventListener):
    """ """
    @staticmethod
    def congratulate_finish(exit_code):
        """ """
        print(
            f"Congratulations for finishing the calcs with exit code {exit_code}")

    def update(self, _: Event, *args, **kwargs) -> None:
        """ """
        exit_code = kwargs.pop('exit_code', None)
        if exit_code is not None:
            self.congratulate_finish(exit_code)


class Calculator:
    """ """

    def __init__(self, event_handler: EventHandler):
        """ """
        self.listener1 = EventListener1()
        self.listener2 = EventListener2()
        self.task = GISCalculationTask(task_name="Some GIS processing task")
        self.task.event_handler = event_handler
        # Append callbacks to the event handler
        self.task.event_handler.subscribe(
            event=Event(EventID('onStart')), listener=self.listener1)
        self.task.event_handler.subscribe(
            event=Event(EventID('onFinish')), listener=self.listener2)

    def run(self):
        """ """
        self.task.calculate()


if __name__ == '__main__':
    """ Test event handling with two differnet event handlers.
    The results from both calculations should be the same"""
    print("Running mock calculations with two different event handlers.")
    print("Produced outputs should be equal in both cases.")
    event_handler1 = InternalEventHandler()
    event_handler2 = PyPiEventHandler()
    calc1 = Calculator(event_handler=event_handler1)
    calc2 = Calculator(event_handler=event_handler2)
    print("------------------------------------------------------")
    print("Running the calculator with the internal event handler")
    print("------------------------------------------------------")
    calc1.run()
    print("------------------------------------------------------")
    print("Running the calculator with the external event handler")
    print("------------------------------------------------------")
    calc2.run()
