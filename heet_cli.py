import ee
import os
import re
import sys
import signal
import argparse
import requests
import logging
import pandas as pd

from pathlib import Path
from datetime import datetime
from typing import Tuple, Iterator, Union
from yaspin import yaspin
from yaspin.spinners import Spinners
from PyInquirer import style_from_dict, Token, prompt, Separator
from pyfiglet import figlet_format
from tqdm import tqdm
from termcolor import colored
import polling2

from delineator import heet_validate  # Does not import ee
from delineator import heet_monitor as mtr

# ! IMPORTANT !
#
# Additional imports of heet_* modules are delayed until EE authentications
# has been checked and completed if needed. Otherwise imports will fail
# if not authenticated to EE.
#

# ==============================================================================
#  Set up logger
# ==============================================================================

# Create new log each run (TODO; better implementation)
with open("heet.log", "w") as file:
    pass


# Gets or creates a logger
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.DEBUG)

# define file handler and set formatter
file_handler = logging.FileHandler("heet.log")
formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)

# ==============================================================================
# CLI Arguments
# ==============================================================================


parser = argparse.ArgumentParser(
    description="Generate catchment and reservoir shapefiles (and associated \
        parameters) for one or more dam locations."
)

parser.add_argument(
    "inputfile",
    type=str,
    help="Path to CSV file containing a list of dams and associated \
        input parameters.",
)

parser.add_argument(
    "jobname",
    type=str,
    help="Short job name for naming output folders. Must be 3-10 characters \
        long and only contain: A-Z, 0-9 or -.",
)

parser.add_argument(
    "outputs",
    choices=[
        "standard",
        "extended",
        "diagnostic-catch",
        "diagnostic-res",
        "diagnostic-riv",
        "diagnostic",
    ],
    help="The set of output files to export",
)

# ==============================================================================
# Functions
# ==============================================================================


def print_term(string, color, font="speed", figlet=False):
    if colored:
        if not figlet:
            print(colored(string, color))
        else:
            print(colored(figlet_format(string, font=font), color))
    else:
        print(string)


def has_internet_connection(url="http://www.google.com/", timelimit=5):
    try:
        iconnect = requests.head(url, timeout=timelimit)
        return True
    except requests.ConnectionError as error:
        return False


def is_authenticated():

    if "CI_ROBOT_USER" in os.environ:
        return False
    else:
        try:
            ee.Initialize()
            return True
        except Exception as error:
            return False


def authenticate_ee():
    try:
        if "CI_ROBOT_USER" in os.environ:
            gc_service_account = os.environ["GCLOUD_ACCOUNT_EMAIL"]
            credentials = ee.ServiceAccountCredentials(
                gc_service_account, "service_account_creds.json"
            )
            ee.Initialize(credentials)
            return True
        else:
            ee.Authenticate()
            ee.Initialize()
            return True
    except Exception as error:
        print(error)
        sys.exit(
            "[ERROR] HEET Encountered an error authenticating to Google Earth \
                        Engine and will close\n[ERROR] see heet.log for details"
        )


def output_asset_folder(jobname: str) -> str:
    """Produce a name for the asset folder where calculation results
    are stored locally"""
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    time = now.strftime("%H%M")
    folder_name = jobname + "_" + year + month + day + "-" + time
    return folder_name


def signal_handler(signal, frame):
    sys.exit("CTRL-C was pressed. Exiting...")


def update_sp_success(sp):
    sp.color = "cyan"
    sp.ok("*")
    return sp


def update_sp_fail(sp):
    sp.color = "red"
    sp.fail("!")
    return sp


def update_sp_err_fatal(sp):
    sp.write("")
    sp.write("  [ERROR] HEET encountered a fatal error and will exit")
    sp.write("")
    sp.write("Thank you for using HEET!")
    return sp


