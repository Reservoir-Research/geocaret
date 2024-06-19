"""Supported event handler classes:
    1. Internal Event Handler - simple event handler made for the purpose
        of this application.
    2. PyPi Event Handler - adapter class using an external event handler
        at https://pypi.org/project/eventhandler/
"""
from typing import Optional, Callable, Dict, List
# External Event Handler
import eventhandler as ext_ehandler
from heet.events.abstract import EventListener, EventHandler, Event, EventID


class InternalEventHandler(EventHandler):
    """Event Handler / Observer that manages listener/subscriber subscriptions
       and posts events."""

    def __init__(self, name: Optional[str] = None) -> None:
        """ """
        self._listeners: Dict[EventID, List[EventListener]] = {}
        if name is None:
            self.name = "No Name"
        else:
            self.name = name

    def subscribe(self, event: Event, listener: EventListener) -> None:
        """Link event listener to event identifier."""
        if event.id not in self._listeners:
            self._listeners[event.id] = []
        self._listeners[event.id].append(listener)

    def unsubscribe(self, event: Event, listener: EventListener) -> None:
        """Remove the link between event listener and the event ID"""
        if event.id in self._listeners:
            try:
                self._listeners[event.id].remove(listener)
            except ValueError:
                pass

    def post(self, event: Event, *args, **kwargs) -> None:
        """
        Notify all observers (listeners) about the event.
        """
        try:
            for listener in self._listeners[event.id]:
                listener.update(event, *args, **kwargs)
        except KeyError:
            pass


class PyPiEventHandler(EventHandler):
    """Event handler for the eventhandler libary
      - PyPi: https://pypi.org/project/eventhandler/
      - GITHUB: https://github.com/davidvicenteranz/eventhandler
      - loading: from eventhandler import EventHandler
    The library performs event handling based on callback functions, thus
    some modifications to the way EventListeners are handled were necessary.
    """
    adaptee = ext_ehandler.EventHandler()

    def __init__(self, name: Optional[str] = None) -> None:
        """ """
        if name is None:
            self.name = "No Name"
        else:
            self.name = name

    def __link(self, callback: Callable, event_name: str) -> None:
        """Link a callback to be executed on fired event..
        Args:
            callback (Callable): function to link.
            event_name (str): The event that will trigger the callback execution.
        """
        self.adaptee.link(callback, event_name)

    def __unlink(self, callback: Callable, event_name: str) -> None:
        """Unlink a callback execution from especific event.
        Args:
            callback (Callable): function to link.
            event_name (str): The event that will trigger the callback execution.
        """
        self.adaptee.unlink(callback, event_name)

    def __fire(self, event_name: str, *args, **kwargs) -> None:
        """Triggers all callbacks executions linked to given event.
        Args:
            event_name (str): Event to trigger.
            *args: Arguments to be passed to callback functions execution.
            *kwargs: Keyword arguments to be passed to callback functions
                execution.
        """
        self.adaptee.fire(event_name, *args, **kwargs)

    def subscribe(self, event: Event, listener: EventListener) -> None:
        """Link event listener to event. Uses partial functions for partial
            initialisation of callables without *args and *kwargs."""
        event_name: str = event.id.name
        self.adaptee.register_event(event_name)
        listener_callback = listener.update
        self.__link(callback=listener_callback, event_name=event_name)

    def unsubscribe(self, event: Event, listener: EventListener) -> None:
        """Remove the link between event listener and the event ID"""
        event_name: str = event.id.name
        listener_callback = listener.update
        self.__unlink(callback=listener_callback, event_name=event_name)

    def post(self, event: Event, *args, **kwargs) -> None:
        """
        Notify registered observers (listeners) about the event.
        """
        # Merge data stored in the event into kwargs
        kwargs.update(event.data)
        self.__fire(event.id.name, event, *args, **kwargs)
