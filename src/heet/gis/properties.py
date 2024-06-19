"""Properties of gis object"""
from typing import List, Callable, Any, Optional


class Property:
    """ """
    def __init__(self, raw_value: Any, unit: str, formatted_value: str) -> None:
        """ """
        self.raw_value = raw_value
        self.unit = unit
        self.formatted_value = formatted_value

    def format_raw_value(self, formatter: Callable[[Any], Any]) -> Any:
        self.formatted_value = formatter(self.raw_value)


class Properties:
    """ """
    def __init__(self, properties: Optional[List[Property]] = None) -> None:
        self.properties: List[Property] = []
        if properties is not None:
            self.properties.extend(properties)

    def add_property(self, property_item: Property):
        """ """
        self.properties.append(property_item)
