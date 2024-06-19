"""Module with printers used to send output to console.
Implemented in the Template class."""
import sys
from abc import ABC, abstractmethod
from typing import TextIO
from pyfiglet import figlet_format
from termcolor import colored
from yaspin import yaspin
from yaspin.core import Yaspin
from yaspin.spinners import Spinners
from heet.utils import classproperty


class GenericPrinter(ABC):
    """Interface class for supporting objects generating outputs in
    a terminal/console."""

    @classproperty
    def name(cls):
        return cls.__name__

    @abstractmethod
    def text_out(self, text: str) -> None:
        pass


class YaspinPrinter(GenericPrinter):
    """Generate outputs to terminal using Yaspin spinner objects."""
    def __init__(self, spinner: Yaspin) -> None:
        self._spinner = spinner

    def text_out(self, text: str) -> None:
        """Text output function."""
        self._spinner.write(text)

    def success_out(self, color: str = "cyan") -> None:
        """Spinner success message/icon"""
        self._spinner.color = color
        self._spinner.ok("✅")

    def fail_out(self, color: str = "red") -> None:
        """Spinner fail message/icon"""
        self._spinner.color = color
        self._spinner.fail("💥")


class ColorPrinter(GenericPrinter):
    """Generate outputs to terminal using the `termcolor` package with print.
    """
    def __init__(self, color: str = "blue", file: TextIO = sys.stdout):
        self.color = color
        self.file = file

    def text_out(self, text: str) -> None:
        """Coloured terminal print function."""
        print(colored(text, self.color), file=self.file)


class FigletPrinter(ColorPrinter):
    """Generate figlets."""
    def __init__(self, color: str = "blue", figlet_font: str = 'speed',
                 file: TextIO = sys.stdout):
        self.figlet_font = figlet_font
        super().__init__(color=color, file=file)

    def text_out(self, text: str) -> None:
        """Coloured terminal print function."""
        print(colored(figlet_format(
            text, font=self.figlet_font), self.color), file=self.file)


if __name__ == '__main__':
    import time
    print('Test printers...')
    print('1. Test spinner...')
    spinner_obj = yaspin(Spinners.line, text="Test Text", color="yellow")
    print(type(spinner_obj))
    spinner = YaspinPrinter(spinner=spinner_obj)
    with spinner_obj as running_spinner:
        spinner.text_out("Running dummy analysis.")
        time.sleep(2)
    spinner.success_out()
    print('2. Test color printer...')
    cprinter = ColorPrinter(color="blue")
    cprinter.text_out("Test color text.")
    print('3. Test figlet printer...')
    fprinter = FigletPrinter(color="yellow")
    fprinter.text_out("HEET")
