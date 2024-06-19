"""Module providing the Application abstract base class and classes
   implementing the Application interface.

   Application is used as a Controller in the MVC design pattern.
   It interacts with the Computational Engine (Model) and Terminal
   (View). """
import sys
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import signal
from heet.utils import get_package_file, read_config
from heet.web.connectivity import ConnectionMonitor
from heet.events.event_handlers import AppEventHandler
from heet.events.abstract import EventHandler
from heet.io.printers import ColorPrinter
from heet.jobs import Job
from heet.io.terminal import View, Terminal

# Load configuration file
EMISSIONSAPP_CONFIG: dict = read_config(
    get_package_file("./config/emissions/general.yaml"))
APP_NAME = EMISSIONSAPP_CONFIG['application']['name_short']


# Application class:
# Flush the log file
# Load configuration files
# Add logging
# Add task monitor
# Add exporter
# Add calculation engine


class Controller(ABC):
    """Abstract base class providing an interface for a generic application."""

    @abstractmethod
    def init(self) -> None:
        """ """

    @abstractmethod
    def start(self) -> None:
        """Start the application and perform necessary checks."""

    @abstractmethod
    def stop(self) -> None:
        """Stop the applications and clean all temporary resources."""


class Application(Controller):
    """Applies MVC pattern to separate the logic from the view."""
    def __init__(self, name: str, connection_monitor: bool = False) -> None:
        self.name = name
        # Model constitutes of a list of jobs, each one being an ordered
        # list of tasks.
        self.jobs: List[Job] = []
        self.current_job_index: Optional[int] = None
        self.connection_monitor: Optional[ConnectionMonitor] = None
        if connection_monitor:
            self.connection_monitor = ConnectionMonitor()
        self.events: EventHandler = AppEventHandler()
        # View constitutes a terminal object
        #self.terminal = Terminal()
        self.init()

    @property
    def current_job(self) -> Optional[Job]:
        if self.current_job_index is not None:
            return self.jobs[self.current_job_index]
        return None

    @staticmethod
    def int_signal_handler(signal, frame):
        """Handler for signal.SIGINT"""
        sys.exit(" CTRL-C was pressed. Exiting...")

    def init(self) -> None:
        print('initializing the application')
        # Register a signal for handling asynchrounous events
        signal.signal(signal.SIGINT, self.int_signal_handler)

    def add_job(self, job: Job) -> None:
        self.jobs.append(job)

    def remove_job(self, job: Job) -> None:
        try:
            self.jobs.remove(job)
        except ValueError:
            pass

    def _run_jobs(self) -> None:
        """Run all the jobs in series."""
        for job_index, job in enumerate(self.jobs):
            self.current_job_index = job_index
            job.run()

    def start(self) -> None:
        """ """
        if self.connection_monitor:
            with self.connection_monitor:
                self._run_jobs()
        else:
            self._run_jobs()

    def stop(self) -> None:
        """ """


class GHGApplication(Application):
    """High level component representing the application for delineating
    reservoirs and catchments and generating input files required for post-
    processing with a GHG emission tool/model RE-Emission."""
    def __init__(self, job: Job, app_name: str = APP_NAME):
        self.job = job
        self.app_name: str = app_name

        # Set up the terminal for outputting messages to console
        #self.terminal = EmissionsTerminal()
        # Set up connection monitor
        self.monitor = ConnectionMonitor()
        # Input
        #self.input: Input = None
        # Initialize empty data structures
        self.data_sources: List = []
        self.data: List = []
        self.exporters: List = []
        self._messages: Dict[str, str] = self._application_messages()

    def _application_messages(self) -> Dict[str, str]:
        """ """
        messages = {
            'thanks': f"Thank you for using {self.app_name}!",
            'error': f"  [ERROR] {self.app_name} encountered an error and will exit.",
            'fatal_error': f"  [ERROR] {self.app_name} encountered a fatal error and will exit."
        }
        return messages

    @property
    def messages(self) -> List[str]:
        return list(self._messages.keys())

    def _greet(self, input_file: str, job_name: str, figlet: bool = True,
               color: str = "blue"):
        """Print greeting message."""
        self.print_term(self.app_name, color=color, figlet=figlet)
        self.print_term("v1.0 By the Future Dams Project", "blue")
        print("")
        print("Welcome! Your analysis will begin automatically.")
        print("* CTRL-C to exit")
        print(f"* Input parameters will be read from: {self.input.input_file}")
        print(f"* Job name: {job.name}")
        print("")

    def init(self) -> None:
        """Initialize the application."""
        # Print greeting message
        def greet():
            printer = ColorPrinter(color="blue", figlet=True)
            printer.text_out(self.app_name)
            printer.figlet = False
            printer.text_out("v1.0 By the Future Dams Project.")
            printer.text_out("")
        greet()

    def run(self) -> None:
        """Start the application and perform necessary checks."""
        # Print
        print("Your analysis will begin automatically.")
        print("* CTRL-C to exit")
        print(f"* Input parameters will be read from: {input_file}")
        print(f"* Job name: {job_name}")
        print("")

    def stop(self) -> None:
        """Stop the applications and clean all temporary resources."""


if __name__ == '__main__':
    #a = GHGApplication(app_name=APP_CONFIG['application']['name_short'])
    #print(a.messages)
    ghg_app = Application(name="First App", connection_monitor=True)
    ghg_app.start()
