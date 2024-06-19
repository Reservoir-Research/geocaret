"""Class for outputting progress in terminal using Yaspin Spinner."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any
import sys
import pathlib
from yaspin import yaspin
from yaspin.spinners import Spinners

import heet.log_setup
from heet.utils import get_package_file, read_config
from heet.io.renderer import JinjaRenderer
from heet.io.printers import (
    GenericPrinter,
    YaspinPrinter,
    ColorPrinter,
    FigletPrinter)
from heet.io.messages import Message

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)

# Emission terminal templates folder
EMISSION_TERMINAL_TEMPLATES = get_package_file(
    "./templates/terminal/emissions")

EMISSION_TERMINAL_TEMPLATE_CONFIG = EMISSION_TERMINAL_TEMPLATES.joinpath(
    'templates_config.yaml')

# Load configuration file
APP_CONFIG: dict = read_config(get_package_file(
    "./config/emissions/general.yaml"))

# Emission terminal printers
EMISSIONS_APP_PRINTERS = [
    YaspinPrinter(yaspin(Spinners.line, text="Test Text", color="yellow")),
    ColorPrinter(color=APP_CONFIG['printers']['font_color']),
    FigletPrinter(color=APP_CONFIG['printers']['figlet_color'])]


class View:
    """ """
    @abstractmethod
    def out(self, name: str, **data) -> None:
        """ """


class Terminal(View):
    """Handler for outputting software messages via Console/Terminal."""

    # Default message set (empty)
    default_msgs: Dict[str, Dict[str, Any]] = {}

    def __init__(
            self,
            renderer: JinjaRenderer,
            printers: Optional[Dict[str, GenericPrinter]] = None):
        self.renderer = renderer
        if printers is None:
            self._printers = {}
        else:
            self._printers = printers
        self._messages = self.default_msgs

    def print(message: Message, printer: GenericPrinter) -> None:
        """Prints message object using a supplied printer."""

    def add_printer(self, printer: GenericPrinter,
                    overwrite: bool = True) -> None:
        """Adds printer implementing GenericPrinter interface to the
           dictionary of supported printers."""
        if overwrite or printer.name not in self._printers:
            self._printers[printer.name] = printer

    def remove_printer(self, printer: GenericPrinter) -> None:
        """Remove printer from the dictionary of supported printers."""
        try:
            self._printers.pop(printer.name)
        except KeyError:
            pass

    @property
    def printers(self) -> List[str]:
        """Return the list of available printer names."""
        return list(self._printers.keys())

    def add_message(self, name: str, template_file: str,
                    variables: List[str],
                    printer: GenericPrinter) -> None:
        """Add message to the dictionary of handled messages."""
        message = {name: {'template': template_file,
                          'variables': list(variables),
                          'printer': GenericPrinter}}
        if bool(self._messages):
            self._messages.update(message)
        else:
            self._messages = message

    def add_messages_from_config(self, file_name: pathlib.Path) -> None:
        """Read YAML file with message structure and read all the messages
           into the messages attribute from the file."""
        messages = read_config(file_name)
        for message, message_data in messages.items():
            if message not in self._messages:
                self._messages[message] = message_data

    def remove_message(self, name: str) -> None:
        """Remove message from the dictionary of supported messages."""
        self._messages.pop(name, None)

    @property
    def messages(self) -> List[str]:
        """Return the list of available message names (ids)."""
        return list(self._messages.keys())

    def required_variables(self, message: str) -> Optional[List[str]]:
        """Return a list of required variables for a given message name."""
        try:
            required_vars = self._messages[message]['variables']
        except KeyError:
            required_vars = None
        return required_vars

    def out(self, name: str, **data) -> None:
        """Prints message of type name to console/terminal."""
        # Retrieve the message dictionary
        try:
            message = self._messages[name]
        except KeyError:
            return None
        # Render the message
        template_file = message['template']
        rendered_text = self.renderer.render_template(
            template_file=template_file, **data).split_lines()
        template_printer = message['printer']
        try:
            printer = self._printers[template_printer]
        except KeyError:
            return None
        # Output the mesage with the dedicated printer
        for line in rendered_text:
            printer.text_out(line)


class EmissionsTerminal(Terminal):
    """Terminal functionality specific to GHG emission applications."""
    # Default messages
    default_msgs = Terminal.default_msgs.copy()

    def __init__(
            self,
            printers: Optional[Dict[str, GenericPrinter]] = None):
        renderer = JinjaRenderer(
            template_folder=EMISSION_TERMINAL_TEMPLATES)
        super().__init__(renderer, printers)
        # Add messages specific to Emission calculation applications
        self.add_messages_from_config(EMISSION_TERMINAL_TEMPLATE_CONFIG)
        # Add printers to support the addded messages
        for printer in EMISSIONS_APP_PRINTERS:
            self.add_printer(printer)


if __name__ == "__main__":
    et = EmissionsTerminal()
    message_name = 'err_folder'
    print("Required variables: ")
    print(et.required_variables(message=message_name))
    print("Outputting the message.")
    et.out(
        name='err_folder',
        error_message="Ooops. Wrong folder",
        folder_path="./outputs",
        thanks_message="Thank you for checking out this code.")
