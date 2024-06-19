"""Module adding jinja rendering capability.

   Used e.g. for rendering messages output in `Terminal` from message templates
   stored as jinja `.j2` template files inside the `templates` directory.
"""

import pathlib
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
import logging
import json
import yaml
from jinja2 import Environment, FileSystemLoader
from heet.utils import get_package_file
import heet.log_setup

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)
logger.setLevel(logging.INFO)

@dataclass
class RenderedOutput:
    """Class storing the rendered output data with additional information
       coming from variable checking functionality in JinjaRenderer."""
    text: str
    variables_checked: bool
    missing_vars: Optional[List[str]] = field(default=None)

    def __post_init__(self):
        if self.missing_vars is None:
            self.missing_vars = ['']

    def as_list_of_strings(self) -> List[str]:
        """Convert a string with line breaks into the list of strings,
           each representing a single line."""
        return self.text.splitlines()

    def as_json_dict(self) -> Dict:
        """Convert a valid JSON string into a dictionary."""
        return json.loads(self.text)


class JinjaRenderer:
    """Renders text using a jinja template file and data.

    Attributes:
        template_folder: path to the folder in which the jinja template(s) are
            located.
        check_variables: Flag determining whether a check is performed that
            looks if any arguments that need to be supplied to jinja.render
            function are missing in the method call.
        jinja_env: Jinja rendering environment.
    """

    def __init__(
            self,
            template_folder: pathlib.Path,
            check_variables: bool = False):
        self.template_folder = template_folder
        self.check_variables = check_variables
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_folder),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True)

    @staticmethod
    def _load_config(config_file: pathlib.Path) -> Dict:
        """ Load yaml config file and return contents in a dictionary."""
        with open(get_package_file(
                config_file.as_posix()), "r", encoding="utf8") as file:
            return yaml.load(file, Loader=yaml.FullLoader)

    @staticmethod
    def _find_missing_vars(
            required_vars: List[str],
            given_vars: List[str]) -> List[str]:
        """Checks whether some variables given in the template are missing
           in the template rendering function."""
        missing_variables = []
        missing_variables = list(set(required_vars) - set(given_vars))
        return missing_variables

    def list_templates(self) -> List[str]:
        """List jinja template files included in the template folder."""
        return [
            fn.name for fn in self.template_folder.iterdir()
            if fn.is_file() and fn.suffix.lower() == ".j2"]

    def render(
            self,
            template_file: Union[str, pathlib.Path],
            required_vars: Optional[List[str]] = None,
            logging: bool = False,
            **data: Any) -> RenderedOutput:
        """Render text in a template file and return a list of strings
        representing separate individual text lines."""
        output = RenderedOutput(
            text="",
            variables_checked=False,
            missing_vars=None)
        # Cast pathlib.Path object to string
        if isinstance(template_file, pathlib.Path):
            template_file = template_file.name
        if template_file in self.list_templates():
            _template = self.jinja_env.get_template(template_file)
            if self.check_variables and required_vars is not None:
                # Perform variable checking
                missing_vars = self._find_missing_vars(
                    required_vars=required_vars,
                    given_vars=list(data.keys()))
                output.variables_checked = True
                output.missing_vars = missing_vars
                if logging:
                    logger.warning(
                        "Following variables are required for the template " +
                        "but missing from the function arguments:")
                    logger.warning("%s", ', '.join(missing_vars))
            output.text = _template.render(**data)
        else:
            logger.debug("File %s not found.", template_file)
        return output


if __name__ == '__main__':
    pass