def update_sp_err_internet(sp):
    sp.write("")
    sp.write("  [ERROR] HEET encountered an error and will exit")
    sp.write("  [ERROR] No internet connection")
    sp.write("")
    sp.write("  Please connect to the internet and try again")
    sp.write("")
    sp.write("Thank you for using HEET!")
    return sp


def update_sp_err_folder(sp, folder_path):
    sp.write("")
    sp.write("  [ERROR] HEET encountered an error and will exit")
    sp.write(
        f"  [ERROR] Folder {folder_path} already exists. Please fix this and try again"
    )
    sp.write("")
    sp.write("Thank you for using HEET!")
    return sp


def update_sp_err_fnf(sp):
    sp.write("")
    sp.write("  [ERROR] HEET encountered an error and will exit")
    sp.write("  [ERROR] File not found")
    sp.write("")
    sp.write("Thank you for using HEET!")
    return sp


def update_sp_err_load(sp, input_file_path):
    sp.write("")
    sp.write("  [ERROR] HEET encountered an error and will exit")
    sp.write(f"  [ERROR] There was a problem loading input file {input_file_path}")
    sp.write("")
    sp.write("  Please see heet.log for further details.")
    sp.write("")
    sp.write("Thank you for using HEET!")
    return sp


def update_sp_inv_fields(sp, issues):
    sp.write("")
    sp.write("  [ERROR] HEET encountered an error and will exit ")
    sp.write("  [ERROR] Input file contains errors.")
    sp.write("")
    sp.write(f"  Please fix the following issues:\n{issues}")
    sp.write("")
    sp.write("Thank you for using HEET!")
    return sp


def update_sp_inv_file(sp, issues):
    sp.write("")
    sp.write("  [ERROR] HEET encountered an error and will exit ")
    sp.write("  [ERROR] Input file contains errors")
    sp.write("")
    sp.write(f"  Please fix the following issues:\n{issues}")
    sp.write("")
    sp.write("  See heet_input_report.csv for further details")
    sp.write("")
    sp.write("Thank you for using HEET!")
    return sp


def update_sp_err_running(sp):
    # sp.write("123456789|123456789|123456789|123456789|123456789|123456789|123456789|123456789|")
    sp.write("")
    sp.write(
        "  Oops! Your Google Earth Engine Asset Task List already contains HEET tasks"
    )
    sp.write("        It looks like another HEET analysis is already running")
    sp.write("")
    sp.write(
        "        If you choose to continue, any existing HEET tasks (with a description"
    )
    sp.write(
        "        starting 'XHEET-X') will be cancelled and the contents of Asset Folder"
    )
    sp.write("        XHEET/tmp will be deleted")
    sp.write("")
    sp.write(
        "        You will be asked to confirm that you understand this msg and then"
    )
    sp.write("        asked if you want to continue...")
    sp.write("")
    return sp


def update_sp_err_interrupted(sp):
    sp.write("")
    sp.write(
        "  Oops! Your Google Earth Engine Asset Folder XHEET/tmp already contains some"
    )
    sp.write(
        "        files. It looks like a previous HEET analysis was interrupted and did"
    )
    sp.write("        not complete")
    sp.write("")
    sp.write(
        "        If you choose to continue, any existing HEET tasks (with a description"
    )
    sp.write(
        "        starting 'XHEET-X') will be cancelled and the contents of Asset Folder"
    )
    sp.write("        XHEET/tmp will be deleted")
    sp.write("")
    sp.write(
        "        You will be asked to confirm that you understand this msg and then"
    )
    sp.write("        asked if you want to continue...")
    sp.write("")
    return sp


def update_sp_err_upload(sp):
    sp.write("")
    sp.write("  [ERROR] HEET encountered an error and will exit")
    sp.write("  [ERROR] There was a problem uploading file to Google Earth Engine.")
    sp.write("          See heet.log for details.")
    sp.write("")
    sp.write("Thank you for using HEET!")
    return sp


