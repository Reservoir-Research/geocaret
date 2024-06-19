""" """
import os
import sys
import argparse
import ee
from pathlib import Path
from yaspin import yaspin
from yaspin.spinners import Spinners
from PyInquirer import style_from_dict, Token, prompt
from tqdm import tqdm
import polling2
# Import application modules
import heet.validate  # Does not import ee
import heet.monitor as mtr
import heet.log_setup
# Additional imports of heet_* modules are delayed until EE authentications
# has been checked and completed if needed. Otherwise imports will fail
# if not authenticated to EE.
from heet.web.connectivity import ConnectionMonitor
from heet.assets import EmissionAssets
from heet.jobs import Job
from heet.converters import Converter
from heet.earth_engine import EarthEngine
from heet.terminal import EmissionsTerminal

assets = EmissionAssets()
engine = EarthEngine()

# ==============================================================================
#  Set up logger
# ==============================================================================

# Create new log file each run (TODO; better implementation)
with open("heet.log", 'w') as file:
    pass

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)

# ==============================================================================
# CLI Arguments
# ==============================================================================


parser = argparse.ArgumentParser(
    description='Generate catchment and reservoir shapefiles (and associated \
        parameters) for one or more dam locations.')
parser.add_argument(
    'inputfile', type=str,
    help='Path to CSV file containing a list of dams and associated \
        input parameters.')
parser.add_argument(
    'jobname', type=str,
    help='Short job name for naming output folders. Must be 3-10 characters \
        long and only contain: A-Z, 0-9 or -.')
parser.add_argument(
    'outputs',
    choices=['standard',
             'extended',
             'diagnostic-catch',
             'diagnostic-res',
             'diagnostic-riv',
             'diagnostic'],
    help='The set of output files to export')
    

