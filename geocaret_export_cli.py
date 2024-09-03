import os
import argparse
import logging
import ee
import polling2
from tqdm import tqdm
from yaspin import yaspin
from yaspin.spinners import Spinners

ee.Initialize() # Needs initialising before loading from geocaret

from geocaret import config as cfg
from geocaret import log as lg
from geocaret import task
from geocaret import monitor as mtr

lg.log_file_name = "geocaret_export.log"

parser = argparse.ArgumentParser(
    usage="python geocaret_export_cli.py  --results-path <path-to-results-folder-in-GEE> --drive-folder <folder-in-GDrive> --project <GEE-project-name>"
)
parser.add_argument(
    "--results-path", 
    required=True,
    help="Full path to the geocaret results folder on Earth Engine (must start from projects/<project-name>/...)"
)

# EE Export to Drive functionality is not well documented
# Important:
# - If drive folder does not exist it will be created in the TOP LEVEL of
#   your google drive
# - If drive folder already exists as a top level folder
#   OR as a subdirectory items will be added the existing folder
# - If multiple drive folders of the same name exist, behaviour is unclear
#   but files will likely be added to the most recently modified folder
parser.add_argument(
    "--drive-folder",
    default=os.getcwd(),
    help="Name of Google Drive Folder to save to",
)

parser.add_argument(
    "--project",
    type=str,
    default = "",
    help="Name of Earth Engine cloud project to use",
)

args = parser.parse_args()
results_path = args.results_path
drive_folder = args.drive_folder
project = args.project

if project:
    ee.Initialize(project=project)
else:
    ee.Initialize()

# Warning - overwriting ipmorted config data.
cfg.output_drive_folder = drive_folder

# ==============================================================================
#  Set up logger
# ==============================================================================

# Create new log each run (TODO; better implementation)
with open(lg.log_file_name, "w") as file:
    pass


# Gets or creates a logger
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.DEBUG)

# define file handler and set formatter
file_handler = logging.FileHandler(lg.log_file_name)
formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)


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
    sp.write("  [ERROR] GeoCARET EXPORTER encountered a fatal error and will exit")
    sp.write("")
    sp.write("Thank you for using GeoCARET EXPORTER!")
    return sp


def update_sp_warn_skip(sp):
    sp.write("")
    sp.write(
        "  [WARNING] GeoCARET EXPORTER encountered an problem and will skip Export step"
    )
    sp.write("  [WARNING] Check geocaret_export.log for further details.")
    sp.write("")
    sp.write("")
    return sp


def update_sp_err_time(sp):
    current_active_analyses = ",".join([str(i) for i in mtr.active_analyses])
    sp.write(
        "  [WARNING] Analysis wait time limit exceeded. Cancelling all unfinished GeoCARET EXPORTER"
    )
    sp.write(f"            tasks (active analysis ids: {current_active_analyses})")
    sp.write("")
    return sp


def update_sp_inf_service(sp):
    sp.write("")
    sp.write("  [INFO] Service Account Authenticated; Skipping step")
    sp.write("")
    return sp


if __name__ == "__main__":
    breakpoint = False
    # ==========================================================================
    
    if breakpoint:
        import sys
        print(f"Exporting results folder {results_path} to Google Drive folder {cfg.output_drive_folder}")
        sys.exit("STOP")
            
    # Exporting Results
    # ==========================================================================
    step_desc = f"Exporting results folder {results_path} to Google Drive folder {cfg.output_drive_folder}"

    
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            if "CI_ROBOT_USER" in os.environ:
                sp = update_sp_inf_service(sp)
            else:
                task.export_to_drive(export_from_path=results_path)
        except Exception as error:
            # Handles any issue, including connectivity
            print("Raised exception")
            print(error)
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
                    task.wait_until_exports()
                    active_count = len(mtr.active_exports)
                    new_exports = remaining_export_size - active_count
                    remaining_export_size = active_count
                    pbar.update(new_exports)
                except polling2.TimeoutException:
                    keep_going = 0
                    sp = update_sp_fail(sp)
                    sp = update_sp_err_time(sp)
                    logger.info(
                        "(Waiting) Analysis wait time limit exceeded. Cancelling all unfinished GeoCARET tasks."
                    )
                    try:
                        task.kill_all_heet_tasks()
                    except Exception:
                        sp = update_sp_err_fatal(sp)
                        sys.exit()
                except Exception:
                    sp = update_sp_fail(sp)
                    sys.exit()
            pbar.close()