def update_sp_warn_skip(sp):
    sp.write("")
    sp.write("  [WARNING] HEET encountered an problem and will skip this step")
    sp.write("  [WARNING] Check heet.log for further details.")
    sp.write("")
    return sp


def update_sp_inv_output(sp, issues):
    # sp.write("123456789|123456789|123456789|123456789|123456789|123456789|123456789|123456789|")
    sp.write("")
    sp.write(
        "  [Warning] Calculated parameters contain impossible or improbable values on"
    )
    sp.write("            some fields")
    sp.write("")
    sp.write(f"  Please be aware of the following issues:\n{issues}")
    sp.write("")
    sp.write("  See heet_output_report.csv for further details")
    sp.write("")
    return sp


def update_sp_err_time(sp):
    current_active_analyses = ",".join([str(i) for i in mtr.active_analyses])
    sp.write(
        "  [WARNING] Analysis wait time limit exceeded. Cancelling all unfinished HEET"
    )
    sp.write(f"            tasks (active analysis ids: {current_active_analyses})")
    sp.write("")
    return sp


def update_sp_err_noaudit(sp):
    sp.write("  [WARNING] tasks.csv NOT saved")
    return sp


def update_sp_inf_service(sp):
    sp.write("")
    sp.write("  [INFO] Service Account Authenticated; Skipping step")
    sp.write("")
    return sp


# ==============================================================================
# Main
# ==============================================================================


signal.signal(signal.SIGINT, signal_handler)


