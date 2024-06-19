""" """
from abc import ABC, abstractmethod
import pathlib
from typing import Any, List, Dict, Optional
from heet.io.renderer import JinjaRenderer
from heet.utils import get_package_file, read_config
from heet.exceptions import MessageNotFoundException

JINJA_TEMPLATE_PATH = get_package_file('./templates/terminal/emissions/')


class Message(ABC):
    """Message template."""
    def __init__(self, name: Optional[str] = None) -> None:
        self._name = name
        self._text: List[str] = []

    @property
    def name(self) -> str:
        if self._name:
            return self._name
        return ""

    def number_lines(self) -> int:
        return len(self._text)

    @abstractmethod
    def text(self) -> str:
        pass


class TextMessage(Message):
    """Simple text message."""
    def __init__(self, message: List[str], name: Optional[str] = None,
                 **data: Any) -> None:
        super().__init__(name=name)
        self._text = message
        self.data = data

    @classmethod
    def from_dict(cls, config_dict: Dict, name: str,
                  **data: Any) -> 'TextMessage':
        """ """
        try:
            message_dict = config_dict[name]
            return cls(
                message=message_dict['text'],
                name=name,
                data=data)
        except KeyError:
            return cls(message=[''], name="Not supported")

    @classmethod
    def from_config_file(
            cls, config_file: pathlib.Path, name: str,
            **data: Any) -> 'TextMessage':
        """ """
        # Load config
        config_dict = read_config(config_file, 'yaml')
        return cls.from_dict(config_dict, name, **data)

    def text(self) -> str:
        for txt_line in self._text:
            try:
                yield txt_line.format(**self.data)
            except KeyError:
                yield txt_line


class JinjaRenderedMessage(Message):
    """Message from template file parsed through jinja templating engine.

    Attributes:
        template_file (pathlib.Path): Full posix path to the template file
        name
    """
    def __init__(self, file_path: pathlib.Path,
                 name: Optional[str] = None,
                 required_vars: Optional[List[str]] = None,
                 logging: bool = False,
                 **data: Any) -> None:
        super().__init__(name=name)
        self._text: List[str] = []
        # Get folder and the name of the template file from template file path
        template_folder = pathlib.Path(file_path.parent)
        self.template_file = pathlib.Path(file_path.name)
        self.required_vars = required_vars
        self._logging = logging
        self.data = data
        check_variables = bool(required_vars)
        self.renderer = JinjaRenderer(
            template_folder=template_folder,
            check_variables=check_variables)

    @classmethod
    def from_dict(cls, config_dict: Dict, name: str,
                  required_vars: Optional[List[str]] = None,
                  logging: bool = False,
                  **data: Any) -> 'JinjaRenderedMessage':
        """ """
        try:
            message_dict = config_dict[name]
            return cls(
                file_path=pathlib.Path(
                    JINJA_TEMPLATE_PATH, message_dict['template']),
                name=name,
                required_vars=required_vars,
                logging=logging,
                data=data)
        except KeyError as err:
            raise MessageNotFoundException(name) from err

    @classmethod
    def from_config_file(
            cls, config_file: pathlib.Path, name: str,
            required_vars: Optional[List[str]] = None,
            logging: bool = False,
            **data: Any) -> 'JinjaRenderedMessage':
        """ """
        # Load config
        config_dict = read_config(config_file, 'yaml')
        return cls.from_dict(config_dict, name, required_vars, logging, **data)

    def _render_message(self) -> None:
        # Render message
        rendered_output = self.renderer.render(
            template_file=self.template_file,
            required_vars=self.required_vars,
            logging=self._logging,
            **self.data)
        self._text = rendered_output.as_list_of_strings()

    def text(self) -> str:
        self._render_message()
        for txt_line in self._text:
            try:
                yield txt_line.format(**self.data)
            except KeyError:
                yield txt_line


if __name__ == "__main__":
    print(JINJA_TEMPLATE_PATH)
    msg1 = TextMessage(
        message=["heyhey {xx}", 'lulu', 'ula {xx}', "hey2 {t}, {xx}"],
                 xx=3, t=56)
    for line in msg1.text():
        print(line)

    txt_config_file = get_package_file('config/emissions/text_messages.yaml')

    msg1b = TextMessage.from_config(txt_config_file, 'error', app_name='dupa')
    for line in msg1.text():
        print(line)

    input_data = {'app_version': '1.0'}
    msg2 = JinjaRenderedMessage(
        file_path=pathlib.Path('/home/lepton/Dropbox (The University of Manchester)/git_projects/heet/src/heet/templates/terminal/emissions/greet.j2'),
        app_version=1.0)
    for line in msg2.text():
        print(line)
