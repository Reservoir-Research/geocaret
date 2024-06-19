"""Command Line Interface (CLI) using Python's click package.

    Highest level abstraction and entry point for running the application.
"""
import os
from typing import Optional
import logging
import click
import heet.log_setup
from heet.utils import remove_dir, get_package_file, load_yaml
from heet.application import GHGApplication
from heet.jobs import Job

#  Only work with emissions TODO: change global settings for running different
#  software applications, e.g. bathymetry
APP_CONFIG = load_yaml(
    file_name=get_package_file("./config/emissions/general.yaml"))
# Create a logger
module_directory = os.path.dirname(__file__)
CONSOLE_LOG_NAME = "_".join([__name__, 'console'])
logger = heet.log_setup.create_logger(logger_name=CONSOLE_LOG_NAME)


@click.group()
@click.option('-v', '--verbose', is_flag=True)
def start(verbose: bool):
    """Set logging level, set up the simulation environment and carry out
    analysis pre-checks."""
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


@start.command()
def sanitize():
    """Clear the working environment (local and web)."""
    # Clear the temporary folder set up for local storage of temporary and
    # log files
    remove_dir(dir_path=APP_CONFIG['application']['temp_folder'])


@start.command()
@click.option(
    '-i', '--input-file',
    type=click.Path(exists=True),
    help='Path to CSV file containing a list of dams and associated ' +
    'input parameters.')
@click.option(
    '-j', '--job-name', required=True, type=click.STRING,
    help='Short job name for naming output folders. Must be 3-10 characters ' +
    'long and only contain: A-Z, 0-9 or -.')
@click.option(
    '-o', '--outputs', required=True,
    type=click.Choice(
        ['standard', 'extended', 'diagnostic-catch', 'diagnostic-res',
         'diagnostic-riv', 'diagnostic']),
    help='The set of output files to export.')
def simulate(input_file: Optional[str], job_name: Optional[str],
             outputs: Optional[str]):
    """
    Generate catchment and reservoir shapefiles (and associated parameters)
    for one or more dam locations..
    """
    # Create event handlers ... or should that be done separaterly in the
    # Application, Task and Job classes???
    # Instantiatea job object
    job =  Job(name=job_name)
    # Instantiate the application object
    app = GHGApplication(job=job)


    # Simulation steps
    #1. Start connection monitor
    #2. Instantiate a Job object
    # Prepare tasks to be executed
    # Each task should be able to post events to e.g. terminal
    #3. Start Terminal object
    #4. Create asset folders
    #5. Start monitor
    #6. Greet
    #7. Check internet connection
    #8. Prepare local results folder around yaspin spinner
    #9. Load input file:
    #   - check if exists
    #   - load file to dataframe
    #   - validate fields
    #   - validate file
    #10. Authenticate
    #11. Post authentification setup
    #12. Check asset folder
    #13. Prepare google engine asset folder
    #14. Upload input file
    #15. Run Analysis
    #16. Task completion (1)
    #17, Preparing for export
    #18. Task completion (2)
    #19. Exporting Results
    #20. Exporting Results (Json, local Folder)
    #21. Exporting CSV Results
    #22. Exporting Results (Assets Folder)
    #23. Exporting CSV Results (Json, local Folder)
    #24.  Exporting Results (Assets Folder)
    #25. Cleaning up

@start.command()
@click.option(
    '-i', '--input-folder',
    type=click.Path(exists=False),
    help='Path to output folder with calculation results.')
def postprocess(input_folder: str):
    """ """
    click.echo("Functions for post-processing of the output results.")
    click.echo("Make sure exists flag in click.Path is set to True!!")


if __name__ == '__main__':
    pass
