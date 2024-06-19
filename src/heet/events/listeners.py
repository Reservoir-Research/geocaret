"""Application's- event listeners"""
from typing import List, Optional
from heet.terminal import EmissionsTerminal
from heet.events.abstract import EventListener, Event, EventType


class EmissionsTerminalEventListener(EventListener):
    """Event listener outputting messages to terminal"""
    def __init__(
            self, terminal: EmissionsTerminal,
            event_types: Optional[List[EventType]] = None) -> None:
        super().__init__(event_types)
        self.terminal = terminal

    def update(self, event: Event, *args, **kwargs) -> None:
        """
        Trigger action based on the received event.
        """
        # Do not update if event type not in supported types and supported
        # list is not empty
        if event.type not in self._event_types and bool(self._event_types):
            return None
        name = kwargs.pop('name', '')
        self.terminal.output_msg(name=name, **kwargs)
