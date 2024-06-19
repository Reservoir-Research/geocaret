%% Event handling classes
classDiagram
    class Logic {
        +events: EventHandler
    }
    class EventHandler {
        <<abstract>>
        +subscribe(event: Event, listener: EventListener)*
        +unsubscribe(event: Event, listener: EventListener)*
        +post(event: Event, data)*
    }
    class InternalEventHandler {
        -listeners: Event -> EventListener[]
        +subscribe(event: Event, listener: EventListener)
        +unsubscribe(event: Event, listener: EventListener)
        +post(event: Event, data)
    }
    class PyPiEventHandler {
        -adaptee: ExtEventHandler
        +subscribe(event: Event, listener: EventListener)
        +unsubscribe(event: Event, listener: EventListener)
        +post(event: Event, data)
    }
    class EventListener{
        <<abstract>>
        -event_types: EventType[]
        -supported(event: Event)
        +add_event_type(event_type: EventType)
        +remove_event_type(event_type: EventType)
        +update(event: Event, data)*
    }
    class EventListener_1_n{
        +update(event: Event, data)
    }
    class Event {
        id: EventID
        type: EventType
        data: dict
    }
    class EventID {
        name: str
    }
    class EventType {
        +GENERIC
        +INFO_MESSAGE
        +WARNING_MESSAGE
        +ERROR_MESSAGE
        +STATUS_UPDATE
        +DATA_EXPORT
        +DATA_IMPORT
    }
    Logic o-- EventHandler
    EventHandler o-- EventListener
    EventHandler --> Event
    EventListener <|-- EventListener_1_n
    EventHandler <|-- InternalEventHandler
    EventHandler <|-- PyPiEventHandler
    EventListener o-- EventType
    Event *-- EventID
    Event *-- EventType
    EventListener --> Event