def main():

    os.system("")  # enables ansi escape characters in terminal
    args = parser.parse_args()
    input_file_path = Path(args.inputfile)
    jobname = (args.jobname).upper()
    outputs = args.outputs

    # Validate jobname
    pattern = re.compile("^[a-zA-Z0-9\\-]{3,10}$")
    if bool(re.search(pattern, jobname)) == False:
        sys.exit(
            f"[ERROR] HEET encountered an error and could not start \n \
              [ERROR] Job name {jobname} must be 3-10 characters long and only contain: A-Z, 0-9 or - "
        )

    # Define an output folder name
    output_folder_name = output_asset_folder(jobname)
    output_folder_path = Path("outputs", output_folder_name)

    # Tasks on critical path
    ntasks = len(mtr.critical_path)

    # ==========================================================================
    # Greeting
    # ==========================================================================
    print_term("HEET", color="blue", figlet=True)
    print_term("v1.0 By the Future Dams Project", "blue")

    print("")
    print("Welcome! Your analysis will begin automatically.")
    print(f"* CTRL-C to exit")
    print(f"* Input parameters will be read from: {args.inputfile}")
    print(f"* Job name: {jobname}")
    print("")

    # ==========================================================================
    # Internet connection
    # ==========================================================================
    step_desc = "Checking internet connection"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        connected = has_internet_connection()

        if connected == True:
            sp = update_sp_success(sp)
        else:
            sp = update_sp_fail(sp)
            sp = update_sp_err_internet(sp)
            sys.exit()

    # ==========================================================================
    # Preparing local results folder
    # ==========================================================================
    step_desc = f"Preparing local output folder outputs/{output_folder_name}"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:
        try:
            output_folder_path.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            sp = update_sp_fail(sp)
            sp = update_sp_err_folder(sp, output_folder_path)
            sys.exit()
        else:
            sp = update_sp_success(sp)

    # ==========================================================================
    # Checking local input file
    # ==========================================================================
    step_desc = "Checking input file"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        # File exists
        if not input_file_path.exists():
            sp = update_sp_fail(sp)
            sp = update_sp_err_fnf(sp)
            sys.exit()

        # File Loads
        try:
            df_inputs = heet_validate.csv_to_df(input_file_path)
        except Exception:
            sp = update_sp_fail(sp)
            sp = update_sp_err_load(sp, input_file_path)
            sys.exit()

        # Fields valid
        try:
            status = heet_validate.valid_input_fields(df_inputs)
        except Exception:
            sp = update_sp_fail(sp)
            sp = update_sp_err_fatal(sp)
            sys.exit()
        else:
            if status["valid"] == False:
                sp = update_sp_fail(sp)
                sp = update_sp_inv_fields(sp, status["issues"])
                sys.exit()

        # File valid
        try:
            status = heet_validate.valid_input(
                df_inputs, input_file_path, output_folder_path
            )
        except Exception:
            sp = update_sp_fail(sp)
            sp = update_sp_err_fatal(sp)
            sys.exit()
        else:
            if status["valid"] == False:
                sp = update_sp_fail(sp)
                sp = update_sp_inv_file(sp, status["issues"])
                sys.exit()
            else:
                sp = update_sp_success(sp)
    # ==========================================================================
    # Authentication
    # ==========================================================================
    step_desc = "Checking Google Earth Engine authentication"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        ee_authenticated = is_authenticated()

        if ee_authenticated == True:
            sp = update_sp_success(sp)
        else:
            sp = update_sp_fail(sp)
            sp.write("")
            try:
                authenticate_ee()
            except Exception:
                sp = update_sp_fail(sp)
                sp = update_sp_err_fatal(sp)
                sys.exit()
            else:
                sp.write("")
                sp = update_sp_success(sp)

    # ==========================================================================
    # Post Authentication Setup
    # ==========================================================================

    # Unconventional, heet imports (using ee) are delayed until GEE
    # authentication and initialisation are confirmed.
    from delineator import heet_task
    from delineator import heet_export
    from delineator import heet_config as cfg

    cfg.output_asset_folder_name = output_folder_name
    cfg.output_drive_folder = "XHEET_" + cfg.output_asset_folder_name

    # Set export parameters for output selected
    if outputs == "extended":
        cfg.exportRawDamPts = True

    if outputs == "diagnostic-catch":
        cfg.exportRawDamPts = True
        cfg.exportWatershedCpts = True
        cfg.exportWatershedDpts = True
        cfg.exportCatchmentPixels = True

    if outputs == "diagnostic-res":
        cfg.exportReservoirPixels = True
        cfg.exportWaterbodies = True

    if outputs == "diagnostic-riv":
        cfg.exportSimplifiedReservoir = True
        cfg.exportRiver = True

    if outputs == "diagnostic":
        cfg.exportRawDamPts = True
        cfg.exportWatershedCpts = True
        cfg.exportWatershedDpts = True
        cfg.exportCatchmentPixels = True
        cfg.exportReservoirPixels = True
        cfg.exportWaterbodies = True
        cfg.exportSimplifiedReservoir = True

    # ==========================================================================
    # Check asset folder
    # ==========================================================================

    # Setting pyinquirer styles
    style = style_from_dict(
        {
            Token.Separator: "#000080",
            Token.QuestionMark: "#008080 bold",
            Token.Selected: "#000080",  # default
            Token.Pointer: "#000080 bold",
            Token.Instruction: "",  # default
            Token.Answer: "#000080 bold",
            Token.Question: "",
        }
    )

    questions = [
        {
            "type": "confirm",
            "message": "I understand what will happen if I continue",
            "name": "understand",
        },
        {
            "type": "confirm",
            "message": "Would you like to continue?",
            "name": "continue",
        },
    ]

    step_desc = "Checking Google Earth Engine Asset Folder:"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            existing_tasks = heet_task.existing_tasks_running()
            existing_files = heet_task.existing_job_files()
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_err_fatal(sp)
            sys.exit()
        else:
            if (existing_tasks == True) or (existing_files == True):
                sp = update_sp_fail(sp)

                if existing_tasks == True:
                    sp = update_sp_err_running(sp)
                elif existing_files == True:
                    sp = update_sp_err_interrupted(sp)

                if "CI_ROBOT_USER" in os.environ:
                    # If robot, don't trigger interactive questions
                    sp = update_sp_inf_service(sp)
                else:
                    # Followup questions
                    answer1 = prompt(
                        [questions[0]], style=style, raise_keyboard_interrupt=False
                    )
                    if answer1 == {}:
                        sys.exit("Exiting (Keyboard Interrupt)")
                    if answer1["understand"] == False:
                        sys.exit("Exiting (Did not understand)")
                    answer2 = prompt(
                        [questions[1]], style=style, raise_keyboard_interrupt=False
                    )
                    if answer2 == {}:
                        sys.exit("Exiting (Keyboard Interrupt)")
                    if answer2["continue"] == False:
                        sys.exit("Exiting (No continue)")
                    sp.write("")
            else:
                sp = update_sp_success(sp)

    # ==========================================================================
    # Prepare asset folder
    # ==========================================================================
    step_desc = "Preparing Google Earth Engine Asset Folder"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        if existing_tasks == True:
            try:
                heet_task.kill_all_heet_tasks()
                heet_task.wait_until_jobs_finish()
            except Exception:
                # Handles any issue, including connectivity
                sp = update_sp_fail(sp)
                sp = update_sp_err_fatal(sp)
                sys.exit()

        try:
            heet_task.prepare_gee_assets_folder()
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_err_fatal(sp)
            sys.exit()
        else:
            sp = update_sp_success(sp)

    # ==========================================================================
    # Upload input file
    # ==========================================================================
    step_desc = "Uploading input file to Google Earth Engine"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            df = heet_validate.prepare_input_table(df_inputs)
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_err_fatal(sp)
            logger.exception(
                "[heet_cli] There was a problem preparing input file.  Exiting..."
            )
            sys.exit()

        try:
            inputs_ftc = heet_export.df_to_ee(df)
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_err_fatal(sp)
            logger.exception(
                "[heet_cli] There was a problem converting input file from df to ftc.  Exiting..."
            )
            sys.exit()

        try:
            upload_task = heet_export.upload_user_inputs(inputs_ftc)
        except Exception:
            sp = update_sp_fail(sp)
            sp = update_sp_err_upload(sp)
            logger.exception(
                "[heet_cli] There was a problem uploading user inputs to Google Earth Engine. Exiting..."
            )
            sys.exit()

        try:
            heet_task.wait_until_upload(upload_task)
        except polling2.TimeoutException:
            sp = update_sp_fail(sp)
            sp = update_sp_err_upload(sp)
            logger.info(
                "[heet_cli] Uploading user inputs to Google Earth Engine timed out. Exiting..."
            )
            sys.exit()
        except Exception:
            sp = update_sp_fail(sp)
            sp = update_sp_err_upload(sp)
            logger.exception(
                "[heet_cli] There was a problem uploading user inputs to Google Earth Engine. Exiting..."
            )

        try:
            upload_success = upload_task.status()["state"] in ["COMPLETED"]
        except Exception:
            sp = update_sp_fail(sp)
            sp = update_sp_err_upload(sp)
            logger.debug(
                "[heet_cli] There was a problem uploading user inputs to Google Earth Engine. Exiting..."
            )

        if upload_success == True:
            sp = update_sp_success(sp)
        else:
            sp = update_sp_fail(sp)

    # ==========================================================================
    # Run Analysis
    # ==========================================================================

    batch_size = df_inputs.shape[0]
    n_calcs = batch_size * ntasks

    step_desc = f"Analysing {batch_size} dam locations ({n_calcs} calculations)"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            sp = update_sp_success(sp)
            pbar = tqdm(total=n_calcs, ncols=80)
            status = heet_task.run_analysis(pbar)
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_err_fatal(sp)
            logger.exception("Fatal error when running analysis")
            sys.exit()
        else:
            if status == 1:
                sp = update_sp_fail(sp)
                sp = update_sp_err_time(sp)
                logger.info(
                    "(Running) Analysis wait time limit exceeded. Cancelling all unfinished HEET tasks."
                )
                try:
                    heet_task.kill_all_heet_tasks()
                except Exception:
                    sp = update_sp_err_fatal(sp)
                    sys.exit()
        pbar.close()

    # ==========================================================================
    # Task completion (1)
    # ==========================================================================
    step_desc = "Waiting for running analysis tasks to complete"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet_task.wait_until_jobs_finish()
        except polling2.TimeoutException:
            sp = update_sp_fail(sp)
            sp = update_sp_err_time(sp)
            logger.info(
                "(Waiting) Analysis wait time limit exceeded. Cancelling all unfinished HEET tasks."
            )
            try:
                heet_task.kill_all_heet_tasks()
            except Exception:
                sp = update_sp_err_fatal(sp)
                sys.exit()
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_err_fatal(sp)
            sys.exit()
        else:
            sp = update_sp_success(sp)

    # ==========================================================================
    # Preparing for export
    # ==========================================================================
    step_desc = "Collecting calculated parameters for export"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet_task.assets_to_ftc()
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_warn_skip(sp)
        else:
            sp = update_sp_success(sp)

    # ==========================================================================
    # Task completion (2)
    # ==========================================================================
    step_desc = "Waiting for data collection tasks to complete"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet_task.wait_until_jobs_finish()
        except polling2.TimeoutException:
            sp = update_sp_fail(sp)
            sp = update_sp_err_time(sp)
            logger.info(
                "(Waiting) Analysis wait time limit exceeded. Cancelling all unfinished HEET tasks."
            )
            try:
                heet_task.kill_all_heet_tasks()
            except Exception:
                sp = update_sp_err_fatal(sp)
                sys.exit()
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_err_fatal(sp)
            sys.exit()
        else:
            sp = update_sp_success(sp)

    # ==========================================================================
    # Exporting Results
    # ==========================================================================
    step_desc = "Exporting results to Google Drive"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            if "CI_ROBOT_USER" in os.environ:
                sp = update_sp_inf_service(sp)
            else:
                heet_task.export_to_drive()
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_warn_skip(sp)
        else:
            sp = update_sp_success(sp)
            mtr.active_exports = list(mtr.active_export_tasks_log.keys())
            export_size = len(mtr.active_exports)
            remaining_export_size = export_size
            pbar = tqdm(total=export_size, ncols=80)

            keep_going = 1
            while (len(mtr.active_exports) > 0) and (keep_going == 1):
                try:
                    heet_task.wait_until_exports()
                    active_count = len(mtr.active_exports)
                    new_exports = remaining_export_size - active_count
                    remaining_export_size = active_count
                    pbar.update(new_exports)
                except polling2.TimeoutException:
                    keep_going = 0
                    sp = update_sp_fail(sp)
                    sp = update_sp_err_time(sp)
                    logger.info(
                        "(Waiting) Analysis wait time limit exceeded. Cancelling all unfinished HEET tasks."
                    )
                    try:
                        heet_task.kill_all_heet_tasks()
                    except Exception:
                        sp = update_sp_err_fatal(sp)
                        sys.exit()
                except Exception:
                    sp = update_sp_fail(sp)
                    sys.exit()
            pbar.close()

    # ==========================================================================
    # Exporting Results (Json, local Folder)
    # ==========================================================================
    step_desc = "Downloading json results to local results folder"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet_export.batch_export_to_json(output_folder_path)
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_warn_skip(sp)
            logger.exception(
                "[batch_export_to_json] Problem exporting output parameters to json"
            )
        else:
            sp = update_sp_success(sp)

    # ==========================================================================
    # Exporting CSV Results
    # ==========================================================================
    step_desc = "Downloading csv results to local results folder"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet_export.download_output_parameters(output_folder_path)
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_warn_skip(sp)
        else:
            sp = update_sp_success(sp)

    # ==========================================================================
    # Exporting Results (Assets Folder)
    # ==========================================================================
    step_desc = "Exporting results to Google Earth Engine Assets Folder"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            if "CI_ROBOT_USER" in os.environ:
                sp = update_sp_inf_service(sp)
            else:
                heet_task.export_to_assets()
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_err_fatal(sp)
            sys.exit()
        else:
            sp = update_sp_success(sp)

    # ==========================================================================
    # Checking local output file structure
    # ==========================================================================
    step_desc = "Checking csv results contain required columns"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        output_file_path = Path(output_folder_path, "output_parameters.csv")

        try:
            df_outputs = heet_validate.csv_to_df(output_file_path)
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_warn_skip(sp)
            sys.exit()
        else:
            try:
                status = heet_validate.valid_output_fields(df_outputs)
            except Exception:
                # Handles any issue, including connectivity
                sp = update_sp_fail(sp)
                sp = update_sp_warn_skip(sp)
                sys.exit()
            else:
                if status["valid"] == True:
                    sp = update_sp_success(sp)
                else:
                    sp = update_sp_fail(sp)
                    sp = update_sp_inv_output(sp, status["issues"])

    # ==========================================================================
    # Check outputs for data validation issues
    # ==========================================================================
    step_desc = "Checking csv results for impossible and improbable output values"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        output_file_path = Path(output_folder_path, "output_parameters.csv")

        try:
            df_outputs = heet_validate.csv_to_df(output_file_path)
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_warn_skip(sp)
            sys.exit()
        else:
            try:
                status = heet_validate.valid_output(
                    df_outputs, output_file_path, output_folder_path
                )
            except Exception:
                # Handles any issue, including connectivity
                sp = update_sp_fail(sp)
                sp = update_sp_warn_skip(sp)
                sys.exit()
            else:
                if status["valid"] == True:
                    sp = update_sp_success(sp)
                else:
                    sp = update_sp_fail(sp)
                    sp = update_sp_inv_output(sp, status["issues"])

    # ==========================================================================
    # Exporting Results (Assets Folder)
    # ==========================================================================
    step_desc = "Generating Earth Engine task log"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet_task.task_audit(output_folder_path)
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_warn_skip(sp)
            logger.debug("[heet_cli] HEET encountered a problem generating tasks.csv")
            sys.exit()
        else:
            sp = update_sp_success(sp)

    # ==========================================================================
    # Cleaning up
    # ==========================================================================
    step_desc = "Cleaning up Google Earth Engine workspace"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet_task.clear_tmp_folder()
        except Exception:
            # Handles any issue, including connectivity
            sp = update_sp_fail(sp)
            sp = update_sp_err_fatal(sp)
            sys.exit()
        else:
            sp = update_sp_success(sp)

        # ==========================================================================
        # Results Summary
        # ==========================================================================

        sp.write("")
        sp.write("Your results:")
        sp.write("")
        sp.write(
            "  Please right click and follow the link below to view your results in Google drive:"
        )
        sp.write(
            f"  https://drive.google.com/drive/u/0/search?q={cfg.output_drive_folder}"
        )
        sp.write("")
        sp.write(
            "  Please follow the link below and navigate to the Assets tab to view your results in Google Earth Engine:"
        )
        sp.write(f"  https://code.earthengine.google.com/")
        sp.write("")
        sp.write(
            "  Please check the following local folder for output parameters (csv/json) and input/output validation reports"
        )
        sp.write(f"  outputs/{output_folder_name}")
        sp.write("")
        sp.write("Visualisation:")
        sp.write("")
        sp.write(
            "  To visualise your results, please navigate to the following script and update the parameters as directed:"
        )
        sp.write(
            f"  https://code.earthengine.google.com/264776718cccc3c6df5295200185d0a1"
        )
        sp.write("")
        sp.write("Thank you for using HEET!")


if __name__ == "__main__":
    main()
