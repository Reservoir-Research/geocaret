"""Collection of abstract classes for implementation of event handling."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Hashable, List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto


class EventType(Enum):
    """Types of events that are fired/posted and supported by the
    application"""
    GENERIC = auto()
    INFO_MESSAGE = auto()
    WARNING_MESSAGE = auto()
    ERROR_MESSAGE = auto()
    STATUS_UPDATE = auto()
    DATA_EXPORT = auto()
    DATA_IMPORT = auto()


@dataclass
class EventID(Hashable):
    """Unique identifier of an event."""
    name: str

    def __eq__(self, other: object) -> bool:
        """ """
        if not isinstance(other, EventID):
            return NotImplemented
        return self.name == other.name

    def __lt__(self, other: object):
        if not isinstance(other, EventID):
            return NotImplemented
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)


@dataclass
class Event:
    """Event wrapper class
    Attributes:
        id: Unique event identifier
        type: Event type used to filter events supported by listeners
        data: Data dictionary used to ship data with events"""
    id: EventID
    type: EventType = field(default=EventType.GENERIC)
    data: Dict[str, Any] = field(default_factory=dict)


class EventListener(ABC):
    """
    The EventListener (observer) interface.
    Attributes:
        _event_types: Supported event types by the event listener
    """

    def __init__(
            self,
            event_types: Optional[List[EventType]] = None) -> None:
        if event_types is None:
            self._event_types = []
        else:
            self._event_types = event_types

    def add_event_type(self, event_type: EventType) -> None:
        """Add event type to the list of supported event types"""
        if event_type not in self._event_types:
            self._event_types.append(event_type)

    def remove_event_type(self, event_type: EventType) -> None:
        """Remove event type from the list of supported events"""
        try:
            self._event_types.remove(event_type)
        except ValueError:
            pass

    def _supported(self, event: Event) -> bool:
        """Check if the event is suppored by the EventLister"""
        if self._event_types is None:
            return True
        return event.type in self._event_types

    @abstractmethod
    def update(self, event: Event, *args, **kwargs) -> None:
        """
        Receive update from subject.
        """


class EventHandler(ABC):
    """Template for the application event handlers"""

    @abstractmethod
    def subscribe(
            self, event: Event, listener: EventListener) -> None:
        """ """

    @abstractmethod
    def unsubscribe(
            self, event: Event, listener: EventListener) -> None:
        """ """

    @abstractmethod
    def post(self, event: Event, *args, **kwargs) -> None:
        """ """