def main():

    # Start connection monitor
    internet_monitor = ConnectionMonitor()

    # Instantiate a Job object
    job = Job(name=args.jobname)

    # Instantiate Terminal object
    et = EmissionsTerminal()

    os.system("")  # enables ansi escape characters in terminal
    args = parser.parse_args()

    input_file_path = Path(args.inputfile)
    outputs = (args.outputs)

    # Define an output folder name
    output_folder_name, output_folder_path = job.output_asset_folder()

    # Tasks on critical path
    ntasks = len(mtr.critical_path)

    # Print greeting message
    et.greet(input_file=args.inputfile, job_name=job.name)

    # ==========================================================================
    # Internet connection
    # ==========================================================================
    step_desc = "Checking internet connection"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        if internet_monitor.connected():
            et.sp_success()
        else:
            et.sp_fail()
            et.sp_err_internet()
            sys.exit()

    # ==========================================================================
    # Preparing local results folder
    # ==========================================================================
    step_desc = f"Preparing local output folder outputs/{output_folder_name}"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:
        try:
            output_folder_path.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            et.sp_fail()
            et.sp_err_folder(output_folder_path)
            sys.exit()
        else:
            et.sp_success()

    # ==========================================================================
    # Checking local input file
    # ==========================================================================
    step_desc = "Checking input file"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        # File exists
        if not input_file_path.exists():
            et.sp_fail()
            et.sp_err_fnf()
            sys.exit()

        # File Loads
        try:
            df_inputs = heet.catchment.validate.csv_to_df(input_file_path)
        except Exception:
            et.sp_fail()
            et.sp_err_load(input_file_path)
            sys.exit()

        # Fields valid
        try:
            status = heet.validate.valid_fields(df_inputs)
        except Exception:
            et.sp_fail()
            et.sp_err_fatal()
            sys.exit()
        else:
            if not status['valid']:
                et.sp_fail()
                et.sp_inv_fields(status['issues'])
                sys.exit()

        # File valid
        try:
            status = heet.validate.valid_input(df_inputs, input_file_path, output_folder_path)
        except Exception:
            et.sp_fail()
            et.sp_err_fatal()
            sys.exit()
        else:
            if not status['valid']:
                et.sp_fail()
                et.sp_inv_file(status['issues'])
                sys.exit()
            else:
                et.sp_success()
    # ==========================================================================
    # Authentication
    # ==========================================================================
    step_desc = "Checking Google Earth Engine authentication"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        ee_authenticated = engine.is_authenticated()

        if ee_authenticated:
            et.sp_success()
        else:
            et.sp_fail()
            try:
                engine.authenticate()
            except Exception:
                et.sp_fail()
                et.sp_err_fatal()
                sys.exit()
            else:
                et.sp_success()

    # ==========================================================================
    # Post Authentication Setup
    # ==========================================================================

    # Unconventional, heet imports (using ee) are delayed until GEE
    # authentication and initialisation are confirmed.
    import heet.task
    import heet.export
    import heet.config as cfg

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
    style = style_from_dict({
        Token.Separator: '#000080',
        Token.QuestionMark: '#008080 bold',
        Token.Selected: '#000080',  # default
        Token.Pointer: '#000080 bold',
        Token.Instruction: '',  # default
        Token.Answer: '#000080 bold',
        Token.Question: '',
    })

    questions = [
        {
            'type': 'confirm',
            'message': 'I understand what will happen if I continue',
            'name': 'understand',
        },
        {
            'type': 'confirm',
            'message': 'Would you like to continue?',
            'name': 'continue'
        }
    ]

    step_desc = "Checking Google Earth Engine Asset Folder"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            existing_tasks = Job.existing_tasks_running()
            existing_files = assets.existing_job_files()
        except Exception:
            # Handles any issue, including connectivity
            et.sp_err_fatal()
            sys.exit()
        else:
            if existing_tasks or existing_files:
                et.sp_fail()

                if existing_tasks:
                    et.sp_err_running()
                elif existing_files:
                    et.sp_err_interrupted()

                # Followup questions
                answer1 = prompt(
                    [questions[0]], style=style, raise_keyboard_interrupt=False)
                if answer1 == {}:
                    sys.exit("Exiting (Keyboard Interrupt)")
                if not answer1["understand"]:
                    sys.exit("Exiting (Did not understand)")
                answer2 = prompt(
                    [questions[1]], style=style, raise_keyboard_interrupt=False)
                if answer2 == {}:
                    sys.exit("Exiting (Keyboard Interrupt)")
                if not answer2["continue"]:
                    sys.exit("Exiting (No continue)")
                sp.write("")
            else:
                et.sp_success()

    # ==========================================================================
    # Prepare asset folder
    # ==========================================================================
    step_desc = "Preparing Google Earth Engine Asset Folder"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        if existing_tasks:
            try:
                Job.kill_all_running_tasks()
                heet.task.wait_until_jobs_finish()
            except Exception:
                # Handles any issue, including connectivity
                et.sp_fail()
                et.sp_err_fatal()
                sys.exit()

        try:
            assets.create_assets_folder()
        except Exception:
            # Handles any issue, including connectivity
            et.sp_fail()
            et.sp_err_fatal()
            sys.exit()
        else:
            et.sp_success()

    # ==========================================================================
    # Upload input file
    # ==========================================================================
    step_desc = "Uploading input file to Google Earth Engine"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            df = heet.validate.prepare_input_table(df_inputs)
        except Exception:
            # Handles any issue, including connectivity
            et.sp_fail()
            et.sp_err_fatal()
            logger.exception("[cli] There was a problem preparing input file.  Exiting...")
            sys.exit()

        try:
            inputs_ftc = Converter.df_to_ftc(data=df)
        except Exception:
            # Handles any issue, including connectivity
            et.sp_fail()
            et.sp_err_fatal()
            logger.exception(
                "[cli] There was a problem converting input file from df to ftc.  Exiting...")
            sys.exit()

        try:
            upload_task = heet.export.upload_user_inputs(inputs_ftc)
        except Exception:
            et.sp_fail()
            et.sp_err_upload()
            logger.exception(
                "[cli] There was a problem uploading user inputs to Google Earth Engine. Exiting...")
            sys.exit()

        try:
            heet.task.wait_until_upload(upload_task)
        except polling2.TimeoutException:
            et.sp_fail()
            et.sp_err_upload()
            logger.info("[cli] Uploading user inputs to Google Earth Engine timed out. Exiting...")
            sys.exit()
        except Exception:
            et.sp_fail()
            et.sp_err_upload()
            logger.exception(
                "[cli] There was a problem uploading user inputs to Google Earth Engine. Exiting...")

        try:
            upload_success = upload_task.status()['state'] in ['COMPLETED']
        except Exception:
            et.sp_fail()
            et.sp_err_upload()
            logger.exception(
                "[cli] There was a problem uploading user inputs to Google Earth Engine. Exiting...")

        if upload_success:
            et.sp_success()
        else:
            et.sp_fail()

    # ==========================================================================
    # Run Analysis
    # ==========================================================================

    batch_size = df_inputs.shape[0]
    n_calcs = batch_size * ntasks

    step_desc = f"Analysing {batch_size} dam locations ({n_calcs} calculations)"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            et.sp_success()
            pbar = tqdm(total=n_calcs, ncols=80)
            status = heet.task.run_analysis(pbar)
        except Exception:
            # Handles any issue, including connectivity
            et.sp_fail()
            et.sp_err_fatal()
            logger.exception("Fatal error when running analysis")
            sys.exit()
        else:
            if status == 1:
                et.sp_fail()
                et.sp_err_time()
                logger.info(
                    "(Running) Analysis wait time limit exceeded. Cancelling all unfinished HEET tasks.")
                try:
                    Job.kill_all_running_tasks()
                except Exception:
                    et.sp_err_fatal()
                    sys.exit()
        pbar.close()

    # ==========================================================================
    # Task completion (1)
    # ==========================================================================
    step_desc = "Waiting for running analysis tasks to complete"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet.task.wait_until_jobs_finish()
        except polling2.TimeoutException:
            et.sp_fail()
            et.sp_err_time()
            logger.info(
                "(Waiting) Analysis wait time limit exceeded. Cancelling all unfinished HEET tasks.")
            try:
                Job.kill_all_running_tasks()
            except Exception:
                et.sp_err_fatal()
                sys.exit()
        except Exception:
            # Handles any issue, including connectivity
            et.sp_fail()
            et.sp_err_fatal()
            sys.exit()
        else:
            et.sp_success()

    # ==========================================================================
    # Preparing for export
    # ==========================================================================
    step_desc = "Collecting calculated parameters for export"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet.task.assets_to_ftc()
        except Exception:
            # Handles any issue, including connectivity
            et.sp_fail()
            et.sp_warn_skip()
        else:
            et.sp_success()

    # ==========================================================================
    # Task completion (2)
    # ==========================================================================
    step_desc = "Waiting for data collection tasks to complete"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet.task.wait_until_jobs_finish()
        except polling2.TimeoutException:
            et.sp_fail()
            et.sp_err_time()
            logger.info(
                "(Waiting) Analysis wait time limit exceeded. Cancelling all unfinished HEET tasks.")
            try:
                Job.kill_all_running_tasks()
            except Exception:
                et.sp_err_fatal()
                sys.exit()
        except Exception:
            # Handles any issue, including connectivity
            et.sp_fail()
            et.sp_err_fatal()
            sys.exit()
        else:
            et.sp_success()

    # ==========================================================================
    # Exporting Results
    # ==========================================================================
    step_desc = "Exporting results to Google Drive"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet.task.export_to_drive()
        except Exception:
            # Handles any issue, including connectivity
            et.sp_fail()
            et.sp_warn_skip()
        else:
            et.sp_success()
            mtr.active_exports = list(mtr.active_export_tasks_log.keys())
            export_size = len(mtr.active_exports)
            remaining_export_size = export_size
            pbar = tqdm(total=export_size, ncols=80)

            keep_going = 1
            while ((len(mtr.active_exports) > 0) and (keep_going == 1)):
                try:
                    heet.task.wait_until_exports()
                    active_count = len(mtr.active_exports)
                    new_exports = remaining_export_size - active_count
                    remaining_export_size = active_count
                    pbar.update(new_exports)
                except polling2.TimeoutException:
                    keep_going = 0
                    et.sp_fail()
                    et.sp_err_time()
                    logger.info(
                        "(Waiting) Analysis wait time limit exceeded. Cancelling all unfinished HEET tasks.")
                    try:
                        Job.kill_all_running_tasks()
                    except Exception:
                        et.sp_err_fatal()
                        sys.exit()
                except Exception:
                    et.sp_fail()
                    sys.exit()
            pbar.close()

    # ==========================================================================
    # Exporting Results (Json, local Folder)
    # ==========================================================================
    step_desc = "Downloading json results to local results folder"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet.export.batch_export_to_json(output_folder_path)
        except Exception:
            # Handles any issue, including connectivity
            et.sp_fail()
            et.sp_warn_skip()
            logger.exception("[batch_export_to_json] Problem exporting output parameters to json")
        else:
            et.sp_success()

    # ==========================================================================
    # Exporting CSV Results
    # ==========================================================================
    step_desc = "Downloading csv results to local results folder"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet.export.download_output_parameters(output_folder_path)
        except Exception:
            # Handles any issue, including connectivity
            et.sp_fail()
            et.sp_warn_skip()
        else:
            et.sp_success()

    # ==========================================================================
    # Exporting Results (Assets Folder)
    # ==========================================================================
    step_desc = "Exporting results to Google Earth Engine Assets Folder"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet.task.export_to_assets()
        except Exception:
            # Handles any issue, including connectivity
            et.sp_fail()
            et.sp_err_fatal()
            sys.exit()
        else:
            et.sp_success()

    # ==========================================================================
    # Exporting CSV Results (Json, local Folder)
    # ==========================================================================
    step_desc = "Checking csv results for impossible and improbable output values"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        output_file_path = Path(output_folder_path, "output_parameters.csv")

        try:
            df_outputs = heet.validate.csv_to_df(output_file_path)
        except Exception:
            # Handles any issue, including connectivity
            et.sp_fail()
            et.sp_warn_skip()
            sys.exit()
        else:
            try:
                status = heet.validate.valid_output(
                    df_outputs, output_file_path, output_folder_path)
            except Exception:
                # Handles any issue, including connectivity
                et.sp_fail()
                et.sp_warn_skip()
                sys.exit()
            else:
                if status['valid']:
                    et.sp_success()
                else:
                    et.sp_fail()
                    et.sp_inv_output(status['issues'])

    # ==========================================================================
    # Exporting Results (Assets Folder)
    # ==========================================================================
    step_desc = "Generating Earth Engine task log"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            heet.task.task_audit(output_folder_path)
        except Exception:
            # Handles any issue, including connectivity
            et.sp_fail()
            et.sp_warn_skip()
            logger.error(
                "[cli] HEET encountered a problem generating tasks.csv",
                exc_info=heet.log_setup.EXC_INFO,
                stack_info=heet.log_setup.STACK_INFO)
            sys.exit()
        else:
            et.sp_success()

    # ==========================================================================
    # Cleaning up
    # ==========================================================================
    step_desc = "Cleaning up Google Earth Engine workspace"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        try:
            assets.clear_working_folder()
        except Exception:
            # Handles any issue, including connectivity
            et.sp_fail()
            et.sp_err_fatal()
            sys.exit()
        else:
            et.sp_success()

        # =====================================================================
        # Results Summary
        # =====================================================================
        et.sp_results_summary(
            output_folder_name=output_folder_name,
            output_drive_folder=cfg.output_drive_folder)


if __name__ == "__main__":
    #main()
    import time
    spinner = yaspin()
    spinner.start()
    time.sleep(3)  # time consuming tasks
    spinner.stop()

    ##

    internet_monitor = ConnectionMonitor()
    et = EmissionsTerminal()
    step_desc = "Checking internet connection"
    with yaspin(Spinners.line, text=step_desc, color="yellow") as sp:

        if not internet_monitor.connected():
            et.sp_success()
        else:
            et.sp_fail()
            et.sp_err_internet()
            sys.exit()
